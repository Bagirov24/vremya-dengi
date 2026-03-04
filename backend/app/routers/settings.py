from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from cryptography.fernet import Fernet

from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.models.user import User
from app.services import settings_service
from app.config import settings

router = APIRouter()
fernet = Fernet(settings.SECRET_KEY.encode().ljust(32)[:32])


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None
    email_digest_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None


class BrokerKeyUpdate(BaseModel):
    broker: str  # tinkoff / finam
    api_key: str


@router.get("/profile")
async def get_profile(
    user: User = Depends(get_current_active_user),
):
    """Get user profile and settings."""
    user_settings = await settings_service.get_settings(user)
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "is_verified": user.is_verified,
        "xp": user.xp,
        "level": user.level,
        "streak_days": user.streak_days,
        **user_settings,
    }


@router.put("/profile")
async def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile and settings."""
    update_data = data.model_dump(exclude_unset=True)

    # Handle full_name separately
    if "full_name" in update_data:
        user.full_name = update_data.pop("full_name")

    if update_data:
        result = await settings_service.update_settings(db, user, update_data)
    else:
        await db.flush()
        await db.commit()
        result = await settings_service.get_settings(user)

    return result


@router.post("/broker-key")
async def update_broker_key(
    data: BrokerKeyUpdate,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Save encrypted broker API key."""
    encrypted = fernet.encrypt(data.api_key.encode()).decode()

    if data.broker == "tinkoff":
        user.tinkoff_api_key = encrypted
    elif data.broker == "finam":
        user.finam_api_key = encrypted
    else:
        raise HTTPException(status_code=400, detail="Invalid broker")

    await db.flush()
    await db.commit()
    return {"status": "saved", "broker": data.broker}


@router.delete("/broker-key/{broker}")
async def delete_broker_key(
    broker: str,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if broker == "tinkoff":
        user.tinkoff_api_key = None
    elif broker == "finam":
        user.finam_api_key = None
    else:
        raise HTTPException(status_code=400, detail="Invalid broker")

    await db.flush()
    await db.commit()
    return {"status": "deleted", "broker": broker}


@router.post("/telegram/connect")
async def connect_telegram(
    chat_id: str,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await settings_service.connect_telegram(db, user, chat_id)


@router.post("/telegram/disconnect")
async def disconnect_telegram(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await settings_service.disconnect_telegram(db, user)


@router.post("/push-subscription")
async def save_push_subscription(
    subscription: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await settings_service.update_push_subscription(db, user, subscription)


@router.get("/export")
async def export_data(
    user: User = Depends(get_current_active_user),
):
    """Export user data (GDPR compliance)."""
    return await settings_service.export_user_data(user)
