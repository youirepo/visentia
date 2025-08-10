from manim import *
import numpy as np


from manim import *

class EducationalScene(MovingCameraScene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=48, color=YELLOW)
        self.play(Write(title))
        self.wait(2)
        self.play(self.camera.frame.animate.move_to(title.get_center()).scale(0.5))
        self.wait(1)
        
        # Introduction Text
        intro_text = Text("Every breath you take, every bite of food you eat, exists because of one remarkable process: photosynthesis.", font_size=24, color=WHITE)
        self.play(Write(intro_text), run_time=4)
        self.wait(2)
        
        # Photosynthesis overview
        self.play(FadeOut(title, intro_text))
        overview_text = Text("Photosynthesis is nature's way of capturing sunlight and converting it into the chemical energy that powers virtually all life on Earth.", font_size=28, color=WHITE)
        self.play(Write(overview_text), run_time=4)
        self.wait(2)
        
        # Fundamental Equation
        fundamental_eq = MathTex("6CO_2 + 6H_2O + light energy \\rightarrow C_6H_{12}O_6 + 6O_2 + ATP", font_size=36, color=GREEN)
        self.play(FadeOut(overview_text), Write(fundamental_eq), run_time=3)
        self.wait(2)

        # Description of the Equation
        eq_description = Text("This means: six molecules of carbon dioxide plus six molecules of water, using light energy, produce one molecule of glucose, six molecules of oxygen, and stored chemical energy.", font_size=24, color=WHITE)
        self.play(Write(eq_description), run_time=4)
        self.wait(3)

        # Process Explanation
        self.play(FadeOut(fundamental_eq, eq_description))
        process_text = Text("Plants take in the carbon dioxide we exhale, combine it with water from their roots, and use sunlight to create sugar - their food - while releasing oxygen as a byproduct.", font_size=24, color=WHITE)
        self.play(Write(process_text), run_time=4)
        self.wait(3)

        # Chloroplasts and Chlorophyll
        self.play(FadeOut(process_text))
        chloroplast_text = Text("This process occurs primarily in the chloroplasts, tiny green organelles packed inside plant cells.", font_size=24, color=WHITE)
        chlorophyll_text = Text("The green color comes from chlorophyll, a molecule perfectly designed to absorb light energy.", font_size=24, color=WHITE)
        self.play(Write(chloroplast_text), run_time=3)
        self.wait(2)
        self.play(Write(chlorophyll_text), run_time=3)
        self.wait(2)

        # Chlorophyll Absorption
        chlorophyll_absorption_text = Text("Chlorophyll absorbs red and blue light very efficiently, but reflects green light - which is why plants appear green to our eyes.", font_size=24, color=WHITE)
        self.play(FadeOut(chloroplast_text, chlorophyll_text), Write(chlorophyll_absorption_text), run_time=4)
        self.wait(3)

        # Food Chain
        self.play(FadeOut(chlorophyll_absorption_text))
        food_chain_text = Text("But photosynthesis isn't just about making food for plants. The glucose produced becomes the foundation of virtually every food chain on Earth.", font_size=24, color=WHITE)
        self.play(Write(food_chain_text), run_time=4)
        self.wait(3)

        # Oxygen and Life
        self.play(FadeOut(food_chain_text))
        oxygen_text = Text("The oxygen we breathe is entirely a product of photosynthesis. For the first billion years of Earth's history, there was virtually no oxygen in the atmosphere.", font_size=24, color=WHITE)
        self.play(Write(oxygen_text), run_time=4)
        self.wait(3)

        # Conclusion
        self.play(FadeOut(oxygen_text))
        conclusion_text = Text("In our next episode, we'll dive into exactly how plants capture light energy and convert it into chemical energy in the first stage of photosynthesis.", font_size=24, color=YELLOW)
        self.play(Write(conclusion_text), run_time=4)
        self.wait(3)

        # Ending
        self.play(FadeOut(conclusion_text))


if __name__ == "__main__":
    scene = EducationalScene()
    scene.render()
