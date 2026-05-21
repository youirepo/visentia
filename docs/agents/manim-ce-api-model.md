# Manim CE API model (StaticLinter)

The freeform `StaticLinter` validates LLM-generated Manim against a **curated** snapshot of the Manim Community Edition public API. The snapshot must match the `manim==…` pin in `requirements.txt`.

## Bundled data

- **Version:** `0.19.0` (see `MANIM_CE_VERSION` in `src/visentia/freeform/api_model.py`)
- **File:** `src/visentia/freeform/data/manim_ce_0_19_0.json`
  - `symbols` — names available after `from manim import *` (578 entries for 0.19.0)
  - `class_kwargs` — allowed keyword arguments for common mobject classes (`Rectangle`, `Polygon`, `Line`, `Text`, `MathTex`, …)

## When to refresh

Refresh the JSON whenever you **bump the Manim pin** in `requirements.txt` / `pyproject.toml`. Do not edit the allowlist by hand except for deliberate exclusions (e.g. probe-known hallucinations like `CYAN` stay absent because they are not in Manim).

## Regeneration (after a Manim bump)

From the repo root with the target Manim installed in `.venv`:

```bash
source .venv/bin/activate
python scripts/refresh_manim_api_model.py
```

The script:

1. `exec("from manim import *")` and records all public symbol names
2. Introspects `__init__` signatures for linter-covered classes and merges `VMobject` kwargs
3. Writes `src/visentia/freeform/data/manim_ce_<version>.json`
4. Updates `MANIM_CE_VERSION` and `_DATA_FILE` in `api_model.py` if the version changed

Then run:

```bash
pytest tests/test_static_linter.py tests/test_sandboxed_renderer.py -q
```

and fix any intentional allowlist exclusions documented in `test_static_linter.py`.

## HITL note

This data is **curated**, not LLM-generated. A human should skim the diff when Manim is bumped — especially new/changed kwargs on classes the linter checks.
