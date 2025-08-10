from manim import *
import numpy as np


from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=36, color=YELLOW)
        self.play(Write(title))
        self.wait(2)
        self.play(title.animate.to_edge(UP))
        
        # Opening line
        opening_text = Text("Every breath you take, every bite of food you eat, exists because of one remarkable process: photosynthesis.", font_size=24, color=WHITE)
        self.play(FadeIn(opening_text))
        self.wait(4)
        self.play(FadeOut(opening_text))

        # Photosynthesis explanation
        photosynthesis_text = Text("Photosynthesis is nature's way of capturing sunlight and converting it into the chemical energy that powers virtually all life on Earth.", font_size=24, color=WHITE)
        leaves_image = ImageMobject("leaves.jpg").scale(0.5).to_edge(RIGHT)
        self.play(FadeIn(photosynthesis_text), FadeIn(leaves_image))
        self.wait(4)
        self.play(FadeOut(photosynthesis_text), FadeOut(leaves_image))

        # Photosynthesis Equation
        equation = MathTex("6CO_2 + 6H_2O + light energy \\rightarrow C_6H_{12}O_6 + 6O_2 + ATP", font_size=36, color=GREEN)
        self.play(Write(equation))
        self.wait(3)
        
        # Explanation
        explanation_text = Text("Six molecules of carbon dioxide plus six molecules of water, using light energy, produce one molecule of glucose, six molecules of oxygen, and stored chemical energy.", font_size=24, color=WHITE)
        self.play(Transform(equation, explanation_text))
        self.wait(5)
        self.play(FadeOut(explanation_text))

        # Chloroplasts and Chlorophyll
        chloroplast_text = Text("This process occurs primarily in the chloroplasts, tiny green organelles packed inside plant cells.", font_size=24, color=WHITE)
        chloroplast_diagram = Circle(color=GREEN).shift(DOWN)
        chlorophyll_text = Text("The green color comes from chlorophyll, a molecule perfectly designed to absorb light energy.", font_size=24, color=WHITE)
        self.play(FadeIn(chloroplast_text))
        self.play(Create(chloroplast_diagram))
        self.wait(4)
        self.play(Transform(chloroplast_text, chlorophyll_text))
        self.wait(3)
        self.play(FadeOut(chloroplast_text), FadeOut(chloroplast_diagram))

        # Absorption of Light
        absorption_text = Text("Chlorophyll absorbs red and blue light very efficiently, but reflects green light - which is why plants appear green to our eyes.", font_size=24, color=WHITE)
        self.play(FadeIn(absorption_text))
        self.wait(4)
        self.play(FadeOut(absorption_text))

        # Significance of Photosynthesis
        significance_text = Text("But photosynthesis isn't just about making food for plants.", font_size=24, color=WHITE)
        self.play(FadeIn(significance_text))
        self.wait(2)
        self.play(FadeOut(significance_text))

        # Food Chain
        food_chain_text = Text("The glucose produced becomes the foundation of virtually every food chain on Earth.", font_size=24, color=WHITE)
        self.play(FadeIn(food_chain_text))
        self.wait(3)
        self.play(FadeOut(food_chain_text))

        # Oxygen Production
        oxygen_text = Text("The oxygen we breathe is entirely a product of photosynthesis.", font_size=24, color=WHITE)
        self.play(FadeIn(oxygen_text))
        self.wait(3)
        self.play(FadeOut(oxygen_text))

        # Next Episode
        next_episode_text = Text("In our next episode, we'll dive into exactly how plants capture light energy and convert it into chemical energy in the first stage of photosynthesis.", font_size=24, color=WHITE)
        self.play(FadeIn(next_episode_text))
        self.wait(4)
        self.play(FadeOut(next_episode_text))

        # Fade out title
        self.play(FadeOut(title))


if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
