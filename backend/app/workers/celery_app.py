"""Celery application configuration with beat schedule."""
import os
from celery import Celery
from celery.schedules import crontab


# Redis broker URL from env or default
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "vremya_dengi",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.workers.email_tasks",
        "app.workers.investment_tasks",
        "app.workers.notification_tasks",
        "app.workers.billing_tasks",
        "app.workers.analytics_tasks",
    ],
)

# ---- Celery configuration ------------------------------------------------
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,

    # Reliability
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,

    # Result backend
    result_expires=3600,  # 1 hour

    # Queues
    task_default_queue="default",
    task_routes={
        "app.workers.email_tasks.*": {"queue": "default"},
        "app.workers.investment_tasks.*": {"queue": "default"},
        "app.workers.notification_tasks.*": {"queue": "default"},
        "app.workers.billing_tasks.*": {"queue": "default"},
        "app.workers.analytics_tasks.*": {"queue": "periodic"},
    },

    # Retry policy
    task_default_retry_delay=60,  # 1 min
    task_max_retries=3,
)

# ---- Beat schedule (periodic tasks) --------------------------------------
celery_app.conf.beat_schedule = {
    # Every 5 minutes: process recurring transactions
    "process-recurring-transactions": {
        "task": "app.workers.analytics_tasks.process_recurring_transactions",
        "schedule": crontab(minute="*/5"),
        "options": {"queue": "periodic"},
    },

    # Every 15 minutes: sync investment portfolios
    "sync-investment-portfolios": {
        "task": "app.workers.investment_tasks.sync_all_portfolios",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "periodic"},
    },

    # Every hour: check subscription expirations
    "check-subscription-expiry": {
        "task": "app.workers.billing_tasks.check_subscription_expiry",
        "schedule": crontab(minute=0),
        "options": {"queue": "periodic"},
    },

    # Daily at 08:00 MSK: send daily summary notifications
    "send-daily-summary": {
        "task": "app.workers.notification_tasks.send_daily_summary_all",
        "schedule": crontab(hour=5, minute=0),  # 05:00 UTC = 08:00 MSK
        "options": {"queue": "periodic"},
    },

    # Daily at 09:00 MSK: calculate gamification XP
    "calculate-daily-xp": {
        "task": "app.workers.analytics_tasks.calculate_daily_xp",
        "schedule": crontab(hour=6, minute=0),  # 06:00 UTC = 09:00 MSK
        "options": {"queue": "periodic"},
    },

    # Daily at 02:00 MSK: cleanup old notifications
    "cleanup-old-notifications": {
        "task": "app.workers.notification_tasks.cleanup_old_notifications",
        "schedule": crontab(hour=23, minute=0),  # 23:00 UTC = 02:00 MSK
        "options": {"queue": "periodic"},
    },

    # Weekly Monday 10:00 MSK: send weekly report
    "send-weekly-report": {
        "task": "app.workers.email_tasks.send_weekly_report_all",
        "schedule": crontab(hour=7, minute=0, day_of_week=1),
        "options": {"queue": "periodic"},
    },

    # Monthly 1st at 10:00 MSK: generate monthly analytics
    "generate-monthly-analytics": {
        "task": "app.workers.analytics_tasks.generate_monthly_report",
        "schedule": crontab(hour=7, minute=0, day_of_month=1),
        "options": {"queue": "periodic"},
    },
}
