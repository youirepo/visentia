"""Abstract `LLMProvider` interface plus shared types, errors, and temperature constants.

Visentia's modules call `provider.complete(...)` and nothing else. Provider-specific
quirks (request shapes, auth, response unwrapping) live in implementations under this
package. Adding a new provider = one new module + one new class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, TypedDict

CODEGEN_TEMPERATURE: float = 0.2
"""Default temperature for code generation. Probe (2026-05-19) ran at T=1 and observed
bug-per-run variance; production codegen should sit lower for reproducibility."""

NARRATION_TEMPERATURE: float = 0.4
"""Default temperature for narration / voiceover script generation. Slightly higher
than codegen because variety in phrasing matters more than determinism."""

CLASSIFICATION_TEMPERATURE: float = 0.2
"""Default temperature for structured-output classification (Math Content Type, params).
Treated like codegen — we want repeatable structured output, not creative variation."""


class Message(TypedDict):
    """One turn in a chat-style conversation. System prompt is a separate kwarg on
    `LLMProvider.complete` because providers diverge on whether `system` is a message
    role (OpenAI) or a top-level parameter (Anthropic, Google)."""

    role: Literal["user", "assistant"]
    content: str


class LLMError(Exception):
    """Base class for errors originating in the LLM tier. Caught by the orchestrator
    and surfaced to the Tutor as `Failure` with a plain-language message."""


class MissingApiKeyError(LLMError):
    """Raised at provider construction when the required API-key env var is missing."""


class LLMProvider(ABC):
    """Abstract provider. Implementations expose `name` and `model` for metadata
    sidecars, and a single `complete` method for actual generation."""

    name: str
    model: str

    @abstractmethod
    def complete(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        temperature: float = CODEGEN_TEMPERATURE,
        response_schema: dict | None = None,
    ) -> str:
        """Return the model's reply text.

        Args:
            messages: chat turns (user/assistant). System prompt is passed separately.
            system: optional system prompt / instruction.
            temperature: sampling temperature. Pick from the module-level constants.
            response_schema: optional JSON schema. If set, providers that support
                structured output should constrain the response to that schema.
                Providers that don't support it must still return a JSON string that
                can be parsed against the schema (best-effort).

        Returns:
            The model's response as a plain string. If `response_schema` is set, the
            string is JSON conforming to that schema.

        Raises:
            LLMError (or subclass) on any provider-side failure.
        """
        ...
