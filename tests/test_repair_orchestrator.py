"""RepairOrchestrator repair loop + template fallback (slice #8)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from visentia.classifier import Classification
from visentia.freeform.renderer import RenderFailure, RenderSuccess
from visentia.llm.base import CODEGEN_TEMPERATURE, LLMProvider, Message
from visentia.orchestrator import RepairOrchestrator
from visentia.results import Failure, Mp4

_FIXTURE_SOURCE = (
    Path(__file__).parent / "fixtures" / "freeform" / "renders_fine.py"
).read_text(encoding="utf-8")

_BAD_SOURCE = "class BadScene(Scene):\n  pass"


class _FreeformClassifierProvider(LLMProvider):
    """Procedure / no template — for freeform-only repair tests."""

    name = "fake"
    model = "fake-model"

    def __init__(self) -> None:
        self.codegen_calls = 0
        self.last_repair_context: str | None = None

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
            self.codegen_calls += 1
            if "Repair context:" in content:
                self.last_repair_context = content.split("Repair context:", 1)[-1].strip()
            if self.codegen_calls == 1:
                return _BAD_SOURCE
            return _FIXTURE_SOURCE
        return json.dumps(
            {
                "math_content_type": "Procedure",
                "suggested_mode": "Quick",
                "suggested_template_id": "none",
            }
        )


class _AlwaysBadCodegenProvider(_FreeformClassifierProvider):
    def complete(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        temperature: float = CODEGEN_TEMPERATURE,
        response_schema: dict | None = None,
    ) -> str:
        content = messages[-1]["content"] if messages else ""
        if "Return the complete Python file" in content or "Math content type" in content:
            self.codegen_calls += 1
            return _BAD_SOURCE
        return json.dumps(
            {
                "math_content_type": "Procedure",
                "suggested_mode": "Quick",
                "suggested_template_id": "none",
            }
        )


def test_repair_loop_succeeds_on_attempt_2(tmp_path: Path) -> None:
    provider = _FreeformClassifierProvider()
    orchestrator = RepairOrchestrator(provider=provider)

    result = orchestrator.generate_video("any prompt", output_dir=tmp_path, max_attempts=3)

    assert isinstance(result, Mp4)
    assert result.metadata["path_taken"] == "freeform-success-on-attempt-2"
    assert result.metadata["freeform_attempts"] == 2
    assert result.metadata["classification_mode"] == "freeform"
    assert provider.codegen_calls == 2
    assert provider.last_repair_context is not None


def test_repair_budget_exhausted_returns_failure(tmp_path: Path) -> None:
    provider = _AlwaysBadCodegenProvider()
    orchestrator = RepairOrchestrator(provider=provider)

    result = orchestrator.generate_video("any", output_dir=tmp_path, max_attempts=3)

    assert isinstance(result, Failure)
    assert result.attempts_made == 3
    assert result.path_taken == "total-failure"
    assert provider.codegen_calls == 3
    assert "Traceback" not in result.message


def test_mocked_renderer_retries_then_succeeds(tmp_path: Path) -> None:
    out_mp4 = tmp_path / "mock.mp4"
    out_mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42")

    renderer = MagicMock()
    renderer.render.side_effect = [
        RenderFailure(kind="name_error", message="undefined name", stderr="NameError: Foo"),
        RenderSuccess(mp4_path=out_mp4),
    ]

    provider = _FreeformClassifierProvider()
    # Always return valid source so lint passes; render fails once.
    provider.codegen_calls = 0

    class LintOkOnly(_FreeformClassifierProvider):
        def complete(self, messages, *, system=None, temperature=CODEGEN_TEMPERATURE, response_schema=None):
            content = messages[-1]["content"] if messages else ""
            if "Return the complete Python file" in content or "Math content type" in content:
                self.codegen_calls += 1
                if "Repair context:" in content:
                    self.last_repair_context = content.split("Repair context:", 1)[-1].strip()
                return _FIXTURE_SOURCE
            return json.dumps(
                {
                    "math_content_type": "Procedure",
                    "suggested_mode": "Quick",
                    "suggested_template_id": "none",
                }
            )

    provider = LintOkOnly()
    orchestrator = RepairOrchestrator(provider=provider, sandboxed_renderer=renderer)

    result = orchestrator.generate_video("any", output_dir=tmp_path, max_attempts=3)

    assert isinstance(result, Mp4)
    assert result.metadata["path_taken"] == "freeform-success-on-attempt-2"
    assert renderer.render.call_count == 2
    assert provider.codegen_calls == 2
    assert provider.last_repair_context is not None
    assert "render" in provider.last_repair_context.lower()


@pytest.mark.slow
def test_template_fallback_after_freeform_exhaust(tmp_path: Path) -> None:
    """When a template is registered, exhaust freeform then render the template."""

    class _TriangleProvider(_AlwaysBadCodegenProvider):
        def complete(
            self,
            messages: list[Message],
            *,
            system: str | None = None,
            temperature: float = CODEGEN_TEMPERATURE,
            response_schema: dict | None = None,
        ) -> str:
            content = messages[-1]["content"] if messages else ""
            if "Parameter schema" in content or "Template: Triangle3Side" in content:
                return json.dumps(
                    {"side_a": 3, "side_b": 4, "side_c": 5, "include_sweep": False}
                )
            return super().complete(
                messages,
                system=system,
                temperature=temperature,
                response_schema=response_schema,
            )

    provider = _TriangleProvider()
    orchestrator = RepairOrchestrator(provider=provider)
    template_calls: list[str] = []
    real_render_template = orchestrator._render_template

    def tracking_template(prompt, classification, output_dir):
        template_calls.append("call")
        if len(template_calls) == 1:
            raise RuntimeError("Simulated template failure — use freeform")
        return real_render_template(prompt, classification, output_dir)

    orchestrator._render_template = tracking_template  # type: ignore[method-assign]

    classification = Classification(
        math_content_type="Relationship",
        suggested_template_id="Triangle3Side",
        suggested_mode="Quick",
    )

    with patch(
        "visentia.orchestrator.ContentClassifier.classify",
        return_value=classification,
    ):
        result = orchestrator.generate_video(
            "triangle sides 3 4 5",
            output_dir=tmp_path,
            max_attempts=2,
        )

    assert isinstance(result, Mp4)
    assert result.metadata["path_taken"] == "freeform-fallback-to-template:Triangle3Side"
    assert result.metadata["classification_mode"] == "freeform-fallback-to-template"
    assert result.metadata["freeform_attempts"] == 2
    assert provider.codegen_calls == 2
    assert len(template_calls) == 2
