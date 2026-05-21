from manim import *


class RaisesNameError(Scene):
    def construct(self):
        self.play(Create(NotARealMobject()))
