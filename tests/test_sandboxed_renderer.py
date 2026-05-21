"""SandboxedRenderer integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from visentia.freeform.renderer import (
    RenderFailure,
    RenderSuccess,
    RenderTimeout,
    SandboxedRenderer,
)

_FIXTURES = Path(__file__).parent / "fixtures" / "freeform"


def _read(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


@pytest.mark.slow
def test_renders_fine_fixture(tmp_path: Path) -> None:
    renderer = SandboxedRenderer(timeout_s=120)
    result = renderer.render(_read("renders_fine.py"), "RendersFine", tmp_path)
    assert isinstance(result, RenderSuccess)
    assert result.mp4_path.exists()
    assert result.mp4_path.stat().st_size > 0


@pytest.mark.slow
def test_raises_name_error_fixture(tmp_path: Path) -> None:
    renderer = SandboxedRenderer(timeout_s=120)
    result = renderer.render(_read("raises_name_error.py"), "RaisesNameError", tmp_path)
    assert isinstance(result, RenderFailure)
    assert result.kind == "name_error"


@pytest.mark.slow
def test_infinite_loop_times_out(tmp_path: Path) -> None:
    renderer = SandboxedRenderer(timeout_s=8)
    result = renderer.render(_read("infinite_loop.py"), "InfiniteLoop", tmp_path)
    assert isinstance(result, RenderTimeout)
