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
