import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '\u0410\u0432\u0442\u043E\u0440\u0438\u0437\u0430\u0446\u0438\u044F \u2014 \u0412\u0440\u0435\u043C\u044F \u0414\u0435\u043D\u0435\u0433',
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {children}
    </div>
  )
}
