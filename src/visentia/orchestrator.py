"""RepairOrchestrator: the pipeline policy module.

This slice (#4) adds the LLM tier:
  - `ContentClassifier` (via an injected `LLMProvider`) classifies the Prompt into a
    Math Content Type + suggested Mode.
  - The classification is logged on every call and written to a sidecar JSON next to
    the MP4.
  - Render still uses the placeholder `SpineScene` — template path lands in slice #6,
    freeform path in #7, full repair loop in #8.

The `generate_video(prompt, max_attempts) -> GenerateResult` contract is unchanged from
the PRD. Subsequent slices replace internals, not the signature.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from manim import config as manim_config
from manim import tempconfig

from visentia.classifier import Classification, ClassifierError, ContentClassifier
from visentia.llm import LLMError, LLMProvider, MissingApiKeyError
from visentia.llm.gemini import Gemini
from visentia.results import Failure, GenerateResult, Mp4
from visentia.scenes.spine import SpineScene
from visentia.voiceover import VoiceoverSynthesizer

logger = logging.getLogger(__name__)


class RepairOrchestrator:
    """Stub-evolving implementation of the v0.1 pipeline.

    Subsequent slices replace the body:
      - #6: template path routes to a curriculum template
      - #7: freeform path with static lint + sandboxed render
      - #8: repair loop with bounded retries and template fallback
    """

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider

    @property
    def provider(self) -> LLMProvider:
        if self._provider is None:
            self._provider = Gemini()
        return self._provider

    def generate_video(
        self,
        prompt: str,
        *,
        output_dir: Path | None = None,
        max_attempts: int = 3,
    ) -> GenerateResult:
        del max_attempts

        target_dir = (output_dir or Path.cwd() / "videos").resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            classifier = ContentClassifier(self.provider)
            classification = classifier.classify(prompt)
        except MissingApiKeyError as exc:
            return Failure(
                message=str(exc),
                attempts_made=0,
                last_error="missing API key",
            )
        except ClassifierError as exc:
            return Failure(
                message="Visentia couldn't classify the Prompt. The model returned an unexpected response.",
                attempts_made=1,
                last_error=str(exc),
            )
        except LLMError as exc:
            return Failure(
                message="Visentia couldn't reach the LLM provider. Check your internet connection and API key.",
                attempts_made=1,
                last_error=str(exc),
            )

        logger.info(
            "Visentia classification: math_content_type=%s suggested_mode=%s suggested_template_id=%s",
            classification.math_content_type,
            classification.suggested_mode,
            classification.suggested_template_id,
        )

        try:
            mp4_path = _render_spine_scene(target_dir)
        except Exception as exc:
            return Failure(
                message="Visentia couldn't render the placeholder video. Check that Manim is installed correctly.",
                attempts_made=1,
                last_error=str(exc),
            )

        metadata = {
            "path_taken": "spine-stub",
            "renderer": "manim",
            "manim_quality": manim_config.quality,
            "voice": VoiceoverSynthesizer.DEFAULT_VOICE,
            "tts": "edge-tts",
            "llm_provider": self.provider.name,
            "llm_model": self.provider.model,
            "classification": {
                "math_content_type": classification.math_content_type,
                "suggested_template_id": classification.suggested_template_id,
                "suggested_mode": classification.suggested_mode,
            },
            "prompt": prompt,
        }

        sidecar_path = _write_metadata_sidecar(mp4_path, metadata)
        logger.info("Visentia sidecar metadata written to %s", sidecar_path)

        return Mp4(path=mp4_path, metadata=metadata)


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


def _write_metadata_sidecar(mp4_path: Path, metadata: dict) -> Path:
    """Write `<mp4>.json` next to the MP4 and return its path."""

    sidecar = mp4_path.with_suffix(mp4_path.suffix + ".json")
    sidecar.write_text(json.dumps(metadata, indent=2, default=str))
    return sidecar


def sidecar_path_for(mp4_path: Path) -> Path:
    """Public helper for tests and downstream tools to locate the sidecar JSON."""

    return mp4_path.with_suffix(mp4_path.suffix + ".json")
