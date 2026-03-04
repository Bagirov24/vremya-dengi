from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.routers.auth import get_current_user
from app.services.gamification_service import (
    calculate_level, award_xp, update_streak, get_available_badges,
    XP_PER_STREAK_DAY
)
from app.models.notification import Achievement

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/status")
async def get_gamification_status(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    xp = current_user.xp or 0
    level, next_xp = calculate_level(xp)
    streak = await update_streak(db, str(current_user.id))
    if streak > 0:
        await award_xp(db, str(current_user.id), XP_PER_STREAK_DAY, "daily_streak")

    result = await db.execute(
        select(Achievement).where(Achievement.user_id == current_user.id)
    )
    unlocked = [a.badge_id for a in result.scalars().all()]

    all_badges = get_available_badges()
    badges = [
        {**b, "unlocked": b["id"] in unlocked}
        for b in all_badges
    ]

    return {
        "xp": xp,
        "level": level,
        "next_level_xp": next_xp,
        "streak": streak,
        "badges": badges,
    }


@router.get("/badges")
async def get_badges(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Achievement).where(Achievement.user_id == current_user.id)
    )
    unlocked = {a.badge_id: a.unlocked_at for a in result.scalars().all()}
    all_badges = get_available_badges()
    return [
        {
            **b,
            "unlocked": b["id"] in unlocked,
            "unlocked_at": str(unlocked[b["id"]]) if b["id"] in unlocked else None
        }
        for b in all_badges
    ]


@router.get("/leaderboard")
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    from app.models.user import User
    result = await db.execute(
        select(User).order_by(User.xp.desc()).limit(20)
    )
    users = result.scalars().all()
    return [
        {
            "name": u.name,
            "level": calculate_level(u.xp or 0)[0],
            "xp": u.xp or 0,
            "streak": u.streak or 0,
        }
        for u in users
    ]
