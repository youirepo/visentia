"""Anthropic implementation of `LLMProvider`.

Implements the model choice made in issue #27 — Sonnet 5 for classification and parameter
filling, Opus 5 for freeform code generation and narration — which had been recorded as a
decision on map #22 but never built.

## Three places the Anthropic API does not line up with this repo's `LLMProvider`

**`temperature` no longer exists.** It was removed on Claude Opus 5 and Claude Sonnet 5;
sending it returns HTTP 400. `complete()` still accepts the argument, because the
interface and every call site pass one, but the value is discarded rather than
translated. Nothing here silently reinterprets it: repeatability for structured calls
comes from the response schema, which constrains the output far harder than `T=0.2` ever
did. The `*_TEMPERATURE` constants in `llm.base` are inert on this path.

**Structured output is `output_config`, not `response_schema`.** The shape is
`output_config={"format": {"type": "json_schema", "schema": ...}}`, and the schema must be
real JSON Schema — lowercase type names, `additionalProperties` declared. The template
schemas in this repo are written in Gemini's dialect (`"type": "OBJECT"`), so
`to_json_schema()` translates them at the boundary. See its docstring for why the
translation lives here rather than in the templates.

**Effort replaces the tuning knob temperature used to be.** `output_config.effort`
controls thinking depth and token spend. Classification is a menu pick and runs at `low`;
codegen is the job the model is actually bad at and runs at `high`. This is a different
axis from temperature — it buys reasoning, not determinism — and is set per call site
rather than derived from the temperature argument.
"""

from __future__ import annotations

import os
from typing import Any

import anthropic

from visentia.llm.base import (
    CODEGEN_TEMPERATURE,
    LLMError,
    LLMProvider,
    Message,
    MissingApiKeyError,
)

CHAT_MODEL: str = "claude-sonnet-5"
"""Classification and parameter filling (#27). The model picks a template and fills a
typed schema — a constrained job, and the cheaper model at $2/$10 per MTok."""

CODEGEN_MODEL: str = "claude-opus-5"
"""Freeform Manim generation and narration (#27). This is the job PRISM measures at
26-57% spatial correctness, so it gets the capable model at $5/$25 per MTok."""

DEFAULT_MODEL: str = CODEGEN_MODEL

API_KEY_ENV_VAR: str = "ANTHROPIC_API_KEY"
MODEL_ENV_VAR: str = "VISENTIA_ANTHROPIC_MODEL"
"""Override the model without code changes, e.g. to price-check a run on Sonnet."""

MAX_TOKENS: int = 16_000
"""Non-streaming ceiling. Large enough for a full Manim scene; small enough to stay under
the SDK's HTTP timeout without streaming."""

LOW_EFFORT: str = "low"
HIGH_EFFORT: str = "high"


class Claude(LLMProvider):
    """`LLMProvider` backed by the Anthropic Messages API.

    Model and effort are constructor arguments so one class serves both roles from #27:

        Claude(model=CHAT_MODEL, effort=LOW_EFFORT)       # classify, fill params
        Claude(model=CODEGEN_MODEL, effort=HIGH_EFFORT)   # generate Manim, narrate
    """

    name = "anthropic"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        *,
        effort: str = HIGH_EFFORT,
        max_tokens: int = MAX_TOKENS,
    ) -> None:
        self.model = resolve_model(model)
        self.effort = effort
        self.max_tokens = max_tokens
        self._client = anthropic.Anthropic(**({"api_key": api_key} if api_key else {}))

    def complete(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        temperature: float = CODEGEN_TEMPERATURE,
        response_schema: dict | None = None,
    ) -> str:
        # Accepted for interface compatibility and deliberately unused — Opus 5 and
        # Sonnet 5 reject `temperature` with a 400. See the module docstring.
        del temperature

        request: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
        }
        if system is not None:
            request["system"] = system

        output_config: dict[str, Any] = {"effort": self.effort}
        if response_schema is not None:
            output_config["format"] = {
                "type": "json_schema",
                "schema": to_json_schema(response_schema),
            }
        request["output_config"] = output_config

        try:
            response = self._client.messages.create(**request)
        except anthropic.AuthenticationError as exc:
            raise MissingApiKeyError(
                f"Anthropic rejected the credentials. Set {API_KEY_ENV_VAR} in your "
                "environment or .env file."
            ) from exc
        except anthropic.NotFoundError as exc:
            raise LLMError(
                f"Anthropic has no model named {self.model!r}. Check {MODEL_ENV_VAR}."
            ) from exc
        except anthropic.RateLimitError as exc:
            # The SDK already retried with backoff; arriving here means it kept failing.
            raise LLMError(
                f"Anthropic rate limit not cleared after retries (model={self.model!r}): {exc}"
            ) from exc
        except anthropic.APIStatusError as exc:
            raise LLMError(
                f"Anthropic API error {exc.status_code} (model={self.model!r}): {exc.message}"
            ) from exc
        except anthropic.APIConnectionError as exc:
            raise LLMError(f"Could not reach the Anthropic API: {exc}") from exc

        if response.stop_reason == "refusal":
            category = getattr(response.stop_details, "category", None)
            raise LLMError(
                f"Anthropic declined this request (category={category!r}). "
                "Rephrasing the Prompt usually clears it."
            )

        text = _first_text(response)
        if not text:
            raise LLMError(
                f"Anthropic returned no text (model={self.model!r}, "
                f"stop_reason={response.stop_reason!r})."
            )
        return text


def _first_text(response: Any) -> str:
    """The response's text, skipping thinking blocks.

    Thinking is adaptive by default on both models, so `content` routinely opens with a
    `thinking` block. Reading `content[0].text` would fail or return reasoning.
    """

    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ).strip()


def resolve_model(explicit: str | None = None) -> str:
    """Model from the constructor arg, else `VISENTIA_ANTHROPIC_MODEL`, else the default."""

    if explicit is not None:
        return explicit
    return os.environ.get(MODEL_ENV_VAR, DEFAULT_MODEL)


_GEMINI_TYPE_NAMES = {
    "OBJECT": "object",
    "STRING": "string",
    "NUMBER": "number",
    "INTEGER": "integer",
    "BOOLEAN": "boolean",
    "ARRAY": "array",
}


def to_json_schema(schema: dict) -> dict:
    """Translate a template `param_schema` into JSON Schema for `output_config.format`.

    The schemas in `templates/library.py` are written in the dialect the Gemini SDK
    accepted: uppercase type names (`"OBJECT"`, `"STRING"`). Anthropic wants ordinary
    JSON Schema. The translation lives in the provider rather than in the templates on
    purpose — a template describes *what parameters a scene takes*, which is not a fact
    about any model vendor, and rewriting six schemas into one vendor's dialect would
    just move the coupling somewhere harder to see.

    `additionalProperties: false` is added to every object, which structured outputs
    expects and which is also what we want: a model inventing an extra parameter should
    fail loudly at the boundary rather than have it silently dropped by the validator.
    """

    if not isinstance(schema, dict):
        return schema

    translated: dict[str, Any] = {}
    for key, value in schema.items():
        if key == "type" and isinstance(value, str):
            translated[key] = _GEMINI_TYPE_NAMES.get(value.upper(), value)
        elif key == "properties" and isinstance(value, dict):
            translated[key] = {name: to_json_schema(sub) for name, sub in value.items()}
        elif key == "items":
            translated[key] = to_json_schema(value)
        else:
            translated[key] = value

    if translated.get("type") == "object":
        translated.setdefault("additionalProperties", False)
        translated.setdefault("required", sorted(translated.get("properties", {})))

    return translated
