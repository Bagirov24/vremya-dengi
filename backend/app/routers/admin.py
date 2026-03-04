from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.models.user import User, SubscriptionPlan
from app.models.transaction import Transaction
from app.models.investment import Investment

router = APIRouter()


async def require_admin(user: User = Depends(get_current_active_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
async def admin_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get platform-wide statistics."""
    users_count = (await db.execute(select(func.count(User.id)))).scalar()
    tx_count = (await db.execute(select(func.count(Transaction.id)))).scalar()
    inv_count = (await db.execute(select(func.count(Investment.id)))).scalar()

    plan_stats = {}
    for plan in SubscriptionPlan:
        count = await db.execute(
            select(func.count(User.id)).where(User.subscription_plan == plan)
        )
        plan_stats[plan.value] = count.scalar()

    return {
        "total_users": users_count,
        "total_transactions": tx_count,
        "total_investments": inv_count,
        "subscription_breakdown": plan_stats,
    }


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users with pagination."""
    query = select(User)
    if search:
        query = query.where(
            User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%")
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(desc(User.created_at)).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "items": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "subscription_plan": u.subscription_plan.value if u.subscription_plan else "free",
                "xp": u.xp,
                "level": u.level,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "size": size,
    }


@router.put("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Activate/deactivate user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    await db.flush()
    await db.commit()
    return {"user_id": str(user.id), "is_active": user.is_active}


@router.put("/users/{user_id}/set-plan")
async def set_user_plan(
    user_id: UUID,
    plan: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Set subscription plan for a user (admin override)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user.subscription_plan = SubscriptionPlan(plan)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan")

    await db.flush()
    await db.commit()
    return {"user_id": str(user.id), "plan": plan}
