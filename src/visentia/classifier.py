"""ContentClassifier: routes a Prompt into a Math Content Type + suggested artifact form.

The classifier returns one of three Math Content Types (Relationship / Procedure /
Derivation), one of two Modes (Quick / Deep), and an optional `suggested_template_id`
when a registered curriculum template fits the Prompt. Slice #6 introduced
`Triangle3Side` for the converse of Pythagoras / classifying triangles from side lengths.

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

    `suggested_template_id` is `None` when no template matches; otherwise the template id
    string (e.g. `"Triangle3Side"`).
    """

    math_content_type: MathContentType
    suggested_template_id: str | None
    suggested_mode: Mode


_CLASSIFIER_SYSTEM_PROMPT = """\
You are Visentia's math-content classifier. You read a Tutor's natural-language Prompt
about an NSW NESA mathematics concept and return a JSON classification describing what
kind of explanation best fits.

The prototype's scope is NESA **Stage 6** (Years 11-12) Mathematics, functions and
calculus. The Year 7-10 templates below remain registered from the earlier scope and are
still valid when a Prompt clearly asks for that material.

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

If the Prompt matches a registered template, set `suggested_template_id` to that id;
otherwise use "none".

Registered templates:

- "Triangle3Side": classifying a triangle as acute, right, or obtuse from three given
  side lengths; converse of Pythagoras; comparing c² with a²+b² where c is the longest.

- "WorkedExample": calculating a total from a rate (price per unit) when units must be
  converted first — e.g. cost per 100g for a quantity in kg; procedure with unit cancellation.

- "AreaTransform": deriving area formulas by cut-and-rearrange motion — rhombus from diagonals,
  trapezium by duplicating and rotating; Year 8 area derivations.

- "FunctionGraph": Stage 6 curve sketching — what a function looks like and why. Sketching
  y = f(x), intercepts, turning points and their classification, vertical asymptotes,
  transformations (shifts, stretches, reflections), and comparing two curves on one set of
  axes. Prefer this whenever the Prompt is about the *shape* of a graph.

- "CalculusOnCurve": Stage 6 calculus on a graph — differentiation from first principles
  (a secant shrinking onto a tangent), the tangent and gradient at a point, the derivative
  plotted as its own function, the area under a curve as a limit of rectangles, the
  definite integral, and limits. Prefer this whenever the Prompt is about *rates of change
  or accumulation* on a curve, rather than the curve's shape.

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
        "suggested_template_id": {
            "type": "STRING",
            "enum": [
                "Triangle3Side",
                "WorkedExample",
                "AreaTransform",
                "FunctionGraph",
                "CalculusOnCurve",
                "none",
            ],
        },
    },
    "required": ["math_content_type", "suggested_mode", "suggested_template_id"],
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
            raw_template = data["suggested_template_id"]
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
        if raw_template not in (
            "Triangle3Side",
            "WorkedExample",
            "AreaTransform",
            "FunctionGraph",
            "CalculusOnCurve",
            "none",
        ):
            raise ClassifierError(
                f"Classifier returned invalid template id: {raw_template!r}"
            )

        suggested_template_id = None if raw_template == "none" else raw_template

        return Classification(
            math_content_type=math_content_type,
            suggested_template_id=suggested_template_id,
            suggested_mode=suggested_mode,
        )
