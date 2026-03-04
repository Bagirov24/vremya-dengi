// ==========================================
// Notification Types
// ==========================================

export type NotificationType = 'info' | 'warning' | 'success' | 'error';

export type NotificationChannel = 'in_app' | 'email' | 'push';

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: NotificationType;
  channel: NotificationChannel;
  is_read: boolean;
  action_url?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  push_enabled: boolean;
  budget_alerts: boolean;
  goal_milestones: boolean;
  recurring_reminders: boolean;
  investment_updates: boolean;
  weekly_summary: boolean;
}

export interface NotificationGroup {
  date: string;
  notifications: Notification[];
}
