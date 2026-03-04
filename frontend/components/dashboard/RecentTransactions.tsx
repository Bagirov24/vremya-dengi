'use client'

interface Transaction {
  id: string
  description: string
  amount: number
  category: string
  date: string
  type: 'income' | 'expense'
}

interface RecentTransactionsProps {
  transactions: Transaction[]
}

export default function RecentTransactions({ transactions }: RecentTransactionsProps) {
  const fmt = (val: number) =>
    new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(val)

  const categoryIcons: Record<string, string> = {
    'Еда': '🍔', 'Транспорт': '🚗', 'Развлечения': '🎬',
    'Коммуналка': '🏠', 'Здоровье': '🏥', 'Зарплата': '💰',
    'Инвестиции': '📈', 'Покупки': '🛒',
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Последние транзакции</h3>
        <button className="text-sm text-blue-500 hover:text-blue-600 dark:text-blue-400">Все транзакции</button>
      </div>
      <div className="space-y-3">
        {transactions.map(tx => (
          <div key={tx.id} className="flex items-center justify-between py-3 border-b border-gray-50 dark:border-gray-700 last:border-0">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{categoryIcons[tx.category] || '💳'}</span>
              <div>
                <div className="font-medium text-gray-900 dark:text-white text-sm">{tx.description}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">{tx.category} · {tx.date}</div>
              </div>
            </div>
            <span className={`font-semibold text-sm ${tx.type === 'income' ? 'text-green-500' : 'text-red-500'}`}>
              {tx.type === 'income' ? '+' : '-'}{fmt(Math.abs(tx.amount))}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
