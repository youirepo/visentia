"""ContentClassifier: routes a Prompt into a Math Content Type + suggested artifact form.

In v0.1 the classifier returns one of three Math Content Types (Relationship / Procedure
/ Derivation) and one of two Modes (Quick / Deep). The `suggested_template_id` field is
always `None` in this slice because no curriculum templates exist yet — every Prompt
takes the freeform path. Templates land in slice #6 (Triangle3Side) and #10–#13.

The classifier asks Gemini for structured JSON via `response_schema`, so output shape is
constrained by the provider when supported.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from visentia.llm import (
    CLASSIFICATION_TEMPERATURE,
    LLMError,
    LLMProvider,
)

MathContentType = Literal["Relationship", "Procedure", "Derivation"]
Mode = Literal["Quick", "Deep"]


@dataclass(frozen=True)
class Classification:
    """Classifier output for one Prompt.

    `suggested_template_id` is `None` in v0.1 slice #4 (no templates registered yet).
    Slice #6 introduces `Triangle3Side`; from that point onward the classifier sets
    `suggested_template_id` when it matches.
    """

    math_content_type: MathContentType
    suggested_template_id: str | None
    suggested_mode: Mode


_CLASSIFIER_SYSTEM_PROMPT = """\
You are Visentia's math-content classifier. You read a Tutor's natural-language Prompt
about an NSW NESA Year 7-10 (Stage 4 + Stage 5) math concept and return a JSON
classification describing what kind of explanation best fits.

Classify into exactly one Math Content Type:

- "Relationship": prompts about *when* X is true, or *how* X depends on Y.
  Example: "How does the third side of a triangle determine whether the triangle is
  acute, right, or obtuse?" → Relationship.

- "Procedure": prompts about *how to do* X, or refresher-style "remind me how X works".
  Example: "How do I calculate a total amount given a rate, like apples at $5 per 100g
  for 4.5kg?" → Procedure.

- "Derivation": prompts about *why* X is true, or "show me where X comes from".
  Example: "Where does the rhombus area formula come from?" → Derivation.

Also pick a Mode:

- "Quick": short refresher / top-up artifact.
- "Deep": longer, thorough relearning.

Return JSON only. Do not include commentary, markdown, or backticks."""


_CLASSIFICATION_SCHEMA: dict = {
    "type": "OBJECT",
    "properties": {
        "math_content_type": {
            "type": "STRING",
            "enum": ["Relationship", "Procedure", "Derivation"],
        },
        "suggested_mode": {
            "type": "STRING",
            "enum": ["Quick", "Deep"],
        },
    },
    "required": ["math_content_type", "suggested_mode"],
}


class ClassifierError(LLMError):
    """Raised when the classifier cannot parse a usable classification from the LLM reply."""


class ContentClassifier:
    """Wraps an `LLMProvider` to produce structured `Classification` results."""

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def classify(self, prompt: str) -> Classification:
        user_message = (
            f"Prompt: {prompt.strip()}\n\n"
            "Return the JSON classification."
        )
        reply = self._provider.complete(
            messages=[{"role": "user", "content": user_message}],
            system=_CLASSIFIER_SYSTEM_PROMPT,
            temperature=CLASSIFICATION_TEMPERATURE,
            response_schema=_CLASSIFICATION_SCHEMA,
        )

        try:
            data = json.loads(reply)
        except json.JSONDecodeError as exc:
            raise ClassifierError(
                f"Classifier returned non-JSON reply: {reply!r}"
            ) from exc

        try:
            math_content_type = data["math_content_type"]
            suggested_mode = data["suggested_mode"]
        except KeyError as exc:
            raise ClassifierError(
                f"Classifier reply missing required field: {exc}. Raw reply: {data!r}"
            ) from exc

        if math_content_type not in ("Relationship", "Procedure", "Derivation"):
            raise ClassifierError(
                f"Classifier returned invalid Math Content Type: {math_content_type!r}"
            )
        if suggested_mode not in ("Quick", "Deep"):
            raise ClassifierError(
                f"Classifier returned invalid Mode: {suggested_mode!r}"
            )

        return Classification(
            math_content_type=math_content_type,
            suggested_template_id=None,
            suggested_mode=suggested_mode,
        )
