from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.models.user import User, SubscriptionPlan
from app.config import settings


# --- Subscription Plans Config ---

PLAN_PRICES = {
    SubscriptionPlan.FREE: 0,
    SubscriptionPlan.BASIC: 299,  # RUB/month
    SubscriptionPlan.PRO: 599,
    SubscriptionPlan.FAMILY: 899,
}

PLAN_FEATURES = {
    SubscriptionPlan.FREE: {
        "max_transactions": 50,
        "max_budgets": 3,
        "max_goals": 2,
        "investments": False,
        "analytics": "basic",
        "export": False,
        "telegram": False,
    },
    SubscriptionPlan.BASIC: {
        "max_transactions": 500,
        "max_budgets": 10,
        "max_goals": 10,
        "investments": True,
        "analytics": "advanced",
        "export": True,
        "telegram": False,
    },
    SubscriptionPlan.PRO: {
        "max_transactions": -1,  # unlimited
        "max_budgets": -1,
        "max_goals": -1,
        "investments": True,
        "analytics": "full",
        "export": True,
        "telegram": True,
    },
    SubscriptionPlan.FAMILY: {
        "max_transactions": -1,
        "max_budgets": -1,
        "max_goals": -1,
        "investments": True,
        "analytics": "full",
        "export": True,
        "telegram": True,
        "family_members": 5,
    },
}


async def get_subscription_info(db: AsyncSession, user: User) -> dict:
    """Get current subscription details for user."""
    plan = user.subscription_plan or SubscriptionPlan.FREE
    is_active = True
    if plan != SubscriptionPlan.FREE and user.subscription_expires_at:
        is_active = user.subscription_expires_at > datetime.utcnow()

    return {
        "plan": plan.value,
        "price": PLAN_PRICES.get(plan, 0),
        "is_active": is_active,
        "expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
        "stripe_customer_id": user.stripe_customer_id,
        "features": PLAN_FEATURES.get(plan, {}),
    }


async def get_plans() -> list:
    """Get all available subscription plans."""
    plans = []
    for plan in SubscriptionPlan:
        plans.append({
            "id": plan.value,
            "name": plan.value.capitalize(),
            "price": PLAN_PRICES.get(plan, 0),
            "features": PLAN_FEATURES.get(plan, {}),
        })
    return plans


async def change_plan(
    db: AsyncSession, user: User, new_plan: str
) -> dict:
    """Change user subscription plan."""
    try:
        plan_enum = SubscriptionPlan(new_plan)
    except ValueError:
        return {"error": "Invalid plan"}

    user.subscription_plan = plan_enum
    if plan_enum == SubscriptionPlan.FREE:
        user.subscription_expires_at = None
    else:
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)

    user.updated_at = datetime.utcnow()
    await db.flush()
    await db.commit()
    await db.refresh(user)

    return {
        "status": "plan_changed",
        "plan": plan_enum.value,
        "expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
    }


async def check_feature_access(
    user: User, feature: str
) -> bool:
    """Check if user's plan allows access to a feature."""
    plan = user.subscription_plan or SubscriptionPlan.FREE
    features = PLAN_FEATURES.get(plan, {})
    return features.get(feature, False)
