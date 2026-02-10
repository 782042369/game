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
  player_state: ApiPlayerState
  message: string
}

// 获取选项请求
export interface GetChoicesRequest {
  session_id: string
}

// 获取选项响应
export interface GetChoicesResponse {
  story_context: string
  choices: ApiChoice[]
}

// 提交选择请求
export interface SubmitChoiceRequest {
  session_id: string
  choice_id: string
}

// 提交选择响应
export interface SubmitChoiceResponse {
  player_state: ApiPlayerState
  feedback: {
    success: string
    flavor?: string[]
  }
  triggered_events?: string[]
}

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10秒超时
})

// 请求拦截器：添加错误处理
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // 服务器返回错误状态码
      throw new ApiError(
        error.response.data?.message || 'API 请求失败',
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
   * 获取 AI 生成的选项
   */
  async getChoices(sessionId: string): Promise<GetChoicesResponse> {
    try {
      const { data } = await apiClient.post<GetChoicesResponse>('/api/game/choices', {
        session_id: sessionId,
      })
      return data
    }
    catch (error) {
      if (error instanceof ApiError)
        throw error
      throw new ApiError('获取选项失败')
    }
  },

  /**
   * 提交玩家选择
   */
  async submitChoice(sessionId: string, choiceId: string): Promise<SubmitChoiceResponse> {
    try {
      const { data } = await apiClient.post<SubmitChoiceResponse>('/api/game/choice/submit', {
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
}

export default gameApi
