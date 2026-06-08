import json
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.database import get_db
from app.dependencies import get_current_user
from app.repositories.generation_repo import GenerationRepository
from app.repositories.user_repo import UserRepository
from app.models.generation import GenerateRequest, GenerationRead, generation_from_doc
from app.models.user import UserRead
from app.services.generation_service import run_generation
from app.core.exceptions import AppException
from app.core import job_queue
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_qstash_client():
    from qstash import QStash
    settings = get_settings()
    return QStash(token=settings.qstash_token)


def _verify_qstash_signature(request: Request, body: bytes) -> None:
    from qstash import Receiver
    settings = get_settings()
    if not settings.qstash_current_signing_key:
        return  # skip verification in dev (no signing keys configured)
    receiver = Receiver(
        current_signing_key=settings.qstash_current_signing_key,
        next_signing_key=settings.qstash_next_signing_key,
    )
    try:
        receiver.verify(
            signature=request.headers.get("Upstash-Signature", ""),
            body=body.decode(),
            url=f"{settings.api_base_url}/api/v1/generate/worker",
        )
    except Exception:
        raise HTTPException(401, "Invalid QStash signature")


# ── Sync endpoint (unchanged — used by direct callers) ─────────────────────────

@router.post("/", response_model=GenerationRead, status_code=201)
async def generate_content(
    body: GenerateRequest,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    gen_repo = GenerationRepository(db)
    user_repo = UserRepository(db)
    try:
        return await run_generation(body, current_user.id, gen_repo, user_repo)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ── Queue endpoint — returns immediately ──────────────────────────────────────

@router.post("/queue", status_code=202)
async def queue_generation(
    body: GenerateRequest,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Enqueue a generation job. Returns {job_id} immediately (202).
    Poll GET /api/v1/generate/job/{job_id} for status + result.

    Uses QStash when QSTASH_TOKEN is set, otherwise falls back to
    asyncio.Queue (in-process, zero config).
    """
    settings = get_settings()

    if settings.qstash_token:
        # ── QStash path ────────────────────────────────────────────────────────
        import uuid
        job_id = str(uuid.uuid4())
        job_queue._jobs[job_id] = {"status": "queued", "gen_id": None, "error": None}

        try:
            client = _get_qstash_client()
            client.message.publish_json(
                url=f"{settings.api_base_url}/api/v1/generate/worker",
                body={
                    "job_id": job_id,
                    "request": body.model_dump(),
                    "user_id": current_user.id,
                },
                retries=3,
                delay="0s",
            )
            logger.info("Job published to QStash", job_id=job_id)
        except Exception as e:
            del job_queue._jobs[job_id]
            logger.warning("QStash publish failed, falling back to asyncio.Queue", error=str(e))
            # Graceful fallback to in-process queue
            try:
                job_id = await job_queue.enqueue(body.model_dump(), current_user.id)
            except RuntimeError as re:
                raise HTTPException(503, str(re))

    else:
        # ── asyncio.Queue fallback ─────────────────────────────────────────────
        try:
            job_id = await job_queue.enqueue(body.model_dump(), current_user.id)
            logger.info("Job enqueued (asyncio.Queue)", job_id=job_id)
        except RuntimeError as e:
            raise HTTPException(503, str(e))

    return {"job_id": job_id, "status": "queued"}


# ── QStash webhook — called by QStash to process the job ──────────────────────

@router.post("/worker")
async def generation_worker(request: Request, db=Depends(get_db)):
    """
    Webhook endpoint called by QStash (or directly by the asyncio worker).
    Verifies the QStash signature, then runs the generation pipeline.
    """
    body = await request.body()
    _verify_qstash_signature(request, body)

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON body")

    job_id = data.get("job_id")
    if not job_id:
        raise HTTPException(400, "Missing job_id")

    job_queue._set_job(job_id, status="processing")
    logger.info("Worker received job", job_id=job_id)

    try:
        req = GenerateRequest(**data["request"])
        user_id = data["user_id"]
        gen_repo = GenerationRepository(db)
        user_repo = UserRepository(db)
        result = await run_generation(req, user_id, gen_repo, user_repo)
        job_queue._set_job(job_id, status="completed", gen_id=result.id)
        logger.info("Worker completed job", job_id=job_id, gen_id=result.id)
        return {"ok": True, "gen_id": result.id}

    except AppException as e:
        job_queue._set_job(job_id, status="failed", error=e.message)
        logger.warning("Worker job failed", job_id=job_id, error=e.message)
        # Return 200 to QStash so it doesn't retry AppExceptions (expected failures)
        return {"ok": False, "error": e.message}

    except Exception as e:
        job_queue._set_job(job_id, status="failed", error=str(e))
        logger.warning("Worker job error", job_id=job_id, error=str(e))
        # Non-200 → QStash will retry (up to retries=3)
        raise HTTPException(500, str(e))


# ── Job status polling ─────────────────────────────────────────────────────────

@router.get("/job/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    """Poll job status. When status=completed, result is attached."""
    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found — it may have been lost on a server restart")

    response: dict = {"job_id": job_id, "status": job["status"], "error": job.get("error")}

    if job["status"] == "completed" and job.get("gen_id"):
        repo = GenerationRepository(db)
        doc = await repo.find_by_id(job["gen_id"])
        if doc and str(doc["user_id"]) == current_user.id:
            response["result"] = generation_from_doc(doc).model_dump()

    return response


@router.get("/queue/stats")
async def get_queue_stats(current_user: UserRead = Depends(get_current_user)):
    """Debug queue state — shows active mode (qstash or asyncio)."""
    settings = get_settings()
    stats = job_queue.queue_stats()
    stats["mode"] = "qstash" if settings.qstash_token else "asyncio"
    return stats


# ── Legacy status endpoint ─────────────────────────────────────────────────────

@router.get("/status/{gen_id}", response_model=GenerationRead)
async def get_generation_status(
    gen_id: str,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    repo = GenerationRepository(db)
    doc = await repo.find_by_id(gen_id)
    if not doc:
        raise HTTPException(404, "Generation not found")
    if str(doc["user_id"]) != current_user.id:
        raise HTTPException(403, "Not your generation")
    return generation_from_doc(doc)
