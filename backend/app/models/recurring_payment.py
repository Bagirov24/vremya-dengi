"""Recurring payment model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Integer, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RecurringFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class RecurringPayment(Base):
    __tablename__ = "recurring_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)
    frequency = Column(Enum(RecurringFrequency), default=RecurringFrequency.MONTHLY)
    next_payment_date = Column(DateTime, nullable=False)
    last_payment_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    auto_create = Column(Boolean, default=True)
    reminder_days_before = Column(Integer, default=3)
    total_paid = Column(Float, default=0.0)
    payment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="recurring_payments")
