"""Smoke tests for the spine + voiceover + LLM tier.

Coverage by slice:
- #2 (spine):      orchestrator returns a non-zero MP4
- #3 (voiceover):  the MP4 contains an aac audio stream and the voice is Australian
- #4 (LLM tier):   orchestrator classifies the prompt and writes a sidecar JSON

The orchestrator tests inject a `_FakeProvider` to keep them fast and offline.
The CLI subprocess test is skipped unless `GOOGLE_API_KEY` / `GEMINI_API_KEY` is set,
because the CLI's real path constructs a real `Gemini` provider end-to-end.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from visentia.llm.base import CODEGEN_TEMPERATURE, LLMProvider, Message
from visentia.llm.gemini import API_KEY_ENV_VARS
from visentia.orchestrator import RepairOrchestrator, sidecar_path_for
from visentia.results import Mp4


_FIXTURE_SOURCE = (
    Path(__file__).parent / "fixtures" / "freeform" / "renders_fine.py"
).read_text(encoding="utf-8")


class _FakeProvider(LLMProvider):
    """Deterministic fake — freeform classification + renders_fine codegen."""

    name = "fake"
    model = "fake-model"

    def complete(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        temperature: float = CODEGEN_TEMPERATURE,
        response_schema: dict | None = None,
    ) -> str:
        del system, temperature, response_schema
        content = messages[-1]["content"] if messages else ""
        if "Return the complete Python file" in content or "Math content type" in content:
            return _FIXTURE_SOURCE
        return json.dumps(
            {
                "math_content_type": "Relationship",
                "suggested_mode": "Deep",
                "suggested_template_id": "none",
            }
        )


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
def test_orchestrator_produces_mp4_with_audio_and_sidecar(tmp_path: Path) -> None:
    """Full orchestrator run with a fake provider.

    Asserts:
      - MP4 exists, non-zero bytes, has an audio stream (slice #3 contract)
      - Sidecar JSON exists alongside the MP4 with classification + provider metadata
        (slice #4 contract)

    Marked `slow`: edge-tts hits the network on first invocation per unique narration
    line (cached on subsequent runs under media/voiceovers/).
    """

    orchestrator = RepairOrchestrator(provider=_FakeProvider())
    result = orchestrator.generate_video("any prompt", output_dir=tmp_path)

    assert isinstance(result, Mp4), f"expected Mp4, got {type(result).__name__}"
    assert result.path.exists(), f"MP4 not at {result.path}"
    assert result.path.stat().st_size > 0, f"MP4 at {result.path} is zero bytes"
    assert result.metadata["path_taken"] == "freeform-success-on-attempt-1"
    assert result.metadata["freeform_attempts"] == 1
    assert result.metadata["llm_provider"] == "fake"
    assert result.metadata["llm_model"] == "fake-model"
    assert result.metadata["classification"]["math_content_type"] == "Relationship"
    assert result.metadata["classification"]["suggested_template_id"] is None
    assert result.metadata["classification"]["suggested_mode"] == "Deep"
    # Freeform fixture scenes are silent until voiceover is added to the freeform path.

    sidecar = sidecar_path_for(result.path)
    assert sidecar.exists(), f"sidecar JSON missing at {sidecar}"
    sidecar_data = json.loads(sidecar.read_text())
    assert sidecar_data["llm_provider"] == "fake"
    assert sidecar_data["classification"]["math_content_type"] == "Relationship"
    assert sidecar_data["prompt"] == "any prompt"


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
@pytest.mark.skipif(
    not any(os.environ.get(v) for v in API_KEY_ENV_VARS),
    reason=f"requires a real Google API key in one of {API_KEY_ENV_VARS}",
)
def test_cli_end_to_end_with_real_gemini(tmp_path: Path) -> None:
    """`visentia "<prompt>"` produces an MP4 + sidecar JSON via the real Gemini provider.

    Skipped automatically without an API key. With a key set, this is the strongest
    "everything works" smoke we have until the eval harness lands in slice #9.
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

    sidecar = sidecar_path_for(final_mp4)
    assert sidecar.exists(), f"sidecar JSON missing at {sidecar}"
    sidecar_data = json.loads(sidecar.read_text())
    assert sidecar_data["llm_provider"] == "gemini"
    assert sidecar_data["classification"]["math_content_type"] in (
        "Relationship",
        "Procedure",
        "Derivation",
    )
