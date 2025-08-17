from manim import *

class TestFontSize(Scene):
    def construct(self):
        # Test different font sizes
        title = Text("Test Font Sizes", font_size=72, color=WHITE)
        subtitle = Text("Checking visibility", font_size=48, color=WHITE)
        small_text = Text("This should be visible", font_size=36, color=WHITE)
        tiny_text = Text("This might be too small", font_size=24, color=WHITE)
        
        # Position text elements
        title.to_edge(UP)
        subtitle.next_to(title, DOWN, buff=0.5)
        small_text.next_to(subtitle, DOWN, buff=0.5)
        tiny_text.next_to(small_text, DOWN, buff=0.5)
        
        # Animate them in
        self.play(FadeIn(title))
        self.wait(2)
        self.play(FadeIn(subtitle))
        self.wait(2)
        self.play(FadeIn(small_text))
        self.wait(2)
        self.play(FadeIn(tiny_text))
        self.wait(3)
        
        # Fade everything out
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(small_text), FadeOut(tiny_text))
        self.wait(1)
