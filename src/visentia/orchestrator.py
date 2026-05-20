"""RepairOrchestrator: the pipeline policy module.

Routes each Prompt through classification, then either a curriculum template (when the
classifier suggests one and params fill successfully) or the placeholder spine until the
freeform path lands in slice #7.
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
from visentia.templates import FillError, ParamFiller, TemplateLibrary
from visentia.voiceover import VoiceoverSynthesizer

logger = logging.getLogger(__name__)


class RepairOrchestrator:
    """v0.1 pipeline: classify → template render (if matched) else placeholder spine."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        *,
        template_library: TemplateLibrary | None = None,
    ) -> None:
        self._provider = provider
        self._template_library = template_library or TemplateLibrary()

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

        path_taken = "spine-stub"
        template_params: dict | None = None

        try:
            if classification.suggested_template_id:
                mp4_path, path_taken, template_params = self._render_template(
                    prompt,
                    classification,
                    target_dir,
                )
            else:
                mp4_path = _render_spine_scene(target_dir)
        except Exception as exc:
            return Failure(
                message="Visentia couldn't render the Explainer Artifact. Check that Manim is installed correctly.",
                attempts_made=1,
                last_error=str(exc),
            )

        metadata = {
            "path_taken": path_taken,
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
        if template_params is not None:
            metadata["template_params"] = template_params

        sidecar_path = _write_metadata_sidecar(mp4_path, metadata)
        logger.info("Visentia sidecar metadata written to %s", sidecar_path)

        return Mp4(path=mp4_path, metadata=metadata)

    def _render_template(
        self,
        prompt: str,
        classification: Classification,
        output_dir: Path,
    ) -> tuple[Path, str, dict]:
        template_id = classification.suggested_template_id
        assert template_id is not None

        spec = self._template_library.get(template_id)
        filler = ParamFiller(self.provider)
        fill_result = filler.fill(prompt, spec)

        if isinstance(fill_result, FillError):
            raise RuntimeError(fill_result.message + (f" ({fill_result.last_error})" if fill_result.last_error else ""))

        mp4_path = self._template_library.render(template_id, fill_result, output_dir)
        return mp4_path, f"template:{template_id}", fill_result


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
