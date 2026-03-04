from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.investment import Investment, Trade, Dividend, InvestmentType, BrokerType

router = APIRouter()


class InvestmentCreate(BaseModel):
    broker: str = "manual"
    type: str
    ticker: str
    name: str
    quantity: float = 0
    avg_price: float = 0
    current_price: float = 0
    currency: str = "RUB"
    sector: Optional[str] = None


class TradeCreate(BaseModel):
    investment_id: str
    action: str  # buy / sell
    quantity: float
    price: float
    commission: float = 0
    date: Optional[datetime] = None
    note: Optional[str] = None


class DividendCreate(BaseModel):
    investment_id: str
    amount: float
    tax: float = 0
    payment_date: datetime
    currency: str = "RUB"


@router.get("")
async def get_investments(
    broker: Optional[str] = None,
    type: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Investment).where(Investment.user_id == user.id)
    if broker:
        query = query.where(Investment.broker == broker)
    if type:
        query = query.where(Investment.type == type)
    query = query.order_by(Investment.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("")
async def create_investment(
    data: InvestmentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inv = Investment(
        user_id=user.id,
        broker=BrokerType(data.broker),
        type=InvestmentType(data.type),
        ticker=data.ticker,
        name=data.name,
        quantity=data.quantity,
        avg_price=data.avg_price,
        current_price=data.current_price,
        currency=data.currency,
        sector=data.sector,
    )
    db.add(inv)
    await db.flush()
    return inv


@router.get("/portfolio")
async def get_portfolio(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Investment).where(Investment.user_id == user.id)
    )
    investments = result.scalars().all()
    total_value = sum(i.quantity * i.current_price for i in investments)
    total_cost = sum(i.quantity * i.avg_price for i in investments)
    total_pnl = total_value - total_cost
    pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0

    by_type = {}
    for inv in investments:
        t = inv.type.value if inv.type else "other"
        if t not in by_type:
            by_type[t] = 0
        by_type[t] += inv.quantity * inv.current_price

    return {
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_pnl": round(total_pnl, 2),
        "pnl_percent": round(pnl_percent, 2),
        "positions_count": len(investments),
        "by_type": by_type,
    }


@router.delete("/{inv_id}")
async def delete_investment(
    inv_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Investment).where(and_(Investment.id == inv_id, Investment.user_id == user.id))
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    await db.delete(inv)
    return {"status": "deleted"}


# --- Trades ---
@router.post("/trades")
async def create_trade(
    data: TradeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trade = Trade(
        investment_id=data.investment_id,
        user_id=user.id,
        action=data.action,
        quantity=data.quantity,
        price=data.price,
        commission=data.commission,
        date=data.date or datetime.utcnow(),
        note=data.note,
    )
    db.add(trade)
    await db.flush()
    return trade


@router.get("/trades/{inv_id}")
async def get_trades(
    inv_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trade).where(and_(Trade.investment_id == inv_id, Trade.user_id == user.id)).order_by(Trade.date.desc())
    )
    return result.scalars().all()


# --- Dividends ---
@router.post("/dividends")
async def create_dividend(
    data: DividendCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    div = Dividend(
        investment_id=data.investment_id,
        user_id=user.id,
        amount=data.amount,
        tax=data.tax,
        payment_date=data.payment_date,
        currency=data.currency,
    )
    db.add(div)
    await db.flush()
    return div


@router.get("/dividends/{inv_id}")
async def get_dividends(
    inv_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dividend).where(and_(Dividend.investment_id == inv_id, Dividend.user_id == user.id)).order_by(Dividend.payment_date.desc())
    )
    return result.scalars().all()
