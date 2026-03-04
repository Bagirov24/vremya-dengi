from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.models.user import User
from app.models.investment import Achievement
from app.services.gamification_service import (
    calculate_level, award_xp, update_streak, get_available_badges,
    XP_PER_STREAK_DAY,
)

router = APIRouter()


@router.get("/status")
async def get_gamification_status(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get gamification status: XP, level, streak, badges."""
    xp = user.xp or 0
    level, next_xp = calculate_level(xp)
    streak = await update_streak(db, str(user.id))
    if streak > 0:
        await award_xp(db, str(user.id), XP_PER_STREAK_DAY, "daily_streak")

    result = await db.execute(
        select(Achievement).where(Achievement.user_id == user.id)
    )
    unlocked = [a.badge_id for a in result.scalars().all()]

    all_badges = get_available_badges()
    badges = [
        {**badge, "unlocked": badge["id"] in unlocked}
        for badge in all_badges
    ]

    return {
        "xp": xp,
        "level": level,
        "next_level_xp": next_xp,
        "progress_pct": round((xp / next_xp * 100) if next_xp > 0 else 100, 1),
        "streak_days": streak,
        "badges": badges,
    }


@router.get("/achievements")
async def list_achievements(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's unlocked achievements."""
    result = await db.execute(
        select(Achievement).where(Achievement.user_id == user.id)
    )
    achievements = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "badge_id": a.badge_id,
            "name": a.name,
            "description": a.description,
            "icon": a.icon,
            "xp_reward": a.xp_reward,
            "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None,
        }
        for a in achievements
    ]


@router.get("/leaderboard")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
):
    """Get top 20 users by XP."""
    from sqlalchemy import desc
    result = await db.execute(
        select(User.full_name, User.xp, User.level, User.avatar_url)
        .where(User.is_active == True)
        .order_by(desc(User.xp))
        .limit(20)
    )
    rows = result.all()
    return [
        {
            "rank": i + 1,
            "name": row[0] or "Anonymous",
            "xp": row[1] or 0,
            "level": row[2] or 1,
            "avatar_url": row[3],
        }
        for i, row in enumerate(rows)
    ]
