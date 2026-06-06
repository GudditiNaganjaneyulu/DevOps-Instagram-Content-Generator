import redis.asyncio as aioredis
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis: aioredis.Redis | None = None


async def connect_redis() -> None:
    global _redis
    settings = get_settings()
    _redis = await aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
    )
    await _redis.ping()
    logger.info("Redis connected")


async def disconnect_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        logger.info("Redis disconnected")


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized — call connect_redis() first")
    return _redis


async def cache_get(key: str) -> str | None:
    return await get_redis().get(key)


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    await get_redis().setex(key, ttl, value)


async def cache_delete(key: str) -> None:
    await get_redis().delete(key)


async def increment_counter(key: str, ttl: int = 86400) -> int:
    r = get_redis()
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, ttl)
    return count
