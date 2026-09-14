"""LLM provider abstraction.

The rest of Visentia talks to LLMs only through `LLMProvider`. Swapping providers is a one-import
change at the call site plus a new implementation in this package.

`Claude` is the provider the engine uses (issue #27: Sonnet 5 for classification and
parameter filling, Opus 5 for freeform codegen and narration). `Gemini` predates that
decision and is no longer wired into the orchestrator.
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
from visentia.llm.claude import (
    CHAT_MODEL,
    CODEGEN_MODEL,
    DEFAULT_MODEL,
    HIGH_EFFORT,
    LOW_EFFORT,
    Claude,
)
from visentia.llm.gemini import DEFAULT_GEMINI_MODEL, Gemini

__all__ = [
    "CHAT_MODEL",
    "CLASSIFICATION_TEMPERATURE",
    "CODEGEN_MODEL",
    "CODEGEN_TEMPERATURE",
    "Claude",
    "DEFAULT_MODEL",
    "HIGH_EFFORT",
    "LOW_EFFORT",
    "DEFAULT_GEMINI_MODEL",
    "Gemini",
    "LLMError",
    "LLMProvider",
    "Message",
    "MissingApiKeyError",
    "NARRATION_TEMPERATURE",
]
