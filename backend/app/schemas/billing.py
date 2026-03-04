from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubscriptionPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    FAMILY = "family"


class PlanInfo(BaseModel):
    plan: SubscriptionPlan
    name: str
    price_monthly: float
    price_yearly: float
    features: List[str]
    is_current: bool = False


class SubscriptionStatus(BaseModel):
    plan: SubscriptionPlan
    is_active: bool
    expires_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    cancel_at_period_end: bool = False


class CheckoutRequest(BaseModel):
    plan: SubscriptionPlan
    billing_period: str = Field(default="monthly", pattern="^(monthly|yearly)$")
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class BillingPortalResponse(BaseModel):
    portal_url: str


class WebhookEvent(BaseModel):
    event_type: str
    data: dict
