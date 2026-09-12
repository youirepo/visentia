"""FunctionGraph and CalculusOnCurve — the Stage 6 templates (issue #33).

Two templates over one substrate, so most tests run against both. The render tests are
marked slow; everything else pins the parameter surface and the substrate geometry that
keeps a generated graph spatially correct.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from visentia.classifier import ContentClassifier
from visentia.llm.base import CLASSIFICATION_TEMPERATURE, LLMProvider, Message
from visentia.scenes.expressions import parse_function
from visentia.scenes.graph_substrate import (
    build_axes,
    line_through,
    plot_curve,
    riemann_rectangles,
    window_for,
)
from visentia.templates import TemplateLibrary
from visentia.templates.spec import (
    ParamValidationError,
    validate_calculus_on_curve_params,
    validate_function_graph_params,
    validate_params,
)

STAGE_6_TEMPLATES = ("FunctionGraph", "CalculusOnCurve")


@pytest.mark.parametrize("template_id", STAGE_6_TEMPLATES)
def test_registered_in_library(template_id: str) -> None:
    assert template_id in {spec.id for spec in TemplateLibrary().list_templates()}


@pytest.mark.parametrize("template_id", STAGE_6_TEMPLATES)
def test_fixture_params_validate(template_id: str) -> None:
    spec = TemplateLibrary().get(template_id)
    normalised = validate_params(spec, spec.fixture_params)
    assert normalised["beats"]
    assert normalised["x_min"] < normalised["x_max"]


@pytest.mark.parametrize("template_id", STAGE_6_TEMPLATES)
def test_every_beat_kind_in_the_schema_has_a_handler(template_id: str) -> None:
    """A beat the schema offers but the scene cannot play would fail at render time."""

    spec = TemplateLibrary().get(template_id)
    schema_kinds = set(
        spec.param_schema["properties"]["beats"]["items"]["properties"]["kind"]["enum"]
    )
    assert schema_kinds == set(spec.scene_class.BEATS)


class TestParameterSurface:
    def test_accepts_a_full_function_graph_spec(self) -> None:
        normalised = validate_function_graph_params(
            {
                "title": "Transformations",
                "function": "x^2",
                "x_min": -4,
                "x_max": 4,
                "beats": [
                    {"kind": "plot"},
                    {"kind": "transform", "expression": "(x - 2)**2", "description": "a shift right"},
                    {"kind": "compare_curves", "expression": "2*x**2"},
                ],
            }
        )
        assert [beat["kind"] for beat in normalised["beats"]] == [
            "plot",
            "transform",
            "compare_curves",
        ]

    def test_accepts_a_full_calculus_spec(self) -> None:
        normalised = validate_calculus_on_curve_params(
            {
                "function": "x**3 - 3*x",
                "x_min": -2,
                "x_max": 2,
                "beats": [
                    {"kind": "secant_to_tangent", "x": 1, "steps": [1, 0.5, 0.25]},
                    {"kind": "gradient_function"},
                    {"kind": "riemann_sum", "lower": 0, "upper": 2, "counts": [4, 16]},
                ],
            }
        )
        assert normalised["beats"][0]["steps"] == [1.0, 0.5, 0.25]
        assert normalised["beats"][2]["counts"] == [4, 16]

    @pytest.mark.parametrize(
        ("params", "reason"),
        [
            ({"function": "__import__('os')", "x_min": 0, "x_max": 1, "beats": [{"kind": "plot"}]},
             "unsafe expression"),
            ({"function": "x", "x_min": 2, "x_max": 1, "beats": [{"kind": "plot"}]},
             "inverted domain"),
            ({"function": "x", "x_min": 0, "x_max": 1, "beats": []}, "no beats"),
            ({"function": "x", "x_min": 0, "x_max": 1, "beats": [{"kind": "nope"}]},
             "unknown beat kind"),
            ({"function": "x", "x_min": 0, "x_max": 1, "beats": [{"kind": "transform"}]},
             "transform without an expression"),
            ({"function": "x", "x_min": -500, "x_max": 500, "beats": [{"kind": "plot"}]},
             "domain too wide to be legible"),
            ({"function": "x", "x_min": 0, "x_max": 1, "y_min": 5, "y_max": 1,
              "beats": [{"kind": "plot"}]}, "inverted y range"),
        ],
    )
    def test_rejects_bad_function_graph_params(self, params: dict, reason: str) -> None:
        with pytest.raises(ParamValidationError):
            validate_function_graph_params(params)

    @pytest.mark.parametrize(
        ("params", "reason"),
        [
            ({"function": "x**2", "x_min": 0, "x_max": 2, "beats": [{"kind": "tangent_at", "x": 9}]},
             "point outside the plotted domain"),
            ({"function": "x**2", "x_min": 0, "x_max": 4,
              "beats": [{"kind": "riemann_sum", "lower": 3, "upper": 1}]},
             "region bounds inverted"),
            ({"function": "x**2", "x_min": 0, "x_max": 4,
              "beats": [{"kind": "riemann_sum", "lower": 1, "upper": 3, "counts": [0]}]},
             "zero rectangles"),
            ({"function": "x**2", "x_min": 0, "x_max": 4, "beats": [{"kind": "tangent_at"}]},
             "tangent without an x"),
        ],
    )
    def test_rejects_bad_calculus_params(self, params: dict, reason: str) -> None:
        with pytest.raises(ParamValidationError):
            validate_calculus_on_curve_params(params)

    def test_beat_count_is_capped(self) -> None:
        with pytest.raises(ParamValidationError):
            validate_function_graph_params(
                {
                    "function": "x",
                    "x_min": 0,
                    "x_max": 1,
                    "beats": [{"kind": "plot"}] * 20,
                }
            )


class TestSubstrateGeometry:
    """The drawing rules that keep a generated graph from being confidently wrong."""

    def test_a_rational_curve_is_split_at_its_asymptote(self) -> None:
        """One continuous path would draw a stroke joining the two branches."""

        function = parse_function("1/(x - 2)")
        window = window_for(function, -2, 6)
        curve = plot_curve(build_axes(window), function, window)
        assert len(curve) >= 2

    def test_a_continuous_curve_is_one_segment(self) -> None:
        function = parse_function("x**2")
        window = window_for(function, -3, 3)
        curve = plot_curve(build_axes(window), function, window)
        assert len(curve) == 1

    def test_the_window_is_not_flattened_by_a_pole(self) -> None:
        function = parse_function("1/(x - 2)")
        window = window_for(function, -2, 6)
        assert window.y_max - window.y_min < 100

    def test_explicit_y_bounds_are_honoured(self) -> None:
        window = window_for(parse_function("x**2"), -3, 3, y_min=-1, y_max=10)
        assert (window.y_min, window.y_max) == (-1.0, 10.0)

    def test_a_steep_tangent_is_clipped_to_the_window(self) -> None:
        """An unclipped steep line runs off the frame and over the header text."""

        function = parse_function("x**2")
        window = window_for(function, -3, 3)
        axes = build_axes(window)
        line = line_through(axes, window, x0=2.5, y0=6.25, gradient=50.0)

        top = axes.coords_to_point(0, window.y_max)[1]
        bottom = axes.coords_to_point(0, window.y_min)[1]
        assert line.get_top()[1] <= top + 1e-6
        assert line.get_bottom()[1] >= bottom - 1e-6

    def test_riemann_rectangles_stay_inside_the_window(self) -> None:
        function = parse_function("1/x")
        window = window_for(function, 0.1, 4)
        axes = build_axes(window)
        rectangles = riemann_rectangles(
            axes, function, window, lower=0.1, upper=2, count=8
        )

        top = axes.coords_to_point(0, window.y_max)[1]
        for rectangle in rectangles:
            assert rectangle.get_top()[1] <= top + 1e-6

    def test_riemann_rectangle_count_is_honoured(self) -> None:
        function = parse_function("x**2")
        window = window_for(function, 0, 2)
        rectangles = riemann_rectangles(
            build_axes(window), function, window, lower=0, upper=2, count=12
        )
        assert len(rectangles) == 12


class _Stage6Provider(LLMProvider):
    name = "fake"
    model = "fake-model"

    def __init__(self, template_id: str) -> None:
        self.template_id = template_id

    def complete(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        temperature: float = CLASSIFICATION_TEMPERATURE,
        response_schema: dict | None = None,
    ) -> str:
        del system, temperature, response_schema, messages
        return json.dumps(
            {
                "math_content_type": "Derivation",
                "suggested_mode": "Deep",
                "suggested_template_id": self.template_id,
            }
        )


@pytest.mark.parametrize("template_id", STAGE_6_TEMPLATES)
def test_classifier_can_route_to_each_stage_6_template(template_id: str) -> None:
    classifier = ContentClassifier(provider=_Stage6Provider(template_id))
    assert classifier.classify("Sketch y = x^2 - 4x + 3").suggested_template_id == template_id


@pytest.mark.slow
@pytest.mark.parametrize("template_id", STAGE_6_TEMPLATES)
def test_fixture_renders(template_id: str, tmp_path: Path) -> None:
    library = TemplateLibrary()
    mp4 = library.render(template_id, library.get(template_id).fixture_params, tmp_path)
    assert mp4.exists()
    assert mp4.stat().st_size > 0


class TestLabelPlacement:
    """Labels are the most common way one of these graphs becomes unreadable."""

    def test_a_label_moves_off_an_obstacle(self) -> None:
        from manim import MathTex

        from visentia.scenes.graph_substrate import _collides, place_label_clear

        obstacle = MathTex("1.0").move_to([0.0, -0.4, 0.0])
        label = MathTex("(1, 0)")
        place_label_clear(label, np.array([0.0, 0.0, 0.0]), preferred=np.array([0.0, -1.0, 0.0]),
                          obstacles=[obstacle])

        assert not _collides(label, [obstacle])

    def test_a_label_moves_off_the_curve(self) -> None:
        from manim import MathTex

        from visentia.scenes.graph_substrate import _collides, place_label_clear

        curve_points = np.array([[x, 0.0, 0.0] for x in np.linspace(-2, 2, 50)])
        label = MathTex("(1, 0)")
        place_label_clear(label, np.array([0.0, 0.0, 0.0]), curve_points=curve_points)

        assert not _collides(label, (), curve_points)

    def test_a_label_is_kept_inside_the_frame(self) -> None:
        from manim import MathTex

        from visentia.scenes.graph_substrate import place_label_clear

        label = MathTex("(1, 0)")
        place_label_clear(label, np.array([7.0, 3.8, 0.0]))

        assert label.get_right()[0] <= 14.222 / 2
        assert label.get_top()[1] <= 4.0
