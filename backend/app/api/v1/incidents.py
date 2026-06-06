from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.incident import IncidentAnalyzeRequest, IncidentRead, incident_from_doc
from app.models.user import UserRead
from app.services.incident_service import analyze_and_generate
from app.core.exceptions import AppException

router = APIRouter()


@router.post("/analyze", response_model=IncidentRead, status_code=201)
async def analyze_incident(
    body: IncidentAnalyzeRequest,
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        return await analyze_and_generate(body, current_user.id, db)
    except AppException as e:
        raise HTTPException(e.status_code, e.message)


@router.get("/", response_model=list[IncidentRead])
async def list_incidents(
    current_user: UserRead = Depends(get_current_user),
    db=Depends(get_db),
):
    from bson import ObjectId
    docs = await db.incidents.find(
        {"user_id": ObjectId(current_user.id)}
    ).sort("created_at", -1).limit(50).to_list(50)
    return [incident_from_doc(d) for d in docs]
