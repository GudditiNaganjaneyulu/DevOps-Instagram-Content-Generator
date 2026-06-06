from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
    _db = _client[settings.mongodb_db_name]
    await _client.admin.command("ping")
    logger.info("MongoDB connected", db=settings.mongodb_db_name)
    try:
        await _create_indexes()
    except Exception as e:
        logger.warning("Index creation skipped (grant dbAdmin role in Atlas to enable)", error=str(e)[:120])


async def disconnect_db() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB disconnected")


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialized — call connect_db() first")
    return _db


async def _create_indexes() -> None:
    db = get_db()
    await db.users.create_index("email", unique=True)
    await db.users.create_index("provider_id")
    await db.generations.create_index("user_id")
    await db.generations.create_index("created_at")
    await db.generations.create_index([("category", 1), ("created_at", -1)])
    await db.incidents.create_index("user_id")
    await db.trends.create_index("fetched_at")
    await db.analytics.create_index([("user_id", 1), ("date", -1)])
    logger.info("MongoDB indexes created")
