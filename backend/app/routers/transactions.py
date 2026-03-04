from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TransactionType

router = APIRouter()


class TransactionCreate(BaseModel):
    type: str
    amount: float
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    tags: Optional[list] = []
    currency: Optional[str] = "RUB"


class TransactionUpdate(BaseModel):
    type: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    tags: Optional[list] = None


@router.get("")
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Transaction).where(Transaction.user_id == user.id)
    if type:
        query = query.where(Transaction.type == type)
    if category:
        query = query.where(Transaction.category == category)
    if date_from:
        query = query.where(Transaction.date >= date_from)
    if date_to:
        query = query.where(Transaction.date <= date_to)
    query = query.order_by(Transaction.date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("")
async def create_transaction(
    data: TransactionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tx = Transaction(
        user_id=user.id,
        type=TransactionType(data.type),
        amount=data.amount,
        category=data.category,
        subcategory=data.subcategory,
        description=data.description,
        date=data.date or datetime.utcnow(),
        tags=data.tags,
        currency=data.currency,
    )
    db.add(tx)
    await db.flush()
    return tx


@router.put("/{tx_id}")
async def update_transaction(
    tx_id: str,
    data: TransactionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction).where(and_(Transaction.id == tx_id, Transaction.user_id == user.id))
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(tx, field, value)
    return tx


@router.delete("/{tx_id}")
async def delete_transaction(
    tx_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction).where(and_(Transaction.id == tx_id, Transaction.user_id == user.id))
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await db.delete(tx)
    return {"status": "deleted"}


@router.get("/summary")
async def get_summary(
    period: str = Query("month"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.utcnow()
    if period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0)
    elif period == "week":
        start = now - __import__("datetime").timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0)
    else:
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0)

    income = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            and_(Transaction.user_id == user.id, Transaction.type == TransactionType.INCOME, Transaction.date >= start)
        )
    )
    expense = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            and_(Transaction.user_id == user.id, Transaction.type == TransactionType.EXPENSE, Transaction.date >= start)
        )
    )
    return {
        "income": income.scalar(),
        "expense": expense.scalar(),
        "balance": income.scalar() - expense.scalar() if income.scalar() and expense.scalar() else 0,
        "period": period,
    }
