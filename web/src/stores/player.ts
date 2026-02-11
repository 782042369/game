import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { gameApi, type ApiPlayerState, type ApiChoice } from '../api/game'

/**
 * 玩家状态管理（v4 - AI内容展示）
 *
 * 职责：
 * - 管理玩家状态（由后端AI返回）
 * - 管理游戏选项和剧情上下文
 * - 管理AI生成的公司、NPC、魔幻元素等内容
 * - 封装所有后端API调用
 * - 不包含任何本地计算
 */

// ========== AI生成内容类型定义 ==========

/** 游戏元数据（AI生成） */
export interface GameMeta {
  company_type: string
  style_type: string
  magical_level: '现实' | '轻度魔幻' | '中度魔幻' | '重度魔幻'
  seed_used: number
}

/** 魔幻元素（AI生成） */
export interface MagicalElement {
  type: 'object' | 'phenomenon' | 'ability'
  name: string
  description: string
  effect: string
}

/** 公司完整档案（AI生成） */
export interface CompanyProfile {
  name: string
  type: string
  culture: string
  atmosphere: string
  special_rules: string[]
  magical_elements: string[]
}

/** NPC完整档案（AI生成） */
export interface NPCProfile {
  id: string
  name: string
  role: 'boss' | 'colleague' | 'hr' | 'mentor' | 'rival'
  personality: string
  background: string
  appearance: string
  relationships: Record<string, string>
  attitude_toward_player: number
  secrets: string[]
}

/** NPC反应 */
export interface NPCReaction {
  npc_id: string
  npc_name: string
  reaction: string
  attitude_change: number
}

/** 触发的事件 */
export interface TriggeredEvent {
  type: 'threshold' | 'chain' | 'time' | 'random' | 'magical'
  message: string
  effect: string
}

// ========== API响应类型扩展 ==========

/** 开始游戏响应（扩展版） */
export interface GameStartResponse {
  session_id: string
  player_state: Record<string, unknown>
  message: string
  choices: ApiChoice[]
  // AI生成的内容
  game_meta?: GameMeta
  company_info?: CompanyProfile
  npcs?: NPCProfile[]
  current_magical_element?: MagicalElement
}

/** 提交选择响应（扩展版） */
export interface ChoiceSubmitResponse {
  success: boolean
  player_state: Record<string, unknown>
  feedback: { success: string }
  triggered_events?: TriggeredEvent[]
  game_over: boolean
  game_over_reason?: string
  // 动态更新内容
  npc_reactions?: NPCReaction[]
  active_magical_element?: MagicalElement
  updated_npcs?: NPCProfile[]
}

// 默认玩家状态（避免null错误）
const DEFAULT_PLAYER_STATE: ApiPlayerState = {
  chill: 50,
  progress: 0,
  suspicion: 0,
  energy: 100,
  salary: 5000,
  reputation: 0,
  level: 0,
  day: 1,
  week: 1,
  turn: 0,
  unlocked_skills: [],
  unlocked_achievements: [],
  seen_events: [],
}

// 降级选项（当后端没有返回下一轮选项时使用）
const FALLBACK_CHOICES: ApiChoice[] = [
  { id: 'work_hard', text: '努力工作', category: 'work', effects: { energy: -15, progress: 10, suspicion: -2 } },
  { id: 'slack_off', text: '摸鱼刷手机', category: 'slack', effects: { energy: 5, chill: 15, suspicion: 5 } },
  { id: 'coffee_break', text: '喝咖啡休息', category: 'social', effects: { energy: 10, chill: 5 } },
  { id: 'learn_skill', text: '学习新技术', category: 'skill', effects: { energy: -10, progress: 5, reputation: 2 } },
  { id: 'chat_colleague', text: '和同事聊天', category: 'social', effects: { energy: -5, chill: 10, suspicion: 2 } },
]

export const usePlayerStore = defineStore('player', () => {
  // ========== 状态 ==========

  const sessionId = ref<string | null>(null)
  const playerState = ref<ApiPlayerState>({ ...DEFAULT_PLAYER_STATE })
  const currentChoices = ref<ApiChoice[]>([])
  const storyContext = ref<string>('')
  const currentMessage = ref<string>('')
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isGameOver = ref(false)

  // ========== AI生成内容状态 ==========
  const gameMeta = ref<GameMeta | null>(null)
  const companyInfo = ref<CompanyProfile | null>(null)
  const npcs = ref<NPCProfile[]>([])
  const currentMagicalElement = ref<MagicalElement | null>(null)
  const lastNPCReactions = ref<NPCReaction[]>([])
  const lastTriggeredEvents = ref<TriggeredEvent[]>([])

  // ========== 计算属性 ==========

  const hasError = computed(() => error.value !== null)

  // ========== Actions ==========

  /**
   * 开始新游戏（调用后端API）
   */
  async function startNewGame(difficulty: 'normal' | 'easy' | 'hard' = 'normal') {
    isLoading.value = true
    error.value = null
    isGameOver.value = false

    try {
      const response = await gameApi.startGame(difficulty, '程序员小王') as unknown as GameStartResponse

      sessionId.value = response.session_id
      // 转换 player_state（后端返回的是 Record<string, number | string[]>）
      const state = response.player_state as Record<string, unknown>
      playerState.value = {
        ...DEFAULT_PLAYER_STATE,
        chill: (state.chill as number) ?? DEFAULT_PLAYER_STATE.chill,
        progress: (state.progress as number) ?? DEFAULT_PLAYER_STATE.progress,
        suspicion: (state.suspicion as number) ?? DEFAULT_PLAYER_STATE.suspicion,
        energy: (state.energy as number) ?? DEFAULT_PLAYER_STATE.energy,
        salary: (state.salary as number) ?? DEFAULT_PLAYER_STATE.salary,
        reputation: (state.reputation as number) ?? DEFAULT_PLAYER_STATE.reputation,
        level: (state.level as number) ?? DEFAULT_PLAYER_STATE.level,
        day: (state.day as number) ?? DEFAULT_PLAYER_STATE.day,
        week: (state.week as number) ?? DEFAULT_PLAYER_STATE.week,
        turn: (state.turn as number) ?? DEFAULT_PLAYER_STATE.turn,
        unlocked_skills: (state.unlocked_skills as string[]) || DEFAULT_PLAYER_STATE.unlocked_skills,
        unlocked_achievements: (state.unlocked_achievements as string[]) || DEFAULT_PLAYER_STATE.unlocked_achievements,
        seen_events: (state.seen_events as string[]) || DEFAULT_PLAYER_STATE.seen_events,
      }
      currentMessage.value = response.message
      currentChoices.value = response.choices || FALLBACK_CHOICES
      storyContext.value = response.message

      // DEBUG: 打印响应结构
      console.log('🔍 DEBUG response.npcs:', response.npcs)
      console.log('🔍 DEBUG response.npcs length:', response.npcs?.length)

      // 存储AI生成的内容（如果后端返回了）
      gameMeta.value = response.game_meta || null
      companyInfo.value = response.company_info || null
      npcs.value = response.npcs || []
      console.log('🔍 DEBUG store.npcs after assign:', npcs.value)
      currentMagicalElement.value = response.current_magical_element || null

      // 清空之前的数据
      lastNPCReactions.value = []
      lastTriggeredEvents.value = []

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
   * 提交玩家选择
   */
  async function submitChoice(choiceId: string) {
    if (!sessionId.value) {
      error.value = '没有活动会话，请先开始游戏'
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await gameApi.submitChoice(sessionId.value, choiceId) as unknown as ChoiceSubmitResponse

      // 转换 player_state
      const state = response.player_state as Record<string, unknown>
      playerState.value = {
        ...playerState.value,
        chill: (state.chill as number) ?? playerState.value.chill,
        progress: (state.progress as number) ?? playerState.value.progress,
        suspicion: (state.suspicion as number) ?? playerState.value.suspicion,
        energy: (state.energy as number) ?? playerState.value.energy,
        salary: (state.salary as number) ?? playerState.value.salary,
        reputation: (state.reputation as number) ?? playerState.value.reputation,
        level: (state.level as number) ?? playerState.value.level,
        day: (state.day as number) ?? playerState.value.day,
        week: (state.week as number) ?? playerState.value.week,
        turn: (state.turn as number) ?? playerState.value.turn,
        unlocked_skills: (state.unlocked_skills as string[]) || playerState.value.unlocked_skills,
        unlocked_achievements: (state.unlocked_achievements as string[]) || playerState.value.unlocked_achievements,
        seen_events: (state.seen_events as string[]) || playerState.value.seen_events,
      }
      currentMessage.value = response.feedback.success

      // 处理NPC反应
      if (response.npc_reactions && response.npc_reactions.length > 0) {
        lastNPCReactions.value = response.npc_reactions
        // 更新NPC好感度
        response.npc_reactions.forEach((reaction) => {
          const npc = npcs.value.find(n => n.id === reaction.npc_id)
          if (npc) {
            npc.attitude_toward_player += reaction.attitude_change
            // 确保好感度在0-100范围内
            npc.attitude_toward_player = Math.max(0, Math.min(100, npc.attitude_toward_player))
          }
        })
      }
      else {
        lastNPCReactions.value = []
      }

      // 存储触发的事件
      if (response.triggered_events && response.triggered_events.length > 0) {
        lastTriggeredEvents.value = response.triggered_events
      }
      else {
        lastTriggeredEvents.value = []
      }

      // 存储魔幻元素
      if (response.active_magical_element) {
        currentMagicalElement.value = response.active_magical_element
      }

      // 更新NPC信息（如果AI提供了更新）
      if (response.updated_npcs && response.updated_npcs.length > 0) {
        npcs.value = response.updated_npcs
      }

      // 检查游戏结束
      if (response.game_over) {
        isGameOver.value = true
        sessionId.value = null
        currentChoices.value = []
        storyContext.value = response.game_over_reason || '游戏已结束'
      }
      else {
        // 后端目前不返回下一轮选项，使用降级方案
        // TODO: 后端需要添加choices字段到ChoiceSubmitResponse
        currentChoices.value = FALLBACK_CHOICES
        storyContext.value = response.feedback.success
      }

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
   * 从后端获取玩家状态
   */
  async function fetchState() {
    if (!sessionId.value) {
      error.value = '没有活动会话'
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const data = await gameApi.getState(sessionId.value)
      const state = data.session?.metadata?.player_state
      if (state) {
        const stateRecord = state as Record<string, unknown>
        playerState.value = {
          ...DEFAULT_PLAYER_STATE,
          chill: (stateRecord.chill as number) ?? DEFAULT_PLAYER_STATE.chill,
          progress: (stateRecord.progress as number) ?? DEFAULT_PLAYER_STATE.progress,
          suspicion: (stateRecord.suspicion as number) ?? DEFAULT_PLAYER_STATE.suspicion,
          energy: (stateRecord.energy as number) ?? DEFAULT_PLAYER_STATE.energy,
          salary: (stateRecord.salary as number) ?? DEFAULT_PLAYER_STATE.salary,
          reputation: (stateRecord.reputation as number) ?? DEFAULT_PLAYER_STATE.reputation,
          level: (stateRecord.level as number) ?? DEFAULT_PLAYER_STATE.level,
          day: (stateRecord.day as number) ?? DEFAULT_PLAYER_STATE.day,
          week: (stateRecord.week as number) ?? DEFAULT_PLAYER_STATE.week,
          turn: (stateRecord.turn as number) ?? DEFAULT_PLAYER_STATE.turn,
          unlocked_skills: (stateRecord.unlocked_skills as string[]) || DEFAULT_PLAYER_STATE.unlocked_skills,
          unlocked_achievements: (stateRecord.unlocked_achievements as string[]) || DEFAULT_PLAYER_STATE.unlocked_achievements,
          seen_events: (stateRecord.seen_events as string[]) || DEFAULT_PLAYER_STATE.seen_events,
        }
      }
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
   * 更新玩家状态（由后端返回）
   */
  function updateState(newState: Partial<ApiPlayerState>) {
    playerState.value = { ...playerState.value, ...newState }
  }

  /**
   * 重置状态
   */
  function reset() {
    sessionId.value = null
    playerState.value = { ...DEFAULT_PLAYER_STATE }
    currentChoices.value = []
    storyContext.value = ''
    currentMessage.value = ''
    isLoading.value = false
    error.value = null
    isGameOver.value = false
    // 重置AI内容状态
    gameMeta.value = null
    companyInfo.value = null
    npcs.value = []
    currentMagicalElement.value = null
    lastNPCReactions.value = []
    lastTriggeredEvents.value = []
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
    playerState,
    currentChoices,
    storyContext,
    currentMessage,
    isLoading,
    error,
    isGameOver,
    hasError,

    // AI内容状态
    gameMeta,
    companyInfo,
    npcs,
    currentMagicalElement,
    lastNPCReactions,
    lastTriggeredEvents,

    // Actions
    startNewGame,
    submitChoice,
    fetchState,
    updateState,
    reset,
    clearError,
  }
})
