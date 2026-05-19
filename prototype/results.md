# Feasibility probe — Gemini 2.5 Flash + Manim

**Date:** 2026-05-19
**Question being answered:** Can Gemini 2.5 Flash produce Manim Community Edition code that renders and grades ≥5/10 on the three seed eval prompts in `docs/evals/seed.md`?

**Setup:**
- LLM: `gemini-3-flash-preview` via [aistudio.google.com](https://aistudio.google.com), temperature 1 (AI Studio's recommended default)
- System prompt: "expert in Manim Community Edition, output one Python file, target Australian Year 8, 30–60s aim, mathematically correct, no commentary"
- Renderer: Manim Community Edition v0.19.0 (local, macOS, `-ql` low-quality preview)
- Note: at temperature 1 there's meaningful run-to-run variability. EV-001 needed 3 fixes; EV-002 needed 0. For the production pipeline we'd test lower temperatures (0.0–0.4) for codegen reliability — but at this probe stage we're testing capability, not config-tuning.
- Note: `gemini-3-flash-preview` is a preview model. Production should plan a fallback to a stable model (Gemini 2.5 Flash GA, or Claude Sonnet 4.5 as the documented upgrade path) in case the preview shifts behaviour or is deprecated.

---

## EV-001 — Converse of Pythagoras (attempt 1)

**Generated file:** `prototype/EV-flash-001.py`
**Rendered:** Yes, after 3 manual fixes
**Grade:** ~6.5/10
**Verdict:** Yellow light — viable, with prompt-engineering and a syntax-repair loop needed

### Fixes required to render

| Issue | Location | Fix |
|---|---|---|
| `CYAN` color symbol hallucinated (not in Manim CE palette) | lines 48–49 | `CYAN` → `TEAL` |
| Missing raw-string prefix on MathTex containing `\text{...}` (Python turned `\t` into tab) | line 33 | added `r` prefix |
| Same `\text` issue | line 79 | added `r` prefix |

All three are detectable by static analysis before rendering. In the production pipeline they should be caught by a pre-render linter and either auto-fixed or sent back to the LLM for repair.

### What worked

- **Math is correct.** Inequality directions: $c^2 = a^2+b^2$ (right), $c^2 < a^2+b^2$ (acute), $c^2 > a^2+b^2$ (obtuse) — all correct
- Worked example (5, 7, 10) arithmetically sound: $c^2 = 100$, $a^2+b^2 = 74$, $100 > 74$ → obtuse ✓
- Visual layout clean: triangle, comparison strip, three colour-coded cases, worked example sequence
- **Tutor's verdict:** "honestly, for a first pass, great"

### What's weak vs `success_10`

- **No parameter sweep** — the success_10 ideal (drag third side, watch angle morph) isn't there; Flash defaulted to a static linear walkthrough
- **Only one numerical example** (5, 7, 10) instead of three ((3,4,5), (5,5,6), (5,5,7))
- **No angle labelling at the relevant vertex** — explains how to classify "the triangle" but doesn't visually flag which angle is the one being classified (Tutor observation)
- **Doesn't explain *why* the inequality rules hold** — just states them (Tutor observation)
- **Pacing too fast** — `self.wait()` durations too short for Year 8 absorption (Tutor observation)
- **`c` label spacing** — slightly too close to its side; trivial layout tweak

### Failure modes (per seed.md) — all avoided

- ✓ Converse-vs-Pythagoras distinction maintained
- ✓ Inequality directions correct
- ✓ Sides sorted by length in the example
- ✓ Valid triangle in example (triangle inequality holds for 5-7-10)

### What this tells us about Flash

1. **Math correctness is reliable** for Year 8 Pythagoras content
2. **Default pedagogical pattern is "linear lecture"** — needs explicit prompt-engineering to push toward parameter exploration, multiple examples, "why" explanations, slower pacing
3. **Syntactic API failures are bounded and recoverable** — hallucinated symbols (CYAN) and Python/LaTeX string escaping are both linter-fixable
4. **No deeper conceptual failure** — Flash didn't confuse the converse with Pythagoras, didn't invert the inequalities, didn't produce nonsense

---

## EV-002 — Rate conversion (attempt 1)

**Generated file:** `prototype/EV-flash-002.py`
**Rendered:** Yes, after fixing one copy-paste artifact (not a Flash bug)
**Grade:** ~7/10
**Verdict:** Green-leaning — math correct, structure clean, **zero Flash-attributable syntax errors**

### Fixes required to render

| Issue | Location | Cause | Fix |
|---|---|---|---|
| Missing `from manim import *` | line 1 | User dropped the import line during copy-paste from AI Studio | Re-added the import |

**Zero Flash-attributable bugs** on EV-002, vs three on EV-001. Flash's per-run reliability varies, but the failure mode of the manual probe (copy-paste from a web UI) is itself an artifact that wouldn't exist in the production pipeline (which would use the API directly).

### What worked

- **Math is correct.** $4.5\text{ kg} \to 4500\text{ g}$, $4500/100 = 45$ lots, $45 \times \$5 = \$225$ — all arithmetic sound
- **Procedural structure**: Step 1 (convert units) → Step 2 (count "lots of 100g") → Step 3 (multiply by price) → general formula. Clear and pedagogically sensible for Year 8.
- **Concludes with a general rule** (Total = Total Quantity ÷ Rate Quantity × Rate Price) — matches `success_10`'s "general procedure stated in plain English" criterion that EV-001 missed
- **Tutor's verdict:** "honestly, great, even better than the first one. It explained it step-by-step and then finished with a formula."

### What's weak vs `success_10`

- **No animated unit cancellation.** The eval's signature pedagogical move (units physically cancelling via strike-through animation) isn't there. Flash showed the conversion as a separate numerical step but didn't reach for the dimensional-analysis flourish that makes the insight transferable.
- **Approached as "count lots of 100g"** rather than fraction multiplication with cancellation. Defensible alternative pedagogy but different from the eval's expected approach.

### Failure modes (per seed.md) — all avoided

- ✓ kg → g conversion correctly applied (not the "$0.225 forgot to convert" trap)
- ✓ Rate not inverted
- ✓ Units tracked throughout

### What this adds to what we knew

- Flash's math reliability extends beyond Relationship prompts (EV-001) to Procedure prompts (EV-002) — **two for two on math correctness**
- Output quality varies between runs — EV-001 needed three fixes; EV-002 needed zero. The production pipeline still needs a syntax-validation safety net for the cases when Flash slips up.
- Flash continues not to reach for sophisticated pedagogical patterns unprompted. Both EV-001 (parameter sweep) and EV-002 (animated unit cancellation) would need explicit prompt engineering to coax out. The pattern of "math right, structure clean, pedagogy serviceable but not stellar by default" is now confirmed across two prompt types.

---

## EV-003 — Area derivations, rhombus + trapezium (attempt 1)

**Generated file:** `prototype/EV-flash-003.py`
**Rendered:** Yes, after one Flash-attributable fix and one CLI-argument correction
**Grade:** ~5/10 (rhombus weak, trapezium acceptable)
**Verdict:** Confirms the template-library hypothesis decisively

### Fixes required to render

| Issue | Location | Cause | Fix |
|---|---|---|---|
| `stroke_dash_array=[5, 5]` invalid kwarg on `Rectangle` | line 30 | Flash invented an SVG/CSS-style API parameter that doesn't exist in Manim CE | Replaced with `DashedVMobject(Rectangle(...))` |
| Class name mismatch (`AreaDerivation` vs `AreaDerivations`) | CLI invocation | Off-by-one (the 's'); Manim warned but fell back to the only Scene in the file | Use the correct plural class name when invoking |
| Stale `__pycache__/EV-flash-003.cpython-313.pyc` masked the fix on re-run | n/a | Python bytecode cache invalidation didn't pick up the edit | Cleared `__pycache__/` |

The `.pyc` cache issue is itself a finding: a manual prototype workflow that repeatedly patches the same file accumulates state. Production pipeline uses per-run temp directories, so this class of bug disappears.

### What worked

- **Math is correct** for both formulas: Rhombus area = $\tfrac{1}{2} d_1 d_2$, Trapezium area = $\tfrac{1}{2}(a+b)h$
- **Trapezium section reaches for motion-as-proof**: duplicates the trapezium, rotates 180°, abuts to form a parallelogram. The pedagogical pattern the eval calls for.
- **Tutor's verdict on trapezium**: "did a good job at rotating and showing the parallelogram. It wasn't super clear but after looking at it, it made a bit more sense. Overall OK."

### What's weak vs `success_10`

- **Rhombus uses bounding-box argument, not cut-and-rearrange.** Flash drew a rectangle around the kite and claimed "area = half the rectangle" without showing *why* that's true. The cut-along-diagonals → rearrange-into-rectangle motion the eval calls for never happens.
- **Tutor's pedagogical critique on rhombus**: "it just states that it's half the rectangle without really explaining why. I mean it does draw the rectangle around it but I can't quite understand how that shows it is exactly half the rectangle."
- **Trapezium join is geometrically approximate.** The rotation centre + `next_to(..., RIGHT, buff=0)` placement doesn't quite produce a clean parallelogram — there are small visual gaps along the slanted join that undermine the "look, it's a parallelogram" claim.
- **Layout issue on rhombus**: x and y labels cross the diagonals they're labelling — needs more buff space or repositioning logic.

### Failure modes (per seed.md)

- ✓ Formulas correct (didn't drop the $\tfrac{1}{2}$ factor)
- ✓ Trapezium copy *does* rotate 180° (not translate)
- ✓ Shape congruence preserved during transformations (geometrically)
- ✗ **Treats rhombus as "fits in half a rectangle" rather than using the more elegant cut-and-rearrange-the-four-triangles derivation** — partially triggered; this was listed as a specific failure mode in `seed.md`

### What this adds — the load-bearing finding

**Pedagogical-pattern selection is non-deterministic within a single Scene.** Same prompt, same model run, two sub-derivations: rhombus got the weaker bounding-box argument; trapezium got the stronger motion-as-proof. Flash *can* produce motion-as-proof (trapezium proves this) but *doesn't reliably choose to*. This is the single strongest argument for the planned scene-template library — pre-built `AreaTransform` templates encode the cut-and-rearrange pedagogy at the *template* level, so the LLM only chooses *parameters*, not pedagogical patterns.

---

## Final verdict

**Green light for the LLM tier of the free stack** (Gemini 3 Flash Preview generating Manim Community Edition code), with one architectural elevation:

> **The scene-template library is no longer just "v0.1 hybrid component" — it's the critical v0.1 priority.** Three independent pieces of evidence from this probe (parameter-sweep gap in EV-001, unit-cancellation gap in EV-002, cut-and-rearrange gap in EV-003 rhombus) all point at the same finding: raw Flash-codegen produces *correct math* but *inconsistent pedagogy*. Templates are the layer that turns "OK" into "I'd actually use this."

### Findings confirmed across all three prompts

1. **Math correctness: 3/3.** Flash never produced wrong arithmetic or wrong inequality directions. This is the load-bearing property for a math-tutor tool, and it holds.
2. **Render success: 3/3 with bounded recoverable bugs.** Four Flash-attributable syntax errors total: hallucinated symbol (`CYAN`), missing raw-string prefix (×2), invalid kwarg (`stroke_dash_array`). All detectable by static analysis before render. None deep.
3. **Per-run bug count varies (3 / 0 / 1) at temperature 1.** Production pipeline should test lower temperatures (0.0–0.4) for codegen reliability.
4. **Default pedagogical pattern is "linear walkthrough with correct math."** Acceptable for the Tutor as a refresh-quality artifact (the Tutor said "would use" on all three) but consistently below the eval's `success_10` ideal.
5. **Pedagogical-pattern selection is unreliable even within a single Scene.** EV-003 demonstrated this directly. This invalidates "freeform codegen with prompt engineering alone" as a strategy and validates the template-first hybrid architecture.

### Architectural implications for v0.1

- **First-priority work: build the five scene templates** identified earlier — `Triangle3Side`, `AreaTransform`, `WorkedExample`, `NumberLine`, `CoordinatePlane`. The probe's pedagogy gaps map directly onto these primitives (`AreaTransform` would fix EV-003 rhombus; `Triangle3Side` with a parameter-sweep mode would lift EV-001; `WorkedExample` with animated unit cancellation would lift EV-002).
- **Second-priority work: build the Math Content Type classifier.** The classifier routes prompts to the right template, with freeform Manim as the fallback when no template matches.
- **Pre-render syntax validator is required, not optional.** Catches the four classes of Flash bug seen here (and others) before wasting a render cycle. Linter + retry-and-repair loop.
- **Provider abstraction is essential.** `gemini-3-flash-preview` is, by definition, a preview model — it can change behaviour or be deprecated. The codebase needs swap-points for Gemini 2.5 GA, Claude Sonnet 4.5, etc.
- **Use the API, not the AI Studio web UI.** This probe surfaced an entirely artificial failure mode (copy-paste dropping the import line in EV-002). The production pipeline avoids this trivially.

### Out of scope for this probe (still need verification, lower risk)

The probe was deliberately scoped to the load-bearing question: *can a free LLM produce usable Manim code for our eval set?* The following stack components are unverified and will be confirmed during v0.1 build:

- **`edge-tts` voiceover synthesis** — separate verification, no LLM judgment involved; either it produces acceptable Australian-English voice or we swap for another free TTS (Microsoft TTS, Piper, etc.).
- **Voiceover-to-animation timing** — solved by the `manim-voiceover` plugin, which is the standard approach in the Manim community. Worth a smoke test in build week 1.
- **End-to-end pipeline (prompt → MP4)** — wiring step. The LLM → Manim hop is now de-risked; the pipeline glue is conventional engineering.
- **Provider abstraction layer** — design work, not a feasibility question.
- **Desktop/CLI shell** — explicitly v0.2.

---

## Future-feature notes from the probe

### Follow-up Prompt (Tutor's idea, EV-003 feedback)

> *"Perhaps, this is another future use case, re-prompting to understand further the explanation."* — Tutor, after EV-003 rhombus

After watching an Explainer Artifact, the Tutor can issue a **follow-up Prompt** that takes the previous Prompt + previous Artifact + new question as context. The system either deepens the original explanation, replaces the artifact with a stronger one, or generates a complementary artifact addressing the specific gap. This is materially different from independent one-shot Prompts — it requires conversation memory and a way to reason about *what was already shown* so the new artifact doesn't repeat it.

Likely a v0.2 or v0.3 feature; should be reflected in CONTEXT.md's glossary if/when it moves from "future idea" to "planned." Not in scope for v0.1.

## Running decision

Superseded by the **Final verdict** section above (probe complete on 2026-05-19).
