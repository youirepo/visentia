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
            asyncio.run(_synthesize(input_text, self.voice, audio_path))
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
        }


async def _synthesize(text: str, voice: str, output_path: Path) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
