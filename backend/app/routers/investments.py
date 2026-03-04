from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.models.user import User
from app.services import investment_service

router = APIRouter()


# --- Investments ---

@router.get("/portfolio")
async def portfolio_summary(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get portfolio summary with P&L."""
    return await investment_service.get_portfolio_summary(db, user.id)


@router.get("/")
async def list_investments(
    type: Optional[str] = None,
    broker: Optional[str] = None,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await investment_service.get_investments(db, user.id, type, broker)


@router.post("/")
async def create_investment(
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await investment_service.create_investment(db, user.id, data)


@router.get("/{investment_id}")
async def get_investment(
    investment_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    inv = await investment_service.get_investment_by_id(db, user.id, investment_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    return inv


@router.put("/{investment_id}")
async def update_investment(
    investment_id: UUID,
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    inv = await investment_service.update_investment(db, user.id, investment_id, data)
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    return inv


@router.delete("/{investment_id}")
async def delete_investment(
    investment_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await investment_service.delete_investment(db, user.id, investment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"status": "deleted"}


# --- Trades ---

@router.post("/{investment_id}/trades")
async def create_trade(
    investment_id: UUID,
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await investment_service.create_trade(db, user.id, investment_id, data)


@router.get("/trades/history")
async def trade_history(
    investment_id: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await investment_service.get_trades(db, user.id, investment_id, page, size)
    return {"items": items, "total": total, "page": page, "size": size}


# --- Dividends ---

@router.post("/{investment_id}/dividends")
async def create_dividend(
    investment_id: UUID,
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await investment_service.create_dividend(db, user.id, investment_id, data)


@router.get("/dividends/all")
async def list_dividends(
    investment_id: Optional[UUID] = None,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await investment_service.get_dividends(db, user.id, investment_id)
