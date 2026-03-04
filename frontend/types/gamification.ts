// ==========================================
// Gamification Types
// ==========================================

export interface GamificationProfile {
  total_xp: number;
  level: number;
  streak_days: number;
  next_level_xp: number;
  xp_to_next_level: number;
  badges_count: number;
  rank?: number;
  last_activity_date?: string;
}

export interface Badge {
  id: string;
  badge_id: string;
  name: string;
  description: string;
  icon: string;
  xp_reward: number;
  unlocked_at: string;
  is_displayed: boolean;
}

export interface BadgeDefinition {
  badge_id: string;
  name: string;
  description: string;
  icon: string;
  xp_reward: number;
  requirement: string;
  is_unlocked: boolean;
  progress?: number;
  progress_max?: number;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  name: string;
  avatar_url?: string;
  total_xp: number;
  level: number;
  is_current_user: boolean;
}

export interface XPEvent {
  id: string;
  action: string;
  xp_earned: number;
  description: string;
  created_at: string;
}

export interface LevelInfo {
  level: number;
  title: string;
  min_xp: number;
  max_xp: number;
  color: string;
  icon: string;
}
