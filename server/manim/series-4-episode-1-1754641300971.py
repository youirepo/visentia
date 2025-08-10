from manim import *
import numpy as np

from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Background and Title
        self.camera.background_color = BLACK
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(title))
        self.wait(2)

        # Introduction Text
        intro_text = Text("Every breath you take, every bite of food you eat, exists because of photosynthesis.", font_size=24, color=WHITE).next_to(title, DOWN)
        self.play(FadeIn(intro_text))
        self.wait(2)

        # Explanation of Photosynthesis
        explanation_text = Text("Photosynthesis captures sunlight and converts it into chemical energy.", font_size=24, color=WHITE).next_to(intro_text, DOWN)
        self.play(FadeIn(explanation_text))
        self.wait(2)

        # Equation of Photosynthesis
        equation = MathTex("6CO_2 + 6H_2O + \text{light energy} \rightarrow C_6H_{12}O_6 + 6O_2 + \text{ATP}", font_size=36, color=GREEN).next_to(explanation_text, DOWN)
        self.play(Write(equation))
        self.wait(3)

        # Explanation of the Equation
        explanation_eq = Text("Six molecules of CO2 and H2O with light produce glucose, O2, and ATP.", font_size=24, color=WHITE).next_to(equation, DOWN)
        self.play(FadeIn(explanation_eq))
        self.wait(3)

        # Diagram of Photosynthesis Process
        chloroplast = Ellipse(width=3, height=2, color=GREEN, fill_opacity=0.5).to_edge(LEFT)
        sunlight_arrow = Arrow(LEFT, RIGHT, color=YELLOW).next_to(chloroplast, RIGHT, buff=0.1)
        sunlight_text = Text("Sunlight", font_size=24, color=YELLOW).next_to(sunlight_arrow, UP)
        self.play(Create(chloroplast), Create(sunlight_arrow), Write(sunlight_text))
        self.wait(2)

        # Chlorophyll explanation
        chlorophyll_text = Text("Chlorophyll absorbs red and blue light, reflects green.", font_size=24, color=WHITE).next_to(chloroplast, DOWN)
        self.play(FadeIn(chlorophyll_text))
        self.wait(3)

        # Visualizing Oxygen Release
        oxygen_molecule = MathTex("O_2", font_size=36, color=BLUE).next_to(chloroplast, RIGHT, buff=2)
        oxygen_arrow = Arrow(chloroplast.get_right(), oxygen_molecule.get_left(), color=BLUE)
        self.play(Create(oxygen_arrow), Write(oxygen_molecule))
        self.wait(3)

        # Food Chain Explanation
        food_chain_text = Text("Glucose is the foundation of all food chains.", font_size=24, color=WHITE).next_to(oxygen_molecule, DOWN)
        self.play(FadeIn(food_chain_text))
        self.wait(3)

        # Oxygen and Life on Earth
        oxygen_life_text = Text("The oxygen we breathe comes from photosynthesis.", font_size=24, color=WHITE).next_to(food_chain_text, DOWN)
        self.play(FadeIn(oxygen_life_text))
        self.wait(3)

        # Conclusion and Next Episode Tease
        conclusion_text = Text("In the next episode: How plants capture and convert light energy.", font_size=24, color=WHITE).next_to(oxygen_life_text, DOWN)
        self.play(FadeIn(conclusion_text))
        self.wait(3)

        # Fade Out
        self.play(FadeOut(Group(title, intro_text, explanation_text, equation, explanation_eq, chloroplast, sunlight_arrow, sunlight_text, chlorophyll_text, oxygen_molecule, oxygen_arrow, food_chain_text, oxygen_life_text, conclusion_text)))
        self.wait(2)


if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
