import type { GameEvent } from '../types/events'

import { EventType } from '../types/events'

export const EVENTS: GameEvent[] = [
  {
    id: 'boss_patrol',
    type: EventType.BOSS,
    name: '老板突击检查',
    description: '老板像末影人一样瞬移到了你的身后...',
    rarity: 'common',
    choices: [
      {
        id: 'pretend_work',
        text: '快速切回 IDE 疯狂打字',
        effects: [{ stat: 'suspicion', value: -10 }],
      },
      {
        id: 'freeze',
        text: '僵住了，屏幕上还是 Reddit',
        effects: [{ stat: 'suspicion', value: 15 }],
      },
    ],
  },
  {
    id: 'server_down',
    type: EventType.RANDOM,
    name: '服务器宕机',
    description: '由于你的祖传代码触发了无限循环，服务器冒烟了！',
    rarity: 'uncommon',
    effects: [
      { stat: 'chill', value: -20 },
      { stat: 'energy', value: -30 },
      { stat: 'progress', value: -5 },
    ],
  },
  {
    id: 'red_bull_gift',
    type: EventType.SPECIAL,
    name: '同事的红牛',
    description: '隔壁桌的哥们给了你一罐红牛。',
    rarity: 'common',
    effects: [
      { stat: 'energy', value: 40 },
    ],
  },
]
