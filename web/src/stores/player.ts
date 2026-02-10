import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'

import type { PlayerState } from '../game/types/player'
import { PlayerLevel } from '../game/types/player'
import { INITIAL_PLAYER_STATE } from '../game/data/constants'
import { gameApi, type ApiPlayerState, type SubmitChoiceResponse } from '../api/game'

export const usePlayerStore = defineStore('player', () => {
  // ========== 状态 ==========

  // 本地玩家状态
  const playerState = reactive<PlayerState>({ ...INITIAL_PLAYER_STATE })

  // 会话 ID（用于后端 API 调用）
  const sessionId = ref<string | null>(null)

  // 当前可用的选项（从 AI 生成）
  const currentChoices = ref<any[]>([])

  // 当前剧情上下文
  const storyContext = ref<string>('')

  // 加载状态
  const isLoading = ref<boolean>(false)

  // 错误信息
  const error = ref<string | null>(null)

  // ========== 计算属性 ==========

  const isGameOver = computed(() => {
    return playerState.suspicion >= 80 || (playerState.day > 30 && playerState.progress < 100)
  })

  const canWork = computed(() => playerState.energy > 10)
  const canSlack = computed(() => playerState.suspicion < 70)

  // ========== Actions ==========

  /**
   * 开始新游戏（调用后端 API）
   */
  async function startNewGame(difficulty: 'normal' | 'easy' | 'hard' = 'normal') {
    try {
      isLoading.value = true
      error.value = null

      const response = await gameApi.startGame(difficulty, '程序员小王')

      // 保存会话 ID
      sessionId.value = response.session_id

      // 转换后端返回的玩家状态到前端格式
      Object.assign(playerState, convertApiPlayerState(response.player_state))

      return response
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
   * 获取 AI 生成的选项
   */
  async function fetchChoices() {
    if (!sessionId.value) {
      error.value = '没有活动会话，请先开始游戏'
      return
    }

    try {
      isLoading.value = true
      error.value = null

      const response = await gameApi.getChoices(sessionId.value)

      // 保存选项和剧情上下文
      currentChoices.value = response.choices
      storyContext.value = response.story_context

      return response
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : '获取选项失败'
      throw err
    }
    finally {
      isLoading.value = false
    }
  }

  /**
   * 提交玩家选择（调用后端 API）
   */
  async function submitChoice(choiceId: string) {
    if (!sessionId.value) {
      error.value = '没有活动会话，请先开始游戏'
      return
    }

    try {
      isLoading.value = true
      error.value = null

      const response = await gameApi.submitChoice(sessionId.value, choiceId)

      // 更新玩家状态
      Object.assign(playerState, convertApiPlayerState(response.player_state))

      return response
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
   * 转换后端 API 返回的玩家状态到前端格式
   */
  function convertApiPlayerState(apiState: ApiPlayerState): PlayerState {
    return {
      chill: apiState.chill,
      progress: apiState.progress,
      suspicion: apiState.suspicion,
      energy: apiState.energy,
      salary: apiState.salary,
      reputation: apiState.reputation,
      level: apiState.level as PlayerLevel,
      day: apiState.day,
      week: apiState.week,
      turn: apiState.turn,
      unlockedSkills: apiState.unlocked_skills,
      unlockedAchievements: apiState.unlocked_achievements,
      seenEvents: apiState.seen_events,
    }
  }

  /**
   * 更新玩家状态（兼容旧代码）
   * @deprecated 使用 submitChoice() 替代
   */
  function updatePlayerState(changes: Partial<PlayerState>) {
    Object.assign(playerState, changes)
  }

  /**
   * 执行行动（兼容旧代码）
   * @deprecated 使用 submitChoice() 替代
   */
  function executeAction(_actionId: string, result: any) {
    Object.assign(playerState, result.changes)
  }

  /**
   * 解锁技能
   */
  function unlockSkill(skillId: string) {
    if (!playerState.unlockedSkills.includes(skillId)) {
      playerState.unlockedSkills.push(skillId)
    }
  }

  /**
   * 添加成就
   */
  function addAchievement(achievementId: string) {
    if (!playerState.unlockedAchievements.includes(achievementId)) {
      playerState.unlockedAchievements.push(achievementId)
    }
  }

  /**
   * 重置玩家状态
   */
  function resetPlayerState() {
    Object.assign(playerState, INITIAL_PLAYER_STATE)
    sessionId.value = null
    currentChoices.value = []
    storyContext.value = ''
    error.value = null
  }

  /**
   * 清除错误信息
   */
  function clearError() {
    error.value = null
  }

  return {
    // 状态
    playerState,
    sessionId,
    currentChoices,
    storyContext,
    isLoading,
    error,

    // 计算属性
    isGameOver,
    canWork,
    canSlack,

    // Actions
    startNewGame,
    fetchChoices,
    submitChoice,
    updatePlayerState,
    executeAction,
    unlockSkill,
    addAchievement,
    resetPlayerState,
    clearError,
  }
})
