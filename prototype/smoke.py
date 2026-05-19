from manim import *
class Smoke(Scene):
    def construct(self):
        c = Circle(color=BLUE).set_fill(BLUE, opacity=0.5)
        self.play(Create(c))
        self.play(c.animate.shift(RIGHT * 2))
        self.wait()
