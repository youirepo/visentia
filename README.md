# Visentia

Visentia helps a Tutor understand a math concept well enough to teach it. Type a Prompt; get back a narrated Manim explainer video.

Curriculum scope (MVP): NSW NESA Year 7–10 mathematics (Stage 4 + Stage 5).

> This is **v0.1 in flight**. Registered templates: **Triangle3Side** (EV-001), **WorkedExample** (EV-002 rate + unit cancellation), **AreaTransform** (EV-003 rhombus/trapezium derivations). Unmatched prompts use **freeform** codegen (issues [#7](https://github.com/youirepo/visentia/issues/7)–[#8](https://github.com/youirepo/visentia/issues/8)) with repair loop + template fallback.

## Quick start: install + run

Requirements:

- macOS or Linux
- Python 3.11+
- Manim CE's system dependencies — on macOS: `brew install ffmpeg cairo pango pkg-config py3cairo sox`. On Linux see [Manim's install docs](https://docs.manim.community/en/stable/installation.html) and add `sox` from your package manager.
- Internet access on first invocation per unique narration line (`edge-tts` reaches Microsoft's free read-aloud endpoint; results are cached locally under `media/voiceovers/`).

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Configure your API key. Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com/app/apikey), then put it in a `.env` at the project root:

```bash
echo "GOOGLE_API_KEY=your-key-here" >> .env
```

(The CLI auto-loads `.env` on startup via `python-dotenv`. `GEMINI_API_KEY` and `GOOGLE_AI_STUDIO_API_KEY` are recognized aliases.)

Run:

```bash
visentia "If you have a triangle not to scale with the 3 sides given, how to know if it is right angle or acute or obtuse?"
```

The MP4 is written under `./videos/` by default. Use `--output-dir DIR` to override. A sidecar `<mp4>.json` next to the video records the active LLM provider, the classification result, the voice used, and the original prompt.

Web UI:

```bash
visentia serve
```

Open http://127.0.0.1:8765 — enter a Prompt, watch progress while it generates, then play the video in the page. Metadata from the sidecar is shown below the player. Use `--port` to change the port.

Eval harness (human grading):

```bash
visentia eval
visentia eval --ids EV-001
export VISENTIA_GEMINI_MODEL=gemini-2.5-flash
```

Runs every entry in [`docs/evals/seed.md`](docs/evals/seed.md) through the pipeline, writes MP4s under `./eval-runs/<timestamp>/`, and emits `./eval-reports/eval-<timestamp>.md` with classifier accuracy, pipeline metadata, and tick-box checklists for 10/10, 5/10, and failure modes.

Google AI Studio's **free tier** caps requests per model per day (e.g. 20/day for `gemini-3-flash`). A full seed eval uses several LLM calls per entry (classify, param fill, and sometimes freeform repair). On `429 RESOURCE_EXHAUSTED`, wait for the daily reset, enable billing on the project, switch models via `VISENTIA_GEMINI_MODEL`, or run fewer entries with `--ids`.

Tests:

```bash
pytest
```

## Project orientation

| File | What it is |
|---|---|
| [`CONTEXT.md`](./CONTEXT.md) | Domain glossary (Tutor, Prompt, Explainer Artifact, Math Content Type, Mode). Read this first. |
| [`docs/adr/`](./docs/adr/) | Architectural Decision Records. 0001 (explainer artifact concept), 0002 (video-first MVP via Manim), 0003 (two-layer validation pipeline for LLM codegen). |
| [`docs/agents/manim-ce-api-model.md`](./docs/agents/manim-ce-api-model.md) | How to refresh the StaticLinter's Manim CE API snapshot when Manim is bumped. |
| [`docs/evals/seed.md`](./docs/evals/seed.md) | The seed eval set — real Tutor prompts with graded success criteria. Visentia's regression suite. |
| [`prototype/results.md`](./prototype/results.md) | The 2026-05-19 Gemini 3 Flash Preview + Manim codegen feasibility probe. |
| GitHub [issue #1](https://github.com/youirepo/visentia/issues/1) | v0.1 PRD. |
| GitHub issues [#2–#13](https://github.com/youirepo/visentia/issues) | v0.1 work decomposition (vertical tracer-bullet slices). |

## Tech stack (v0.1)

All free-tier: Gemini 3 Flash Preview (`gemini-3-flash-preview`) via Google AI Studio for LLM, `edge-tts` for narration, Manim Community Edition for rendering. A provider abstraction layer (slice [#4](https://github.com/youirepo/visentia/issues/4)) keeps the LLM swappable from day one.
