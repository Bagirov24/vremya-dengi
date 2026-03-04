from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, update
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.models.investment import Notification


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    type: str,
    title: str,
    message: str,
    data: Optional[dict] = None,
) -> Notification:
    """Create a new notification for a user."""
    notif = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        data=data,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif


async def get_notifications(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    size: int = 20,
    unread_only: bool = False,
):
    """Get paginated notifications for a user."""
    query = select(Notification).where(Notification.user_id == user_id)

    if unread_only:
        query = query.where(Notification.is_read == "false")

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(desc(Notification.created_at)).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total


async def mark_as_read(
    db: AsyncSession, user_id: UUID, notification_id: UUID
) -> bool:
    """Mark a single notification as read."""
    result = await db.execute(
        select(Notification).where(
            and_(Notification.id == notification_id, Notification.user_id == user_id)
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        return False
    notif.is_read = "true"
    await db.flush()
    await db.commit()
    return True


async def mark_all_as_read(db: AsyncSession, user_id: UUID) -> int:
    """Mark all notifications as read. Returns count of updated."""
    stmt = (
        update(Notification)
        .where(
            and_(Notification.user_id == user_id, Notification.is_read == "false")
        )
        .values(is_read="true")
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def delete_notification(
    db: AsyncSession, user_id: UUID, notification_id: UUID
) -> bool:
    result = await db.execute(
        select(Notification).where(
            and_(Notification.id == notification_id, Notification.user_id == user_id)
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        return False
    await db.delete(notif)
    await db.commit()
    return True


async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
    """Get count of unread notifications."""
    result = await db.execute(
        select(func.count()).where(
            and_(Notification.user_id == user_id, Notification.is_read == "false")
        )
    )
    return result.scalar()


# --- Budget alert helper ---

async def check_budget_alerts(
    db: AsyncSession, user_id: UUID
):
    """Check all budgets and create alerts for those exceeding threshold."""
    from app.models.transaction import Budget

    now = datetime.utcnow()
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.user_id == user_id,
                Budget.start_date <= now,
                Budget.end_date >= now,
            )
        )
    )
    budgets = result.scalars().all()
    alerts = []

    for budget in budgets:
        if budget.limit_amount > 0:
            ratio = (budget.spent_amount or 0) / budget.limit_amount
            if ratio >= budget.alert_threshold:
                pct = int(ratio * 100)
                alert = await create_notification(
                    db=db,
                    user_id=user_id,
                    type="budget_alert",
                    title=f"\u0411\u044e\u0434\u0436\u0435\u0442 '{budget.category}' \u043f\u0440\u0435\u0432\u044b\u0448\u0435\u043d",
                    message=f"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u043e {pct}% \u0431\u044e\u0434\u0436\u0435\u0442\u0430 ({budget.spent_amount:.0f} \u0438\u0437 {budget.limit_amount:.0f})",
                    data={"budget_id": str(budget.id), "percentage": pct},
                )
                alerts.append(alert)

    return alerts
