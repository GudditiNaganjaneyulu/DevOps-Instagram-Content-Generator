import time
from datetime import date, datetime, timezone
from bson import ObjectId
from app.services.ai.text_engine import TextGenerationEngine
from app.services.ai.image_engine import ImageGenerationEngine
from app.repositories.generation_repo import GenerationRepository
from app.repositories.user_repo import UserRepository
from app.models.generation import GenerationStatus, GenerateRequest, GenerationRead, generation_from_doc
from app.core.exceptions import DailyLimitExceededError, GenerationFailedError
from app.core.redis_client import cache_get, increment_counter
from app.core.logging import get_logger
from app.config import get_settings

logger = get_logger(__name__)

text_engine = TextGenerationEngine()
image_engine = ImageGenerationEngine()


def _daily_key(user_id: str) -> str:
    return f"gen_count:{user_id}:{date.today().isoformat()}"


async def _get_today_count(user_id: str) -> int:
    val = await cache_get(_daily_key(user_id))
    return int(val) if val else 0


async def _increment_today_count(user_id: str) -> int:
    # TTL = 25h so keys auto-expire even if Redis clock drifts slightly
    return await increment_counter(_daily_key(user_id), ttl=90000)


async def run_generation(
    request: GenerateRequest,
    user_id: str,
    gen_repo: GenerationRepository,
    user_repo: UserRepository,
) -> GenerationRead:
    settings = get_settings()

    today_count = await _get_today_count(user_id)
    user_doc = await user_repo.find_by_id(user_id)
    daily_limit = user_doc.get("settings", {}).get("daily_limit", settings.daily_generation_limit)
    if today_count >= daily_limit:
        raise DailyLimitExceededError()

    doc = {
        "user_id": ObjectId(user_id),
        "status": GenerationStatus.processing,
        "category": request.category,
        "content_type": request.content_type,
        "tone": request.tone,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    created = await gen_repo.create(doc)
    gen_id = str(created["_id"])
    start = time.monotonic()

    try:
        text_result, text_provider = await text_engine.generate_meme(
            category=request.category,
            tone=request.tone,
            context=request.context,
            content_type=request.content_type,
        )

        updates: dict = {
            "joke_text": text_result.get("joke_text", ""),
            "caption": text_result.get("caption", ""),
            "hashtags": text_result.get("hashtags", []),
            "image_prompt": text_result.get("image_prompt", ""),
            "text_provider": text_provider,
        }

        if request.include_image:
            # Pass joke_text to text card renderer (primary provider);
            # AI providers receive the same string as fallback image prompt
            card_prompt = text_result.get("joke_text") or text_result.get("image_prompt", "")
            img_result = await image_engine.generate_and_store(
                prompt=card_prompt,
                folder=f"devops-emotions/{request.category}",
            )
            updates["image_url"] = img_result["url"]
            updates["thumbnail_url"] = img_result["thumbnail_url"]
            updates["image_provider"] = img_result["provider_used"]

        updates["status"] = GenerationStatus.completed
        updates["generation_time_ms"] = int((time.monotonic() - start) * 1000)

        final = await gen_repo.update(gen_id, updates)
        await user_repo.increment_generation_count(user_id)
        new_count = await _increment_today_count(user_id)
        logger.info("Generation completed", gen_id=gen_id, ms=updates["generation_time_ms"], daily_count=new_count)
        return generation_from_doc(final)

    except Exception as e:
        await gen_repo.update(gen_id, {
            "status": GenerationStatus.failed,
            "error_message": str(e)[:500],
        })
        logger.error("Generation failed", gen_id=gen_id, error=str(e))
        raise GenerationFailedError(str(e))
