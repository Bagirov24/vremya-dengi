'use client'

import { useState, useEffect } from 'react'
import { useTheme } from 'next-themes'

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [currency, setCurrency] = useState('RUB')
  const [language, setLanguage] = useState('ru')
  const [brokers, setBrokers] = useState<{name: string, apiKey: string, connected: boolean}[]>([
    { name: 'Tinkoff', apiKey: '', connected: false },
    { name: 'Finam', apiKey: '', connected: false },
  ])
  const [notifications, setNotifications] = useState({ push: true, email: true, digest: 'daily' })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/settings/profile`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.json()).then(d => {
      setName(d.name || ''); setEmail(d.email || '')
      setCurrency(d.currency || 'RUB'); setLanguage(d.language || 'ru')
      if (d.brokers) setBrokers(d.brokers)
    }).catch(() => {})
  }, [])

  const handleSave = async () => {
    setSaving(true)
    const token = localStorage.getItem('token')
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/settings/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name, currency, language, notifications, brokers }),
    })
    setSaving(false)
  }

  const updateBrokerKey = (idx: number, key: string) => {
    const updated = [...brokers]; updated[idx].apiKey = key; setBrokers(updated)
  }

  const connectBroker = async (idx: number) => {
    const token = localStorage.getItem('token')
    const b = brokers[idx]
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/settings/broker/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ broker: b.name, api_key: b.apiKey }),
    })
    if (res.ok) {
      const updated = [...brokers]; updated[idx].connected = true; setBrokers(updated)
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Настройки</h1>

      <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Профиль</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Имя</label>
            <input value={name} onChange={e => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
            <input value={email} disabled
              className="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-100 dark:bg-gray-600 text-gray-500" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Валюта</label>
              <select value={currency} onChange={e => setCurrency(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="RUB">Рубль (RUB)</option>
                <option value="USD">Доллар (USD)</option>
                <option value="EUR">Евро (EUR)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Язык</label>
              <select value={language} onChange={e => setLanguage(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Тема</h2>
        <div className="flex gap-3">
          {['light', 'dark', 'system'].map(t => (
            <button key={t} onClick={() => setTheme(t)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                theme === t ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}>{t === 'light' ? 'Светлая' : t === 'dark' ? 'Тёмная' : 'Система'}</button>
          ))}
        </div>
      </section>

      <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Брокеры</h2>
        <div className="space-y-4">
          {brokers.map((b, i) => (
            <div key={b.name} className="flex items-center gap-3">
              <span className="w-20 text-sm font-medium text-gray-700 dark:text-gray-300">{b.name}</span>
              <input type="password" placeholder="API ключ" value={b.apiKey}
                onChange={e => updateBrokerKey(i, e.target.value)}
                className="flex-1 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-sm" />
              <button onClick={() => connectBroker(i)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  b.connected ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}>{b.connected ? 'Подключен' : 'Подключить'}</button>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Уведомления</h2>
        <div className="space-y-3">
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={notifications.push} onChange={e => setNotifications({...notifications, push: e.target.checked})}
              className="w-4 h-4 rounded" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Push-уведомления</span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={notifications.email} onChange={e => setNotifications({...notifications, email: e.target.checked})}
              className="w-4 h-4 rounded" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Email дайджест</span>
          </label>
        </div>
      </section>

      <button onClick={handleSave} disabled={saving}
        className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition disabled:opacity-50">
        {saving ? 'Сохранение...' : 'Сохранить'}
      </button>
    </div>
  )
}
