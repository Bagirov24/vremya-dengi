from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.models.user import User
from app.services import billing_service
from app.config import settings

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
router = APIRouter()

PRICE_MAP = {
    "basic": settings.STRIPE_PRICE_BASIC,
    "pro": settings.STRIPE_PRICE_PRO,
    "family": settings.STRIPE_PRICE_FAMILY,
}


@router.get("/plans")
async def list_plans():
    """Get available subscription plans."""
    return await billing_service.get_plans()


@router.get("/subscription")
async def get_subscription(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user subscription info."""
    return await billing_service.get_subscription_info(db, user)


@router.post("/create-checkout")
async def create_checkout(
    plan: str,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create Stripe checkout session."""
    if plan not in PRICE_MAP:
        raise HTTPException(status_code=400, detail="Invalid plan")

    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, name=user.full_name)
        user.stripe_customer_id = customer.id
        await db.flush()

    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": PRICE_MAP[plan], "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.FRONTEND_URL}/billing?success=true",
        cancel_url=f"{settings.FRONTEND_URL}/billing?canceled=true",
        metadata={"user_id": str(user.id), "plan": plan},
    )

    await db.commit()
    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/change-plan")
async def change_plan(
    plan: str,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Change subscription plan directly (for free downgrades)."""
    result = await billing_service.change_plan(db, user, plan)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        plan = session.get("metadata", {}).get("plan")
        user_id = session.get("metadata", {}).get("user_id")

        if plan and user_id:
            from sqlalchemy import select
            from app.models.user import User as UserModel
            from uuid import UUID

            result = await db.execute(
                select(UserModel).where(UserModel.id == UUID(user_id))
            )
            user = result.scalar_one_or_none()
            if user:
                user.stripe_subscription_id = session.get("subscription")
                await billing_service.change_plan(db, user, plan)

    return {"status": "ok"}
