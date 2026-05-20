"""TemplateLibrary: registry of curriculum Manim templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from manim import tempconfig

from visentia.scenes.triangle_3_side import Triangle3SideScene
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

_REGISTRY: dict[str, TemplateSpec] = {
    "Triangle3Side": _TRIANGLE_3_SIDE,
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
