from manim import *

class RateCalculation(Scene):
    def construct(self):
        # Title and Context
        title = Text("Calculating Totals using Rates", color=BLUE)
        self.play(Write(title))
        self.wait(1.5)
        self.play(title.animate.to_edge(UP).scale(0.8))

        # The Problem
        problem = VGroup(
            Text("Rate: $5 per 100g", font_size=36),
            Text("Find cost of: 4.5kg", font_size=36)
        ).arrange(DOWN).next_to(title, DOWN, buff=0.5)
        
        self.play(FadeIn(problem))
        self.wait(2)

        # Step 1: Unit Conversion
        step1_text = Text("Step 1: Match the units (kg to g)", color=YELLOW, font_size=32)
        step1_text.next_to(problem, DOWN, buff=0.5)
        
        conversion = MathTex("4.5", "\\text{ kg}", "=", "4500", "\\text{ g}")
        conversion.set_color_by_tex("4500", YELLOW)
        conversion.next_to(step1_text, DOWN)

        self.play(Write(step1_text))
        self.play(Write(conversion))
        self.wait(2)

        # Clear space for calculation
        self.play(
            FadeOut(problem),
            FadeOut(step1_text),
            conversion.animate.to_edge(UP).shift(DOWN*1.5)
        )

        # Step 2: The Logic (How many 'units' of 100g?)
        logic_text = Text("Step 2: How many '100g' lots are in 4500g?", font_size=32, color=YELLOW)
        logic_text.next_to(conversion, DOWN, buff=0.5)
        
        scaling_math = MathTex(
            "\\text{Number of lots} = \\frac{4500\\text{ g}}{100\\text{ g}}", "=", "45"
        )
        scaling_math.next_to(logic_text, DOWN)

        self.play(Write(logic_text))
        self.play(Write(scaling_math))
        self.wait(2.5)

        # Step 3: Final Multiplication
        final_text = Text("Step 3: Multiply by the price", font_size=32, color=YELLOW)
        final_text.next_to(scaling_math, DOWN, buff=0.5)
        
        total_calc = MathTex(
            "\\text{Total Cost} = 45 \\times \\$5", "=", "\\$225"
        )
        total_calc.next_to(final_text, DOWN)
        total_calc.set_color(GREEN)

        self.play(Write(final_text))
        self.play(Write(total_calc))
        self.wait(1)

        # Highlight Result
        box = SurroundingRectangle(total_calc, color=GREEN, buff=0.2)
        self.play(Create(box))
        self.wait(3)

        # Summary Formula
        self.play(FadeOut(conversion), FadeOut(logic_text), FadeOut(scaling_math), FadeOut(final_text))
        
        summary = VGroup(
            Text("General Rule:", font_size=32, color=BLUE),
            MathTex("\\text{Total} = \\frac{\\text{Total Quantity}}{\\text{Rate Quantity}} \\times \\text{Rate Price}")
        ).arrange(DOWN).move_to(ORIGIN)
        
        self.play(ReplacementTransform(VGroup(total_calc, box), summary))
        self.wait(4)