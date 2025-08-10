from manim import *
import numpy as np

from manim import *

class Introduction(Scene):
    def construct(self):
        # Title
        series_name = Text("Mastering Introduction to Derivatives", color=BLUE).scale(1.5)
        episode_name = Text("Episode: Foundations of Introduction to Derivatives", color=YELLOW).next_to(series_name, DOWN)
        
        self.play(Write(series_name), Write(episode_name))
        self.wait(2)
        self.play(FadeOut(series_name), FadeOut(episode_name))
        
        # Intro
        intro_text = Text("Welcome to this comprehensive exploration of Introduction to Derivatives.").scale(0.8)
        self.play(Write(intro_text))
        self.wait(2)
        
        # Description
        description = Text("In this episode, we'll examine the fundamental aspects that make this subject both fascinating and important for understanding our world.", t2c={"fundamental aspects": BLUE}).scale(0.8)
        description.next_to(intro_text, DOWN)
        self.play(ReplacementTransform(intro_text, description))
        self.wait(2)

        # More info
        more_info = Text("Introduction to Derivatives represents a critical area of study that impacts multiple aspects of human knowledge and experience. By understanding these core principles, we build a foundation for deeper learning and practical application.", t2c={"Introduction to Derivatives": BLUE, "critical area of study": YELLOW}).scale(0.8)
        more_info.next_to(description, DOWN)
        self.play(ReplacementTransform(description, more_info))
        self.wait(2)

        # Conclusion
        conclusion = Text("Thank you for joining this educational journey. Keep questioning, keep learning, and keep growing.", color=GREEN).scale(1)
        self.play(FadeInFrom(conclusion, UP))
        self.wait(2)

        self.play(FadeOut(more_info), FadeOut(conclusion))

if __name__ == "__main__":
    scene = FoundationsofIntroductiontoDerivativesScene()
    scene.render()
