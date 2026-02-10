export interface SkillEffect {
  description: string
  // Mechanics implementation details would go here
}

export interface SkillConfig {
  id: string
  name: string
  description: string
  category: 'basic' | 'advanced' | 'master'
  cost: { salary?: number }
  effects: SkillEffect[]
  unlockRequirement?: string
  icon?: string
  level?: number
}
