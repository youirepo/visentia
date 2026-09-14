"""RepairOrchestrator: the pipeline policy module.

Routes each Prompt through classification, then either a curriculum template (when the
classifier suggests one and params fill successfully) or freeform codegen with a
shared lint/render repair loop (ADR-0003).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from manim import config as manim_config

from visentia.classifier import Classification, ClassifierError, ContentClassifier
from visentia.freeform import (
    CodegenError,
    FreeformCodegen,
    LintOk,
    RenderFailure,
    RenderSuccess,
    RenderTimeout,
    SandboxedRenderer,
    StaticLinter,
)
from visentia.freeform.repair import format_lint_repair_context, format_render_result_context
from visentia.llm import LLMError, LLMProvider, MissingApiKeyError
from visentia.llm.gemini import Gemini
from visentia.results import Failure, GenerateResult, Mp4
from visentia.templates import FillError, ParamFiller, TemplateLibrary
from visentia.voiceover import VoiceoverSynthesizer

logger = logging.getLogger(__name__)


class FreeformExhausted(Exception):
    """Freeform repair budget spent without a successful render."""

    def __init__(self, *, attempts: int, message: str, last_error: str) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


class RepairOrchestrator:
    """v0.1 pipeline: classify → template (if matched) else freeform with repair loop."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        *,
        template_library: TemplateLibrary | None = None,
        sandboxed_renderer: SandboxedRenderer | None = None,
    ) -> None:
        self._provider = provider
        self._template_library = template_library or TemplateLibrary()
        self._sandboxed_renderer = sandboxed_renderer

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
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

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

        template_params: dict | None = None
        freeform_attempts: int | None = None
        classification_mode = (
            "template" if classification.suggested_template_id else "freeform"
        )

        try:
            if classification.suggested_template_id:
                try:
                    mp4_path, path_taken, template_params = self._render_template(
                        prompt,
                        classification,
                        target_dir,
                    )
                except RuntimeError as template_exc:
                    logger.warning(
                        "Template path failed (%s); trying freeform with repair loop",
                        template_exc,
                    )
                    classification_mode = "freeform"
                    mp4_path, path_taken, freeform_attempts = self._render_freeform(
                        prompt,
                        classification,
                        target_dir,
                        max_attempts=max_attempts,
                    )
            else:
                mp4_path, path_taken, freeform_attempts = self._render_freeform(
                    prompt,
                    classification,
                    target_dir,
                    max_attempts=max_attempts,
                )
        except FreeformExhausted as exc:
            logger.warning(
                "Freeform exhausted after %s attempts; last_error=%s",
                exc.attempts,
                exc.last_error[:500],
            )
            if classification.suggested_template_id:
                try:
                    mp4_path, path_taken, template_params = self._render_template(
                        prompt,
                        classification,
                        target_dir,
                    )
                    path_taken = f"freeform-fallback-to-{path_taken}"
                    classification_mode = "freeform-fallback-to-template"
                    freeform_attempts = exc.attempts
                except Exception as fallback_exc:
                    return Failure(
                        message=(
                            "Visentia couldn't generate a freeform video after several tries, "
                            "and the curriculum template fallback also failed."
                        ),
                        attempts_made=exc.attempts,
                        last_error=str(fallback_exc),
                        path_taken="total-failure",
                    )
            else:
                return Failure(
                    message=str(exc.args[0]),
                    attempts_made=exc.attempts,
                    last_error=exc.last_error,
                    path_taken="total-failure",
                )
        except CodegenError as exc:
            return Failure(
                message="Visentia couldn't generate Manim code for this Prompt.",
                attempts_made=1,
                last_error=str(exc),
                path_taken="total-failure",
            )
        except Exception as exc:
            return Failure(
                message="Visentia couldn't render the Explainer Artifact. Check that Manim is installed correctly.",
                attempts_made=1,
                last_error=str(exc),
                path_taken="total-failure",
            )

        metadata = {
            "path_taken": path_taken,
            "classification_mode": classification_mode,
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
        if freeform_attempts is not None:
            metadata["freeform_attempts"] = freeform_attempts

        sidecar_path = _write_metadata_sidecar(mp4_path, metadata)
        logger.info(
            "Visentia sidecar metadata written to %s (path_taken=%s, freeform_attempts=%s)",
            sidecar_path,
            path_taken,
            freeform_attempts,
        )

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
            raise RuntimeError(
                fill_result.message
                + (f" ({fill_result.last_error})" if fill_result.last_error else "")
            )

        mp4_path = self._template_library.render(template_id, fill_result, output_dir)
        # Named rather than bare "template" so eval runs can report template *coverage* —
        # which templates the classifier actually reaches, and how each one fares against
        # the freeform baseline (issue #33).
        return mp4_path, f"template:{template_id}", fill_result

    def _render_freeform(
        self,
        prompt: str,
        classification: Classification,
        output_dir: Path,
        *,
        max_attempts: int,
    ) -> tuple[Path, str, int]:
        codegen = FreeformCodegen(self.provider)
        linter = StaticLinter()
        renderer = self._sandboxed_renderer or SandboxedRenderer()

        repair_context: str | None = None
        last_error = ""

        for attempt in range(1, max_attempts + 1):
            logger.info("Freeform attempt %s/%s", attempt, max_attempts)

            try:
                source = codegen.generate(
                    prompt,
                    classification.math_content_type,
                    repair_context=repair_context,
                )
            except CodegenError as exc:
                last_error = str(exc)
                repair_context = (
                    f"Code generation failed: {exc}\nReturn the complete corrected Python file only."
                )
                continue

            lint_result = linter.lint(source)
            if not isinstance(lint_result, LintOk):
                last_error = "; ".join(e.message for e in lint_result)
                repair_context = format_lint_repair_context(lint_result)
                logger.info("Freeform attempt %s: lint failed", attempt)
                continue

            render_result = renderer.render(
                source, lint_result.scene_class_name, output_dir
            )

            if isinstance(render_result, RenderSuccess):
                path_taken = f"freeform-success-on-attempt-{attempt}"
                logger.info("Freeform succeeded on attempt %s", attempt)
                return render_result.mp4_path, path_taken, attempt

            last_error = (
                render_result.stderr
                if isinstance(render_result, (RenderFailure, RenderTimeout))
                else str(render_result)
            )
            if isinstance(render_result, RenderFailure):
                last_error = render_result.message + (
                    f" ({render_result.stderr[:500]})" if render_result.stderr else ""
                )
            repair_context = format_render_result_context(render_result)
            logger.info("Freeform attempt %s: render failed", attempt)

        raise FreeformExhausted(
            attempts=max_attempts,
            message=(
                "Visentia couldn't produce a valid video after several tries. "
                "Try rephrasing the Prompt or simplifying what you're asking for."
            ),
            last_error=last_error,
        )


def _write_metadata_sidecar(mp4_path: Path, metadata: dict) -> Path:
    """Write `<mp4>.json` next to the MP4 and return its path."""

    sidecar = mp4_path.with_suffix(mp4_path.suffix + ".json")
    sidecar.write_text(json.dumps(metadata, indent=2, default=str))
    return sidecar


def sidecar_path_for(mp4_path: Path) -> Path:
    """Public helper for tests and downstream tools to locate the sidecar JSON."""

    return mp4_path.with_suffix(mp4_path.suffix + ".json")
