import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'

import type { GameConfig, GameState } from '../game/types/game'

export const useGameStore = defineStore('game', () => {
  // 状态
  const gameState = reactive<GameState>({
    isPlaying: false,
    isPaused: false,
    isGameOver: false,

    // 时间相关
    currentTurn: 0, // 当前回合 (0-7)
    currentDay: 1, // 当前天数 (1-30)
    currentWeek: 1, // 当前周数 (1-4)
    currentPeriod: 'morning', // 当前时段

    // 游戏配置
    difficulty: 'normal',
    seed: Date.now(), // 随机数种子

    // UI状态
    isInEvent: false,
    isLoading: false,
    error: null,
  })

  // 计算属性
  const isGameOver = computed(() => gameState.isGameOver)
  const canSave = computed(() => gameState.isPlaying && !gameState.isInEvent)

  // Actions
  function startNewGame(config?: Partial<GameConfig>) {
    // Reset state manually for now
    gameState.isPlaying = true
    gameState.isPaused = false
    gameState.isGameOver = false
    gameState.currentTurn = 0
    gameState.currentDay = 1
    gameState.currentWeek = 1
    gameState.currentPeriod = 'morning'
    gameState.isInEvent = false

    if (config) {
      if (config.difficulty)
        gameState.difficulty = config.difficulty
      if (config.seed)
        gameState.seed = config.seed
    }
  }

  function pauseGame() {
    gameState.isPaused = true
  }

  function resumeGame() {
    gameState.isPaused = false
  }

  function endGame() {
    gameState.isGameOver = true
    gameState.isPlaying = false
  }

  function nextTurn() {
    // Simple turn logic for now, will be expanded in engine
    gameState.currentTurn++
    if (gameState.currentTurn >= 8) { // MAX_TURNS_PER_DAY
      // Day transition logic would be here or in engine
    }
  }

  function setInEvent(inEvent: boolean) {
    gameState.isInEvent = inEvent
  }

  return {
    // 状态
    gameState,

    // 计算属性
    isGameOver,
    canSave,

    // Actions
    startNewGame,
    pauseGame,
    resumeGame,
    endGame,
    nextTurn,
    setInEvent,
  }
})
