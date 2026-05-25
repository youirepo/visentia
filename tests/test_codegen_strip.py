"""Codegen output normalization."""

from visentia.freeform.codegen import _strip_code_fences


def test_strip_closed_fence() -> None:
    raw = "Here is the file:\n```python\nfrom manim import *\nclass S(Scene):\n    pass\n```"
    assert _strip_code_fences(raw).startswith("from manim import")


def test_strip_preamble_without_fence() -> None:
    raw = (
        "Sure! Below is the Manim scene.\n\n"
        "from manim import *\n\nclass MyScene(Scene):\n    def construct(self):\n        pass\n"
    )
    out = _strip_code_fences(raw)
    assert out.startswith("from manim import")
    assert "Sure!" not in out
