# 摸鱼大作战 - UI/UX设计方案

> **项目名称**: 摸鱼大作战 (Slack Master 2026)
> **设计版本**: v1.0
> **最后更新**: 2025-02-10
> **设计师**: 老王

---

## 目录

- [1. 设计理念](#1-设计理念)
- [2. 设计系统](#2-设计系统)
- [3. 主界面布局](#3-主界面布局)
- [4. 组件设计](#4-组件设计)
- [5. 交互设计](#5-交互设计)
- [6. 响应式设计](#6-响应式设计)
- [7. 无障碍设计](#7-无障碍设计)
- [8. 像素风格实现](#8-像素风格实现)
- [9. UnoCSS配置](#9-unocss配置)

---

## 1. 设计理念

### 1.1 核心原则

**AI-Native Terminal UI**: 结合现代AI工具的简洁界面和复古终端的美学，创造独特的程序员游戏体验。

**设计关键词**:
- ✨ **简洁至上** - 减少视觉干扰，专注于游戏内容
- 🎮 **像素复古** - 8-bit游戏美学，程序员情怀
- 💻 **终端体验** - 命令行风格的交互
- 🎯 **信息清晰** - 数值和状态一目了然
- 🎨 **朴素和谐** - 低饱和度配色，护眼舒适

### 1.2 体验目标

| 情感状态 | UI实现方式 |
|---------|-----------|
| **代入感** | 终端风格界面，程序员黑话文本 |
| **紧张感** | 老板巡逻时的红色警告动画 |
| **成就感** | 技能解锁时的绿色成功反馈 |
| **幽默感** | 夸张的像素字体和程序员梗文本 |

---

## 2. 设计系统

### 2.1 色彩系统

#### 主色调（程序员风格）

```css
/* 深色主题背景 */
.bg-terminal      { background-color: #020617; }  /* 深蓝黑，像终端 */
.bg-card         { background-color: #1E293B; }  /* 卡片背景 */
.bg-surface      { background-color: #334155; }  /* 表面层次 */

/* 文字颜色 */
.text-primary    { color: #F8FAFC; }  /* 主要文字，白色 */
.text-secondary  { color: #CBD5E1; }  /* 次要文字，浅灰 */
.text-muted      { color: #94A3B8; }  /* 提示文字，更灰 */

/* 功能色 */
.text-success     { color: #22C55E; }  /* 成功，绿色 */
.text-warning     { color: #F59E0B; }  /* 警告，橙色 */
.text-danger      { color: #EF4444; }  /* 危险，红色 */
.text-info       { color: #3B82F6; }  /* 信息，蓝色 */

/* 像素风格高亮 */
.pixel-glow      { color: #00FF00; text-shadow: 0 0 10px #00FF00; }
.pixel-cyan      { color: #00FFFF; text-shadow: 0 0 8px #00FFFF; }
.pixel-yellow    { color: #FFFF00; text-shadow: 0 0 8px #FFFF00; }
```

#### 游戏状态色彩

```typescript
// 游戏状态色彩映射
const gameStatusColors = {
  // 安全状态
  safe: {
    bg: '#065F46',      // 深绿
    text: '#34D399',    // 亮绿
    border: '#10B981'
  },
  // 警告状态
  warning: {
    bg: '#92400E',      // 深橙
    text: '#FBBF24',    // 亮橙
    border: '#F59E0B'
  },
  // 危险状态
  danger: {
    bg: '#991B1B',      // 深红
    text: '#FCA5A5',    // 亮红
    border: '#EF4444'
  },
  // 特殊状态
  boss: {
    bg: '#581C87',      // 深紫
    text: '#E879F9',    // 亮紫
    border: '#A855F7'
  }
}
```

### 2.2 字体系统

#### 主要字体

```css
/* 像素字体 - 游戏标题 */
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

/* 等宽字体 - 代码和终端风格 */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

/* 无衬线字体 - 现代可读 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* 字体层级 */
.font-pixel    { font-family: 'Press Start 2P', monospace; }      /* 像素字体 */
.font-mono     { font-family: 'JetBrains Mono', monospace; }      /* 等宽字体 */
.font-sans     { font-family: 'Inter', sans-serif; }              /* 无衬线字体 */
```

#### 字体大小和行高

```css
/* 响应式字体大小 */
.text-xs { font-size: 0.75rem; line-height: 1rem; }      /* 12px */
.text-sm { font-size: 0.875rem; line-height: 1.25rem; } /* 14px */
.text-base { font-size: 1rem; line-height: 1.5rem; }   /* 16px */
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }/* 18px */
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }/* 20px */
.text-2xl { font-size: 1.5rem; line-height: 2rem; }    /* 24px */
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }/* 30px */

/* 游戏专用尺寸 */
.text-hud { font-size: 0.75rem; line-height: 1rem; }    /* HUD小字 */
.text-pixel { font-size: 1.5rem; line-height: 1.5rem; } /* 像素大字 */
```

### 2.3 间距系统

```css
/* 基础间距 - 基于4px网格 */
.space-px    { width: 1px; height: 1px; }
.space-1     { width: 0.25rem; height: 0.25rem; }    /* 4px */
.space-2     { width: 0.5rem; height: 0.5rem; }     /* 8px */
.space-3     { width: 0.75rem; height: 0.75rem; }   /* 12px */
.space-4     { width: 1rem; height: 1rem; }         /* 16px */
.space-6     { width: 1.5rem; height: 1.5rem; }     /* 24px */
.space-8     { width: 2rem; height: 2rem; }         /* 32px */
.space-12    { width: 3rem; height: 3rem; }        /* 48px */
.space-16    { width: 4rem; height: 4rem; }        /* 64px */

/* 游戏特殊间距 */
.hud-gap    { gap: 0.25rem; }    /* HUD组件间距 */
.card-gap   { gap: 0.5rem; }     /* 卡片内容间距 */
.panel-gap  { gap: 1rem; }      /* 面板间距 */
```

---

## 3. 主界面布局

### 3.1 整体布局结构

```
┌─────────────────────────────────────────────────────┐
│  摸鱼大作战 [v1.0]    [存档] [设置] [帮助]       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────────────────┐   │
│  │    HUD      │  │                         │   │
│  │             │  │                         │   │
│  │ 状态栏      │  │                         │   │
│  │ 时间: 09:00 │  │                         │   │
│  │ Chill: 75  │  │                         │   │
│  │ Suspicion: 25│  │      事件区域           │   │
│  │ Progress: 40│  │                         │   │
│  │ Energy: 60  │  │                         │   │
│  │             │  │                         │   │
│  │ 等级: 初级  │  │                         │   │
│  │ 周期: 第1周│  │                         │   │
│  │             │  │                         │   │
│  └─────────────┘  └─────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │                 行动面板                    │   │
│  │  [认真工作]  [更新Jira]  [代码Review]      │   │
│  │  [摸鱼]      [刷Reddit]  [厕所摸鱼]        │   │
│  │  [假装工作]  [Alt+Tab]   [咖啡休息]        │   │
│  │  [帮同事]    [学习技能]  [副业项目]        │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │                 快捷键                       │   │
│  │  1-9: 快速行动  S:存档  L:加载  Q:退出      │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 3.2 HUD设计

```vue
<!-- HUD组件 -->
<template>
  <div class="hud-panel">
    <!-- 顶部状态栏 -->
    <div class="hud-header">
      <div class="hud-time">
        <span class="icon">⏰</span>
        <span>{{ gameTime }}</span>
      </div>
      <div class="hud-status">
        <div
          v-for="stat in stats"
          :key="stat.key"
          :class="['stat-item', `stat-${stat.status}`]"
        >
          <span class="stat-label">{{ stat.label }}:</span>
          <span class="stat-value">{{ stat.value }}</span>
          <div class="stat-bar">
            <div
              class="stat-fill"
              :style="{ width: `${stat.percentage}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 等级信息 -->
    <div class="hud-level">
      <div class="level-info">
        <span class="level-text">{{ player.level }}</span>
        <div class="exp-bar">
          <div class="exp-fill" :style="{ width: `${expPercentage}%` }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hud-panel {
  @apply bg-terminal border-2 border-cyan-500 rounded-lg p-3 font-mono text-hud;
}

.hud-header {
  @apply flex justify-between items-start mb-3;
}

.hud-time {
  @apply flex items-center gap-1 text-cyan-400;
}

.stat-item {
  @apply mb-2 last:mb-0;
}

.stat-label {
  @apply text-muted mr-2;
}

.stat-value {
  @apply text-primary font-bold mr-2;
}

.stat-bar {
  @apply w-full bg-gray-700 rounded-full h-2 overflow-hidden;
}

.stat-fill {
  @apply h-full transition-all duration-300;
}

.stat-safe .stat-fill { @apply bg-green-500; }
.stat-warning .stat-fill { @apply bg-yellow-500; }
.stat-danger .stat-fill { @apply bg-red-500; }
.stat-boss .stat-fill { @apply bg-purple-500; }
</style>
```

### 3.3 事件区域设计

```vue
<!-- 事件显示区域 -->
<template>
  <div class="event-area">
    <!-- 事件标题 -->
    <div class="event-header">
      <h2 class="event-title">事件日志</h2>
      <div class="event-timeline">{{ currentPeriod }}</div>
    </div>

    <!-- 事件内容 -->
    <div class="event-content">
      <!-- 当前事件 -->
      <div v-if="currentEvent" class="current-event">
        <div class="event-text">{{ currentEvent.description }}</div>
        <div v-if="currentEvent.choices" class="event-choices">
          <button
            v-for="choice in currentEvent.choices"
            :key="choice.id"
            @click="selectChoice(choice)"
            class="choice-btn"
          >
            {{ choice.text }}
          </button>
        </div>
      </div>

      <!-- 历史事件 -->
      <div v-else class="event-history">
        <div
          v-for="event in recentEvents"
          :key="event.id"
          class="history-item"
          :class="event.type"
        >
          <span class="time">{{ event.time }}</span>
          <span class="text">{{ event.text }}</span>
        </div>
      </div>
    </div>

    <!-- 滚动到底部 -->
    <div ref="eventScroll" class="event-scroll"></div>
  </div>
</template>

<style scoped>
.event-area {
  @apply bg-card border border-gray-600 rounded-lg p-4 flex flex-col h-full;
}

.event-header {
  @apply flex justify-between items-center mb-4;
}

.event-title {
  @apply text-xl font-bold text-primary font-pixel;
}

.event-timeline {
  @apply text-sm text-muted font-mono;
}

.event-text {
  @apply text-base text-secondary leading-relaxed mb-4;
  line-height: 1.6;
}

.choice-btn {
  @apply w-full text-left px-3 py-2 bg-terminal border border-cyan-500 text-cyan-400
         hover:bg-cyan-500 hover:text-black transition-colors duration-200
         rounded cursor-pointer;
}

.history-item {
  @apply mb-2 last:mb-0;
}

.history-item .time {
  @apply text-xs text-muted mr-2;
}

.history-item.work .text { @apply text-blue-400; }
.history-item.slack .text { @apply text-green-400; }
.history-item.boss .text { @apply text-red-400; }
.history-item.social .text { @apply text-yellow-400; }
</style>
```

---

## 4. 组件设计

### 4.1 行动按钮组件

```vue
<!-- 行动按钮 -->
<template>
  <button
    @click="handleClick"
    :disabled="disabled"
    :class="[
      'action-btn',
      actionType,
      { 'disabled': disabled },
      { 'selected': selected }
    ]"
  >
    <!-- 按钮图标 -->
    <div class="btn-icon">
      <span v-if="icon" class="icon">{{ icon }}</span>
    </div>

    <!-- 按钮文字 -->
    <div class="btn-text">
      <span class="title">{{ title }}</span>
      <span v-if="description" class="description">{{ description }}</span>
    </div>

    <!-- 快捷键 -->
    <div v-if="hotkey" class="btn-hotkey">
      {{ hotkey }}
    </div>

    <!-- 需求标识 -->
    <div v-if="required" class="btn-required">
      需要 {{ required }}
    </div>
  </button>
</template>

<style scoped>
.action-btn {
  @apply relative px-4 py-3 bg-terminal border-2 border-gray-600
         rounded-lg text-left transition-all duration-200
         hover:border-cyan-400 hover:shadow-lg
         focus:outline-none focus:ring-2 focus:ring-cyan-400;

  /* 按钮状态 */
  &.work {
    @apply border-blue-500 hover:border-blue-400;
    .btn-icon { @apply text-blue-400; }
  }

  &.slack {
    @apply border-green-500 hover:border-green-400;
    .btn-icon { @apply text-green-400; }
  }

  &.boss {
    @apply border-red-500 hover:border-red-400;
    .btn-icon { @apply text-red-400; }
  }

  &.skill {
    @apply border-purple-500 hover:border-purple-400;
    .btn-icon { @apply text-purple-400; }
  }

  /* 禁用状态 */
  &.disabled {
    @apply opacity-50 cursor-not-allowed;
    &:hover { @apply border-gray-600; }
  }

  /* 选中状态 */
  &.selected {
    @apply border-cyan-400 bg-cyan-500 text-black;
  }
}

.btn-icon {
  @apply text-xl mr-3;
}

.btn-text {
  @apply flex-1;
}

.title {
  @apply block text-base font-bold text-primary;
}

.description {
  @apply block text-xs text-muted mt-1;
}

.btn-hotkey {
  @apply absolute top-1 right-1 text-xs text-muted bg-black/50 px-1 rounded;
}

.btn-required {
  @apply absolute bottom-1 right-1 text-xs text-yellow-400;
}
</style>
```

### 4.2 技能卡片组件

```vue
<!-- 技能卡片 -->
<template>
  <div class="skill-card" :class="{ 'locked': !unlocked, 'selected': selected }">
    <!-- 技能图标 -->
    <div class="skill-icon">
      <span>{{ icon }}</span>
      <div v-if="unlocked" class="skill-level">
        Lv.{{ level }}
      </div>
    </div>

    <!-- 技能信息 -->
    <div class="skill-info">
      <h3 class="skill-name">{{ name }}</h3>
      <p class="skill-desc">{{ description }}</p>

      <!-- 技能效果 -->
      <div class="skill-effects">
        <div v-for="effect in effects" :key="effect" class="skill-effect">
          {{ effect }}
        </div>
      </div>

      <!-- 技能需求 -->
      <div v-if="requirements" class="skill-requirements">
        需要: {{ requirements }}
      </div>
    </div>

    <!-- 解锁按钮 -->
    <button
      v-if="!unlocked && canUnlock"
      @click="unlock"
      class="unlock-btn"
    >
      解锁 ({{ cost }})
    </button>
  </div>
</template>

<style scoped>
.skill-card {
  @apply bg-card border-2 border-gray-600 rounded-lg p-4
         transition-all duration-200 hover:border-cyan-400;

  &.locked {
    @apply opacity-60;
    .skill-icon { @apply grayscale; }
  }

  &.selected {
    @apply border-cyan-400 bg-cyan-500/10;
  }
}

.skill-icon {
  @apply text-3xl mb-3 text-center relative;
}

.skill-level {
  @apply absolute -top-2 -right-2 bg-cyan-500 text-black text-xs
         px-1 rounded-full font-bold;
}

.skill-name {
  @apply text-lg font-bold text-primary mb-1;
}

.skill-desc {
  @apply text-sm text-secondary mb-3;
}

.skill-effects {
  @apply space-y-1 mb-3;
}

.skill-effect {
  @apply text-xs text-muted;
}

.skill-requirements {
  @apply text-xs text-yellow-400 italic;
}

.unlock-btn {
  @apply w-full mt-2 px-3 py-1 bg-cyan-500 text-black
         hover:bg-cyan-400 transition-colors duration-200
         rounded text-sm font-bold cursor-pointer;
}
</style>
```

### 4.3 存档管理组件

```vue
<!-- 存档管理 -->
<template>
  <div class="save-manager">
    <div class="save-header">
      <h3 class="save-title">游戏存档</h3>
      <div class="save-actions">
        <button @click="autoSave" class="action-btn auto-btn">
          自动存档
        </button>
        <button @click="exportSave" class="action-btn export-btn">
          导出存档
        </button>
      </div>
    </div>

    <!-- 存档列表 -->
    <div class="save-slots">
      <div
        v-for="slot in saveSlots"
        :key="slot.id"
        class="save-slot"
        :class="{ 'has-data': slot.hasData }"
      >
        <div class="slot-info">
          <div class="slot-name">
            {{ slot.name }}
            <span v-if="slot.hasData" class="slot-date">
              {{ formatDate(slot.date) }}
            </span>
          </div>
          <div v-if="slot.summary" class="slot-summary">
            {{ slot.summary }}
          </div>
        </div>

        <div class="slot-actions">
          <button
            v-if="slot.hasData"
            @click="load(slot.id)"
            class="slot-btn load-btn"
          >
            加载
          </button>
          <button
            @click="save(slot.id)"
            class="slot-btn save-btn"
          >
            {{ slot.hasData ? '覆盖' : '保存' }}
          </button>
          <button
            v-if="slot.hasData"
            @click="deleteSave(slot.id)"
            class="slot-btn delete-btn"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.save-manager {
  @apply bg-card border border-gray-600 rounded-lg p-4;
}

.save-header {
  @apply flex justify-between items-center mb-4;
}

.save-title {
  @apply text-xl font-bold text-primary;
}

.save-actions {
  @apply gap-2;
}

.action-btn {
  @apply px-3 py-1 bg-terminal border border-cyan-500 text-cyan-400
         hover:bg-cyan-500 hover:text-black transition-colors
         rounded text-sm cursor-pointer;
}

.save-slots {
  @apply space-y-3;
}

.save-slot {
  @apply bg-terminal/50 border border-gray-600 rounded-lg p-3
         flex justify-between items-center;

  &.has-data {
    @apply border-cyan-500/50;
  }
}

.slot-info {
  @apply flex-1;
}

.slot-name {
  @apply font-bold text-primary mb-1;
}

.slot-date {
  @apply text-xs text-muted ml-2;
}

.slot-summary {
  @apply text-xs text-muted;
}

.slot-actions {
  @apply gap-1 ml-4;
}

.slot-btn {
  @apply px-2 py-1 text-xs bg-terminal border border-gray-600
         hover:bg-gray-600 transition-colors rounded cursor-pointer;

  &.load-btn {
    @apply border-green-500 hover:bg-green-500 text-green-400;
  }

  &.save-btn {
    @apply border-blue-500 hover:bg-blue-500 text-blue-400;
  }

  &.delete-btn {
    @apply border-red-500 hover:bg-red-500 text-red-400;
  }
}
</style>
```

---

## 5. 交互设计

### 5.1 视觉反馈

#### 动画效果

```css
/* 像素风格动画 */
@keyframes pixel-blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes pixel-glow {
  0% {
    text-shadow: 0 0 5px currentColor;
    box-shadow: 0 0 5px currentColor;
  }
  50% {
    text-shadow: 0 0 20px currentColor, 0 0 30px currentColor;
    box-shadow: 0 0 20px currentColor, 0 0 30px currentColor;
  }
  100% {
    text-shadow: 0 0 5px currentColor;
    box-shadow: 0 0 5px currentColor;
  }
}

@keyframes scanlines {
  0% { transform: translateY(0); }
  100% { transform: translateY(100%); }
}

/* 应用动画 */
.cursor-blink {
  animation: pixel-blink 1s infinite;
}

.glow-effect {
  animation: pixel-glow 2s infinite;
}

.scanlines-overlay {
  position: relative;
  overflow: hidden;
}

.scanlines-overlay::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 255, 0, 0.03) 2px,
    rgba(0, 255, 0, 0.03) 4px
  );
  animation: scanlines 8s linear infinite;
  pointer-events: none;
}
```

#### 状态变化反馈

```typescript
// 数值变化动画
const statChangeAnimation = {
  enter: {
    scale: [1, 1.2, 1],
    opacity: [0, 1, 1],
    duration: 300,
    easing: 'ease-out'
  },
  exit: {
    scale: [1, 0.8],
    opacity: [1, 0],
    duration: 200,
    easing: 'ease-in'
  }
}

// 警告动画
const warningAnimation = {
  keyframes: [
    { transform: 'translateX(0)', filter: 'hue-rotate(0deg)' },
    { transform: 'translateX(2px)', filter: 'hue-rotate(20deg)' },
    { transform: 'translateX(-2px)', filter: 'hue-rotate(-20deg)' },
    { transform: 'translateX(0)', filter: 'hue-rotate(0deg)' }
  ],
  duration: 500,
  iterations: 3
}
```

### 5.2 键盘快捷键

```typescript
// 快捷键映射
const shortcuts = {
  // 数字键 - 行动
  '1': 'work_hard',
  '2': 'jira_update',
  '3': 'code_review',
  '4': 'slack_off',
  '5': 'browse_reddit',
  '6': 'toilet_slack',
  '7': 'pretend_work',
  '8': 'alt_tab_master',
  '9': 'coffee_break',

  // 功能键
  's': 'save_game',
  'l': 'load_game',
  'q': 'quit_game',
  'tab': 'cycle_skills',
  'esc': 'close_modal'
}
```

### 5.3 触摸优化

```css
/* 移动端触摸优化 */
@media (hover: none) {
  .action-btn {
    @apply py-4; /* 增加触摸区域 */
  }

  .touch-target {
    min-height: 44px;
    min-width: 44px;
  }

  /* 触摸反馈 */
  .action-btn:active {
    @apply scale-95 bg-black/50;
  }
}

/* 防止误触 */
.btn-guard {
  @apply select-none;
  -webkit-tap-highlight-color: transparent;
}
```

---

## 6. 响应式设计

### 6.1 断点定义

```css
/* 响应式断点 */
@media (max-width: 640px) {
  /* 手机端 - 垂直布局 */
  .game-container {
    @apply flex-col;
  }

  .hud-panel {
    @apply w-full;
  }

  .event-area {
    @apply order-2;
  }

  .action-panel {
    @apply grid-cols-2 gap-2;
  }
}

@media (min-width: 641px) and (max-width: 1024px) {
  /* 平板端 - 水平布局 */
  .game-container {
    @apply grid-cols-1 lg:grid-cols-3;
  }

  .action-panel {
    @apply grid-cols-3;
  }
}

@media (min-width: 1025px) {
  /* 桌面端 - 完整布局 */
  .game-container {
    @apply grid-cols-4;
  }

  .action-panel {
    @apply grid-cols-4;
  }
}
```

### 6.2 自适应字体

```typescript
// 响应式字体大小
const responsiveFontSizes = {
  xs: { mobile: '0.625rem', tablet: '0.75rem', desktop: '0.875rem' },
  sm: { mobile: '0.75rem', tablet: '0.875rem', desktop: '1rem' },
  base: { mobile: '0.875rem', tablet: '1rem', desktop: '1.125rem' },
  lg: { mobile: '1rem', tablet: '1.125rem', desktop: '1.25rem' },
  xl: { mobile: '1.25rem', tablet: '1.5rem', desktop: '1.875rem' }
}
```

---

## 7. 无障碍设计

### 7.1 屏幕阅读器支持

```vue
<!-- 无障碍属性示例 -->
<template>
  <button
    :aria-label="`${action.title} - ${action.description}`"
    :aria-description="action.effects"
    :aria-pressed="selected"
    @click="handleAction"
    class="action-btn"
  >
    <span class="visually-hidden">{{ action.title }}</span>
    {{ action.title }}
  </button>
</template>

<style scoped>
/* 隐藏但屏幕阅读器可读 */
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 焦点样式 */
.action-btn:focus {
  outline: 2px solid #00FFFF;
  outline-offset: 2px;
}
</style>
```

### 7.2 键盘导航

```typescript
// 键盘导航逻辑
const keyboardNavigation = {
  nextElement: (current: HTMLElement) => {
    const allFocusable = document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const currentIndex = Array.from(allFocusable).indexOf(current)
    return allFocusable[currentIndex + 1] || allFocusable[0]
  },

  prevElement: (current: HTMLElement) => {
    const allFocusable = document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const currentIndex = Array.from(allFocusable).indexOf(current)
    return allFocusable[currentIndex - 1] || allFocusable[allFocusable.length - 1]
  }
}
```

---

## 8. 像素风格实现

### 8.1 像素字体渲染

```css
/* 像素字体优化 */
.font-pixel {
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
  -webkit-font-smoothing: none;
  -moz-osx-font-smoothing: grayscale;
  font-weight: normal;
  text-rendering: optimizeSpeed;
}

/* 像素边框效果 */
.pixel-border {
  position: relative;
  background: #1E293B;
  border: none;
}

.pixel-border::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #00FFFF, #00FF00, #FFFF00, #00FFFF);
  background-size: 400% 400%;
  border-radius: 4px;
  z-index: -1;
  animation: pixel-border-gradient 3s linear infinite;
}

@keyframes pixel-border-gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
```

### 8.2 像素图标设计

```vue
<!-- 像素图标组件 -->
<template>
  <div class="pixel-icon" :class="iconClass">
    <svg viewBox="0 0 24 24" class="icon-svg">
      <!-- 图标路径 -->
      <path :d="iconPath" fill="currentColor" />
    </svg>
  </div>
</template>

<style scoped>
.pixel-icon {
  @apply w-6 h-6;
  image-rendering: pixelated;
}

.icon-svg {
  @apply w-full h-full;
  filter: drop-shadow(0 0 2px currentColor);
}
</style>
```

---

## 9. UnoCSS配置

### 9.1 UnoCSS配置文件

```typescript
// uno.config.ts
import {
  defineConfig,
  presetAttributify,
  presetWind4,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

export default defineConfig({
  presets: [
    presetWind4(),
    presetAttributify(),
  ],
  transformers: [transformerDirectives(), transformerVariantGroup()],

  // 自定义主题
  theme: {
    colors: {
      // 游戏主题色彩
      terminal: '#020617',
      card: '#1E293B',
      surface: '#334155',

      // 游戏状态色
      safe: '#22C55E',
      warning: '#F59E0B',
      danger: '#EF4444',
      boss: '#8B5CF6',

      // 像素风格色彩
      pixel: {
        green: '#00FF00',
        cyan: '#00FFFF',
        yellow: '#FFFF00',
        red: '#FF0000',
        purple: '#FF00FF'
      }
    },

    // 字体家族
    fontFamily: {
      pixel: ['Press Start 2P', 'cursive'],
      mono: ['JetBrains Mono', 'monospace'],
      sans: ['Inter', 'system-ui', 'sans-serif']
    },

    // 动画时长
    animation: {
      'pixel-blink': 'pixel-blink 1s infinite',
      'pixel-glow': 'pixel-glow 2s infinite',
      'scanlines': 'scanlines 8s linear infinite'
    },

    // 关键帧
    keyframes: {
      'pixel-blink': {
        '0%, 50%': { opacity: '1' },
        '51%, 100%': { opacity: '0' }
      },
      'pixel-glow': {
        '0%': {
          'text-shadow': '0 0 5px currentColor',
          'box-shadow': '0 0 5px currentColor'
        },
        '50%': {
          'text-shadow': '0 0 20px currentColor, 0 0 30px currentColor',
          'box-shadow': '0 0 20px currentColor, 0 0 30px currentColor'
        },
        '100%': {
          'text-shadow': '0 0 5px currentColor',
          'box-shadow': '0 0 5px currentColor'
        }
      },
      'scanlines': {
        '0%': { transform: 'translateY(0)' },
        '100%': { transform: 'translateY(100%)' }
      }
    }
  },

  // 短手定义
  shortcuts: {
    // 游戏组件样式
    'hud-panel': 'bg-terminal border-2 border-cyan-500 rounded-lg p-3 font-mono',
    'action-btn': 'px-4 py-3 bg-terminal border-2 border-gray-600 rounded-lg text-left transition-all duration-200 hover:border-cyan-400',
    'event-area': 'bg-card border border-gray-600 rounded-lg p-4',

    // 像素效果
    'pixel-border': 'border-2 border-gray-500',
    'pixel-glow-text': 'text-shadow: 0 0 10px currentColor',

    // 游戏状态
    'stat-safe': 'border-green-500 bg-green-500/10',
    'stat-warning': 'border-yellow-500 bg-yellow-500/10',
    'stat-danger': 'border-red-500 bg-red-500/10',
    'stat-boss': 'border-purple-500 bg-purple-500/10'
  },

  // 规则
  rules: [
    // 自定义选择器
    ['pixel-cursor', { 'cursor': 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'16\' height=\'16\'%3E%3Ctext y=\'14\' font-size=\'12\' fill=\'%2300FF00\'%3E▮%3C/text%3E%3C/svg%3E") 0 0, auto' }],

    // 游戏专用类
    ['.game-hud>*>*', { 'margin-bottom': '0.5rem' }],
    ['.action-list>*>:not(:last-child)', { 'margin-bottom': '0.25rem' }]
  ]
})
```

### 9.2 CSS变量定义

```css
/* CSS变量定义 */
:root {
  /* 游戏主题色彩 */
  --game-bg: #020617;
  --game-card: #1E293B;
  --game-surface: #334155;

  /* 文字色彩 */
  --text-primary: #F8FAFC;
  --text-secondary: #CBD5E1;
  --text-muted: #94A3B8;

  /* 功能色 */
  --color-success: #22C55E;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;
  --color-info: #3B82F6;

  /* 像素色彩 */
  --pixel-green: #00FF00;
  --pixel-cyan: #00FFFF;
  --pixel-yellow: #FFFF00;
  --pixel-red: #FF0000;
  --pixel-purple: #FF00FF;

  /* 间距系统 */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;

  /* 圆角 */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* 暗色主题 */
@media (prefers-color-scheme: dark) {
  :root {
    --game-bg: #000000;
    --game-card: #0F172A;
    --game-surface: #1E293B;
  }
}
```

---

## 总结

这个UI/UX设计方案结合了现代游戏界面设计理念和复古像素美学，为摸鱼大作战游戏创造了独特的视觉体验。通过终端风格的界面设计、像素艺术元素和清晰的布局结构，既体现了程序员文化的特色，又保证了良好的可读性和交互性。

### 设计亮点：

1. **AI-Native Terminal UI** - 结合AI工具的简洁界面和终端美学
2. **像素艺术风格** - 8-bit游戏美学，程序员情怀满满
3. **响应式设计** - 完美适配手机、平板和桌面
4. **无障碍支持** - 完整的键盘导航和屏幕阅读器支持
5. **性能优化** - 使用UnoCSS实现原子化CSS，减少体积
6. **交互反馈** - 丰富的动画效果和状态变化提示

这套设计方案既保证了游戏的功能性，又创造了独特的视觉体验，完美契合摸鱼大作战的游戏定位和目标受众。
