"""Investment portfolio sync and price update tasks."""
import logging
import asyncio
from datetime import datetime
from decimal import Decimal

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.config import settings
from app.models import Investment, User

logger = logging.getLogger(__name__)

_engine = create_async_engine(settings.DATABASE_URL, pool_size=5)
_async_session = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


async def _fetch_stock_price(ticker: str) -> dict | None:
    """Fetch current stock price from external API."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Using free MOEX ISS API for Russian stocks
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                marketdata = data.get("marketdata", {}).get("data", [])
                if marketdata:
                    row = marketdata[0]
                    columns = data["marketdata"]["columns"]
                    last_idx = columns.index("LAST") if "LAST" in columns else None
                    change_idx = columns.index("LASTTOPREVPRICE") if "LASTTOPREVPRICE" in columns else None
                    return {
                        "price": row[last_idx] if last_idx is not None else None,
                        "change_pct": row[change_idx] if change_idx is not None else None,
                    }
    except Exception as exc:
        logger.error("Failed to fetch price for %s: %s", ticker, exc)
    return None


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def sync_portfolio_prices(self, user_id: int):
    """Sync investment prices for a single user."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(Investment).where(Investment.user_id == user_id)
            )
            investments = result.scalars().all()

            updated = 0
            for inv in investments:
                price_data = await _fetch_stock_price(inv.ticker)
                if price_data and price_data.get("price"):
                    inv.current_price = Decimal(str(price_data["price"]))
                    inv.change_pct = price_data.get("change_pct", 0)
                    inv.total_value = inv.current_price * inv.quantity
                    inv.profit_loss = inv.total_value - (inv.buy_price * inv.quantity)
                    inv.updated_at = datetime.utcnow()
                    updated += 1

            await session.commit()
            logger.info("Updated %d/%d positions for user %s", updated, len(investments), user_id)
            return {"user_id": user_id, "updated": updated, "total": len(investments)}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2)
def sync_all_portfolios(self):
    """Sync prices for all users with active investments."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(Investment.user_id).distinct()
            )
            user_ids = [row[0] for row in result.fetchall()]

        dispatched = 0
        for uid in user_ids:
            sync_portfolio_prices.delay(uid)
            dispatched += 1

        logger.info("Dispatched portfolio sync for %d users", dispatched)
        return {"dispatched": dispatched}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2)
def check_price_alerts(self, user_id: int):
    """Check if any investment hit price alert thresholds."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(Investment).where(
                    Investment.user_id == user_id,
                    Investment.alert_price.isnot(None),
                )
            )
            investments = result.scalars().all()

            user_result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                return

            alerts_triggered = []
            for inv in investments:
                if inv.current_price and inv.alert_price:
                    if inv.current_price >= inv.alert_price:
                        alerts_triggered.append({
                            "ticker": inv.ticker,
                            "price": float(inv.current_price),
                            "alert_price": float(inv.alert_price),
                        })
                        # Reset alert after triggering
                        inv.alert_price = None

            if alerts_triggered:
                await session.commit()
                # Send notification via notification_tasks
                from app.workers.notification_tasks import create_notification
                for alert in alerts_triggered:
                    create_notification.delay(
                        user_id=user_id,
                        title=f"{alert['ticker']} dostig {alert['price']}",
                        message=f"Tsena {alert['ticker']} dostigla {alert['price']} RUB (alert: {alert['alert_price']} RUB)",
                        type="investment_alert",
                    )

            return {"alerts_triggered": len(alerts_triggered)}

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2)
def calculate_portfolio_stats(self, user_id: int):
    """Calculate aggregate portfolio statistics."""
    async def _run():
        async with _async_session() as session:
            result = await session.execute(
                select(Investment).where(Investment.user_id == user_id)
            )
            investments = result.scalars().all()

            total_invested = sum(float(i.buy_price * i.quantity) for i in investments)
            total_value = sum(float(i.total_value or 0) for i in investments)
            total_pnl = total_value - total_invested
            pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

            # Group by sector/type
            by_type = {}
            for inv in investments:
                t = inv.asset_type or "stock"
                by_type[t] = by_type.get(t, 0) + float(inv.total_value or 0)

            return {
                "user_id": user_id,
                "total_invested": total_invested,
                "total_value": total_value,
                "total_pnl": total_pnl,
                "pnl_pct": round(pnl_pct, 2),
                "allocation": by_type,
            }

    return asyncio.run(_run())
