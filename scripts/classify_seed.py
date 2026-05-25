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

import sys
from pathlib import Path

from dotenv import load_dotenv

from visentia.classifier import ContentClassifier
from visentia.eval.parser import parse_eval_file
from visentia.llm.gemini import Gemini

SEED_PATH = Path(__file__).resolve().parent.parent / "docs" / "evals" / "seed.md"


def main() -> int:
    load_dotenv()

    entries = parse_eval_file(SEED_PATH)
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

        ok = result.math_content_type == entry.math_content_type
        mark = "OK" if ok else "MISS"
        if ok:
            correct += 1
        print(
            f"  {entry.id}: {mark:4s}  classifier={result.math_content_type:13s} "
            f"expected={entry.math_content_type:13s} mode={result.suggested_mode}"
        )

    print(f"\nResult: {correct}/{len(entries)} classified correctly.")
    return 0 if correct == len(entries) else 2


if __name__ == "__main__":
    raise SystemExit(main())
