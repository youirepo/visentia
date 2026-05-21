"""Geometry helpers for triangle side labels."""

from __future__ import annotations

import numpy as np

from visentia.scenes.triangle_3_side import (
    _edge_label_position,
    _triangle_vertices,
)


def test_edge_labels_sit_outside_triangle() -> None:
    verts = _triangle_vertices(3, 4, 5)
    v0, v1, v2 = verts
    centroid = np.mean(verts, axis=0)

    for start, end, other in ((v0, v1, v2), (v1, v2, v0), (v0, v2, v1)):
        pos = _edge_label_position(start, end, other)
        mid = (np.array(start) + np.array(end)) / 2
        outward = pos - mid
        assert float(np.dot(outward, centroid - mid)) < 0
