from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime
import enum


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    FAMILY = "family"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Settings
    currency = Column(String(3), default="RUB")
    language = Column(String(2), default="ru")
    theme = Column(String(10), default="dark")
    timezone = Column(String(50), default="Europe/Moscow")
    
    # Subscription
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Gamification
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    badges = Column(JSONB, default=[])
    
    # Broker API keys (encrypted)
    tinkoff_api_key = Column(Text, nullable=True)
    finam_api_key = Column(Text, nullable=True)
    
    # Telegram
    telegram_chat_id = Column(String(50), nullable=True)
    telegram_connected = Column(Boolean, default=False)
    
    # Push notifications
    push_subscription = Column(JSONB, nullable=True)
    email_digest_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    recurring_payments = relationship("RecurringPayment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
