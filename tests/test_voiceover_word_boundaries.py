"""Word-boundary capture in the edge-tts bridge (issue #35).

`Communicate.save()` discarded edge-tts's WordBoundary stream, leaving every `<bookmark>`
cue timed by `manim-voiceover`'s linear-interpolation fallback. These tests pin the two
things the tracker actually depends on: `text_offset` is a character offset into the
bookmark-stripped input text, and `audio_offset` is in 100-nanosecond ticks.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from visentia import voiceover
from visentia.voiceover import _synthesize, _with_terminal_boundary

TICKS = voiceover.AUDIO_OFFSET_RESOLUTION


class _FakeCommunicate:
    """Stands in for `edge_tts.Communicate`, replaying a scripted stream."""

    last_kwargs: dict = {}

    def __init__(self, text: str, voice: str, **kwargs) -> None:
        self.text = text
        self.voice = voice
        type(self).last_kwargs = kwargs

    async def stream(self):
        yield {"type": "audio", "data": b"MP3"}
        for word, offset in (("The", 0), ("gradient", 1), ("is", 2), ("two", 3)):
            yield {
                "type": "WordBoundary",
                "offset": offset * TICKS // 2,
                "duration": TICKS // 2,
                "text": word,
            }
        yield {"type": "audio", "data": b"DATA"}


def _run(text: str, tmp_path: Path, monkeypatch) -> list[dict]:
    monkeypatch.setattr(voiceover.edge_tts, "Communicate", _FakeCommunicate)
    return asyncio.run(_synthesize(text, "en-AU-NatashaNeural", tmp_path / "out.mp3"))


def test_requests_word_boundaries_not_sentence_boundaries(tmp_path, monkeypatch):
    _run("The gradient is two.", tmp_path, monkeypatch)
    assert _FakeCommunicate.last_kwargs.get("boundary") == "WordBoundary"


def test_audio_is_written_from_the_stream(tmp_path, monkeypatch):
    _run("The gradient is two.", tmp_path, monkeypatch)
    assert (tmp_path / "out.mp3").read_bytes() == b"MP3DATA"


def test_text_offsets_point_at_the_words_in_the_input(tmp_path, monkeypatch):
    text = "The gradient is two."
    boundaries = _run(text, tmp_path, monkeypatch)

    spoken = [b for b in boundaries if b["text"]]
    assert [b["text"] for b in spoken] == ["The", "gradient", "is", "two"]
    for boundary in spoken:
        start = boundary["text_offset"]
        assert text[start : start + boundary["word_length"]] == boundary["text"]


def test_offsets_are_strictly_increasing_for_repeated_words(tmp_path, monkeypatch):
    """A repeated word must not rewind the cursor to its first occurrence.

    `TimeInterpolator` builds an `interp1d` over `text_offset`; a non-monotonic sequence
    would make bookmark times meaningless.
    """

    class _Repeats(_FakeCommunicate):
        async def stream(self):
            yield {"type": "audio", "data": b"MP3"}
            for i, word in enumerate(("is", "is", "is")):
                yield {
                    "type": "WordBoundary",
                    "offset": i * TICKS,
                    "duration": TICKS,
                    "text": word,
                }

    monkeypatch.setattr(voiceover.edge_tts, "Communicate", _Repeats)
    boundaries = asyncio.run(
        _synthesize("is is is", "en-AU-NatashaNeural", tmp_path / "out.mp3")
    )

    offsets = [b["text_offset"] for b in boundaries]
    assert offsets == sorted(offsets)
    assert len(set(offsets)) == len(offsets)


def test_a_normalised_word_is_skipped_without_desynchronising_the_rest(tmp_path, monkeypatch):
    """edge-tts voices "5" as "five"; the word is absent from the source text."""

    class _Normalises(_FakeCommunicate):
        async def stream(self):
            yield {"type": "audio", "data": b"MP3"}
            for i, word in enumerate(("gradient", "five", "here")):
                yield {
                    "type": "WordBoundary",
                    "offset": i * TICKS,
                    "duration": TICKS,
                    "text": word,
                }

    text = "gradient 5 here"
    monkeypatch.setattr(voiceover.edge_tts, "Communicate", _Normalises)
    boundaries = asyncio.run(
        _synthesize(text, "en-AU-NatashaNeural", tmp_path / "out.mp3")
    )

    spoken = [b for b in boundaries if b["text"]]
    assert [b["text"] for b in spoken] == ["gradient", "here"]
    assert text[spoken[-1]["text_offset"]:].startswith("here")


def test_terminal_boundary_covers_text_after_the_last_word():
    boundaries = [
        {"audio_offset": 0, "duration": TICKS, "text_offset": 0, "word_length": 3, "text": "Two"},
    ]
    result = _with_terminal_boundary(boundaries, "Two halves.")

    assert len(result) == 2
    assert result[-1]["text_offset"] == len("Two halves.")
    assert result[-1]["audio_offset"] == TICKS


def test_no_terminal_boundary_when_the_last_word_ends_the_text():
    boundaries = [
        {"audio_offset": 0, "duration": TICKS, "text_offset": 0, "word_length": 3, "text": "Two"},
    ]
    assert _with_terminal_boundary(boundaries, "Two") == boundaries


def test_empty_boundaries_pass_through():
    assert _with_terminal_boundary([], "anything") == []
