"""Tests for WorkedExample template (slice #11, EV-002)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from visentia.llm.base import CODEGEN_TEMPERATURE, LLMProvider, Message
from visentia.orchestrator import RepairOrchestrator
from visentia.results import Mp4
from visentia.templates import TemplateLibrary
from visentia.templates.spec import ParamValidationError, validate_worked_example_params

_EV002_FIXTURE = {
    "item_label": "Apples",
    "rate_numerator": 5,
    "currency_symbol": r"\$",
    "rate_denominator": 100,
    "rate_unit": "g",
    "quantity": 4.5,
    "quantity_unit": "kg",
    "unit_conversion_factor": 1000,
}


class _WorkedExampleProvider(LLMProvider):
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
        if "Parameter schema" in text or "Template: WorkedExample" in text:
            return json.dumps(_EV002_FIXTURE)
        return json.dumps(
            {
                "math_content_type": "Procedure",
                "suggested_mode": "Quick",
                "suggested_template_id": "WorkedExample",
            }
        )


def test_validate_rejects_incompatible_dimensions() -> None:
    with pytest.raises(ParamValidationError, match="dimensions"):
        validate_worked_example_params(
            {
                **_EV002_FIXTURE,
                "rate_unit": "g",
                "quantity_unit": "L",
                "unit_conversion_factor": 1,
            }
        )


def test_validate_accepts_ev002_fixture() -> None:
    params = validate_worked_example_params(_EV002_FIXTURE)
    assert params["quantity"] == 4.5
    assert params["unit_conversion_factor"] == 1000


@pytest.mark.slow
def test_template_library_fixture_render(tmp_path: Path) -> None:
    library = TemplateLibrary()
    spec = library.get("WorkedExample")
    mp4 = library.render("WorkedExample", spec.fixture_params, tmp_path)
    assert mp4.exists()
    assert mp4.stat().st_size > 0
    assert "workedexample" in mp4.name.lower()


@pytest.mark.slow
def test_orchestrator_routes_ev002_prompt_to_worked_example(tmp_path: Path) -> None:
    orchestrator = RepairOrchestrator(provider=_WorkedExampleProvider())
    prompt = (
        "What do you do if you want to calculate a total amount given a rate? "
        "For example, if apples cost $5/100g how much is 4.5kg?"
    )
    result = orchestrator.generate_video(prompt, output_dir=tmp_path)

    assert isinstance(result, Mp4)
    assert result.metadata["path_taken"] == "template"
    assert result.metadata["template_params"]["rate_numerator"] == 5
    assert result.path.exists()
    assert result.path.stat().st_size > 0
