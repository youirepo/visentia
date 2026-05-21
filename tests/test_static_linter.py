"""StaticLinter unit tests — four probe bug classes + happy path."""

from __future__ import annotations

from pathlib import Path

import pytest

from visentia.freeform.linter import LintOk, StaticLinter

_FIXTURES = Path(__file__).parent / "fixtures" / "freeform"


def _read(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture
def linter() -> StaticLinter:
    return StaticLinter()


def test_lint_accepts_valid_fixture(linter: StaticLinter) -> None:
    result = linter.lint(_read("renders_fine.py"))
    assert isinstance(result, LintOk)
    assert result.scene_class_name == "RendersFine"


def test_lint_cyan_hallucination(linter: StaticLinter) -> None:
    result = linter.lint(_read("lint_cyan.py"))
    assert isinstance(result, list)
    codes = {e.code for e in result}
    assert "unknown_symbol" in codes
    assert any("CYAN" in e.message for e in result)


def test_lint_missing_raw_string_on_mathtex(linter: StaticLinter) -> None:
    result = linter.lint(_read("lint_missing_r_mathtex.py"))
    assert isinstance(result, list)
    assert any(e.code == "missing_raw_string" for e in result)


def test_lint_stroke_dash_array_kwarg(linter: StaticLinter) -> None:
    result = linter.lint(_read("lint_stroke_dash_array.py"))
    assert isinstance(result, list)
    assert any(e.code == "invalid_kwarg" for e in result)
    assert any("stroke_dash_array" in e.message for e in result)


def test_lint_missing_manim_import(linter: StaticLinter) -> None:
    result = linter.lint(_read("lint_missing_import.py"))
    assert isinstance(result, list)
    assert any(e.code == "missing_import" for e in result)
