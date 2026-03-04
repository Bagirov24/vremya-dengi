from pydantic import BaseModel, Field
from typing import Optional


class SettingsUpdate(BaseModel):
    currency: Optional[str] = Field(None, max_length=3)
    language: Optional[str] = Field(None, max_length=2)
    theme: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    email_digest_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None


class SettingsResponse(BaseModel):
    currency: str = "RUB"
    language: str = "ru"
    theme: str = "dark"
    timezone: str = "Europe/Moscow"
    email_digest_enabled: bool = True
    push_enabled: bool = True
    telegram_connected: bool = False
    telegram_chat_id: Optional[str] = None

    class Config:
        from_attributes = True


class TelegramConnect(BaseModel):
    chat_id: str = Field(..., max_length=50)


class BrokerKeyUpdate(BaseModel):
    tinkoff_api_key: Optional[str] = None
    finam_api_key: Optional[str] = None


class ExportRequest(BaseModel):
    format: str = Field(default="csv", pattern="^(csv|xlsx|pdf)$")
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    include_investments: bool = True
    include_transactions: bool = True
