from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    generate,
    gallery,
    incidents,
    trends,
    scheduler,
    analytics,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(generate.router, prefix="/generate", tags=["Generate"])
api_router.include_router(gallery.router, prefix="/gallery", tags=["Gallery"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(trends.router, prefix="/trends", tags=["Trends"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["Scheduler"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
