import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/providers/ThemeProvider'
import { QueryProvider } from '@/components/providers/QueryProvider'
import { Toaster } from 'sonner'

const inter = Inter({ subsets: ['latin', 'cyrillic'] })

export const metadata: Metadata = {
  title: '\u0412\u0440\u0435\u043c\u044f \u2014 \u0414\u0435\u043d\u044c\u0433\u0438',
  description: '\u041b\u0438\u0447\u043d\u044b\u0439 \u0444\u0438\u043d\u0430\u043d\u0441\u043e\u0432\u044b\u0439 \u043f\u043e\u043c\u043e\u0449\u043d\u0438\u043a',
  manifest: '/manifest.json',
}

export const viewport: Viewport = {
  themeColor: '#1F2937',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={`${inter.className} bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          <QueryProvider>
            {children}
            <Toaster position="top-right" richColors />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
