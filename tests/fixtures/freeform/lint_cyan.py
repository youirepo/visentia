from manim import *


class LintCyan(Scene):
    def construct(self):
        t = Text("x", color=CYAN)
        self.add(t)
