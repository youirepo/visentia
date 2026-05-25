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


VALIDATORS: dict[str, Any] = {
    "Triangle3Side": validate_triangle_3_side_params,
    "WorkedExample": validate_worked_example_params,
    "AreaTransform": validate_area_transform_params,
}


def validate_params(spec: TemplateSpec, params: dict[str, Any]) -> dict[str, Any]:
    """Validate `params` for `spec` and return a normalised copy."""

    validator = VALIDATORS.get(spec.id)
    if validator is None:
        raise ParamValidationError(f"No validator registered for template {spec.id!r}")
    return validator(params)
