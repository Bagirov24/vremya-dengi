from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.models.user import User


VALID_CURRENCIES = ["RUB", "USD", "EUR", "GBP", "CNY", "TRY"]
VALID_LANGUAGES = ["ru", "en"]
VALID_THEMES = ["dark", "light", "system"]


async def get_settings(user: User) -> dict:
    """Get current user settings."""
    return {
        "currency": user.currency or "RUB",
        "language": user.language or "ru",
        "theme": user.theme or "dark",
        "timezone": user.timezone or "Europe/Moscow",
        "email_digest_enabled": user.email_digest_enabled,
        "push_enabled": user.push_enabled,
        "telegram_connected": user.telegram_connected,
        "telegram_chat_id": user.telegram_chat_id,
    }


async def update_settings(
    db: AsyncSession,
    user: User,
    data: dict,
) -> dict:
    """Update user settings. Returns updated settings."""
    allowed_fields = {
        "currency", "language", "theme", "timezone",
        "email_digest_enabled", "push_enabled",
    }

    for key, value in data.items():
        if key not in allowed_fields or value is None:
            continue

        # Validation
        if key == "currency" and value not in VALID_CURRENCIES:
            continue
        if key == "language" and value not in VALID_LANGUAGES:
            continue
        if key == "theme" and value not in VALID_THEMES:
            continue

        setattr(user, key, value)

    user.updated_at = datetime.utcnow()
    await db.flush()
    await db.commit()
    await db.refresh(user)

    return await get_settings(user)


async def connect_telegram(
    db: AsyncSession, user: User, chat_id: str
) -> dict:
    """Connect Telegram bot to user account."""
    user.telegram_chat_id = chat_id
    user.telegram_connected = True
    user.updated_at = datetime.utcnow()
    await db.flush()
    await db.commit()
    return {"status": "connected", "chat_id": chat_id}


async def disconnect_telegram(db: AsyncSession, user: User) -> dict:
    """Disconnect Telegram bot."""
    user.telegram_chat_id = None
    user.telegram_connected = False
    user.updated_at = datetime.utcnow()
    await db.flush()
    await db.commit()
    return {"status": "disconnected"}


async def update_push_subscription(
    db: AsyncSession, user: User, subscription: dict
) -> dict:
    """Save push notification subscription data."""
    user.push_subscription = subscription
    user.push_enabled = True
    user.updated_at = datetime.utcnow()
    await db.flush()
    await db.commit()
    return {"status": "subscribed"}


async def export_user_data(user: User) -> dict:
    """Export all user data for GDPR compliance."""
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "settings": {
            "currency": user.currency,
            "language": user.language,
            "theme": user.theme,
            "timezone": user.timezone,
        },
        "subscription": {
            "plan": user.subscription_plan.value if user.subscription_plan else "free",
            "expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
        },
    }
