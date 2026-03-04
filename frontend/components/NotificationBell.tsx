'use client'

import { useEffect, useState } from 'react'

interface Notification {
  id: string
  type: string
  title: string
  body: string
  read: boolean
  created_at: string
}

export default function NotificationBell() {
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) return
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/notifications/unread-count`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.json()).then(d => setUnread(d.count || 0)).catch(() => {})
  }, [])

  const loadNotifications = async () => {
    const token = localStorage.getItem('token')
    const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notifications/?limit=20`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    const data = await r.json()
    setNotifications(data)
  }

  const toggle = () => {
    if (!open) loadNotifications()
    setOpen(!open)
  }

  const markAllRead = async () => {
    const token = localStorage.getItem('token')
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notifications/read-all`, {
      method: 'PUT', headers: { Authorization: `Bearer ${token}` }
    })
    setUnread(0)
    setNotifications(n => n.map(x => ({ ...x, read: true })))
  }

  return (
    <div className="relative">
      <button onClick={toggle} className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition">
        <svg className="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {unread > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 flex items-center justify-center rounded-full">
            {unread > 9 ? '9+' : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-12 w-80 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 z-50">
          <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700">
            <span className="font-semibold text-gray-900 dark:text-white">Уведомления</span>
            {unread > 0 && (
              <button onClick={markAllRead} className="text-xs text-blue-500">Прочитать все</button>
            )}
          </div>
          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400 text-sm">Нет уведомлений</div>
            ) : notifications.map(n => (
              <div key={n.id} className={`p-3 border-b border-gray-50 dark:border-gray-700 ${!n.read ? 'bg-blue-50/50 dark:bg-blue-900/10' : ''}`}>
                <div className="font-medium text-sm text-gray-900 dark:text-white">{n.title}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{n.body}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
