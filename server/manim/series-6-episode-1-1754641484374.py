from manim import *
import numpy as np

from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=48, color=YELLOW)
        self.play(Write(title))
        self.wait(2)
        self.play(title.to_edge, UP)

        # Introduction
        intro_text = Text("Every breath you take, every bite of food you eat, exists because of one remarkable process: photosynthesis.", font_size=28)
        self.play(FadeIn(intro_text))
        self.wait(4)
        self.play(FadeOut(intro_text))

        # Definition of Photosynthesis
        definition = Text("Photosynthesis captures sunlight and converts it into chemical energy.", font_size=32, color=TEAL)
        self.play(Write(definition))
        self.wait(3)
        self.play(FadeOut(definition))

        # Fundamental Equation
        equation = MathTex("6CO_2 + 6H_2O + \text{light energy} \\rightarrow C_6H_{12}O_6 + 6O_2 + \text{ATP}", font_size=36)
        self.play(Write(equation))
        self.wait(3)
        self.play(equation.to_edge, UP)

        # Explanation of Equation
        explanation = Text("Six molecules of carbon dioxide plus six molecules of water, using light energy, produce one molecule of glucose, six molecules of oxygen, and stored chemical energy.", font_size=28)
        self.play(FadeIn(explanation))
        self.wait(4)
        self.play(FadeOut(explanation))

        # Process Description
        process_1 = Text("Plants take in CO2 and water, using sunlight to create sugar.", font_size=28)
        self.play(FadeIn(process_1))
        self.wait(4)
        self.play(FadeOut(process_1))

        process_2 = Text("Oxygen is released as a byproduct.", font_size=28)
        self.play(FadeIn(process_2))
        self.wait(3)
        self.play(FadeOut(process_2))

        # Chloroplasts
        chloroplasts = Text("This process occurs primarily in the chloroplasts.", font_size=28)
        self.play(FadeIn(chloroplasts))
        self.wait(3)
        self.play(FadeOut(chloroplasts))

        # Chlorophyll
        chlorophyll_text = Text("Chlorophyll absorbs red and blue light, reflects green light.", font_size=28)
        chlorophyll_diagram = Circle(radius=1, color=GREEN)
        self.play(Write(chlorophyll_text))
        self.play(Create(chlorophyll_diagram))
        self.wait(4)
        self.play(FadeOut(chlorophyll_text), FadeOut(chlorophyll_diagram))

        # Food Chain
        food_chain = Text("Glucose produced is the foundation of virtually every food chain on Earth.", font_size=28)
        self.play(FadeIn(food_chain))
        self.wait(3)
        self.play(FadeOut(food_chain))

        # Oxygen Production
        oxygen_production = Text("The oxygen we breathe is entirely a product of photosynthesis.", font_size=28)
        self.play(FadeIn(oxygen_production))
        self.wait(3)
        self.play(FadeOut(oxygen_production))

        # Closing
        closing = Text("In our next episode, we'll dive into how plants capture light energy.", font_size=28)
        self.play(Write(closing))
        self.wait(3)
        self.play(FadeOut(closing), FadeOut(equation))



if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
