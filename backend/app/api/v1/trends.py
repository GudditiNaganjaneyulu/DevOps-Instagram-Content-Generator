from fastapi import APIRouter, Depends, Query
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.trend import TrendRead
from app.models.user import UserRead
from app.services.trend_service import get_trends, generate_trend_meme

router = APIRouter()


@router.get("/", response_model=list[TrendRead])
async def list_trends(
    limit: int = Query(20, ge=1, le=50),
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    return await get_trends(db, limit)


@router.post("/{trend_id}/generate")
async def generate_for_trend(
    trend_id: str,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    return await generate_trend_meme(trend_id, current_user.id, db)
