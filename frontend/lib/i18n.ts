type Locale = 'ru' | 'en'

const translations: Record<Locale, Record<string, string>> = {
  ru: {
    'nav.dashboard': 'Главная',
    'nav.transactions': 'Транзакции',
    'nav.investments': 'Инвестиции',
    'nav.settings': 'Настройки',
    'nav.achievements': 'Достижения',
    'dashboard.balance': 'Баланс',
    'dashboard.income': 'Доходы',
    'dashboard.expenses': 'Расходы',
    'dashboard.analytics': 'Аналитика',
    'dashboard.recent': 'Последние транзакции',
    'investments.portfolio': 'Портфель',
    'investments.trades': 'Сделки',
    'investments.dividends': 'Дивиденды',
    'settings.profile': 'Профиль',
    'settings.theme': 'Тема',
    'settings.brokers': 'Брокеры',
    'settings.notifications': 'Уведомления',
    'settings.save': 'Сохранить',
    'auth.login': 'Войти',
    'auth.register': 'Зарегистрироваться',
    'auth.email': 'Email',
    'auth.password': 'Пароль',
    'gamification.level': 'Уровень',
    'gamification.streak': 'Серия',
    'gamification.badges': 'Значки',
  },
  en: {
    'nav.dashboard': 'Dashboard',
    'nav.transactions': 'Transactions',
    'nav.investments': 'Investments',
    'nav.settings': 'Settings',
    'nav.achievements': 'Achievements',
    'dashboard.balance': 'Balance',
    'dashboard.income': 'Income',
    'dashboard.expenses': 'Expenses',
    'dashboard.analytics': 'Analytics',
    'dashboard.recent': 'Recent Transactions',
    'investments.portfolio': 'Portfolio',
    'investments.trades': 'Trades',
    'investments.dividends': 'Dividends',
    'settings.profile': 'Profile',
    'settings.theme': 'Theme',
    'settings.brokers': 'Brokers',
    'settings.notifications': 'Notifications',
    'settings.save': 'Save',
    'auth.login': 'Sign In',
    'auth.register': 'Sign Up',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'gamification.level': 'Level',
    'gamification.streak': 'Streak',
    'gamification.badges': 'Badges',
  },
}

export function t(key: string, locale: Locale = 'ru'): string {
  return translations[locale]?.[key] || key
}

export function getLocale(): Locale {
  if (typeof window === 'undefined') return 'ru'
  return (localStorage.getItem('locale') as Locale) || 'ru'
}

export function setLocale(locale: Locale) {
  localStorage.setItem('locale', locale)
}
