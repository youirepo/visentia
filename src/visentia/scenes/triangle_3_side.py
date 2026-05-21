"""Triangle3Side — Converse of Pythagoras (EV-001)."""

from __future__ import annotations

import math
from typing import ClassVar, Literal

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
    np,
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

from visentia.scenes.layout import as_diagram_shape, as_on_screen_text, place_in_band_below
from visentia.voiceover import VoiceoverSynthesizer

_KEY_EXAMPLES: list[tuple[float, float, float]] = [
    (3, 4, 5),
    (5, 5, 6),
    (5, 5, 7),
]

_SWEEP_LEG = 5.0
_SWEEP_C_START = 5.0
_SWEEP_C_END = 8.5

# Outward offset from each edge (clear gap above the stroke).
_SIDE_LABEL_OFFSET = 0.22


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
    return {"right": GREEN, "acute": TEAL, "obtuse": RED}[kind]


def _triangle_vertices(side_a: float, side_b: float, side_c: float) -> list[list[float]]:
    sa, sb, sc = _sort_sides(side_a, side_b, side_c)
    if sa + sb <= sc:
        raise ValueError("Invalid triangle")
    x = (sb * sb - sa * sa + sc * sc) / (2 * sc)
    y = math.sqrt(max(0.0, sb * sb - x * x))
    return [[0.0, 0.0, 0.0], [float(x), float(y), 0.0], [float(sc), 0.0, 0.0]]


def _format_side_length(value: float) -> str:
    if math.isclose(value, round(value), rel_tol=0, abs_tol=1e-6):
        return str(int(round(value)))
    return f"{value:g}"


def _edge_label_position(
    v_start: list[float],
    v_end: list[float],
    v_other: list[float],
    *,
    offset: float = _SIDE_LABEL_OFFSET,
) -> np.ndarray:
    """Midpoint of an edge, shifted outward (away from the third vertex)."""

    p1 = np.array(v_start, dtype=float)
    p2 = np.array(v_end, dtype=float)
    p3 = np.array(v_other, dtype=float)
    mid = (p1 + p2) / 2
    edge = p2 - p1
    perp = np.array([-edge[1], edge[0], 0.0])
    norm = float(np.linalg.norm(perp[:2]))
    if norm < 1e-9:
        perp = np.array([0.0, 1.0, 0.0])
    else:
        perp /= norm
    centroid = (p1 + p2 + p3) / 3
    if float(np.dot(perp, centroid - mid)) > 0:
        perp = -perp
    return mid + perp * offset


def _side_label_mob(
    text: str,
    v_start: list[float],
    v_end: list[float],
    v_other: list[float],
    *,
    color=WHITE,
    font_size: int = 28,
    highlight: bool = False,
) -> MathTex:
    mob = as_on_screen_text(MathTex(text, color=YELLOW if highlight else color, font_size=font_size))
    pos = _edge_label_position(v_start, v_end, v_other)
    mob.move_to(pos)
    edge = np.array(v_end, dtype=float) - np.array(v_start, dtype=float)
    if float(np.linalg.norm(edge[:2])) > 1e-9:
        mob.rotate(math.atan2(edge[1], edge[0]), about_point=mob.get_center())
    return mob


def _labeled_triangle(
    side_a: float,
    side_b: float,
    side_c: float,
    *,
    scale: float = 0.85,
    label_mode: Literal["variables", "lengths"] = "variables",
) -> VGroup:
    """Triangle with labels centered on each side, just outside the edge."""

    sa, sb, sc = _sort_sides(side_a, side_b, side_c)
    verts = _triangle_vertices(side_a, side_b, side_c)
    v0, v1, v2 = verts  # base v0–v2 is longest (c); v0–v1 is a; v1–v2 is b.

    tri = as_diagram_shape(
        Polygon(*verts, color=WHITE, fill_opacity=0.15, stroke_width=3)
    )

    if label_mode == "variables":
        label_a = _side_label_mob("a", v0, v1, v2)
        label_b = _side_label_mob("b", v1, v2, v0)
        label_c = _side_label_mob("c", v0, v2, v1, highlight=True, font_size=32)
    else:
        label_a = _side_label_mob(_format_side_length(sa), v0, v1, v2)
        label_b = _side_label_mob(_format_side_length(sb), v1, v2, v0)
        label_c = _side_label_mob(
            _format_side_length(sc),
            v0,
            v2,
            v1,
            highlight=True,
            font_size=32,
        )

    group = VGroup(tri, label_a, label_b, label_c)
    group.scale(scale)
    return group


class Triangle3SideScene(VoiceoverScene):
    params: ClassVar[dict] = {
        "side_a": 3,
        "side_b": 4,
        "side_c": 5,
        "include_sweep": True,
    }

    def construct(self) -> None:
        self.set_speech_service(
            VoiceoverSynthesizer.create_service(),
            create_subcaption=False,
        )
        p = self.params
        include_sweep = bool(p.get("include_sweep", True))

        header = as_on_screen_text(
            VGroup(
                Text("Converse of Pythagoras", font_size=34),
                Text(
                    "Classify from side lengths (not drawn to scale)",
                    font_size=22,
                    color=TEAL,
                ),
            ).arrange(DOWN, buff=0.2)
        ).to_edge(UP, buff=0.35)

        # --- Intro: diagram while explaining longest side c ---
        intro_tri = _labeled_triangle(3, 4, 5, scale=0.9)
        place_in_band_below(header, intro_tri, buff=0.45)

        with self.voiceover(
            text=(
                "When you know three side lengths but not the angles, use the converse "
                "of Pythagoras. First find the longest side — that is c. "
                "Then compare c squared with a squared plus b squared."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(header), run_time=min(0.4, tracker.duration * 0.1))
            self.play(Create(intro_tri[0]), FadeIn(intro_tri[1:]), run_time=min(1.0, tracker.duration * 0.35))
            self.play(Indicate(intro_tri[3], color=YELLOW), run_time=min(0.6, tracker.duration * 0.2))
            self.wait(max(0.0, tracker.duration - min(2.0, tracker.duration * 0.65)))

        # --- Rules: one on-screen formula per spoken case ---
        rule = as_on_screen_text(
            MathTex(
                r"\text{Longest side } c:\quad c^2 \stackrel{?}{=} a^2 + b^2",
                font_size=34,
            )
        )
        case_right = as_on_screen_text(
            VGroup(
                MathTex(r"c^2 = a^2 + b^2", color=GREEN, font_size=32),
                Text("→ Right-angled", font_size=26, color=GREEN),
            ).arrange(RIGHT, buff=0.35)
        )
        case_acute = as_on_screen_text(
            VGroup(
                MathTex(r"c^2 < a^2 + b^2", color=TEAL, font_size=32),
                Text("→ Acute", font_size=26, color=TEAL),
            ).arrange(RIGHT, buff=0.35)
        )
        case_obtuse = as_on_screen_text(
            VGroup(
                MathTex(r"c^2 > a^2 + b^2", color=RED, font_size=32),
                Text("→ Obtuse", font_size=26, color=RED),
            ).arrange(RIGHT, buff=0.35)
        )
        rules_panel = (
            VGroup(rule, case_right, case_acute, case_obtuse)
            .arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        )
        place_in_band_below(header, rules_panel, buff=0.35)
        case_right.set_opacity(0)
        case_acute.set_opacity(0)
        case_obtuse.set_opacity(0)

        self.play(FadeOut(intro_tri))

        with self.voiceover(
            text="If c squared equals a squared plus b squared, the triangle is right angled.",
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(rule), run_time=min(0.5, tracker.duration * 0.15))
            self.play(case_right.animate.set_opacity(1), run_time=min(0.4, tracker.duration * 0.15))
            self.wait(max(0.0, tracker.duration - min(0.9, tracker.duration * 0.3)))

        with self.voiceover(
            text="If c squared is less than a squared plus b squared, the triangle is acute.",
            subcaption_buff=0,
        ) as tracker:
            self.play(case_acute.animate.set_opacity(1), run_time=min(0.4, tracker.duration * 0.2))
            self.wait(max(0.0, tracker.duration - min(0.4, tracker.duration * 0.2)))

        with self.voiceover(
            text="If c squared is greater than a squared plus b squared, the triangle is obtuse.",
            subcaption_buff=0,
        ) as tracker:
            self.play(case_obtuse.animate.set_opacity(1), run_time=min(0.4, tracker.duration * 0.2))
            self.wait(max(0.0, tracker.duration - min(0.4, tracker.duration * 0.2)))

        # Clear the rules band before examples so triangles never draw over formulas.
        self.play(FadeOut(rules_panel))

        for example in _KEY_EXAMPLES:
            self._play_example(example, header)

        if include_sweep:
            self._play_parameter_sweep(header)

        prompt_sides = (float(p["side_a"]), float(p["side_b"]), float(p["side_c"]))
        if prompt_sides not in _KEY_EXAMPLES:
            banner = as_on_screen_text(Text("From your Prompt", font_size=24, color=YELLOW))
            place_in_band_below(header, banner, buff=0.35)
            self.play(FadeIn(banner))
            self._play_example(prompt_sides, header)
            self.play(FadeOut(banner))

        with self.voiceover(
            text="Remember: always use the longest side as c before you compare the squares.",
            subcaption_buff=0,
        ) as tracker:
            self.wait(tracker.duration)

    def _play_example(
        self,
        sides: tuple[float, float, float],
        header: VGroup,
    ) -> None:
        a, b, c = sides
        label, kind = _classify(a, b, c)
        color = _color_for(kind)
        sa, sb, sc = _sort_sides(a, b, c)
        sum_sq = sa * sa + sb * sb
        c_sq = sc * sc

        tri = _labeled_triangle(a, b, c, scale=0.7, label_mode="lengths")
        tri[0].set_color(color).set_fill(color, opacity=0.25)

        example_title = as_on_screen_text(
            Text(f"Example: sides {a:g}, {b:g}, {c:g}", font_size=24, color=color)
        )
        readout = as_on_screen_text(
            MathTex(
                rf"c^2 = {c_sq:g}",
                r" \quad\text{vs}\quad ",
                rf"a^2+b^2 = {sum_sq:g}",
                font_size=28,
            )
        )
        if kind == "right":
            relation = MathTex(rf"{c_sq:g} = {sum_sq:g}", color=color, font_size=30)
        elif kind == "acute":
            relation = MathTex(rf"{c_sq:g} < {sum_sq:g}", color=color, font_size=30)
        else:
            relation = MathTex(rf"{c_sq:g} > {sum_sq:g}", color=color, font_size=30)
        relation = as_on_screen_text(relation)
        verdict = as_on_screen_text(Text(label, font_size=32, color=color))

        # Text above triangle in the column so labels are never covered.
        content = (
            VGroup(example_title, readout, relation, verdict, tri)
            .arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        )
        place_in_band_below(header, content, buff=0.4)

        narration = (
            f"For sides {a:g}, {b:g}, and {c:g}, the longest side is {sc:g}. "
            f"c squared is {c_sq:g}, and a squared plus b squared is {sum_sq:g}. "
            f"So this triangle is {label.lower()}."
        )

        with self.voiceover(text=narration, subcaption_buff=0) as tracker:
            reveal = min(0.8, tracker.duration * 0.12)
            self.play(FadeIn(content), run_time=reveal)
            self.play(Indicate(verdict, color=color), run_time=min(0.4, tracker.duration * 0.1))
            self.wait(max(0.0, tracker.duration - reveal - min(0.4, tracker.duration * 0.1)))

        self.play(FadeOut(content))

    def _play_parameter_sweep(self, header: VGroup) -> None:
        c_tracker = ValueTracker(_SWEEP_C_START)
        leg = _SWEEP_LEG

        banner = as_on_screen_text(
            Text(
                f"Sweeping longest side c from {_SWEEP_C_START:g} to {_SWEEP_C_END:g} (other sides {_SWEEP_LEG:g}, {_SWEEP_LEG:g})",
                font_size=22,
            )
        )

        def make_sweep_column() -> VGroup:
            c_val = c_tracker.get_value()
            label, kind = _classify(leg, leg, c_val)
            color = _color_for(kind)
            sa, sb, sc = _sort_sides(leg, leg, c_val)
            sum_sq = sa * sa + sb * sb
            c_sq = sc * sc

            readout = as_on_screen_text(
                MathTex(
                    rf"c = {c_val:.2f},\quad c^2 = {c_sq:.1f}",
                    r" \quad\text{vs}\quad ",
                    rf"a^2+b^2 = {sum_sq:.0f}",
                    font_size=26,
                )
            )
            tag = as_on_screen_text(Text(label, font_size=34, color=color))
            tri = _labeled_triangle(leg, leg, c_val, scale=0.55, label_mode="lengths")
            tri[0].set_color(color).set_fill(color, opacity=0.25)

            return VGroup(banner, readout, tag, tri).arrange(DOWN, buff=0.25, aligned_edge=LEFT)

        sweep = always_redraw(make_sweep_column)
        place_in_band_below(header, sweep, buff=0.45)

        with self.voiceover(
            text=(
                "With the other two sides fixed at five, watch the label change. "
                "Acute when c squared is less than fifty, "
                "right angled when c is about seven point one, "
                "and obtuse when c grows larger still."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(sweep), run_time=min(0.6, tracker.duration * 0.1))
            anim_time = tracker.duration * 0.85
            self.play(
                c_tracker.animate.set_value(_SWEEP_C_END),
                run_time=anim_time,
                rate_func=lambda t: t,
            )
            self.wait(max(0.0, tracker.duration - min(0.6, tracker.duration * 0.1) - anim_time))

        self.play(FadeOut(sweep))
