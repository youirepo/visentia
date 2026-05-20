"""Smoke tests for the spine slice (#2, extended in slice #3 with voiceover).

These tests verify the architectural skeleton connects end-to-end:
- `RepairOrchestrator.generate_video` returns an `Mp4` pointing at a non-zero-byte file
  whose MP4 contains an audio track (voiceover via edge-tts).
- The console script wires up correctly (verified via `--help`, which doesn't render).

Subsequent slices add behaviour-specific tests against their own contracts.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from visentia.orchestrator import RepairOrchestrator
from visentia.results import Mp4


def _mp4_has_audio_stream(mp4_path: Path) -> bool:
    """Use ffprobe to confirm the MP4 contains at least one audio stream."""

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            str(mp4_path),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return "audio" in result.stdout


@pytest.mark.slow
def test_orchestrator_produces_nonzero_mp4_with_audio(tmp_path: Path) -> None:
    """The stub orchestrator renders the placeholder Scene with voiceover.

    Marked `slow`: on first invocation `edge-tts` makes a network call to Microsoft's
    read-aloud endpoint to synthesize the placeholder narration (cached on subsequent runs).
    """

    orchestrator = RepairOrchestrator()
    result = orchestrator.generate_video("any prompt", output_dir=tmp_path)

    assert isinstance(result, Mp4), f"expected Mp4, got {type(result).__name__}"
    assert result.path.exists(), f"MP4 not at {result.path}"
    assert result.path.stat().st_size > 0, f"MP4 at {result.path} is zero bytes"
    assert result.metadata["path_taken"] == "spine-stub"
    assert result.metadata["tts"] == "edge-tts"
    assert result.metadata["voice"].startswith("en-AU-"), (
        f"voice must be Australian English, got {result.metadata['voice']!r}"
    )
    assert _mp4_has_audio_stream(result.path), (
        f"MP4 at {result.path} has no audio stream — voiceover did not bake in"
    )


def test_cli_help_works() -> None:
    """`visentia --help` succeeds and mentions the PROMPT argument."""

    result = subprocess.run(
        [sys.executable, "-m", "visentia", "--help"],
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 0, result.stderr
    assert "PROMPT" in result.stdout
    assert "visentia" in result.stdout.lower()


@pytest.mark.slow
def test_cli_end_to_end_produces_mp4_with_audio(tmp_path: Path) -> None:
    """`visentia "<prompt>"` produces an MP4 with an audio track and exits 0.

    Marked `slow` because it invokes Manim end-to-end with edge-tts narration. First-run
    cost includes a network call for TTS; subsequent runs hit the manim-voiceover cache.
    """

    result = subprocess.run(
        [sys.executable, "-m", "visentia", "any prompt", "--output-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, (
        f"CLI exited {result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    mp4s = [p for p in tmp_path.rglob("*.mp4") if "partial_movie_files" not in p.parts]
    assert mp4s, f"no top-level MP4 found under {tmp_path}"
    final_mp4 = mp4s[0]
    assert final_mp4.stat().st_size > 0, f"MP4 at {final_mp4} is zero bytes"
    assert _mp4_has_audio_stream(final_mp4), (
        f"CLI-produced MP4 at {final_mp4} has no audio stream"
    )
