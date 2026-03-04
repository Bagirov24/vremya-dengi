from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from cryptography.fernet import Fernet
import json

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
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
async def get_profile(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "currency": user.currency,
        "language": user.language,
        "theme": user.theme,
        "timezone": user.timezone,
        "email_digest_enabled": user.email_digest_enabled,
        "push_enabled": user.push_enabled,
        "telegram_connected": user.telegram_connected,
        "has_tinkoff_key": bool(user.tinkoff_api_key),
        "has_finam_key": bool(user.finam_api_key),
    }


@router.put("/profile")
async def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    return {"status": "updated"}


@router.post("/broker-key")
async def set_broker_key(
    data: BrokerKeyUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    encrypted = fernet.encrypt(data.api_key.encode()).decode()
    if data.broker == "tinkoff":
        user.tinkoff_api_key = encrypted
    elif data.broker == "finam":
        user.finam_api_key = encrypted
    else:
        raise HTTPException(status_code=400, detail="Unknown broker")
    return {"status": "saved"}


@router.delete("/broker-key/{broker}")
async def delete_broker_key(
    broker: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if broker == "tinkoff":
        user.tinkoff_api_key = None
    elif broker == "finam":
        user.finam_api_key = None
    else:
        raise HTTPException(status_code=400, detail="Unknown broker")
    return {"status": "deleted"}


@router.get("/export")
async def export_data(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.transaction import Transaction
    result = await db.execute(select(Transaction).where(Transaction.user_id == user.id))
    transactions = result.scalars().all()
    data = {
        "user": {"email": user.email, "full_name": user.full_name},
        "transactions": [
            {
                "type": t.type.value,
                "amount": t.amount,
                "category": t.category,
                "date": str(t.date),
                "description": t.description,
            }
            for t in transactions
        ],
    }
    return data
