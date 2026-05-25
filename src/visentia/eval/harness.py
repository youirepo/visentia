"""EvalHarness — run seed evals and emit a human-grading markdown report."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from visentia.classifier import ContentClassifier
from visentia.eval.parser import EvalEntry, parse_eval_file
from visentia.llm import LLMProvider
from visentia.orchestrator import RepairOrchestrator
from visentia.results import Failure, GenerateResult, Mp4


@dataclass
class EvalEntryResult:
    entry: EvalEntry
    classified_math_content_type: str
    classifier_correct: bool
    classified_mode: str
    suggested_template_id: str | None
    generate_result: GenerateResult
    wall_clock_s: float
    provider_name: str
    model_name: str


@dataclass
class EvalReport:
    """Full eval run — markdown report plus per-entry results."""

    markdown: str
    report_path: Path
    entries: list[EvalEntryResult] = field(default_factory=list)
    classifier_correct_count: int = 0
    generation_success_count: int = 0

    @property
    def entry_count(self) -> int:
        return len(self.entries)


class EvalHarness:
    def __init__(
        self,
        orchestrator: RepairOrchestrator | None = None,
        *,
        provider: LLMProvider | None = None,
    ) -> None:
        self._orchestrator = orchestrator or RepairOrchestrator(provider=provider)
        self._provider = provider or self._orchestrator.provider

    def run_evals(
        self,
        eval_file: Path | None = None,
        *,
        output_dir: Path | None = None,
        report_dir: Path | None = None,
        max_attempts: int = 3,
    ) -> EvalReport:
        return run_evals(
            eval_file,
            orchestrator=self._orchestrator,
            output_dir=output_dir,
            report_dir=report_dir,
            max_attempts=max_attempts,
        )


def run_evals(
    eval_file: Path | None = None,
    *,
    orchestrator: RepairOrchestrator | None = None,
    output_dir: Path | None = None,
    report_dir: Path | None = None,
    max_attempts: int = 3,
) -> EvalReport:
    """Parse `eval_file`, run each prompt through the pipeline, write a timestamped report."""

    seed_path = (eval_file or _default_seed_path()).resolve()
    entries = parse_eval_file(seed_path)

    orchestrator = orchestrator or RepairOrchestrator()
    classifier = ContentClassifier(orchestrator.provider)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = (output_dir or Path.cwd() / "eval-runs" / stamp).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    reports_dir = (report_dir or Path.cwd() / "eval-reports").resolve()
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"eval-{stamp}.md"

    entry_results: list[EvalEntryResult] = []

    for entry in entries:
        entry_dir = run_dir / entry.id
        entry_dir.mkdir(parents=True, exist_ok=True)

        started = time.monotonic()
        classification = classifier.classify(entry.prompt)
        result = orchestrator.generate_video(
            entry.prompt,
            output_dir=entry_dir,
            max_attempts=max_attempts,
        )
        elapsed = time.monotonic() - started

        entry_results.append(
            EvalEntryResult(
                entry=entry,
                classified_math_content_type=classification.math_content_type,
                classifier_correct=classification.math_content_type == entry.math_content_type,
                classified_mode=classification.suggested_mode,
                suggested_template_id=classification.suggested_template_id,
                generate_result=result,
                wall_clock_s=elapsed,
                provider_name=orchestrator.provider.name,
                model_name=orchestrator.provider.model,
            )
        )

    correct = sum(1 for r in entry_results if r.classifier_correct)
    successes = sum(1 for r in entry_results if isinstance(r.generate_result, Mp4))

    markdown = _render_report(
        seed_path=seed_path,
        stamp=stamp,
        run_dir=run_dir,
        entry_results=entry_results,
        classifier_correct=correct,
        generation_success=successes,
    )
    report_path.write_text(markdown, encoding="utf-8")

    return EvalReport(
        markdown=markdown,
        report_path=report_path,
        entries=entry_results,
        classifier_correct_count=correct,
        generation_success_count=successes,
    )


def _default_seed_path() -> Path:
    return Path(__file__).resolve().parents[3] / "docs" / "evals" / "seed.md"


def _render_report(
    *,
    seed_path: Path,
    stamp: str,
    run_dir: Path,
    entry_results: list[EvalEntryResult],
    classifier_correct: int,
    generation_success: int,
) -> str:
    total = len(entry_results)
    lines = [
        f"# Visentia Eval Report — {stamp}",
        "",
        f"**Eval file:** `{seed_path}`  ",
        f"**Run output:** `{run_dir}`  ",
        f"**Generated (UTC):** {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
        f"- **Classifier accuracy:** {classifier_correct}/{total} entries classified correctly",
        f"- **Generation success:** {generation_success}/{total} entries produced an MP4",
        "",
        "---",
        "",
    ]

    for row in entry_results:
        lines.extend(_render_entry_section(row))
        lines.extend(["", "---", ""])

    return "\n".join(lines).rstrip() + "\n"


def _render_entry_section(row: EvalEntryResult) -> list[str]:
    entry = row.entry
    result = row.generate_result

    class_mark = "yes" if row.classifier_correct else "**no**"
    lines = [
        f"## {entry.id} — {entry.title}",
        "",
        "### Prompt",
        "",
        f"> {entry.prompt}",
        "",
        "### Pipeline",
        "",
        f"- **Provider / model:** {row.provider_name} / `{row.model_name}`",
        f"- **Wall-clock time:** {row.wall_clock_s:.1f}s",
        f"- **Expected Math Content Type:** `{entry.math_content_type}`",
        f"- **Classified Math Content Type:** `{row.classified_math_content_type}` ({class_mark})",
        f"- **Classified mode:** `{row.classified_mode}`",
        f"- **Suggested template:** `{row.suggested_template_id or 'none'}`",
    ]

    if isinstance(result, Mp4):
        meta = result.metadata
        lines.extend(
            [
                f"- **Path taken:** `{meta.get('path_taken', '?')}`",
                f"- **Classification mode:** `{meta.get('classification_mode', '?')}`",
                f"- **Freeform attempts:** `{meta.get('freeform_attempts', '—')}`",
                f"- **MP4:** `{result.path}`",
                "",
                "**Generation:** succeeded",
            ]
        )
    else:
        assert isinstance(result, Failure)
        lines.extend(
            [
                f"- **Path taken:** `{result.path_taken}`",
                f"- **Attempts made:** {result.attempts_made}",
                "",
                "**Generation:** failed",
                "",
                f"> {result.message}",
            ]
        )
        if result.last_error:
            lines.extend(["", "<details>", "<summary>Operator detail</summary>", "", "```", result.last_error[:4000], "```", "</details>"])

    lines.extend(["", "### HITL grading — 10/10", ""])
    lines.extend(_checklist_lines(entry.success_10))

    lines.extend(["", "### HITL grading — 5/10 (floor)", ""])
    lines.extend(_checklist_lines(entry.success_5))

    lines.extend(["", "### Failure modes to check", ""])
    lines.extend(_checklist_lines(entry.failure_modes))

    return lines


def _checklist_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- [ ] _(none listed in eval file)_"]
    return [f"- [ ] {item}" for item in items]
