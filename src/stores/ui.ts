import { defineStore } from 'pinia'
import { reactive } from 'vue'

import type { GameEvent } from '../game/types/events'

export interface ActionFeedback {
  type: 'success' | 'warning' | 'danger' | 'info'
  message: string
}

export interface UIState {
  currentEvent: GameEvent | null
  selectedAction: string | null
  showModal: boolean
  modalType: 'none' | 'event' | 'settings' | 'save'
  actionFeedback: ActionFeedback | null
  error: string | null
  theme: 'dark' | 'light'
}

export const useUIStore = defineStore('ui', () => {
  // 状态
  const uiState = reactive<UIState>({
    currentEvent: null,
    selectedAction: null,
    showModal: false,
    modalType: 'none',

    // 动画状态
    actionFeedback: null,

    // 错误状态
    error: null,

    // 主题状态
    theme: 'dark',
  })

  // Actions
  function showEvent(event: GameEvent) {
    uiState.currentEvent = event
    uiState.showModal = true
    uiState.modalType = 'event'
  }

  function selectAction(actionId: string) {
    uiState.selectedAction = actionId
  }

  function showActionFeedback(feedback: ActionFeedback) {
    uiState.actionFeedback = feedback
    setTimeout(() => {
      uiState.actionFeedback = null
    }, 3000)
  }

  function showError(message: string) {
    uiState.error = message
    setTimeout(() => {
      uiState.error = null
    }, 5000)
  }

  function hideModal() {
    uiState.showModal = false
    uiState.currentEvent = null
    uiState.selectedAction = null
    uiState.modalType = 'none'
  }

  return {
    // 状态
    uiState,

    // Actions
    showEvent,
    selectAction,
    showActionFeedback,
    showError,
    hideModal,
  }
})
