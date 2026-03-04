// Settings & Preferences Types

export type ThemeMode = 'light' | 'dark' | 'system';
export type Language = 'ru' | 'en';
export type Currency = 'RUB' | 'USD' | 'EUR' | 'GBP' | 'CNY';
export type DateFormat = 'DD.MM.YYYY' | 'MM/DD/YYYY' | 'YYYY-MM-DD';
export type TimeFormat = '24h' | '12h';

export interface NotificationSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  transaction_alerts: boolean;
  budget_alerts: boolean;
  investment_alerts: boolean;
  weekly_report: boolean;
  monthly_report: boolean;
  marketing_emails: boolean;
}

export interface AppearanceSettings {
  theme: ThemeMode;
  language: Language;
  currency: Currency;
  date_format: DateFormat;
  time_format: TimeFormat;
  compact_mode: boolean;
  show_decimals: boolean;
  animations_enabled: boolean;
}

export interface SecuritySettings {
  two_factor_enabled: boolean;
  two_factor_method?: 'app' | 'sms' | 'email';
  session_timeout: number;
  login_notifications: boolean;
  biometric_enabled: boolean;
  trusted_devices: TrustedDevice[];
}

export interface TrustedDevice {
  id: string;
  name: string;
  device_type: 'desktop' | 'mobile' | 'tablet';
  browser: string;
  last_active: string;
  ip_address: string;
  is_current: boolean;
}

export interface PrivacySettings {
  profile_visible: boolean;
  show_in_leaderboard: boolean;
  share_statistics: boolean;
  data_collection: boolean;
}

export interface ExportSettings {
  format: 'csv' | 'xlsx' | 'pdf' | 'json';
  date_range: 'all' | 'year' | 'month' | 'custom';
  include_categories: boolean;
  include_notes: boolean;
  include_attachments: boolean;
}

export interface UserSettings {
  id: string;
  user_id: string;
  notifications: NotificationSettings;
  appearance: AppearanceSettings;
  security: SecuritySettings;
  privacy: PrivacySettings;
  default_export: ExportSettings;
  created_at: string;
  updated_at: string;
}

export interface SettingsUpdateRequest {
  notifications?: Partial<NotificationSettings>;
  appearance?: Partial<AppearanceSettings>;
  security?: Partial<SecuritySettings>;
  privacy?: Partial<PrivacySettings>;
  default_export?: Partial<ExportSettings>;
}

export interface SettingsSection {
  id: string;
  title: string;
  description: string;
  icon: string;
  path: string;
}
