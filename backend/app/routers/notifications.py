from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.models.user import User
from app.services import notification_service

router = APIRouter()


@router.get("/")
async def list_notifications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await notification_service.get_notifications(
        db, user.id, page, size, unread_only
    )
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/unread-count")
async def unread_count(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.get_unread_count(db, user.id)
    return {"unread_count": count}


@router.put("/{notification_id}/read")
async def mark_read(
    notification_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    success = await notification_service.mark_as_read(db, user.id, notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "read"}


@router.put("/read-all")
async def mark_all_read(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.mark_all_as_read(db, user.id)
    return {"status": "all_read", "updated_count": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await notification_service.delete_notification(db, user.id, notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "deleted"}


@router.post("/check-budgets")
async def check_budget_alerts(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger budget alert check."""
    alerts = await notification_service.check_budget_alerts(db, user.id)
    return {"alerts_created": len(alerts)}
