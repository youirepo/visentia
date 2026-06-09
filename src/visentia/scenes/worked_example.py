"""WorkedExample — rate × quantity with unit conversion and cancellation (EV-002)."""

from __future__ import annotations

from typing import ClassVar

from manim import (
    DOWN,
    GRAY,
    GREEN,
    LEFT,
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

from visentia.scenes.layout import as_on_screen_text, fit_in_vertical_band, place_in_band_below
from visentia.voiceover import VoiceoverSynthesizer


def _fmt_quantity(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


def _tex_money(amount: float) -> str:
    """Dollar amounts in MathTex — bare ``$`` breaks LaTeX (``align*`` ends early)."""

    return rf"\text{{\$}}{amount:g}"


def _tex_frac_rate(rate_num: float, rate_den: float, rate_unit: str) -> str:
    return rf"\frac{{{_tex_money(rate_num)}}}{{{rate_den:g}\,\text{{{rate_unit}}}}}"


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
                    f"{item}: ${_fmt_quantity(rate_num)} per {_fmt_quantity(rate_den)}{rate_unit} — "
                    f"find total for {_fmt_quantity(quantity)}{quantity_unit}",
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
                font_size=36,
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
                _tex_frac_rate(rate_num, rate_den, rate_unit)
                + rf" \times {_fmt_quantity(quantity_converted)}\,\text{{{rate_unit}}}",
                font_size=38,
            )
        )
        step2 = VGroup(setup_title, setup_math).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place_in_band_below(header, step2, buff=0.45)

        with self.voiceover(
            text=(
                f"Set up the calculation: ${_fmt_quantity(rate_num)} per "
                f"{_fmt_quantity(rate_den)} {rate_unit}, "
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
                _tex_frac_rate(rate_num, rate_den, rate_unit)
                + rf" \times {_fmt_quantity(quantity_converted)}\,\text{{{rate_unit}}}",
                font_size=36,
                color=WHITE,
            )
        )
        after_cancel = as_on_screen_text(
            MathTex(
                rf"\frac{{{_tex_money(rate_num)}}}{{{rate_den:g}}}"
                + rf" \times {_fmt_quantity(quantity_converted)}",
                font_size=38,
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

        step_band = VGroup(cancel_title, before_cancel, after_cancel, cancel_note)

        # --- Step 4: compute ---
        compute_title = as_on_screen_text(
            Text("Step 4: Calculate", font_size=26, color=TEAL)
        )
        lots = quantity_converted / rate_den
        compute_lines = as_on_screen_text(
            VGroup(
                MathTex(
                    rf"{_tex_money(rate_num)} \times {_fmt_quantity(lots)}"
                    rf" = {_tex_money(total_cost)}",
                    font_size=40,
                    color=GREEN,
                ),
                MathTex(
                    rf"\text{{or}}\quad"
                    rf"\frac{{{_tex_money(rate_num)}}}{{{rate_den:g}}} "
                    rf"\times {_fmt_quantity(quantity_converted)} "
                    rf"= {_tex_money(total_cost)}",
                    font_size=32,
                ),
            ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        )
        step4 = VGroup(compute_title, compute_lines).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place_in_band_below(header, step4, buff=0.45)

        with self.voiceover(
            text=(
                f"${_fmt_quantity(rate_num)} times {_fmt_quantity(lots)} hundred-gram lots "
                f"is ${_fmt_quantity(total_cost)}."
            ),
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeOut(step_band), run_time=min(0.3, tracker.duration * 0.1))
            reveal = min(0.7, tracker.duration * 0.15)
            self.play(FadeIn(step4), run_time=reveal)
            self.wait(max(0.0, tracker.duration - reveal - min(0.3, tracker.duration * 0.1)))

        step_band = step4

        # --- Final answer (hold on screen) ---
        answer_title = as_on_screen_text(Text("Answer", font_size=30, color=TEAL))
        answer_math = as_on_screen_text(
            MathTex(
                rf"\text{{Total}} = {_tex_money(total_cost)}",
                font_size=52,
                color=GREEN,
            )
        )
        answer_detail = as_on_screen_text(
            MathTex(
                _tex_frac_rate(rate_num, rate_den, rate_unit)
                + rf" \times {_fmt_quantity(quantity_converted)}\,\text{{{rate_unit}}}"
                + rf" = {_tex_money(total_cost)}",
                font_size=34,
            )
        )
        final = VGroup(answer_title, answer_math, answer_detail).arrange(
            DOWN, buff=0.35, aligned_edge=LEFT
        )
        place_in_band_below(header, final, buff=0.45)

        with self.voiceover(
            text=f"The total cost is ${_fmt_quantity(total_cost)}.",
            subcaption_buff=0,
        ) as tracker:
            self.play(FadeOut(step_band), run_time=min(0.3, tracker.duration * 0.1))
            reveal = min(0.7, tracker.duration * 0.2)
            self.play(FadeIn(final), run_time=reveal)
            self.wait(max(1.0, tracker.duration - reveal - min(0.3, tracker.duration * 0.1)))

        self.wait(1.5)
