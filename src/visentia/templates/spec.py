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


VALIDATORS: dict[str, Any] = {
    "Triangle3Side": validate_triangle_3_side_params,
}


def validate_params(spec: TemplateSpec, params: dict[str, Any]) -> dict[str, Any]:
    """Validate `params` for `spec` and return a normalised copy."""

    validator = VALIDATORS.get(spec.id)
    if validator is None:
        raise ParamValidationError(f"No validator registered for template {spec.id!r}")
    return validator(params)
