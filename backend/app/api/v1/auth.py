from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.repositories.user_repo import UserRepository
from app.models.user import UserCreate, UserRead, AuthProvider, user_from_doc
import httpx

router = APIRouter()


class OAuthExchangeRequest(BaseModel):
    access_token: str
    provider: str  # "google" | "github"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshRequest(BaseModel):
    refresh_token: str


async def _fetch_google_user(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code != 200:
            raise HTTPException(400, "Invalid Google access token")
        return resp.json()


async def _fetch_github_user(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"},
        )
        if resp.status_code != 200:
            raise HTTPException(400, "Invalid GitHub access token")
        data = resp.json()
        if not data.get("email"):
            emails_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails = emails_resp.json()
            primary = next((e["email"] for e in emails if e.get("primary")), None)
            data["email"] = primary
        return data


@router.post("/google", response_model=TokenResponse)
async def google_auth(body: OAuthExchangeRequest, db=Depends(get_db)):
    profile = await _fetch_google_user(body.access_token)
    user_data = UserCreate(
        email=profile["email"],
        name=profile.get("name", profile["email"].split("@")[0]),
        image=profile.get("picture"),
        provider=AuthProvider.google,
        provider_id=profile["id"],
    )
    repo = UserRepository(db)
    doc = await repo.upsert_oauth_user(user_data)
    user = user_from_doc(doc)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=user,
    )


@router.post("/github", response_model=TokenResponse)
async def github_auth(body: OAuthExchangeRequest, db=Depends(get_db)):
    profile = await _fetch_github_user(body.access_token)
    if not profile.get("email"):
        raise HTTPException(400, "GitHub account must have a public or verified email")
    user_data = UserCreate(
        email=profile["email"],
        name=profile.get("name") or profile.get("login", ""),
        image=profile.get("avatar_url"),
        provider=AuthProvider.github,
        provider_id=str(profile["id"]),
    )
    repo = UserRepository(db)
    doc = await repo.upsert_oauth_user(user_data)
    user = user_from_doc(doc)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=user,
    )


@router.post("/refresh")
async def refresh_token(body: RefreshRequest, db=Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(400, "Invalid refresh token")
    user_id = payload["sub"]
    repo = UserRepository(db)
    doc = await repo.find_by_id(user_id)
    if not doc:
        raise HTTPException(401, "User not found")
    return {"access_token": create_access_token(user_id), "token_type": "bearer"}
