"""CalculusOnCurve — gradients, tangents, limits and area (issue #33).

The second Stage 6 functions-and-calculus template. Where `FunctionGraph` says what a
curve *is*, this one says what calculus *does to it*: the two ideas Stage 6 calculus is
built on — the gradient at a point as the limit of a secant, and the area under a curve as
the limit of a sum — plus the beats that surround them.

Beats (played in `params["beats"]` order):

- ``tangent_at``        — the tangent at a point, with its gradient stated
- ``secant_to_tangent`` — a secant collapsing onto the tangent as h shrinks (first principles)
- ``gradient_function`` — the derivative plotted beneath the function, features aligned
- ``riemann_sum``       — rectangles under the curve, refined through successive counts
- ``area_under``        — the shaded definite integral the rectangles converge to
- ``limit_approach``    — values of the function as x approaches a point from both sides

The two limit beats (``secant_to_tangent``, ``riemann_sum``) are the reason this template
exists: both are the *same* visual argument — a crude approximation refined until it stops
moving — and both are near-impossible to get right in free-form generated Manim.

**Known limitation.** The axes are scaled independently to fill the plotting band, so the
x and y units are generally different lengths on screen. Gradients are therefore correct
as *stated* but not as *measured with a protractor* — a tangent of gradient 1 will not
meet the axis at 45 degrees unless the two ranges happen to match. This matches how a
Stage 6 graph is usually drawn by hand, but it is worth knowing before reading an angle
off a rendered frame.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
from manim import (
    BLACK,
    BLUE,
    DOWN,
    GREEN,
    GREY,
    ORANGE,
    RED,
    RIGHT,
    UP,
    YELLOW,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    MathTex,
    Transform,
    VGroup,
    Write,
)

from visentia.scenes.expressions import DERIVATIVE_STEP, Function, parse_function
from visentia.scenes.graph_substrate import (
    GraphTemplateScene,
    area_under_curve,
    coordinate_label,
    line_through,
    marker_dot,
    plot_curve,
    point_on,
    riemann_rectangles,
)
from visentia.scenes.layout import as_on_screen_text


class CalculusOnCurveScene(GraphTemplateScene):
    title = "Calculus on a curve"

    BEATS: ClassVar[dict[str, str]] = {
        "tangent_at": "_play_tangent_at",
        "secant_to_tangent": "_play_secant_to_tangent",
        "gradient_function": "_play_gradient_function",
        "riemann_sum": "_play_riemann_sum",
        "area_under": "_play_area_under",
        "limit_approach": "_play_limit_approach",
    }

    params: ClassVar[dict] = {
        "title": "Gradient of a curve",
        "function": "x**2",
        "x_min": -1.0,
        "x_max": 3.0,
        "beats": [
            {"kind": "tangent_at", "x": 1.5},
        ],
    }

    # --- the tangent at a point ---------------------------------------------

    def _play_tangent_at(self, beat: dict) -> None:
        heading_text = beat.get("heading", "Tangent")
        x = float(beat["x"])
        y = self.function.at(x)
        gradient = self.function.derivative_at(x)

        dot = marker_dot(self.axes, self.function, x, color=YELLOW)
        tangent = line_through(
            self.axes, self.window, x0=x, y0=y, gradient=gradient, color=YELLOW
        )
        readout = as_on_screen_text(
            MathTex(
                rf"f'({_num(x)}) = {_num(gradient)}",
                font_size=32,
                color=YELLOW,
            )
        ).move_to([-4.4, self.window_top_y(), 0.0])

        with self.voiceover(
            text=(
                f"Take the point where x equals {_spoken(x)}. "
                '<bookmark mark="dot"/> The tangent at that point '
                '<bookmark mark="tangent"/> touches the curve and matches its direction. '
                '<bookmark mark="value"/> Its gradient is the derivative there: '
                f"{_spoken(gradient)}."
            )
        ):
            self._show_heading(heading_text)
            self.play(Write(self.curve_label), run_time=0.5)
            if self.curve not in self.mobjects:
                self.play(Create(self.curve), run_time=1.0)
            self.wait_until_bookmark("dot")
            self.play(FadeIn(dot, scale=0.5), run_time=0.4)
            self.wait_until_bookmark("tangent")
            self.play(Create(tangent), run_time=0.9)
            self.wait_until_bookmark("value")
            self.play(FadeIn(readout), run_time=0.5)
            self.wait_for_voiceover()

        self._clear_beat(dot, tangent, readout)

    # --- first principles: secant collapsing onto the tangent ----------------

    def _play_secant_to_tangent(self, beat: dict) -> None:
        heading_text = beat.get("heading", "From first principles")
        x = float(beat["x"])
        y = self.function.at(x)
        steps = _shrinking_steps(beat, self.window.x_max - x)

        fixed_dot = marker_dot(self.axes, self.function, x, color=YELLOW)
        moving_dot = Dot(point_on(self.axes, self.function, x + steps[0]), color=RED, radius=0.075)
        secant = self._secant(x, steps[0])
        readout = self._gradient_readout(steps[0], _secant_gradient(self.function, x, steps[0]))

        with self.voiceover(
            text=(
                "The gradient of a curve at a point is not something we can read off directly. "
                '<bookmark mark="secant"/> So take a second point a distance h away and draw '
                "the line between them — that gradient we can compute. "
                '<bookmark mark="shrink"/> Now let h shrink. '
                "As the second point slides towards the first, the line steadies onto a single "
                "direction. "
                '<bookmark mark="tangent"/> That limit is the tangent, and its gradient is the '
                "derivative."
            )
        ):
            self._show_heading(heading_text)
            if self.curve not in self.mobjects:
                self.play(Create(self.curve), Write(self.curve_label), run_time=1.0)
            self.play(FadeIn(fixed_dot, scale=0.5), run_time=0.3)

            self.wait_until_bookmark("secant")
            self.play(FadeIn(moving_dot, scale=0.5), Create(secant), FadeIn(readout), run_time=0.8)

            self.wait_until_bookmark("shrink")
            for step in steps[1:]:
                new_secant = self._secant(x, step)
                new_readout = self._gradient_readout(step, _secant_gradient(self.function, x, step))
                self.play(
                    Transform(secant, new_secant),
                    Transform(readout, new_readout),
                    moving_dot.animate.move_to(point_on(self.axes, self.function, x + step)),
                    run_time=0.55,
                )

            self.wait_until_bookmark("tangent")
            tangent = line_through(
                self.axes,
                self.window,
                x0=x,
                y0=y,
                gradient=self.function.derivative_at(x),
                color=YELLOW,
            )
            final_readout = self._gradient_readout(None, self.function.derivative_at(x))
            self.play(
                Transform(secant, tangent),
                Transform(readout, final_readout),
                FadeOut(moving_dot),
                run_time=0.9,
            )
            self.wait_for_voiceover()

        self._clear_beat(fixed_dot, secant, readout)

    def _secant(self, x: float, step: float):
        gradient = _secant_gradient(self.function, x, step)
        return line_through(
            self.axes,
            self.window,
            x0=x,
            y0=self.function.at(x),
            gradient=gradient,
            color=RED,
            stroke_width=2.5,
            # The secant is *defined* by the two points, so it has to reach both of them —
            # a line stopping short of the moving point reads as a different line.
            half_width=max(abs(step) * 1.25, (self.window.x_max - self.window.x_min) / 5),
        )

    def _gradient_readout(self, step: float | None, gradient: float) -> VGroup:
        if step is None:
            body = rf"h \to 0:\quad \text{{gradient}} = {_num(gradient)}"
        else:
            body = rf"h = {_num(step)}:\quad \text{{gradient}} = {_num(gradient)}"
        readout = as_on_screen_text(
            MathTex(body, font_size=30, color=YELLOW if step is None else RED)
        )
        readout.move_to([-3.9, self.window_top_y(), 0.0])
        return VGroup(readout)

    # --- the derivative as a curve in its own right --------------------------

    def _play_gradient_function(self, beat: dict) -> None:
        heading_text = beat.get("heading", "The gradient function")
        derivative = _numeric_derivative(self.function)
        derivative_curve = plot_curve(self.axes, derivative, self.window, color=GREEN, stroke_width=3.0)
        label = self._curve_label(derivative, color=GREEN)
        reflow = self._layout_curve_labels(derivative_curve)

        with self.voiceover(
            text=(
                "The derivative is itself a function: at every x it gives the gradient of the "
                "original curve. "
                '<bookmark mark="plot"/> Plotted on the same axes, '
                "it crosses zero exactly where the original curve turns, "
                "is positive where the curve rises, and negative where it falls."
            )
        ):
            self._show_heading(heading_text)
            if self.curve not in self.mobjects:
                self.play(Create(self.curve), Write(self.curve_label), run_time=1.0)
            self.wait_until_bookmark("plot")
            self.play(Create(derivative_curve), FadeIn(label), *reflow, run_time=1.4)
            self.wait_for_voiceover()

        self._clear_beat(derivative_curve, label)

    # --- area as a limit of sums ---------------------------------------------

    def _play_riemann_sum(self, beat: dict) -> None:
        heading_text = beat.get("heading", "Area as a sum")
        lower, upper = float(beat["lower"]), float(beat["upper"])
        counts = [int(count) for count in beat.get("counts", [4, 8, 16, 32])]

        rectangles = riemann_rectangles(
            self.axes, self.function, self.window, lower=lower, upper=upper, count=counts[0]
        )
        readout = self._count_readout(counts[0])

        with self.voiceover(
            text=(
                f"To find the area under the curve between {_spoken(lower)} and {_spoken(upper)}, "
                "start with something we can already do: rectangles. "
                '<bookmark mark="rects"/> A handful of them is a rough estimate. '
                '<bookmark mark="refine"/> Use more, and each one hugs the curve more closely. '
                "The estimate settles on a value, and that value is the exact area."
            )
        ):
            self._show_heading(heading_text)
            if self.curve not in self.mobjects:
                self.play(Create(self.curve), Write(self.curve_label), run_time=1.0)
            self.wait_until_bookmark("rects")
            self.play(FadeIn(rectangles), FadeIn(readout), run_time=0.7)
            self.wait_until_bookmark("refine")
            for count in counts[1:]:
                self.play(
                    Transform(
                        rectangles,
                        riemann_rectangles(
                            self.axes,
                            self.function,
                            self.window,
                            lower=lower,
                            upper=upper,
                            count=count,
                        ),
                    ),
                    Transform(readout, self._count_readout(count)),
                    run_time=0.7,
                )
            self.wait_for_voiceover()

        self._clear_beat(rectangles, readout)

    def _count_readout(self, count: int) -> VGroup:
        readout = as_on_screen_text(
            MathTex(rf"n = {count}", font_size=30, color=BLUE)
        ).move_to([-5.0, self.window_top_y(), 0.0])
        return VGroup(readout)

    def _play_area_under(self, beat: dict) -> None:
        heading_text = beat.get("heading", "The definite integral")
        lower, upper = float(beat["lower"]), float(beat["upper"])

        region = area_under_curve(
            self.axes, self.function, self.window, lower=lower, upper=upper
        )
        bounds = VGroup(
            *[
                DashedLine(
                    self.axes.coords_to_point(value, self.window.y_min),
                    self.axes.coords_to_point(value, self.function.at(value)),
                    dash_length=0.1,
                    stroke_width=2,
                    color=GREY,
                )
                for value in (lower, upper)
                if self.function.is_finite_at(value)
            ]
        )
        notation = as_on_screen_text(
            MathTex(
                rf"\int_{{{_num(lower)}}}^{{{_num(upper)}}} f(x)\,dx",
                font_size=34,
                color=BLUE,
            )
        ).move_to([-4.6, self.window_top_y(), 0.0])

        with self.voiceover(
            text=(
                "The exact area is written like this. "
                '<bookmark mark="notation"/> The integral sign is a stretched S, for sum — '
                "it is the sum the rectangles were approaching. "
                '<bookmark mark="shade"/> The numbers on it are the two ends of the region.'
            )
        ):
            self._show_heading(heading_text)
            if self.curve not in self.mobjects:
                self.play(Create(self.curve), Write(self.curve_label), run_time=1.0)
            self.wait_until_bookmark("notation")
            self.play(Write(notation), run_time=0.8)
            self.wait_until_bookmark("shade")
            self.play(Create(bounds), FadeIn(region), run_time=1.0)
            self.wait_for_voiceover()

        self._clear_beat(region, bounds, notation)

    # --- limits --------------------------------------------------------------

    def _play_limit_approach(self, beat: dict) -> None:
        heading_text = beat.get("heading", "Approaching a value")
        x = float(beat["x"])
        offsets = _shrinking_steps(beat, min(1.0, (self.window.x_max - self.window.x_min) / 4))

        target = DashedLine(
            self.axes.coords_to_point(x, self.window.y_min),
            self.axes.coords_to_point(x, self.window.y_max),
            dash_length=0.1,
            stroke_width=2,
            color=GREY,
        )
        # Where the function is undefined at the point itself — a removable discontinuity
        # like (x^2-1)/(x-1) at x = 1 — the curve is drawn through the gap because no sample
        # lands exactly on it. An open circle is how Stage 6 writes "not defined here", and
        # it is the whole reason the limit is worth asking about.
        hole = None
        if not self.function.is_finite_at(x):
            approached = (self.function.at(x - 1e-4) + self.function.at(x + 1e-4)) / 2.0
            if np.isfinite(approached) and self.window.contains_y(approached):
                hole = Circle(
                    radius=0.09,
                    color=self.window_hole_color(),
                    stroke_width=3.0,
                ).move_to(self.axes.coords_to_point(x, approached))
                hole.set_fill(BLACK, opacity=1.0)

        left_dot = Dot(point_on(self.axes, self.function, x - offsets[0]), color=ORANGE, radius=0.07)
        right_dot = Dot(point_on(self.axes, self.function, x + offsets[0]), color=GREEN, radius=0.07)
        readout = self._limit_readout(x, offsets[0])

        with self.voiceover(
            text=(
                f"What happens to this function as x approaches {_spoken(x)}? "
                '<bookmark mark="approach"/> Come in from the left and from the right at the '
                "same time, and watch the two values. "
                '<bookmark mark="converge"/> If they meet, that shared value is the limit.'
            )
        ):
            self._show_heading(heading_text)
            if self.curve not in self.mobjects:
                self.play(Create(self.curve), Write(self.curve_label), run_time=1.0)
            self.play(Create(target), run_time=0.5)
            if hole is not None:
                self.play(Create(hole), run_time=0.4)
            self.wait_until_bookmark("approach")
            self.play(FadeIn(left_dot), FadeIn(right_dot), FadeIn(readout), run_time=0.5)
            self.wait_until_bookmark("converge")
            for offset in offsets[1:]:
                self.play(
                    left_dot.animate.move_to(point_on(self.axes, self.function, x - offset)),
                    right_dot.animate.move_to(point_on(self.axes, self.function, x + offset)),
                    Transform(readout, self._limit_readout(x, offset)),
                    run_time=0.6,
                )
            self.wait_for_voiceover()

        self._clear_beat(target, left_dot, right_dot, readout, hole)

    def _limit_readout(self, x: float, offset: float) -> VGroup:
        left_value = self.function.at(x - offset)
        right_value = self.function.at(x + offset)
        readout = as_on_screen_text(
            VGroup(
                MathTex(rf"f({_num(x - offset)}) = {_num(left_value)}", font_size=26, color=ORANGE),
                MathTex(rf"f({_num(x + offset)}) = {_num(right_value)}", font_size=26, color=GREEN),
            ).arrange(DOWN, buff=0.15, aligned_edge=RIGHT)
        )
        readout.move_to([-4.3, self.window_top_y() - 0.2, 0.0])
        return VGroup(readout)

    # --- shared --------------------------------------------------------------

    def window_hole_color(self):
        """Colour of the open circle marking a point the function does not reach."""

        return YELLOW

    def window_top_y(self) -> float:
        """y-coordinate for readouts: just under the beat heading, clear of the curve."""

        return 1.55


def _numeric_derivative(function: Function) -> Function:
    """`function`'s derivative, as another `Function` that can be plotted like any other."""

    def evaluate(x):
        x = np.asarray(x, dtype=float)
        with np.errstate(all="ignore"):
            return (function(x + DERIVATIVE_STEP) - function(x - DERIVATIVE_STEP)) / (
                2.0 * DERIVATIVE_STEP
            )

    return Function(source=f"d/dx {function.source}", latex=r"f'(x)", _callable=evaluate)


def _secant_gradient(function: Function, x: float, step: float) -> float:
    return (function.at(x + step) - function.at(x)) / step


def _shrinking_steps(beat: dict, span: float) -> list[float]:
    """A halving sequence of h values, from the beat or from the plotted span."""

    declared = beat.get("steps")
    if declared:
        return [float(step) for step in declared]

    start = float(beat.get("h", min(2.0, max(0.4, span / 2.0))))
    return [start, start / 2, start / 4, start / 8]


def _num(value: float) -> str:
    number = float(value)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.2f}".rstrip("0").rstrip(".")


def _spoken(value: float) -> str:
    return _num(value).replace("-", "negative ")
