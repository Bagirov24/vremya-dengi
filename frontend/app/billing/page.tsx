'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/dashboard/Sidebar'

const plans = [
  {
    id: 'free',
    name: '\u0411\u0435\u0441\u043F\u043B\u0430\u0442\u043D\u044B\u0439',
    price: 0,
    period: '',
    features: [
      '\u0414\u043E 50 \u0442\u0440\u0430\u043D\u0437\u0430\u043A\u0446\u0438\u0439/\u043C\u0435\u0441',
      '\u0411\u0430\u0437\u043E\u0432\u0430\u044F \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0430',
      '1 \u0431\u044E\u0434\u0436\u0435\u0442',
      'Email-\u043F\u043E\u0434\u0434\u0435\u0440\u0436\u043A\u0430',
    ],
    current: true,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 299,
    period: '/\u043C\u0435\u0441',
    features: [
      '\u0411\u0435\u0437\u043B\u0438\u043C\u0438\u0442 \u0442\u0440\u0430\u043D\u0437\u0430\u043A\u0446\u0438\u0439',
      '\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043D\u043D\u0430\u044F \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0430',
      '\u0411\u0435\u0437\u043B\u0438\u043C\u0438\u0442 \u0431\u044E\u0434\u0436\u0435\u0442\u043E\u0432',
      '\u0418\u043D\u0432\u0435\u0441\u0442\u0438\u0446\u0438\u0438 \u0438 \u043F\u043E\u0440\u0442\u0444\u0435\u043B\u044C',
      '\u041F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442\u043D\u0430\u044F \u043F\u043E\u0434\u0434\u0435\u0440\u0436\u043A\u0430',
    ],
    popular: true,
  },
  {
    id: 'business',
    name: 'Business',
    price: 799,
    period: '/\u043C\u0435\u0441',
    features: [
      '\u0412\u0441\u0451 \u0438\u0437 Pro',
      'API \u0434\u043E\u0441\u0442\u0443\u043F',
      '\u041C\u0443\u043B\u044C\u0442\u0438-\u0430\u043A\u043A\u0430\u0443\u043D\u0442\u044B',
      '\u041A\u043E\u043C\u0430\u043D\u0434\u043D\u044B\u0439 \u0434\u043E\u0441\u0442\u0443\u043F',
      '\u0412\u044B\u0434\u0435\u043B\u0435\u043D\u043D\u044B\u0439 \u043C\u0435\u043D\u0435\u0434\u0436\u0435\u0440',
    ],
  },
]

export default function BillingPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly')

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="flex-1 overflow-y-auto">
        <header className="sticky top-0 z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(true)} className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            <h1 className="text-xl font-bold">\u0422\u0430\u0440\u0438\u0444\u044B \u0438 \u043E\u043F\u043B\u0430\u0442\u0430</h1>
          </div>
        </header>

        <div className="max-w-5xl mx-auto px-6 py-8">
          {/* Period Toggle */}
          <div className="flex justify-center mb-8">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-1 flex">
              <button
                onClick={() => setBillingPeriod('monthly')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${billingPeriod === 'monthly' ? 'bg-white dark:bg-gray-700 shadow-sm' : ''}`}
              >
                \u0415\u0436\u0435\u043C\u0435\u0441\u044F\u0447\u043D\u043E
              </button>
              <button
                onClick={() => setBillingPeriod('yearly')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${billingPeriod === 'yearly' ? 'bg-white dark:bg-gray-700 shadow-sm' : ''}`}
              >
                \u0415\u0436\u0435\u0433\u043E\u0434\u043D\u043E <span className="text-green-500 text-xs">-20%</span>
              </button>
            </div>
          </div>

          {/* Plans Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map(plan => (
              <div
                key={plan.id}
                className={`bg-white dark:bg-gray-800 rounded-2xl p-6 border-2 transition relative ${
                  plan.popular
                    ? 'border-blue-500 shadow-lg shadow-blue-500/10'
                    : 'border-gray-100 dark:border-gray-700'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-blue-600 text-white text-xs font-medium rounded-full">
                    \u041F\u043E\u043F\u0443\u043B\u044F\u0440\u043D\u044B\u0439
                  </div>
                )}
                <h3 className="text-lg font-bold">{plan.name}</h3>
                <div className="mt-2">
                  <span className="text-3xl font-bold">
                    {plan.price === 0 ? '\u0411\u0435\u0441\u043F\u043B\u0430\u0442\u043D\u043E' : `${billingPeriod === 'yearly' ? Math.round(plan.price * 0.8) : plan.price} \u20BD`}
                  </span>
                  {plan.period && <span className="text-gray-500 text-sm">{plan.period}</span>}
                </div>
                <ul className="mt-6 space-y-3">
                  {plan.features.map(f => (
                    <li key={f} className="flex items-center gap-2 text-sm">
                      <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                      {f}
                    </li>
                  ))}
                </ul>
                <button
                  className={`w-full mt-6 py-2.5 rounded-lg font-medium transition ${
                    plan.current
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-500 cursor-default'
                      : plan.popular
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                  disabled={plan.current}
                >
                  {plan.current ? '\u0422\u0435\u043A\u0443\u0449\u0438\u0439 \u043F\u043B\u0430\u043D' : '\u0412\u044B\u0431\u0440\u0430\u0442\u044C'}
                </button>
              </div>
            ))}
          </div>

          {/* Invoice History */}
          <div className="mt-12">
            <h2 className="text-lg font-bold mb-4">\u0418\u0441\u0442\u043E\u0440\u0438\u044F \u043F\u043B\u0430\u0442\u0435\u0436\u0435\u0439</h2>
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700">
              <div className="p-8 text-center text-gray-400">\u041F\u043B\u0430\u0442\u0435\u0436\u0435\u0439 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
