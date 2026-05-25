"""AreaTransform — visual derivations for rhombus and trapezium areas (EV-003)."""

from __future__ import annotations

from typing import ClassVar

from manim import (
    DOWN,
    GREEN,
    LEFT,
    PI,
    RIGHT,
    TEAL,
    UP,
    WHITE,
    YELLOW,
    Create,
    FadeIn,
    FadeOut,
    MathTex,
    Polygon,
    Rotate,
    Text,
    VGroup,
)
from manim_voiceover import VoiceoverScene

from visentia.scenes.layout import as_diagram_shape, as_on_screen_text, place_in_band_below
from visentia.voiceover import VoiceoverSynthesizer


def _rhombus_vertices(d1: float, d2: float) -> list[list[float]]:
    return [
        [0.0, d2 / 2, 0.0],
        [d1 / 2, 0.0, 0.0],
        [0.0, -d2 / 2, 0.0],
        [-d1 / 2, 0.0, 0.0],
    ]


def _trapezium_vertices(a: float, b: float, h: float) -> list[list[float]]:
    """Isosceles trapezium: parallel sides a (top) and b (bottom), height h."""

    return [
        [-b / 2, -h / 2, 0.0],
        [b / 2, -h / 2, 0.0],
        [a / 2, h / 2, 0.0],
        [-a / 2, h / 2, 0.0],
    ]


class AreaTransformScene(VoiceoverScene):
    params: ClassVar[dict] = {
        "rhombus_d1": 4.0,
        "rhombus_d2": 2.5,
        "trapezium_a": 2.0,
        "trapezium_b": 4.0,
        "trapezium_h": 2.0,
        "include_trapezium": True,
    }

    def construct(self) -> None:
        self.set_speech_service(
            VoiceoverSynthesizer.create_service(),
            create_subcaption=False,
        )
        p = self.params
        d1 = float(p["rhombus_d1"])
        d2 = float(p["rhombus_d2"])
        ta = float(p["trapezium_a"])
        tb = float(p["trapezium_b"])
        th = float(p["trapezium_h"])
        include_trap = bool(p.get("include_trapezium", True))

        header = as_on_screen_text(
            VGroup(
                Text("Deriving area formulas", font_size=34),
                Text("Rhombus and trapezium", font_size=22, color=TEAL),
            ).arrange(DOWN, buff=0.2)
        ).to_edge(UP, buff=0.35)

        self._play_rhombus_scene(header, d1, d2)

        if include_trap:
            self.play(FadeOut(header))
            trap_header = as_on_screen_text(
                VGroup(
                    Text("Deriving area formulas", font_size=34),
                    Text("Trapezium", font_size=22, color=TEAL),
                ).arrange(DOWN, buff=0.2)
            ).to_edge(UP, buff=0.35)
            self._play_trapezium_scene(trap_header, ta, tb, th)

    def _play_rhombus_scene(self, header: VGroup, d1: float, d2: float) -> None:
        section = as_on_screen_text(Text("1. Rhombus", font_size=28, color=YELLOW))
        place_in_band_below(header, section, buff=0.3)

        verts = _rhombus_vertices(d1, d2)
        rhombus = as_diagram_shape(
            Polygon(*verts, color=TEAL, fill_opacity=0.2, stroke_width=3)
        ).scale(0.9)

        diag_h = as_diagram_shape(
            Polygon(
                verts[0], verts[2], color=WHITE, stroke_width=2, fill_opacity=0
            )
        ).scale(0.9)
        diag_v = as_diagram_shape(
            Polygon(
                verts[1], verts[3], color=WHITE, stroke_width=2, fill_opacity=0
            )
        ).scale(0.9)
        label_d1 = as_on_screen_text(MathTex(r"d_1", font_size=28)).next_to(diag_h, DOWN, buff=0.15)
        label_d2 = as_on_screen_text(MathTex(r"d_2", font_size=28)).next_to(diag_v, LEFT, buff=0.15)

        diagram = VGroup(rhombus, diag_h, diag_v, label_d1, label_d2)
        place_in_band_below(section, diagram, buff=0.35)

        rect = as_diagram_shape(
            Polygon(
                [-d1 / 2, -d2 / 2, 0],
                [d1 / 2, -d2 / 2, 0],
                [d1 / 2, d2 / 2, 0],
                [-d1 / 2, d2 / 2, 0],
                color=GREEN,
                fill_opacity=0.15,
                stroke_width=3,
            )
        ).scale(0.9)
        rect.move_to(diagram.get_center())

        formula = as_on_screen_text(
            MathTex(r"\text{Area}=\frac{1}{2}\,d_1\,d_2", font_size=40, color=GREEN)
        )
        note = as_on_screen_text(
            Text("Four congruent triangles fill half of a d₁×d₂ rectangle", font_size=22)
        )
        closing = VGroup(formula, note).arrange(DOWN, buff=0.3)
        place_in_band_below(diagram, closing, buff=0.45)

        with self.voiceover(
            text=(
                "A rhombus has perpendicular diagonals d1 and d2. "
                "Cut along both diagonals to make four congruent right triangles."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(header), FadeIn(section), run_time=min(0.5, tracker.duration * 0.12))
            self.play(Create(rhombus), run_time=min(0.6, tracker.duration * 0.15))
            self.play(Create(diag_h), Create(diag_v), FadeIn(label_d1), FadeIn(label_d2), run_time=min(0.7, tracker.duration * 0.18))
            self.wait(max(0.0, tracker.duration - min(1.8, tracker.duration * 0.45)))

        with self.voiceover(
            text=(
                "Rearrange those triangles to fill exactly half of a d1 by d2 rectangle. "
                "So the rhombus area is one half d1 d2."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(
                FadeOut(diag_h, diag_v, label_d1, label_d2),
                run_time=min(0.3, tracker.duration * 0.1),
            )
            self.play(FadeOut(rhombus), FadeIn(rect), run_time=min(1.0, tracker.duration * 0.35))
            self.play(FadeIn(closing), run_time=min(0.5, tracker.duration * 0.15))
            self.wait(max(0.0, tracker.duration - min(1.8, tracker.duration * 0.6)))

        self.play(FadeOut(section, diagram, rect, closing, header))

    def _play_trapezium_scene(self, header: VGroup, a: float, b: float, h: float) -> None:
        section = as_on_screen_text(Text("2. Trapezium", font_size=28, color=YELLOW))
        place_in_band_below(header, section, buff=0.3)

        verts = _trapezium_vertices(a, b, h)
        trap = as_diagram_shape(
            Polygon(*verts, color=TEAL, fill_opacity=0.2, stroke_width=3)
        ).scale(0.85)
        trap.shift(LEFT * 1.2)

        trap2 = trap.copy().set_color(GREEN)
        label_a = as_on_screen_text(MathTex("a", font_size=26)).next_to(trap, UP, buff=0.1)
        label_b = as_on_screen_text(MathTex("b", font_size=26)).next_to(trap, DOWN, buff=0.1)
        label_h = as_on_screen_text(MathTex("h", font_size=26)).next_to(trap, LEFT, buff=0.35)

        diagram = VGroup(trap, label_a, label_b, label_h)
        place_in_band_below(section, diagram, buff=0.35)

        formula = as_on_screen_text(
            MathTex(r"\text{Area}=\frac{1}{2}(a+b)\,h", font_size=40, color=GREEN)
        )
        note = as_on_screen_text(
            Text("Two copies form a parallelogram with base (a+b) and height h", font_size=22)
        )
        closing = VGroup(formula, note).arrange(DOWN, buff=0.3)
        place_in_band_below(diagram, closing, buff=0.45)

        with self.voiceover(
            text=(
                "For a trapezium with parallel sides a and b and height h, "
                "duplicate the shape and rotate it one hundred eighty degrees."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(header), FadeIn(section), run_time=min(0.5, tracker.duration * 0.12))
            self.play(Create(trap), FadeIn(label_a), FadeIn(label_b), FadeIn(label_h), run_time=min(0.8, tracker.duration * 0.2))
            self.wait(max(0.0, tracker.duration - min(1.3, tracker.duration * 0.32)))

        with self.voiceover(
            text=(
                "Slide the copy to sit along the slanted side. Together they make a parallelogram "
                "with base a plus b and height h. Halve that area for one trapezium."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(trap2), run_time=min(0.4, tracker.duration * 0.1))
            self.play(
                Rotate(trap2, PI, about_point=trap.get_center()),
                run_time=min(0.6, tracker.duration * 0.15),
            )
            self.play(trap2.animate.next_to(trap, RIGHT, buff=0), run_time=min(0.7, tracker.duration * 0.18))
            self.play(FadeIn(closing), run_time=min(0.5, tracker.duration * 0.15))
            self.wait(max(0.0, tracker.duration - min(2.2, tracker.duration * 0.58)))

        self.play(FadeOut(header, section, diagram, trap, trap2, label_a, label_b, label_h, closing))
