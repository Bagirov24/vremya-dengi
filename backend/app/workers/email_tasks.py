"""Email-related Celery tasks: transactional emails, reports, alerts."""
import logging
from datetime import datetime, timedelta

import resend
from jinja2 import Template
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.config import settings
from app.models import User, Transaction

logger = logging.getLogger(__name__)

# Async engine for DB access inside tasks
_engine = create_async_engine(settings.DATABASE_URL, pool_size=5)
_async_session = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


def _send_email(to: str, subject: str, html: str) -> dict:
    """Send email via Resend API."""
    if not settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, skipping email to %s", to)
        return {"status": "skipped"}

    resend.api_key = settings.RESEND_API_KEY
    try:
        result = resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to],
            "subject": subject,
            "html": html,
        })
        logger.info("Email sent to %s: %s", to, subject)
        return {"status": "sent", "id": result.get("id")}
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
        raise


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def send_welcome_email(self, user_id: int, email: str, name: str):
    """Send welcome email after registration."""
    try:
        html = f"""
        <h1>Dobro pozhalovat v Vremya Dengi, {name}!</h1>
        <p>Vash akkaunt uspeshno sozdan.</p>
        <p>Nachnite otslezhivat svoi finansy pramo seychas.</p>
        <a href="{settings.APP_URL}/dashboard">Otkryt dashboard</a>
        """
        return _send_email(email, "Dobro pozhalovat v Vremya Dengi!", html)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def send_password_reset_email(self, email: str, reset_token: str):
    """Send password reset link."""
    try:
        reset_url = f"{settings.APP_URL}/auth/reset-password?token={reset_token}"
        html = f"""
        <h2>Sbros parolya</h2>
        <p>Vy zaprosili sbros parolya. Nazmite ssylku nizhe:</p>
        <a href="{reset_url}">Sbrosit parol</a>
        <p>Ssylka deystvitelna 1 chas.</p>
        """
        return _send_email(email, "Sbros parolya - Vremya Dengi", html)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def send_budget_alert_email(self, user_id: int, email: str, category: str, spent: float, limit: float):
    """Alert user when spending approaches budget limit."""
    try:
        pct = int((spent / limit) * 100) if limit > 0 else 0
        html = f"""
        <h2>Preduprezhdenie o byudzhete</h2>
        <p>Vy potratili <strong>{spent:.2f} RUB</strong> iz <strong>{limit:.2f} RUB</strong>
        v kategorii <strong>{category}</strong> ({pct}%).</p>
        <a href="{settings.APP_URL}/dashboard">Posmotret podrobnosti</a>
        """
        return _send_email(email, f"Byudzhet {category}: {pct}% ispolzovano", html)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2)
def send_weekly_report_email(self, user_id: int, email: str, report_data: dict):
    """Send weekly financial report to a single user."""
    try:
        html = f"""
        <h2>Vash ezhenedelnyy otchet</h2>
        <p><strong>Period:</strong> {report_data.get('period', 'N/A')}</p>
        <p><strong>Dokhody:</strong> {report_data.get('income', 0):.2f} RUB</p>
        <p><strong>Raskhody:</strong> {report_data.get('expenses', 0):.2f} RUB</p>
        <p><strong>Ekonomiya:</strong> {report_data.get('savings', 0):.2f} RUB</p>
        <p><strong>Top kategorii rashodov:</strong></p>
        <ul>
        {''.join(f"<li>{c['name']}: {c['amount']:.2f} RUB</li>" for c in report_data.get('top_categories', []))}
        </ul>
        <a href="{settings.APP_URL}/dashboard">Podrobnyy analiz</a>
        """
        return _send_email(email, "Ezhenedelnyy finansovyy otchet", html)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2)
def send_weekly_report_all(self):
    """Generate and send weekly reports to all active users."""
    import asyncio

    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(User).where(User.is_active == True)
            )
            users = result.scalars().all()

            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)

            for user in users:
                try:
                    # Get user transactions for the week
                    tx_result = await session.execute(
                        select(Transaction).where(
                            Transaction.user_id == user.id,
                            Transaction.created_at >= week_ago,
                        )
                    )
                    transactions = tx_result.scalars().all()

                    income = sum(t.amount for t in transactions if t.type == "income")
                    expenses = sum(abs(t.amount) for t in transactions if t.type == "expense")

                    # Aggregate by category
                    cat_totals = {}
                    for t in transactions:
                        if t.type == "expense":
                            cat_totals[t.category] = cat_totals.get(t.category, 0) + abs(t.amount)

                    top_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:5]

                    report_data = {
                        "period": f"{week_ago.strftime('%d.%m')} - {now.strftime('%d.%m.%Y')}",
                        "income": income,
                        "expenses": expenses,
                        "savings": income - expenses,
                        "top_categories": [{"name": n, "amount": a} for n, a in top_cats],
                    }

                    send_weekly_report_email.delay(user.id, user.email, report_data)
                except Exception as exc:
                    logger.error("Failed to generate report for user %s: %s", user.id, exc)

    asyncio.run(_run())
    return {"status": "weekly_reports_dispatched"}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_subscription_email(self, email: str, plan: str, action: str):
    """Send subscription-related email (upgrade, downgrade, cancel)."""
    try:
        subjects = {
            "activated": f"Podpiska {plan} aktivirovana",
            "cancelled": "Podpiska otmenena",
            "expiring": "Vasha podpiska istekaet",
        }
        html = f"""
        <h2>Podpiska {plan}</h2>
        <p>Status: <strong>{action}</strong></p>
        <a href="{settings.APP_URL}/billing">Upravlenie podpiskoy</a>
        """
        return _send_email(email, subjects.get(action, "Obnovlenie podpiski"), html)
    except Exception as exc:
        self.retry(exc=exc)
