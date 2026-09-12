"""Safe function expressions in one variable, for the Stage 6 graph templates (issue #33).

Stage 6 functions-and-calculus templates need to accept *a function* as a parameter. A
typed coefficient spec (``{"kind": "polynomial", "coefficients": [...]}``) is too narrow —
it cannot express ``x*exp(-x)``, which is ordinary product-rule material — and free-form
Python is the thing templates exist to avoid.

The middle ground is an expression string in ``x``, parsed to a Python AST and accepted
only if every node is on a whitelist. Nothing is ``eval``'d that has not been walked node
by node: no attribute access, no calls except the named functions below, no names except
``x`` and two constants.

The module is deliberately Manim-free so the numerics can be tested without rendering.
"""

from __future__ import annotations

import ast
import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

DERIVATIVE_STEP = 1e-6
"""Central-difference step for numeric differentiation.

Stage 6 curves are smooth on the plotted band, and a tangent drawn from a slope accurate
to ~1e-9 is pixel-identical to one drawn from an exact derivative. Symbolic
differentiation would mean either a dependency (sympy is not in the Manim-pinned
requirements) or a second evaluator to maintain.
"""

_FUNCTIONS: dict[str, Callable] = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "exp": np.exp,
    "ln": np.log,
    "log": np.log,
    "log10": np.log10,
    "sqrt": np.sqrt,
    "abs": np.abs,
}

_CONSTANTS: dict[str, float] = {"pi": math.pi, "e": math.e}

_LATEX_FUNCTIONS = {
    "sin": r"\sin",
    "cos": r"\cos",
    "tan": r"\tan",
    "asin": r"\sin^{-1}",
    "acos": r"\cos^{-1}",
    "atan": r"\tan^{-1}",
    "sinh": r"\sinh",
    "cosh": r"\cosh",
    "tanh": r"\tanh",
    "exp": r"\exp",
    "ln": r"\ln",
    "log": r"\ln",
    "log10": r"\log_{10}",
}

VARIABLE = "x"


class ExpressionError(ValueError):
    """Raised when an expression is unparseable, uses a disallowed construct, or is unusable."""


@dataclass(frozen=True)
class Function:
    """A validated one-variable function: callable, printable, differentiable."""

    source: str
    latex: str
    _callable: Callable[[np.ndarray], np.ndarray]

    def __call__(self, x):
        with np.errstate(all="ignore"):
            return self._callable(np.asarray(x, dtype=float))

    def at(self, x: float) -> float:
        """Evaluate at a single point, as a plain float."""

        return float(np.asarray(self(float(x))).item())

    def derivative_at(self, x: float, *, step: float = DERIVATIVE_STEP) -> float:
        """Central-difference derivative at `x`."""

        return (self.at(x + step) - self.at(x - step)) / (2.0 * step)

    def is_finite_at(self, x: float) -> bool:
        try:
            return bool(np.isfinite(self.at(x)))
        except (ValueError, ZeroDivisionError, OverflowError):
            return False


def parse_function(source: str) -> Function:
    """Parse `source` into a `Function`, or raise `ExpressionError`.

    Accepts ``+ - * / **``, unary minus, numeric literals, the variable ``x``, the
    constants ``pi`` and ``e``, and the functions in `_FUNCTIONS`. Also accepts the
    caret (``^``) as a power operator, since that is how a Tutor — and an LLM filling
    the parameter — will usually write it.
    """

    text = str(source).strip()
    if not text:
        raise ExpressionError("Expression is empty.")
    if len(text) > 200:
        raise ExpressionError("Expression is too long (max 200 characters).")

    normalised = text.replace("^", "**")

    try:
        tree = ast.parse(normalised, mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"Could not parse expression {text!r}: {exc.msg}") from exc

    _reject_disallowed_nodes(tree)

    code = compile(tree, filename="<expression>", mode="eval")
    namespace = {"__builtins__": {}, **_FUNCTIONS, **_CONSTANTS}

    def evaluate(x: np.ndarray) -> np.ndarray:
        return eval(code, namespace, {VARIABLE: x})  # noqa: S307 — AST whitelisted above

    function = Function(source=text, latex=to_latex(tree), _callable=evaluate)
    _probe(function, text)
    return function


def _reject_disallowed_nodes(tree: ast.Expression) -> None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Expression, ast.Load)):
            continue
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)) or isinstance(node.value, bool):
                raise ExpressionError(f"Only numeric literals are allowed, got {node.value!r}.")
            continue
        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                raise ExpressionError(
                    f"Operator {type(node.op).__name__} is not allowed in an expression."
                )
            continue
        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, (ast.UAdd, ast.USub)):
                raise ExpressionError("Only unary + and - are allowed.")
            continue
        if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.UAdd, ast.USub)):
            continue
        if isinstance(node, ast.Name):
            if node.id != VARIABLE and node.id not in _CONSTANTS and node.id not in _FUNCTIONS:
                raise ExpressionError(
                    f"Unknown name {node.id!r}. Use {VARIABLE!r}, a number, "
                    f"or one of: {', '.join(sorted(_FUNCTIONS))}."
                )
            continue
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _FUNCTIONS:
                raise ExpressionError(
                    f"Only these functions may be called: {', '.join(sorted(_FUNCTIONS))}."
                )
            if len(node.args) != 1 or node.keywords:
                raise ExpressionError(
                    f"{node.func.id}() takes exactly one argument and no keywords."
                )
            continue
        raise ExpressionError(
            f"{type(node).__name__} is not allowed in a function expression."
        )


def _probe(function: Function, text: str) -> None:
    """Reject an expression that evaluates to nothing usable anywhere sensible."""

    sample = np.linspace(-4.0, 4.0, 33)
    try:
        values = np.asarray(function(sample), dtype=float)
    except Exception as exc:  # noqa: BLE001 — any evaluation failure is a bad expression
        raise ExpressionError(f"Expression {text!r} could not be evaluated: {exc}") from exc

    if values.shape != sample.shape:
        # A constant expression broadcasts to a scalar; that is legitimate (y = 3).
        values = np.broadcast_to(values, sample.shape)
    if not np.any(np.isfinite(values)):
        raise ExpressionError(f"Expression {text!r} is undefined everywhere it was sampled.")


def to_latex(tree: ast.Expression | ast.AST) -> str:
    """Render a whitelisted expression AST as LaTeX, for on-screen labels."""

    node = tree.body if isinstance(tree, ast.Expression) else tree
    return _latex(node, parent_precedence=0)


_PRECEDENCE = {ast.Add: 1, ast.Sub: 1, ast.Mult: 2, ast.Div: 2, ast.Pow: 4}


def _latex(node: ast.AST, *, parent_precedence: int) -> str:
    if isinstance(node, ast.Constant):
        return _number(node.value)

    if isinstance(node, ast.Name):
        if node.id == "pi":
            return r"\pi"
        return node.id

    if isinstance(node, ast.UnaryOp):
        inner = _latex(node.operand, parent_precedence=3)
        rendered = f"-{inner}" if isinstance(node.op, ast.USub) else inner
        # A leading minus needs brackets only where it would bind wrongly: as the right
        # operand of a product, or as the base of a power. "-3x" reads fine; "2 \\cdot (-x)"
        # and "(-x)^{2}" do not.
        return f"({rendered})" if parent_precedence >= 3 else rendered

    if isinstance(node, ast.Call):
        argument = _latex(node.args[0], parent_precedence=0)
        name = node.func.id  # type: ignore[union-attr]
        if name == "sqrt":
            return rf"\sqrt{{{argument}}}"
        if name == "abs":
            return rf"\left|{argument}\right|"
        if name == "exp":
            return rf"e^{{{argument}}}"
        return rf"{_LATEX_FUNCTIONS.get(name, rf'\operatorname{{{name}}}')}\left({argument}\right)"

    if isinstance(node, ast.BinOp):
        precedence = _PRECEDENCE[type(node.op)]

        if isinstance(node.op, ast.Div):
            numerator = _latex(node.left, parent_precedence=0)
            denominator = _latex(node.right, parent_precedence=0)
            return rf"\frac{{{numerator}}}{{{denominator}}}"

        if isinstance(node.op, ast.Pow):
            base = _latex(node.left, parent_precedence=5)
            exponent = _latex(node.right, parent_precedence=0)
            return f"{base}^{{{exponent}}}"

        left = _latex(node.left, parent_precedence=precedence)
        right = _latex(node.right, parent_precedence=precedence + 1)

        if isinstance(node.op, ast.Add):
            # "3 + -x" is how the AST reads; "3 - x" is how a Stage 6 student writes it.
            if isinstance(node.right, ast.UnaryOp) and isinstance(node.right.op, ast.USub):
                rendered = f"{left} - {_latex(node.right.operand, parent_precedence=2)}"
            else:
                rendered = f"{left} + {right}"
        elif isinstance(node.op, ast.Sub):
            rendered = f"{left} - {right}"
        else:
            rendered = _multiplication(node, left, right)

        return f"({rendered})" if parent_precedence > precedence else rendered

    raise ExpressionError(f"Cannot render {type(node).__name__} as LaTeX.")


def _multiplication(node: ast.BinOp, left: str, right: str) -> str:
    """Use implicit multiplication where a reader would, an explicit dot where they wouldn't."""

    # An explicit dot is only needed when the right factor opens with a digit, where
    # juxtaposition would read as one number: "2 \cdot 3", "x \cdot 2". Everywhere else
    # ("3x", "-3x^{2}", "xe^{-x}") implicit multiplication is what a reader expects.
    del node
    if right[:1].isdigit():
        return rf"{left} \cdot {right}"
    return f"{left}{right}"


def _number(value: float) -> str:
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{float(value):g}"


# ---------------------------------------------------------------------------
# Feature finding
#
# The templates let a beat *declare* a feature ("the turning point is at x = 2") or ask
# for it to be found. Declared values are what a Tutor or the syllabus would state;
# found values keep a beat honest when nobody declares one. Both end up as the same
# `Feature`, so the scenes do not care which happened.
# ---------------------------------------------------------------------------

FEATURE_SAMPLES = 801
"""Grid resolution for feature scans. Fine enough to separate Stage 6 turning points."""

_POLE_MAGNITUDE = 1e3


@dataclass(frozen=True)
class Feature:
    """A named point of interest on a curve."""

    kind: str
    x: float
    y: float

    @property
    def is_turning_point(self) -> bool:
        return self.kind in ("maximum", "minimum")


def sample_curve(
    function: Function, x_min: float, x_max: float, *, samples: int = FEATURE_SAMPLES
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate `function` across `[x_min, x_max]`, with non-finite values as NaN."""

    xs = np.linspace(float(x_min), float(x_max), int(samples))
    with np.errstate(all="ignore"):
        ys = np.asarray(function(xs), dtype=float)
    if ys.shape != xs.shape:
        ys = np.broadcast_to(ys, xs.shape).astype(float)
    return xs, np.where(np.isfinite(ys), ys, np.nan)


def _bisect(predicate_value: Callable[[float], float], low: float, high: float) -> float:
    """Bisect for a sign change of `predicate_value` between `low` and `high`."""

    f_low = predicate_value(low)
    for _ in range(60):
        middle = (low + high) / 2.0
        f_middle = predicate_value(middle)
        if not math.isfinite(f_middle):
            return middle
        if (f_low < 0) != (f_middle < 0):
            high = middle
        else:
            low, f_low = middle, f_middle
    return (low + high) / 2.0


def find_roots(function: Function, x_min: float, x_max: float) -> list[Feature]:
    """x-intercepts in `[x_min, x_max]`, poles excluded."""

    xs, ys = sample_curve(function, x_min, x_max)
    roots: list[Feature] = []

    for index in range(len(xs) - 1):
        left, right = ys[index], ys[index + 1]
        if math.isnan(left) or math.isnan(right):
            continue
        if left == 0.0:
            roots.append(Feature("root", float(xs[index]), 0.0))
            continue
        if (left < 0) == (right < 0):
            continue

        crossing = _bisect(function.at, float(xs[index]), float(xs[index + 1]))
        # A sign change across a vertical asymptote is not a root: the curve leaves the
        # frame on one side and returns on the other without ever taking the value zero.
        if abs(function.at(crossing)) > 1e-3:
            continue
        roots.append(Feature("root", crossing, 0.0))

    return _deduplicate(roots)


def find_turning_points(function: Function, x_min: float, x_max: float) -> list[Feature]:
    """Stationary points in `[x_min, x_max]`, classified as maximum or minimum."""

    xs, _ = sample_curve(function, x_min, x_max)
    gradients = np.array([_safe_gradient(function, float(x)) for x in xs])
    turning_points: list[Feature] = []

    for index in range(len(xs) - 1):
        left, right = gradients[index], gradients[index + 1]
        if math.isnan(left) or math.isnan(right) or (left < 0) == (right < 0):
            continue

        stationary = _bisect(
            lambda value: _safe_gradient(function, value), float(xs[index]), float(xs[index + 1])
        )
        y = function.at(stationary)
        if not math.isfinite(y) or abs(y) > _POLE_MAGNITUDE:
            continue

        # Classify from a step either side of the located point rather than from the
        # bracketing grid samples: a stationary point that lands exactly on a sample makes
        # one bracket read as gradient zero, which has no sign.
        step = float(xs[1] - xs[0]) / 4.0
        before = _safe_gradient(function, stationary - step)
        after = _safe_gradient(function, stationary + step)
        if math.isnan(before) or math.isnan(after):
            continue

        # Falling-then-rising is a minimum; rising-then-falling is a maximum.
        kind = "minimum" if before < 0 < after else "maximum"
        turning_points.append(Feature(kind, stationary, y))

    return _deduplicate(turning_points)


def find_vertical_asymptotes(function: Function, x_min: float, x_max: float) -> list[Feature]:
    """x-values in `[x_min, x_max]` where the curve blows up or is undefined."""

    xs, ys = sample_curve(function, x_min, x_max)
    asymptotes: list[Feature] = []

    for index in range(len(xs) - 1):
        left, right = ys[index], ys[index + 1]
        blows_up = (
            (math.isnan(left) != math.isnan(right))
            or (
                not math.isnan(left)
                and not math.isnan(right)
                and (left < 0) != (right < 0)
                and abs(left) > _POLE_MAGNITUDE
                and abs(right) > _POLE_MAGNITUDE
            )
        )
        if not blows_up:
            continue
        asymptotes.append(
            Feature("asymptote", (float(xs[index]) + float(xs[index + 1])) / 2.0, math.nan)
        )

    # One pole shows up twice — once where the curve goes undefined, once where it comes
    # back — so merge anything closer together than the scan grid.
    return _deduplicate(asymptotes, tolerance=float(xs[1] - xs[0]) * 4.0)


def _safe_gradient(function: Function, x: float) -> float:
    try:
        gradient = function.derivative_at(x)
    except (ValueError, ZeroDivisionError, OverflowError):
        return math.nan
    return gradient if math.isfinite(gradient) else math.nan


def _deduplicate(features: list[Feature], *, tolerance: float = 1e-4) -> list[Feature]:
    unique: list[Feature] = []
    for feature in sorted(features, key=lambda item: item.x):
        if unique and abs(unique[-1].x - feature.x) < tolerance:
            continue
        unique.append(feature)
    return unique


def suggested_y_range(
    function: Function, x_min: float, x_max: float, *, padding: float = 0.15
) -> tuple[float, float]:
    """A y-window that frames the interesting part of the curve rather than its poles.

    A single vertical asymptote would otherwise set the window to millions and flatten
    the curve to a horizontal line, which is the most common way an auto-scaled Manim
    graph becomes useless. Outer percentiles are trimmed to keep the visible band.
    """

    _, ys = sample_curve(function, x_min, x_max)
    finite = ys[np.isfinite(ys)]
    if finite.size == 0:
        return (-5.0, 5.0)

    low = float(np.percentile(finite, 2))
    high = float(np.percentile(finite, 98))

    # Trimming can cut off the very features the video is about — the turning points of a
    # steep polynomial sit inside the trimmed tail. Expand (never contract) to include them.
    feature_values = [
        feature.y
        for feature in find_turning_points(function, x_min, x_max)
        if math.isfinite(feature.y)
    ]
    if find_roots(function, x_min, x_max):
        feature_values.append(0.0)
    if feature_values:
        low = min(low, min(feature_values))
        high = max(high, max(feature_values))

    if high - low < 1e-6:
        low, high = low - 1.0, high + 1.0

    margin = (high - low) * padding
    return (low - margin, high + margin)
