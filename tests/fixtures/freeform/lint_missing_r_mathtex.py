from manim import *


class LintMissingR(Scene):
    def construct(self):
        m = MathTex("\text{hello}")
        self.add(m)
