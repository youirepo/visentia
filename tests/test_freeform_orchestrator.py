"""Freeform path orchestrator tests (slice #7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from visentia.llm.base import CODEGEN_TEMPERATURE, LLMProvider, Message
from visentia.orchestrator import RepairOrchestrator
from visentia.results import Failure, Mp4

_FIXTURE_SOURCE = (
    Path(__file__).parent / "fixtures" / "freeform" / "renders_fine.py"
).read_text(encoding="utf-8")


class _FreeformProvider(LLMProvider):
    """Routes to freeform; codegen returns the renders_fine fixture."""

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
                "math_content_type": "Procedure",
                "suggested_mode": "Quick",
                "suggested_template_id": "none",
            }
        )


@pytest.mark.slow
def test_orchestrator_freeform_path_produces_mp4(tmp_path: Path) -> None:
    orchestrator = RepairOrchestrator(provider=_FreeformProvider())
    prompt = (
        "How do I calculate a total amount given a rate, like apples at $5 per 100g for 4.5kg?"
    )
    result = orchestrator.generate_video(prompt, output_dir=tmp_path)

    assert isinstance(result, Mp4), f"expected Mp4, got {type(result).__name__}: {result}"
    assert result.path.exists()
    assert result.path.stat().st_size > 0
    assert result.metadata["path_taken"] == "freeform"
    assert result.metadata["classification"]["suggested_template_id"] is None


def test_orchestrator_surfaces_lint_failure_without_traceback(tmp_path: Path) -> None:
    class _BadCodegenProvider(_FreeformProvider):
        def complete(
            self,
            messages,
            *,
            system=None,
            temperature=CODEGEN_TEMPERATURE,
            response_schema=None,
        ):
            content = messages[-1]["content"] if messages else ""
            if "Return the complete Python file" in content or "Math content type" in content:
                return "class X(Scene):\n  pass"
            return super().complete(
                messages,
                system=system,
                temperature=temperature,
                response_schema=response_schema,
            )

    orchestrator = RepairOrchestrator(provider=_BadCodegenProvider())
    result = orchestrator.generate_video("any", output_dir=tmp_path)
    assert isinstance(result, Failure)
    assert "Traceback" not in result.message
    assert "manim import" in result.message.lower() or "Scene" in result.message
