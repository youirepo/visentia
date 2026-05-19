# Two-Layer Validation for LLM-Generated Manim Code

LLM-generated Manim code is validated in **two layers** before it reaches the Tutor: a fast static linter that checks the Python AST without executing it, followed by a sandboxed Manim render with an error-context repair loop back to the LLM. Templates short-circuit the entire apparatus.

## Status

Accepted (2026-05-19).

## Context

The 2026-05-19 codegen probe (`prototype/results.md`) ran three eval prompts through Gemini 3 Flash Preview at temperature 1 and observed four Flash-attributable bugs across the three files:

- EV-001: hallucinated symbol (`CYAN` is not a Manim CE constant)
- EV-001: two missing raw-string prefixes on `MathTex(...)` (Python's `\t` collapsing to a tab character)
- EV-003: invalid kwarg (`stroke_dash_array` on `Rectangle`, which doesn't accept it)

All four are detectable by static analysis. None were caught by Manim until render time. Per-run bug counts varied (3 / 0 / 1) at temperature 1, so any single render is non-trivially likely to fail. The eval set is three prompts and already surfaced this — production will see more.

This means the freeform codegen path **needs a validation layer**, and the question is what shape it takes. The probe's evidence was specific enough to make the answer concrete.

## Decision

The freeform-codegen path through the pipeline runs LLM output through two validation layers in order. Templates skip both.

### Layer 1 — Static lint (no execution)

Parses Flash's Python output as an AST and checks, at minimum:

- **Symbol resolution against a curated Manim CE allowlist** — every referenced top-level name must exist in the Manim CE public API. Catches the EV-001 `CYAN` class of bug.
- **Kwarg validation per known class** — `Rectangle()`, `Polygon()`, etc. have a fixed kwarg set. Catches the EV-003 `stroke_dash_array` class of bug.
- **Raw-string sniffer for `MathTex` / `Tex` / `MarkupText` arguments** — any string literal containing `\t`, `\n`, `\r`, `\f`, `\b` without an `r` prefix is flagged. Catches the EV-001 `\text{...}` class of bug, which is the highest-frequency LLM Manim failure mode because LaTeX uses backslashes everywhere.
- **Import completeness** — `from manim import *` (or explicit equivalents) must be present.
- **Scene-class shape** — at least one `class X(Scene)` with a `construct(self)` method.

Cost: milliseconds. Safety: total — no LLM-generated code is executed. Failures route to the repair loop with the lint error as context.

### Layer 2 — Sandboxed render (execution)

If Layer 1 passes, run `manim` in an isolated subprocess with:

- Isolated working directory per run (`/tmp/visentia-renders/<run-id>/`)
- Wall-clock timeout (60–120s; Manim renders can be slow, but a hang indicates a runaway construct)
- Captured stderr / stdout for error context
- Resource caps as needed (`ulimit`; container in production)

If the render fails, the traceback is fed back to Flash with a repair prompt — *"Your previous code produced this error: `<traceback>`. Return the corrected file."* — and the loop retries up to **3 attempts**. After that, the pipeline either falls back to a template (if the Math Content Type classifier can route the prompt to one) or surfaces a graceful failure to the Tutor.

### Templates short-circuit both layers

When the Math Content Type classifier routes a prompt to a template, Flash's job is to fill parameters as a JSON blob against a schema. Validation collapses to schema validation (cheap, deterministic, no LLM-code execution at all). The two-layer apparatus is **insurance for the freeform fallback path** — the path the probe showed needs insurance.

## Considered Options

**Single-layer sandbox only.** Skip static lint, run everything in the sandbox. Rejected: every Manim render costs seconds-to-minutes, and the probe's bug classes (undefined symbol, wrong kwarg, missing `r` prefix) are all detectable in milliseconds without execution. Burning a render cycle on a typo is wasteful when retries are bounded and slow.

**Single-layer static only.** Skip the sandbox, lint only. Rejected: static analysis can't catch every runtime failure (value-dependent errors, missing animation choreography, infinite loops in `construct()`). Real ground-truth signal requires execution.

**Lint-and-fail without LLM repair.** Reject failed code outright instead of looping back to Flash. Rejected: probe evidence shows Flash's bugs are surface-level and recoverable when given error context. A repair loop is the standard agentic codegen pattern and turns the bug rate from "render fails" into "render takes 1.x attempts on average."

**Build the linter later, once the pipeline is wired.** Rejected: the same linter pays for itself a second time during template authoring, where every template starts as Python that fails until it doesn't. Build it early and it accelerates template-library v0.1, which is itself the v0.1 critical path.

## Consequences

- **Two new components to build in v0.1**: a Manim CE static linter (module, not external dependency — needs to know our specific allowlist) and a sandboxed-render harness with error-context repair.
- **Manim CE API surface needs to be modelled.** The linter needs an allowlist of valid symbols and per-class kwarg sets. This is curated data, not generated, and must be kept in sync with the Manim CE version pinned in `requirements.txt`. Version-pin Manim explicitly.
- **The freeform fallback path has a measurable failure budget** — 3 repair attempts, then degrade. The Tutor never sees a raw stack trace; they see either a working video or a clean fallback message.
- **The repair-loop count is a quality signal.** If Flash routinely needs all 3 attempts on prompts that should have hit a template, that's evidence the template-library or classifier needs investment. Log attempt counts as a first-class metric.
- **Template path remains the default**, and templates are validated once at author-time (CI render of every template against fixture parameters) rather than per-request. Probe's "templates are the critical v0.1 priority" finding stays intact.
- **Provider abstraction inherits this for free.** When Gemini 3 Flash Preview gets replaced or supplemented (Claude Sonnet 4.5, Gemini 2.5 GA), the validation pipeline doesn't change — only the provider behind the codegen call does.
