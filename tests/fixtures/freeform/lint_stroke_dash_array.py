from manim import *


class LintStrokeDash(Scene):
    def construct(self):
        r = Rectangle(width=2, height=1, stroke_dash_array=[5, 5])
        self.add(r)
