"""TemplateSpec and parameter validation for curriculum templates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Type


@dataclass(frozen=True)
class TemplateSpec:
    """Metadata + render target for one Manim curriculum template."""

    id: str
    description: str
    """Shown to the classifier and ParamFiller so the LLM knows when to use this template."""

    param_schema: dict[str, Any]
    """JSON-schema-shaped dict describing valid `params` for `ParamFiller` and validation."""

    scene_class: Type[Any]
    """A Manim `VoiceoverScene` subclass with a class-level `params` dict set before render."""

    fixture_params: dict[str, Any]
    """Known-good params for CI fixture renders (e.g. Triangle3Side with 3,4,5)."""


class ParamValidationError(ValueError):
    """Raised when params fail schema or domain validation."""


def validate_triangle_3_side_params(params: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalise params for Triangle3Side."""

    for key in ("side_a", "side_b", "side_c"):
        if key not in params:
            raise ParamValidationError(f"Missing required field: {key}")
        value = params[key]
        if not isinstance(value, (int, float)) or value <= 0:
            raise ParamValidationError(f"{key} must be a positive number, got {value!r}")

    a, b, c = float(params["side_a"]), float(params["side_b"]), float(params["side_c"])
    sides = sorted([a, b, c])
    if sides[0] + sides[1] <= sides[2]:
        raise ParamValidationError(
            f"Sides {a}, {b}, {c} do not satisfy the triangle inequality."
        )

    include_sweep = params.get("include_sweep", True)
    if not isinstance(include_sweep, bool):
        raise ParamValidationError("include_sweep must be a boolean if provided")

    return {
        "side_a": a,
        "side_b": b,
        "side_c": c,
        "include_sweep": include_sweep,
    }


_UNIT_DIMENSIONS: dict[str, str] = {
    "g": "mass",
    "kg": "mass",
    "mg": "mass",
    "m": "length",
    "cm": "length",
    "km": "length",
    "L": "volume",
    "mL": "volume",
    "l": "volume",
    "ml": "volume",
}


def validate_worked_example_params(params: dict[str, Any]) -> dict[str, Any]:
    """Validate params for WorkedExample (rate × quantity with unit conversion)."""

    required = (
        "rate_numerator",
        "rate_denominator",
        "rate_unit",
        "quantity",
        "quantity_unit",
        "unit_conversion_factor",
    )
    for key in required:
        if key not in params:
            raise ParamValidationError(f"Missing required field: {key}")

    rate_num = float(params["rate_numerator"])
    rate_den = float(params["rate_denominator"])
    quantity = float(params["quantity"])
    factor = float(params["unit_conversion_factor"])

    if rate_num <= 0 or rate_den <= 0 or quantity <= 0 or factor <= 0:
        raise ParamValidationError("Rate, quantity, and conversion factor must be positive.")

    rate_unit = str(params["rate_unit"]).strip()
    quantity_unit = str(params["quantity_unit"]).strip()
    if rate_unit not in _UNIT_DIMENSIONS:
        raise ParamValidationError(f"Unsupported rate_unit: {rate_unit!r}")
    if quantity_unit not in _UNIT_DIMENSIONS:
        raise ParamValidationError(f"Unsupported quantity_unit: {quantity_unit!r}")

    if _UNIT_DIMENSIONS[rate_unit] != _UNIT_DIMENSIONS[quantity_unit]:
        raise ParamValidationError(
            f"Cannot convert between {quantity_unit!r} and {rate_unit!r} — "
            "different physical dimensions."
        )

    if "$" in rate_unit or "$" in quantity_unit or "dollar" in rate_unit.lower():
        raise ParamValidationError("Currency belongs in currency_symbol, not in unit fields.")

    currency = str(params.get("currency_symbol", r"\$"))
    item_label = str(params.get("item_label", "Item"))

    return {
        "item_label": item_label,
        "rate_numerator": rate_num,
        "currency_symbol": currency,
        "rate_denominator": rate_den,
        "rate_unit": rate_unit,
        "quantity": quantity,
        "quantity_unit": quantity_unit,
        "unit_conversion_factor": factor,
    }


def validate_area_transform_params(params: dict[str, Any]) -> dict[str, Any]:
    """Validate params for AreaTransform (rhombus + trapezium derivations)."""

    fields = ("rhombus_d1", "rhombus_d2", "trapezium_a", "trapezium_b", "trapezium_h")
    for key in fields:
        if key not in params:
            raise ParamValidationError(f"Missing required field: {key}")
        val = float(params[key])
        if val <= 0:
            raise ParamValidationError(f"{key} must be positive, got {val!r}")

    include_trapezium = params.get("include_trapezium", True)
    if not isinstance(include_trapezium, bool):
        raise ParamValidationError("include_trapezium must be a boolean if provided")

    return {
        "rhombus_d1": float(params["rhombus_d1"]),
        "rhombus_d2": float(params["rhombus_d2"]),
        "trapezium_a": float(params["trapezium_a"]),
        "trapezium_b": float(params["trapezium_b"]),
        "trapezium_h": float(params["trapezium_h"]),
        "include_trapezium": include_trapezium,
    }


def _num(params: dict[str, Any], key: str, where: str) -> float:
    if key not in params:
        raise ParamValidationError(f"{where}: missing required field {key!r}")
    try:
        return float(params[key])
    except (TypeError, ValueError) as exc:
        raise ParamValidationError(f"{where}: {key} must be a number, got {params[key]!r}") from exc


# ---------------------------------------------------------------------------
# Stage 6 functions and calculus (issue #33)
#
# Both Stage 6 templates take the same shape — one function, one window, a list of beats —
# so they share a validator, parameterised by which beat kinds the template plays. The
# function itself is validated by parsing it: `parse_function` accepts only whitelisted
# expressions, so an unusable or unsafe function is rejected here rather than at render.
# ---------------------------------------------------------------------------

FUNCTION_GRAPH_BEATS: dict[str, tuple[str, ...]] = {
    "plot": (),
    "intercepts": (),
    "turning_point": (),
    "asymptote": (),
    "transform": ("expression",),
    "compare_curves": ("expression",),
}

CALCULUS_ON_CURVE_BEATS: dict[str, tuple[str, ...]] = {
    "tangent_at": ("x",),
    "secant_to_tangent": ("x",),
    "gradient_function": (),
    "riemann_sum": ("lower", "upper"),
    "area_under": ("lower", "upper"),
    "limit_approach": ("x",),
}

MAX_BEATS = 8
"""Beats per video. Eight beats is already a long Stage 6 explainer; more usually means the
classifier has folded two concepts into one request."""


def _validate_expression(source: object, where: str) -> str:
    from visentia.scenes.expressions import ExpressionError, parse_function

    try:
        return parse_function(str(source)).source
    except ExpressionError as exc:
        raise ParamValidationError(f"{where}: {exc}") from exc


def validate_graph_params(
    params: dict[str, Any], *, beat_kinds: dict[str, tuple[str, ...]], template: str
) -> dict[str, Any]:
    """Validate params for a Stage 6 graph template (function + window + beats)."""

    if "function" not in params:
        raise ParamValidationError(f"{template}: missing required field 'function'")
    function_source = _validate_expression(params["function"], f"{template}.function")

    x_min = _num(params, "x_min", template)
    x_max = _num(params, "x_max", template)
    if x_min >= x_max:
        raise ParamValidationError(f"{template}: x_min ({x_min}) must be less than x_max ({x_max}).")
    if x_max - x_min > 200:
        raise ParamValidationError(
            f"{template}: domain [{x_min}, {x_max}] is too wide to show anything legible."
        )

    y_min = float(params["y_min"]) if params.get("y_min") is not None else None
    y_max = float(params["y_max"]) if params.get("y_max") is not None else None
    if y_min is not None and y_max is not None and y_min >= y_max:
        raise ParamValidationError(f"{template}: y_min ({y_min}) must be less than y_max ({y_max}).")

    beats = params.get("beats")
    if not isinstance(beats, list) or not beats:
        raise ParamValidationError(f"{template}: beats must be a non-empty list.")
    if len(beats) > MAX_BEATS:
        raise ParamValidationError(
            f"{template}: {len(beats)} beats exceeds the maximum of {MAX_BEATS}."
        )

    clean_beats: list[dict[str, Any]] = []
    for index, beat in enumerate(beats):
        where = f"{template}.beats[{index}]"
        if not isinstance(beat, dict):
            raise ParamValidationError(f"{where} must be an object.")

        kind = beat.get("kind")
        if kind not in beat_kinds:
            raise ParamValidationError(
                f"{where}: kind must be one of {tuple(beat_kinds)}, got {kind!r}"
            )

        clean: dict[str, Any] = {"kind": kind}
        for field in beat_kinds[kind]:
            if field not in beat:
                raise ParamValidationError(f"{where} ({kind}): missing required field {field!r}")
            if field == "expression":
                clean[field] = _validate_expression(beat[field], f"{where}.expression")
            else:
                clean[field] = _num(beat, field, where)

        for optional in ("x", "lower", "upper", "h"):
            if optional in beat and optional not in clean:
                clean[optional] = _num(beat, optional, where)

        if kind in ("riemann_sum", "area_under") and clean["lower"] >= clean["upper"]:
            raise ParamValidationError(
                f"{where} ({kind}): lower ({clean['lower']}) must be less than upper ({clean['upper']})."
            )

        for point_field in ("x", "lower", "upper"):
            value = clean.get(point_field)
            if value is not None and not (x_min <= value <= x_max):
                raise ParamValidationError(
                    f"{where} ({kind}): {point_field} = {value} is outside the plotted domain "
                    f"[{x_min}, {x_max}]."
                )

        if "counts" in beat:
            counts = beat["counts"]
            if not isinstance(counts, list) or not counts:
                raise ParamValidationError(f"{where}: counts must be a non-empty list of integers.")
            parsed_counts = []
            for count in counts:
                count = int(count)
                if not 1 <= count <= 200:
                    raise ParamValidationError(f"{where}: rectangle count {count} is out of range 1-200.")
                parsed_counts.append(count)
            clean["counts"] = parsed_counts

        if "steps" in beat:
            steps = beat["steps"]
            if not isinstance(steps, list) or not steps:
                raise ParamValidationError(f"{where}: steps must be a non-empty list of numbers.")
            clean["steps"] = [float(step) for step in steps]

        for text_field in ("heading", "description"):
            if text_field in beat:
                clean[text_field] = str(beat[text_field])

        clean_beats.append(clean)

    result: dict[str, Any] = {
        "title": str(params.get("title", "")),
        "function": function_source,
        "x_min": x_min,
        "x_max": x_max,
        "beats": clean_beats,
    }
    if y_min is not None:
        result["y_min"] = y_min
    if y_max is not None:
        result["y_max"] = y_max
    return result


def validate_function_graph_params(params: dict[str, Any]) -> dict[str, Any]:
    """Validate params for FunctionGraph (sketching, features, transformations)."""

    return validate_graph_params(
        params, beat_kinds=FUNCTION_GRAPH_BEATS, template="FunctionGraph"
    )


def validate_calculus_on_curve_params(params: dict[str, Any]) -> dict[str, Any]:
    """Validate params for CalculusOnCurve (tangents, gradients, area, limits)."""

    return validate_graph_params(
        params, beat_kinds=CALCULUS_ON_CURVE_BEATS, template="CalculusOnCurve"
    )


VALIDATORS: dict[str, Any] = {
    "Triangle3Side": validate_triangle_3_side_params,
    "WorkedExample": validate_worked_example_params,
    "AreaTransform": validate_area_transform_params,
    "FunctionGraph": validate_function_graph_params,
    "CalculusOnCurve": validate_calculus_on_curve_params,
}


def validate_params(spec: TemplateSpec, params: dict[str, Any]) -> dict[str, Any]:
    """Validate `params` for `spec` and return a normalised copy."""

    validator = VALIDATORS.get(spec.id)
    if validator is None:
        raise ParamValidationError(f"No validator registered for template {spec.id!r}")
    return validator(params)
