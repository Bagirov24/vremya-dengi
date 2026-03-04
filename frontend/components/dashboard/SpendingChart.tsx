'use client'

import { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend, Filler
)

interface SpendingChartProps {
  data: { label: string; income: number; expense: number }[]
  period?: 'week' | 'month' | 'year'
}

export default function SpendingChart({ data, period = 'month' }: SpendingChartProps) {
  const chartData = {
    labels: data.map(d => d.label),
    datasets: [
      {
        label: 'Доходы',
        data: data.map(d => d.income),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Расходы',
        data: data.map(d => d.expense),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239,68,68,0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' as const },
      tooltip: {
        callbacks: {
          label: (ctx: any) => {
            return `${ctx.dataset.label}: ${new Intl.NumberFormat('ru-RU', {
              style: 'currency', currency: 'RUB', minimumFractionDigits: 0
            }).format(ctx.raw)}`
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(107,114,128,0.1)' },
      },
      x: {
        grid: { display: false },
      },
    },
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Аналитика расходов</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400 capitalize">{period}</span>
      </div>
      <div className="h-72">
        <Line data={chartData} options={options} />
      </div>
    </div>
  )
}
