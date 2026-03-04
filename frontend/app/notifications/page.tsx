'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { useNotifications } from '@/hooks/useNotifications'

export default function NotificationsPage() {
  const { notifications, loading, markAsRead, markAllAsRead, deleteNotification } = useNotifications()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')

  const filtered = filter === 'unread'
    ? (notifications || []).filter(n => !n.is_read)
    : (notifications || [])

  const unreadCount = (notifications || []).filter(n => !n.is_read).length

  const iconForType = (type: string) => {
    switch (type) {
      case 'transaction': return '\uD83D\uDCB3'
      case 'budget': return '\uD83D\uDCCA'
      case 'investment': return '\uD83D\uDCC8'
      case 'security': return '\uD83D\uDD12'
      case 'system': return '\u2699\uFE0F'
      default: return '\uD83D\uDD14'
    }
  }

  const timeAgo = (date: string) => {
    const diff = Date.now() - new Date(date).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 60) return `${mins} \u043C\u0438\u043D \u043D\u0430\u0437\u0430\u0434`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours} \u0447 \u043D\u0430\u0437\u0430\u0434`
    const days = Math.floor(hours / 24)
    return `${days} \u0434\u043D. \u043D\u0430\u0437\u0430\u0434`
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="flex-1 overflow-y-auto">
        <header className="sticky top-0 z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => setSidebarOpen(true)} className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
              </button>
              <h1 className="text-xl font-bold">\u0423\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F</h1>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 rounded-full">
                  {unreadCount}
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                \u041E\u0442\u043C\u0435\u0442\u0438\u0442\u044C \u0432\u0441\u0435 \u043A\u0430\u043A \u043F\u0440\u043E\u0447\u0438\u0442\u0430\u043D\u043D\u044B\u0435
              </button>
            )}
          </div>
        </header>

        {/* Filter Tabs */}
        <div className="px-6 py-4 flex gap-2">
          {(['all', 'unread'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
              }`}
            >
              {f === 'all' ? '\u0412\u0441\u0435' : '\u041D\u0435\u043F\u0440\u043E\u0447\u0438\u0442\u0430\u043D\u043D\u044B\u0435'}
            </button>
          ))}
        </div>

        {/* Notifications List */}
        <div className="px-6 pb-8 space-y-2">
          {loading ? (
            <div className="text-center py-12 text-gray-400">\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430...</div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-4xl mb-2">\uD83D\uDD14</p>
              <p className="text-gray-400">{filter === 'unread' ? '\u041D\u0435\u0442 \u043D\u0435\u043F\u0440\u043E\u0447\u0438\u0442\u0430\u043D\u043D\u044B\u0445' : '\u041D\u0435\u0442 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u0439'}</p>
            </div>
          ) : (
            filtered.map(n => (
              <div
                key={n.id}
                className={`bg-white dark:bg-gray-800 rounded-xl p-4 border transition hover:shadow-sm cursor-pointer ${
                  n.is_read
                    ? 'border-gray-100 dark:border-gray-700'
                    : 'border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-900/10'
                }`}
                onClick={() => !n.is_read && markAsRead(n.id)}
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{iconForType(n.type)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className={`text-sm font-medium ${!n.is_read ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'}`}>
                        {n.title}
                      </h3>
                      <span className="text-xs text-gray-400 whitespace-nowrap ml-2">{timeAgo(n.created_at)}</span>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{n.message}</p>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteNotification(n.id) }}
                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-red-500 transition"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
