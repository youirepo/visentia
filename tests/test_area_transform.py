"""Tests for AreaTransform template (slice #10, EV-003)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from visentia.llm.base import CODEGEN_TEMPERATURE, LLMProvider, Message
from visentia.orchestrator import RepairOrchestrator
from visentia.results import Mp4
from visentia.templates import TemplateLibrary
from visentia.templates.spec import ParamValidationError, validate_area_transform_params

_FIXTURE = {
    "rhombus_d1": 4,
    "rhombus_d2": 2.5,
    "trapezium_a": 2,
    "trapezium_b": 4,
    "trapezium_h": 2,
    "include_trapezium": False,
}


class _AreaTransformProvider(LLMProvider):
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
        if "Parameter schema" in text or "Template: AreaTransform" in text:
            return json.dumps(_FIXTURE)
        return json.dumps(
            {
                "math_content_type": "Derivation",
                "suggested_mode": "Deep",
                "suggested_template_id": "AreaTransform",
            }
        )


def test_validate_rejects_non_positive() -> None:
    with pytest.raises(ParamValidationError):
        validate_area_transform_params({**_FIXTURE, "rhombus_d1": 0})


@pytest.mark.slow
def test_template_library_fixture_render(tmp_path: Path) -> None:
    library = TemplateLibrary()
    mp4 = library.render("AreaTransform", _FIXTURE, tmp_path)
    assert mp4.exists()
    assert mp4.stat().st_size > 0


@pytest.mark.slow
def test_orchestrator_routes_ev003_prompt(tmp_path: Path) -> None:
    orchestrator = RepairOrchestrator(provider=_AreaTransformProvider())
    prompt = (
        "Year 8, areas of different rhombuses and also trapezium, specifically how "
        "the formulas for these shapes are derived"
    )
    result = orchestrator.generate_video(prompt, output_dir=tmp_path)
    assert isinstance(result, Mp4)
    assert result.metadata["path_taken"] == "template"
