
from manim import *
class TriangleClassification(Scene):
    def construct(self):
        # 1. Introduction
        title = Text("Classifying Triangles by Sides", font_size=40, color=BLUE)
        self.play(Write(title))
        self.wait(1.5)
        self.play(title.animate.to_edge(UP))
        # 2. The Rule - Longest Side
        rule_text = Text("Step 1: Identify the LONGEST side (c)", font_size=32, color=YELLOW)
        rule_text.next_to(title, DOWN, buff=0.5)
        
        # Generic Triangle
        tri_pts = [LEFT*1.5 + DOWN, RIGHT*1.5 + DOWN, UP + RIGHT*0.5]
        triangle = Polygon(*tri_pts, color=WHITE)
        
        label_a = MathTex("a").next_to(Line(tri_pts[0], tri_pts[2]), LEFT, buff=0.1)
        label_b = MathTex("b").next_to(Line(tri_pts[2], tri_pts[1]), RIGHT, buff=0.1)
        label_c = MathTex("c").next_to(Line(tri_pts[0], tri_pts[1]), DOWN, buff=0.1)
        
        triangle_group = VGroup(triangle, label_a, label_b, label_c).center().shift(DOWN*0.5)
        
        self.play(Write(rule_text))
        self.play(Create(triangle))
        self.play(Write(label_a), Write(label_b), Write(label_c))
        self.play(Indicate(label_c, color=YELLOW, scale_factor=1.5))
        self.wait(2)
        
        self.play(FadeOut(rule_text), triangle_group.animate.scale(0.7).to_edge(LEFT, buff=1))

        # 3. The Math Comparison
        comparison = MathTex("Compare: ", "c^2", r" \text{ with } ", "a^2 + b^2", font_size=42)
        comparison.next_to(title, DOWN, buff=0.5).shift(RIGHT*2)
        self.play(Write(comparison))
        self.wait(1.5)

        # 4. Scenario 1: Right Angle
        right_logic = MathTex("c^2 = a^2 + b^2", color=GREEN)
        right_text = Text("Right-Angled", font_size=30, color=GREEN).next_to(right_logic, RIGHT, buff=0.5)
        case1 = VGroup(right_logic, right_text).next_to(comparison, DOWN, buff=0.8).align_to(comparison, LEFT)
        
        self.play(Write(right_logic))
        self.play(FadeIn(right_text))
        self.wait(2)

        # 5. Scenario 2: Acute
        acute_logic = MathTex("c^2 < a^2 + b^2", color=TEAL)
        acute_text = Text("Acute", font_size=30, color=TEAL).next_to(acute_logic, RIGHT, buff=0.5)
        case2 = VGroup(acute_logic, acute_text).next_to(case1, DOWN, buff=0.5).align_to(case1, LEFT)
        
        self.play(Write(acute_logic))
        self.play(FadeIn(acute_text))
        self.wait(2)

        # 6. Scenario 3: Obtuse
        obtuse_logic = MathTex("c^2 > a^2 + b^2", color=RED)
        obtuse_text = Text("Obtuse", font_size=30, color=RED).next_to(obtuse_logic, RIGHT, buff=0.5)
        case3 = VGroup(obtuse_logic, obtuse_text).next_to(case2, DOWN, buff=0.5).align_to(case2, LEFT)
        
        self.play(Write(obtuse_logic))
        self.play(FadeIn(obtuse_text))
        self.wait(2)

        # 7. Quick Example
        self.play(FadeOut(case1), FadeOut(case2), FadeOut(case3), FadeOut(comparison), FadeOut(triangle_group))
        
        example_title = Text("Example: Sides 5, 7, 10", font_size=36).to_edge(UP, buff=1.5)
        longest = MathTex("c = 10", font_size=34, color=YELLOW).next_to(example_title, DOWN)
        calc1 = MathTex("c^2 = 100", font_size=40).shift(LEFT*2 + DOWN)
        calc2 = MathTex("5^2 + 7^2 = 25 + 49 = 74", font_size=40).shift(RIGHT*2 + DOWN)
        
        self.play(Write(example_title))
        self.play(Write(longest))
        self.wait(1)
        self.play(Write(calc1), Write(calc2))
        self.wait(1.5)
        
        final_result = MathTex(r"100 > 74 \implies \text{Obtuse}", color=RED, font_size=50).shift(DOWN*2.5)
        self.play(Write(final_result))
        self.play(Circumscribe(final_result))
        self.wait(4)