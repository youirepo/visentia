"""Curated Manim CE public API model — version-aligned with `requirements.txt`."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path

MANIM_CE_VERSION = "0.19.0"
_DATA_FILE = "manim_ce_0_19_0.json"

LATEX_MOBS = frozenset({"MathTex", "Tex", "MarkupText"})
SCENE_BASES = frozenset({"Scene", "MovingCameraScene", "VoiceoverScene", "ThreeDScene"})


@lru_cache(maxsize=1)
def load_api_model() -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    raw = resources.files("visentia.freeform.data").joinpath(_DATA_FILE).read_text(encoding="utf-8")
    data = json.loads(raw)
    if data.get("manim_version") != MANIM_CE_VERSION:
        raise RuntimeError(
            f"API model version {data.get('manim_version')!r} does not match pin {MANIM_CE_VERSION!r}"
        )
    symbols = frozenset(data["symbols"])
    class_kwargs = {name: frozenset(kwargs) for name, kwargs in data["class_kwargs"].items()}
    return symbols, class_kwargs


def data_file_path() -> Path:
    """Filesystem path to the bundled JSON (for docs / refresh scripts)."""

    return Path(resources.files("visentia.freeform.data").joinpath(_DATA_FILE))
