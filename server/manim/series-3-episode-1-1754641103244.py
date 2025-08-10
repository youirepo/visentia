from manim import *
import numpy as np


from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(title))
        self.wait(2)

        # Introduction
        intro_text = Text("Every breath you take, every bite of food you eat, exists because of one remarkable process: photosynthesis.", font_size=28, color=WHITE).next_to(title, DOWN, buff=0.5)
        self.play(Write(intro_text))
        self.wait(3)

        # Photosynthesis Description
        photosynthesis_text = Text("Photosynthesis is nature's way of capturing sunlight and converting it into chemical energy.", font_size=28, color=WHITE)
        self.play(Transform(intro_text, photosynthesis_text))
        self.wait(3)

        # Fundamental Equation
        equation = MathTex("6CO_2 + 6H_2O + \text{light energy} \rightarrow C_6H_{12}O_6 + 6O_2 + ATP", font_size=36, color=GREEN)
        self.play(Write(equation))
        self.wait(4)

        # Explaining the Equation
        explanation_text = Text("This means: six molecules of carbon dioxide plus six molecules of water, using light energy, produce one molecule of glucose, six molecules of oxygen, and stored chemical energy.", font_size=24, color=WHITE).next_to(equation, DOWN, buff=0.5)
        self.play(Write(explanation_text))
        self.wait(6)

        # Process Description
        process_text = Text("Plants take in carbon dioxide, combine it with water, and use sunlight to create sugar, releasing oxygen.", font_size=28, color=WHITE).next_to(explanation_text, DOWN, buff=1)
        self.play(FadeOut(intro_text), FadeOut(equation), FadeOut(explanation_text), Write(process_text))
        self.wait(4)

        # Chloroplasts and Chlorophyll
        chloroplasts_text = Text("This process occurs in chloroplasts, tiny green organelles in plant cells.", font_size=28, color=WHITE)
        chlorophyll_text = Text("Chlorophyll absorbs red and blue light, reflecting green light.", font_size=28, color=WHITE).next_to(chloroplasts_text, DOWN, buff=0.5)
        self.play(Transform(process_text, chloroplasts_text))
        self.play(Write(chlorophyll_text))
        self.wait(4)

        # Diagram of a Chloroplast
        chloroplast_diagram = Circle(color=GREEN).scale(1.5)
        chlorophyll_lines = VGroup(
            Line(start=ORIGIN, end=RIGHT, color=BLUE).rotate(PI/4),
            Line(start=ORIGIN, end=RIGHT, color=RED).rotate(-PI/4)
        ).move_to(chloroplast_diagram.get_center())
        self.play(FadeOut(chlorophyll_text), ShowCreation(chloroplast_diagram), ShowCreation(chlorophyll_lines))
        self.wait(3)

        # Food Chain and Solar Energy
        food_chain_text = Text("The glucose produced becomes the foundation of virtually every food chain on Earth.", font_size=28, color=WHITE)
        solar_energy_text = Text("When you eat a vegetable, you're consuming stored solar energy.", font_size=28, color=WHITE).next_to(food_chain_text, DOWN, buff=0.5)
        self.play(Transform(process_text, food_chain_text), FadeOut(chloroplast_diagram), FadeOut(chlorophyll_lines))
        self.play(Write(solar_energy_text))
        self.wait(4)

        # Oxygen and Life
        oxygen_text = Text("The oxygen we breathe is entirely a product of photosynthesis, enabling complex life.", font_size=28, color=WHITE).next_to(solar_energy_text, DOWN, buff=0.5)
        self.play(Write(oxygen_text))
        self.wait(4)

        # Conclusion and Next Episode
        conclusion_text = Text("In our next episode, we'll dive into how plants capture light energy.", font_size=28, color=WHITE).next_to(oxygen_text, DOWN, buff=1)
        self.play(FadeOut(process_text), FadeOut(solar_energy_text), FadeOut(oxygen_text), Write(conclusion_text))
        self.wait(3)

        # Fade out everything
        self.play(FadeOut(conclusion_text), FadeOut(title))
        self.wait(2)


if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
