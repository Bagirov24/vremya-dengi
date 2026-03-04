// ==========================================
// User & Auth Types
// ==========================================

export type SubscriptionPlan = 'free' | 'pro_monthly' | 'pro_yearly';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  phone?: string;
  subscription_plan: SubscriptionPlan;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface ResetPasswordRequest {
  email: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface UpdateProfileRequest {
  name?: string;
  phone?: string;
  avatar_url?: string;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}
