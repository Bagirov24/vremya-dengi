from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.models.investment import Investment, Trade, Dividend, InvestmentType


# --- Investment CRUD ---

async def create_investment(
    db: AsyncSession, user_id: UUID, data: dict
) -> Investment:
    inv = Investment(user_id=user_id, **data)
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return inv


async def get_investments(
    db: AsyncSession,
    user_id: UUID,
    type_filter: Optional[str] = None,
    broker_filter: Optional[str] = None,
) -> List[Investment]:
    query = select(Investment).where(Investment.user_id == user_id)
    if type_filter:
        query = query.where(Investment.type == type_filter)
    if broker_filter:
        query = query.where(Investment.broker == broker_filter)
    query = query.order_by(desc(Investment.created_at))
    result = await db.execute(query)
    return result.scalars().all()


async def get_investment_by_id(
    db: AsyncSession, user_id: UUID, investment_id: UUID
) -> Optional[Investment]:
    result = await db.execute(
        select(Investment).where(
            and_(Investment.id == investment_id, Investment.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def update_investment(
    db: AsyncSession, user_id: UUID, investment_id: UUID, data: dict
) -> Optional[Investment]:
    inv = await get_investment_by_id(db, user_id, investment_id)
    if not inv:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(inv, key, value)
    inv.last_updated = datetime.utcnow()
    await db.flush()
    await db.commit()
    await db.refresh(inv)
    return inv


async def delete_investment(
    db: AsyncSession, user_id: UUID, investment_id: UUID
) -> bool:
    inv = await get_investment_by_id(db, user_id, investment_id)
    if not inv:
        return False
    await db.delete(inv)
    await db.commit()
    return True


# --- Trade CRUD ---

async def create_trade(
    db: AsyncSession, user_id: UUID, investment_id: UUID, data: dict
) -> Trade:
    trade = Trade(user_id=user_id, investment_id=investment_id, **data)
    db.add(trade)

    # Update investment avg_price and quantity
    inv = await get_investment_by_id(db, user_id, investment_id)
    if inv:
        if data.get("action") == "buy":
            total_cost = (inv.avg_price * inv.quantity) + (data["price"] * data["quantity"])
            inv.quantity += data["quantity"]
            inv.avg_price = total_cost / inv.quantity if inv.quantity > 0 else 0
        elif data.get("action") == "sell":
            inv.quantity = max(0, inv.quantity - data["quantity"])
        inv.last_updated = datetime.utcnow()

    await db.flush()
    await db.commit()
    await db.refresh(trade)
    return trade


async def get_trades(
    db: AsyncSession,
    user_id: UUID,
    investment_id: Optional[UUID] = None,
    page: int = 1,
    size: int = 20,
):
    query = select(Trade).where(Trade.user_id == user_id)
    if investment_id:
        query = query.where(Trade.investment_id == investment_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(desc(Trade.date)).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()
    return items, total


# --- Dividend CRUD ---

async def create_dividend(
    db: AsyncSession, user_id: UUID, investment_id: UUID, data: dict
) -> Dividend:
    div = Dividend(user_id=user_id, investment_id=investment_id, **data)
    db.add(div)
    await db.commit()
    await db.refresh(div)
    return div


async def get_dividends(
    db: AsyncSession, user_id: UUID, investment_id: Optional[UUID] = None
) -> List[Dividend]:
    query = select(Dividend).where(Dividend.user_id == user_id)
    if investment_id:
        query = query.where(Dividend.investment_id == investment_id)
    query = query.order_by(desc(Dividend.payment_date))
    result = await db.execute(query)
    return result.scalars().all()


# --- Portfolio Summary ---

async def get_portfolio_summary(db: AsyncSession, user_id: UUID):
    """Calculate total portfolio value and P&L."""
    investments = await get_investments(db, user_id)

    total_value = 0.0
    total_invested = 0.0
    by_type = {}

    for inv in investments:
        market_value = inv.quantity * inv.current_price
        cost_basis = inv.quantity * inv.avg_price
        total_value += market_value
        total_invested += cost_basis

        type_key = inv.type.value if hasattr(inv.type, 'value') else str(inv.type)
        if type_key not in by_type:
            by_type[type_key] = {"value": 0, "invested": 0, "count": 0}
        by_type[type_key]["value"] += market_value
        by_type[type_key]["invested"] += cost_basis
        by_type[type_key]["count"] += 1

    # Dividends total
    div_q = select(func.coalesce(func.sum(Dividend.amount - Dividend.tax), 0)).where(
        Dividend.user_id == user_id
    )
    dividends_total = (await db.execute(div_q)).scalar()

    return {
        "total_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "total_pnl": round(total_value - total_invested, 2),
        "total_pnl_pct": round(
            ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0, 2
        ),
        "dividends_total": round(float(dividends_total), 2),
        "positions_count": len(investments),
        "by_type": by_type,
    }
