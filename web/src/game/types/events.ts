export enum EventType {
  WORK = 'work',
  SOCIAL = 'social',
  BOSS = 'boss',
  RANDOM = 'random',
  SPECIAL = 'special',
  STORY = 'story',
}

export interface EventEffect {
  stat?: string // keyof PlayerState
  value?: number
  special?: string // e.g. "unlock_skill", "game_over"
  description?: string
}

export interface EventChoice {
  id: string
  text: string
  effects: EventEffect[]
}

export interface GameEvent {
  id: string
  type: EventType
  name?: string // Optional display name
  description: string
  rarity: 'common' | 'uncommon' | 'rare' | 'legendary'
  trigger?: {
    condition: string // Simplified for now, could be a function in engine
    chance?: number
  }
  effects?: EventEffect[] // Immediate effects if no choices
  choices?: EventChoice[]
  oneTime?: boolean
}
