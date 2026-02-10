import type { PlayerState } from './player'

export interface ActionCost {
  energy?: number
  money?: number
  chill?: number
}

export interface ActionEffect {
  stat: keyof PlayerState
  value: number
  description?: string
}

export interface ActionType {
  id: string
  name: string
  description: string
  category: 'work' | 'slack' | 'skill' | 'social' | 'growth'
  icon?: string
  cost: ActionCost
  effects: ActionEffect[] // Base effects, dynamic effects handled in engine
  required?: string
}

export interface ActionResult {
  success: boolean
  action: ActionType
  changes: Partial<PlayerState>
  feedback: {
    success: string
    failure?: string
    flavor: string[]
  }
  triggeredEvents: string[]
}
