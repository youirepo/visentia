"""LLM provider abstraction.

The rest of Visentia talks to LLMs only through `LLMProvider`. Swapping providers (Gemini
Flash GA → Claude Sonnet 4.5 → some future model) is a one-import change at the call site
plus a new implementation in this package.
"""

from visentia.llm.base import (
    CLASSIFICATION_TEMPERATURE,
    CODEGEN_TEMPERATURE,
    NARRATION_TEMPERATURE,
    LLMError,
    LLMProvider,
    Message,
    MissingApiKeyError,
)
from visentia.llm.gemini import DEFAULT_GEMINI_MODEL, Gemini

__all__ = [
    "CLASSIFICATION_TEMPERATURE",
    "CODEGEN_TEMPERATURE",
    "DEFAULT_GEMINI_MODEL",
    "Gemini",
    "LLMError",
    "LLMProvider",
    "Message",
    "MissingApiKeyError",
    "NARRATION_TEMPERATURE",
]
