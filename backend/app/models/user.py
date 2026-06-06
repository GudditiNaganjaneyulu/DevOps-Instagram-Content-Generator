from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import Any


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if ObjectId.is_valid(str(v)):
            return str(v)
        raise ValueError("Invalid ObjectId")


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class AuthProvider(str, Enum):
    google = "google"
    github = "github"
    email = "email"


class UserSettings(BaseModel):
    theme: str = "dark"
    daily_limit: int = 10
    default_category: str = "kubernetes"
    default_tone: str = "sarcastic"
    email_notifications: bool = True


class UserUsage(BaseModel):
    total_generations: int = 0
    today_count: int = 0
    total_downloads: int = 0
    last_reset: datetime = Field(default_factory=datetime.utcnow)


class UserBase(BaseModel):
    email: EmailStr
    name: str
    image: str | None = None


class UserCreate(UserBase):
    provider: AuthProvider
    provider_id: str


class UserRead(UserBase):
    id: str
    role: UserRole = UserRole.user
    settings: UserSettings = Field(default_factory=UserSettings)
    usage: UserUsage = Field(default_factory=UserUsage)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    image: str | None = None
    settings: UserSettings | None = None


def user_from_doc(doc: dict[str, Any]) -> UserRead:
    doc["id"] = str(doc["_id"])
    return UserRead(**doc)
