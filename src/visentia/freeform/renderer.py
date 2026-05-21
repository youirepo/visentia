"""SandboxedRenderer — isolated Manim subprocess (ADR-0003 layer 2)."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

DEFAULT_RENDER_TIMEOUT_S = 120


RenderKind = Literal["success", "timeout", "render_error", "name_error", "setup_error"]


@dataclass(frozen=True)
class RenderSuccess:
    mp4_path: Path
    stderr: str = ""


@dataclass(frozen=True)
class RenderTimeout:
    message: str = "Rendering took too long and was stopped."
    stderr: str = ""


@dataclass(frozen=True)
class RenderFailure:
    kind: RenderKind
    message: str
    stderr: str = ""


RenderResult = RenderSuccess | RenderTimeout | RenderFailure


class SandboxedRenderer:
    """Run Manim in a per-run temp directory with a wall-clock timeout."""

    def __init__(self, *, timeout_s: float = DEFAULT_RENDER_TIMEOUT_S) -> None:
        self._timeout_s = timeout_s

    def render(
        self,
        python_source: str,
        scene_name: str,
        output_dir: Path,
    ) -> RenderResult:
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="visentia-render-") as tmp:
            work = Path(tmp)
            scene_path = work / "scene.py"
            scene_path.write_text(python_source, encoding="utf-8")
            media_dir = work / "media"
            media_dir.mkdir()

            cmd = [
                sys.executable,
                "-m",
                "manim",
                "render",
                str(scene_path),
                scene_name,
                "-ql",
                "--media_dir",
                str(media_dir),
                "--disable_caching",
                "-v",
                "WARNING",
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout_s,
                    cwd=work,
                )
            except subprocess.TimeoutExpired as exc:
                stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
                return RenderTimeout(stderr=stderr)

            stderr = proc.stderr or ""
            stdout = proc.stdout or ""
            combined = stderr + stdout

            if proc.returncode != 0:
                return self._classify_failure(combined)

            mp4 = _find_mp4(media_dir)
            if mp4 is None:
                return RenderFailure(
                    kind="render_error",
                    message="Manim finished but no MP4 was produced.",
                    stderr=combined,
                )

            dest = output_dir / f"freeform_{scene_name.lower()}.mp4"
            dest.write_bytes(mp4.read_bytes())
            return RenderSuccess(mp4_path=dest, stderr=combined)

    def _classify_failure(self, combined: str) -> RenderFailure:
        if "NameError" in combined:
            match = re.search(r"NameError: (.+)", combined)
            detail = match.group(1).strip() if match else "undefined name"
            return RenderFailure(
                kind="name_error",
                message=f"Generated code referenced something that does not exist ({detail}).",
                stderr=combined,
            )
        if "ModuleNotFoundError" in combined or "ImportError" in combined:
            return RenderFailure(
                kind="setup_error",
                message="Visentia could not run Manim for this artifact. Check that Manim is installed correctly.",
                stderr=combined,
            )
        snippet = _last_meaningful_line(combined)
        return RenderFailure(
            kind="render_error",
            message=(
                "Manim could not render the generated scene."
                + (f" ({snippet})" if snippet else "")
            ),
            stderr=combined,
        )


def _find_mp4(media_dir: Path) -> Path | None:
    candidates = [
        p
        for p in media_dir.rglob("*.mp4")
        if "partial_movie_files" not in p.parts
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _last_meaningful_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if stripped and not stripped.startswith("|"):
            return stripped[:200]
    return ""
