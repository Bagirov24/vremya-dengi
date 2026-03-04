from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime
import enum


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="RUB")
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    tags = Column(JSONB, default=[])
    receipt_url = Column(String(500), nullable=True)
    is_recurring = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    limit_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0)
    period = Column(String(20), default="monthly")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    alert_threshold = Column(Float, default=0.8)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="budgets")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0)
    deadline = Column(DateTime, nullable=True)
    icon = Column(String(50), default="target")
    color = Column(String(7), default="#3B82F6")
    is_completed = Column(String(10), default="false")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="goals")


class RecurringPayment(Base):
    __tablename__ = "recurring_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="RUB")
    category = Column(String(100), nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    next_payment_date = Column(DateTime, nullable=False)
    is_active = Column(String(10), default="true")
    auto_deduct = Column(String(10), default="false")
    reminder_days_before = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recurring_payments")
