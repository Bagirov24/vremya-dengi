from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse, TransactionListResponse,
)
from app.services import transaction_service

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new transaction."""
    tx = await transaction_service.create_transaction(db, user.id, data)
    return tx


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List transactions with filters and pagination."""
    items, total = await transaction_service.get_transactions(
        db, user.id, page, size, type, category, date_from, date_to, search
    )
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/stats")
async def transaction_stats(
    period_days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get income/expense statistics for a period."""
    return await transaction_service.get_transaction_stats(db, user.id, period_days)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    tx = await transaction_service.get_transaction_by_id(db, user.id, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    data: TransactionUpdate,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    tx = await transaction_service.update_transaction(db, user.id, transaction_id, data)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await transaction_service.delete_transaction(db, user.id, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"status": "deleted"}


# --- Budgets ---

@router.post("/budgets")
async def create_budget(
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    budget = await transaction_service.create_budget(db, user.id, data)
    return budget


@router.get("/budgets")
async def list_budgets(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await transaction_service.get_budgets(db, user.id)


@router.put("/budgets/{budget_id}")
async def update_budget(
    budget_id: UUID,
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    budget = await transaction_service.update_budget(db, user.id, budget_id, data)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.delete("/budgets/{budget_id}")
async def delete_budget(
    budget_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await transaction_service.delete_budget(db, user.id, budget_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"status": "deleted"}


# --- Goals ---

@router.post("/goals")
async def create_goal(
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await transaction_service.create_goal(db, user.id, data)


@router.get("/goals")
async def list_goals(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await transaction_service.get_goals(db, user.id)


@router.put("/goals/{goal_id}")
async def update_goal(
    goal_id: UUID,
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await transaction_service.update_goal(db, user.id, goal_id, data)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await transaction_service.delete_goal(db, user.id, goal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"status": "deleted"}


# --- Recurring Payments ---

@router.get("/recurring")
async def list_recurring(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await transaction_service.get_recurring_payments(db, user.id)


@router.post("/recurring")
async def create_recurring(
    data: dict,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await transaction_service.create_recurring_payment(db, user.id, data)


@router.delete("/recurring/{rp_id}")
async def delete_recurring(
    rp_id: UUID,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await transaction_service.delete_recurring_payment(db, user.id, rp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recurring payment not found")
    return {"status": "deleted"}
