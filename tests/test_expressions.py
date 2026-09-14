"""Safe function expressions and curve-feature finding (issue #33).

These are the numerics the Stage 6 graph templates rest on: if a turning point is
misclassified or a pole is mistaken for a root, the template draws a confidently wrong
picture, which is exactly the failure mode the template library exists to prevent.
"""

from __future__ import annotations

import math

import pytest

from visentia.scenes.expressions import (
    ExpressionError,
    find_roots,
    find_turning_points,
    find_vertical_asymptotes,
    parse_function,
    suggested_y_range,
)


class TestParsing:
    def test_evaluates_a_polynomial(self):
        assert parse_function("x**2 - 4*x + 3").at(5) == pytest.approx(8.0)

    def test_caret_is_accepted_as_a_power(self):
        assert parse_function("x^2").at(3) == pytest.approx(9.0)

    def test_named_functions_and_constants(self):
        assert parse_function("sin(x) + pi").at(0) == pytest.approx(math.pi)
        assert parse_function("ln(e)").at(0) == pytest.approx(1.0)

    def test_derivative_matches_the_analytic_value(self):
        assert parse_function("x**3").derivative_at(2) == pytest.approx(12.0, rel=1e-4)

    @pytest.mark.parametrize(
        "source",
        [
            "__import__('os').system('ls')",
            "open('/etc/passwd')",
            "x.__class__",
            "[i for i in range(3)]",
            "lambda: 1",
            "y + 1",
            "x if x else 0",
            "x and 1",
        ],
    )
    def test_rejects_anything_off_the_whitelist(self, source):
        with pytest.raises(ExpressionError):
            parse_function(source)

    def test_rejects_an_empty_or_unparseable_expression(self):
        with pytest.raises(ExpressionError):
            parse_function("")
        with pytest.raises(ExpressionError):
            parse_function("x +")

    def test_rejects_an_expression_undefined_everywhere_sampled(self):
        with pytest.raises(ExpressionError):
            parse_function("ln(-1 - x**2)")


class TestLatex:
    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            ("x**2 - 4*x + 3", "x^{2} - 4x + 3"),
            ("-3*x**3 + 2", "-3x^{3} + 2"),
            ("x*exp(-x)", "xe^{-x}"),
            ("(x^2 - 1)/(x - 2)", r"\frac{x^{2} - 1}{x - 2}"),
            ("sqrt(x)", r"\sqrt{x}"),
            ("sin(2*x)", r"\sin\left(2x\right)"),
            ("x**(-2)", "x^{-2}"),
            ("(-x)**2", "(-x)^{2}"),
        ],
    )
    def test_renders_readable_latex(self, source, expected):
        assert parse_function(source).latex == expected


class TestFeatures:
    def test_finds_polynomial_roots(self):
        roots = find_roots(parse_function("x**2 - 4*x + 3"), -2, 6)
        assert [round(root.x, 6) for root in roots] == [1.0, 3.0]

    def test_classifies_a_minimum_that_lands_exactly_on_a_sample_point(self):
        """The vertex of y = x² - 4x + 3 sits at x = 2, which is a grid sample.

        The gradient there is exactly 0, which has no sign — classifying from the
        bracketing samples alone reads it as a maximum.
        """

        turning_points = find_turning_points(parse_function("x**2 - 4*x + 3"), -2, 6)
        assert [(tp.kind, round(tp.x, 6)) for tp in turning_points] == [("minimum", 2.0)]

    def test_classifies_both_turning_points_of_a_cubic(self):
        turning_points = find_turning_points(parse_function("x**3 - 3*x"), -3, 3)
        assert [(tp.kind, round(tp.x, 4)) for tp in turning_points] == [
            ("maximum", -1.0),
            ("minimum", 1.0),
        ]

    def test_a_pole_is_not_reported_as_a_root(self):
        """1/(x-2) changes sign at x = 2 without ever being zero."""

        assert find_roots(parse_function("1/(x - 2)"), -4, 6) == []

    def test_finds_a_vertical_asymptote_once(self):
        asymptotes = find_vertical_asymptotes(parse_function("1/(x - 2)"), -4, 6)
        assert len(asymptotes) == 1
        assert asymptotes[0].x == pytest.approx(2.0, abs=0.05)

    def test_y_range_ignores_the_pole_instead_of_flattening_the_curve(self):
        low, high = suggested_y_range(parse_function("1/(x - 2)"), -4, 6)
        assert -20 < low < 0 < high < 20

    def test_y_range_frames_a_parabola(self):
        low, high = suggested_y_range(parse_function("x**2 - 4*x + 3"), -2, 6)
        assert low < -1.0
        assert high > 8.0
