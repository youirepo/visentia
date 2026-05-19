
from manim import *

class AreaDerivations(Scene):
    def construct(self):
        # Title
        title = Text("Area of Rhombus & Trapezium", font_size=40, color=BLUE)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP).scale(0.8))

        # --- PART 1: RHOMBUS / KITE ---
        rhombus_label = Text("1. Rhombus and Kite", font_size=30, color=YELLOW).next_to(title, DOWN)
        self.play(Write(rhombus_label))

        # Create Kite
        d1, d2 = 4, 2.5
        p1 = [0, d2/2, 0]
        p2 = [d1/2, 0, 0]
        p3 = [0, -d2/2, 0]
        p4 = [-d1/2, 0, 0]
        kite = Polygon(p1, p2, p3, p4, color=WHITE)
        
        diag_x = Line(p4, p2, color=RED)
        diag_y = Line(p3, p1, color=GREEN)
        label_x = MathTex("x", color=RED).next_to(diag_x, DOWN, buff=0.1)
        label_y = MathTex("y", color=GREEN).next_to(diag_y, LEFT, buff=0.1)
        
        # Bounding Box
        rect = DashedVMobject(Rectangle(width=d1, height=d2, color=BLUE_E))
        
        kite_group = VGroup(kite, diag_x, diag_y, label_x, label_y).shift(LEFT*3 + DOWN*0.5)
        rect.move_to(kite_group)

        self.play(Create(kite))
        self.play(Create(diag_x), Write(label_x), Create(diag_y), Write(label_y))
        self.wait(1)
        self.play(Create(rect))
        
        kite_formula = MathTex("Area = \\frac{1}{2}xy", font_size=42).next_to(kite_group, RIGHT, buff=1)
        kite_expl = Text("Half the rectangle!", font_size=24).next_to(kite_formula, DOWN)
        
        self.play(Write(kite_formula))
        self.play(FadeIn(kite_expl))
        self.wait(2)

        # Clear Part 1
        self.play(FadeOut(kite_group), FadeOut(rect), FadeOut(kite_formula), FadeOut(kite_expl), FadeOut(rhombus_label))

        # --- PART 2: TRAPEZIUM ---
        trap_label = Text("2. Trapezium", font_size=30, color=YELLOW).next_to(title, DOWN)
        self.play(Write(trap_label))

        # Points for Trapezium
        a_val, b_val, h_val = 1.5, 3.5, 2
        t1 = [-b_val/2, -h_val/2, 0]
        t2 = [b_val/2, -h_val/2, 0]
        t3 = [a_val/2, h_val/2, 0]
        t4 = [-a_val/2, h_val/2, 0]
        
        trapezium = Polygon(t1, t2, t3, t4, color=WHITE, fill_opacity=0.3, fill_color=BLUE)
        trapezium.shift(LEFT*2 + DOWN*0.5)
        
        label_a = MathTex("a").next_to(trapezium, UP, buff=0.1)
        label_b = MathTex("b").next_to(trapezium, DOWN, buff=0.1)
        
        height_line = DashedLine(t4, [t4[0], t1[1], 0]).shift(LEFT*2 + DOWN*0.5)
        label_h = MathTex("h").next_to(height_line, LEFT, buff=0.1)

        self.play(Create(trapezium), Write(label_a), Write(label_b), Create(height_line), Write(label_h))
        self.wait(1)

        # Duplicate and Rotate to form Parallelogram
        trap2 = trapezium.copy().set_color(GREEN)
        self.play(trap2.animate.rotate(PI).next_to(trapezium, RIGHT, buff=0))
        
        # New Labels
        label_a2 = MathTex("a").next_to(trap2, DOWN, buff=0.1)
        label_b2 = MathTex("b").next_to(trap2, UP, buff=0.1)
        
        self.play(Write(label_a2), Write(label_b2))
        self.wait(1)

        # Derivation Text
        para_area = Text("Parallelogram Area = base × h", font_size=24).to_edge(RIGHT, buff=0.5).shift(UP)
        para_math = MathTex("Area = (a+b)h", font_size=36).next_to(para_area, DOWN)
        trap_final = MathTex("Area = \\frac{1}{2}(a+b)h", font_size=42, color=YELLOW).next_to(para_math, DOWN, buff=0.5)
        
        self.play(Write(para_area))
        self.play(Write(para_math))
        self.wait(1)
        self.play(Indicate(trapezium))
        self.play(Write(trap_final))
        self.play(Circumscribe(trap_final))
        
        self.wait(4)