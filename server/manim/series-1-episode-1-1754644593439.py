from manim import *
import numpy as np

class TheChemistryofLifeIntroductiontoPhotosynthesisScene(Scene):
    def construct(self):
        # Title
        title = Text("The Chemistry of Life: Introduction to Photosynthesis", font_size=48, color=WHITE)
        title.animate.to_edge(UP)
        self.play(Write(title))
        self.wait(2)
        
        # Content sections
        # Section 1
        section1 = Text("Every breath you take, every bite of food you eat, exists because of one remarkable process photosynthesis", font_size=24, color=YELLOW)
        section1.animate.move_to(ORIGIN)
        self.play(FadeIn(section1))
        self.wait(3)
        self.play(FadeOut(section1))
        # Section 2
        section2 = Text("Photosynthesis is natures way of capturing sunlight and converting it into the chemical energy that powers virtually all life on Earth", font_size=24, color=YELLOW)
        section2.animate.move_to(ORIGIN)
        self.play(FadeIn(section2))
        self.wait(3)
        self.play(FadeOut(section2))
        # Section 3
        section3 = Text("Its happening right now in the leaves outside your window, in ocean algae, and in plants across the globe", font_size=24, color=YELLOW)
        section3.animate.move_to(ORIGIN)
        self.play(FadeIn(section3))
        self.wait(3)
        self.play(FadeOut(section3))
        # Section 4
        section4 = Text("The fundamental equation of photosynthesis is beautifully simple\n6CO  6HO  light energy  CHO  6O  ATP\n\nThis means six molecules of carbon dioxide plus six molecules of water, using light energy, produce one molecule of glucose, six molecules of oxygen, and stored chemical energy", font_size=24, color=YELLOW)
        section4.animate.move_to(ORIGIN)
        self.play(FadeIn(section4))
        self.wait(3)
        self.play(FadeOut(section4))
        
        # Conclusion
        conclusion = Text("Thank you for learning about The Chemistry of Life!", font_size=36, color=GREEN)
        conclusion.animate.move_to(ORIGIN)
        self.play(FadeIn(conclusion))
        self.wait(2)

if __name__ == "__main__":
    scene = TheChemistryofLifeIntroductiontoPhotosynthesisScene()
    scene.render()
