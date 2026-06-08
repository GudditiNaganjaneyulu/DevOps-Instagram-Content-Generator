from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any


class GenerationStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ContentType(str, Enum):
    meme = "meme"
    comic = "comic"
    incident = "incident"
    trend = "trend"
    dialogue = "dialogue"


class ContentCategory(str, Enum):
    kubernetes = "kubernetes"
    docker = "docker"
    terraform = "terraform"
    aws = "aws"
    azure = "azure"
    gcp = "gcp"
    cicd = "cicd"
    incident = "incident"
    observability = "observability"
    security = "security"
    platform = "platform"
    sre = "sre"
    ai_engineering = "ai_engineering"
    feelings = "feelings"
    general = "general"


class ContentTone(str, Enum):
    sarcastic = "sarcastic"
    empathetic = "empathetic"
    dark_humor = "dark_humor"
    motivational = "motivational"
    educational = "educational"


class GenerateRequest(BaseModel):
    category: ContentCategory = ContentCategory.kubernetes
    tone: ContentTone = ContentTone.sarcastic
    content_type: ContentType = ContentType.meme
    context: str | None = None
    include_image: bool = True
    image_style: str = "dark_tech"


class GenerationRead(BaseModel):
    id: str
    user_id: str
    status: GenerationStatus
    category: ContentCategory
    content_type: ContentType
    tone: ContentTone
    joke_text: str | None = None
    caption: str | None = None
    hashtags: list[str] = []
    image_prompt: str | None = None
    image_url: str | None = None
    thumbnail_url: str | None = None
    text_provider: str | None = None
    image_provider: str | None = None
    generation_time_ms: int | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


def generation_from_doc(doc: dict[str, Any]) -> GenerationRead:
    doc["id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    return GenerationRead(**doc)
