# Stores 模块 - Pinia状态管理

> **[根目录](../../CLAUDE.md) > [src](../) > **stores****

最后更新: 2026-02-10

---

## 模块快照

**职责**: 游戏状态管理中心，使用Pinia实现响应式状态管理。

**Store列表**:
- **game.ts**: 游戏全局状态（回合、周期、游戏状态等）
- **player.ts**: 玩家数据（属性、技能、成就等）
- **ui.ts**: UI相关状态（弹窗、加载状态、错误提示等）

---

## Store架构

### Game Store (`game.ts`)
```typescript
interface GameState {
  isPlaying: boolean
  isPaused: boolean
  isGameOver: boolean
  currentTurn: number      // 当前回合 (0-7)
  currentDay: number       // 当前天数 (1-30)
  currentWeek: number      // 当前周数 (1-4)
  difficulty: 'normal' | 'easy' | 'hard'
  seed: number            // 随机数种子
}
```

**关键方法**:
- `startNewGame()` - 初始化新游戏
- `pauseGame()` / `resumeGame()` - 暂停/继续
- `nextTurn()` - 推进回合
- `endGame()` - 结束游戏

### Player Store (`player.ts`)
```typescript
interface PlayerState {
  // 核心属性
  chill: number        // 摸鱼值 (0-100)
  progress: number     // 工作进度 (0-100%)
  suspicion: number    // 被怀疑度 (0-100)
  energy: number       // 精力值 (0-100)

  // 资源属性
  salary: number       // 薪水
  reputation: number   // 声望

  // 进度属性
  level: PlayerLevel
  day: number
  week: number
  turn: number

  // 解锁内容
  unlockedSkills: string[]
  unlockedAchievements: string[]
  seenEvents: string[]
}
```

**关键方法**:
- `updatePlayerState()` - 更新玩家状态
- `executeAction()` - 执行行动并应用结果
- `unlockSkill()` - 解锁技能
- `addAchievement()` - 添加成就

### UI Store (`ui.ts`)
```typescript
interface UIState {
  currentEvent: GameEvent | null
  selectedAction: string | null
  showModal: boolean
  actionFeedback: ActionFeedback | null
  error: string | null
}
```

**关键方法**:
- `showEvent()` - 显示事件弹窗
- `showActionFeedback()` - 显示行动反馈
- `showError()` - 显示错误提示
- `hideModal()` - 隐藏弹窗

---

## Store间通信

```typescript
// 监听游戏结束
watch(() => gameStore.gameState.isGameOver, (isGameOver) => {
  if (isGameOver) {
    uiStore.showError('游戏结束！')
  }
})

// 监听怀疑度变化
watch(() => playerStore.playerState.suspicion, (suspicion) => {
  if (suspicion >= 50) {
    uiStore.showActionFeedback({
      type: 'warning',
      message: '老板对你开始产生怀疑了...'
    })
  }
})
```

---

## 参考文档

- **状态管理详细设计**: @docs/FRONTEND-ARCHITECTURE.md#4-状态管理
- **类型定义**: @src/game/types/
- **Pinia文档**: https://pinia.vuejs.org/
