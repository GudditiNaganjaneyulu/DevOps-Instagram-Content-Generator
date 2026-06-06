from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Search .env in backend/ first, then fall back to project root (../.env)
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    # App
    app_env: str = "development"
    app_debug: bool = True
    app_name: str = "DevOps Runtime Emotions AI Studio"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # MongoDB
    mongodb_url: str = "mongodb://root:devpassword@localhost:27017"
    mongodb_db_name: str = "devops_emotions"

    # Redis
    redis_url: str = "redis://:devpassword@localhost:6379"

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    cloudinary_upload_preset: str = "devops_emotions"

    # AI Providers — text
    groq_api_key: str = ""
    google_ai_api_key: str = ""
    openrouter_api_key: str = ""

    # AI Providers — image
    huggingface_api_key: str = ""
    stable_horde_api_key: str = "0000000000"  # anonymous key works, register at stablehorde.net for priority
    fal_api_key: str = ""

    # Auth / JWT
    jwt_secret: str = "changeme_at_least_32_chars_long_secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    github_id: str = ""
    github_secret: str = ""

    # Scheduler
    daily_generation_limit: int = 5
    scheduler_hour: int = 9
    scheduler_minute: int = 0

    # Reddit
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "DevOpsEmotions/1.0"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
