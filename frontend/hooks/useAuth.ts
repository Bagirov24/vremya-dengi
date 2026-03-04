'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';

interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  subscription_plan?: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

export function useAuth() {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setState({ user: null, isLoading: false, isAuthenticated: false, error: null });
      return;
    }
    try {
      const user = await authApi.me();
      setState({ user: user as User, isLoading: false, isAuthenticated: true, error: null });
    } catch {
      localStorage.removeItem('token');
      setState({ user: null, isLoading: false, isAuthenticated: false, error: null });
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const { access_token } = await authApi.login(email, password);
      localStorage.setItem('token', access_token);
      await fetchUser();
      router.push('/dashboard');
    } catch (err: any) {
      setState(prev => ({ ...prev, isLoading: false, error: err.message || 'Login failed' }));
      throw err;
    }
  }, [fetchUser, router]);

  const register = useCallback(async (data: { email: string; password: string; name: string }) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const { access_token } = await authApi.register(data);
      localStorage.setItem('token', access_token);
      await fetchUser();
      router.push('/dashboard');
    } catch (err: any) {
      setState(prev => ({ ...prev, isLoading: false, error: err.message || 'Registration failed' }));
      throw err;
    }
  }, [fetchUser, router]);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setState({ user: null, isLoading: false, isAuthenticated: false, error: null });
    router.push('/auth');
  }, [router]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    login,
    register,
    logout,
    clearError,
    refetch: fetchUser,
  };
}
