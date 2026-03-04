from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User, SubscriptionPlan
from app.models.transaction import Transaction
from app.models.investment import Investment

router = APIRouter()


async def require_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
async def admin_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    users_count = await db.execute(select(func.count(User.id)))
    tx_count = await db.execute(select(func.count(Transaction.id)))
    inv_count = await db.execute(select(func.count(Investment.id)))

    plan_stats = {}
    for plan in SubscriptionPlan:
        count = await db.execute(
            select(func.count(User.id)).where(User.subscription_plan == plan)
        )
        plan_stats[plan.value] = count.scalar()

    return {
        "total_users": users_count.scalar(),
        "total_transactions": tx_count.scalar(),
        "total_investments": inv_count.scalar(),
        "subscription_stats": plan_stats,
    }


@router.get("/users")
async def admin_users(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "subscription_plan": u.subscription_plan.value,
            "xp": u.xp,
            "level": u.level,
            "created_at": str(u.created_at),
        }
        for u in users
    ]


@router.put("/users/{user_id}/toggle")
async def toggle_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    return {"user_id": str(user.id), "is_active": user.is_active}
