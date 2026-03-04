"""Analytics, gamification, and recurring transaction tasks."""
import logging
import asyncio
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.config import settings
from app.models import User, Transaction, Gamification

logger = logging.getLogger(__name__)

_engine = create_async_engine(settings.DATABASE_URL, pool_size=5)
_async_session = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(bind=True, max_retries=2)
def process_recurring_transactions(self):
    """Process recurring transactions (subscriptions, salary, rent, etc.)."""
    async def _run():
        async with _async_session() as session:
            now = datetime.utcnow()

            # Find recurring transactions due today
            result = await session.execute(
                select(Transaction).where(
                    Transaction.is_recurring == True,
                    Transaction.next_recurrence <= now,
                )
            )
            recurring = result.scalars().all()

            created = 0
            for tx in recurring:
                # Create new transaction based on recurring template
                new_tx = Transaction(
                    user_id=tx.user_id,
                    amount=tx.amount,
                    type=tx.type,
                    category=tx.category,
                    description=f"{tx.description} (auto)",
                    is_recurring=False,
                    created_at=now,
                )
                session.add(new_tx)

                # Calculate next recurrence
                freq = tx.recurrence_frequency or "monthly"
                if freq == "daily":
                    tx.next_recurrence = now + timedelta(days=1)
                elif freq == "weekly":
                    tx.next_recurrence = now + timedelta(weeks=1)
                elif freq == "monthly":
                    tx.next_recurrence = now + relativedelta(months=1)
                elif freq == "yearly":
                    tx.next_recurrence = now + relativedelta(years=1)

                created += 1

            if created > 0:
                await session.commit()

            logger.info("Processed %d recurring transactions", created)
            return {"created": created}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2)
def calculate_daily_xp(self):
    """Calculate and award daily XP for all active users."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(User).where(User.is_active == True)
            )
            users = result.scalars().all()

            yesterday = datetime.utcnow().date() - timedelta(days=1)
            updated = 0

            for user in users:
                try:
                    # Count yesterday's transactions
                    tx_result = await session.execute(
                        select(func.count(Transaction.id)).where(
                            Transaction.user_id == user.id,
                            func.date(Transaction.created_at) == yesterday,
                        )
                    )
                    tx_count = tx_result.scalar() or 0

                    if tx_count == 0:
                        continue

                    # XP rules
                    xp_earned = 0
                    xp_earned += min(tx_count * 10, 50)  # 10 XP per tx, max 50

                    # Streak bonus: check if user logged tx every day this week
                    week_ago = yesterday - timedelta(days=6)
                    streak_result = await session.execute(
                        select(func.count(func.distinct(func.date(Transaction.created_at)))).where(
                            Transaction.user_id == user.id,
                            func.date(Transaction.created_at) >= week_ago,
                            func.date(Transaction.created_at) <= yesterday,
                        )
                    )
                    streak_days = streak_result.scalar() or 0
                    if streak_days >= 7:
                        xp_earned += 100  # Weekly streak bonus
                    elif streak_days >= 3:
                        xp_earned += 25  # 3-day streak

                    # Update gamification record
                    gam_result = await session.execute(
                        select(Gamification).where(Gamification.user_id == user.id)
                    )
                    gam = gam_result.scalar_one_or_none()

                    if gam:
                        gam.xp = (gam.xp or 0) + xp_earned
                        gam.streak_days = streak_days
                        # Level up: every 500 XP
                        gam.level = (gam.xp // 500) + 1
                        gam.updated_at = datetime.utcnow()
                    else:
                        new_gam = Gamification(
                            user_id=user.id,
                            xp=xp_earned,
                            level=1,
                            streak_days=streak_days,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                        session.add(new_gam)

                    updated += 1

                except Exception as exc:
                    logger.error("XP calc failed for user %s: %s", user.id, exc)

            await session.commit()
            logger.info("Daily XP calculated for %d users", updated)
            return {"users_updated": updated}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2)
def generate_monthly_report(self):
    """Generate monthly analytics snapshot for all users."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(User).where(User.is_active == True)
            )
            users = result.scalars().all()

            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            prev_month_start = month_start - relativedelta(months=1)

            reports_generated = 0
            for user in users:
                try:
                    # Current month stats
                    income_result = await session.execute(
                        select(func.sum(Transaction.amount)).where(
                            Transaction.user_id == user.id,
                            Transaction.type == "income",
                            Transaction.created_at >= prev_month_start,
                            Transaction.created_at < month_start,
                        )
                    )
                    income = income_result.scalar() or 0

                    expense_result = await session.execute(
                        select(func.sum(Transaction.amount)).where(
                            Transaction.user_id == user.id,
                            Transaction.type == "expense",
                            Transaction.created_at >= prev_month_start,
                            Transaction.created_at < month_start,
                        )
                    )
                    expenses = abs(expense_result.scalar() or 0)

                    # Top spending categories
                    cat_result = await session.execute(
                        select(
                            Transaction.category,
                            func.sum(Transaction.amount).label("total")
                        ).where(
                            Transaction.user_id == user.id,
                            Transaction.type == "expense",
                            Transaction.created_at >= prev_month_start,
                            Transaction.created_at < month_start,
                        ).group_by(Transaction.category)
                        .order_by(func.sum(Transaction.amount))
                        .limit(5)
                    )
                    top_cats = [{"name": r[0], "amount": abs(r[1])} for r in cat_result.fetchall()]

                    # Send notification with monthly summary
                    from app.workers.notification_tasks import create_notification
                    savings = float(income) - float(expenses)
                    month_name = prev_month_start.strftime("%B %Y")

                    create_notification.delay(
                        user_id=user.id,
                        title=f"Otchet za {month_name}",
                        message=f"Dokhody: {float(income):.0f} RUB | Raskhody: {float(expenses):.0f} RUB | Ekonomiya: {savings:.0f} RUB",
                        type="monthly_report",
                    )
                    reports_generated += 1

                except Exception as exc:
                    logger.error("Monthly report failed for user %s: %s", user.id, exc)

            logger.info("Generated monthly reports for %d users", reports_generated)
            return {"reports_generated": reports_generated}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2)
def check_budget_limits(self, user_id: int):
    """Check all budget limits for a user after a new transaction."""
    async def _run():
        async with _async_session() as session:
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0)

            # Get user's budget limits (stored in settings or a Budget model)
            user_result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                return

            # Get spending by category this month
            cat_result = await session.execute(
                select(
                    Transaction.category,
                    func.sum(Transaction.amount).label("total")
                ).where(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    Transaction.created_at >= month_start,
                ).group_by(Transaction.category)
            )

            warnings_sent = 0
            for category, total in cat_result.fetchall():
                spent = abs(total)
                # Default budget limit per category (could be from user settings)
                limit = 50000  # placeholder default

                pct = int((spent / limit) * 100) if limit > 0 else 0

                if pct >= 100:
                    from app.workers.notification_tasks import send_budget_warning
                    send_budget_warning.delay(user_id, category, 100)
                    warnings_sent += 1
                elif pct >= 90:
                    from app.workers.notification_tasks import send_budget_warning
                    send_budget_warning.delay(user_id, category, 90)
                    warnings_sent += 1
                elif pct >= 80:
                    from app.workers.notification_tasks import send_budget_warning
                    send_budget_warning.delay(user_id, category, 80)
                    warnings_sent += 1

            return {"warnings_sent": warnings_sent}

    return asyncio.run(_run())
