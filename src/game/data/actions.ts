import type { ActionType } from '../types/actions'

export const ACTIONS: ActionType[] = [
  // 搬砖类
  {
    id: 'work_hard',
    name: '绝命冲刺',
    description: '手指在键盘上飞舞，哪怕全是 Bug 也要强行上线。',
    category: 'work',
    icon: '🚀',
    cost: { energy: 20 },
    effects: [
      { stat: 'progress', value: 8 },
      { stat: 'energy', value: -20 },
      { stat: 'chill', value: -10 },
    ],
  },
  {
    id: 'jira_update',
    name: '假装修文档',
    description: '在 Jira 和文档里反复横跳，试图让老板觉得你很忙。',
    category: 'work',
    icon: '📋',
    cost: { energy: 5 },
    effects: [
      { stat: 'progress', value: 2 },
      { stat: 'reputation', value: 2 },
      { stat: 'suspicion', value: -2 },
    ],
  },

  // 摸鱼类
  {
    id: 'slack_off',
    name: '带薪发呆',
    description: '盯着屏幕思考人生，实际上大脑已经宕机了。',
    category: 'slack',
    icon: '😶‍🌫️',
    cost: { energy: -5 },
    effects: [
      { stat: 'chill', value: 5 },
      { stat: 'energy', value: 5 },
      { stat: 'suspicion', value: 3 },
    ],
  },
  {
    id: 'browse_reddit',
    name: '刷水帖',
    description: '看看论坛里又有哪个大佬被裁了，给自己压压惊。',
    category: 'slack',
    icon: '📱',
    cost: { energy: -10 },
    effects: [
      { stat: 'chill', value: 10 },
      { stat: 'suspicion', value: 8 },
    ],
  },

  // 社交类
  {
    id: 'coffee_break',
    name: '续命圣水',
    description: '去茶水间接一杯冰美式，感觉灵魂重新回到了身体。',
    category: 'social',
    icon: '☕',
    cost: { energy: -20 },
    effects: [
      { stat: 'energy', value: 20 },
      { stat: 'chill', value: 5 },
    ],
  },
]
