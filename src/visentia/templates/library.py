"""TemplateLibrary: registry of curriculum Manim templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from manim import tempconfig

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

_REGISTRY: dict[str, TemplateSpec] = {
    "Triangle3Side": _TRIANGLE_3_SIDE,
    "WorkedExample": _WORKED_EXAMPLE,
    "AreaTransform": _AREA_TRANSFORM,
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
