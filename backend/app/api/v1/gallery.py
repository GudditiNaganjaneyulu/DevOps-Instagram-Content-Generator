from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from app.core.database import get_db
from app.dependencies import get_current_user
from app.repositories.generation_repo import GenerationRepository
from app.models.generation import GenerationRead, generation_from_doc
from app.models.user import UserRead

router = APIRouter()


@router.get("/", response_model=dict)
async def list_gallery(
    category: str | None = Query(None),
    content_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    repo = GenerationRepository(db)
    skip = (page - 1) * limit
    docs = await repo.find_by_user(
        current_user.id,
        category=category,
        content_type=content_type,
        skip=skip,
        limit=limit,
    )
    total = await repo.count_by_user(current_user.id)
    items = [generation_from_doc(d) for d in docs]
    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{gen_id}", response_model=GenerationRead)
async def get_generation(
    gen_id: str,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    repo = GenerationRepository(db)
    doc = await repo.find_by_id(gen_id)
    if not doc:
        raise HTTPException(404, "Generation not found")
    if str(doc["user_id"]) != current_user.id:
        raise HTTPException(403, "Forbidden")
    return generation_from_doc(doc)


@router.get("/{gen_id}/download")
async def download_image(
    gen_id: str,
    db=Depends(get_db),
):
    # Public endpoint — Cloudinary URL is already access-controlled at the CDN level
    repo = GenerationRepository(db)
    doc = await repo.find_by_id(gen_id)
    if not doc:
        raise HTTPException(404, "Not found")
    if not doc.get("image_url"):
        raise HTTPException(404, "No image for this generation")
    return RedirectResponse(url=doc["image_url"])
