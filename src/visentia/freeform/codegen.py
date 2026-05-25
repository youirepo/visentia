"""FreeformCodegen — LLM Manim source generation for the fallback path."""

from __future__ import annotations

import re

from visentia.classifier import MathContentType
from visentia.llm import CODEGEN_TEMPERATURE, LLMError, LLMProvider, Message

_CODEGEN_SYSTEM = """\
You are an expert in Manim Community Edition (Manim CE). Output exactly one Python file
and nothing else — no markdown fences, no commentary.

Requirements:
- Start with `from manim import *`
- Define exactly one Scene subclass with a `construct(self)` method
- Target NSW NESA Year 7-10 mathematics; keep runtime under ~60 seconds of animation
- Use only Manim CE APIs (no CYAN — use TEAL; no stroke_dash_array on Rectangle)
- Use raw strings for all MathTex/Tex/MarkupText LaTeX (prefix with r)
- Mathematically correct; clear step-by-step visuals for the Tutor
"""


class CodegenError(LLMError):
    """Raised when freeform codegen fails."""


class FreeformCodegen:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def generate(
        self,
        prompt: str,
        content_type: MathContentType,
        *,
        repair_context: str | None = None,
    ) -> str:
        """Return candidate Manim Python source for the Prompt."""

        user_parts = [
            f"Math content type: {content_type}",
            f"Tutor prompt: {prompt.strip()}",
            "Return the complete Python file.",
        ]
        if repair_context:
            user_parts.append(f"Repair context:\n{repair_context}")

        messages: list[Message] = [{"role": "user", "content": "\n\n".join(user_parts)}]

        try:
            reply = self._provider.complete(
                messages=messages,
                system=_CODEGEN_SYSTEM,
                temperature=CODEGEN_TEMPERATURE,
            )
        except LLMError:
            raise
        except Exception as exc:
            raise CodegenError(f"Codegen failed: {exc}") from exc

        return _strip_code_fences(reply)


def _strip_code_fences(text: str) -> str:
    """Keep only the Python file — models often wrap code in markdown or add a preamble."""

    stripped = text.strip()
    match = re.search(r"```(?:python)?\s*\n(.*?)```", stripped, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Opening fence without a closing fence (common with long generations).
    match = re.search(r"```(?:python)?\s*\n(.+)", stripped, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Prose before the file body — start at the Manim import.
    for marker in ("from manim import *", "from manim import"):
        idx = stripped.find(marker)
        if idx != -1:
            return stripped[idx:].strip()

    return stripped
