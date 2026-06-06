from typing import Any, Generic, TypeVar
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    def _to_doc(self, data: dict) -> dict:
        return {k: v for k, v in data.items() if v is not None}

    async def find_by_id(self, id: str) -> dict | None:
        if not ObjectId.is_valid(id):
            return None
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def find_one(self, filter: dict) -> dict | None:
        return await self.collection.find_one(filter)

    async def find_many(
        self,
        filter: dict,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_dir: int = -1,
    ) -> list[dict]:
        cursor = (
            self.collection.find(filter)
            .sort(sort_by, sort_dir)
            .skip(skip)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def count(self, filter: dict) -> int:
        return await self.collection.count_documents(filter)

    async def create(self, doc: dict) -> dict:
        now = datetime.now(timezone.utc)
        doc.setdefault("created_at", now)
        doc.setdefault("updated_at", now)
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def update(self, id: str, updates: dict) -> dict | None:
        if not ObjectId.is_valid(id):
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": updates}
        )
        return await self.find_by_id(id)

    async def delete(self, id: str) -> bool:
        if not ObjectId.is_valid(id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def upsert(self, filter: dict, doc: dict) -> dict:
        now = datetime.now(timezone.utc)
        doc.setdefault("created_at", now)
        doc["updated_at"] = now
        result = await self.collection.find_one_and_update(
            filter,
            {"$set": doc},
            upsert=True,
            return_document=True,
        )
        return result
