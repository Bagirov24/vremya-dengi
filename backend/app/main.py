"""Vremya-Dengi API — FastAPI Application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base

# Routers
from app.routers import (
    auth,
    transactions,
    investments,
    billing,
    notifications,
    settings as settings_router,
    gamification,
    health,
    admin,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if needed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Personal finance management API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(investments.router, prefix="/api/v1/investments", tags=["investments"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(gamification.router, prefix="/api/v1/gamification", tags=["gamification"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Vremya-Dengi API", "version": "1.0.0", "status": "ok"}
