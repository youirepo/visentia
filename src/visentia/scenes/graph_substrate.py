"""Shared axes-and-curve substrate for the Stage 6 graph templates (issue #33).

`FunctionGraph` and `CalculusOnCurve` are two templates over one visual vocabulary: a
pair of axes, a curve on them, and things attached to points of that curve. Everything
they share lives here, so the vocabulary is written — and made spatially correct — once.

Two failure modes are handled here rather than in each scene, because both are ways a
generated graph goes confidently wrong:

- **The line through the asymptote.** Plotting a rational function as one continuous path
  draws a near-vertical stroke joining the two branches, which reads as part of the curve.
  Curves are therefore built as separate segments, split wherever the function leaves the
  window or goes undefined.
- **The pole-flattened window.** Auto-scaling to a curve with a vertical asymptote sets
  the y-range to the largest sampled value, squashing everything else onto the x-axis. The
  window comes from trimmed percentiles instead (see `expressions.suggested_y_range`).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from manim import (
    BLUE,
    Create,
    FadeIn,
    FadeOut,
    Transform,
    DOWN,
    GREY,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    YELLOW,
    Axes,
    DashedLine,
    Dot,
    Line,
    MathTex,
    Rectangle,
    Text,
    VGroup,
    VMobject,
)

from manim_voiceover import VoiceoverScene

from visentia.scenes.expressions import (
    Function,
    find_vertical_asymptotes,
    parse_function,
    suggested_y_range,
)
from visentia.scenes.layout import as_on_screen_text
from visentia.voiceover import VoiceoverSynthesizer

AXES_TOP_Y = 2.05
"""Top of the plotting band — below the header and the beat heading."""

AXES_BOTTOM_Y = -2.75
"""Bottom of the plotting band — above the caption strip (`layout.BOTTOM_SAFE_Y`)."""

AXES_WIDTH = 9.8
AXES_HEIGHT = AXES_TOP_Y - AXES_BOTTOM_Y

CURVE_SAMPLES = 600
"""Points per curve. Enough for a smooth Stage 6 curve without a heavy scene graph."""


@dataclass(frozen=True)
class GraphWindow:
    """The plotted region, in graph coordinates."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float

    def contains_y(self, y: float) -> bool:
        return self.y_min <= y <= self.y_max

    @property
    def x_step(self) -> float:
        return _nice_step(self.x_max - self.x_min)

    @property
    def y_step(self) -> float:
        return _nice_step(self.y_max - self.y_min)


def window_for(
    function: Function,
    x_min: float,
    x_max: float,
    *,
    y_min: float | None = None,
    y_max: float | None = None,
) -> GraphWindow:
    """Choose a window for `function`, honouring any explicitly requested y-bounds."""

    if y_min is None or y_max is None:
        suggested_low, suggested_high = suggested_y_range(function, x_min, x_max)
        y_min = suggested_low if y_min is None else y_min
        y_max = suggested_high if y_max is None else y_max

    if y_max - y_min < 1e-6:
        y_min, y_max = y_min - 1.0, y_max + 1.0

    return GraphWindow(float(x_min), float(x_max), float(y_min), float(y_max))


def build_axes(window: GraphWindow) -> Axes:
    """Axes sized to the plotting band and centred in it."""

    axes = Axes(
        x_range=[window.x_min, window.x_max, window.x_step],
        y_range=[window.y_min, window.y_max, window.y_step],
        x_length=AXES_WIDTH,
        y_length=AXES_HEIGHT,
        axis_config={
            "include_numbers": True,
            "font_size": 20,
            "stroke_width": 2,
            "color": GREY,
            "tip_width": 0.16,
            "tip_height": 0.16,
        },
        tips=True,
    )
    axes.move_to([0.0, (AXES_TOP_Y + AXES_BOTTOM_Y) / 2.0, 0.0])
    return axes


def plot_curve(
    axes: Axes,
    function: Function,
    window: GraphWindow,
    *,
    color=BLUE,
    stroke_width: float = 3.5,
    x_min: float | None = None,
    x_max: float | None = None,
) -> VGroup:
    """The curve as one or more segments, broken where it leaves the window.

    Returns a `VGroup` rather than a single path: a rational function plotted as one path
    would join its branches with a stroke across the asymptote.
    """

    start = window.x_min if x_min is None else float(x_min)
    end = window.x_max if x_max is None else float(x_max)

    xs = np.linspace(start, end, CURVE_SAMPLES)
    with np.errstate(all="ignore"):
        ys = np.asarray(function(xs), dtype=float)
    if ys.shape != xs.shape:
        ys = np.broadcast_to(ys, xs.shape).astype(float)

    segments = VGroup()
    current: list[np.ndarray] = []

    for x, y in zip(xs, ys):
        if not np.isfinite(y) or not window.contains_y(float(y)):
            if len(current) > 1:
                segments.add(_path(current, color, stroke_width))
            current = []
            continue
        current.append(axes.coords_to_point(float(x), float(y)))

    if len(current) > 1:
        segments.add(_path(current, color, stroke_width))

    return segments


def _path(points: list[np.ndarray], color, stroke_width: float) -> VMobject:
    path = VMobject(color=color, stroke_width=stroke_width)
    path.set_points_smoothly(points)
    return path


def asymptote_lines(axes: Axes, function: Function, window: GraphWindow, *, color=GREY) -> VGroup:
    """Dashed verticals at each pole in the window."""

    lines = VGroup()
    for feature in find_vertical_asymptotes(function, window.x_min, window.x_max):
        lines.add(
            DashedLine(
                axes.coords_to_point(feature.x, window.y_min),
                axes.coords_to_point(feature.x, window.y_max),
                dash_length=0.12,
                stroke_width=2,
                color=color,
            )
        )
    return lines


def point_on(axes: Axes, function: Function, x: float) -> np.ndarray:
    return axes.coords_to_point(float(x), function.at(float(x)))


def marker_dot(axes: Axes, function: Function, x: float, *, color=YELLOW) -> Dot:
    return Dot(point_on(axes, function, x), color=color, radius=0.075)


def coordinate_label(
    axes: Axes,
    x: float,
    y: float,
    *,
    color=YELLOW,
    direction=UP,
    decimals: int = 2,
    obstacles=(),
    curve_points=None,
) -> MathTex:
    """A `(x, y)` label, placed where it does not sit on top of something else.

    Labelling an x-intercept is the case that goes wrong by default: `(1, 0)` placed below
    the point lands exactly on the axis tick reading `1.0`. `obstacles` (the axis numbers
    and any labels already placed) and `curve_points` steer it somewhere legible.
    """

    label = as_on_screen_text(
        MathTex(rf"({_fmt(x, decimals)},\; {_fmt(y, decimals)})", font_size=26, color=color)
    )
    return place_label_clear(
        label,
        axes.coords_to_point(float(x), float(y)),
        preferred=direction,
        obstacles=obstacles,
        curve_points=curve_points,
    )


_LABEL_DIRECTIONS = (UP, DOWN, RIGHT, LEFT)


def place_label_clear(
    label,
    anchor,
    *,
    preferred=UP,
    obstacles=(),
    curve_points=None,
    buff: float = 0.18,
):
    """Place `label` next to `anchor`, trying directions until nothing overlaps."""

    directions = [preferred] + [d for d in _LABEL_DIRECTIONS if not np.array_equal(d, preferred)]

    for extra in (0.0, 0.28, 0.6):
        for direction in directions:
            label.next_to(anchor, direction, buff=buff + extra)
            _keep_in_frame(label)
            if not _collides(label, obstacles, curve_points):
                return label

    label.next_to(anchor, preferred, buff=buff)
    return _keep_in_frame(label)


def _collides(label, obstacles=(), curve_points=None) -> bool:
    left, right = label.get_left()[0], label.get_right()[0]
    bottom, top = label.get_bottom()[1], label.get_top()[1]
    pad = 0.06

    for obstacle in obstacles:
        if obstacle is None or obstacle is label:
            continue
        if (
            obstacle.get_left()[0] - pad < right
            and obstacle.get_right()[0] + pad > left
            and obstacle.get_bottom()[1] - pad < top
            and obstacle.get_top()[1] + pad > bottom
        ):
            return True

    if curve_points is not None and len(curve_points):
        points = np.asarray(curve_points)
        inside = (
            (points[:, 0] > left - pad)
            & (points[:, 0] < right + pad)
            & (points[:, 1] > bottom - pad)
            & (points[:, 1] < top + pad)
        )
        if bool(np.any(inside)):
            return True

    return False


def line_through(
    axes: Axes,
    window: GraphWindow,
    *,
    x0: float,
    y0: float,
    gradient: float,
    color=YELLOW,
    stroke_width: float = 3.0,
    half_width: float | None = None,
) -> Line:
    """A straight line of given gradient through `(x0, y0)`, clipped to the window.

    Used for both tangents and secants. Clipping matters: an unclipped steep tangent runs
    off the frame and over the header text.
    """

    span = (window.x_max - window.x_min) / 4.0 if half_width is None else float(half_width)
    left_x = max(window.x_min, x0 - span)
    right_x = min(window.x_max, x0 + span)

    def clamp(x: float) -> tuple[float, float]:
        y = y0 + gradient * (x - x0)
        if y > window.y_max and gradient != 0:
            x = x0 + (window.y_max - y0) / gradient
            y = window.y_max
        elif y < window.y_min and gradient != 0:
            x = x0 + (window.y_min - y0) / gradient
            y = window.y_min
        return x, y

    start = clamp(left_x)
    end = clamp(right_x)
    return Line(
        axes.coords_to_point(*start),
        axes.coords_to_point(*end),
        color=color,
        stroke_width=stroke_width,
    )


def riemann_rectangles(
    axes: Axes,
    function: Function,
    window: GraphWindow,
    *,
    lower: float,
    upper: float,
    count: int,
    color=BLUE,
    opacity: float = 0.45,
) -> VGroup:
    """`count` rectangles under the curve between `lower` and `upper` (midpoint rule).

    Built directly rather than via `axes.get_riemann_rectangles` so heights can be clamped
    to the window — a rectangle taller than the frame is the usual way this animation
    breaks.
    """

    rectangles = VGroup()
    width = (float(upper) - float(lower)) / int(count)
    baseline = min(max(0.0, window.y_min), window.y_max)

    for index in range(int(count)):
        left = float(lower) + index * width
        height_value = function.at(left + width / 2.0)
        if not np.isfinite(height_value):
            continue
        top = float(np.clip(height_value, window.y_min, window.y_max))

        corner = axes.coords_to_point(left, baseline)
        opposite = axes.coords_to_point(left + width, top)
        rectangle = Rectangle(
            width=abs(opposite[0] - corner[0]),
            height=abs(opposite[1] - corner[1]),
            stroke_width=1.2,
            stroke_color=WHITE,
            fill_color=color,
            fill_opacity=opacity,
        )
        rectangle.move_to((corner + opposite) / 2.0)
        rectangles.add(rectangle)

    return rectangles


def area_under_curve(
    axes: Axes,
    function: Function,
    window: GraphWindow,
    *,
    lower: float,
    upper: float,
    color=BLUE,
    opacity: float = 0.45,
) -> VMobject:
    """The shaded region between the curve and the x-axis over `[lower, upper]`."""

    xs = np.linspace(float(lower), float(upper), 200)
    baseline = min(max(0.0, window.y_min), window.y_max)

    top_points = []
    for x in xs:
        y = function.at(float(x))
        if not np.isfinite(y):
            continue
        top_points.append(axes.coords_to_point(float(x), float(np.clip(y, window.y_min, window.y_max))))

    if len(top_points) < 2:
        return VMobject()

    region = VMobject(fill_color=color, fill_opacity=opacity, stroke_width=0)
    region.set_points_as_corners(
        [axes.coords_to_point(float(xs[0]), baseline)]
        + top_points
        + [axes.coords_to_point(float(xs[-1]), baseline), axes.coords_to_point(float(xs[0]), baseline)]
    )
    return region


def header(title: str, subtitle: str) -> VGroup:
    """The two-line header used by both Stage 6 graph templates."""

    return as_on_screen_text(
        VGroup(
            Text(title, font_size=34),
            Text(subtitle, font_size=22, color=BLUE),
        ).arrange(DOWN, buff=0.2)
    ).to_edge(UP, buff=0.3)


def beat_heading(text: str, anchor: VGroup) -> Text:
    heading = as_on_screen_text(Text(text, font_size=24, color=YELLOW))
    heading.next_to(anchor, DOWN, buff=0.18)
    return heading


def _keep_in_frame(mobject, *, margin: float = 0.25):
    """Shift a label back inside the frame if it was placed over an edge."""

    half_width = 14.222 / 2 - margin
    half_height = 8.0 / 2 - margin
    if mobject.get_right()[0] > half_width:
        mobject.shift(LEFT * (mobject.get_right()[0] - half_width))
    if mobject.get_left()[0] < -half_width:
        mobject.shift(RIGHT * (-half_width - mobject.get_left()[0]))
    if mobject.get_top()[1] > half_height:
        mobject.shift(DOWN * (mobject.get_top()[1] - half_height))
    if mobject.get_bottom()[1] < -half_height:
        mobject.shift(UP * (-half_height - mobject.get_bottom()[1]))
    return mobject


def _fmt(value: float, decimals: int = 2) -> str:
    """Format a coordinate: whole numbers without a decimal point."""

    number = float(value)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.{decimals}f}".rstrip("0").rstrip(".")


def _nice_step(span: float) -> float:
    """A tick step that yields roughly 6-10 labelled ticks across `span`."""

    if span <= 0:
        return 1.0
    raw = span / 8.0
    magnitude = 10.0 ** np.floor(np.log10(raw))
    for multiple in (1.0, 2.0, 2.5, 5.0, 10.0):
        step = multiple * magnitude
        if step >= raw:
            return float(step)
    return float(10.0 * magnitude)


# ---------------------------------------------------------------------------
# The beat scene
# ---------------------------------------------------------------------------


class GraphTemplateScene(VoiceoverScene):
    """Base for the Stage 6 graph templates: axes and curve persist, beats play on them.

    Subclasses declare `title` and `BEATS` (a beat `kind` to method map) and implement one
    method per beat. `params["beats"]` is played in order: the list *is* the animation
    sequence.

    Unlike the junior templates, the axes and the base curve are built once and stay on
    screen for the whole video. Every functions-and-calculus idiom is a statement *about
    the same curve*, and rebuilding it per beat would throw away the continuity that makes
    the sequence read as one explanation.

    ## Narration timing

    Beat narration carries `<bookmark mark="..."/>` cues and each visual step waits for its
    mark via `wait_until_bookmark`, so the tangent appears on the word "tangent" rather
    than at a guessed fraction of the clip. This depends on real word boundaries reaching
    the tracker (issue #35); with the linear-interpolation fallback the marks still land in
    roughly the right order, just imprecisely.
    """

    title: str = "Functions"
    BEATS: dict[str, str] = {}

    def construct(self) -> None:
        self.set_speech_service(
            VoiceoverSynthesizer.create_service(),
            create_subcaption=False,
        )
        params = self.params  # type: ignore[attr-defined]

        self.function = parse_function(params["function"])
        self.window = window_for(
            self.function,
            params["x_min"],
            params["x_max"],
            y_min=params.get("y_min"),
            y_max=params.get("y_max"),
        )
        self.axes = build_axes(self.window)
        self.header_mob = header(self.title, str(params.get("title", "")))

        self.play(FadeIn(self.header_mob), run_time=0.5)
        self.play(Create(self.axes), run_time=0.8)

        self.curve = plot_curve(self.axes, self.function, self.window)
        self._placed_labels: list = []
        self._curve_labels: list = []
        self.curve_label = self._curve_label(self.function)
        self._layout_curve_labels()

        for beat in params["beats"]:
            handler = getattr(self, self.BEATS[beat["kind"]])
            handler(beat)

        self.play(FadeOut(*self.mobjects))
        self.wait(0.3)

    # --- shared beat scaffolding -------------------------------------------

    LABEL_CORNERS = (
        [AXES_WIDTH / 2 - 1.0, AXES_TOP_Y - 0.2, 0.0],
        [-AXES_WIDTH / 2 + 1.0, AXES_TOP_Y - 0.2, 0.0],
        [AXES_WIDTH / 2 - 1.0, AXES_BOTTOM_Y + 0.35, 0.0],
        [-AXES_WIDTH / 2 + 1.0, AXES_BOTTOM_Y + 0.35, 0.0],
    )

    def _curve_label(self, function: Function, *, color=BLUE) -> MathTex:
        """Register a `y = f(x)` label. Position comes from `_layout_curve_labels`."""

        label = as_on_screen_text(MathTex(rf"y = {function.latex}", font_size=30, color=color))
        self._curve_labels = [*getattr(self, "_curve_labels", []), label]
        return label

    def _layout_curve_labels(self, *extra_curves) -> list:
        """Assign every curve label a corner clear of the curves and of each other.

        Laid out together rather than one at a time: placing a second label against the
        first label's *old* position is how both ended up in the same corner. Returns
        animations for labels already on screen that need to move, so the shuffle can play
        alongside whatever prompted it.
        """

        curve_points = self._curve_points(*extra_curves)
        axis_obstacles = self._obstacles()
        taken: list = []
        animations: list = []

        for label in getattr(self, "_curve_labels", []):
            target = None
            for corner in self.LABEL_CORNERS:
                probe = label.copy()
                probe.move_to(corner)
                _keep_in_frame(probe)
                if not _collides(probe, [*axis_obstacles, *taken], curve_points):
                    target = probe
                    break
            if target is None:
                target = label.copy()
                target.move_to(self.LABEL_CORNERS[0])
                _keep_in_frame(target)

            taken.append(target)
            if np.linalg.norm(target.get_center() - label.get_center()) < 1e-3:
                continue
            if label in self.mobjects:
                animations.append(label.animate.move_to(target.get_center()))
            else:
                label.move_to(target.get_center())

        return animations

    def _show_heading(self, text: str) -> None:
        """Put `text` in the beat-heading slot, replacing whatever is there.

        Beats own their own mobjects but share one heading slot; letting each beat fade in
        its own heading stacks them on the same line, which is how the first render of this
        template ended up reading "TheIntercuepts".
        """

        heading = beat_heading(text, self.header_mob)
        existing = getattr(self, "_heading_mob", None)
        if existing is not None and existing in self.mobjects:
            self.play(Transform(existing, heading), run_time=0.4)
        else:
            self._heading_mob = heading
            self.play(FadeIn(heading), run_time=0.4)

    def _obstacles(self) -> list:
        """Mobjects a new label should not be placed on top of."""

        obstacles: list = []
        for axis in (self.axes.get_x_axis(), self.axes.get_y_axis()):
            numbers = getattr(axis, "numbers", None)
            if numbers is not None:
                obstacles.extend(numbers)
        obstacles.extend(getattr(self, "_placed_labels", []))
        return obstacles

    def _remember_label(self, label) -> None:
        self._placed_labels = [*getattr(self, "_placed_labels", []), label]

    def _curve_points(self, *extra):
        """Points of the plotted curve, plus any additional curves passed in."""

        sources = [self.curve, *[curve for curve in extra if curve is not None]]
        points = [
            segment.points
            for source in sources
            for segment in source
            if len(segment.points)
        ]
        return np.concatenate(points) if points else None

    def _clear_beat(self, *mobjects) -> None:
        """Fade out everything a beat added, leaving axes and curve in place."""

        present = [mobject for mobject in mobjects if mobject in self.mobjects]
        if present:
            self.play(FadeOut(*present), run_time=0.4)
        # Labels placed by this beat are gone, so they no longer constrain the next one.
        self._placed_labels = []
