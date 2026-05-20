"""Layout helpers for Manim curriculum templates — keep visuals inside the frame."""

from __future__ import annotations

from manim import DOWN, UP, Mobject, VGroup

# Default Manim frame runs y ∈ [-4, 4]. Leave margin so nothing clips at the bottom.
BOTTOM_SAFE_Y = -2.85
TOP_CONTENT_Y = 2.0


def fit_in_vertical_band(
    mob: Mobject,
    *,
    top_y: float = TOP_CONTENT_Y,
    bottom_y: float = BOTTOM_SAFE_Y,
) -> Mobject:
    """Scale and shift `mob` so it fits between `top_y` and `bottom_y`."""

    if mob.height > top_y - bottom_y:
        mob.scale_to_fit_height((top_y - bottom_y) * 0.95)
    if mob.get_top()[1] > top_y:
        mob.shift(DOWN * (mob.get_top()[1] - top_y))
    if mob.get_bottom()[1] < bottom_y:
        mob.shift(UP * (bottom_y - mob.get_bottom()[1]))
    return mob


def place_below(anchor: Mobject, content: Mobject, *, buff: float = 0.35) -> Mobject:
    """Position `content` under `anchor` without moving `anchor`, then fit in the safe band."""

    content.next_to(anchor, DOWN, buff=buff)
    return fit_in_vertical_band(content)


def stack_below(anchor: Mobject, *pieces: Mobject, buff: float = 0.3) -> VGroup:
    """Stack `pieces` vertically under `anchor`; fit the stack (anchor stays put)."""

    column = VGroup(*pieces).arrange(DOWN, buff=buff, aligned_edge=LEFT)
    column.next_to(anchor, DOWN, buff=buff)
    fit_in_vertical_band(column)
    return VGroup(anchor, column)
