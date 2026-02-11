import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 游戏状态管理（v2 - 纯UI状态）

 职责：
 - 管理UI相关状态（sessionId, loading, error）
 - 封装API调用
 - 不包含任何游戏逻辑计算
 */
export const useGameStore = defineStore('game', () => {
  // ========== UI状态 ==========

  const sessionId = ref<string | null>(null)
  const currentMessage = ref<string>('')
  const choices = ref<any[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ========== 计算属性 ==========

  const isGameOver = computed(() => {
    // 由后端AI判断，前端只展示
    return choices.value.length === 0 && currentMessage.value !== ''
  })

  const hasError = computed(() => error.value !== null)

  // ========== Actions ==========

  /**
   * 开始新游戏（调用后端API）
   */
  async function startNewGame(playerName: string = '程序员小王', difficulty: 'normal' | 'easy' | 'hard' = 'normal') {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/game/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: playerName, difficulty }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      sessionId.value = data.session_id
      currentMessage.value = data.message
      choices.value = data.choices || []

      return data
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : '开始游戏失败'
      throw err
    }
    finally {
      isLoading.value = false
    }
  }

  /**
   * 提交行动选择
   */
  async function makeChoice(choiceId: string) {
    if (!sessionId.value) {
      error.value = '没有活动会话，请先开始游戏'
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/game/act', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.value,
          choice_id: choiceId,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      currentMessage.value = data.feedback?.success || ''
      choices.value = data.choices || []

      // 检查游戏结束
      if (data.game_over) {
        sessionId.value = null
        choices.value = []
      }

      return data
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : '提交选择失败'
      throw err
    }
    finally {
      isLoading.value = false
    }
  }

  /**
   * 获取当前状态
   */
  async function fetchState() {
    if (!sessionId.value) {
      error.value = '没有活动会话'
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`/api/game/state?session_id=${sessionId.value}`)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : '获取状态失败'
      throw err
    }
    finally {
      isLoading.value = false
    }
  }

  /**
   * 重置状态
   */
  function reset() {
    sessionId.value = null
    currentMessage.value = ''
    choices.value = []
    isLoading.value = false
    error.value = null
  }

  /**
   * 清除错误
   */
  function clearError() {
    error.value = null
  }

  return {
    // 状态
    sessionId,
    currentMessage,
    choices,
    isLoading,
    error,

    // 计算属性
    isGameOver,
    hasError,

    // Actions
    startNewGame,
    makeChoice,
    fetchState,
    reset,
    clearError,
  }
})
