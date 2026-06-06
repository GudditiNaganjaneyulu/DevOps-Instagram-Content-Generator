from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.dependencies import get_admin_user
from app.models.user import UserRead
from app.services.scheduler_service import trigger_now, _scheduler

router = APIRouter()


@router.post("/run")
async def run_scheduler_now(
    admin: UserRead = Depends(get_admin_user),
    db=Depends(get_db),
):
    result = await trigger_now(db)
    return {"message": "Scheduler triggered", "job": str(result.get("_id", ""))}


@router.get("/status")
async def scheduler_status(admin: UserRead = Depends(get_admin_user)):
    if _scheduler is None:
        return {"running": False}
    jobs = [
        {
            "id": job.id,
            "next_run": str(job.next_run_time),
        }
        for job in _scheduler.get_jobs()
    ]
    return {"running": _scheduler.running, "jobs": jobs}
