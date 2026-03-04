from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0)
    currency: str = Field(default="RUB", max_length=3)
    category: str = Field(..., max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    date: Optional[datetime] = None
    tags: List[str] = []
    receipt_url: Optional[str] = Field(None, max_length=500)
    is_recurring: Optional[str] = None


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    receipt_url: Optional[str] = Field(None, max_length=500)


class TransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: TransactionType
    amount: float
    currency: str
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    date: datetime
    tags: List[Any] = []
    receipt_url: Optional[str] = None
    is_recurring: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    per_page: int


class TransactionStats(BaseModel):
    total_income: float = 0
    total_expense: float = 0
    balance: float = 0
    by_category: dict = {}
    daily_totals: List[dict] = []


class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None


class BudgetCreate(BaseModel):
    category: str = Field(..., max_length=100)
    limit_amount: float = Field(..., gt=0)
    period: str = Field(default="monthly", max_length=20)
    start_date: datetime
    end_date: datetime
    alert_threshold: float = Field(default=0.8, ge=0, le=1)


class BudgetUpdate(BaseModel):
    limit_amount: Optional[float] = Field(None, gt=0)
    period: Optional[str] = Field(None, max_length=20)
    end_date: Optional[datetime] = None
    alert_threshold: Optional[float] = Field(None, ge=0, le=1)


class BudgetResponse(BaseModel):
    id: UUID
    user_id: UUID
    category: str
    limit_amount: float
    spent_amount: float
    period: str
    start_date: datetime
    end_date: datetime
    alert_threshold: float
    created_at: datetime

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    name: str = Field(..., max_length=255)
    target_amount: float = Field(..., gt=0)
    deadline: Optional[datetime] = None
    icon: str = Field(default="target", max_length=50)
    color: str = Field(default="#3B82F6", max_length=7)


class GoalUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    deadline: Optional[datetime] = None
    is_completed: Optional[str] = None


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    target_amount: float
    current_amount: float
    deadline: Optional[datetime] = None
    icon: str
    color: str
    is_completed: str
    created_at: datetime

    class Config:
        from_attributes = True


class RecurringPaymentCreate(BaseModel):
    name: str = Field(..., max_length=255)
    amount: float = Field(..., gt=0)
    currency: str = Field(default="RUB", max_length=3)
    category: str = Field(..., max_length=100)
    frequency: str = Field(..., max_length=20)
    next_payment_date: datetime
    auto_deduct: str = Field(default="false", max_length=10)
    reminder_days_before: int = Field(default=1, ge=0, le=30)


class RecurringPaymentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    frequency: Optional[str] = Field(None, max_length=20)
    next_payment_date: Optional[datetime] = None
    is_active: Optional[str] = None
    auto_deduct: Optional[str] = None


class RecurringPaymentResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    amount: float
    currency: str
    category: str
    frequency: str
    next_payment_date: datetime
    is_active: str
    auto_deduct: str
    reminder_days_before: int
    created_at: datetime

    class Config:
        from_attributes = True
