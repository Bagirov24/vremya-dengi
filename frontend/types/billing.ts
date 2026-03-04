// ==========================================
// Billing & Subscription Types
// ==========================================

import type { SubscriptionPlan } from './user';

export type BillingInterval = 'monthly' | 'yearly';
export type SubscriptionStatus = 'active' | 'canceled' | 'past_due' | 'trialing' | 'inactive';
export type InvoiceStatus = 'paid' | 'open' | 'void' | 'uncollectible';

export interface PricingPlan {
  id: string;
  name: string;
  plan: SubscriptionPlan;
  interval: BillingInterval;
  price: number;
  currency: string;
  stripe_price_id: string;
  features: string[];
  is_popular: boolean;
}

export interface Subscription {
  id: string;
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  interval: BillingInterval;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  stripe_subscription_id: string;
  created_at: string;
}

export interface Invoice {
  id: string;
  amount: number;
  currency: string;
  status: InvoiceStatus;
  description: string;
  invoice_url?: string;
  invoice_pdf?: string;
  period_start: string;
  period_end: string;
  created_at: string;
}

export interface CheckoutSessionRequest {
  price_id: string;
  success_url: string;
  cancel_url: string;
}

export interface CheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
}

export interface BillingPortalResponse {
  portal_url: string;
}
