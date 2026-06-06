from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import BaseRepository
from app.models.generation import GenerationStatus


class GenerationRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db.generations)

    async def find_by_user(
        self,
        user_id: str,
        category: str | None = None,
        content_type: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[dict]:
        filter: dict = {"user_id": ObjectId(user_id)}
        if category:
            filter["category"] = category
        if content_type:
            filter["content_type"] = content_type
        return await self.find_many(filter, skip=skip, limit=limit)

    async def count_by_user(self, user_id: str) -> int:
        return await self.count({"user_id": ObjectId(user_id)})

    async def count_today_by_user(self, user_id: str) -> int:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return await self.count({
            "user_id": ObjectId(user_id),
            "created_at": {"$gte": today},
            "status": GenerationStatus.completed,
        })

    async def find_completed(self, skip: int = 0, limit: int = 20) -> list[dict]:
        return await self.find_many(
            {"status": GenerationStatus.completed, "image_url": {"$exists": True}},
            skip=skip,
            limit=limit,
        )

    async def get_stats(self) -> dict:
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
            }}
        ]
        results = await self.collection.aggregate(pipeline).to_list(None)
        stats = {r["_id"]: r["count"] for r in results}
        total = sum(stats.values())
        completed = stats.get(GenerationStatus.completed, 0)
        return {
            "total": total,
            "completed": completed,
            "failed": stats.get(GenerationStatus.failed, 0),
            "pending": stats.get(GenerationStatus.pending, 0),
            "success_rate": round(completed / total * 100, 1) if total else 0,
        }
