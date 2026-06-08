"""
In-process async job queue for content generation.
Uses asyncio.Queue — zero dependencies, zero config, zero cost.

Jobs are in-memory only: queue is cleared on Render cold-start.
Frontend polls /api/v1/generate/status/{job_id} until completed.
"""
import asyncio
import uuid
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

# In-memory job registry: job_id → {status, gen_id, error}
_jobs: dict[str, dict[str, Any]] = {}
_queue: asyncio.Queue | None = None
_worker_task: asyncio.Task | None = None

MAX_QUEUE_SIZE = 20  # reject if more than 20 pending jobs


def _get_queue() -> asyncio.Queue:
    global _queue
    if _queue is None:
        _queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
    return _queue


def get_job(job_id: str) -> dict[str, Any] | None:
    return _jobs.get(job_id)


def _set_job(job_id: str, **kwargs: Any) -> None:
    if job_id in _jobs:
        _jobs[job_id].update(kwargs)


async def enqueue(request_data: dict, user_id: str) -> str:
    q = _get_queue()
    if q.full():
        raise RuntimeError("Queue is full — try again shortly")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "queued", "gen_id": None, "error": None}
    await q.put({"job_id": job_id, "request": request_data, "user_id": user_id})
    logger.info("Job enqueued", job_id=job_id, queue_size=q.qsize())
    return job_id


async def _worker() -> None:
    from app.core.database import get_db
    from app.repositories.generation_repo import GenerationRepository
    from app.repositories.user_repo import UserRepository
    from app.services.generation_service import run_generation
    from app.models.generation import GenerateRequest

    q = _get_queue()
    logger.info("Generation worker started")

    while True:
        try:
            job = await q.get()
            job_id = job["job_id"]
            _set_job(job_id, status="processing")
            logger.info("Processing job", job_id=job_id)

            try:
                db = get_db()
                gen_repo = GenerationRepository(db)
                user_repo = UserRepository(db)
                req = GenerateRequest(**job["request"])
                result = await run_generation(req, job["user_id"], gen_repo, user_repo)
                _set_job(job_id, status="completed", gen_id=result.id)
                logger.info("Job completed", job_id=job_id, gen_id=result.id)

            except Exception as e:
                _set_job(job_id, status="failed", error=str(e))
                logger.warning("Job failed", job_id=job_id, error=str(e))

            finally:
                q.task_done()

        except asyncio.CancelledError:
            logger.info("Generation worker stopped")
            break
        except Exception as e:
            logger.warning("Worker loop error", error=str(e))


def start_worker() -> asyncio.Task:
    global _worker_task
    _get_queue()  # ensure queue is initialised
    _worker_task = asyncio.create_task(_worker(), name="generation-worker")
    return _worker_task


def stop_worker() -> None:
    global _worker_task
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        _worker_task = None


def queue_stats() -> dict[str, Any]:
    q = _get_queue()
    pending = [j for j in _jobs.values() if j["status"] == "queued"]
    processing = [j for j in _jobs.values() if j["status"] == "processing"]
    return {
        "queue_size": q.qsize(),
        "max_size": MAX_QUEUE_SIZE,
        "pending": len(pending),
        "processing": len(processing),
        "total_jobs": len(_jobs),
        "worker_running": _worker_task is not None and not _worker_task.done(),
    }
