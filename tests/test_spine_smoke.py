"""Smoke tests for the spine slice (#2).

These tests verify the architectural skeleton connects end-to-end:
- `RepairOrchestrator.generate_video` returns an `Mp4` pointing at a real, non-zero-byte file.
- The console script wires up correctly (verified via `--help`, which doesn't require a render).

Subsequent slices add behaviour-specific tests against their own contracts.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from visentia.orchestrator import RepairOrchestrator
from visentia.results import Mp4


def test_orchestrator_produces_nonzero_mp4(tmp_path: Path) -> None:
    """The stub orchestrator renders the placeholder Scene and returns a real MP4."""

    orchestrator = RepairOrchestrator()
    result = orchestrator.generate_video("any prompt", output_dir=tmp_path)

    assert isinstance(result, Mp4), f"expected Mp4, got {type(result).__name__}"
    assert result.path.exists(), f"MP4 not at {result.path}"
    assert result.path.stat().st_size > 0, f"MP4 at {result.path} is zero bytes"
    assert result.metadata["path_taken"] == "spine-stub"


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
def test_cli_end_to_end(tmp_path: Path) -> None:
    """`visentia "<prompt>"` produces an MP4 on disk and exits 0.

    Marked `slow` because it invokes Manim end-to-end (~10-30s on a fast machine). Run with
    `pytest -m slow` or `pytest` (default selection includes it).
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

    mp4s = list(tmp_path.rglob("*.mp4"))
    assert mp4s, f"no MP4 found under {tmp_path}"
    assert mp4s[0].stat().st_size > 0, f"MP4 at {mp4s[0]} is zero bytes"
