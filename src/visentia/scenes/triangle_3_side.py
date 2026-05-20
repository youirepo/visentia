"""Triangle3Side — Converse of Pythagoras (EV-001).

Classifies a triangle as acute, right, or obtuse from three side lengths by comparing
c² with a² + b², where c is the longest side. Targets EV-001 `success_10` choreography.
"""

from __future__ import annotations

import math
from typing import ClassVar

from manim import (
    DOWN,
    GREEN,
    RED,
    RIGHT,
    TEAL,
    UP,
    YELLOW,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    MathTex,
    Polygon,
    Text,
    VGroup,
    ValueTracker,
    always_redraw,
)
from manim_voiceover import VoiceoverScene

from visentia.voiceover import VoiceoverSynthesizer

# Canonical examples from docs/evals/seed.md (EV-001 success_10).
_KEY_EXAMPLES: list[tuple[float, float, float]] = [
    (3, 4, 5),
    (5, 5, 6),
    (5, 5, 7),
]

_COLOR_RIGHT = GREEN
_COLOR_ACUTE = TEAL
_COLOR_OBTUSE = RED


def _sort_sides(a: float, b: float, c: float) -> tuple[float, float, float]:
    """Return (shorter1, shorter2, longest) so longest is last."""

    sides = sorted([float(a), float(b), float(c)])
    return sides[0], sides[1], sides[2]


def _classify(a: float, b: float, c: float) -> tuple[str, str]:
    """Return (classification_label, color_name) for sides a,b,c (any order)."""

    sa, sb, sc = _sort_sides(a, b, c)
    sum_sq = sa * sa + sb * sb
    c_sq = sc * sc
    if math.isclose(c_sq, sum_sq, rel_tol=1e-9):
        return "Right-angled", "right"
    if c_sq < sum_sq:
        return "Acute", "acute"
    return "Obtuse", "obtuse"


def _color_for(kind: str):
    return {"right": _COLOR_RIGHT, "acute": _COLOR_ACUTE, "obtuse": _COLOR_OBTUSE}[kind]


def _triangle_vertices(side_a: float, side_b: float, side_c: float) -> list[list[float]]:
    """Build 2D vertices with longest side `side_c` on the base."""

    sa, sb, sc = _sort_sides(side_a, side_b, side_c)
    if sa + sb <= sc:
        raise ValueError("Invalid triangle")

    # Base along x-axis: B=(0,0), C=(sc,0); apex A from distances sb and sa to B and C.
    x = (sb * sb - sa * sa + sc * sc) / (2 * sc)
    y_sq = sb * sb - x * x
    y = math.sqrt(max(0.0, y_sq))
    return [[0.0, 0.0, 0.0], [float(x), float(y), 0.0], [float(sc), 0.0, 0.0]]


class Triangle3SideScene(VoiceoverScene):
    """Parameterised template scene. `params` is set by `TemplateLibrary.render` before render."""

    params: ClassVar[dict] = {
        "side_a": 3,
        "side_b": 4,
        "side_c": 5,
        "include_sweep": True,
    }

    def construct(self) -> None:
        self.set_speech_service(VoiceoverSynthesizer.create_service())
        p = self.params
        include_sweep = bool(p.get("include_sweep", True))

        title = Text("Converse of Pythagoras", font_size=36)
        subtitle = Text(
            "Classify a triangle from its side lengths (not drawn to scale)",
            font_size=24,
            color=TEAL,
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.25).to_edge(UP)

        with self.voiceover(
            text=(
                "When you know three side lengths but not the angles, use the converse "
                "of Pythagoras. First find the longest side, call it c. "
                "Compare c squared with the sum of the squares of the other two sides."
            )
        ) as tracker:
            self.play(FadeIn(header), run_time=tracker.duration * 0.6)
            self.wait(tracker.duration * 0.4)

        rule = MathTex(
            r"\text{Longest side } c:\quad",
            r"c^2",
            r" \stackrel{?}{=} ",
            r"a^2 + b^2",
            font_size=40,
        )
        rule.next_to(header, DOWN, buff=0.4)

        with self.voiceover(
            text=(
                "If c squared equals a squared plus b squared, the triangle is right angled. "
                "If c squared is less, the triangle is acute. "
                "If c squared is greater, the triangle is obtuse."
            )
        ) as tracker:
            self.play(FadeIn(rule), run_time=tracker.duration)

        for example in _KEY_EXAMPLES:
            self._play_example(example, rule)

        if include_sweep:
            self._play_parameter_sweep(rule)

        if p.get("side_a") and (p["side_a"], p["side_b"], p["side_c"]) not in _KEY_EXAMPLES:
            prompt_label = Text("From your Prompt", font_size=28, color=YELLOW).next_to(
                rule, DOWN, buff=0.5
            )
            self.play(FadeIn(prompt_label))
            self._play_example(
                (float(p["side_a"]), float(p["side_b"]), float(p["side_c"])),
                rule,
            )
            self.play(FadeOut(prompt_label))

        with self.voiceover(
            text="Remember: always use the longest side as c before you compare the squares."
        ) as tracker:
            self.wait(tracker.duration)

    def _play_example(
        self,
        sides: tuple[float, float, float],
        rule: MathTex,
    ) -> None:
        a, b, c = sides
        label, kind = _classify(a, b, c)
        color = _color_for(kind)
        sa, sb, sc = _sort_sides(a, b, c)

        verts = _triangle_vertices(a, b, c)
        tri = Polygon(*verts, color=color, fill_opacity=0.25, stroke_width=3)
        tri.scale(0.9).next_to(rule, DOWN, buff=0.8)

        example_title = Text(
            f"Sides {a:g}, {b:g}, {c:g}",
            font_size=28,
            color=color,
        ).next_to(tri, UP, buff=0.2)

        sum_sq = sa * sa + sb * sb
        c_sq = sc * sc
        readout = MathTex(
            rf"c^2 = {c_sq:g}",
            r" \quad\text{vs}\quad ",
            rf"a^2+b^2 = {sum_sq:g}",
            font_size=32,
        ).next_to(tri, DOWN, buff=0.25)

        if kind == "right":
            relation = MathTex(rf"{c_sq:g} = {sum_sq:g}", color=color, font_size=34)
        elif kind == "acute":
            relation = MathTex(rf"{c_sq:g} < {sum_sq:g}", color=color, font_size=34)
        else:
            relation = MathTex(rf"{c_sq:g} > {sum_sq:g}", color=color, font_size=34)

        verdict = Text(label, font_size=36, color=color).next_to(relation, RIGHT, buff=0.4)
        panel = VGroup(readout, relation, verdict).arrange(DOWN, buff=0.2).next_to(tri, DOWN, buff=0.5)

        narration = (
            f"For sides {a:g}, {b:g}, and {c:g}, the longest side is {sc:g}. "
            f"c squared is {c_sq:g}, and a squared plus b squared is {sum_sq:g}. "
            f"So this triangle is {label.lower()}."
        )

        group = VGroup(tri, example_title, panel)

        with self.voiceover(text=narration) as tracker:
            self.play(
                FadeIn(example_title),
                Create(tri),
                run_time=tracker.duration * 0.35,
            )
            self.play(FadeIn(panel), run_time=tracker.duration * 0.35)
            self.play(Indicate(verdict, color=color), run_time=tracker.duration * 0.3)

        self.play(FadeOut(group))

    def _play_parameter_sweep(self, rule: MathTex) -> None:
        """Sweep the longest side while legs stay 5, 5 — acute → right → obtuse."""

        leg = 5.0
        c_tracker = ValueTracker(5.0)

        def make_group() -> VGroup:
            c_val = c_tracker.get_value()
            verts = _triangle_vertices(leg, leg, c_val)
            tri = Polygon(*verts, color=WHITE, fill_opacity=0.2, stroke_width=3)
            tri.scale(0.85).next_to(rule, DOWN, buff=0.9)
            _, kind = _classify(leg, leg, c_val)
            color = _color_for(kind)
            tri.set_color(color)
            sa, sb, sc = _sort_sides(leg, leg, c_val)
            sum_sq = sa * sa + sb * sb
            c_sq = sc * sc
            readout = MathTex(
                rf"c^2 = {c_sq:.1f}",
                r" \quad ",
                rf"a^2+b^2 = {sum_sq:.0f}",
                font_size=30,
            ).next_to(tri, DOWN, buff=0.3)
            label, _ = _classify(leg, leg, c_val)
            tag = Text(label, font_size=28, color=color).next_to(readout, DOWN, buff=0.15)
            return VGroup(tri, readout, tag)

        sweep_group = always_redraw(make_group)
        caption = Text(
            "Sweeping the longest side (legs fixed at 5 and 5)",
            font_size=24,
        ).next_to(rule, DOWN, buff=0.35)

        with self.voiceover(
            text=(
                "Watch what happens when the longest side grows while the other two sides "
                "stay fixed. The triangle morphs from acute, through right angled, to obtuse."
            )
        ) as tracker:
            self.play(FadeIn(caption), FadeIn(sweep_group), run_time=tracker.duration * 0.2)
            self.play(
                c_tracker.animate.set_value(7.0),
                run_time=tracker.duration * 0.7,
                rate_func=lambda t: t,
            )
            self.wait(tracker.duration * 0.1)

        self.play(FadeOut(sweep_group), FadeOut(caption))
