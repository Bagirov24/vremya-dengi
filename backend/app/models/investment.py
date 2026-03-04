from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime
import enum


class BrokerType(str, enum.Enum):
    TINKOFF = "tinkoff"
    FINAM = "finam"
    MANUAL = "manual"


class InvestmentType(str, enum.Enum):
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"
    CRYPTO = "crypto"


class Investment(Base):
    __tablename__ = "investments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    broker = Column(Enum(BrokerType), default=BrokerType.MANUAL)
    type = Column(Enum(InvestmentType), nullable=False)
    ticker = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    quantity = Column(Float, default=0)
    avg_price = Column(Float, default=0)
    current_price = Column(Float, default=0)
    currency = Column(String(3), default="RUB")
    sector = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="investments")
    trades = relationship("Trade", back_populates="investment", cascade="all, delete-orphan")
    dividends = relationship("Dividend", back_populates="investment", cascade="all, delete-orphan")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investment_id = Column(UUID(as_uuid=True), ForeignKey("investments.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(10), nullable=False)  # buy / sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    investment = relationship("Investment", back_populates="trades")


class Dividend(Base):
    __tablename__ = "dividends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investment_id = Column(UUID(as_uuid=True), ForeignKey("investments.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    tax = Column(Float, default=0)
    payment_date = Column(DateTime, nullable=False)
    currency = Column(String(3), default="RUB")
    created_at = Column(DateTime, default=datetime.utcnow)

    investment = relationship("Investment", back_populates="dividends")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # budget_alert, goal_reached, payment_reminder, achievement
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(String(5), default="false")
    data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    xp_reward = Column(Integer, default=0)
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")
