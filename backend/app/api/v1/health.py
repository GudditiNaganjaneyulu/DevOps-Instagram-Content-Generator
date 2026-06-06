from fastapi import APIRouter
from app.core.database import get_db
from app.core.redis_client import get_redis
from app.config import get_settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    settings = get_settings()
    status = {"status": "ok", "version": settings.app_version, "env": settings.app_env}

    try:
        db = get_db()
        await db.command("ping")
        status["mongodb"] = "connected"
    except Exception as e:
        status["mongodb"] = f"error: {e}"
        status["status"] = "degraded"

    try:
        redis = get_redis()
        await redis.ping()
        status["redis"] = "connected"
    except Exception as e:
        status["redis"] = f"error: {e}"
        status["status"] = "degraded"

    return status
