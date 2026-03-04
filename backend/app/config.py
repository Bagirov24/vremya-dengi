from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Vremya Dengi"
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:3000"
    SECRET_KEY: str = "change-me-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/vremya_dengi"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # JWT
    JWT_SECRET: str = "jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    JWT_REFRESH_EXPIRATION_DAYS: int = 30
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_BASIC: str = ""
    STRIPE_PRICE_PRO: str = ""
    STRIPE_PRICE_FAMILY: str = ""
    
    # Brokers
    TINKOFF_API_TOKEN: Optional[str] = None
    FINAM_API_TOKEN: Optional[str] = None
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@vremya-dengi.ru"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    
    # Push Notifications
    VAPID_PUBLIC_KEY: str = ""
    VAPID_PRIVATE_KEY: str = ""
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
