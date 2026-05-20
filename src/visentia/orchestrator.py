"""RepairOrchestrator: the pipeline policy module.

This slice (#2) ships the module as a stub. `generate_video` ignores the prompt and renders
the placeholder `SpineScene`. The interface — `generate_video(prompt, max_attempts) -> GenerateResult` —
is the one the PRD commits to, so every subsequent slice (LLM wiring, template path, freeform
path, repair loop) only replaces the body, not the signature.
"""

from __future__ import annotations

from pathlib import Path

from manim import config as manim_config
from manim import tempconfig

from visentia.results import Failure, GenerateResult, Mp4
from visentia.scenes.spine import SpineScene
from visentia.voiceover import VoiceoverSynthesizer


class RepairOrchestrator:
    """Stub implementation of the pipeline. See `generate_video` for details.

    The non-stub implementation arrives across slices:
      - #4: classifier picks a Math Content Type
      - #6: template path routes to a curriculum template
      - #7: freeform path with static lint + sandboxed render
      - #8: repair loop with bounded retries and template fallback
    """

    def generate_video(
        self,
        prompt: str,
        *,
        output_dir: Path | None = None,
        max_attempts: int = 3,
    ) -> GenerateResult:
        del prompt, max_attempts

        target_dir = (output_dir or Path.cwd() / "videos").resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            mp4_path = _render_spine_scene(target_dir)
        except Exception as exc:
            return Failure(
                message="Visentia couldn't render the placeholder video. Check that Manim is installed correctly.",
                attempts_made=1,
                last_error=str(exc),
            )

        return Mp4(
            path=mp4_path,
            metadata={
                "path_taken": "spine-stub",
                "renderer": "manim",
                "manim_quality": manim_config.quality,
                "voice": VoiceoverSynthesizer.DEFAULT_VOICE,
                "tts": "edge-tts",
            },
        )


def _render_spine_scene(output_dir: Path) -> Path:
    """Render the placeholder Scene to `output_dir` and return the resulting MP4 path."""

    with tempconfig(
        {
            "media_dir": str(output_dir),
            "output_file": "spine",
            "format": "mp4",
            "verbosity": "WARNING",
            "quality": "low_quality",
            "disable_caching": True,
        }
    ):
        scene = SpineScene()
        scene.render()
        return Path(scene.renderer.file_writer.movie_file_path).resolve()
