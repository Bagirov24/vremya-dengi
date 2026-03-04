'use client'

import { useEffect, useState } from 'react'

interface BalanceCardProps {
  title: string
  amount: number
  currency?: string
  trend?: number
  icon?: React.ReactNode
}

export default function BalanceCard({ title, amount, currency = 'RUB', trend, icon }: BalanceCardProps) {
  const [animated, setAnimated] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(amount), 100)
    return () => clearTimeout(timer)
  }, [amount])

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
    }).format(val)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-gray-500 dark:text-gray-400">{title}</span>
        {icon && <div className="text-blue-500 dark:text-blue-400">{icon}</div>}
      </div>
      <div className="text-2xl font-bold text-gray-900 dark:text-white">
        {formatCurrency(animated)}
      </div>
      {trend !== undefined && (
        <div className={`flex items-center mt-2 text-sm ${
          trend >= 0 ? 'text-green-500' : 'text-red-500'
        }`}>
          <span>{trend >= 0 ? '+' : ''}{trend.toFixed(1)}%</span>
          <span className="ml-1 text-gray-400 dark:text-gray-500">vs last month</span>
        </div>
      )}
    </div>
  )
}
