from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.dependencies import get_current_user
from app.repositories.generation_repo import GenerationRepository
from app.repositories.user_repo import UserRepository
from app.models.generation import GenerateRequest, GenerationRead, generation_from_doc
from app.models.user import UserRead
from app.services.generation_service import run_generation
from app.core.exceptions import AppException

router = APIRouter()


@router.post("/", response_model=GenerationRead, status_code=201)
async def generate_content(
    body: GenerateRequest,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    gen_repo = GenerationRepository(db)
    user_repo = UserRepository(db)
    try:
        return await run_generation(body, current_user.id, gen_repo, user_repo)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/status/{gen_id}", response_model=GenerationRead)
async def get_generation_status(
    gen_id: str,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    repo = GenerationRepository(db)
    doc = await repo.find_by_id(gen_id)
    if not doc:
        raise HTTPException(404, "Generation not found")
    if str(doc["user_id"]) != current_user.id:
        raise HTTPException(403, "Not your generation")
    return generation_from_doc(doc)
