from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, date, timedelta
from typing import Optional


XP_PER_TRANSACTION = 10
XP_PER_BUDGET_CHECK = 5
XP_PER_INVESTMENT = 20
XP_PER_STREAK_DAY = 15
LEVEL_THRESHOLDS = [0, 100, 300, 600, 1000, 1500, 2200, 3000, 4000, 5500, 7500]

BADGES = [
    {"id": "first_tx", "name": "Первая запись", "icon": "⭐", "condition": "transactions >= 1"},
    {"id": "streak_7", "name": "7 дней подряд", "icon": "🔥", "condition": "streak >= 7"},
    {"id": "streak_30", "name": "Месяц без перерыва", "icon": "🏆", "condition": "streak >= 30"},
    {"id": "tx_100", "name": "100 транзакций", "icon": "💯", "condition": "transactions >= 100"},
    {"id": "investor", "name": "Инвестор", "icon": "📈", "condition": "investments >= 1"},
    {"id": "saver", "name": "Копилка", "icon": "💰", "condition": "savings_goal_reached"},
    {"id": "budget_master", "name": "Мастер бюджета", "icon": "🎯", "condition": "budget_on_track_30_days"},
    {"id": "level_5", "name": "Уровень 5", "icon": "🌟", "condition": "level >= 5"},
]


def calculate_level(xp: int) -> tuple[int, int]:
    """Returns (level, xp_needed_for_next_level)"""
    for i in range(len(LEVEL_THRESHOLDS) - 1, -1, -1):
        if xp >= LEVEL_THRESHOLDS[i]:
            next_threshold = LEVEL_THRESHOLDS[i + 1] if i + 1 < len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[i] + 2000
            return i + 1, next_threshold
    return 1, LEVEL_THRESHOLDS[1]


async def award_xp(db: AsyncSession, user_id: str, amount: int, reason: str):
    """Award XP to user and check for level-up"""
    from app.models.user import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    old_level, _ = calculate_level(user.xp or 0)
    user.xp = (user.xp or 0) + amount
    new_level, next_xp = calculate_level(user.xp)
    await db.commit()
    return {
        "xp_added": amount,
        "total_xp": user.xp,
        "level": new_level,
        "next_level_xp": next_xp,
        "leveled_up": new_level > old_level,
        "reason": reason,
    }


async def update_streak(db: AsyncSession, user_id: str):
    """Update daily login streak"""
    from app.models.user import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return 0
    today = date.today()
    last = user.last_active_date
    if last == today:
        return user.streak or 0
    if last == today - timedelta(days=1):
        user.streak = (user.streak or 0) + 1
    else:
        user.streak = 1
    user.last_active_date = today
    await db.commit()
    return user.streak


def get_available_badges():
    return BADGES
