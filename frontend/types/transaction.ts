// ==========================================
// Transaction Types
// ==========================================

export type TransactionType = 'income' | 'expense';

export type TransactionCategory =
  | 'salary'
  | 'freelance'
  | 'investments'
  | 'gifts'
  | 'food'
  | 'transport'
  | 'housing'
  | 'utilities'
  | 'entertainment'
  | 'health'
  | 'education'
  | 'shopping'
  | 'subscriptions'
  | 'travel'
  | 'other';

export interface Transaction {
  id: string;
  user_id: string;
  type: TransactionType;
  amount: number;
  category: TransactionCategory;
  description?: string;
  date: string;
  tags?: string[];
  is_recurring: boolean;
  recurring_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTransactionRequest {
  type: TransactionType;
  amount: number;
  category: TransactionCategory;
  description?: string;
  date: string;
  tags?: string[];
}

export interface UpdateTransactionRequest {
  type?: TransactionType;
  amount?: number;
  category?: TransactionCategory;
  description?: string;
  date?: string;
  tags?: string[];
}

export interface TransactionFilters {
  type?: TransactionType;
  category?: TransactionCategory;
  date_from?: string;
  date_to?: string;
  min_amount?: number;
  max_amount?: number;
  search?: string;
  limit?: number;
  offset?: number;
}

export interface TransactionStats {
  total_income: number;
  total_expense: number;
  balance: number;
  by_category: Record<string, number>;
  by_month: MonthlyStats[];
  avg_daily_expense: number;
  top_categories: CategoryStat[];
}

export interface MonthlyStats {
  month: string;
  income: number;
  expense: number;
  balance: number;
}

export interface CategoryStat {
  category: TransactionCategory;
  amount: number;
  percentage: number;
  count: number;
}

// Budget
export type BudgetPeriod = 'weekly' | 'monthly' | 'yearly';

export interface Budget {
  id: string;
  name: string;
  category?: TransactionCategory;
  amount: number;
  spent: number;
  period: BudgetPeriod;
  start_date: string;
  end_date: string;
  is_active: boolean;
  notify_at_percent: number;
  progress_percent: number;
  created_at: string;
}

export interface CreateBudgetRequest {
  name: string;
  category?: TransactionCategory;
  amount: number;
  period: BudgetPeriod;
}

// Goal
export interface Goal {
  id: string;
  name: string;
  description?: string;
  target_amount: number;
  current_amount: number;
  deadline?: string;
  icon?: string;
  color?: string;
  is_completed: boolean;
  is_active: boolean;
  progress_percent: number;
  completed_at?: string;
  created_at: string;
}

export interface CreateGoalRequest {
  name: string;
  description?: string;
  target_amount: number;
  deadline?: string;
  icon?: string;
  color?: string;
}

// Recurring Payment
export type RecurringFrequency = 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly' | 'yearly';

export interface RecurringPayment {
  id: string;
  name: string;
  description?: string;
  amount: number;
  category?: TransactionCategory;
  frequency: RecurringFrequency;
  next_payment_date: string;
  last_payment_date?: string;
  is_active: boolean;
  auto_create: boolean;
  reminder_days_before: number;
  total_paid: number;
  payment_count: number;
  created_at: string;
}

export interface CreateRecurringPaymentRequest {
  name: string;
  description?: string;
  amount: number;
  category?: TransactionCategory;
  frequency: RecurringFrequency;
  next_payment_date: string;
  auto_create?: boolean;
  reminder_days_before?: number;
}
