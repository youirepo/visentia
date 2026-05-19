"""AppShell: the CLI entry point.

Deliberately thin per the PRD — argument parsing, progress messaging, dispatch to the
orchestrator, surface the result. No pipeline logic lives here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from visentia.orchestrator import RepairOrchestrator
from visentia.results import Failure, Mp4


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    print(f"Visentia: generating Explainer Artifact for prompt: {args.prompt!r}")

    orchestrator = RepairOrchestrator()
    result = orchestrator.generate_video(args.prompt, output_dir=args.output_dir)

    if isinstance(result, Mp4):
        print(f"Visentia: done. MP4 written to {result.path}")
        return 0

    if isinstance(result, Failure):
        print(f"Visentia: generation failed. {result.message}", file=sys.stderr)
        if result.last_error:
            print(f"  (operator detail: {result.last_error})", file=sys.stderr)
        return 1

    raise AssertionError(f"Unexpected result type from orchestrator: {type(result).__name__}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="visentia",
        description=(
            "Visentia v0.1: generate a narrated Manim Explainer Artifact from a natural-language "
            "Prompt. This slice (#2) is the spine — every prompt currently renders the same "
            "placeholder Scene."
        ),
    )
    parser.add_argument(
        "prompt",
        metavar="PROMPT",
        help="Natural-language Prompt describing the math concept to explain.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to write the MP4 to. Defaults to ./videos relative to the working directory.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
