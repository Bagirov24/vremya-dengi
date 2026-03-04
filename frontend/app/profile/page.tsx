'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { useAuth } from '@/hooks/useAuth'

export default function ProfilePage() {
  const { user, loading, updateProfile } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    avatar_url: user?.avatar_url || '',
  })

  const handleSave = async () => {
    await updateProfile(form)
    setEditing(false)
  }

  const stats = [
    { label: '\u0423\u0440\u043E\u0432\u0435\u043D\u044C', value: user?.level || 1, icon: '\u2B50' },
    { label: 'XP', value: `${user?.xp || 0} / ${user?.xp_next || 100}`, icon: '\uD83D\uDCCA' },
    { label: '\u0411\u044D\u0439\u0434\u0436\u0438', value: user?.badges_count || 0, icon: '\uD83C\uDFC5' },
    { label: '\u0421 \u043D\u0430\u043C\u0438', value: user?.created_at ? new Date(user.created_at).toLocaleDateString('ru-RU') : '\u2014', icon: '\uD83D\uDCC5' },
  ]

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="flex-1 overflow-y-auto">
        <header className="sticky top-0 z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(true)} className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            <h1 className="text-xl font-bold">\u041F\u0440\u043E\u0444\u0438\u043B\u044C</h1>
          </div>
        </header>

        <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
          {/* Avatar & Name */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-6">
              <div className="relative">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                  {user?.avatar_url ? (
                    <img src={user.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    (user?.name || 'U').charAt(0).toUpperCase()
                  )}
                </div>
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold">{user?.name || '\u041F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044C'}</h2>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
              <button
                onClick={() => setEditing(!editing)}
                className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition"
              >
                {editing ? '\u041E\u0442\u043C\u0435\u043D\u0430' : '\u0420\u0435\u0434\u0430\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u0442\u044C'}
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {stats.map(s => (
              <div key={s.label} className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700 text-center">
                <span className="text-2xl">{s.icon}</span>
                <p className="text-lg font-bold mt-1">{s.value}</p>
                <p className="text-xs text-gray-500">{s.label}</p>
              </div>
            ))}
          </div>

          {/* Edit Form */}
          {editing && (
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700 space-y-4">
              <h3 className="font-semibold">\u0420\u0435\u0434\u0430\u043A\u0442\u0438\u0440\u043E\u0432\u0430\u043D\u0438\u0435 \u043F\u0440\u043E\u0444\u0438\u043B\u044F</h3>
              <div className="grid gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\u0418\u043C\u044F</label>
                  <input
                    value={form.name}
                    onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                    className="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
                  <input
                    value={form.email}
                    onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                    className="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\u0422\u0435\u043B\u0435\u0444\u043E\u043D</label>
                  <input
                    value={form.phone}
                    onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                    className="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <button
                onClick={handleSave}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
              >
                \u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C
              </button>
            </div>
          )}

          {/* Danger Zone */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-red-200 dark:border-red-800">
            <h3 className="font-semibold text-red-600">\u041E\u043F\u0430\u0441\u043D\u0430\u044F \u0437\u043E\u043D\u0430</h3>
            <p className="text-sm text-gray-500 mt-1">\u042D\u0442\u0438 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044F \u043D\u0435\u043E\u0431\u0440\u0430\u0442\u0438\u043C\u044B</p>
            <div className="mt-4 flex gap-3">
              <button className="px-4 py-2 rounded-lg border border-red-200 dark:border-red-800 text-red-600 text-sm font-medium hover:bg-red-50 dark:hover:bg-red-900/20 transition">
                \u0423\u0434\u0430\u043B\u0438\u0442\u044C \u0430\u043A\u043A\u0430\u0443\u043D\u0442
              </button>
              <button className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition">
                \u042D\u043A\u0441\u043F\u043E\u0440\u0442 \u0434\u0430\u043D\u043D\u044B\u0445
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
