#!/usr/bin/env python3
"""Regenerate `src/visentia/freeform/data/manim_ce_*.json` from the installed Manim pin."""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path

import manim
from manim import Mobject, VMobject

REPO_ROOT = Path(__file__).resolve().parents[1]
API_MODEL_PY = REPO_ROOT / "src/visentia/freeform/api_model.py"
DATA_DIR = REPO_ROOT / "src/visentia/freeform/data"

LINTER_CLASSES = [
    "Rectangle",
    "Polygon",
    "Line",
    "Text",
    "MathTex",
    "Tex",
    "MarkupText",
    "Circle",
    "Dot",
    "VGroup",
    "Arrow",
]


def _params(cls: type) -> set[str]:
    return {
        p
        for p in inspect.signature(cls.__init__).parameters
        if p not in ("self", "args", "kwargs")
    }


def _kwargs_for(cls: type) -> list[str]:
    own = _params(cls)
    if issubclass(cls, VMobject):
        own |= _params(VMobject)
    if issubclass(cls, Mobject):
        own |= _params(Mobject)
    return sorted(own)


def main() -> None:
    version = manim.__version__
    ns: dict = {}
    exec("from manim import *", ns)
    symbols = sorted(k for k in ns if not k.startswith("_"))

    class_kwargs = {name: _kwargs_for(ns[name]) for name in LINTER_CLASSES}

    out = DATA_DIR / f"manim_ce_{version.replace('.', '_')}.json"
    out.write_text(
        json.dumps(
            {"manim_version": version, "symbols": symbols, "class_kwargs": class_kwargs},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out} ({len(symbols)} symbols, {len(class_kwargs)} classes)")

    text = API_MODEL_PY.read_text(encoding="utf-8")
    text = re.sub(
        r'MANIM_CE_VERSION = "[^"]+"',
        f'MANIM_CE_VERSION = "{version}"',
        text,
        count=1,
    )
    text = re.sub(
        r'_DATA_FILE = "manim_ce_[^"]+\.json"',
        f'_DATA_FILE = "{out.name}"',
        text,
        count=1,
    )
    API_MODEL_PY.write_text(text, encoding="utf-8")
    print(f"Updated {API_MODEL_PY}")


if __name__ == "__main__":
    main()
