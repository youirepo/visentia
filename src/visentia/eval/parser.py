"""Parse eval markdown files (docs/evals/seed.md format)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class EvalEntry:
    id: str
    prompt: str
    math_content_type: str
    expected_artifact_form: str = ""
    success_10: list[str] = field(default_factory=list)
    success_5: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)
    title: str = ""


def parse_eval_file(path: Path) -> list[EvalEntry]:
    """Parse all eval entries from a seed-style markdown file."""

    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?=^## EV-\d+)", text, flags=re.MULTILINE)
    entries: list[EvalEntry] = []

    for chunk in chunks:
        if not chunk.strip().startswith("## EV-"):
            continue
        entry = _parse_entry_chunk(chunk)
        if entry is not None:
            entries.append(entry)

    if not entries:
        raise ValueError(f"No eval entries found in {path}")

    return entries


def _parse_entry_chunk(chunk: str) -> EvalEntry | None:
    header = re.match(r"^## (EV-\d+)\s*[—-]\s*(.+)$", chunk, re.MULTILINE)
    if not header:
        return None

    entry_id = header.group(1)
    title = header.group(2).strip()

    yaml_match = re.search(r"```yaml\n(.*?)\n```", chunk, re.DOTALL)
    if not yaml_match:
        return None

    yaml_block = yaml_match.group(1)
    id_in_yaml = _yaml_field(yaml_block, "id") or entry_id
    math_type = _yaml_field(yaml_block, "math_content_type")
    artifact_form = _yaml_field(yaml_block, "expected_artifact_form") or ""
    prompt = _yaml_multiline_prompt(yaml_block)

    if not math_type or not prompt:
        return None

    success_10 = _bullet_list_after(chunk, r"\*\*10/10\*\*")
    success_5 = _bullet_list_after(chunk, r"\*\*5/10\*\*")
    failure_modes = _bullet_list_after_heading(chunk, "Failure modes")

    return EvalEntry(
        id=id_in_yaml,
        title=title,
        prompt=prompt,
        math_content_type=math_type,
        expected_artifact_form=artifact_form,
        success_10=success_10,
        success_5=success_5,
        failure_modes=failure_modes,
    )


def _yaml_field(block: str, key: str) -> str:
    match = re.search(rf"^{key}:\s*(.+)$", block, re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip().strip('"')


def _yaml_multiline_prompt(block: str) -> str:
    match = re.search(r"^prompt:\s*\|\n((?:  .+\n)+)", block, re.MULTILINE)
    if not match:
        single = re.search(r'^prompt:\s*"(.*)"\s*$', block, re.MULTILINE)
        if single:
            return single.group(1).strip()
        return ""
    return " ".join(line.strip() for line in match.group(1).splitlines())


def _bullet_list_after(text: str, marker_pattern: str) -> list[str]:
    match = re.search(
        rf"{marker_pattern}\s*:?\s*\n((?:- .+(?:\n|$))+)",
        text,
        re.MULTILINE,
    )
    if not match:
        return []
    return _lines_to_bullets(match.group(1))


def _bullet_list_after_heading(text: str, heading_substring: str) -> list[str]:
    match = re.search(
        rf"###[^\n]*{re.escape(heading_substring)}[^\n]*\n+((?:- .+(?:\n|$))+)",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    if not match:
        return []
    return _lines_to_bullets(match.group(1))


def _lines_to_bullets(block: str) -> list[str]:
    items: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items
