"""Notification tasks: in-app, push, daily summary, cleanup."""
import logging
import asyncio
import json
from datetime import datetime, timedelta

from pywebpush import webpush, WebPushException
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.config import settings
from app.models import Notification, User, Transaction

logger = logging.getLogger(__name__)

_engine = create_async_engine(settings.DATABASE_URL, pool_size=5)
_async_session = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(bind=True, max_retries=2)
def create_notification(self, user_id: int, title: str, message: str, type: str = "info"):
    """Create in-app notification for user."""
    async def _run():
        async with _async_session() as session:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type,
                is_read=False,
                created_at=datetime.utcnow(),
            )
            session.add(notification)
            await session.commit()
            logger.info("Notification created for user %s: %s", user_id, title)
            return {"notification_id": notification.id}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_push_notification(self, user_id: int, title: str, body: str, url: str = None):
    """Send web push notification."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user or not user.push_subscription:
                return {"status": "no_subscription"}

            try:
                subscription_info = json.loads(user.push_subscription)
                payload = json.dumps({
                    "title": title,
                    "body": body,
                    "url": url or f"{settings.APP_URL}/notifications",
                    "icon": f"{settings.APP_URL}/icon-192.png",
                })

                webpush(
                    subscription_info=subscription_info,
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY if hasattr(settings, 'VAPID_PRIVATE_KEY') else "",
                    vapid_claims={"sub": f"mailto:{settings.EMAIL_FROM}"},
                )
                logger.info("Push sent to user %s: %s", user_id, title)
                return {"status": "sent"}
            except WebPushException as exc:
                logger.error("Push failed for user %s: %s", user_id, exc)
                if exc.response and exc.response.status_code == 410:
                    # Subscription expired, clear it
                    user.push_subscription = None
                    await session.commit()
                    return {"status": "subscription_expired"}
                raise

    try:
        return asyncio.run(_run())
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2)
def send_daily_summary_all(self):
    """Send daily summary notification to all users."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(User).where(User.is_active == True)
            )
            users = result.scalars().all()

            today = datetime.utcnow().date()
            yesterday = today - timedelta(days=1)

            dispatched = 0
            for user in users:
                try:
                    # Count yesterday's transactions
                    tx_result = await session.execute(
                        select(func.count(Transaction.id), func.sum(Transaction.amount))
                        .where(
                            Transaction.user_id == user.id,
                            Transaction.type == "expense",
                            func.date(Transaction.created_at) == yesterday,
                        )
                    )
                    row = tx_result.fetchone()
                    tx_count = row[0] or 0
                    tx_total = abs(row[1] or 0)

                    if tx_count > 0:
                        create_notification.delay(
                            user_id=user.id,
                            title="Itogi dnya",
                            message=f"Vchera: {tx_count} operatsiy na summu {tx_total:.0f} RUB",
                            type="daily_summary",
                        )
                        dispatched += 1
                except Exception as exc:
                    logger.error("Daily summary failed for user %s: %s", user.id, exc)

            return {"dispatched": dispatched}

    return asyncio.run(_run())


@celery_app.task(bind=True)
def cleanup_old_notifications(self):
    """Delete notifications older than 90 days."""
    async def _run():
        cutoff = datetime.utcnow() - timedelta(days=90)
        async with _async_session() as session:
            result = await session.execute(
                delete(Notification).where(
                    Notification.created_at < cutoff,
                    Notification.is_read == True,
                )
            )
            deleted = result.rowcount
            await session.commit()
            logger.info("Cleaned up %d old notifications", deleted)
            return {"deleted": deleted}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2)
def send_budget_warning(self, user_id: int, category: str, pct: int):
    """Notify user about budget threshold (80%, 90%, 100%)."""
    thresholds = {
        80: "Vy potratili 80% byudzheta",
        90: "Vy potratili 90% byudzheta",
        100: "Byudzhet prevyshen!",
    }
    msg = thresholds.get(pct, f"Byudzhet ispolzovan na {pct}%")

    create_notification.delay(
        user_id=user_id,
        title=f"{category}: {msg}",
        message=f"Kategoriya '{category}' — {pct}% byudzheta ispolzovano.",
        type="budget_warning",
    )

    # Also send push
    send_push_notification.delay(
        user_id=user_id,
        title=f"{category}: {pct}%",
        body=msg,
        url=f"{settings.APP_URL}/transactions",
    )

    return {"user_id": user_id, "category": category, "pct": pct}
