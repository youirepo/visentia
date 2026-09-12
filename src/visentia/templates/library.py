"""TemplateLibrary: registry of curriculum Manim templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from manim import tempconfig

from visentia.scenes.calculus_on_curve import CalculusOnCurveScene
from visentia.scenes.function_graph import FunctionGraphScene
from visentia.scenes.triangle_3_side import Triangle3SideScene
from visentia.scenes.area_transform import AreaTransformScene
from visentia.scenes.worked_example import WorkedExampleScene
from visentia.templates.spec import TemplateSpec, validate_params

TRIANGLE_3_SIDE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "side_a": {"type": "NUMBER", "description": "First side length"},
        "side_b": {"type": "NUMBER", "description": "Second side length"},
        "side_c": {"type": "NUMBER", "description": "Third side length"},
        "include_sweep": {
            "type": "BOOLEAN",
            "description": "Include a parameter sweep animation (set false for fast CI renders)",
        },
    },
    "required": ["side_a", "side_b", "side_c"],
}

_TRIANGLE_3_SIDE = TemplateSpec(
    id="Triangle3Side",
    description=(
        "Converse of Pythagoras: classify a triangle as acute, right, or obtuse from three "
        "side lengths (no drawing to scale). Compare c² with a²+b² where c is the longest side."
    ),
    param_schema=TRIANGLE_3_SIDE_SCHEMA,
    scene_class=Triangle3SideScene,
    fixture_params={"side_a": 3, "side_b": 4, "side_c": 5, "include_sweep": False},
)

WORKED_EXAMPLE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "item_label": {"type": "STRING", "description": "Short label for the scenario (e.g. Apples)"},
        "rate_numerator": {"type": "NUMBER", "description": "Price or rate numerator (e.g. 5 dollars)"},
        "currency_symbol": {"type": "STRING", "description": "LaTeX currency symbol, default $"},
        "rate_denominator": {"type": "NUMBER", "description": "Rate denominator quantity (e.g. 100)"},
        "rate_unit": {"type": "STRING", "description": "Unit in the rate denominator (e.g. g)"},
        "quantity": {"type": "NUMBER", "description": "Total quantity to price (e.g. 4.5)"},
        "quantity_unit": {"type": "STRING", "description": "Unit of the quantity (e.g. kg)"},
        "unit_conversion_factor": {
            "type": "NUMBER",
            "description": "Multiply quantity by this to express it in rate_unit (e.g. 1000 for kg→g)",
        },
    },
    "required": [
        "rate_numerator",
        "rate_denominator",
        "rate_unit",
        "quantity",
        "quantity_unit",
        "unit_conversion_factor",
    ],
}

_WORKED_EXAMPLE = TemplateSpec(
    id="WorkedExample",
    description=(
        "Procedure: total cost from a rate (price per unit quantity) when the quantity needs a "
        "unit conversion first. Shows conversion, fraction setup, animated unit cancellation, "
        "and the final total. Example: dollars per 100g for a mass in kg."
    ),
    param_schema=WORKED_EXAMPLE_SCHEMA,
    scene_class=WorkedExampleScene,
    fixture_params={
        "item_label": "Apples",
        "rate_numerator": 5,
        "currency_symbol": r"\$",
        "rate_denominator": 100,
        "rate_unit": "g",
        "quantity": 4.5,
        "quantity_unit": "kg",
        "unit_conversion_factor": 1000,
    },
)

AREA_TRANSFORM_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "rhombus_d1": {"type": "NUMBER", "description": "Rhombus horizontal diagonal length"},
        "rhombus_d2": {"type": "NUMBER", "description": "Rhombus vertical diagonal length"},
        "trapezium_a": {"type": "NUMBER", "description": "Shorter parallel side of trapezium"},
        "trapezium_b": {"type": "NUMBER", "description": "Longer parallel side of trapezium"},
        "trapezium_h": {"type": "NUMBER", "description": "Perpendicular height of trapezium"},
        "include_trapezium": {
            "type": "BOOLEAN",
            "description": "Include trapezium scene (set false for fast CI renders)",
        },
    },
    "required": ["rhombus_d1", "rhombus_d2", "trapezium_a", "trapezium_b", "trapezium_h"],
}

_AREA_TRANSFORM = TemplateSpec(
    id="AreaTransform",
    description=(
        "Derivation: area of a rhombus from diagonals (half of d1×d2 rectangle) and area of a "
        "trapezium by duplicating, rotating 180°, and forming a parallelogram with base (a+b)."
    ),
    param_schema=AREA_TRANSFORM_SCHEMA,
    scene_class=AreaTransformScene,
    fixture_params={
        "rhombus_d1": 4,
        "rhombus_d2": 2.5,
        "trapezium_a": 2,
        "trapezium_b": 4,
        "trapezium_h": 2,
        "include_trapezium": False,
    },
)

# --- Stage 6: functions and calculus (issue #33) ----------------------------
#
# Both Stage 6 templates take one function, one domain, and a list of beats. The beat list
# is the animation sequence. Keeping the two schemas structurally
# identical means the ParamFiller learns one shape, not two.


def _graph_schema(beat_kinds: list[str], beat_description: str) -> dict[str, Any]:
    return {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING", "description": "Short subtitle naming the concept"},
            "function": {
                "type": "STRING",
                "description": (
                    "The function of x, as an expression: '+ - * / ^', numbers, 'x', the "
                    "constants pi and e, and the functions sin cos tan asin acos atan sinh "
                    "cosh tanh exp ln log log10 sqrt abs. Examples: 'x**2 - 4*x + 3', "
                    "'x*exp(-x)', '(x^2 - 1)/(x - 2)'."
                ),
            },
            "x_min": {
                "type": "NUMBER",
                "description": (
                    "Left end of the plotted domain. Choose a domain just wide enough to show "
                    "the features being discussed: a cubic or quartic over a wide domain reaches "
                    "values so large that its turning points are squashed flat."
                ),
            },
            "x_max": {"type": "NUMBER", "description": "Right end of the plotted domain"},
            "y_min": {
                "type": "NUMBER",
                "description": "Optional bottom of the plotted range; omit to frame the curve automatically",
            },
            "y_max": {
                "type": "NUMBER",
                "description": "Optional top of the plotted range; omit to frame the curve automatically",
            },
            "beats": {
                "type": "ARRAY",
                "description": beat_description,
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "kind": {"type": "STRING", "enum": beat_kinds},
                        "x": {"type": "NUMBER", "description": "The x-value the beat is about"},
                        "lower": {"type": "NUMBER", "description": "Left end of a region"},
                        "upper": {"type": "NUMBER", "description": "Right end of a region"},
                        "h": {"type": "NUMBER", "description": "Starting step for a shrinking sequence"},
                        "counts": {
                            "type": "ARRAY",
                            "description": "Successive rectangle counts, e.g. [4, 8, 16, 32]",
                            "items": {"type": "INTEGER"},
                        },
                        "steps": {
                            "type": "ARRAY",
                            "description": "Explicit shrinking h values, e.g. [2, 1, 0.5, 0.25]",
                            "items": {"type": "NUMBER"},
                        },
                        "expression": {
                            "type": "STRING",
                            "description": "A second function, for transform and compare_curves beats",
                        },
                        "description": {
                            "type": "STRING",
                            "description": "How to describe a transformation, e.g. 'a shift 2 units right'",
                        },
                        "heading": {"type": "STRING", "description": "Optional on-screen beat heading"},
                    },
                    "required": ["kind"],
                },
            },
        },
        "required": ["function", "x_min", "x_max", "beats"],
    }


FUNCTION_GRAPH_SCHEMA: dict[str, Any] = _graph_schema(
    ["plot", "intercepts", "turning_point", "asymptote", "transform", "compare_curves"],
    (
        "Ordered list of beats. 'plot' draws and labels the curve; 'intercepts' reveals the "
        "x- and y-intercepts; 'turning_point' marks a stationary point and classifies it "
        "(optionally at a declared 'x'); 'asymptote' dashes in vertical asymptotes; "
        "'transform' (expression, description) morphs the curve into a transformed version "
        "of itself; 'compare_curves' (expression) draws a second curve alongside. Start with "
        "'plot' unless a later beat draws the curve itself."
    ),
)

_FUNCTION_GRAPH = TemplateSpec(
    id="FunctionGraph",
    description=(
        "Stage 6 curve sketching: what a function looks like and why. Plot a curve, reveal "
        "its intercepts, mark and classify turning points, show vertical asymptotes, apply a "
        "transformation (shift, stretch, reflection), or compare two curves on one set of "
        "axes. Use for 'sketch y = ...', 'what does this graph look like', 'how does changing "
        "this move the graph', domain and range, and features of polynomials, rationals, "
        "exponentials and logarithms."
    ),
    param_schema=FUNCTION_GRAPH_SCHEMA,
    scene_class=FunctionGraphScene,
    fixture_params={
        "title": "Features of a quadratic",
        "function": "x**2 - 4*x + 3",
        "x_min": -1,
        "x_max": 5,
        "beats": [
            {"kind": "plot"},
            {"kind": "intercepts"},
            {"kind": "turning_point"},
        ],
    },
)

CALCULUS_ON_CURVE_SCHEMA: dict[str, Any] = _graph_schema(
    [
        "tangent_at",
        "secant_to_tangent",
        "gradient_function",
        "riemann_sum",
        "area_under",
        "limit_approach",
    ],
    (
        "Ordered list of beats. 'tangent_at' (x) draws the tangent and states its gradient; "
        "'secant_to_tangent' (x, optional h or steps) shrinks a secant onto the tangent — "
        "differentiation from first principles; 'gradient_function' plots the derivative on "
        "the same axes; 'riemann_sum' (lower, upper, optional counts) refines rectangles "
        "under the curve; 'area_under' (lower, upper) shades the definite integral and shows "
        "its notation; 'limit_approach' (x) closes in on a value from both sides."
    ),
)

_CALCULUS_ON_CURVE = TemplateSpec(
    id="CalculusOnCurve",
    description=(
        "Stage 6 calculus on a graph: the gradient at a point as the limit of a secant "
        "(first principles), the derivative plotted as its own function, the area under a "
        "curve as a limit of rectangles, the definite integral, and one-sided limits. Use "
        "for 'what is a derivative really', 'differentiate from first principles', 'why is "
        "the integral the area', tangents and gradients at a point, and limits."
    ),
    param_schema=CALCULUS_ON_CURVE_SCHEMA,
    scene_class=CalculusOnCurveScene,
    fixture_params={
        "title": "Gradient as a limit",
        "function": "x**2",
        "x_min": -0.5,
        "x_max": 3,
        "beats": [{"kind": "secant_to_tangent", "x": 1, "steps": [1.5, 0.75]}],
    },
)


_REGISTRY: dict[str, TemplateSpec] = {
    "Triangle3Side": _TRIANGLE_3_SIDE,
    "WorkedExample": _WORKED_EXAMPLE,
    "AreaTransform": _AREA_TRANSFORM,
    "FunctionGraph": _FUNCTION_GRAPH,
    "CalculusOnCurve": _CALCULUS_ON_CURVE,
}


class TemplateLibrary:
    """Registry of named templates. New templates are data additions to `_REGISTRY`."""

    def list_templates(self) -> list[TemplateSpec]:
        return list(_REGISTRY.values())

    def get(self, template_id: str) -> TemplateSpec:
        try:
            return _REGISTRY[template_id]
        except KeyError as exc:
            raise KeyError(f"Unknown template: {template_id!r}") from exc

    def render(self, template_id: str, params: dict[str, Any], output_dir: Path) -> Path:
        spec = self.get(template_id)
        normalised = validate_params(spec, params)
        output_dir.mkdir(parents=True, exist_ok=True)

        spec.scene_class.params = normalised  # type: ignore[attr-defined]

        slug = template_id.lower()
        with tempconfig(
            {
                "media_dir": str(output_dir),
                "output_file": slug,
                "format": "mp4",
                "verbosity": "WARNING",
                "quality": "low_quality",
                "disable_caching": True,
            }
        ):
            scene = spec.scene_class()
            scene.render()
            return Path(scene.renderer.file_writer.movie_file_path).resolve()
