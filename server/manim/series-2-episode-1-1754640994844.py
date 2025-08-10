from manim import *
import numpy as np


from manim import *

class EducationalScene(MovingCameraScene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=48, color=YELLOW)
        self.play(Write(title))
        self.wait(2)
        self.play(title.to_edge, UP)

        # Introduction
        intro_text = Text("Every breath you take, every bite of food you eat, exists because of one remarkable process: photosynthesis.", font_size=24).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(intro_text))
        self.wait(5)
        
        # Photosynthesis Process
        process_text = Text("Photosynthesis captures sunlight and converts it into chemical energy.", font_size=24)
        self.play(Transform(intro_text, process_text))
        self.wait(3)
        
        # Photosynthesis Equation
        equation = MathTex("6CO_2 + 6H_2O + \text{light energy} \rightarrow C_6H_{12}O_6 + 6O_2 + \text{ATP}", font_size=36)
        self.play(FadeOut(intro_text), Write(equation))
        self.wait(4)

        # Explanation of the equation
        explanation_text = Text("This means: six molecules of carbon dioxide plus six molecules of water, using light energy, produce one molecule of glucose, six molecules of oxygen, and stored chemical energy.", font_size=24)
        self.play(ReplacementTransform(equation, explanation_text))
        self.wait(6)

        # Plant and Chloroplasts
        plant_diagram = ImageMobject("plant.png").scale(0.5).to_edge(LEFT)
        chloroplast_circle = Circle(color=GREEN).move_to(plant_diagram.get_center())
        chlorophyll_text = Text("Chlorophyll", font_size=24, color=GREEN).next_to(chloroplast_circle, RIGHT)
        self.play(FadeIn(plant_diagram), GrowFromCenter(chloroplast_circle), Write(chlorophyll_text))
        self.wait(3)

        # Chlorophyll explanation
        chlorophyll_explanation = Text("Chlorophyll absorbs red and blue light, reflects green light.", font_size=24)
        self.play(ReplacementTransform(explanation_text, chlorophyll_explanation))
        self.wait(4)

        # Food Chain
        food_chain_text = Text("Photosynthesis is the foundation of every food chain.", font_size=24).move_to(chlorophyll_explanation)
        self.play(ReplacementTransform(chlorophyll_explanation, food_chain_text))
        self.wait(3)

        # Oxygen Production
        oxygen_text = Text("The oxygen we breathe comes from photosynthesis.", font_size=24)
        self.play(ReplacementTransform(food_chain_text, oxygen_text))
        self.wait(3)

        # Conclusion
        conclusion_text = Text("In our next episode, we'll dive into how plants capture and convert light energy.", font_size=24).next_to(oxygen_text, DOWN, buff=0.5)
        self.play(FadeIn(conclusion_text))
        self.wait(4)

        # Fade out
        self.play(FadeOut(title), FadeOut(oxygen_text), FadeOut(conclusion_text), FadeOut(plant_diagram), FadeOut(chlorophyll_text), FadeOut(chloroplast_circle))
        self.wait(2)


if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
