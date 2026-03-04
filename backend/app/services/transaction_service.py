from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from app.models.transaction import Transaction, Budget, Goal, RecurringPayment, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate


# --- Transaction CRUD ---

async def create_transaction(
    db: AsyncSession,
    user_id: UUID,
    data: TransactionCreate,
) -> Transaction:
    """Create a new transaction and update related budgets."""
    tx = Transaction(
        user_id=user_id,
        type=data.type,
        amount=data.amount,
        currency=data.currency,
        category=data.category,
        subcategory=data.subcategory,
        description=data.description,
        date=data.date or datetime.utcnow(),
        tags=data.tags or [],
        receipt_url=data.receipt_url,
        is_recurring=data.is_recurring,
    )
    db.add(tx)
    await db.flush()

    # Auto-update budget spent_amount
    if data.type == TransactionType.EXPENSE:
        await _update_budget_spent(db, user_id, data.category, data.amount)

    await db.commit()
    await db.refresh(tx)
    return tx


async def get_transactions(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    size: int = 20,
    type_filter: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
):
    """Get paginated transactions with filters."""
    query = select(Transaction).where(Transaction.user_id == user_id)

    if type_filter:
        query = query.where(Transaction.type == type_filter)
    if category:
        query = query.where(Transaction.category == category)
    if date_from:
        query = query.where(Transaction.date >= date_from)
    if date_to:
        query = query.where(Transaction.date <= date_to)
    if search:
        query = query.where(
            Transaction.description.ilike(f"%{search}%")
            | Transaction.category.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.order_by(desc(Transaction.date)).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total


async def get_transaction_by_id(
    db: AsyncSession, user_id: UUID, transaction_id: UUID
) -> Optional[Transaction]:
    result = await db.execute(
        select(Transaction).where(
            and_(Transaction.id == transaction_id, Transaction.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def update_transaction(
    db: AsyncSession, user_id: UUID, transaction_id: UUID, data: TransactionUpdate
) -> Optional[Transaction]:
    tx = await get_transaction_by_id(db, user_id, transaction_id)
    if not tx:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tx, key, value)
    tx.updated_at = datetime.utcnow()

    await db.flush()
    await db.commit()
    await db.refresh(tx)
    return tx


async def delete_transaction(
    db: AsyncSession, user_id: UUID, transaction_id: UUID
) -> bool:
    tx = await get_transaction_by_id(db, user_id, transaction_id)
    if not tx:
        return False
    await db.delete(tx)
    await db.commit()
    return True


async def get_transaction_stats(
    db: AsyncSession,
    user_id: UUID,
    period_days: int = 30,
):
    """Get income/expense summary for a period."""
    since = datetime.utcnow() - timedelta(days=period_days)

    income_q = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= since,
        )
    )
    expense_q = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= since,
        )
    )

    income = (await db.execute(income_q)).scalar()
    expenses = (await db.execute(expense_q)).scalar()

    # Category breakdown
    cat_q = (
        select(Transaction.category, func.sum(Transaction.amount))
        .where(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= since,
            )
        )
        .group_by(Transaction.category)
        .order_by(desc(func.sum(Transaction.amount)))
    )
    cat_result = await db.execute(cat_q)
    categories = [{"category": row[0], "amount": row[1]} for row in cat_result.all()]

    return {
        "period_days": period_days,
        "total_income": float(income),
        "total_expenses": float(expenses),
        "balance": float(income - expenses),
        "categories": categories,
    }


# --- Budget CRUD ---

async def create_budget(db: AsyncSession, user_id: UUID, data: dict) -> Budget:
    budget = Budget(user_id=user_id, **data)
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    return budget


async def get_budgets(db: AsyncSession, user_id: UUID) -> List[Budget]:
    result = await db.execute(
        select(Budget).where(Budget.user_id == user_id).order_by(Budget.created_at)
    )
    return result.scalars().all()


async def get_budget_by_id(db: AsyncSession, user_id: UUID, budget_id: UUID) -> Optional[Budget]:
    result = await db.execute(
        select(Budget).where(and_(Budget.id == budget_id, Budget.user_id == user_id))
    )
    return result.scalar_one_or_none()


async def update_budget(db: AsyncSession, user_id: UUID, budget_id: UUID, data: dict) -> Optional[Budget]:
    budget = await get_budget_by_id(db, user_id, budget_id)
    if not budget:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(budget, key, value)
    await db.flush()
    await db.commit()
    await db.refresh(budget)
    return budget


async def delete_budget(db: AsyncSession, user_id: UUID, budget_id: UUID) -> bool:
    budget = await get_budget_by_id(db, user_id, budget_id)
    if not budget:
        return False
    await db.delete(budget)
    await db.commit()
    return True


# --- Goal CRUD ---

async def create_goal(db: AsyncSession, user_id: UUID, data: dict) -> Goal:
    goal = Goal(user_id=user_id, **data)
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


async def get_goals(db: AsyncSession, user_id: UUID) -> List[Goal]:
    result = await db.execute(
        select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at)
    )
    return result.scalars().all()


async def update_goal(db: AsyncSession, user_id: UUID, goal_id: UUID, data: dict) -> Optional[Goal]:
    result = await db.execute(
        select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == user_id))
    )
    goal = result.scalar_one_or_none()
    if not goal:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(goal, key, value)
    await db.flush()
    await db.commit()
    await db.refresh(goal)
    return goal


async def delete_goal(db: AsyncSession, user_id: UUID, goal_id: UUID) -> bool:
    result = await db.execute(
        select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == user_id))
    )
    goal = result.scalar_one_or_none()
    if not goal:
        return False
    await db.delete(goal)
    await db.commit()
    return True


# --- Recurring Payments ---

async def get_recurring_payments(db: AsyncSession, user_id: UUID) -> List[RecurringPayment]:
    result = await db.execute(
        select(RecurringPayment)
        .where(RecurringPayment.user_id == user_id)
        .order_by(RecurringPayment.next_payment_date)
    )
    return result.scalars().all()


async def create_recurring_payment(db: AsyncSession, user_id: UUID, data: dict) -> RecurringPayment:
    rp = RecurringPayment(user_id=user_id, **data)
    db.add(rp)
    await db.commit()
    await db.refresh(rp)
    return rp


async def delete_recurring_payment(db: AsyncSession, user_id: UUID, rp_id: UUID) -> bool:
    result = await db.execute(
        select(RecurringPayment).where(
            and_(RecurringPayment.id == rp_id, RecurringPayment.user_id == user_id)
        )
    )
    rp = result.scalar_one_or_none()
    if not rp:
        return False
    await db.delete(rp)
    await db.commit()
    return True


# --- Helpers ---

async def _update_budget_spent(
    db: AsyncSession, user_id: UUID, category: str, amount: float
):
    """Increment spent_amount on matching active budget."""
    now = datetime.utcnow()
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.user_id == user_id,
                Budget.category == category,
                Budget.start_date <= now,
                Budget.end_date >= now,
            )
        )
    )
    budget = result.scalar_one_or_none()
    if budget:
        budget.spent_amount = (budget.spent_amount or 0) + amount
        await db.flush()
