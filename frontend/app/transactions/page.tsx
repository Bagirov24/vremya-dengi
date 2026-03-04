'use client'

import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { useTransactions } from '@/hooks/useTransactions'
import type { Transaction } from '@/types'

type FilterType = 'all' | 'income' | 'expense' | 'transfer'
type SortField = 'date' | 'amount' | 'category'

export default function TransactionsPage() {
  const router = useRouter()
  const { transactions, stats, loading, deleteTransaction } = useTransactions()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [filter, setFilter] = useState<FilterType>('all')
  const [sortField, setSortField] = useState<SortField>('date')
  const [sortAsc, setSortAsc] = useState(false)
  const [search, setSearch] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  })

  const filtered = useMemo(() => {
    let result = transactions || []
    if (filter !== 'all') result = result.filter(t => t.type === filter)
    if (search) {
      const q = search.toLowerCase()
      result = result.filter(t =>
        t.description?.toLowerCase().includes(q) ||
        t.category?.toLowerCase().includes(q)
      )
    }
    result.sort((a, b) => {
      let cmp = 0
      if (sortField === 'date') cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      else if (sortField === 'amount') cmp = a.amount - b.amount
      else cmp = (a.category || '').localeCompare(b.category || '')
      return sortAsc ? cmp : -cmp
    })
    return result
  }, [transactions, filter, search, sortField, sortAsc])

  const formatAmount = (amount: number, type: string) => {
    const sign = type === 'income' ? '+' : type === 'expense' ? '-' : ''
    return `${sign}${amount.toLocaleString('ru-RU')} \u20BD`
  }

  const formatDate = (date: string) => new Date(date).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'short', year: 'numeric'
  })

  const amountColor = (type: string) =>
    type === 'income' ? 'text-green-500' : type === 'expense' ? 'text-red-500' : 'text-blue-500'

  const filterButtons: { key: FilterType; label: string }[] = [
    { key: 'all', label: '\u0412\u0441\u0435' },
    { key: 'income', label: '\u0414\u043E\u0445\u043E\u0434\u044B' },
    { key: 'expense', label: '\u0420\u0430\u0441\u0445\u043E\u0434\u044B' },
    { key: 'transfer', label: '\u041F\u0435\u0440\u0435\u0432\u043E\u0434\u044B' },
  ]

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
              <h1 className="text-xl font-bold">\u0422\u0440\u0430\u043D\u0437\u0430\u043A\u0446\u0438\u0438</h1>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
              \u0414\u043E\u0431\u0430\u0432\u0438\u0442\u044C
            </button>
          </div>
        </header>

        {/* Stats Cards */}
        <div className="px-6 py-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
            <p className="text-sm text-gray-500">\u0414\u043E\u0445\u043E\u0434\u044B</p>
            <p className="text-2xl font-bold text-green-500">+{(stats?.total_income || 0).toLocaleString('ru-RU')} \u20BD</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
            <p className="text-sm text-gray-500">\u0420\u0430\u0441\u0445\u043E\u0434\u044B</p>
            <p className="text-2xl font-bold text-red-500">-{(stats?.total_expense || 0).toLocaleString('ru-RU')} \u20BD</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
            <p className="text-sm text-gray-500">\u0411\u0430\u043B\u0430\u043D\u0441</p>
            <p className="text-2xl font-bold">{(stats?.balance || 0).toLocaleString('ru-RU')} \u20BD</p>
          </div>
        </div>

        {/* Filters & Search */}
        <div className="px-6 pb-4 flex flex-col sm:flex-row gap-3">
          <div className="flex gap-2">
            {filterButtons.map(fb => (
              <button
                key={fb.key}
                onClick={() => setFilter(fb.key)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                  filter === fb.key
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {fb.label}
              </button>
            ))}
          </div>
          <input
            type="text"
            placeholder="\u041F\u043E\u0438\u0441\u043A \u0442\u0440\u0430\u043D\u0437\u0430\u043A\u0446\u0438\u0439..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="flex-1 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="month"
            value={selectedMonth}
            onChange={e => setSelectedMonth(e.target.value)}
            className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm outline-none"
          />
        </div>

        {/* Transactions List */}
        <div className="px-6 pb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            {/* Table Header */}
            <div className="grid grid-cols-12 gap-4 px-4 py-3 border-b border-gray-100 dark:border-gray-700 text-xs font-medium text-gray-500 uppercase">
              <div className="col-span-5 cursor-pointer" onClick={() => { setSortField('date'); setSortAsc(s => !s) }}>\u041E\u043F\u0438\u0441\u0430\u043D\u0438\u0435</div>
              <div className="col-span-2 cursor-pointer" onClick={() => { setSortField('category'); setSortAsc(s => !s) }}>\u041A\u0430\u0442\u0435\u0433\u043E\u0440\u0438\u044F</div>
              <div className="col-span-2 cursor-pointer" onClick={() => { setSortField('date'); setSortAsc(s => !s) }}>\u0414\u0430\u0442\u0430</div>
              <div className="col-span-2 text-right cursor-pointer" onClick={() => { setSortField('amount'); setSortAsc(s => !s) }}>\u0421\u0443\u043C\u043C\u0430</div>
              <div className="col-span-1"></div>
            </div>

            {loading ? (
              <div className="p-8 text-center text-gray-400">\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430...</div>
            ) : filtered.length === 0 ? (
              <div className="p-8 text-center text-gray-400">\u0422\u0440\u0430\u043D\u0437\u0430\u043A\u0446\u0438\u0439 \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D\u043E</div>
            ) : (
              filtered.map(t => (
                <div key={t.id} className="grid grid-cols-12 gap-4 px-4 py-3 border-b border-gray-50 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition items-center">
                  <div className="col-span-5">
                    <p className="font-medium text-sm">{t.description || '\u0411\u0435\u0437 \u043E\u043F\u0438\u0441\u0430\u043D\u0438\u044F'}</p>
                  </div>
                  <div className="col-span-2">
                    <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                      {t.category || '\u2014'}
                    </span>
                  </div>
                  <div className="col-span-2 text-sm text-gray-500">{formatDate(t.created_at)}</div>
                  <div className={`col-span-2 text-right font-semibold text-sm ${amountColor(t.type)}`}>
                    {formatAmount(t.amount, t.type)}
                  </div>
                  <div className="col-span-1 flex justify-end">
                    <button
                      onClick={() => deleteTransaction(t.id)}
                      className="p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500 transition"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
