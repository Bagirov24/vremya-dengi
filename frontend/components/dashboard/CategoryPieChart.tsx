'use client'

import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

interface CategoryData {
  name: string
  amount: number
  color: string
}

interface CategoryPieChartProps {
  categories: CategoryData[]
  title?: string
}

export default function CategoryPieChart({ categories, title = 'Расходы по категориям' }: CategoryPieChartProps) {
  const data = {
    labels: categories.map(c => c.name),
    datasets: [{
      data: categories.map(c => c.amount),
      backgroundColor: categories.map(c => c.color),
      borderWidth: 0,
      hoverOffset: 8,
    }],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: { position: 'right' as const, labels: { padding: 16, usePointStyle: true } },
    },
  }

  const total = categories.reduce((s, c) => s + c.amount, 0)

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{title}</h3>
      <div className="relative h-64">
        <Doughnut data={data} options={options} />
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{left: '-25%'}}>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(total)}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Всего</div>
          </div>
        </div>
      </div>
    </div>
  )
}
