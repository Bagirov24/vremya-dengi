'use client'

import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'

interface Portfolio {
  ticker: string
  name: string
  quantity: number
  avg_price: number
  current_price: number
  pnl: number
  pnl_percent: number
}

interface Trade {
  id: string
  ticker: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  date: string
  broker: string
}

export default function InvestmentsPage() {
  const [tab, setTab] = useState<'portfolio' | 'trades' | 'dividends'>('portfolio')
  const [portfolio, setPortfolio] = useState<Portfolio[]>([])
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    Promise.all([
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/investments/portfolio`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(r => r.json()),
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/investments/trades`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(r => r.json()),
    ]).then(([p, t]) => {
      setPortfolio(p); setTrades(t)
    }).finally(() => setLoading(false))
  }, [])

  const totalValue = portfolio.reduce((s, p) => s + p.current_price * p.quantity, 0)
  const totalPnl = portfolio.reduce((s, p) => s + p.pnl, 0)
  const fmt = (v: number) => new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(v)

  const tabs = [
    { key: 'portfolio', label: 'Портфель' },
    { key: 'trades', label: 'Сделки' },
    { key: 'dividends', label: 'Дивиденды' },
  ] as const

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Инвестиции</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
          <span className="text-sm text-gray-500 dark:text-gray-400">Стоимость портфеля</span>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{fmt(totalValue)}</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
          <span className="text-sm text-gray-500 dark:text-gray-400">Прибыль/Убыток</span>
          <div className={`text-2xl font-bold mt-1 ${totalPnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {totalPnl >= 0 ? '+' : ''}{fmt(totalPnl)}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
          <span className="text-sm text-gray-500 dark:text-gray-400">Позиции</span>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{portfolio.length}</div>
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              tab === t.key ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}>{t.label}</button>
        ))}
      </div>

      {tab === 'portfolio' && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 dark:border-gray-700">
                <th className="text-left p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Тикер</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Название</th>
                <th className="text-right p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Кол-во</th>
                <th className="text-right p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Цена</th>
                <th className="text-right p-4 text-sm font-medium text-gray-500 dark:text-gray-400">P&L</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.map(p => (
                <tr key={p.ticker} className="border-b border-gray-50 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750">
                  <td className="p-4 font-semibold text-gray-900 dark:text-white">{p.ticker}</td>
                  <td className="p-4 text-gray-600 dark:text-gray-300">{p.name}</td>
                  <td className="p-4 text-right text-gray-900 dark:text-white">{p.quantity}</td>
                  <td className="p-4 text-right text-gray-900 dark:text-white">{fmt(p.current_price)}</td>
                  <td className={`p-4 text-right font-semibold ${p.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {p.pnl >= 0 ? '+' : ''}{fmt(p.pnl)} ({p.pnl_percent.toFixed(1)}%)
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'trades' && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 dark:border-gray-700">
                <th className="text-left p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Дата</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Тикер</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Тип</th>
                <th className="text-right p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Кол-во</th>
                <th className="text-right p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Цена</th>
                <th className="text-right p-4 text-sm font-medium text-gray-500 dark:text-gray-400">Брокер</th>
              </tr>
            </thead>
            <tbody>
              {trades.map(t => (
                <tr key={t.id} className="border-b border-gray-50 dark:border-gray-700">
                  <td className="p-4 text-gray-600 dark:text-gray-300">{t.date}</td>
                  <td className="p-4 font-semibold text-gray-900 dark:text-white">{t.ticker}</td>
                  <td className="p-4"><span className={`px-2 py-1 rounded text-xs font-medium ${t.side === 'buy' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>{t.side === 'buy' ? 'Покупка' : 'Продажа'}</span></td>
                  <td className="p-4 text-right text-gray-900 dark:text-white">{t.quantity}</td>
                  <td className="p-4 text-right text-gray-900 dark:text-white">{fmt(t.price)}</td>
                  <td className="p-4 text-right text-gray-500 dark:text-gray-400">{t.broker}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'dividends' && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-100 dark:border-gray-700 text-center">
          <p className="text-gray-500 dark:text-gray-400">Дивиденды будут отображаться здесь после подключения брокера</p>
        </div>
      )}
    </div>
  )
}
