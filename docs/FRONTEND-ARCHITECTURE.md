# 摸鱼大作战 - 前端架构设计

> **项目名称**: 摸鱼大作战 (Slack Master 2024)
> **架构版本**: v1.0
> **最后更新**: 2025-02-10
> **架构师**: 老王

---

## 目录

- [1. 架构概述](#1-架构概述)
- [2. 技术栈选型](#2-技术栈选型)
- [3. 项目结构](#3-项目结构)
- [4. 状态管理](#4-状态管理)
- [5. 组件设计](#5-组件设计)
- [6. 数据流设计](#6-数据流设计)
- [7. 类型系统](#7-类型系统)
- [8. 错误处理](#8-错误处理)
- [9. 性能优化](#9-性能优化)
- [10. 开发规范](#10-开发规范)
- [11. 部署策略](#11-部署策略)

---

## 1. 架构概述

### 1.1 设计理念

**事件驱动的响应式架构**: 采用Vue 3的Composition API，构建一个基于事件驱动的游戏引擎。每个玩家行动都会触发事件链，通过Pinia管理状态，确保UI能够实时响应游戏状态变化。

### 1.2 核心原则

- **单一职责**: 每个组件和模块都有明确的职责边界
- **数据不可变**: 使用响应式数据，但避免直接修改，确保状态可追踪
- **事件驱动**: 所有游戏交互都通过事件系统处理
- **类型安全**: 使用TypeScript确保编译时类型检查
- **可扩展性**: 模块化设计，便于后续功能扩展

### 1.3 架构分层

```
┌─────────────────────────────────────────────────────┐
│                    表现层 (UI)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   HUD       │  │  事件区域   │  │  行动面板   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────┤
│                    状态层 (State)                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Pinia Store                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  │ Player      │  │ Game       │  │ UI          │  │
│  │  │ State       │  │ State      │  │ State       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │
│  └─────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│                    业务层 (Logic)                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Game Engine                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  │ Actions     │  │ Events     │  │ Skills      │  │
│  │  │ Manager     │  │ Manager    │  │ Manager     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │
│  └─────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│                    数据层 (Data)                   │
│  ┌─────────────────────────────────────────────────┐  │
│  │             Data & Config                        │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  │ Events      │  │ Skills      │  │ Endings     │  │
│  │  │ Data        │  │ Config      │  │ Config      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 2. 技术栈选型

### 2.1 核心技术栈

| 技术库 | 版本 | 用途 | 重要性 |
|--------|------|------|--------|
| Vue 3 | ^3.5.13 | 框架 | 核心 |
| TypeScript | ~5.7.2 | 类型系统 | 核心 |
| Vite | ^8.0.0-beta.13 | 构建工具 | 核心 |
| UnoCSS | ^66.6.0 | CSS原子化 | 核心 |
| Pinia | ^2.2.8 | 状态管理 | 核心 |

### 2.2 工具库

| 库名 | 版本 | 用途 | 重要性 |
|------|------|------|--------|
| @vueuse/core | ^11.3.0 | Vue组合式API工具 | 高 |
| seedrandom | ^3.0.5 | 可复现随机数 | 高 |
| zod | ^3.24.1 | 数据验证 | 高 |
| consola | ^3.2.3 | 日志系统 | 中 |

### 2.3 开发工具

| 工具 | 用途 | 配置 |
|------|------|------|
| ESLint | 代码规范 | @antfu/eslint-config |
| TypeScript | 类型检查 | tsconfig.json |
| Prettier | 代码格式化 | 集成在ESLint中 |
| Vite DevTools | 调试工具 | 插件 |

### 2.4 依赖安装命令

```bash
# 核心依赖
pnpm add pinia @vueuse/core seedrandom zod consola

# 开发依赖
pnpm add -D vite-plugin-vue-devtools

# 类型定义
pnpm add -D @types/seedrandom
```

---

## 3. 项目结构

### 3.1 目录结构

```
src/
├── main.ts                    # 应用入口
├── App.vue                   # 根组件
├── components/                # 通用组件
│   ├── HUD.vue              # HUD状态显示组件
│   ├── ActionPanel.vue      # 行动面板组件
│   ├── EventArea.vue        # 事件区域组件
│   ├── SaveManager.vue      # 存档管理组件
│   ├── SkillCard.vue        # 技能卡片组件
│   └── BaseModal.vue        # 基础弹窗组件
├── stores/                   # Pinia状态管理
│   └── index.ts             # Store入口
│   ├── game.ts              # 游戏状态Store
│   ├── player.ts            # 玩家状态Store
│   └── ui.ts                # UI状态Store
├── composables/              # 组合式函数
│   ├── useGame.ts           # 游戏逻辑组合函数
│   ├── usePlayer.ts         # 玩家数据组合函数
│   ├── useEvents.ts         # 事件系统组合函数
│   ├── useSkills.ts         # 技能系统组合函数
│   ├── useKeyboard.ts        # 键盘快捷键组合函数
│   └── useLocalStorage.ts    # 本地存储组合函数
├── game/                     # 游戏核心逻辑
│   ├── types/               # 类型定义
│   │   ├── player.ts        # 玩家相关类型
│   │   ├── game.ts          # 游戏相关类型
│   │   ├── events.ts        # 事件相关类型
│   │   ├── skills.ts        # 技能相关类型
│   │   └── actions.ts       # 行动相关类型
│   ├── core/               # 核心引擎
│   │   ├── engine.ts        # 游戏引擎主类
│   │   ├── loop.ts          # 游戏循环
│   │   └── state.ts         # 状态管理
│   ├── mechanics/           # 游戏机制
│   │   ├── actions.ts       # 行动系统
│   │   ├── skills.ts        # 技能系统
│   │   ├── events.ts        # 事件系统
│   │   ├── boss.ts          # 老板AI
│   │   └── balance.ts       # 数值平衡
│   ├── data/               # 游戏数据
│   │   ├── events.json     # 事件数据
│   │   ├── skills.json     # 技能数据
│   │   ├── endings.json     # 结局数据
│   │   └── constants.ts     # 常量定义
│   └── utils/              # 工具函数
│       ├── random.ts       # 随机数工具
│       ├── formatter.ts    # 格式化工具
│       ├── validator.ts    # 验证工具
│       └── logger.ts       # 日志工具
├── utils/                    # 全局工具
│   ├── types.ts             # 全局类型
│   ├── helpers.ts           # 通用辅助函数
│   └── constants.ts         # 全局常量
└── styles/                   # 样式文件
    ├── index.css            # 全局样式
    ├── variables.css        # CSS变量
    └── animations.css       # 动画定义

tests/                       # 测试文件
├── unit/                    # 单元测试
│   ├── game/
│   ├── mechanics/
│   └── utils/
├── e2e/                     # 端到端测试
└── setup.ts                 # 测试配置

docs/                        # 文档
├── DESIGN.md               # 游戏设计文档
├── UI-UX-DESIGN.md        # UI/UX设计方案
└── FRONTEND-ARCHITECTURE.md # 前端架构设计
```

### 3.2 模块职责

#### `components/` - UI组件
- **HUD.vue**: 显示游戏核心状态（时间、属性、等级等）
- **ActionPanel.vue**: 行动选择面板，分类显示可执行的行动
- **EventArea.vue**: 事件显示区域，包括当前事件和历史记录
- **SaveManager.vue**: 存档管理界面
- **SkillCard.vue**: 技能展示和解锁界面
- **BaseModal.vue**: 通用弹窗组件

#### `stores/` - 状态管理
- **game.ts**: 游戏全局状态（回合、周期、游戏状态等）
- **player.ts**: 玩家数据（属性、技能、成就等）
- **ui.ts**: UI相关状态（弹窗、加载状态、错误提示等）

#### `composables/` - 组合式函数
- **useGame.ts**: 游戏核心逻辑的组合函数
- **usePlayer.ts**: 玩家数据的组合函数
- **useEvents.ts**: 事件系统的组合函数
- **useSkills.ts**: 技能系统的组合函数
- **useKeyboard.ts**: 键盘快捷键处理
- **useLocalStorage.ts**: 本地存档管理

#### `game/` - 游戏核心
- **types/**: 所有TypeScript类型定义
- **core/**: 游戏引擎核心代码
- **mechanics/**: 游戏机制实现
- **data/**: 游戏配置数据
- **utils/**: 游戏相关工具函数

---

## 4. 状态管理

### 4.1 Pinia Store设计

#### 4.1.1 Game Store (`stores/game.ts`)

```typescript
// 游戏全局状态
export const useGameStore = defineStore('game', () => {
  // 状态
  const gameState = reactive<GameState>({
    isPlaying: false,
    isPaused: false,
    isGameOver: false,

    // 时间相关
    currentTurn: 0,        // 当前回合 (0-7)
    currentDay: 1,         // 当前天数 (1-30)
    currentWeek: 1,        // 当前周数 (1-4)
    currentPeriod: 'morning', // 当前时段

    // 游戏配置
    difficulty: 'normal',
    seed: Date.now(),      // 随机数种子

    // UI状态
    isLoading: false,
    error: null as string | null
  })

  // 计算属性
  const isGameOver = computed(() => gameState.isGameOver)
  const canSave = computed(() => gameState.isPlaying && !gameState.isInEvent)

  // Actions
  function startNewGame(config?: Partial<GameConfig>) {
    // 初始化新游戏
    resetGameState()
    if (config) {
      Object.assign(gameState, config)
    }
    gameState.isPlaying = true
  }

  function pauseGame() {
    gameState.isPaused = true
  }

  function resumeGame() {
    gameState.isPaused = false
  }

  function endGame() {
    gameState.isGameOver = true
    gameState.isPlaying = false
  }

  function nextTurn() {
    // 处理回合逻辑
    updateGameState()
    checkEvents()
  }

  return {
    // 状态
    gameState,

    // 计算属性
    isGameOver,
    canSave,

    // Actions
    startNewGame,
    pauseGame,
    resumeGame,
    endGame,
    nextTurn
  }
})
```

#### 4.1.2 Player Store (`stores/player.ts`)

```typescript
// 玩家状态管理
export const usePlayerStore = defineStore('player', () => {
  // 状态
  const playerState = reactive<PlayerState>({
    // 核心属性
    chill: 50,            // 摸鱼值
    suspicion: 0,         // 怀疑度
    progress: 0,          // 工作进度
    energy: 100,          // 精力值

    // 资源属性
    salary: 5000,         // 薪水
    reputation: 0,        // 声望

    // 进度属性
    level: PlayerLevel.INTERN,
    day: 1,
    week: 1,
    turn: 0,

    // 解锁内容
    unlockedSkills: [],
    unlockedAchievements: [],
    seenEvents: []
  })

  // 计算属性
  const isGameOver = computed(() => {
    return playerState.suspicion >= 80 || playerState.progress >= 100
  })

  const canWork = computed(() => playerState.energy > 20)
  const canSlack = computed(() => playerState.suspicion < 70)

  // Actions
  function updatePlayerState(changes: Partial<PlayerState>) {
    Object.assign(playerState, changes)
    persistPlayerState()
  }

  function executeAction(action: ActionType, result: ActionResult) {
    // 应用行动结果
    Object.assign(playerState, result.changes)
    persistPlayerState()
  }

  function unlockSkill(skillId: string) {
    if (!playerState.unlockedSkills.includes(skillId)) {
      playerState.unlockedSkills.push(skillId)
      persistPlayerState()
    }
  }

  function addAchievement(achievementId: string) {
    if (!playerState.unlockedAchievements.includes(achievementId)) {
      playerState.unlockedAchievements.push(achievementId)
      persistPlayerState()
    }
  }

  return {
    // 状态
    playerState,

    // 计算属性
    isGameOver,
    canWork,
    canSlack,

    // Actions
    updatePlayerState,
    executeAction,
    unlockSkill,
    addAchievement
  }
})
```

#### 4.1.3 UI Store (`stores/ui.ts`)

```typescript
// UI状态管理
export const useUIStore = defineStore('ui', () => {
  // 状态
  const uiState = reactive<UIState>({
    currentEvent: null,
    selectedAction: null,
    showModal: false,
    modalType: 'none',

    // 动画状态
    actionFeedback: null,

    // 错误状态
    error: null,

    // 主题状态
    theme: 'dark'
  })

  // Actions
  function showEvent(event: GameEvent) {
    uiState.currentEvent = event
    uiState.showModal = true
    uiState.modalType = 'event'
  }

  function selectAction(actionId: string) {
    uiState.selectedAction = actionId
  }

  function showActionFeedback(feedback: ActionFeedback) {
    uiState.actionFeedback = feedback
    setTimeout(() => {
      uiState.actionFeedback = null
    }, 3000)
  }

  function showError(message: string) {
    uiState.error = message
    setTimeout(() => {
      uiState.error = null
    }, 5000)
  }

  function hideModal() {
    uiState.showModal = false
    uiState.currentEvent = null
    uiState.selectedAction = null
  }

  return {
    // 状态
    uiState,

    // Actions
    showEvent,
    selectAction,
    showActionFeedback,
    showError,
    hideModal
  }
})
```

### 4.2 Store间通信

```typescript
// Store间的通信通过事件或直接访问
// 示例：游戏状态变更时通知UI Store
const gameStore = useGameStore()
const playerStore = usePlayerStore()
const uiStore = useUIStore()

// 监听游戏结束
watch(() => gameStore.gameState.isGameOver, (isGameOver) => {
  if (isGameOver) {
    uiStore.showError('游戏结束！')
  }
})

// 监听玩家状态变化
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

## 5. 组件设计

### 5.1 组件层次结构

```
App (根组件)
├── GameLayout (布局组件)
│   ├── Header (标题栏)
│   ├── MainContent (主内容区)
│   │   ├── HUD (状态显示)
│   │   ├── EventArea (事件区域)
│   │   └── ActionPanel (行动面板)
│   └── Footer (底部栏)
├── Modals (弹窗组件)
│   ├── EventModal (事件弹窗)
│   ├── SaveModal (存档弹窗)
│   └── SettingsModal (设置弹窗)
└── Toasts (提示组件)
    ├── ActionToast (行动反馈)
    └── ErrorToast (错误提示)
```

### 5.2 组件设计原则

1. **单一职责**: 每个组件只负责一个功能
2. **无外部依赖**: 组件通过props和events通信
3. **样式隔离**: 使用scoped CSS或CSS-in-JS
4. **可复用性**: 组件设计考虑复用场景

### 5.3 组件通信模式

```typescript
// Props (父到子)
interface Props {
  gameState: GameState
  playerState: PlayerState
  disabled?: boolean
}

// Events (子到父)
const emit = defineEmits<{
  action: [actionId: string]
  eventChoice: [choiceId: string]
  save: [slot: number]
}>()
```

---

## 6. 数据流设计

### 6.1 单向数据流

```
User Action → Component → Store → Game Engine → State Update → UI Re-render
```

### 6.2 事件驱动架构

```typescript
// 事件总线
type GameEvent =
  | { type: 'ACTION_EXECUTED'; actionId: string; result: ActionResult }
  | { type: 'TRIGGERED_EVENT'; event: GameEvent }
  | { type: 'SKILL_UNLOCKED'; skillId: string }
  | { type: 'GAME_OVER'; reason: GameOverReason }

// 事件处理器
function handleGameEvent(event: GameEvent) {
  switch (event.type) {
    case 'ACTION_EXECUTED':
      // 更新玩家状态
      playerStore.executeAction(event.actionId, event.result)
      // 检查事件触发
      eventManager.checkTriggers()
      break

    case 'TRIGGERED_EVENT':
      // 显示事件
      uiStore.showEvent(event.event)
      break

    case 'SKILL_UNLOCKED':
      // 更新技能状态
      playerStore.unlockSkill(event.skillId)
      break

    case 'GAME_OVER':
      // 结束游戏
      gameStore.endGame()
      break
  }
}
```

### 6.3 响应式数据流

```typescript
// 使用watchEffect自动响应数据变化
watchEffect(() => {
  // 当玩家状态变化时，自动更新UI
  if (playerStore.playerState.suspicion > 70) {
    uiStore.showActionFeedback({
      type: 'danger',
      message: '老板快要发现你了！'
    })
  }
})
```

---

## 7. 类型系统

### 7.1 核心类型定义

```typescript
// types/player.ts
export interface PlayerState {
  // 核心属性
  chill: number
  suspicion: number
  progress: number
  energy: number

  // 资源属性
  salary: number
  reputation: number

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

export enum PlayerLevel {
  INTERN = 0,
  JUNIOR = 1,
  SENIOR = 2,
  LEAD = 3,
  CTO = 4
}

// types/game.ts
export interface GameState {
  isPlaying: boolean
  isPaused: boolean
  isGameOver: boolean
  currentTurn: number
  currentDay: number
  currentWeek: number
  currentPeriod: Period
  difficulty: Difficulty
  seed: number
}

export type Period = 'morning' | 'afternoon' | 'evening' | 'night'
export type Difficulty = 'easy' | 'normal' | 'hard'

// types/actions.ts
export interface ActionType {
  id: string
  name: string
  category: 'work' | 'slack' | 'skill' | 'social' | 'growth'
  cost: ActionCost
  effects: ActionEffect[]
}

export interface ActionResult {
  success: boolean
  changes: Partial<PlayerState>
  feedback: ActionFeedback
  triggeredEvents: string[]
}
```

### 7.2 Zod验证模式

```typescript
import { z } from 'zod'

// 存档数据验证
const SaveDataSchema = z.object({
  version: z.string(),
  timestamp: z.number(),
  player: z.object({
    state: PlayerStateSchema,
    skills: z.array(z.string()),
    achievements: z.array(z.string())
  }),
  game: z.object({
    state: GameStateSchema,
    history: z.array(GameEventSchema)
  })
})

type SaveData = z.infer<typeof SaveDataSchema>
```

---

## 8. 错误处理

### 8.1 错误类型定义

```typescript
export enum GameErrorType {
  INVALID_ACTION = 'INVALID_ACTION',
  INSUFFICIENT_ENERGY = 'INSUFFICIENT_ENERGY',
  MAX_SUSPICION_EXCEEDED = 'MAX_SUSPICION_EXCEEDED',
  SAVE_FAILED = 'SAVE_FAILED',
  LOAD_FAILED = 'LOAD_FAILED'
}

export interface GameError {
  type: GameErrorType
  message: string
  timestamp: number
  context?: Record<string, any>
}
```

### 8.2 错误处理策略

```typescript
// 全局错误处理器
export function handleError(error: unknown) {
  if (error instanceof GameError) {
    // 处理游戏错误
    uiStore.showError(error.message)
    logger.error(error)
  } else if (error instanceof Error) {
    // 处理普通错误
    uiStore.showError('发生错误: ' + error.message)
    logger.error(error)
  } else {
    // 处理未知错误
    uiStore.showError('发生未知错误')
    logger.error('Unknown error:', error)
  }
}

// Actions错误处理
async function executeAction(actionId: string) {
  try {
    const result = await gameEngine.executeAction(actionId)
    return result
  } catch (error) {
    handleError(error)
    return null
  }
}
```

### 8.3 错误边界组件

```vue
<template>
  <div v-if="error" class="error-boundary">
    <h2>出现错误</h2>
    <p>{{ error.message }}</p>
    <button @click="retry">重试</button>
    <button @click="reset">重置游戏</button>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'

const error = ref<Error | null>(null)

onErrorCaptured((err) => {
  error.value = err
  return false // 阻止错误继续向上传播
})

const retry = () => {
  error.value = null
}

const reset = () => {
  // 重置游戏状态
  gameStore.startNewGame()
  error.value = null
}
</script>
```

---

## 9. 性能优化

### 9.1 渲染优化

```typescript
// 使用shallowRef避免深层响应式
const playerData = shallowRef<PlayerData>(initialPlayerData)

// 使用computed缓存计算结果
const formattedStats = computed(() => {
  return {
    chill: formatPercentage(playerState.chill),
    suspicion: formatPercentage(playerState.suspicion)
  }
})

// 使用v-once优化静态内容
<div v-once class="static-content">
  游戏标题和版本信息
</div>
```

### 9.2 状态优化

```typescript
// 使用debounce减少高频更新
import { useDebounceFn } from '@vueuse/core'

const debouncedUpdate = useDebounceFn((newState: Partial<PlayerState>) => {
  playerStore.updatePlayerState(newState)
}, 300)

// 使用throttle控制更新频率
const throttledNextTurn = useThrottleFn(() => {
  gameStore.nextTurn()
}, 1000)
```

### 9.3 资源优化

```typescript
// 懒加载组件
const HeavyComponent = defineAsyncComponent(() =>
  import('./HeavyComponent.vue')
)

// 图片懒加载
const loadImages = async () => {
  const images = import.meta.glob('./assets/images/*')
  for (const path in images) {
    await images[path]()
  }
}
```

---

## 10. 开发规范

### 10.1 代码组织规范

1. **文件命名**: 使用kebab-case
2. **组件命名**: 使用PascalCase
3. **函数命名**: 使用camelCase
4. **常量命名**: 使用SCREAMING_SNAKE_CASE

### 10.2 TypeScript规范

```typescript
// 必须使用类型注解
const playerState: PlayerState = reactive(initialPlayerState)

// 使用接口定义对象结构
interface PlayerConfig {
  name: string
  difficulty: Difficulty
  seed?: number
}

// 使用泛型增强类型安全
function updateState<T>(state: Ref<T>, updates: Partial<T>): void {
  Object.assign(state.value, updates)
}
```

### 10.3 组件开发规范

```vue
<template>
  <!-- 使用语义化HTML标签 -->
  <section class="action-panel">
    <!-- 每个交互元素都要有合适的ARIA属性 -->
    <button
      v-for="action in actions"
      :key="action.id"
      :aria-label="`${action.name} - ${action.description}`"
      @click="handleAction(action.id)"
      :class="['action-btn', action.category]"
    >
      <span class="icon">{{ action.icon }}</span>
      <span class="text">{{ action.name }}</span>
    </button>
  </section>
</template>

<script setup lang="ts">
// 使用明确的props定义
interface Props {
  actions: Action[]
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

// 使用明确的events定义
const emit = defineEmits<{
  action: [actionId: string]
}>()

// 业务逻辑放在composable中
const { executeAction } = useGameEngine()

const handleAction = (actionId: string) => {
  if (props.disabled) return
  emit('action', actionId)
  executeAction(actionId)
}
</script>

<style scoped>
/* 使用scoped样式 */
.action-panel {
  @apply bg-card rounded-lg p-4;
}

.action-btn {
  @apply transition-all duration-200;
}

/* 使用CSS变量 */
.action-btn {
  --color-primary: #00FFFF;
  color: var(--color-primary);
}
</style>
```

### 10.4 Git工作流规范

```bash
# 提交消息格式
<type>: <description>

# 类型说明
feat:     新功能
fix:      Bug修复
docs:     文档更新
style:    代码格式化
refactor: 重构
test:     测试相关
chore:    构建或工具相关
```

### 10.5 代码审查清单

- [ ] TypeScript类型正确
- [ ] 组件职责单一
- [ ] 错误处理完善
- [ ] 性能考虑周全
- [ ] 代码注释清晰
- [ ] 遵循编码规范
- [ ] 无硬编码值
- [ ] 无重复代码

---

## 11. 部署策略

### 11.1 构建配置

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [vue()],
  build: {
    // 启用CSS代码分割
    cssCodeSplit: true,

    // 构建优化
    rollupOptions: {
      output: {
        manualChunks: {
          // 将第三方库单独打包
          vendor: ['vue', 'pinia'],
          utils: ['@vueuse/core']
        }
      }
    }
  },

  // 预加载资源
  preview: {
    port: 4173
  }
})
```

### 11.2 环境变量

```bash
# .env
VITE_APP_VERSION=1.0.0
VITE_APP_TITLE=摸鱼大作战
VITE_API_BASE_URL=https://api.example.com
```

### 11.3 部署选项

```bash
# 静态部署到GitHub Pages
pnpm build
gh-pages -d dist

# 部署到Vercel
# 1. 连接GitHub仓库
# 2. 配置Vercel项目
# 3. 自动部署
```

---

## 总结

这套前端架构设计采用了现代化的技术栈和最佳实践，确保了代码的可维护性、可扩展性和性能。通过模块化的设计、完善的状态管理、严格的类型检查和错误处理机制，为摸鱼大作战游戏提供了坚实的技术基础。

### 架构优势：

1. **可扩展性**: 模块化设计便于添加新功能
2. **可维护性**: 清晰的代码结构和类型定义
3. **性能**: 优化的渲染和状态管理
4. **开发体验**: TypeScript + VS Code 智能提示
5. **测试友好**: 模块化便于单元测试

### 下一步：

1. 实现游戏核心引擎
2. 完善状态管理
3. 添加事件系统
4. 实现存档功能
5. 编写测试用例

**最后更新**: 2025-02-10
**架构师**: 老王 (Laowang)