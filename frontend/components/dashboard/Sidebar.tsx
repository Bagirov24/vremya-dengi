'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

const navItems = [
  { href: '/dashboard', label: '\u0414\u0430\u0448\u0431\u043E\u0440\u0434', icon: '\uD83C\uDFE0' },
  { href: '/transactions', label: '\u0422\u0440\u0430\u043D\u0437\u0430\u043A\u0446\u0438\u0438', icon: '\uD83D\uDCB3' },
  { href: '/investments', label: '\u0418\u043D\u0432\u0435\u0441\u0442\u0438\u0446\u0438\u0438', icon: '\uD83D\uDCC8' },
  { href: '/notifications', label: '\u0423\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F', icon: '\uD83D\uDD14' },
  { href: '/billing', label: '\u0422\u0430\u0440\u0438\u0444\u044B', icon: '\uD83D\uDCB0' },
  { href: '/profile', label: '\u041F\u0440\u043E\u0444\u0438\u043B\u044C', icon: '\uD83D\uDC64' },
  { href: '/settings', label: '\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438', icon: '\u2699\uFE0F' },
]

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + '/')

  const sidebarContent = (
    <div className="flex flex-col h-full bg-gray-900 text-white w-64">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-gray-800">
        <Link href="/dashboard" className="flex items-center gap-2">
          <span className="text-2xl">\uD83D\uDCB0</span>
          <h1 className="text-lg font-bold">\u0412\u0440\u0435\u043C\u044F \u0414\u0435\u043D\u0435\u0433</h1>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            onClick={onClose}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              isActive(item.href)
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      {/* User section */}
      <div className="px-4 py-4 border-t border-gray-800">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold">
            {(user?.name || 'U').charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.name || '\u041F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044C'}</p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors text-left flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
          \u0412\u044B\u0439\u0442\u0438
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Mobile sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-200 ease-in-out md:hidden ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Desktop sidebar */}
      <aside className="hidden md:flex md:flex-shrink-0">
        {sidebarContent}
      </aside>
    </>
  )
}

export default Sidebar
