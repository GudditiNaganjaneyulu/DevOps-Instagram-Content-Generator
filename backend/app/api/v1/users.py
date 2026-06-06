from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.dependencies import get_current_user
from app.repositories.user_repo import UserRepository
from app.models.user import UserRead, UserUpdate, user_from_doc

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(current_user: UserRead = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_me(
    body: UserUpdate,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    repo = UserRepository(db)
    updates = body.model_dump(exclude_none=True)
    if "settings" in updates:
        updates = {f"settings.{k}": v for k, v in updates["settings"].items()}
    doc = await repo.update(current_user.id, updates)
    return user_from_doc(doc)


@router.get("/me/usage")
async def get_usage(current_user: UserRead = Depends(get_current_user)):
    return current_user.usage
