"""Placeholder Manim Scene used by the spine slice.

This Scene exists only to prove the architectural skeleton connects end-to-end. It
ignores the Prompt entirely and renders a fixed animation: a blue circle is created,
then shifted right, with a single voiceover cue narrating both moves.

Adapted from prototype/smoke.py, which served the same purpose during the feasibility
probe. Slice #3 added voiceover via `manim-voiceover` + `edge-tts`. Subsequent slices
replace this Scene with classifier-driven template renders.
"""

from manim import BLUE, RIGHT, Circle, Create
from manim_voiceover import VoiceoverScene

from visentia.voiceover import VoiceoverSynthesizer

_PLACEHOLDER_NARRATION = (
    "Visentia is alive. This is a placeholder render. "
    "Future slices will replace it with a real Explainer Artifact."
)


class SpineScene(VoiceoverScene):
    def construct(self) -> None:
        self.set_speech_service(VoiceoverSynthesizer.create_service())

        circle = Circle(color=BLUE).set_fill(BLUE, opacity=0.5)

        with self.voiceover(text=_PLACEHOLDER_NARRATION) as tracker:
            half = tracker.duration / 2
            self.play(Create(circle), run_time=half)
            self.play(circle.animate.shift(RIGHT * 2), run_time=half)
