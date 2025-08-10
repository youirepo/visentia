from manim import *
import numpy as np

from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=48, color=YELLOW).to_edge(UP)
        self.play(Write(title))
        self.wait(2)

        # Introduction Text
        intro_text = Text(
            "Every breath you take, every bite of food you eat,\nexists because of one remarkable process: photosynthesis.",
            font_size=28, color=WHITE
        ).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(intro_text, shift=UP))
        self.wait(3)

        # Photosynthesis Process
        process_text = Text(
            "Photosynthesis is nature's way of capturing sunlight\nand converting it into chemical energy.",
            font_size=28, color=WHITE
        ).next_to(intro_text, DOWN, buff=0.5)
        self.play(FadeIn(process_text, shift=UP))
        self.wait(3)

        # Photosynthesis Equation
        equation = MathTex(
            "6CO_2 + 6H_2O + \text{light energy} \rightarrow C_6H_{12}O_6 + 6O_2 + ATP",
            font_size=36, color=GREEN
        ).next_to(process_text, DOWN, buff=0.7)
        self.play(Write(equation))
        self.wait(4)

        # Explanation of Equation
        explanation_text = Text(
            "Six molecules of carbon dioxide plus six molecules of water,\nusing light energy, produce one molecule of glucose,\nsix molecules of oxygen, and stored chemical energy.",
            font_size=24, color=WHITE
        ).next_to(equation, DOWN, buff=0.5)
        self.play(FadeIn(explanation_text, shift=UP))
        self.wait(5)

        # Chloroplast and Chlorophyll
        chloroplast_text = Text(
            "This process occurs primarily in the chloroplasts,\ntiny green organelles packed inside plant cells.",
            font_size=28, color=WHITE
        ).next_to(explanation_text, DOWN, buff=0.5)
        self.play(FadeIn(chloroplast_text, shift=UP))
        self.wait(3)

        # Chlorophyll Absorption
        chlorophyll_text = Text(
            "Chlorophyll absorbs red and blue light efficiently,\nbut reflects green light.",
            font_size=28, color=WHITE
        ).next_to(chloroplast_text, DOWN, buff=0.5)
        self.play(FadeIn(chlorophyll_text, shift=UP))
        self.wait(3)

        # Food Chain Foundation
        food_chain_text = Text(
            "The glucose produced becomes the foundation\nof virtually every food chain on Earth.",
            font_size=28, color=WHITE
        ).next_to(chlorophyll_text, DOWN, buff=0.5)
        self.play(FadeIn(food_chain_text, shift=UP))
        self.wait(3)

        # Oxygen Production
        oxygen_text = Text(
            "The oxygen we breathe is entirely a product of photosynthesis.\nIt was photosynthetic bacteria and later plants\nthat pumped oxygen into the air.",
            font_size=28, color=WHITE
        ).next_to(food_chain_text, DOWN, buff=0.5)
        self.play(FadeIn(oxygen_text, shift=UP))
        self.wait(5)

        # Closing Statement
        closing_text = Text(
            "In our next episode, we'll dive into exactly how plants\ncapture light energy and convert it into chemical energy.",
            font_size=28, color=WHITE
        ).to_edge(DOWN)
        self.play(FadeIn(closing_text, shift=UP))
        self.wait(4)

        # Fade out all
        self.play(FadeOut(Group(title, intro_text, process_text, equation, explanation_text, chloroplast_text, 
                                 chlorophyll_text, food_chain_text, oxygen_text, closing_text)))


if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
