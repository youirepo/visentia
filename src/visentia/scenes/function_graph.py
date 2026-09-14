"""FunctionGraph — curve sketching, features, and transformations (issue #33).

The first of two Stage 6 functions-and-calculus templates. It answers "what does this
function look like, and why does it look like that": plot the curve, name its features,
move it, and set it beside a related curve.

Beats (played in `params["beats"]` order — the list *is* the animation sequence):

- ``plot``           — draw the curve and label it
- ``intercepts``     — reveal x-intercepts and the y-intercept
- ``turning_point``  — mark a stationary point, classified as maximum or minimum
- ``asymptote``      — dash in the vertical asymptotes and show the curve approaching one
- ``transform``      — morph the curve into a transformed version of itself
- ``compare_curves`` — draw a second curve alongside the first

Feature beats take a declared ``x`` when the Tutor or the syllabus states one, and find it
numerically otherwise (see `expressions.find_turning_points`). Either way the beat draws
the same thing, so a wrong declared value is visible rather than silently rendered.
"""

from __future__ import annotations

from typing import ClassVar

from manim import (
    BLUE,
    DOWN,
    GREEN,
    ORANGE,
    RIGHT,
    UP,
    YELLOW,
    Create,
    FadeIn,
    FadeOut,
    Flash,
    MathTex,
    Transform,
    VGroup,
    Write,
)

from visentia.scenes.expressions import (
    find_roots,
    find_turning_points,
    find_vertical_asymptotes,
    parse_function,
)
from visentia.scenes.graph_substrate import (
    GraphTemplateScene,
    asymptote_lines,
    coordinate_label,
    marker_dot,
    place_label_clear,
    plot_curve,
)
from visentia.scenes.layout import as_on_screen_text


class FunctionGraphScene(GraphTemplateScene):
    title = "Sketching a function"

    BEATS: ClassVar[dict[str, str]] = {
        "plot": "_play_plot",
        "intercepts": "_play_intercepts",
        "turning_point": "_play_turning_point",
        "asymptote": "_play_asymptote",
        "transform": "_play_transform",
        "compare_curves": "_play_compare_curves",
    }

    params: ClassVar[dict] = {
        "title": "Quadratic features",
        "function": "x**2 - 4*x + 3",
        "x_min": -1.0,
        "x_max": 5.0,
        "beats": [
            {"kind": "plot"},
            {"kind": "intercepts"},
            {"kind": "turning_point"},
        ],
    }

    # --- beat 1: draw the curve --------------------------------------------

    def _play_plot(self, beat: dict) -> None:
        heading_text = beat.get("heading", "The curve")

        with self.voiceover(
            text=(
                f"Here is the graph of {_spoken(self.function.source)}. "
                '<bookmark mark="draw"/> Watch the shape as it is drawn, '
                "left to right across the domain we care about."
            )
        ) as tracker:
            self._show_heading(heading_text)
            self.play(Write(self.curve_label), run_time=0.5)
            self.wait_until_bookmark("draw")
            self.play(Create(self.curve), run_time=min(2.5, tracker.duration * 0.5))
            self.wait_for_voiceover()


    # --- beat 2: intercepts -------------------------------------------------

    def _play_intercepts(self, beat: dict) -> None:
        heading_text = beat.get("heading", "Intercepts")
        roots = find_roots(self.function, self.window.x_min, self.window.x_max)

        x_dots = VGroup(*[marker_dot(self.axes, self.function, root.x, color=GREEN) for root in roots])
        x_labels = VGroup()
        for root in roots:
            label = coordinate_label(
                self.axes,
                root.x,
                0.0,
                color=GREEN,
                direction=UP,
                obstacles=self._obstacles(),
                curve_points=self._curve_points(),
            )
            self._remember_label(label)
            x_labels.add(label)

        # When a root sits at the origin it is already labelled; a second dot and label on
        # the same point reads as two different features.
        root_at_origin = any(abs(root.x) < 1e-3 for root in roots)
        show_y_intercept = (
            self.window.x_min <= 0 <= self.window.x_max
            and self.function.is_finite_at(0)
            and not root_at_origin
        )
        y_dot = marker_dot(self.axes, self.function, 0.0, color=ORANGE) if show_y_intercept else None
        y_label = (
            coordinate_label(
                self.axes,
                0.0,
                self.function.at(0.0),
                color=ORANGE,
                direction=RIGHT,
                obstacles=self._obstacles(),
                curve_points=self._curve_points(),
            )
            if show_y_intercept
            else None
        )

        roots_phrase = (
            "The curve crosses the x-axis where y is zero."
            if roots
            else "On this domain the curve never crosses the x-axis."
        )
        if show_y_intercept:
            y_phrase = ' <bookmark mark="y"/> It crosses the y-axis where x is zero.'
        elif root_at_origin:
            y_phrase = " That first one is the y-intercept as well, since it sits at the origin."
        else:
            y_phrase = ""

        with self.voiceover(
            text=f'{roots_phrase} <bookmark mark="x"/> There they are.{y_phrase}'
        ):
            self._show_heading(heading_text)
            self.wait_until_bookmark("x")
            if len(x_dots):
                self.play(FadeIn(x_dots, scale=0.5), run_time=0.5)
                self.play(FadeIn(x_labels), run_time=0.5)
            if show_y_intercept:
                self.wait_until_bookmark("y")
                self.play(FadeIn(y_dot, scale=0.5), FadeIn(y_label), run_time=0.6)
            self.wait_for_voiceover()

        self._clear_beat(x_dots, x_labels, y_dot, y_label)

    # --- beat 3: turning point ----------------------------------------------

    def _play_turning_point(self, beat: dict) -> None:
        heading_text = beat.get("heading", "Turning point")
        turning_point = self._turning_point_for(beat)

        if turning_point is None:
            with self.voiceover(
                text="On this domain the curve has no turning point — it is always increasing or always decreasing."
            ):
                self._show_heading(heading_text)
                self.wait_for_voiceover()
            return

        dot = marker_dot(self.axes, self.function, turning_point.x, color=YELLOW)
        # Label outside the curve: below a minimum, above a maximum. Inside the bowl it
        # lands on the curve and, near the x-axis, on the tick numbers as well.
        outward = DOWN if turning_point.kind == "minimum" else UP
        label = coordinate_label(
            self.axes,
            turning_point.x,
            turning_point.y,
            color=YELLOW,
            direction=outward,
            obstacles=self._obstacles(),
            curve_points=self._curve_points(),
        )
        name = as_on_screen_text(
            MathTex(rf"\text{{{turning_point.kind}}}", font_size=26, color=YELLOW)
        ).next_to(label, outward, buff=0.12)

        with self.voiceover(
            text=(
                "The gradient of the curve is zero at a turning point. "
                f'<bookmark mark="mark"/> This one is a {turning_point.kind}, '
                f'<bookmark mark="name"/> where the curve stops {_direction(turning_point.kind)}.'
            )
        ):
            self._show_heading(heading_text)
            self.wait_until_bookmark("mark")
            self.play(FadeIn(dot, scale=0.5), Flash(dot, color=YELLOW, line_length=0.18), run_time=0.7)
            self.play(FadeIn(label), run_time=0.4)
            self.wait_until_bookmark("name")
            self.play(FadeIn(name), run_time=0.4)
            self.wait_for_voiceover()

        self._clear_beat(dot, label, name)

    def _turning_point_for(self, beat: dict):
        """The declared turning point if the beat names one, else the found one."""

        found = find_turning_points(self.function, self.window.x_min, self.window.x_max)
        if beat.get("x") is None:
            return found[0] if found else None

        declared_x = float(beat["x"])
        nearest = min(found, key=lambda tp: abs(tp.x - declared_x), default=None)
        if nearest is not None and abs(nearest.x - declared_x) < 0.05:
            return nearest
        # The Tutor named a point the curve does not actually turn at. Draw what they
        # asked for: a wrong claim should be visible on screen, not silently corrected.
        from visentia.scenes.expressions import Feature

        return Feature("stationary point", declared_x, self.function.at(declared_x))

    # --- beat 4: asymptotes --------------------------------------------------

    def _play_asymptote(self, beat: dict) -> None:
        heading_text = beat.get("heading", "Asymptote")
        lines = asymptote_lines(self.axes, self.function, self.window)
        found = find_vertical_asymptotes(self.function, self.window.x_min, self.window.x_max)

        if not len(lines):
            with self.voiceover(text="This function has no vertical asymptote on the domain shown."):
                self._show_heading(heading_text)
                self.wait_for_voiceover()
            return

        where = ", ".join(f"x equals {_spoken_number(feature.x)}" for feature in found)
        # The asymptote is scanned on a grid, so its x lands near — not on — the true pole.
        # Placed at the top of the line the label would sit under the beat heading, so it
        # goes a little way down the line and dodges anything already there.
        labels = VGroup()
        for feature, line in zip(found, lines):
            label = as_on_screen_text(
                MathTex(rf"x = {_round_str(feature.x)}", font_size=26, color=YELLOW)
            )
            anchor = line.get_top() + DOWN * 0.45
            place_label_clear(
                label,
                anchor,
                preferred=RIGHT,
                obstacles=[*self._obstacles(), *labels],
                curve_points=self._curve_points(),
            )
            labels.add(label)

        with self.voiceover(
            text=(
                f"The function is undefined at {where}. "
                '<bookmark mark="dash"/> The curve runs away from the dashed line without '
                "ever touching it — that line is a vertical asymptote."
            )
        ):
            self._show_heading(heading_text)
            self.wait_until_bookmark("dash")
            self.play(Create(lines), run_time=0.8)
            self.play(FadeIn(labels), run_time=0.5)
            self.wait_for_voiceover()

        self._clear_beat(lines, labels)

    # --- beat 5: transformation ---------------------------------------------

    def _play_transform(self, beat: dict) -> None:
        heading_text = beat.get("heading", "Transformation")
        transformed = parse_function(str(beat["expression"]))
        description = str(beat.get("description", "a transformation of the same curve"))

        # Plotted in the *original* window: the point of a transformation beat is that the
        # curve moves relative to fixed axes. Rescaling to refit it would hide the motion.
        target_curve = plot_curve(self.axes, transformed, self.window, color=ORANGE)
        target_label = self._curve_label(transformed, color=ORANGE)
        # The transformed label replaces the original rather than joining it on screen.
        self._curve_labels = [label for label in self._curve_labels if label is not target_label]
        target_label.move_to(self.curve_label.get_center())

        with self.voiceover(
            text=(
                f"Now apply {description}. "
                '<bookmark mark="morph"/> Watch what happens to every point on the curve '
                "at once — the shape is preserved, only its position changes."
            )
        ):
            self._show_heading(heading_text)
            self.wait_until_bookmark("morph")
            self.play(
                Transform(self.curve, target_curve),
                Transform(self.curve_label, target_label),
                run_time=1.8,
            )
            self.wait_for_voiceover()

        # The curve is now the transformed one; later beats describe what is on screen.
        self.function = transformed

    # --- beat 6: two curves side by side -------------------------------------

    def _play_compare_curves(self, beat: dict) -> None:
        heading_text = beat.get("heading", "Comparing")
        other = parse_function(str(beat["expression"]))
        other_curve = plot_curve(self.axes, other, self.window, color=GREEN)
        other_label = self._curve_label(other, color=GREEN)
        reflow = self._layout_curve_labels(other_curve)

        with self.voiceover(
            text=(
                f"Compare that with {_spoken(other.source)}. "
                '<bookmark mark="second"/> Both curves are drawn on the same axes, '
                "so the difference between them is the difference between the functions."
            )
        ):
            self._show_heading(heading_text)
            self.wait_until_bookmark("second")
            self.play(Create(other_curve), FadeIn(other_label), *reflow, run_time=1.5)
            self.wait_for_voiceover()

        self._clear_beat(other_curve, other_label)


def _direction(kind: str) -> str:
    return {"maximum": "rising and starts to fall", "minimum": "falling and starts to rise"}.get(
        kind, "changing direction"
    )


def _round_str(value: float) -> str:
    """Format a feature's x-value without claiming more precision than the scan has.

    Features found numerically land close to, not on, the true value; printing 1.9937 as
    "2.00" is misleading and printing "1.99" is worse.
    """

    if abs(value - round(value)) < 0.02:
        return str(int(round(value)))
    return f"{value:.2f}"


def _spoken_number(value: float) -> str:
    return _round_str(value).replace("-", "negative ")


def _spoken(source: str) -> str:
    """Read an expression aloud well enough for TTS, without a full verbaliser."""

    replacements = [
        ("**", " to the power "),
        ("^", " to the power "),
        ("*", " times "),
        ("/", " over "),
        ("+", " plus "),
        ("-", " minus "),
        ("sqrt", "the square root of "),
        ("exp", "e to the "),
        ("ln", "the natural log of "),
    ]
    spoken = source
    for old, new in replacements:
        spoken = spoken.replace(old, new)
    return " ".join(spoken.split())
