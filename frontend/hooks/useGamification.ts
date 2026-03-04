'use client';

import { useState, useEffect, useCallback } from 'react';
import { gamificationApi } from '@/lib/api';

export interface GamificationProfile {
  total_xp: number;
  level: number;
  streak_days: number;
  next_level_xp: number;
  badges_count: number;
}

export interface Badge {
  id: string;
  badge_id: string;
  name: string;
  description: string;
  icon: string;
  unlocked_at: string;
  is_displayed: boolean;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  name: string;
  avatar_url?: string;
  total_xp: number;
  level: number;
}

export function useGamification() {
  const [profile, setProfile] = useState<GamificationProfile | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await gamificationApi.profile();
      setProfile(data as GamificationProfile);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchBadges = useCallback(async () => {
    try {
      const data = await gamificationApi.badges();
      setBadges(data as Badge[]);
    } catch {}
  }, []);

  const fetchLeaderboard = useCallback(async () => {
    try {
      const data = await gamificationApi.leaderboard();
      setLeaderboard(data as LeaderboardEntry[]);
    } catch {}
  }, []);

  useEffect(() => {
    fetchProfile();
    fetchBadges();
    fetchLeaderboard();
  }, [fetchProfile, fetchBadges, fetchLeaderboard]);

  const levelProgress = profile
    ? Math.round(((profile.total_xp % profile.next_level_xp) / profile.next_level_xp) * 100)
    : 0;

  return {
    profile,
    badges,
    leaderboard,
    levelProgress,
    isLoading,
    error,
    refetch: fetchProfile,
  };
}
