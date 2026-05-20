"""AppShell: CLI entry point for generate and serve commands.

Deliberately thin per the PRD — argument parsing, .env loading, progress messaging,
dispatch to the orchestrator or web server. No pipeline logic lives here.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from visentia.orchestrator import RepairOrchestrator, sidecar_path_for
from visentia.results import Failure, Mp4


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    load_dotenv()

    if argv and argv[0] == "serve":
        return _serve_main(argv[1:])

    return _generate_main(argv)


def _generate_main(argv: list[str]) -> int:
    parser = _build_generate_parser()
    args = parser.parse_args(argv)

    _configure_logging(verbose=args.verbose)

    print(f"Visentia: generating Explainer Artifact for prompt: {args.prompt!r}")
    print("Visentia: classifying...")

    orchestrator = RepairOrchestrator()
    result = orchestrator.generate_video(args.prompt, output_dir=args.output_dir)

    if isinstance(result, Mp4):
        classification = result.metadata.get("classification", {})
        provider = result.metadata.get("llm_provider", "?")
        model = result.metadata.get("llm_model", "?")
        print(
            f"Visentia: classified as {classification.get('math_content_type')!r} "
            f"({classification.get('suggested_mode')} Mode) via {provider} / {model}"
        )
        print(f"Visentia: done. MP4 written to {result.path}")
        print(f"           Sidecar metadata: {sidecar_path_for(result.path)}")
        return 0

    if isinstance(result, Failure):
        print(f"Visentia: generation failed. {result.message}", file=sys.stderr)
        if result.last_error:
            print(f"  (operator detail: {result.last_error})", file=sys.stderr)
        return 1

    raise AssertionError(f"Unexpected result type from orchestrator: {type(result).__name__}")


def _serve_main(argv: list[str]) -> int:
    from visentia.web_server import run_server

    parser = _build_serve_parser()
    args = parser.parse_args(argv)
    _configure_logging(verbose=args.verbose)

    try:
        run_server(host=args.host, port=args.port, output_dir=args.output_dir)
    except KeyboardInterrupt:
        print("\nVisentia: server stopped.")
    return 0


def _build_generate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="visentia",
        description=(
            "Visentia v0.1: generate a narrated Manim Explainer Artifact from a natural-language "
            "Prompt, or start the localhost web UI with `visentia serve`."
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
        help="Directory to write the MP4 (and sidecar JSON) to. Defaults to ./videos.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show INFO-level logs (classification, sidecar path, etc.).",
    )
    return parser


def _build_serve_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="visentia serve",
        description="Start the Visentia localhost web UI.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to bind (default: 8765).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for web-generated MP4s. Defaults to ./videos.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show INFO-level server logs.",
    )
    return parser


def _configure_logging(*, verbose: bool) -> None:
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


if __name__ == "__main__":
    raise SystemExit(main())
