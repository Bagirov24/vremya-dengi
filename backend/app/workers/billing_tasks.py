"""Billing and subscription management tasks."""
import logging
import asyncio
from datetime import datetime, timedelta

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.config import settings
from app.models import User, Subscription

logger = logging.getLogger(__name__)

_engine = create_async_engine(settings.DATABASE_URL, pool_size=5)
_async_session = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

stripe.api_key = settings.STRIPE_SECRET_KEY


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_stripe_webhook(self, event_type: str, event_data: dict):
    """Process Stripe webhook event asynchronously."""
    async def _run():
        async with _async_session() as session:
            customer_id = event_data.get("customer")
            if not customer_id:
                return {"status": "no_customer"}

            result = await session.execute(
                select(User).where(User.stripe_customer_id == customer_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                logger.warning("No user found for Stripe customer %s", customer_id)
                return {"status": "user_not_found"}

            if event_type == "customer.subscription.created":
                sub = event_data.get("items", {}).get("data", [{}])[0]
                plan_id = sub.get("price", {}).get("id", "")
                plan_name = "Pro Monthly" if plan_id == settings.STRIPE_PRO_MONTHLY_PRICE_ID else "Pro Yearly"

                user.plan = "pro"
                user.subscription_id = event_data.get("id")
                await session.commit()

                from app.workers.email_tasks import send_subscription_email
                send_subscription_email.delay(user.email, plan_name, "activated")

            elif event_type == "customer.subscription.deleted":
                user.plan = "free"
                user.subscription_id = None
                await session.commit()

                from app.workers.email_tasks import send_subscription_email
                send_subscription_email.delay(user.email, "Free", "cancelled")

            elif event_type == "invoice.payment_failed":
                from app.workers.notification_tasks import create_notification
                create_notification.delay(
                    user_id=user.id,
                    title="Oshibka oplaty",
                    message="Ne udalos obnovit podpisku. Provertte platezhnye dannye.",
                    type="billing_error",
                )

            logger.info("Processed Stripe event %s for user %s", event_type, user.id)
            return {"status": "processed", "event_type": event_type}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2)
def check_subscription_expiry(self):
    """Check for subscriptions expiring within 3 days and notify users."""
    async def _run():
        async with _async_session() as session:
            expiry_threshold = datetime.utcnow() + timedelta(days=3)

            result = await session.execute(
                select(User).where(
                    User.plan == "pro",
                    User.subscription_end.isnot(None),
                    User.subscription_end <= expiry_threshold,
                    User.subscription_end > datetime.utcnow(),
                )
            )
            users = result.scalars().all()

            notified = 0
            for user in users:
                days_left = (user.subscription_end - datetime.utcnow()).days

                from app.workers.notification_tasks import create_notification
                create_notification.delay(
                    user_id=user.id,
                    title="Podpiska istekaet",
                    message=f"Vasha Pro podpiska istekaet cherez {days_left} dn. Prodlite ee.",
                    type="billing_warning",
                )

                from app.workers.email_tasks import send_subscription_email
                send_subscription_email.delay(user.email, "Pro", "expiring")
                notified += 1

            # Also downgrade expired subscriptions
            expired_result = await session.execute(
                select(User).where(
                    User.plan == "pro",
                    User.subscription_end.isnot(None),
                    User.subscription_end <= datetime.utcnow(),
                )
            )
            expired_users = expired_result.scalars().all()

            downgraded = 0
            for user in expired_users:
                user.plan = "free"
                downgraded += 1

            if downgraded > 0:
                await session.commit()

            logger.info("Subscription check: %d notified, %d downgraded", notified, downgraded)
            return {"notified": notified, "downgraded": downgraded}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def sync_stripe_subscription(self, user_id: int):
    """Sync subscription status from Stripe."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user or not user.stripe_customer_id:
                return {"status": "no_stripe_customer"}

            try:
                subscriptions = stripe.Subscription.list(
                    customer=user.stripe_customer_id,
                    status="active",
                    limit=1,
                )

                if subscriptions.data:
                    sub = subscriptions.data[0]
                    user.plan = "pro"
                    user.subscription_id = sub.id
                    user.subscription_end = datetime.fromtimestamp(sub.current_period_end)
                else:
                    user.plan = "free"
                    user.subscription_id = None

                await session.commit()
                return {"user_id": user_id, "plan": user.plan}

            except stripe.error.StripeError as exc:
                logger.error("Stripe sync failed for user %s: %s", user_id, exc)
                raise

    try:
        return asyncio.run(_run())
    except Exception as exc:
        self.retry(exc=exc)
