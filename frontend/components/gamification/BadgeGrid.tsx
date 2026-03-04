'use client'

interface Badge {
  id: string
  name: string
  icon: string
  description: string
  unlocked: boolean
  unlockedAt?: string
}

interface BadgeGridProps {
  badges: Badge[]
}

export default function BadgeGrid({ badges }: BadgeGridProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Значки</h3>
      <div className="grid grid-cols-4 sm:grid-cols-6 gap-4">
        {badges.map(b => (
          <div key={b.id} className={`flex flex-col items-center gap-1 p-3 rounded-xl transition ${
            b.unlocked ? 'bg-yellow-50 dark:bg-yellow-900/10' : 'opacity-40 grayscale'
          }`}>
            <span className="text-3xl">{b.icon}</span>
            <span className="text-xs text-center font-medium text-gray-700 dark:text-gray-300">{b.name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
