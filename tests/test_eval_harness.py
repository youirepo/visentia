"""Eval harness parser and report tests (slice #9)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from visentia.classifier import Classification
from visentia.eval import parse_eval_file, run_evals
from visentia.llm.base import CODEGEN_TEMPERATURE, LLMProvider, Message
from visentia.results import Failure, Mp4

_SEED = Path(__file__).resolve().parents[1] / "docs" / "evals" / "seed.md"
_FIXTURE_SOURCE = (
    Path(__file__).parent / "fixtures" / "freeform" / "renders_fine.py"
).read_text(encoding="utf-8")


def test_parse_seed_has_three_entries() -> None:
    entries = parse_eval_file(_SEED)
    assert [e.id for e in entries] == ["EV-001", "EV-002", "EV-003"]
    assert entries[0].math_content_type == "Relationship"
    assert entries[1].math_content_type == "Procedure"
    assert entries[2].math_content_type == "Derivation"
    assert len(entries[0].success_10) >= 3
    assert len(entries[0].failure_modes) >= 2


class _EvalProvider(LLMProvider):
    """Classify per entry id; codegen always returns renders_fine."""

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
        lowered = content.lower()
        if "triangle" in lowered and "obtuse" in lowered:
            mct, template = "Relationship", "none"
        elif "apples" in lowered or "100g" in lowered:
            mct, template = "Procedure", "none"
        elif "rhombus" in lowered or "trapezium" in lowered:
            mct, template = "Derivation", "none"
        else:
            mct, template = "Procedure", "none"
        return json.dumps(
            {
                "math_content_type": mct,
                "suggested_mode": "Quick",
                "suggested_template_id": template,
            }
        )


def test_run_evals_report_structure(tmp_path: Path) -> None:
    from visentia.orchestrator import RepairOrchestrator

    orchestrator = RepairOrchestrator(provider=_EvalProvider())
    report = run_evals(
        _SEED,
        orchestrator=orchestrator,
        output_dir=tmp_path / "runs",
        report_dir=tmp_path / "reports",
        max_attempts=1,
    )

    assert report.entry_count == 3
    assert report.classifier_correct_count == 3
    assert report.generation_success_count == 3
    assert report.report_path.name.startswith("eval-")
    assert report.report_path.exists()

    text = report.markdown
    assert "Classifier accuracy:** 3/3" in text
    assert "## EV-001" in text
    assert "## EV-002" in text
    assert "## EV-003" in text
    assert "### HITL grading — 10/10" in text
    assert "- [ ]" in text
    assert "freeform-success-on-attempt" in text or "template" in text

    for row in report.entries:
        assert row.classifier_correct
        assert isinstance(row.generate_result, Mp4)
        assert row.generate_result.path.exists()


def test_report_records_classifier_mismatch(tmp_path: Path) -> None:
    from visentia.orchestrator import RepairOrchestrator

    orchestrator = RepairOrchestrator(provider=_EvalProvider())
    entries = parse_eval_file(_SEED)
    mini = tmp_path / "mini.md"
    mini.write_text(
        f"## EV-002 — Rate\n\n```yaml\nid: EV-002\nprompt: |\n  {entries[1].prompt}\n"
        f"math_content_type: Procedure\nexpected_artifact_form: Video\n```\n\n"
        f"### Success criteria\n\n**10/10**:\n- one\n\n**5/10**:\n- floor\n\n"
        f"### Failure modes to check\n\n- mode\n",
        encoding="utf-8",
    )

    with patch(
        "visentia.orchestrator.ContentClassifier.classify",
        return_value=Classification(
            math_content_type="Relationship",
            suggested_template_id=None,
            suggested_mode="Quick",
        ),
    ):
        report = run_evals(
            mini,
            orchestrator=orchestrator,
            output_dir=tmp_path / "runs",
            report_dir=tmp_path / "reports",
            max_attempts=1,
        )

    assert report.classifier_correct_count == 0
    assert "**no**" in report.markdown


def test_repair_succeeds_on_attempt_2_in_report(tmp_path: Path) -> None:
    """Deliberately broken first codegen; repair on attempt 2 (issue #8 + #9)."""

    class _RepairEvalProvider(_EvalProvider):
        def __init__(self) -> None:
            self.codegen_calls = 0

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
                if self.codegen_calls == 1:
                    return "class X(Scene):\n  pass"
                return _FIXTURE_SOURCE
            return super().complete(
                messages,
                system=system,
                temperature=temperature,
                response_schema=response_schema,
            )

    from visentia.orchestrator import RepairOrchestrator

    provider = _RepairEvalProvider()
    orchestrator = RepairOrchestrator(provider=provider)

    # Single-entry mini eval file
    mini = tmp_path / "mini.md"
    entries = parse_eval_file(_SEED)
    mini.write_text(
        f"## EV-002 — Rate\n\n```yaml\nid: EV-002\nprompt: |\n  {entries[1].prompt}\n"
        f"math_content_type: Procedure\nexpected_artifact_form: Video\n```\n\n"
        f"### Success criteria\n\n**10/10**:\n- item one\n\n**5/10**:\n- floor one\n\n"
        f"### Failure modes to check\n\n- fail one\n",
        encoding="utf-8",
    )

    report = run_evals(
        mini,
        orchestrator=orchestrator,
        output_dir=tmp_path / "runs",
        report_dir=tmp_path / "reports",
        max_attempts=3,
    )

    assert report.generation_success_count == 1
    row = report.entries[0]
    assert isinstance(row.generate_result, Mp4)
    assert row.generate_result.metadata["path_taken"] == "freeform-success-on-attempt-2"
    assert provider.codegen_calls == 2


def test_cli_eval_help() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "visentia", "eval", "--help"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0
    assert "--eval-file" in result.stdout
