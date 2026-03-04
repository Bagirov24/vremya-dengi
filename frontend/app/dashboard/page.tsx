'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { BalanceCards } from '@/components/dashboard/BalanceCards'
import { ExpenseChart } from '@/components/dashboard/ExpenseChart'
import { IncomeExpenseChart } from '@/components/dashboard/IncomeExpenseChart'
import { RecentTransactions } from '@/components/dashboard/RecentTransactions'
import { BudgetProgress } from '@/components/dashboard/BudgetProgress'
import { GoalsList } from '@/components/dashboard/GoalsList'
import { GamificationBar } from '@/components/dashboard/GamificationBar'

export default function DashboardPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 px-4 md:px-6 py-3">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-xl font-bold">Dashboard</h1>
            <GamificationBar />
          </div>
        </header>

        {/* Content */}
        <div className="p-4 md:p-6 space-y-6">
          <BalanceCards />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <IncomeExpenseChart />
            <ExpenseChart />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RecentTransactions />
            <div className="space-y-6">
              <BudgetProgress />
              <GoalsList />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
