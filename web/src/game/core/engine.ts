import type { ActionResult, ActionType } from '../types/actions'
import type { PlayerState } from '../types/player'

import { MAX_TURNS_PER_DAY } from '../data/constants'

export class GameEngine {
  executeAction(action: ActionType, currentState: PlayerState): ActionResult {
    const changes: Partial<PlayerState> = {}

    // 处理精力消耗
    if (action.cost.energy) {
      if (action.cost.energy > 0) {
        changes.energy = Math.max(0, currentState.energy - action.cost.energy)
      }
    }

    // 应用效果
    action.effects.forEach((effect) => {
      const key = effect.stat as keyof PlayerState
      const currentVal = (changes[key] !== undefined ? changes[key] : currentState[key]) as number
      const newVal = currentVal + effect.value

      let clamped = newVal
      if (['chill', 'progress', 'suspicion', 'energy', 'reputation'].includes(effect.stat)) {
        clamped = Math.max(0, Math.min(100, newVal))
      }

      (changes as any)[key] = clamped
    })

    // 更新回合
    const currentTurn = (changes.turn !== undefined ? changes.turn : currentState.turn)
    changes.turn = currentTurn + 1

    // 检查工作日结束
    if (changes.turn >= MAX_TURNS_PER_DAY) {
      changes.turn = 0
      changes.day = currentState.day + 1
      changes.energy = 100 // 次日体力恢复
      // 进度衰减（模拟项目变动或被同事拖累）
      changes.progress = Math.max(0, (changes.progress || currentState.progress) - 2)
    }

    // 随机事件判定
    const triggeredEvents: string[] = []
    const rand = Math.random()
    if (rand < 0.2) {
      triggeredEvents.push('boss_patrol')
    }
    else if (rand < 0.05) {
      triggeredEvents.push('coffee_spill')
    }

    return {
      success: true,
      action,
      changes,
      feedback: {
        success: `顺利完成了：${action.name}`,
        flavor: ['生活不只有眼前的 Bug，还有远方的摸鱼。', '只要我摸得够快，KPI 就追不上我。'],
      },
      triggeredEvents,
    }
  }
}
