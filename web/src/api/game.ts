import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// API 错误类型
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// 玩家状态（从后端 API 返回）
export interface ApiPlayerState {
  chill: number
  progress: number
  suspicion: number
  energy: number
  salary: number
  reputation: number
  level: number
  day: number
  week: number
  turn: number
  unlocked_skills: string[]
  unlocked_achievements: string[]
  seen_events: string[]
}

// AI 选项
export interface ApiChoice {
  id: string
  text: string
  category: 'work' | 'slack' | 'social' | 'skill' | 'growth'
  effects: {
    energy?: number
    chill?: number
    progress?: number
    suspicion?: number
    reputation?: number
  }
}

// 开始游戏请求
export interface StartGameRequest {
  difficulty: 'normal' | 'easy' | 'hard'
  player_name: string
}

// 开始游戏响应
export interface StartGameResponse {
  session_id: string
  player_state: Record<string, number>
  message: string
  choices: ApiChoice[]
}

// 获取选项响应（后端实际返回的结构）
export interface GetStateResponse {
  session: {
    session_id: string
    status: string
    metadata?: {
      player_state?: Record<string, number>
    }
  }
  recent_messages: Array<{
    role: string
    content: string
    created_at: string
  }>
  token_stats: {
    total_tokens: number
    message_count: number
  }
}

// 提交选择请求（对应后端 /api/game/act）
export interface SubmitChoiceRequest {
  session_id: string
  choice_id: string
}

// 提交选择响应（对应后端 ChoiceSubmitResponse）
export interface SubmitChoiceResponse {
  success: boolean
  player_state: Record<string, number>
  feedback: {
    success: string
    flavor?: string[]
  }
  triggered_events: string[]
  game_over: boolean
  game_over_reason?: string
}

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30秒超时（AI响应可能较慢）
})

// 请求拦截器：添加错误处理
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // 服务器返回错误状态码
      throw new ApiError(
        error.response.data?.detail || error.response.data?.message || 'API 请求失败',
        error.response.status,
        error.response.data,
      )
    }
    else if (error.request) {
      // 请求发送但没有收到响应
      throw new ApiError('网络连接失败，请检查后端服务是否启动')
    }
    else {
      // 请求配置错误
      throw new ApiError('请求配置错误')
    }
  },
)

// 游戏 API
export const gameApi = {
  /**
   * 开始新游戏
   */
  async startGame(difficulty: 'normal' | 'easy' | 'hard' = 'normal', playerName = '程序员小王'): Promise<StartGameResponse> {
    try {
      const { data } = await apiClient.post<StartGameResponse>('/api/game/start', {
        difficulty,
        player_name: playerName,
      })
      return data
    }
    catch (error) {
      if (error instanceof ApiError)
        throw error
      throw new ApiError('开始游戏失败')
    }
  },

  /**
   * 提交玩家选择（对应后端 /api/game/act）
   */
  async submitChoice(sessionId: string, choiceId: string): Promise<SubmitChoiceResponse> {
    try {
      const { data } = await apiClient.post<SubmitChoiceResponse>('/api/game/act', {
        session_id: sessionId,
        choice_id: choiceId,
      })
      return data
    }
    catch (error) {
      if (error instanceof ApiError)
        throw error
      throw new ApiError('提交选择失败')
    }
  },

  /**
   * 获取当前状态
   */
  async getState(sessionId: string): Promise<GetStateResponse> {
    try {
      const { data } = await apiClient.get<GetStateResponse>(`/api/game/state?session_id=${sessionId}`)
      return data
    }
    catch (error) {
      if (error instanceof ApiError)
        throw error
      throw new ApiError('获取状态失败')
    }
  },
}

export default gameApi
