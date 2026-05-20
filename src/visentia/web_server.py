"""Minimal localhost web UI for Visentia (slice #5).

Serves a single-page UI and a small JSON API. Generation runs in a background thread
so the browser can poll job status while `RepairOrchestrator.generate_video` works —
same engine as the CLI, not reimplemented.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from visentia.orchestrator import RepairOrchestrator
from visentia.results import Failure, Mp4

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "web_static"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    prompt: str
    status: JobStatus = JobStatus.PENDING
    message: str = "Queued"
    detail: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    video_path: Path | None = None
    output_dir: Path | None = None


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    detail: str = ""
    video_url: str | None = None
    metadata: dict[str, Any] | None = None


class JobStore:
    """In-memory job registry. One render at a time via a lock (Manim is heavy)."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, prompt: str, output_dir: Path) -> Job:
        job = Job(id=str(uuid.uuid4()), prompt=prompt, output_dir=output_dir)
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def run_exclusive(self, fn: Callable[[], None]) -> None:
        """Run `fn` while holding the render lock (blocks concurrent Manim renders)."""

        with self._lock:
            fn()


def create_app(
    output_dir: Path,
    *,
    orchestrator_factory: Callable[[], RepairOrchestrator] | None = None,
) -> FastAPI:
    """Build the FastAPI application.

    `orchestrator_factory` is injectable for tests (e.g. a fake LLM provider).
    """

    base_output = output_dir.resolve()
    base_output.mkdir(parents=True, exist_ok=True)
    store = JobStore()
    make_orchestrator = orchestrator_factory or (lambda: RepairOrchestrator())

    app = FastAPI(title="Visentia", version="0.1.0.dev0")

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        html = (_STATIC_DIR / "index.html").read_text(encoding="utf-8")
        return HTMLResponse(html)

    @app.post("/api/generate")
    def start_generation(body: GenerateRequest) -> dict[str, str]:
        prompt = body.prompt.strip()
        job_dir = base_output / "web" / str(uuid.uuid4())
        job_dir.mkdir(parents=True, exist_ok=True)
        job = store.create(prompt, job_dir)

        def _work() -> None:
            store.run_exclusive(lambda: _execute_job(store, job, make_orchestrator))

        thread = threading.Thread(target=_work, name=f"visentia-job-{job.id}", daemon=True)
        thread.start()
        return {"job_id": job.id}

    @app.get("/api/jobs/{job_id}", response_model=JobResponse)
    def get_job(job_id: str) -> JobResponse:
        job = store.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return _job_to_response(job)

    @app.get("/api/jobs/{job_id}/video")
    def get_job_video(job_id: str) -> FileResponse:
        job = store.get(job_id)
        if job is None or job.status != JobStatus.DONE or job.video_path is None:
            raise HTTPException(status_code=404, detail="Video not available")
        return FileResponse(
            job.video_path,
            media_type="video/mp4",
            filename=job.video_path.name,
        )

    return app


def _execute_job(
    store: JobStore,
    job: Job,
    make_orchestrator: Callable[[], RepairOrchestrator],
) -> None:
    job.status = JobStatus.RUNNING
    job.message = "Classifying Prompt and rendering Explainer Artifact…"
    job.detail = "This may take up to a minute on first run."
    started = time.monotonic()

    orchestrator = make_orchestrator()
    result = orchestrator.generate_video(job.prompt, output_dir=job.output_dir)

    elapsed = int(time.monotonic() - started)
    if isinstance(result, Mp4):
        job.status = JobStatus.DONE
        job.message = "Explainer Artifact ready"
        job.detail = f"Completed in {elapsed}s"
        job.video_path = result.path
        job.metadata = result.metadata
        logger.info("Web job %s done: %s", job.id, result.path)
        return

    if isinstance(result, Failure):
        job.status = JobStatus.FAILED
        job.message = result.message
        job.detail = result.last_error or ""
        logger.warning("Web job %s failed: %s", job.id, result.message)
        return


def _job_to_response(job: Job) -> JobResponse:
    video_url = None
    metadata = None
    if job.status == JobStatus.DONE and job.video_path is not None:
        video_url = f"/api/jobs/{job.id}/video"
        metadata = job.metadata
    return JobResponse(
        job_id=job.id,
        status=job.status,
        message=job.message,
        detail=job.detail,
        video_url=video_url,
        metadata=metadata,
    )


def run_server(
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    output_dir: Path | None = None,
) -> None:
    """Start uvicorn with the Visentia web UI."""

    import uvicorn

    target = (output_dir or Path.cwd() / "videos").resolve()
    app = create_app(target)
    print(f"Visentia web UI: http://{host}:{port}/")
    print(f"Writing artifacts under {target}/web/")
    uvicorn.run(app, host=host, port=port, log_level="info")
