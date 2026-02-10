export type Period = 'morning' | 'afternoon' | 'evening' | 'night'
export type Difficulty = 'easy' | 'normal' | 'hard'

export interface GameState {
  isPlaying: boolean
  isPaused: boolean
  isGameOver: boolean

  // 时间相关
  currentTurn: number // 当前回合 (0-7)
  currentDay: number // 当前天数 (1-30)
  currentWeek: number // 当前周数 (1-4)
  currentPeriod: Period // 当前时段

  // 游戏配置
  difficulty: Difficulty
  seed: number // 随机数种子

  // UI状态
  isInEvent: boolean
  isLoading: boolean
  error: string | null
}

export interface GameConfig {
  difficulty: Difficulty
  seed?: number
}
