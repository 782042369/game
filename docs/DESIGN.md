# 摸鱼大作战 - 完整设计文档

> **项目代号**: Slack Master 2024
> **游戏类型**: 文字冒险 + 模拟经营 + Roguelike
> **目标平台**: Web (Vue 3 + TypeScript)
> **文档版本**: v1.0
> **最后更新**: 2025-02-10

---

## 目录

- [1. 游戏概述](#1-游戏概述)
- [2. MDA框架设计](#2-mda框架设计)
- [3. 核心系统设计](#3-核心系统设计)
- [4. 技术架构](#4-技术架构)
- [5. 事件系统与文本创作](#5-事件系统与文本创作)
- [6. 开发路线图](#6-开发路线图)

---

## 1. 游戏概述

### 1.1 核心概念

**摸鱼大作战**是一款以程序员职场为背景的**纯文字冒险游戏**。玩家扮演一名程序员,在完成工作任务的同时最大化摸鱼收益,同时避免被老板发现。

**设计理念**:
- ✅ **纯文字体验** - 不依赖动画和音效,完全通过文字传达信息
- ✅ **程序员梗文化** - 使用真实的程序员黑话和互联网梗
- ✅ **朴素风格** - 简洁清晰的界面,专注于游戏内容

### 1.2 目标受众

- **主要群体**: 20-35岁的程序员、IT从业者
- **次要群体**: 社畜、职场吐槽爱好者
- **玩家画像**: 熟悉互联网文化,喜欢黑色幽默,追求策略深度

### 1.3 独特卖点

1. **真实职场体验**: 需求变更、开会、甩锅等真实场景
2. **策略深度**: 风险-收益平衡,资源管理
3. **高重玩性**: Roguelike元素 + 多结局
4. **社区共鸣**: 400+条程序员梗和职场黑话

### 1.4 体验目标

| 情感 | 实现方式 |
|------|----------|
| **紧张感** | 老板巡逻时的文字描述和心理压力 |
| **幽默感** | 黑色幽默文本 + 梗文化 |
| **成就感** | 技能解锁 + 升职 + 成就 |
| **代入感** | 真实职场场景 + 角色成长 |
| **策略感** | 资源管理 + 风险控制 |

---

## 2. MDA框架设计

### 2.1 Mechanics (机制) - 规则系统

#### 2.1.1 核心属性系统

```typescript
interface PlayerState {
  // 核心属性
  chill: number;        // 摸鱼值 (0-100) - 越高越爽,影响结局
  progress: number;     // 工作进度 (0-100%) - deadline前必须完成
  suspicion: number;    // 被怀疑度 (0-100) - 超过80会被开除
  energy: number;       // 精力值 (0-100) - 影响行动成功率

  // 资源属性
  salary: number;       // 薪水 ($) - 购买摸鱼道具
  reputation: number;   // 声望 (0-100) - 影响升职

  // 进度属性
  level: PlayerLevel;   // 职场等级 (实习生 → 初级 → 高级 → CTO)
  day: number;          // 当前天数 (1-30)
  week: number;         // 当前周数 (1-4)
  turn: number;         // 当天的回合数 (0-7)

  // 解锁内容
  unlockedSkills: string[];     // 已解锁技能ID
  unlockedAchievements: string[]; // 已解锁成就ID
  seenEvents: string[];         // 已触发事件ID
}

enum PlayerLevel {
  INTERN = 0,        // 实习生
  JUNIOR = 1,        // 初级工程师
  SENIOR = 2,        // 高级工程师
  LEAD = 3,          // 技术主管
  CTO = 4            // CTO
}
```

#### 2.1.2 行动系统

```typescript
enum ActionType {
  // 工作类
  WORK_HARD = 'work_hard',          // 认真工作 (+进度, -精力, -摸鱼)
  JIRA_UPDATE = 'jira_update',      // 更新Jira (+进度, +声望, -摸鱼)
  CODE_REVIEW = 'code_review',      // 代码Review

  // 摸鱼类
  SLACK_OFF = 'slack_off',          // 正常摸鱼 (+摸鱼, +精力, +怀疑)
  BROWSE_REDDIT = 'browse_reddit',  // 刷摸鱼贴 (+摸鱼, +怀疑, 随机事件)
  TOILET_SLACK = 'toilet_slack',    // 厕所摸鱼 (+摸鱼, +怀疑, 需技能)

  // 技能类
  PRETEND_WORK = 'pretend_work',    // 假装工作 (+摸鱼, -怀疑, 需技能)
  ALT_TAB_MASTER = 'alt_tab_master',// Alt+Tab切换 (+摸鱼, -怀疑, 需技能)

  // 社交类
  COFFEE_BREAK = 'coffee_break',    // 咖啡休息 (+精力, +摸鱼, +同事好感)
  HELP_COLLEAGUE = 'help_colleague',// 帮同事 (+薪水, +好感, -精力)
  GOSSIP = 'gossip',                // 八卦 (+摸鱼, +情报, +怀疑)

  // 成长类
  LEARN_SKILL = 'learn_skill',      // 学习技能 (-精力, -薪水, 解锁技能)
  SIDE_PROJECT = 'side_project'     // 副业项目 (+薪水, -精力, -摸鱼)
}
```

#### 2.1.3 技能树系统

```typescript
interface SkillConfig {
  id: string;
  name: string;
  description: string;
  category: 'basic' | 'advanced' | 'master';
  cost: { salary?: number };
  effects: SkillEffect[];
  unlockRequirement: any;
}

// 基础技能树
basic: {
  alt_tab_master: {      // Alt+Tab大师
    cost: 0,
    effect: "降低50%被怀疑度",
    unlock: "开局自带"
  },
  coffee_ninja: {        // 咖啡忍者
    cost: 500,
    effect: "咖啡休息时间+50%",
    unlock: "Chill达到30"
  }
}

// 进阶技能树
advanced: {
  keyboard_warrior: {    // 键盘战士
    cost: 2000,
    effect: "假装敲代码逼真度+100%",
    unlock: "存活7天"
  },
  meeting_avoider: {     // 会议躲避者
    cost: 3000,
    effect: "跳过50%的会议",
    unlock: "声望达到50"
  }
}

// 大师技能树
master: {
  toilet_strategist: {   // 厕所战略家
    cost: 8000,
    effect: "厕所摸鱼时间+100%",
    unlock: "厕所摸鱼累计10次"
  },
  jit_commit: {          // JIT提交大师
    cost: 10000,
    effect: "deadline前效率+200%",
    unlock: "在deadline前1小时完成3次"
  }
}
```

#### 2.1.4 老板AI系统

```typescript
interface BossAI {
  // 巡逻模式
  patrol: {
    morning: { frequency: 0.3, suspicion: 0.5 },    // 早晨:心情好
    afternoon: { frequency: 0.2, suspicion: 0.3 },  // 午后:犯困
    evening: { frequency: 0.6, suspicion: 0.8 },    // 傍晚:检查工作
    friday: { frequency: 0.1, suspicion: 0.2 }     // 周五:提前下班
  },

  // 怀疑度判定
  detection: {
    threshold: 80,         // 超过80%直接开除
    warning: 50,           // 超过50%口头警告
    safe: 20               // 20%以下安全
  }
}
```

### 2.2 Dynamics (动态) - 玩法交互

#### 2.2.1 风险-收益机制

```
高风险高收益:
├── 刷摸鱼贴 (+摸鱼, +怀疑, 随机事件)
├── 副业项目 (+薪水, -精力, 可能被发现)
└── 厕所战略 (+摸鱼, +怀疑, 长时间离岗)

低风险低收益:
├── 认真工作 (+进度, -摸鱼, 安全)
├── 更新Jira (+进度, +声望, 无趣)
└── 帮同事 (+薪水, +好感, -精力)

策略型:
├── 假装工作 (+摸鱼, -怀疑, 需技能)
├── Alt+Tab (+摸鱼, -怀疑, 需技能)
└── 咖啡休息 (+精力, +摸鱼, +同事好感)
```

#### 2.2.2 时间压力系统

```
时间节点压力曲线:

9:00-10:00  → 压力 20% (早晨轻松)
10:00-12:00 → 压力 40% (开始工作)
12:00-13:00 → 压力 10% (午休黄金时间)
13:00-15:00 → 压力 50% (下午困倦期)
15:00-17:00 → 压力 70% (冲刺阶段)
17:00-18:00 → 压力 90% (deadline逼近)

特殊事件:
├── Monday Morning  → 压力 +30%
├── Friday Afternoon → 压力 -40%, 摸鱼 +50%
└── Deadline Day    → 压力 +100%
```

### 2.3 Aesthetics (美学) - 情感体验

#### 2.3.1 反馈系统

**纯文字反馈设计**:
```typescript
interface TextFeedback {
  // 即时反馈
  immediate: string;         // "你认真地完成了代码..."

  // 数值变化
  statChanges: {
    text: string;            // "进度+15%, 精力-10"
    highlighted: string[];   // 高亮显示的关键数值
  };

  // 风味文本
  flavorText: string[];      // ["这就是程序员的日常啊..."]

  // 程序员梗
  programmerMeme: string;    // "又是改需求的一天,艹"
}
```

---

## 3. 核心系统设计

### 3.1 游戏引擎API

#### 3.1.1 GameEngine 类

```typescript
/**
 * 游戏引擎核心类
 */
class GameEngine {
  /**
   * 初始化游戏
   */
  initialize(config?: Partial<GameConfig>): void;

  /**
   * 开始新游戏
   */
  startNewGame(seed?: number): void;

  /**
   * 执行玩家行动
   */
  executeAction(action: ActionType): ActionResult;

  /**
   * 更新游戏状态(每回合调用)
   */
  update(): void;

  /**
   * 检查游戏是否结束
   */
  checkGameOver(): GameOverInfo | null;
}
```

#### 3.1.2 ActionResult 接口

```typescript
interface ActionResult {
  success: boolean;
  action: ActionType;

  // 数值变化
  changes: {
    chill: number;
    progress: number;
    suspicion: number;
    energy: number;
    salary?: number;
    reputation?: number;
  };

  // 文本反馈
  feedback: {
    success: string;          // 成功文本
    failure?: string;         // 失败文本
    flavor: string[];         // 风味文本(程序员梗)
  };

  // 触发的事件
  triggeredEvents: GameEvent[];
}
```

### 3.2 事件系统API

#### 3.2.1 事件定义

```typescript
interface GameEvent {
  id: string;
  type: EventType;
  name: string;
  description: string;

  // 触发条件
  trigger: EventTrigger;

  // 事件效果
  effects: EventEffect[];

  // 选择分支(如果有)
  choices?: EventChoice[];

  // 元数据
  rarity: 'common' | 'uncommon' | 'rare' | 'legendary';
  oneTime: boolean;
}

enum EventType {
  WORK = 'work',
  SOCIAL = 'social',
  BOSS = 'boss',
  RANDOM = 'random',
  SPECIAL = 'special',
  STORY = 'story'
}
```

#### 3.2.2 EventManager 类

```typescript
class EventManager {
  private eventPool: Map<string, GameEvent>;
  private triggeredEvents: Set<string>;

  /**
   * 注册事件
   */
  registerEvent(event: GameEvent): void;

  /**
   * 获取所有可触发的事件
   */
  getAvailableEvents(state: PlayerState): GameEvent[];

  /**
   * 触发事件
   */
  triggerEvent(eventId: string): EventResult;

  /**
   * 检查是否应该触发事件
   */
  checkEventTrigger(state: PlayerState): GameEvent | null;
}
```

### 3.3 技能系统API

#### 3.3.1 SkillManager 类

```typescript
class SkillManager {
  private skills: Map<string, SkillConfig>;
  private playerSkills: Map<string, number>;

  /**
   * 获取所有技能
   */
  getAllSkills(): SkillConfig[];

  /**
   * 获取可解锁技能
   */
  getUnlockableSkills(state: PlayerState): SkillConfig[];

  /**
   * 解锁技能
   */
  unlockSkill(skillId: string): boolean;

  /**
   * 应用技能效果
   */
  applySkillEffects(action: ActionType): SkillEffectResult;

  /**
   * 计算技能加成
   */
  calculateSkillBonus(stat: keyof PlayerState, baseValue: number): number;
}
```

### 3.4 存档系统API

#### 3.4.1 SaveManager 类

```typescript
class SaveManager {
  private saveSlot: number = 1;
  private maxSlots: number = 3;

  /**
   * 保存游戏
   */
  saveGame(slot?: number): Promise<boolean>;

  /**
   * 加载游戏
   */
  loadGame(slot: number): Promise<SaveData | null>;

  /**
   * 删除存档
   */
  deleteSave(slot: number): Promise<boolean>;

  /**
   * 导出存档(用于分享)
   */
  exportSave(): string;

  /**
   * 导入存档
   */
  importSave(data: string): boolean;

  /**
   * 自动保存
   */
  autoSave(): void;
}
```

### 3.5 UI状态管理

#### 3.5.1 Pinia Store 定义

```typescript
/**
 * 游戏Store (Pinia)
 */
export const useGameStore = defineStore('game', () => {
  // 状态
  const playerState = reactive<PlayerState>(initialPlayerState);
  const gameState = reactive<GameInfo>(initialGameState);
  const uiState = reactive<UIState>(initialUIState);

  // 计算属性
  const isGameOver = computed(() => gameState.isGameOver);
  const currentTurn = computed(() => gameState.turn);
  const canSave = computed(() => !gameState.isInEvent);

  // Actions
  function executeAction(action: ActionType) {
    const engine = new GameEngine();
    const result = engine.executeAction(action);
    applyActionResult(result);
  }

  function updatePlayerState(changes: Partial<PlayerState>) {
    Object.assign(playerState, changes);
  }

  function triggerEvent(event: GameEvent) {
    uiState.currentEvent = event;
    gameState.isInEvent = true;
  }

  function resolveEvent(choiceId: string) {
    gameState.isInEvent = false;
    uiState.currentEvent = null;
  }

  return {
    playerState,
    gameState,
    uiState,
    isGameOver,
    currentTurn,
    canSave,
    executeAction,
    updatePlayerState,
    triggerEvent,
    resolveEvent
  };
});
```

---

## 4. 技术架构

### 4.1 技术选型原则

1. **不重复造轮子** - 优先使用成熟的开源库
2. **纯文字游戏** - 不依赖动画和音效库
3. **轻量高效** - 选择体积小、性能好的库
4. **社区活跃** - 使用维护良好的库
5. **TypeScript优先** - 优先选择有完善TS支持的库

### 4.2 核心技术栈

```json
{
  "dependencies": {
    "vue": "^3.5.13",              // 框架
    "pinia": "^2.2.8",             // 状态管理
    "@vueuse/core": "^11.3.0",     // 工具函数
    "seedrandom": "^3.0.5",        // 随机数生成
    "zod": "^3.24.1",              // 数据验证
    "consola": "^3.2.3"            // 日志系统
  },
  "devDependencies": {
    "typescript": "~5.6.2",
    "vite": "^6.0.11",
    "vitest": "^2.1.8",            // 测试框架
    "unocss": "^0.66.1",           // 原子化CSS
    "vite-plugin-vue-devtools": "^7.7.0",
    "@types/node": "^22.10.5",
    "@types/seedrandom": "^3.0.8"
  }
}
```

### 4.3 依赖库说明

#### Pinia - 状态管理

**为什么选择?**
- Vue 3官方推荐
- 完善的TypeScript支持
- API简洁,学习成本低

**使用场景**:
- 玩家状态管理
- 游戏进度存储
- UI状态控制

#### VueUse - 工具函数库

**为什么选择?**
- Vue 3生态最流行的工具库
- 100+个实用函数
- Tree-shakable,按需引入

**常用功能**:
```typescript
import {
  useLocalStorage,  // 本地存储(用于存档)
  useTimestamp,     // 时间戳(用于游戏计时)
  useDebounceFn,    // 防抖
  useThrottleFn,    // 节流
  useIdle           // 检测用户空闲
} from '@vueuse/core'
```

#### seedrandom - 随机数生成

**为什么选择?**
- 可播种的随机数生成器
- 保证存档可复现
- 轻量级(~3KB)

**使用场景**:
```typescript
import seedrandom from 'seedrandom'

// 创建可复现的随机数生成器
const rng = seedrandom('save-file-seed-123')
const shouldTriggerEvent = rng() < 0.3  // 30%概率
```

#### Zod - 数据验证

**为什么选择?**
- TypeScript优先
- 类型自动推导
- 轻量级

**使用场景**:
```typescript
import { z } from 'zod'

// 定义存档数据结构
const SaveDataSchema = z.object({
  version: z.string(),
  timestamp: z.number(),
  player: z.object({
    state: PlayerStateSchema
  })
})

type SaveData = z.infer<typeof SaveDataSchema>
```

#### UnoCSS - 样式方案

**为什么选择?**
- 即时的原子化CSS引擎
- 比Tailwind CSS更快
- 按需生成,无冗余

**朴素风格配置**:
```typescript
export default defineConfig({
  theme: {
    colors: {
      primary: '#333',
      secondary: '#666',
      accent: '#0066cc'
    }
  },
  shortcuts: {
    'btn': 'px-4 py-2 rounded bg-primary text-white',
    'card': 'p-4 border border-gray-200 rounded'
  }
})
```

### 4.4 不需要的库

#### ❌ 动画库
- **GSAP**: 不需要复杂动画
- **Animate.css**: 纯文字游戏不需要

#### ❌ 音效库
- **Howler.js**: 不需要音效
- **Tone.js**: 不需要音乐

#### ❌ 复杂UI库
- **Element Plus**: 太重,自己写简单组件
- **Ant Design Vue**: 太重,朴素文字游戏

#### ❌ 已过时的库
- **Vuex**: Pinia更好
- **Moment.js**: 已废弃,体积大

### 4.5 项目结构

```
src/
├── game/                    # 游戏核心
│   ├── core/               # 核心引擎
│   │   ├── engine.ts       # 游戏主引擎
│   │   ├── state.ts        # 状态管理
│   │   └── loop.ts         # 游戏循环
│   │
│   ├── mechanics/          # 游戏机制
│   │   ├── actions.ts      # 行动系统
│   │   ├── skills.ts       # 技能系统
│   │   ├── events.ts       # 事件系统
│   │   └── boss.ts         # 老板AI
│   │
│   ├── ui/                 # UI组件
│   │   ├── HUD.vue         # 抬头显示
│   │   ├── ActionPanel.vue # 行动面板
│   │   └── EventModal.vue  # 事件弹窗
│   │
│   └── data/               # 游戏数据
│       ├── events.ts       # 事件文本库
│       ├── skills.ts       # 技能配置
│       └── endings.ts      # 结局配置
│
├── stores/                 # Pinia状态
│   └── game.ts            # 游戏状态
│
├── components/             # Vue组件
├── App.vue
└── main.ts
```

### 4.6 数据流设计

```typescript
// 单向数据流
User Input → Component → Store (Pinia) → Game Engine → State Update → UI Re-render

// 响应式状态管理
interface GameState {
  player: reactive<PlayerState>,
  game: reactive<GameInfo>,
  ui: reactive<UIState>
}

// 事件驱动
EventBus.emit('action:execute', action);
EventBus.on('state:changed', (newState) => updateUI());
```

---

## 5. 事件系统与文本创作

### 5.1 文本创作原则

1. **纯文字体验** - 不依赖动画和音效,完全通过文字传达信息
2. **程序员梗文化** - 使用真实的程序员黑话和互联网梗
3. **黑色幽默** - 职场讽刺,但不恶俗
4. **简洁有力** - 每段文本控制在100字以内
5. **即时反馈** - 让玩家一眼就能看懂发生了什么

### 5.2 事件示例

#### 5.2.1 工作相关事件

```yaml
id: code_review_success
type: work
rarity: common
text: |
  大佬Review了你的代码,在群里说:"写得不错!逻辑清晰,注释完整。"
  你感觉内心一阵暖流...
effects:
  reputation: +10
  chill: +5
  energy: +5
---

id: requirement_change_major
type: work
rarity: uncommon
text: |
  【邮件】产品经理:"经过和业务方沟通,我们需要调整一下这个功能的逻辑..."
  你打开邮件附件,发现整个需求文档都改了。
  之前写的代码?全废了。
effects:
  progress: -25
  chill: -30
  energy: -20
---

id: server_crash
type: work
rarity: rare
text: |
  【钉钉】运维:"生产环境报警了!快看日志!"
  你一边骂着"又是哪个憨批改了配置",一边打开终端...
  好不容易定位问题,紧急修复,总算没出大事。
effects:
  progress: -10
  energy: -30
  salary: +500
  suspicion: -20
```

#### 5.2.2 摸鱼相关事件

```yaml
id: boss_patrol_safe
type: boss
rarity: common
text: |
  老板从你身后走过,扫了一眼你的屏幕。
  你正好在写代码,运气不错!
effects:
  suspicion: -5
  chill: +5
---

id: boss_caught
type: boss
rarity: uncommon
text: |
  老板突然站在你身后:"你在看什么?"
  你手忙脚乱地切换窗口,但还是被看到了Reddit页面...
  老板摇摇头走开了。
effects:
  suspicion: +25
  chill: -20
---

id: toilet_slack_success
type: slack
rarity: common
text: |
  你拿着手机去了厕所,一刷就是20分钟。
  看着时间,你心想:这才是真正的摸鱼圣地啊!
effects:
  chill: +15
  suspicion: +10
  progress: -5
```

#### 5.2.3 社交相关事件

```yaml
id: coffee_break_normal
type: social
rarity: common
text: |
  你走到茶水间接了杯咖啡,遇到同事在聊八卦。
  "听说隔壁组有个被裁了..."
  你一边喝咖啡一边听着,感觉放松了不少。
effects:
  energy: +15
  chill: +10
  suspicion: +5
---

id: team_lunch_friday
type: social
rarity: uncommon
trigger: friday
text: |
  周五中午,主管说:"今天中午公司请客,大家去吃顿好的!"
  一行十几个人去了附近的火锅店,喝酒聊天,吐槽工作。
  下午大家都有点晕乎乎的,工作效率明显降低...
effects:
  energy: +30
  chill: +25
  progress: -10
  suspicion: -15
```

#### 5.2.4 特殊事件

```yaml
id: monday_blues
type: special
rarity: common
trigger: monday_morning
text: |
  周一的早晨,你不想起床,不想上班,不想面对那些烂摊子。
  坐在工位上,你盯着屏幕发了10分钟呆...
  怎么周末过得这么快啊...
effects:
  energy: -15
  chill: -20
  motivation: -10
---

id: friday_afternoon_vibes
type: special
rarity: common
trigger: friday_afternoon
text: |
  周五下午4点,办公室里弥漫着一种轻松的氛围。
  有人开始收拾东西,有人聊着周末计划...
  你也打开手机,看看周末有什么安排。
  老板?老板早就提前下班了。
effects:
  chill: +30
  suspicion: -20
  energy: +10
---

id: recruiter_call
type: special
rarity: rare
text: |
  【未知号码】你接起电话,对面传来声音:
  "你好,我是XX公司的猎头,看到您的简历很匹配我们的职位..."
  你们聊了一会儿,对方开的薪资比现在高50%...
  但现在真的适合跳槽吗?
choices:
  - id: accept_interview
    text: 约时间面试
    effects:
      chill: +20
      info: "job_opportunity"

  - id: politely_decline
    text: 婉言谢绝
    effects:
      reputation: +5
      chill: -5
```

#### 5.2.5 结局事件

```yaml
id: promotion_opportunity
type: story
rarity: rare
condition: reputation >= 80, level < 4
text: |
  主管把你叫到办公室:"公司决定晋升你为高级工程师。
  恭喜啊!这是你应得的。"
  你握着主管的手,感觉这么多年的努力终于有了回报。
  但你也知道,职位越高,责任越重...
effects:
  level: +1
  salary: +1000
  reputation: +20
  ending: "promoted"
---

id: fired
type: story
rarity: rare
condition: suspicion >= 80
text: |
  HR把你叫到办公室,递给你一份文件:
  "经过公司讨论,我们决定和你解除劳动合同。
  祝你未来一切顺利。"
  你拿着离职证明,走出公司大门...
  也许,该换个活法了?
effects:
  ending: "fired"
```

### 5.3 文本风格指南

#### 5.3.1 描写风格

**好的示例:**
```
你一边骂着"又是哪个憨批改了配置",一边打开终端...
好不容易定位问题,紧急修复,总算没出大事。
```

**不好的示例:**
```
你感到很生气,因为有人改了配置导致服务器出问题。
经过努力,你成功修复了这个问题。
```

#### 5.3.2 程序员黑话

- **憨批** = 代码写得烂的人
- **摸鱼** = 上班不工作
- **甩锅** = 推卸责任
- **站会** = 每日会议
- **Review** = 代码评审
- **上线** = 部署到生产环境
- **回滚** = 撤销部署
- **需求变更** = 产品经理改需求

#### 5.3.3 情感递进

```
轻松(咖啡休息) → 紧张(老板巡逻) → 释放(周五下午)
无聊(站会) → 烦躁(需求变更) → 成就(代码提交)
```

---

## 6. 开发路线图

### Phase 1: 核心原型 (Week 1-2)

**目标**: 可玩的最小化产品

- [x] 项目初始化 (Vue 3 + TypeScript + Vite)
- [ ] 游戏循环引擎实现
- [ ] 核心属性系统 (Chill, Progress, Suspicion, Energy)
- [ ] 3-5个基础行动 (工作、摸鱼、休息)
- [ ] 简单文本UI界面

**验收标准**:
- 可以选择行动并看到结果
- 数值正确更新
- 游戏可以正常运行

---

### Phase 2: 核心玩法 (Week 3-4)

**目标**: 完整游戏体验

- [ ] 技能系统实现 (6-8个技能)
- [ ] 老板巡逻AI
- [ ] 随机事件系统 (20+事件)
- [ ] UI/UX优化
- [ ] 存档系统
- [ ] 数值平衡调优

**验收标准**:
- 游戏有完整循环
- 风险-收益平衡合理
- 有重玩价值

---

### Phase 3: 内容扩展 (Week 5-6)

**目标**: 丰富游戏内容

- [ ] 100+条事件文本
- [ ] 成就系统 (30+成就)
- [ ] 多结局系统 (10+结局)
- [ ] 技能树完整化
- [ ] 数据统计

**验收标准**:
- 内容丰富不重复
- 有长期游玩目标

---

### Phase 4: 打磨优化 (Week 7-8)

**目标**: 商业品质

- [ ] UI/UX全面优化
- [ ] 性能优化
- [ ] 移动端适配
- [ ] Playtesting & 反馈迭代
- [ ] Bug修复
- [ ] 发布准备

**验收标准**:
- 无重大Bug
- 流畅运行
- 用户体验优秀

---

### 里程碑时间表

```
Week 1-2  │████████████████│ Phase 1: 核心原型
Week 3-4  │████████████████│ Phase 2: 核心玩法
Week 5-6  │████████████████│ Phase 3: 内容扩展
Week 7-8  │████████████████│ Phase 4: 打磨优化
└──────── 🚀 Release v1.0
```

---

## 附录

### A. 术语表

| 术语 | 说明 |
|------|------|
| **Chill** | 摸鱼值,代表摸鱼的愉悦程度 |
| **Suspicion** | 被怀疑度,过高会被开除 |
| **Flow Channel** | 心流通道,挑战与技能的最佳平衡区 |
| **MDA** | Mechanics-Dynamics-Aesthetics 框架 |
| **Roguelike** | 包含随机生成、永久死亡等元素的游戏类型 |

### B. 参考游戏

- **《Progress Quest》** - 反传统RPG的自动化游戏
- **《Papers, Please》** - 压力管理 + 道德选择
- **《I Was a Teenage Exocolonist》** - 生活模拟 + 卡牌战斗

### C. 设计原则

1. **KISS** - 保持简单,避免过度设计
2. **DRY** - 避免重复代码和逻辑
3. **YAGNI** - 只实现当前需要的功能
4. **玩家至上** - 一切以玩家体验为先
5. **数据驱动** - 通过Playtesting验证设计

### D. 安装依赖命令

```bash
# 安装所有核心依赖
pnpm add pinia @vueuse/core seedrandom zod consola

# 安装开发依赖
pnpm add -D unocss vite-plugin-vue-devtools

# 安装类型定义
pnpm add -D @types/node @types/seedrandom
```

### E. 文件大小预估

```
核心框架:
├── Vue 3:          ~50KB (gzipped)
├── Pinia:          ~3KB (gzipped)
├── VueUse:         ~10KB (gzipped)
├── 其他工具库:     ~20KB (gzipped)
├── UnoCSS:         ~5KB (gzipped)
└── 游戏代码:       ~30KB (gzipped)

总计: ~120KB (gzipped)
初次加载时间: < 1秒 (4G网络)
```

---

**文档维护**

本文档应随开发进度持续更新。所有重大设计变更都应记录在此文档中。

**最后更新**: 2025-02-10
**作者**: 老王 (Laowang)
**状态**: ✅ 设计完成,等待实现
