from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class BrokerType(str, Enum):
    TINKOFF = "tinkoff"
    FINAM = "finam"
    MANUAL = "manual"


class InvestmentType(str, Enum):
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"
    CRYPTO = "crypto"


# --- Investment ---

class InvestmentCreate(BaseModel):
    broker: BrokerType = BrokerType.MANUAL
    type: InvestmentType
    ticker: str = Field(..., max_length=20)
    name: str = Field(..., max_length=255)
    quantity: float = Field(default=0, ge=0)
    avg_price: float = Field(default=0, ge=0)
    current_price: float = Field(default=0, ge=0)
    currency: str = Field(default="RUB", max_length=3)
    sector: Optional[str] = Field(None, max_length=100)


class InvestmentUpdate(BaseModel):
    quantity: Optional[float] = Field(None, ge=0)
    avg_price: Optional[float] = Field(None, ge=0)
    current_price: Optional[float] = Field(None, ge=0)
    sector: Optional[str] = Field(None, max_length=100)


class InvestmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    broker: BrokerType
    type: InvestmentType
    ticker: str
    name: str
    quantity: float
    avg_price: float
    current_price: float
    currency: str
    sector: Optional[str] = None
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    investments: List[InvestmentResponse]
    total_value: float = 0
    total_invested: float = 0
    total_profit: float = 0
    profit_percent: float = 0
    by_type: dict = {}
    by_sector: dict = {}


# --- Trade ---

class TradeCreate(BaseModel):
    investment_id: UUID
    action: str = Field(..., max_length=10)
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    commission: float = Field(default=0, ge=0)
    date: Optional[datetime] = None
    note: Optional[str] = None


class TradeResponse(BaseModel):
    id: UUID
    investment_id: UUID
    user_id: UUID
    action: str
    quantity: float
    price: float
    commission: float
    date: datetime
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Dividend ---

class DividendCreate(BaseModel):
    investment_id: UUID
    amount: float = Field(..., gt=0)
    tax: float = Field(default=0, ge=0)
    payment_date: datetime
    currency: str = Field(default="RUB", max_length=3)


class DividendResponse(BaseModel):
    id: UUID
    investment_id: UUID
    user_id: UUID
    amount: float
    tax: float
    payment_date: datetime
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Search ---

class StockSearchResult(BaseModel):
    ticker: str
    name: str
    type: InvestmentType
    exchange: Optional[str] = None
    currency: str = "RUB"
    current_price: Optional[float] = None
    change_percent: Optional[float] = None
