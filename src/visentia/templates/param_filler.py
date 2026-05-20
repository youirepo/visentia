"""ParamFiller: LLM-driven extraction of template parameters from a Prompt."""

from __future__ import annotations

import json
from dataclasses import dataclass

from visentia.llm import CODEGEN_TEMPERATURE, LLMError, LLMProvider
from visentia.templates.spec import ParamValidationError, TemplateSpec, validate_params

MAX_FILL_ATTEMPTS = 2


@dataclass(frozen=True)
class FillError:
    """Param extraction failed after retries."""

    message: str
    last_error: str | None = None


class ParamFiller:
    """Ask the LLM to fill a template's parameter schema from a natural-language Prompt."""

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def fill(self, prompt: str, spec: TemplateSpec) -> dict | FillError:
        system = (
            "You extract structured JSON parameters for a Visentia Manim math template. "
            "Return JSON only — no markdown, no commentary. "
            "All side lengths must be positive and satisfy the triangle inequality. "
            "If the Tutor does not specify numeric sides, pick sensible defaults for a "
            "Year 8 NSW demonstration (e.g. 3, 4, 5)."
        )
        last_error: str | None = None

        for attempt in range(MAX_FILL_ATTEMPTS + 1):
            user_parts = [
                f"Template: {spec.id}",
                f"Description: {spec.description}",
                f"Parameter schema: {json.dumps(spec.param_schema)}",
                f"Tutor Prompt: {prompt.strip()}",
                "Return JSON parameters matching the schema.",
            ]
            if last_error:
                user_parts.append(
                    f"Previous attempt failed validation: {last_error}. Fix the JSON."
                )

            try:
                reply = self._provider.complete(
                    messages=[{"role": "user", "content": "\n\n".join(user_parts)}],
                    system=system,
                    temperature=CODEGEN_TEMPERATURE,
                    response_schema=spec.param_schema,
                )
                data = json.loads(reply)
                return validate_params(spec, data)
            except (json.JSONDecodeError, ParamValidationError, LLMError) as exc:
                last_error = str(exc)
                if attempt >= MAX_FILL_ATTEMPTS:
                    break

        return FillError(
            message=f"Could not extract valid parameters for template {spec.id!r}.",
            last_error=last_error,
        )
