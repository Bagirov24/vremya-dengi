from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User, SubscriptionPlan
from app.config import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
router = APIRouter()

PRICE_MAP = {
    "basic": settings.STRIPE_PRICE_BASIC,
    "pro": settings.STRIPE_PRICE_PRO,
    "family": settings.STRIPE_PRICE_FAMILY,
}


@router.post("/create-checkout")
async def create_checkout(
    plan: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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
        success_url=f"{settings.APP_URL}/settings?billing=success",
        cancel_url=f"{settings.APP_URL}/settings?billing=cancel",
        metadata={"user_id": str(user.id), "plan": plan},
    )
    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        plan = session["metadata"]["plan"]
        sub_id = session.get("subscription")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.subscription_plan = SubscriptionPlan(plan)
            user.stripe_subscription_id = sub_id

    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice["customer"]
        result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
        user = result.scalar_one_or_none()
        if user:
            from datetime import datetime, timedelta
            user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)

    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        customer_id = sub["customer"]
        result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
        user = result.scalar_one_or_none()
        if user:
            user.subscription_plan = SubscriptionPlan.FREE
            user.stripe_subscription_id = None

    await db.commit()
    return {"status": "ok"}


@router.get("/subscription")
async def get_subscription(user: User = Depends(get_current_user)):
    return {
        "plan": user.subscription_plan.value,
        "stripe_customer_id": user.stripe_customer_id,
        "stripe_subscription_id": user.stripe_subscription_id,
        "expires_at": str(user.subscription_expires_at) if user.subscription_expires_at else None,
    }


@router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    stripe.Subscription.modify(user.stripe_subscription_id, cancel_at_period_end=True)
    return {"status": "cancellation_scheduled"}
