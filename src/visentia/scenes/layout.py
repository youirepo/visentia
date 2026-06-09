"""Layout helpers for Manim curriculum templates — keep visuals inside the frame."""

from __future__ import annotations

from manim import DOWN, UP, Mobject, VGroup

BOTTOM_SAFE_Y = -2.85
TOP_CONTENT_Y = 2.0
TEXT_Z_INDEX = 2
SHAPE_Z_INDEX = 0


def as_on_screen_text(mob: Mobject) -> Mobject:
    """Keep labels above filled shapes (triangles) in the render order."""

    mob.set_z_index(TEXT_Z_INDEX)
    return mob


def as_diagram_shape(mob: Mobject) -> Mobject:
    mob.set_z_index(SHAPE_Z_INDEX)
    return mob


def fit_in_vertical_band(
    mob: Mobject,
    *,
    top_y: float = TOP_CONTENT_Y,
    bottom_y: float = BOTTOM_SAFE_Y,
) -> Mobject:
    if mob.height > top_y - bottom_y:
        mob.scale_to_fit_height((top_y - bottom_y) * 0.95)
    if mob.get_top()[1] > top_y:
        mob.shift(DOWN * (mob.get_top()[1] - top_y))
    if mob.get_bottom()[1] < bottom_y:
        mob.shift(UP * (bottom_y - mob.get_bottom()[1]))
    return mob


def scale_to_diagram_band(
    mob: Mobject,
    *,
    top_y: float,
    bottom_y: float,
    fill: float = 0.88,
    max_width: float | None = None,
    center_x: float | None = None,
) -> Mobject:
    """Scale a diagram up or down to use most of the vertical band between text strips.

    Pass ``max_width`` to keep wide diagrams (e.g. a base-(a+b) parallelogram) from
    running off-frame, and ``center_x`` to recenter horizontally rather than keeping
    the mobject's current x (which may be off-centre after a tessellation build).
    """

    band = top_y - bottom_y
    if band <= 0:
        return mob
    mob.scale_to_fit_height(band * fill)
    if max_width is not None and mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    cx = center_x if center_x is not None else mob.get_center()[0]
    mob.move_to([cx, (top_y + bottom_y) / 2, 0.0])
    if mob.get_top()[1] > top_y:
        mob.shift(DOWN * (mob.get_top()[1] - top_y))
    if mob.get_bottom()[1] < bottom_y:
        mob.shift(UP * (bottom_y - mob.get_bottom()[1]))
    return mob


def place_in_band_below(
    anchor: Mobject,
    content: Mobject,
    *,
    buff: float = 0.4,
    bottom_y: float = BOTTOM_SAFE_Y,
) -> Mobject:
    """Place `content` in the strip below `anchor`, never overlapping upward into it."""

    top_y = anchor.get_bottom()[1] - buff
    content.move_to([(content.get_center()[0]), (top_y + bottom_y) / 2, 0])
    if content.height > top_y - bottom_y:
        content.scale_to_fit_height((top_y - bottom_y) * 0.92)
    if content.get_top()[1] > top_y:
        content.shift(DOWN * (content.get_top()[1] - top_y))
    if content.get_bottom()[1] < bottom_y:
        content.shift(UP * (bottom_y - content.get_bottom()[1]))
    return content
