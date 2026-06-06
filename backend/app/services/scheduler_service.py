from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_scheduler: AsyncIOScheduler | None = None

CATEGORIES = ["kubernetes", "terraform", "aws", "cicd", "incident", "observability", "docker"]


async def _run_daily_generation():
    settings = get_settings()
    logger.info("Daily generation job starting")
    try:
        from app.core.database import get_db
        from app.services.ai.text_engine import TextGenerationEngine
        from app.services.ai.image_engine import ImageGenerationEngine

        db = get_db()
        text_engine = TextGenerationEngine()
        image_engine = ImageGenerationEngine()

        job_doc = {
            "job_name": "daily_generation",
            "status": "running",
            "triggered_by": "scheduler",
            "started_at": datetime.now(timezone.utc),
            "generations_created": 0,
            "created_at": datetime.now(timezone.utc),
        }
        result = await db.scheduled_jobs.insert_one(job_doc)
        job_id = result.inserted_id

        count = 0
        for i in range(settings.daily_generation_limit):
            cat = CATEGORIES[i % len(CATEGORIES)]
            try:
                text_result, text_provider = await text_engine.generate_meme(
                    category=cat, tone="sarcastic"
                )
                img_result = {}
                if text_result.get("image_prompt"):
                    img_result = await image_engine.generate_and_store(
                        text_result["image_prompt"],
                        folder=f"devops-emotions/{cat}",
                    )
                await db.generations.insert_one({
                    "user_id": None,
                    "status": "completed",
                    "category": cat,
                    "content_type": "meme",
                    "tone": "sarcastic",
                    "joke_text": text_result.get("joke_text", ""),
                    "caption": text_result.get("caption", ""),
                    "hashtags": text_result.get("hashtags", []),
                    "image_prompt": text_result.get("image_prompt", ""),
                    "image_url": img_result.get("url"),
                    "thumbnail_url": img_result.get("thumbnail_url"),
                    "text_provider": text_provider,
                    "image_provider": img_result.get("provider_used"),
                    "created_at": datetime.now(timezone.utc),
                })
                count += 1
            except Exception as e:
                logger.warning("Scheduled generation failed", category=cat, error=str(e))

        await db.scheduled_jobs.update_one(
            {"_id": job_id},
            {"$set": {
                "status": "completed",
                "generations_created": count,
                "completed_at": datetime.now(timezone.utc),
            }},
        )
        logger.info("Daily generation job completed", count=count)

    except Exception as e:
        logger.error("Daily generation job failed", error=str(e))


async def _refresh_trends():
    logger.info("Trend refresh starting")
    try:
        from app.core.database import get_db
        from app.core.redis_client import cache_delete
        db = get_db()
        await cache_delete("trends:latest")
        from app.services.trend_service import get_trends
        await get_trends(db)
        logger.info("Trends refreshed")
    except Exception as e:
        logger.warning("Trend refresh failed", error=str(e))


async def start_scheduler():
    global _scheduler
    settings = get_settings()

    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(
        _run_daily_generation,
        CronTrigger(hour=settings.scheduler_hour, minute=settings.scheduler_minute),
        id="daily_generation",
        replace_existing=True,
    )
    _scheduler.add_job(
        _refresh_trends,
        CronTrigger(hour="*/6"),
        id="trend_refresh",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started",
        daily_at=f"{settings.scheduler_hour:02d}:{settings.scheduler_minute:02d} UTC",
    )


async def trigger_now(db) -> dict:
    await _run_daily_generation()
    docs = await db.scheduled_jobs.find().sort("created_at", -1).limit(1).to_list(1)
    return docs[0] if docs else {}
