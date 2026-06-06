from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Any


class TrendSource(str, Enum):
    reddit = "reddit"
    hackernews = "hackernews"
    k8s_blog = "k8s_blog"
    aws_blog = "aws_blog"


class TrendRead(BaseModel):
    id: str
    title: str
    url: str | None = None
    source: TrendSource
    score: int = 0
    comments: int = 0
    category: str = "general"
    summary: str | None = None
    generation_id: str | None = None
    image_url: str | None = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


def trend_from_doc(doc: dict[str, Any]) -> TrendRead:
    doc["id"] = str(doc["_id"])
    if doc.get("generation_id"):
        doc["generation_id"] = str(doc["generation_id"])
    return TrendRead(**doc)
