"""Tests for Triangle3Side template + ParamFiller (slice #6)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from visentia.llm.base import CODEGEN_TEMPERATURE, LLMProvider, Message
from visentia.orchestrator import RepairOrchestrator
from visentia.results import Mp4
from visentia.templates import TemplateLibrary
from visentia.templates.spec import ParamValidationError, validate_triangle_3_side_params


class _TriangleTemplateProvider(LLMProvider):
    """Returns Triangle3Side classification and fixture params for ParamFiller."""

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
        text = messages[0]["content"] if messages else ""
        if "Parameter schema" in text or "Template: Triangle3Side" in text:
            return json.dumps(
                {"side_a": 3, "side_b": 4, "side_c": 5, "include_sweep": False}
            )
        return json.dumps(
            {
                "math_content_type": "Relationship",
                "suggested_mode": "Quick",
                "suggested_template_id": "Triangle3Side",
            }
        )


def test_validate_triangle_params_rejects_degenerate_triangle() -> None:
    with pytest.raises(ParamValidationError):
        validate_triangle_3_side_params({"side_a": 1, "side_b": 2, "side_c": 10})


def test_validate_triangle_params_accepts_fixture() -> None:
    params = validate_triangle_3_side_params(
        {"side_a": 3, "side_b": 4, "side_c": 5, "include_sweep": False}
    )
    assert params["include_sweep"] is False


@pytest.mark.slow
def test_template_library_fixture_render(tmp_path: Path) -> None:
    library = TemplateLibrary()
    spec = library.get("Triangle3Side")
    mp4 = library.render("Triangle3Side", spec.fixture_params, tmp_path)
    assert mp4.exists()
    assert mp4.stat().st_size > 0
    assert "triangle3side" in mp4.name.lower()


@pytest.mark.slow
def test_orchestrator_routes_to_triangle_template(tmp_path: Path) -> None:
    orchestrator = RepairOrchestrator(provider=_TriangleTemplateProvider())
    result = orchestrator.generate_video(
        "If you have a triangle not to scale with the 3 sides given, how to know if it is right angle or acute or obtuse?",
        output_dir=tmp_path,
    )

    assert isinstance(result, Mp4)
    assert result.metadata["path_taken"] == "template"
    assert result.metadata["classification_mode"] == "template"
    assert result.metadata["template_params"]["side_a"] == 3
    assert result.path.exists()
    assert result.path.stat().st_size > 0
