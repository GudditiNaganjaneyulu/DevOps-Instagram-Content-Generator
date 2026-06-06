from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import BaseRepository
from app.models.user import UserCreate, UserRole


class UserRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db.users)

    async def find_by_email(self, email: str) -> dict | None:
        return await self.find_one({"email": email.lower()})

    async def find_by_provider(self, provider: str, provider_id: str) -> dict | None:
        return await self.find_one({"provider": provider, "provider_id": provider_id})

    async def upsert_oauth_user(self, user_data: UserCreate) -> dict:
        doc = user_data.model_dump()
        doc["email"] = doc["email"].lower()
        doc.setdefault("role", UserRole.user)
        doc.setdefault("settings", {
            "theme": "dark",
            "daily_limit": 10,
            "default_category": "kubernetes",
            "default_tone": "sarcastic",
            "email_notifications": True,
        })
        doc.setdefault("usage", {
            "total_generations": 0,
            "today_count": 0,
            "total_downloads": 0,
        })
        return await self.upsert(
            {"provider": doc["provider"], "provider_id": doc["provider_id"]},
            doc,
        )

    async def increment_generation_count(self, user_id: str) -> None:
        from bson import ObjectId
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$inc": {
                    "usage.total_generations": 1,
                    "usage.today_count": 1,
                }
            },
        )

    async def reset_today_count(self, user_id: str) -> None:
        from bson import ObjectId
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"usage.today_count": 0}},
        )
