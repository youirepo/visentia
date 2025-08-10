from manim import *
import numpy as np

from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=48, color=YELLOW)
        self.play(Write(title))
        self.wait(2)
        self.play(title.animate.to_edge(UP))

        # Introduction
        intro_text = Text("Every breath you take, every bite of food you eat, exists because of one remarkable process: photosynthesis.", font_size=30)
        self.play(FadeIn(intro_text))
        self.wait(4)
        self.play(FadeOut(intro_text))

        # Photosynthesis Process
        process_text = Text("Photosynthesis is nature's way of capturing sunlight and converting it into chemical energy.", font_size=30)
        self.play(FadeIn(process_text))
        self.wait(4)
        self.play(FadeOut(process_text))

        # Photosynthesis Equation
        equation = MathTex("6CO_2 + 6H_2O + \text{light energy} \rightarrow C_6H_{12}O_6 + 6O_2 + \text{ATP}", font_size=36)
        self.play(Write(equation))
        self.wait(6)
        self.play(FadeOut(equation))

        # Explanation
        explanation_text = Text("This means: six molecules of carbon dioxide plus six molecules of water, using light energy, produce glucose, oxygen, and stored energy.", font_size=30)
        self.play(FadeIn(explanation_text))
        self.wait(6)
        self.play(FadeOut(explanation_text))

        # Visualization with Arrows
        co2 = Text("CO₂", color=BLUE).move_to(LEFT * 3)
        h2o = Text("H₂O", color=BLUE).next_to(co2, DOWN)
        light = Text("Light Energy", color=YELLOW).next_to(h2o, DOWN)
        glucose = Text("C₆H₁₂O₆", color=GREEN).move_to(RIGHT * 3)
        o2 = Text("O₂", color=GREEN).next_to(glucose, DOWN)
        atp = Text("ATP", color=GREEN).next_to(o2, DOWN)

        self.play(FadeIn(co2, h2o, light))
        self.wait(2)

        arrow1 = Arrow(start=co2.get_right(), end=glucose.get_left(), color=WHITE)
        arrow2 = Arrow(start=h2o.get_right(), end=o2.get_left(), color=WHITE)
        arrow3 = Arrow(start=light.get_right(), end=atp.get_left(), color=WHITE)
        self.play(Create(arrow1), Create(arrow2), Create(arrow3))
        self.wait(2)
        self.play(FadeIn(glucose, o2, atp))
        self.wait(4)
        self.play(FadeOut(co2, h2o, light, glucose, o2, atp, arrow1, arrow2, arrow3))

        # Chloroplasts and Chlorophyll
        chloroplast = Circle(radius=1, color=GREEN).shift(LEFT * 3)
        chlorophyll = Text("Chlorophyll", font_size=24, color=GREEN).next_to(chloroplast, DOWN)
        self.play(FadeIn(chloroplast), Write(chlorophyll))
        self.wait(2)

        light_absorb = Arrow(start=UP, end=chloroplast.get_top(), color=YELLOW)
        self.play(Create(light_absorb))
        self.wait(2)
        self.play(FadeOut(chloroplast, chlorophyll, light_absorb))

        # Summary
        summary_text = Text("Photosynthesis isn't just about making food for plants. It's the foundation of virtually every food chain.", font_size=30)
        self.play(FadeIn(summary_text))
        self.wait(6)
        self.play(FadeOut(summary_text))

        # Oxygen's Importance
        oxygen_text = Text("The oxygen we breathe is a product of photosynthesis, making complex life possible.", font_size=30)
        self.play(FadeIn(oxygen_text))
        self.wait(6)
        self.play(FadeOut(oxygen_text))

        # Conclusion
        conclusion_text = Text("In our next episode, we'll dive into how plants capture light energy and convert it into chemical energy.", font_size=30)
        self.play(FadeIn(conclusion_text))
        self.wait(4)
        self.play(FadeOut(conclusion_text))

        # End
        self.play(FadeOut(title))

if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
