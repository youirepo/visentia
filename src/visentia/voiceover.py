"""Voiceover synthesis facade.

This module is Visentia's single point of control over text-to-speech. Scenes never
reach into `edge-tts` or `manim-voiceover.services.*` directly — they ask
`VoiceoverSynthesizer.create_service()` for a `SpeechService` and pass it to their
`VoiceoverScene.set_speech_service` call.

Why the indirection: swapping TTS providers later (Piper for offline use, ElevenLabs
for a polished v0.x, Microsoft Azure Neural if `edge-tts` is ever rate-limited or
deprecated) is a one-module change here — no Scene code needs to change.

## Implementation note

`manim-voiceover` 0.3.7 ships a handful of speech services (`AzureService`,
`OpenAIService`, `GTTSService`, `ElevenLabsService`, `CoquiService`, `PyTTSx3Service`,
`RecorderService`) but **not** an Edge / `edge-tts` service. We bridge `edge-tts` into
`manim-voiceover`'s `SpeechService` interface here. The pattern follows
`manim_voiceover.services.gtts.GTTSService`.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import edge_tts
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService

DEFAULT_VOICE: str = "en-AU-NatashaNeural"
"""Default voice: female Australian English neural voice from Microsoft Edge read-aloud.

Alternative: `en-AU-WilliamNeural` (male). Full list at
https://github.com/rany2/edge-tts#summary (run `edge-tts --list-voices`)."""


class VoiceoverSynthesizer:
    """Facade owning Visentia's TTS-backend choice.

    Scenes call `VoiceoverSynthesizer.create_service()` and forward the result into
    `VoiceoverScene.set_speech_service(...)`. Future TTS swaps live behind this method.
    """

    DEFAULT_VOICE = DEFAULT_VOICE

    @staticmethod
    def create_service(voice: str | None = None, **service_kwargs: Any) -> SpeechService:
        """Return a configured `SpeechService` for use by a `VoiceoverScene`.

        Args:
            voice: edge-tts voice identifier (defaults to `en-AU-NatashaNeural`).
            **service_kwargs: forwarded to `SpeechService.__init__` (e.g., `cache_dir`,
                `global_speed`).
        """
        return EdgeService(voice=voice or DEFAULT_VOICE, **service_kwargs)


class EdgeService(SpeechService):
    """`manim-voiceover` speech service backed by the `edge-tts` library.

    `edge-tts` reaches Microsoft Edge's free read-aloud TTS endpoint. No API key
    required, no quota documented, requires internet only on cache miss.

    Output is an MP3 saved under `manim-voiceover`'s standard cache directory.
    `manim-voiceover` mixes it into the final MP4 via its `VoiceoverScene` machinery
    — we don't touch ffmpeg directly.
    """

    def __init__(self, voice: str = DEFAULT_VOICE, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.voice = voice

    def generate_from_text(
        self,
        text: str,
        cache_dir: str | None = None,
        path: str | None = None,
        **kwargs: Any,
    ) -> dict:
        del kwargs

        target_cache_dir = Path(cache_dir) if cache_dir is not None else Path(self.cache_dir)

        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "edge-tts",
            "voice": self.voice,
        }

        cached = self.get_cached_result(input_data, target_cache_dir)
        if cached is not None:
            return cached

        audio_filename = path or (self.get_audio_basename(input_data) + ".mp3")
        audio_path = target_cache_dir / audio_filename

        try:
            word_boundaries = asyncio.run(_synthesize(input_text, self.voice, audio_path))
        except Exception as exc:
            raise RuntimeError(
                f"edge-tts failed to synthesize speech (voice={self.voice!r}). "
                "Check internet connection and that the voice name is valid "
                "(see `edge-tts --list-voices`)."
            ) from exc

        return {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_filename,
            "word_boundaries": word_boundaries,
        }


AUDIO_OFFSET_RESOLUTION = 10_000_000
"""Ticks per second in `manim-voiceover`'s `audio_offset` field (100-nanosecond units).

`edge-tts` reports `offset` and `duration` in the same units, so the values pass through
unconverted — see `manim_voiceover.tracker.TimeInterpolator`.
"""


async def _synthesize(text: str, voice: str, output_path: Path) -> list[dict]:
    """Synthesize `text` to `output_path` and return `manim-voiceover` word boundaries.

    `Communicate.save()` discards the `WordBoundary` messages in the stream, which leaves
    `VoiceoverTracker` interpolating bookmark times linearly from character offsets — every
    `<bookmark>` cue timed by a guess (issue #35). Streaming keeps them.

    `edge-tts` reports each word's audio offset but not its position in the input text,
    while `TimeInterpolator` keys on `text_offset`. The offsets are therefore reconstructed
    by walking the spoken words through the input text in order.
    """

    # `boundary` defaults to "SentenceBoundary" in edge-tts 7.2.8 — one timing point per
    # sentence is far too coarse to place a bookmark inside one.
    communicate = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    boundaries: list[dict] = []
    cursor = 0

    with output_path.open("wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word = str(chunk["text"])
                if not word:
                    continue
                found = text.find(word, cursor)
                if found < 0:
                    # A spoken word the synthesizer normalised away from the source text
                    # (e.g. "5" voiced as "five"). Skip it rather than desynchronising the
                    # offsets of every word after it.
                    continue
                cursor = found + len(word)
                boundaries.append(
                    {
                        "audio_offset": int(chunk["offset"]),
                        "duration": int(chunk["duration"]),
                        "text_offset": found,
                        "word_length": len(word),
                        "text": word,
                        "boundary_type": "Word",
                    }
                )

    return _with_terminal_boundary(boundaries, text)


def _with_terminal_boundary(boundaries: list[dict], text: str) -> list[dict]:
    """Append an end-of-text boundary so bookmarks after the last word interpolate.

    `TimeInterpolator` builds an `interp1d` over the boundaries and cannot extrapolate; a
    bookmark sitting past the final word would otherwise collapse onto that word's time.
    """

    if not boundaries:
        return boundaries

    last = boundaries[-1]
    end_offset = len(text)
    if end_offset <= last["text_offset"] + int(last["word_length"]):
        return boundaries

    return boundaries + [
        {
            "audio_offset": int(last["audio_offset"]) + int(last.get("duration", 0)),
            "text_offset": end_offset,
            "word_length": 0,
            "text": "",
            "boundary_type": "Word",
        }
    ]
