import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.database import connect_db, disconnect_db
from app.core.redis_client import connect_redis, disconnect_redis
from app.core.cloudinary_client import configure_cloudinary
from app.core.rate_limiter import limiter
from app.core.exceptions import AppException
from app.api.v1.router import api_router
from app.api.v1.health import router as health_router

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting DevOps Runtime Emotions AI Studio", env=settings.app_env)

    await connect_db()
    await connect_redis()
    configure_cloudinary()

    # Start scheduler
    if settings.app_env == "production" or settings.app_debug:
        try:
            from app.services.scheduler_service import start_scheduler
            await start_scheduler()
        except Exception as e:
            logger.warning("Scheduler start skipped", error=str(e))

    yield

    logger.info("Shutting down...")
    await disconnect_db()
    await disconnect_redis()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Rate limiter
    app.state.limiter = limiter

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://*.vercel.app",
            "https://*.netlify.app",
            "https://*.onrender.com",
            "https://web.gudditinaganjaneyulu.qzz.io",
            "https://api.gudditinaganjaneyulu.qzz.io",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})

    # Routers
    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_prefix)

    # Telemetry (after routers so FastAPI instrumentor sees all routes)
    from app.core.telemetry import setup_telemetry
    setup_telemetry(app)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
