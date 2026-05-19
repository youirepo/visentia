"""Result types returned by `RepairOrchestrator.generate_video`.

These types are public and stable across slices — subsequent slices (LLM, freeform path,
repair loop) add fields rather than reshape the union. AppShell pattern-matches on this
union to decide what to show the Tutor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Mp4:
    """Successful generation. `path` points at a non-zero-byte MP4 on disk."""

    path: Path
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Failure:
    """Generation failed after exhausting the retry budget.

    `message` is plain-language and safe to show the Tutor directly — never a stacktrace.
    `attempts_made` and `last_error` are operator-facing detail for logs.
    """

    message: str
    attempts_made: int = 0
    last_error: str | None = None


GenerateResult = Mp4 | Failure
