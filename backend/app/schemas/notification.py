from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime


class NotificationCreate(BaseModel):
    type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=255)
    message: Optional[str] = None
    data: Optional[dict] = None


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: Optional[str] = None
    is_read: str
    data: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    unread_count: int


class NotificationMarkRead(BaseModel):
    notification_ids: List[UUID]
