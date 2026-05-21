"""Tests for the localhost web UI (slice #5)."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from visentia.llm.base import CODEGEN_TEMPERATURE, LLMProvider, Message
from visentia.orchestrator import RepairOrchestrator
from visentia.web_server import JobStatus, create_app


_FIXTURE_SOURCE = (
    Path(__file__).parent / "fixtures" / "freeform" / "renders_fine.py"
).read_text(encoding="utf-8")


class _FakeProvider(LLMProvider):
    name = "fake"
    model = "fake-model"

    def complete(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        temperature: float = CODEGEN_TEMPERATURE,
        response_schema: dict | None = None,
    ) -> str:
        del system, temperature, response_schema
        content = messages[-1]["content"] if messages else ""
        if "Return the complete Python file" in content or "Math content type" in content:
            return _FIXTURE_SOURCE
        return json.dumps(
            {
                "math_content_type": "Relationship",
                "suggested_mode": "Quick",
                "suggested_template_id": "none",
            }
        )


def _poll_until_done(client: TestClient, job_id: str, *, timeout: float = 120.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in (JobStatus.DONE, JobStatus.FAILED):
            return payload
        time.sleep(0.5)
    raise TimeoutError(f"job {job_id} did not finish within {timeout}s")


def test_index_returns_html(tmp_path: Path) -> None:
    app = create_app(
        tmp_path,
        orchestrator_factory=lambda: RepairOrchestrator(provider=_FakeProvider()),
    )
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Visentia" in response.text
    assert "prompt-form" in response.text


@pytest.mark.slow
def test_generate_poll_video_and_metadata(tmp_path: Path) -> None:
    """POST /api/generate → poll → MP4 playable + metadata returned."""

    app = create_app(
        tmp_path,
        orchestrator_factory=lambda: RepairOrchestrator(provider=_FakeProvider()),
    )
    client = TestClient(app)

    start = client.post("/api/generate", json={"prompt": "any prompt"})
    assert start.status_code == 200
    job_id = start.json()["job_id"]

    job = _poll_until_done(client, job_id)
    assert job["status"] == JobStatus.DONE
    assert job["video_url"] == f"/api/jobs/{job_id}/video"
    assert job["metadata"]["llm_provider"] == "fake"
    assert job["metadata"]["classification"]["math_content_type"] == "Relationship"

    video = client.get(job["video_url"])
    assert video.status_code == 200
    assert video.headers["content-type"].startswith("video/")


def test_cli_serve_help() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "visentia", "serve", "--help"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0
    assert "--port" in result.stdout
