from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime


class AchievementResponse(BaseModel):
    id: UUID
    user_id: UUID
    badge_id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    xp_reward: int = 0
    unlocked_at: datetime

    class Config:
        from_attributes = True


class BadgeDefinition(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    xp_reward: int
    condition: str
    is_unlocked: bool = False
    unlocked_at: Optional[datetime] = None


class GamificationProfile(BaseModel):
    xp: int = 0
    level: int = 1
    streak_days: int = 0
    xp_to_next_level: int = 100
    progress_percent: float = 0
    badges: List[Any] = []
    achievements: List[AchievementResponse] = []
    last_activity_date: Optional[datetime] = None


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    xp: int
    level: int
    streak_days: int


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None


class XPEvent(BaseModel):
    event_type: str
    xp_earned: int
    new_total_xp: int
    new_level: int
    level_up: bool = False
    new_badges: List[str] = []
