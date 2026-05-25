"""StaticLinter — AST checks for LLM-generated Manim (ADR-0003 layer 1)."""

from __future__ import annotations

import ast
import builtins
import re
import tokenize
from dataclasses import dataclass
from io import BytesIO
from typing import Literal

from visentia.freeform.api_model import LATEX_MOBS, SCENE_BASES, load_api_model

LintCode = Literal[
    "missing_import",
    "missing_scene",
    "unknown_symbol",
    "invalid_kwarg",
    "missing_raw_string",
    "syntax_error",
]


@dataclass(frozen=True)
class LintError:
    code: LintCode
    message: str
    line: int | None = None


@dataclass(frozen=True)
class LintOk:
    scene_class_name: str


LintResult = LintOk | list[LintError]


class StaticLinter:
    """Pure-function linter for freeform Manim Python source."""

    def lint(self, python_source: str) -> LintResult:
        try:
            tree = ast.parse(python_source)
        except SyntaxError as exc:
            return [LintError(code="syntax_error", message=_syntax_error_message(exc))]

        symbols, class_kwargs = load_api_model()
        errors: list[LintError] = []

        if not _has_manim_import(tree):
            errors.append(
                LintError(
                    code="missing_import",
                    message="Generated code must start with `from manim import *` (or equivalent imports for every Manim symbol used).",
                    line=1,
                )
            )

        scene_name = _find_scene_class(tree)
        if scene_name is None:
            errors.append(
                LintError(
                    code="missing_scene",
                    message="Generated code must define a Scene subclass with a `construct(self)` method.",
                )
            )

        imported = _manim_imported_names(tree, symbols)
        scope = _NameScope(tree, imported)

        for err in _check_calls(tree, scope, symbols, class_kwargs):
            errors.append(err)

        for err in _check_name_references(tree, scope, symbols):
            errors.append(err)

        for err in _check_latex_strings(tree, python_source):
            errors.append(err)

        if errors:
            return _dedupe_errors(errors)
        assert scene_name is not None
        return LintOk(scene_class_name=scene_name)

    @staticmethod
    def plain_language_summary(result: list[LintError]) -> str:
        """Tutor-safe summary — no tracebacks."""

        if not result:
            return "Generated code failed validation."
        if len(result) == 1:
            return result[0].message
        bullets = "\n".join(f"- {e.message}" for e in result[:5])
        extra = "" if len(result) <= 5 else f"\n- …and {len(result) - 5} more issue(s)."
        return "Generated code has several problems:\n" + bullets + extra


def _dedupe_errors(errors: list[LintError]) -> list[LintError]:
    seen: set[tuple[str, str, int | None]] = set()
    out: list[LintError] = []
    for err in errors:
        key = (err.code, err.message, err.line)
        if key in seen:
            continue
        seen.add(key)
        out.append(err)
    return out


def _syntax_error_message(exc: SyntaxError) -> str:
    line_part = f" on line {exc.lineno}" if exc.lineno else ""
    near = ""
    if exc.text:
        near = f" Problematic line: {exc.text.strip()!r}."
    return (
        f"Generated code has a Python syntax error{line_part}: {exc.msg}.{near} "
        "Visentia stopped before running Manim. Try the Prompt again, or rephrase it."
    )


def _has_manim_import(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "manim":
            if node.names and node.names[0].name == "*":
                return True
            # explicit imports count if non-empty
            if node.names:
                return True
    return False


def _manim_imported_names(tree: ast.Module, symbols: frozenset[str]) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "manim":
            for alias in node.names:
                if alias.name == "*":
                    return set(symbols)
                names.add(alias.asname or alias.name)
    return names


def _find_scene_class(tree: ast.Module) -> str | None:
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(isinstance(base, ast.Name) and base.id in SCENE_BASES for base in node.bases):
            continue
        has_construct = any(
            isinstance(item, ast.FunctionDef) and item.name == "construct"
            for item in node.body
        )
        if has_construct:
            return node.name
    return None


class _NameScope:
    """Track locally assigned names per function/class scope."""

    def __init__(self, tree: ast.Module, manim_imports: set[str]) -> None:
        self._builtin = set(dir(builtins))
        self._manim = manim_imports
        self._locals: set[str] = set()
        self._collect_defs(tree)

    def _collect_defs(self, node: ast.AST) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                self._locals.add(child.id)
            elif isinstance(child, ast.FunctionDef):
                self._locals.add(child.name)
            elif isinstance(child, ast.ClassDef):
                self._locals.add(child.name)

    def is_known(self, name: str) -> bool:
        return name in self._locals or name in self._manim or name in self._builtin


def _check_name_references(
    tree: ast.Module,
    scope: _NameScope,
    symbols: frozenset[str],
) -> list[LintError]:
    seen: set[str] = set()
    errors: list[LintError] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name) or not isinstance(node.ctx, ast.Load):
            continue
        name = node.id
        if name in ("self", "cls"):
            continue
        if scope.is_known(name) or name in symbols or name in seen:
            continue
        seen.add(name)
        errors.append(
            LintError(
                code="unknown_symbol",
                message=(
                    f"Generated code uses `{name}`, which is not part of Manim Community Edition. "
                    f"Check the Manim docs or use a supported name (e.g. `TEAL` instead of `CYAN`)."
                ),
                line=node.lineno,
            )
        )
    return errors


def _check_calls(
    tree: ast.Module,
    scope: _NameScope,
    symbols: frozenset[str],
    class_kwargs: dict[str, frozenset[str]],
) -> list[LintError]:
    errors: list[LintError] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name = _call_name(node.func)
        if func_name is None:
            continue

        if func_name in class_kwargs:
            allowed = class_kwargs[func_name]
            for kw in node.keywords:
                if kw.arg is None:
                    continue
                if kw.arg not in allowed:
                    errors.append(
                        LintError(
                            code="invalid_kwarg",
                            message=(
                                f"`{func_name}()` does not accept the keyword `{kw.arg}` in Manim CE. "
                                f"Use supported parameters or wrap with `DashedVMobject` for dashed outlines."
                            ),
                            line=kw.lineno,
                        )
                    )
    return errors


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _check_latex_strings(tree: ast.Module, source: str) -> list[LintError]:
    errors: list[LintError] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name = _call_name(node.func)
        if func_name not in LATEX_MOBS:
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if _string_has_escape_artifacts(arg.value):
                    errors.append(
                        LintError(
                            code="missing_raw_string",
                            message=(
                                f"`{func_name}(...)` needs a raw string for LaTeX (prefix the string with `r`). "
                                f"Backslash sequences like `\\text` were interpreted as Python escapes."
                            ),
                            line=arg.lineno,
                        )
                    )
        for kw in node.keywords:
            if kw.arg in ("tex_string", "tex_strings", "text") and isinstance(kw.value, ast.Constant):
                if isinstance(kw.value.value, str) and _string_has_escape_artifacts(kw.value.value):
                    errors.append(
                        LintError(
                            code="missing_raw_string",
                            message=(
                                f"`{func_name}(...)` needs a raw string for LaTeX (prefix the string with `r`). "
                                f"Backslash sequences like `\\text` were interpreted as Python escapes."
                            ),
                            line=kw.value.lineno,
                        )
                    )

    # Source-level: literal \t \n in non-raw strings passed to latex mobs
    for err in _tokenize_latex_strings(source):
        errors.append(err)

    return errors


def _string_has_escape_artifacts(value: str) -> bool:
    return any(ch in value for ch in ("\t", "\n", "\r", "\f", "\b"))


def _tokenize_latex_strings(source: str) -> list[LintError]:
    errors: list[LintError] = []
    try:
        tokens = list(tokenize.tokenize(BytesIO(source.encode()).readline))
    except tokenize.TokenError:
        return errors

    for tok in tokens:
        if tok.type != tokenize.STRING:
            continue
        raw = tok.string
        if not raw.startswith(("'", '"')) or raw.startswith(("r'", 'r"', "R'", 'R"')):
            continue
        inner = raw[1:-1]
        if re.search(r"\\[tnrfbf]", inner):
            # Heuristic: likely LaTeX command written without raw prefix
            errors.append(
                LintError(
                    code="missing_raw_string",
                    message=(
                        "A string passed to MathTex/Tex/MarkupText contains `\\t`, `\\n`, or similar "
                        "without a raw-string prefix (`r\"...\"`). Use raw strings for LaTeX."
                    ),
                    line=tok.start[0],
                )
            )
    return errors
