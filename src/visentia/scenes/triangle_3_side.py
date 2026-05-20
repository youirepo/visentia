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
    LEFT,
    RED,
    RIGHT,
    TEAL,
    UP,
    WHITE,
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

from visentia.scenes.layout import fit_in_vertical_band, place_below
from visentia.voiceover import VoiceoverSynthesizer

_KEY_EXAMPLES: list[tuple[float, float, float]] = [
    (3, 4, 5),
    (5, 5, 6),
    (5, 5, 7),
]

_COLOR_RIGHT = GREEN
_COLOR_ACUTE = TEAL
_COLOR_OBTUSE = RED

# Legs fixed at 5; sweep longest side c across acute → right → obtuse.
_SWEEP_LEG = 5.0
_SWEEP_C_START = 5.0
_SWEEP_C_END = 8.5
_SWEEP_C_RIGHT = math.sqrt(_SWEEP_LEG**2 + _SWEEP_LEG**2)  # √50 ≈ 7.07


def _sort_sides(a: float, b: float, c: float) -> tuple[float, float, float]:
    sides = sorted([float(a), float(b), float(c)])
    return sides[0], sides[1], sides[2]


def _classify(a: float, b: float, c: float) -> tuple[str, str]:
    sa, sb, sc = _sort_sides(a, b, c)
    sum_sq = sa * sa + sb * sb
    c_sq = sc * sc
    if math.isclose(c_sq, sum_sq, rel_tol=1e-6, abs_tol=0.5):
        return "Right-angled", "right"
    if c_sq < sum_sq:
        return "Acute", "acute"
    return "Obtuse", "obtuse"


def _color_for(kind: str):
    return {"right": _COLOR_RIGHT, "acute": _COLOR_ACUTE, "obtuse": _COLOR_OBTUSE}[kind]


def _triangle_vertices(side_a: float, side_b: float, side_c: float) -> list[list[float]]:
    sa, sb, sc = _sort_sides(side_a, side_b, side_c)
    if sa + sb <= sc:
        raise ValueError("Invalid triangle")
    x = (sb * sb - sa * sa + sc * sc) / (2 * sc)
    y = math.sqrt(max(0.0, sb * sb - x * x))
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
        # Burned-in SRT subs from manim-voiceover lag behind edge-tts audio and sit on
        # the bottom edge (clipping). On-screen labels carry the narration instead.
        self.set_speech_service(
            VoiceoverSynthesizer.create_service(),
            create_subcaption=False,
        )
        p = self.params
        include_sweep = bool(p.get("include_sweep", True))

        title = Text("Converse of Pythagoras", font_size=34)
        subtitle = Text(
            "Classify from side lengths (not drawn to scale)",
            font_size=22,
            color=TEAL,
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.35)

        with self.voiceover(
            text=(
                "When you know three side lengths but not the angles, use the converse "
                "of Pythagoras. Find the longest side, call it c, then compare "
                "c squared with a squared plus b squared."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(header), run_time=min(0.8, tracker.duration * 0.2))
            self.wait(max(0.0, tracker.duration - min(0.8, tracker.duration * 0.2)))

        rule = MathTex(
            r"\text{Longest side } c:\quad",
            r"c^2",
            r" \stackrel{?}{=} ",
            r"a^2 + b^2",
            font_size=36,
        )
        rule.next_to(header, DOWN, buff=0.35)
        fit_in_vertical_band(rule)

        with self.voiceover(
            text=(
                "If c squared equals a squared plus b squared, the triangle is right angled. "
                "If c squared is less, the triangle is acute. "
                "If c squared is greater, the triangle is obtuse."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(rule), run_time=min(0.6, tracker.duration * 0.15))
            self.wait(max(0.0, tracker.duration - min(0.6, tracker.duration * 0.15)))

        for example in _KEY_EXAMPLES:
            self._play_example(example, rule)

        if include_sweep:
            self._play_parameter_sweep(rule)

        prompt_sides = (float(p["side_a"]), float(p["side_b"]), float(p["side_c"]))
        if prompt_sides not in _KEY_EXAMPLES:
            banner = Text("From your Prompt", font_size=24, color=YELLOW)
            place_below(rule, banner, buff=0.25)
            self.play(FadeIn(banner))
            self._play_example(prompt_sides, rule)
            self.play(FadeOut(banner))

        with self.voiceover(
            text="Remember: always use the longest side as c before you compare the squares.",
            subcaption_buff=0,
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
        sum_sq = sa * sa + sb * sb
        c_sq = sc * sc

        verts = _triangle_vertices(a, b, c)
        tri = Polygon(*verts, color=color, fill_opacity=0.25, stroke_width=3)
        tri.scale(0.75)

        example_title = Text(f"Sides {a:g}, {b:g}, {c:g}", font_size=24, color=color)
        readout = MathTex(
            rf"c^2 = {c_sq:g}",
            r" \quad\text{vs}\quad ",
            rf"a^2+b^2 = {sum_sq:g}",
            font_size=28,
        )
        if kind == "right":
            relation = MathTex(rf"{c_sq:g} = {sum_sq:g}", color=color, font_size=30)
        elif kind == "acute":
            relation = MathTex(rf"{c_sq:g} < {sum_sq:g}", color=color, font_size=30)
        else:
            relation = MathTex(rf"{c_sq:g} > {sum_sq:g}", color=color, font_size=30)

        verdict = Text(label, font_size=32, color=color)
        panel = VGroup(readout, relation, verdict).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        content = VGroup(example_title, tri, panel).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        place_below(rule, content, buff=0.4)

        narration = (
            f"For sides {a:g}, {b:g}, and {c:g}, the longest side is {sc:g}. "
            f"c squared is {c_sq:g}, and a squared plus b squared is {sum_sq:g}. "
            f"So this triangle is {label.lower()}."
        )

        with self.voiceover(text=narration, subcaption_buff=0) as tracker:
            # Show all on-screen text at the start so visuals match the narration (no lag).
            reveal = min(0.9, tracker.duration * 0.12)
            self.play(FadeIn(content), run_time=reveal)
            self.play(Indicate(verdict, color=color), run_time=min(0.5, tracker.duration * 0.1))
            self.wait(max(0.0, tracker.duration - reveal - min(0.5, tracker.duration * 0.1)))

        self.play(FadeOut(content))

    def _play_parameter_sweep(self, rule: MathTex) -> None:
        """Sweep c with legs fixed at 5 — acute (c=5) → right (c≈7.07) → obtuse (c=8.5)."""

        c_tracker = ValueTracker(_SWEEP_C_START)
        leg = _SWEEP_LEG

        def make_group() -> VGroup:
            c_val = c_tracker.get_value()
            verts = _triangle_vertices(leg, leg, c_val)
            label, kind = _classify(leg, leg, c_val)
            color = _color_for(kind)
            tri = Polygon(*verts, color=color, fill_opacity=0.25, stroke_width=3)
            tri.scale(0.65)
            sa, sb, sc = _sort_sides(leg, leg, c_val)
            sum_sq = sa * sa + sb * sb
            c_sq = sc * sc
            readout = MathTex(
                rf"c = {c_val:.2f},\quad c^2 = {c_sq:.1f}",
                r" \quad\text{vs}\quad ",
                rf"a^2+b^2 = {sum_sq:.0f}",
                font_size=26,
            )
            tag = Text(label, font_size=30, color=color)
            column = VGroup(tri, readout, tag).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
            return column

        sweep_group = always_redraw(make_group)
        banner = Text(
            f"Sweeping c from {_SWEEP_C_START:g} to {_SWEEP_C_END:g} (legs {_SWEEP_LEG:g} and {_SWEEP_LEG:g})",
            font_size=20,
        )
        sweep_column = VGroup(banner, sweep_group).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        place_below(rule, sweep_column, buff=0.3)
        layout = sweep_column

        with self.voiceover(
            text=(
                "With the other two sides fixed at five, watch the label change. "
                "Acute when c squared is less than fifty, "
                "right angled when c is about seven point one, "
                "and obtuse when c grows larger still."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(layout), run_time=min(0.8, tracker.duration * 0.1))
            anim_time = tracker.duration * 0.85
            self.play(
                c_tracker.animate.set_value(_SWEEP_C_END),
                run_time=anim_time,
                rate_func=lambda t: t,
            )
            self.wait(max(0.0, tracker.duration - min(0.8, tracker.duration * 0.1) - anim_time))

        self.play(FadeOut(layout))
