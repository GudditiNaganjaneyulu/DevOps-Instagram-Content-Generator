from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.dependencies import get_current_user
from app.repositories.generation_repo import GenerationRepository
from app.models.user import UserRead

router = APIRouter()


@router.get("/summary")
async def get_summary(
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    repo = GenerationRepository(db)
    stats = await repo.get_stats()
    today_count = await repo.count_today_by_user(current_user.id)
    user_total = await repo.count_by_user(current_user.id)

    # Provider health check via last 10 generations
    recent = await repo.find_many({"status": "completed"}, limit=10)
    providers: dict[str, int] = {}
    for r in recent:
        p = r.get("text_provider", "unknown")
        providers[p] = providers.get(p, 0) + 1

    return {
        "total_images": stats["total"],
        "completed": stats["completed"],
        "failed": stats["failed"],
        "success_rate": stats["success_rate"],
        "user_total": user_total,
        "today_count": today_count,
        "providers": providers,
    }


@router.get("/usage")
async def get_usage(
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    repo = GenerationRepository(db)

    pipeline = [
        {"$match": {"user_id": {"$exists": True}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 30},
    ]
    daily = await repo.collection.aggregate(pipeline).to_list(30)
    return {
        "daily_breakdown": [{"date": d["_id"], "count": d["count"]} for d in daily]
    }
