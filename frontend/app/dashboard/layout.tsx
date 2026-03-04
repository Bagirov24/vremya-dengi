import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '\u0414\u0430\u0448\u0431\u043E\u0440\u0434 \u2014 \u0412\u0440\u0435\u043C\u044F \u0414\u0435\u043D\u0435\u0433',
  description: '\u041F\u0430\u043D\u0435\u043B\u044C \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u044F \u0444\u0438\u043D\u0430\u043D\u0441\u0430\u043C\u0438',
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
