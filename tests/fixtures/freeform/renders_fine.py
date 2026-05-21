from manim import *


class RendersFine(Scene):
    def construct(self):
        title = Text("Visentia freeform fixture", font_size=36)
        self.play(Write(title))
        self.wait(0.1)
