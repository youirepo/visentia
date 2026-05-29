"""WorkedExample — rate × quantity with unit conversion and cancellation (EV-002)."""

from __future__ import annotations

from typing import ClassVar

from manim import (
    DOWN,
    GRAY,
    GREEN,
    LEFT,
    RED,
    TEAL,
    UP,
    WHITE,
    YELLOW,
    FadeIn,
    FadeOut,
    MathTex,
    Text,
    VGroup,
)
from manim_voiceover import VoiceoverScene

from visentia.scenes.layout import as_on_screen_text, place_in_band_below
from visentia.voiceover import VoiceoverSynthesizer


def _fmt_quantity(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


class WorkedExampleScene(VoiceoverScene):
    params: ClassVar[dict] = {
        "item_label": "Apples",
        "rate_numerator": 5.0,
        "currency_symbol": r"\$",
        "rate_denominator": 100.0,
        "rate_unit": "g",
        "quantity": 4.5,
        "quantity_unit": "kg",
        "unit_conversion_factor": 1000.0,
    }

    def construct(self) -> None:
        self.set_speech_service(
            VoiceoverSynthesizer.create_service(),
            create_subcaption=False,
        )
        p = self.params
        item = str(p["item_label"])
        rate_num = float(p["rate_numerator"])
        currency = str(p["currency_symbol"])
        rate_den = float(p["rate_denominator"])
        rate_unit = str(p["rate_unit"])
        quantity = float(p["quantity"])
        quantity_unit = str(p["quantity_unit"])
        factor = float(p["unit_conversion_factor"])

        quantity_converted = quantity * factor
        total_cost = (rate_num / rate_den) * quantity_converted

        header = as_on_screen_text(
            VGroup(
                Text("Rate conversion with unit cancellation", font_size=32),
                Text(
                    f"{item}: {currency}{rate_num:g} per {rate_den:g}{rate_unit} — "
                    f"find total for {quantity:g}{quantity_unit}",
                    font_size=22,
                    color=TEAL,
                ),
            ).arrange(DOWN, buff=0.25)
        ).to_edge(UP, buff=0.35)

        step_band: VGroup | None = None

        # --- Step 1: convert units ---
        convert_title = as_on_screen_text(
            Text("Step 1: Convert to matching units", font_size=26, color=TEAL)
        )
        convert_math = as_on_screen_text(
            MathTex(
                rf"{_fmt_quantity(quantity)}\,\text{{{quantity_unit}}}"
                rf" \times {factor:g} "
                rf"= {_fmt_quantity(quantity_converted)}\,\text{{{rate_unit}}}",
                font_size=34,
            )
        )
        step1 = VGroup(convert_title, convert_math).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place_in_band_below(header, step1, buff=0.45)

        with self.voiceover(
            text=(
                f"First match the units. The rate is per {rate_unit}, "
                f"so convert {_fmt_quantity(quantity)} {quantity_unit} to {rate_unit} "
                f"by multiplying by {factor:g}."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeIn(header), run_time=min(0.5, tracker.duration * 0.1))
            reveal = min(0.7, tracker.duration * 0.15)
            self.play(FadeIn(step1), run_time=reveal)
            self.wait(max(0.0, tracker.duration - reveal - min(0.5, tracker.duration * 0.1)))

        step_band = step1

        # --- Step 2: set up fraction multiplication ---
        setup_title = as_on_screen_text(
            Text("Step 2: Multiply rate by quantity", font_size=26, color=TEAL)
        )
        setup_math = as_on_screen_text(
            MathTex(
                rf"\frac{{{currency}{rate_num:g}}}{{{rate_den:g}\,\text{{{rate_unit}}}}}"
                rf" \times {_fmt_quantity(quantity_converted)}\,\text{{{rate_unit}}}",
                font_size=36,
            )
        )
        step2 = VGroup(setup_title, setup_math).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place_in_band_below(header, step2, buff=0.45)

        with self.voiceover(
            text=(
                f"Set up the calculation: {currency}{rate_num:g} per {rate_den:g} {rate_unit}, "
                f"times {_fmt_quantity(quantity_converted)} {rate_unit}."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeOut(step_band), run_time=min(0.3, tracker.duration * 0.1))
            reveal = min(0.7, tracker.duration * 0.15)
            self.play(FadeIn(step2), run_time=reveal)
            self.wait(max(0.0, tracker.duration - reveal - min(0.3, tracker.duration * 0.1)))

        step_band = step2

        # --- Step 3: cancel units ---
        cancel_title = as_on_screen_text(
            Text("Step 3: Cancel matching units", font_size=26, color=TEAL)
        )
        before_cancel = as_on_screen_text(
            MathTex(
                rf"\frac{{{currency}{rate_num:g}}}{{{rate_den:g}\,\text{{{rate_unit}}}}}"
                rf" \times {_fmt_quantity(quantity_converted)}\,\text{{{rate_unit}}}",
                font_size=34,
                color=WHITE,
            )
        )
        after_cancel = as_on_screen_text(
            MathTex(
                rf"\frac{{{currency}{rate_num:g}}}{{{rate_den:g}}}"
                rf" \times {_fmt_quantity(quantity_converted)}",
                font_size=36,
                color=GREEN,
            )
        )
        cancel_note = as_on_screen_text(
            Text(f"{rate_unit} cancels — only dollars remain", font_size=24, color=YELLOW)
        )
        step3 = VGroup(cancel_title, before_cancel, after_cancel, cancel_note).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        )
        place_in_band_below(header, step3, buff=0.4)

        with self.voiceover(
            text=(
                f"The {rate_unit} units cancel, just like crossing out units on paper. "
                "You are left with dollars times a plain number."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeOut(step_band), run_time=min(0.3, tracker.duration * 0.1))
            self.play(FadeIn(cancel_title), FadeIn(before_cancel), run_time=min(0.5, tracker.duration * 0.15))
            self.play(
                before_cancel.animate.set_color(GRAY),
                FadeIn(after_cancel),
                FadeIn(cancel_note),
                run_time=min(0.6, tracker.duration * 0.2),
            )
            self.wait(max(0.0, tracker.duration - min(1.1, tracker.duration * 0.45)))

        step_band = VGroup(cancel_title, after_cancel, cancel_note)

        # --- Step 4: compute ---
        compute_title = as_on_screen_text(
            Text("Step 4: Calculate", font_size=26, color=TEAL)
        )
        lots = quantity_converted / rate_den
        compute_lines = as_on_screen_text(
            VGroup(
                MathTex(
                    rf"{currency}{rate_num:g} \times {_fmt_quantity(lots)}"
                    rf" = {currency}{total_cost:g}",
                    font_size=38,
                    color=GREEN,
                ),
                MathTex(
                    rf"\text{{or}}\quad"
                    rf"\frac{{{currency}{rate_num:g}}}{{{rate_den:g}}} "
                    rf"\times {_fmt_quantity(quantity_converted)} "
                    rf"= {currency}{total_cost:g}",
                    font_size=30,
                ),
            ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        )
        step4 = VGroup(compute_title, compute_lines).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place_in_band_below(header, step4, buff=0.45)

        with self.voiceover(
            text=(
                f"{currency}{rate_num:g} times {_fmt_quantity(lots)} hundred-gram lots "
                f"is {currency}{total_cost:g}."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeOut(step_band), run_time=min(0.3, tracker.duration * 0.1))
            reveal = min(0.7, tracker.duration * 0.15)
            self.play(FadeIn(step4), run_time=reveal)
            self.wait(max(0.0, tracker.duration - reveal - min(0.3, tracker.duration * 0.1)))

        step_band = step4

        # --- Final answer (hold on screen) ---
        answer_title = as_on_screen_text(Text("Answer", font_size=28, color=TEAL))
        answer_math = as_on_screen_text(
            MathTex(
                rf"\text{{Total}} = {currency}{total_cost:g}",
                font_size=46,
                color=GREEN,
            )
        )
        answer_detail = as_on_screen_text(
            MathTex(
                rf"\frac{{{currency}{rate_num:g}}}{{{rate_den:g}\,\text{{{rate_unit}}}}}"
                rf" \times {_fmt_quantity(quantity_converted)}\,\text{{{rate_unit}}}"
                rf" = {currency}{total_cost:g}",
                font_size=32,
            )
        )
        final = VGroup(answer_title, answer_math, answer_detail).arrange(
            DOWN, buff=0.35, aligned_edge=LEFT
        )
        place_in_band_below(header, final, buff=0.45)

        with self.voiceover(
            text=f"The total cost is {currency}{total_cost:g}.",
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeOut(step_band), run_time=min(0.3, tracker.duration * 0.1))
            reveal = min(0.7, tracker.duration * 0.2)
            self.play(FadeIn(final), run_time=reveal)
            self.wait(max(0.5, tracker.duration - reveal - min(0.3, tracker.duration * 0.1)))

        step_band = final

        # --- General procedure (keep answer visible) ---
        rule_title = as_on_screen_text(Text("General procedure", font_size=26, color=TEAL))
        rule_text = as_on_screen_text(
            Text(
                "Match units, multiply rate × quantity so units cancel, then evaluate.",
                font_size=24,
                color=WHITE,
            )
        )
        answer_compact = as_on_screen_text(
            MathTex(
                rf"\text{{Total}} = {currency}{total_cost:g}",
                font_size=40,
                color=GREEN,
            )
        )
        step5 = VGroup(rule_title, rule_text, answer_compact).arrange(
            DOWN, buff=0.28, aligned_edge=LEFT
        )
        place_in_band_below(header, step5, buff=0.45)

        with self.voiceover(
            text=(
                "In general: convert so the rate denominator and quantity share the same unit, "
                "multiply, cancel the units, then calculate the total."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeOut(step_band), run_time=min(0.3, tracker.duration * 0.1))
            self.play(FadeIn(step5), run_time=min(0.6, tracker.duration * 0.2))
            self.wait(max(0.5, tracker.duration - min(0.9, tracker.duration * 0.3)))

        self.wait(1.0)
