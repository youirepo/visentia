"""Google Gemini implementation of `LLMProvider`.

Uses the modern `google-genai` SDK (not the deprecated `google-generativeai`). Reads the
API key from `GOOGLE_API_KEY` (preferred) or `GEMINI_API_KEY`. Free-tier models like
`gemini-3-flash-preview` need no extra setup beyond an API key from Google AI Studio.
"""

from __future__ import annotations

import os
from typing import Any

from google import genai
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


class Gemini(LLMProvider):
    """`LLMProvider` backed by Google's `google-genai` SDK.

    Model name is configuration, not part of the class name — `Gemini(model="gemini-2.5-flash")`
    is the path to GA when the preview model is no longer the default. The PRD makes this
    a day-one concern.
    """

    name = "gemini"

    def __init__(self, model: str = DEFAULT_GEMINI_MODEL, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = _read_api_key()
        self.model = model
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
            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=genai_types.GenerateContentConfig(**config_kwargs),
            )
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
