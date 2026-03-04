'use client';

import { useState, useEffect, useCallback } from 'react';
import { settingsApi } from '@/lib/api';

export interface UserSettings {
  currency: string;
  language: string;
  timezone: string;
  theme: 'light' | 'dark' | 'system';
  notifications_email: boolean;
  notifications_push: boolean;
  notifications_budget_alerts: boolean;
  two_factor_enabled: boolean;
}

export function useSettings() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const fetchSettings = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await settingsApi.get();
      setSettings(data as UserSettings);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const updateSettings = useCallback(async (data: Partial<UserSettings>) => {
    setIsSaving(true);
    setSaved(false);
    setError(null);
    try {
      const updated = await settingsApi.update(data);
      setSettings(updated as UserSettings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSaving(false);
    }
  }, []);

  const updatePassword = useCallback(async (current: string, newPassword: string) => {
    setIsSaving(true);
    setError(null);
    try {
      await settingsApi.updatePassword({ current, newPassword });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsSaving(false);
    }
  }, []);

  return {
    settings,
    isLoading,
    isSaving,
    error,
    saved,
    updateSettings,
    updatePassword,
    refetch: fetchSettings,
  };
}
