import type { Metadata } from 'next'
import Sidebar from '@/components/dashboard/Sidebar'

export const metadata: Metadata = {
  title: '\u0414\u0430\u0448\u0431\u043E\u0440\u0434 \u2014 \u0412\u0440\u0435\u043C\u044F \u0414\u0435\u043D\u0435\u0433',
  description: '\u041F\u0435\u0440\u0441\u043E\u043D\u0430\u043B\u044C\u043D\u044B\u0439 \u0444\u0438\u043D\u0430\u043D\u0441\u043E\u0432\u044B\u0439 \u0434\u0430\u0448\u0431\u043E\u0440\u0434',
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  )
}
