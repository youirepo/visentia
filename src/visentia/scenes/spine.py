"""Placeholder Manim Scene used by the spine slice.

This Scene exists only to prove the architectural skeleton connects end-to-end. It ignores
the Prompt entirely and renders a fixed animation: a blue circle is created, then shifted
right. Subsequent slices replace this Scene with classifier-driven template renders.

Adapted from prototype/smoke.py, which served the same purpose during the feasibility probe.
"""

from manim import BLUE, RIGHT, Circle, Create, Scene


class SpineScene(Scene):
    def construct(self) -> None:
        circle = Circle(color=BLUE).set_fill(BLUE, opacity=0.5)
        self.play(Create(circle))
        self.play(circle.animate.shift(RIGHT * 2))
        self.wait()
