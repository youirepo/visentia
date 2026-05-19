# Visentia

Visentia helps a Tutor understand a math concept well enough to teach it. Type a Prompt; get back a narrated Manim explainer video.

Curriculum scope (MVP): NSW NESA Year 7–10 mathematics (Stage 4 + Stage 5).

> This is **v0.1 in flight**. The current spine slice (issue [#2](https://github.com/youirepo/visentia/issues/2)) renders a placeholder Scene regardless of the Prompt. Real classifier-driven template renders land in subsequent slices.

## Quick start: install + run

Requirements:

- macOS or Linux
- Python 3.11+
- Manim CE's system dependencies — on macOS: `brew install ffmpeg cairo pango pkg-config py3cairo`. On Linux see [Manim's install docs](https://docs.manim.community/en/stable/installation.html).

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run:

```bash
visentia "If you have a triangle not to scale with the 3 sides given, how to know if it is right angle or acute or obtuse?"
```

The MP4 is written under `./videos/` by default. Use `--output-dir DIR` to override.

Tests:

```bash
pytest
```

## Project orientation

| File | What it is |
|---|---|
| [`CONTEXT.md`](./CONTEXT.md) | Domain glossary (Tutor, Prompt, Explainer Artifact, Math Content Type, Mode). Read this first. |
| [`docs/adr/`](./docs/adr/) | Architectural Decision Records. 0001 (explainer artifact concept), 0002 (video-first MVP via Manim), 0003 (two-layer validation pipeline for LLM codegen). |
| [`docs/evals/seed.md`](./docs/evals/seed.md) | The seed eval set — real Tutor prompts with graded success criteria. Visentia's regression suite. |
| [`prototype/results.md`](./prototype/results.md) | The 2026-05-19 Gemini 3 Flash Preview + Manim codegen feasibility probe. |
| GitHub [issue #1](https://github.com/youirepo/visentia/issues/1) | v0.1 PRD. |
| GitHub issues [#2–#13](https://github.com/youirepo/visentia/issues) | v0.1 work decomposition (vertical tracer-bullet slices). |

## Tech stack (v0.1)

All free-tier: Gemini 3 Flash Preview (`gemini-3-flash-preview`) via Google AI Studio for LLM, `edge-tts` for narration, Manim Community Edition for rendering. A provider abstraction layer (slice [#4](https://github.com/youirepo/visentia/issues/4)) keeps the LLM swappable from day one.
