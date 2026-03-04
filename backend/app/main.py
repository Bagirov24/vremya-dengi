"""Vremya-Dengi API — FastAPI Application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis import redis_client
from app.middleware.rate_limiter import RateLimiterMiddleware

# Routers
from app.routers import (
    auth, transactions, budgets, goals,
    analytics, investments, recurring,
    notifications, settings as settings_router,
    billing, webhooks, events, telegram,
    health, export,
)
from app.routers.admin import users as admin_users
from app.routers.admin import metrics as admin_metrics
from app.routers.admin import feature_flags as admin_flags
from app.routers.admin import system as admin_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.connect()
    yield
    # Shutdown
    await redis_client.disconnect()


app = FastAPI(
    title="Vremya-Dengi API",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.APP_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
app.add_middleware(RateLimiterMiddleware)

# --- Include Routers ---
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(investments.router, prefix="/api/investments", tags=["Investments"])
app.include_router(recurring.router, prefix="/api/recurring", tags=["Recurring"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["Telegram"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

# Admin
app.include_router(admin_users.router, prefix="/api/admin/users", tags=["Admin"])
app.include_router(admin_metrics.router, prefix="/api/admin/metrics", tags=["Admin"])
app.include_router(admin_flags.router, prefix="/api/admin/features", tags=["Admin"])
app.include_router(admin_system.router, prefix="/api/admin/system", tags=["Admin"])
