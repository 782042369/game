# Components 模块 - UI组件层

> **[根目录](../../CLAUDE.md) > [src](../) > **components****

最后更新: 2026-02-10

---

## 模块快照

**职责**: 游戏UI表现层，负责渲染游戏状态和用户交互。

**关键组件**:
- **HUD.vue**: 抬头显示，实时展示玩家属性（精力、摸鱼值、进度、怀疑度）
- **ActionPanel.vue**: 行动选择面板，分类显示可执行的行动
- **EventArea.vue**: 事件显示区域，记录游戏过程和文字反馈

**技术栈**: Vue 3 Composition API + UnoCSS

---

## 组件层次结构

```
App.vue (根组件)
├── Header (标题栏)
├── Main Content
│   ├── HUD.vue (状态显示)
│   ├── EventArea.vue (事件区域)
│   └── ActionPanel.vue (行动面板)
└── Footer (底部状态栏)
```

---

## 组件说明

### HUD.vue
显示游戏核心状态：
- 时间信息（当前回合、天数、周数）
- 四维属性条（精力、摸鱼、进度、怀疑度）
- 玩家等级和声望

### ActionPanel.vue
行动选择界面：
- 工作类行动（绝命冲刺、假装修文档）
- 摸鱼类行动（带薪发呆、刷水帖）
- 社交类行动（续命圣水）

### EventArea.vue
事件日志区域：
- 滚动显示历史事件
- 时间戳 + 事件类型 + 文字描述
- 最多保留50条记录

---

## 数据流

```
Player State (Pinia Store)
    ↓ props
Component Renders
    ↓ emit @action
Game Engine → State Update → Re-render
```

---

## 参考文档

- **组件设计规范**: @docs/FRONTEND-ARCHITECTURE.md#5-组件设计
- **UI/UX设计**: @docs/UI-UX-DESIGN.md
- **UnoCSS配置**: @uno.config.ts
