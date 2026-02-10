export enum PlayerLevel {
  INTERN = 0,
  JUNIOR = 1,
  SENIOR = 2,
  LEAD = 3,
  CTO = 4,
}

export interface PlayerState {
  // 核心属性
  chill: number // 摸鱼值 (0-100)
  progress: number // 工作进度 (0-100%)
  suspicion: number // 被怀疑度 (0-100)
  energy: number // 精力值 (0-100)

  // 资源属性
  salary: number // 薪水 ($)
  reputation: number // 声望 (0-100)

  // 进度属性
  level: PlayerLevel // 职场等级
  day: number // 当前天数 (1-30)
  week: number // 当前周数 (1-4)
  turn: number // 当天的回合数 (0-7)

  // 解锁内容
  unlockedSkills: string[] // 已解锁技能ID
  unlockedAchievements: string[] // 已解锁成就ID
  seenEvents: string[] // 已触发事件ID
}
