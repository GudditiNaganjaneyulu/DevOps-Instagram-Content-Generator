from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Any


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class ScheduledJobRead(BaseModel):
    id: str
    job_name: str
    status: JobStatus
    triggered_by: str = "scheduler"
    generations_created: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


def job_from_doc(doc: dict[str, Any]) -> ScheduledJobRead:
    doc["id"] = str(doc["_id"])
    return ScheduledJobRead(**doc)
