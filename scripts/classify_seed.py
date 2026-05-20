"""Manual sanity check for the ContentClassifier against docs/evals/seed.md.

This is *not* the eval harness (slice #9) — it's a quick smoke that asks: "does the
classifier put each seed entry in the same Math Content Type the eval file states?"
Run it occasionally to catch classifier drift when changing prompts or models. The
eval harness will subsume this check automatically once it lands.

Usage:
    python scripts/classify_seed.py

Requires `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) in the environment or in .env.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from visentia.classifier import ContentClassifier
from visentia.llm.gemini import Gemini

SEED_PATH = Path(__file__).resolve().parent.parent / "docs" / "evals" / "seed.md"


@dataclass
class SeedEntry:
    id: str
    prompt: str
    expected_math_content_type: str


def _parse_seed(seed_md: str) -> list[SeedEntry]:
    """Pull (id, prompt, math_content_type) out of seed.md's YAML-in-code-fence entries.

    Format is structured but not standard YAML (uses Markdown sections); a tiny regex
    parser is plenty here — slice #9's eval harness will replace this with a real parser.
    """

    entries: list[SeedEntry] = []
    block_re = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
    for raw in block_re.findall(seed_md):
        id_match = re.search(r"^id:\s*(\S+)", raw, re.MULTILINE)
        type_match = re.search(r"^math_content_type:\s*(\S+)", raw, re.MULTILINE)
        prompt_match = re.search(r"^prompt:\s*\|\n((?:  .+\n)+)", raw, re.MULTILINE)
        if not (id_match and type_match and prompt_match):
            continue
        prompt = " ".join(line.strip() for line in prompt_match.group(1).splitlines())
        entries.append(
            SeedEntry(
                id=id_match.group(1),
                prompt=prompt,
                expected_math_content_type=type_match.group(1),
            )
        )
    return entries


def main() -> int:
    load_dotenv()

    entries = _parse_seed(SEED_PATH.read_text())
    if not entries:
        print(f"No seed entries parsed from {SEED_PATH}", file=sys.stderr)
        return 1

    classifier = ContentClassifier(Gemini())

    print(f"Classifying {len(entries)} seed entries via Gemini...\n")
    correct = 0
    for entry in entries:
        try:
            result = classifier.classify(entry.prompt)
        except Exception as exc:
            print(f"  {entry.id}: ERROR - {exc}")
            continue

        ok = result.math_content_type == entry.expected_math_content_type
        mark = "OK" if ok else "MISS"
        if ok:
            correct += 1
        print(
            f"  {entry.id}: {mark:4s}  classifier={result.math_content_type:13s} "
            f"expected={entry.expected_math_content_type:13s} mode={result.suggested_mode}"
        )

    print(f"\nResult: {correct}/{len(entries)} classified correctly.")
    return 0 if correct == len(entries) else 2


if __name__ == "__main__":
    raise SystemExit(main())
