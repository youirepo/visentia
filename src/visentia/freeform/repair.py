"""Repair-context formatting for the freeform codegen loop."""

from __future__ import annotations

from visentia.freeform.linter import LintError, StaticLinter
from visentia.freeform.renderer import RenderFailure, RenderTimeout


def format_lint_repair_context(errors: list[LintError]) -> str:
    summary = StaticLinter.plain_language_summary(errors)
    details = "\n".join(f"- {e.message}" for e in errors[:8])
    return (
        "Your previous Manim Python file failed static validation.\n"
        f"{summary}\n"
        f"{details}\n"
        "Return the complete corrected file only."
    )


def format_render_repair_context(
    *,
    message: str,
    stderr: str = "",
) -> str:
    parts = [
        "Your previous Manim Python file failed to render.",
        message,
    ]
    if stderr.strip():
        tail = stderr.strip()[-2000:]
        parts.append(f"Manim output (truncated):\n{tail}")
    parts.append("Return the complete corrected file only.")
    return "\n".join(parts)


def format_render_result_context(result: RenderFailure | RenderTimeout) -> str:
    if isinstance(result, RenderTimeout):
        return format_render_repair_context(message=result.message, stderr=result.stderr)
    return format_render_repair_context(message=result.message, stderr=result.stderr)
