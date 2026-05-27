"""Google Gemini implementation of `LLMProvider`.

Uses the modern `google-genai` SDK (not the deprecated `google-generativeai`). Reads the
API key from `GOOGLE_API_KEY` (preferred) or `GEMINI_API_KEY`. Free-tier models like
`gemini-3-flash-preview` need no extra setup beyond an API key from Google AI Studio.
"""

from __future__ import annotations

import os
import re
import time
from typing import Any

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from visentia.llm.base import (
    CODEGEN_TEMPERATURE,
    LLMError,
    LLMProvider,
    Message,
    MissingApiKeyError,
)

DEFAULT_GEMINI_MODEL: str = "gemini-3-flash-preview"
"""Default model. Preview by definition — swap to `gemini-2.5-flash` (GA) here if the
preview model is deprecated or behaves unstably mid-session."""

API_KEY_ENV_VARS: tuple[str, ...] = ("GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_AI_STUDIO_API_KEY")
"""Env var names the Gemini provider will look up, in order of precedence. Public so
tests and scripts can check the same set without re-listing the names."""

MODEL_ENV_VAR: str = "VISENTIA_GEMINI_MODEL"
"""Override the default model without code changes, e.g. `gemini-2.5-flash` when the
preview model's free-tier daily quota is exhausted."""

_MAX_RATE_LIMIT_RETRIES: int = 6


class Gemini(LLMProvider):
    """`LLMProvider` backed by Google's `google-genai` SDK.

    Model name is configuration, not part of the class name — `Gemini(model="gemini-2.5-flash")`
    is the path to GA when the preview model is no longer the default. The PRD makes this
    a day-one concern.
    """

    name = "gemini"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = _read_api_key()
        self.model = resolve_gemini_model(model)
        self._client = genai.Client(api_key=api_key)

    def complete(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        temperature: float = CODEGEN_TEMPERATURE,
        response_schema: dict | None = None,
    ) -> str:
        contents = [
            genai_types.Content(role=m["role"], parts=[genai_types.Part(text=m["content"])])
            for m in messages
        ]

        config_kwargs: dict[str, Any] = {"temperature": temperature}
        if system is not None:
            config_kwargs["system_instruction"] = system
        if response_schema is not None:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = response_schema

        try:
            response = _generate_with_rate_limit_retries(
                self._client,
                model=self.model,
                contents=contents,
                config=genai_types.GenerateContentConfig(**config_kwargs),
            )
        except genai_errors.ClientError as exc:
            raise _client_error_to_llm_error(exc, model=self.model) from exc
        except Exception as exc:
            raise LLMError(
                f"Gemini API call failed (model={self.model!r}): {exc}"
            ) from exc

        text = response.text
        if text is None:
            raise LLMError(
                f"Gemini returned no text (model={self.model!r}). "
                "This usually indicates a safety filter block or empty response."
            )
        return text


def resolve_gemini_model(explicit: str | None = None) -> str:
    """Model from constructor arg, else `VISENTIA_GEMINI_MODEL`, else default preview."""

    if explicit is not None:
        return explicit
    return os.environ.get(MODEL_ENV_VAR, DEFAULT_GEMINI_MODEL)


def _generate_with_rate_limit_retries(
    client: genai.Client,
    *,
    model: str,
    contents: list[genai_types.Content],
    config: genai_types.GenerateContentConfig,
) -> Any:
    """Retry burst 429s using RetryInfo; do not spin on daily free-tier quota exhaustion."""

    last_exc: genai_errors.ClientError | None = None
    for attempt in range(_MAX_RATE_LIMIT_RETRIES):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except genai_errors.ClientError as exc:
            last_exc = exc
            if exc.code != 429 or _is_daily_quota_exhausted(exc):
                raise
            delay_s = _retry_delay_seconds(exc, attempt)
            time.sleep(delay_s)
    assert last_exc is not None
    raise last_exc


def _is_daily_quota_exhausted(exc: genai_errors.ClientError) -> bool:
    text = str(exc).lower()
    return "perday" in text or "per_day" in text or "free_tier_requests" in text


def _retry_delay_seconds(exc: genai_errors.ClientError, attempt: int) -> float:
    match = re.search(r"retry in ([\d.]+)s", str(exc), flags=re.IGNORECASE)
    if match:
        return max(float(match.group(1)), 0.5)
    return min(2.0 * (2**attempt), 60.0)


def _client_error_to_llm_error(exc: genai_errors.ClientError, *, model: str) -> LLMError:
    if exc.code == 429 and _is_daily_quota_exhausted(exc):
        return LLMError(
            f"Gemini daily quota exhausted for model={model!r} on the free tier "
            f"(see https://ai.google.dev/gemini-api/docs/rate-limits). "
            f"Wait until the quota resets, enable billing on your Google AI project, "
            f"or set {MODEL_ENV_VAR}=gemini-2.5-flash to use a different model quota. "
            f"For evals, run one entry at a time: visentia eval --ids EV-001."
        )
    if exc.code == 429:
        return LLMError(
            f"Gemini rate limit hit for model={model!r} after retries. "
            "Wait a few seconds and try again."
        )
    return LLMError(f"Gemini API call failed (model={model!r}): {exc}")


def _read_api_key() -> str:
    for var in API_KEY_ENV_VARS:
        value = os.environ.get(var)
        if value:
            return value
    raise MissingApiKeyError(
        "Visentia needs a Google API key to reach Gemini. Set one of "
        f"{' or '.join(API_KEY_ENV_VARS)} in your environment "
        "(or in a .env file at the project root). "
        "Get a free key at https://aistudio.google.com/app/apikey."
    )
