'use client'

interface XPBarProps {
  currentXP: number
  nextLevelXP: number
  level: number
  streak: number
}

export default function XPBar({ currentXP, nextLevelXP, level, streak }: XPBarProps) {
  const progress = (currentXP / nextLevelXP) * 100

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
            {level}
          </div>
          <div>
            <div className="font-semibold text-gray-900 dark:text-white">Уровень {level}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">{currentXP} / {nextLevelXP} XP</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-2xl">🔥</span>
          <div>
            <div className="font-bold text-gray-900 dark:text-white">{streak}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">дней</div>
          </div>
        </div>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
        <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
          style={{ width: `${Math.min(progress, 100)}%` }} />
      </div>
    </div>
  )
}
