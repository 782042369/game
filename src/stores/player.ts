import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'

import type { ActionResult } from '../game/types/actions'
import type { PlayerState } from '../game/types/player'

import { INITIAL_PLAYER_STATE } from '../game/data/constants'

export const usePlayerStore = defineStore('player', () => {
  // 状态
  const playerState = reactive<PlayerState>({ ...INITIAL_PLAYER_STATE })

  // 计算属性
  const isGameOver = computed(() => {
    return playerState.suspicion >= 80 || (playerState.day > 30 && playerState.progress < 100) // Simplified condition
  })

  const canWork = computed(() => playerState.energy > 10)
  const canSlack = computed(() => playerState.suspicion < 70)

  // Actions
  function updatePlayerState(changes: Partial<PlayerState>) {
    Object.assign(playerState, changes)
  }

  function executeAction(_actionId: string, result: ActionResult) {
    // 应用行动结果
    Object.assign(playerState, result.changes)
  }

  function unlockSkill(skillId: string) {
    if (!playerState.unlockedSkills.includes(skillId)) {
      playerState.unlockedSkills.push(skillId)
    }
  }

  function addAchievement(achievementId: string) {
    if (!playerState.unlockedAchievements.includes(achievementId)) {
      playerState.unlockedAchievements.push(achievementId)
    }
  }

  function resetPlayerState() {
    Object.assign(playerState, INITIAL_PLAYER_STATE)
  }

  return {
    // 状态
    playerState,

    // 计算属性
    isGameOver,
    canWork,
    canSlack,

    // Actions
    updatePlayerState,
    executeAction,
    unlockSkill,
    addAchievement,
    resetPlayerState,
  }
})
