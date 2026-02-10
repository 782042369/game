# Game 模块 - 游戏核心

> **[根目录](../../CLAUDE.md) > [src](../) > **game****

最后更新: 2026-02-10

---

## 模块快照

**职责**: 游戏核心逻辑层，包含类型定义、游戏引擎、数据配置。

**子模块**:
- **types/**: TypeScript类型定义
- **core/**: 游戏引擎 (GameEngine)
- **data/**: 游戏配置数据 (行动、事件、常量)

---

## 目录结构

```
game/
├── types/           # 类型定义
│   ├── player.ts    # 玩家状态类型
│   ├── actions.ts   # 行动系统类型
│   ├── events.ts    # 事件系统类型
│   ├── game.ts      # 游戏状态类型
│   └── skills.ts    # 技能系统类型
├── core/            # 游戏引擎
│   └── engine.ts    # GameEngine类
└── data/            # 游戏数据
    ├── actions.ts   # 行动配置
    ├── events.ts    # 事件配置
    └── constants.ts # 常量定义
```

---

## 核心类型

### PlayerState (@types/player.ts)
```typescript
interface PlayerState {
  chill: number        // 摸鱼值 (0-100)
  progress: number     // 工作进度 (0-100%)
  suspicion: number    // 被怀疑度 (0-100)
  energy: number       // 精力值 (0-100)
  salary: number       // 薪水
  reputation: number   // 声望
  level: PlayerLevel   // 职场等级
  day: number          // 当前天数
  turn: number         // 当前回合
  unlockedSkills: string[]
  unlockedAchievements: string[]
  seenEvents: string[]
}
```

### ActionType (@types/actions.ts)
```typescript
interface ActionType {
  id: string
  name: string
  description: string
  category: 'work' | 'slack' | 'skill' | 'social' | 'growth'
  icon?: string
  cost: ActionCost
  effects: ActionEffect[]
}
```

---

## 游戏引擎 (GameEngine)

**文件**: @src/game/core/engine.ts

**核心方法**:
```typescript
class GameEngine {
  executeAction(action: ActionType, currentState: PlayerState): ActionResult
}
```

**功能**:
- 处理精力消耗
- 应用行动效果
- 更新回合和天数
- 检查工作日结束
- 触发随机事件

---

## 游戏数据

### 行动配置 (@data/actions.ts)
定义所有可执行的行动：
- **工作类**: 绝命冲刺、假装修文档
- **摸鱼类**: 带薪发呆、刷水帖
- **社交类**: 续命圣水

### 事件配置 (@data/events.ts)
定义游戏中触发的随机事件

### 常量定义 (@data/constants.ts)
游戏核心常量（如最大回合数等）

---

## 参考文档

- **游戏设计**: @docs/DESIGN.md
- **游戏机制**: @docs/DESIGN.md#3-核心系统设计
- **类型系统**: @docs/FRONTEND-ARCHITECTURE.md#7-类型系统
