from manim import *
import numpy as np

from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis",
                     font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(title))
        self.wait(2)

        # Introduction Text
        intro_text = Text("Every breath you take, every bite of food you eat, \
exists because of one remarkable process: photosynthesis.",
                          font_size=28, color=WHITE).next_to(title, DOWN)
        self.play(FadeIn(intro_text))
        self.wait(3)

        # Photosynthesis Process
        process_text = Text("Photosynthesis is nature's way of capturing sunlight\nand converting it into chemical energy.",
                            font_size=28, color=WHITE).next_to(intro_text, DOWN)
        self.play(FadeIn(process_text))
        self.wait(3)

        # Photosynthesis Equation
        equation = MathTex("6CO_2 + 6H_2O + \text{light energy} \\rightarrow C_6H_{12}O_6 + 6O_2 + \text{ATP}",
                           font_size=36, color=GREEN).next_to(process_text, DOWN, buff=1)
        self.play(Write(equation))
        self.wait(4)

        # Explanation of Equation
        explanation = Text("Six molecules of carbon dioxide plus six molecules\nof water, using light energy, produce one molecule\nof glucose, six molecules of oxygen, and stored\nchemical energy.",
                           font_size=28, color=WHITE).next_to(equation, DOWN, buff=1)
        self.play(FadeIn(explanation))
        self.wait(4)

        # Chloroplasts and Chlorophyll
        chloroplast_text = Text("This process occurs primarily in the chloroplasts,\ntiny green organelles in plant cells.",
                                  font_size=28, color=WHITE).next_to(explanation, DOWN, buff=1)
        chlorophyll_circle = Circle(radius=0.5, color=GREEN).shift(LEFT*3)
        chlorophyll_label = Text("Chlorophyll",
                                 font_size=24, color=GREEN).next_to(chlorophyll_circle, DOWN)
        self.play(FadeIn(chloroplast_text), GrowFromCenter(chlorophyll_circle), Write(chlorophyll_label))
        self.wait(3)

        # Absorption of Light
        absorption_text = Text("Chlorophyll absorbs red and blue light, but reflects green light.\nThis is why plants appear green.",
                                font_size=28, color=WHITE).next_to(chloroplast_text, DOWN, buff=1)
        self.play(FadeIn(absorption_text))
        self.wait(3)

        # Food Chain and Oxygen Production
        food_chain_text = Text("The glucose produced becomes the foundation of every food chain.\nThe oxygen we breathe is a product of photosynthesis.",
                                font_size=28, color=WHITE).next_to(absorption_text, DOWN, buff=1)
        self.play(FadeIn(food_chain_text))
        self.wait(3)

        # Conclusion
        conclusion_text = Text("In our next episode, we'll explore how plants convert light energy\ninto chemical energy in photosynthesis.",
                                font_size=28, color=WHITE).next_to(food_chain_text, DOWN, buff=1)
        self.play(FadeIn(conclusion_text))
        self.wait(3)

        # Fade out
        self.play(FadeOut(VGroup(title, intro_text, process_text, equation, explanation, chloroplast_text, absorption_text, food_chain_text, conclusion_text, chlorophyll_circle, chlorophyll_label)))
        self.wait(2)


if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
