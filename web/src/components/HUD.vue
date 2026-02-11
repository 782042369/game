<script setup lang="ts">
import { computed } from 'vue'

import { PlayerLevel } from '../game/types/player'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()

const player = computed(() => playerStore.playerState)

// 职位等级配置
const LEVEL_CONFIG = [
  { level: PlayerLevel.INTERN, name: '实习生', progress: 0 },
  { level: PlayerLevel.JUNIOR, name: '初级开发', progress: 25 },
  { level: PlayerLevel.SENIOR, name: '资深开发', progress: 50 },
  { level: PlayerLevel.LEAD, name: '技术主管', progress: 75 },
  { level: PlayerLevel.CTO, name: 'CTO', progress: 100 },
]

const levelInfo = computed(() => {
  const currentLevel = player.value.level
  const current = LEVEL_CONFIG.find(l => l.level === currentLevel) || LEVEL_CONFIG[0]
  const next = LEVEL_CONFIG.find(l => l.level === currentLevel + 1)
  return { current, next }
})

const levelName = computed(() => levelInfo.value.current.name)

// 职位进度百分比
const levelProgress = computed(() => {
  const { current, next } = levelInfo.value
  if (!next)
    return 100 // 已到达最高等级
  // 简单计算：当前等级进度 = (声望 / 100) * 等级区间
  const baseProgress = current.progress
  const progressInLevel = (player.value.reputation / 100) * 25
  return Math.min(100, baseProgress + progressInLevel)
})

// 根据属性值计算显示的描述（隐藏具体数值）
function getStatusDescription(value: number, type: 'chill' | 'progress' | 'suspicion' | 'energy'): string {
  if (type === 'energy') {
    if (value >= 80)
      return '精力充沛'
    if (value >= 50)
      return '状态良好'
    if (value >= 20)
      return '有些疲惫'
    return '精疲力竭'
  }
  if (type === 'chill') {
    if (value >= 80)
      return '心情愉悦'
    if (value >= 50)
      return '心态平和'
    if (value >= 20)
      return '略显焦虑'
    return '压力山大'
  }
  if (type === 'progress') {
    if (value >= 80)
      return '进展顺利'
    if (value >= 50)
      return '稳步推进'
    if (value >= 20)
      return '进度缓慢'
    return '停滞不前'
  }
  if (type === 'suspicion') {
    if (value >= 80)
      return '岌岌可危'
    if (value >= 50)
      return '有些危险'
    if (value >= 20)
      return '还算安全'
    return '毫无察觉'
  }
  return ''
}

// 获取状态图标
function getStatusIcon(value: number, type: 'chill' | 'progress' | 'suspicion' | 'energy'): string {
  if (type === 'energy') {
    if (value >= 80)
      return '⚡'
    if (value >= 50)
      return '🔋'
    if (value >= 20)
      return '🪫'
    return '💀'
  }
  if (type === 'chill') {
    if (value >= 80)
      return '😄'
    if (value >= 50)
      return '🙂'
    if (value >= 20)
      return '😐'
    return '😫'
  }
  if (type === 'progress') {
    if (value >= 80)
      return '🚀'
    if (value >= 50)
      return '📈'
    if (value >= 20)
      return '📊'
    return '📉'
  }
  if (type === 'suspicion') {
    if (value >= 80)
      return '🔴'
    if (value >= 50)
      return '🟡'
    if (value >= 20)
      return '🟢'
    return '🔵'
  }
  return ''
}

const stats = computed(() => [
  {
    key: 'chill',
    label: '心情状态',
    icon: '🍃',
    value: player.value.chill,
    description: getStatusDescription(player.value.chill, 'chill'),
    statusIcon: getStatusIcon(player.value.chill, 'chill'),
  },
  {
    key: 'energy',
    label: '体力状况',
    icon: '⚡',
    value: player.value.energy,
    description: getStatusDescription(player.value.energy, 'energy'),
    statusIcon: getStatusIcon(player.value.energy, 'energy'),
  },
])
</script>

<template>
  <div class="mc-panel space-y-4">
    <!-- 标题栏 -->
    <div class="flex justify-between items-center border-b-4 border-mc-border pb-2">
      <div class="flex items-center gap-2">
        <span class="text-xl">📊</span>
        <div class="text-mc-text font-pixel font-bold text-lg tracking-tight">
          个人状态
        </div>
      </div>
      <div class="text-sm text-mc-border font-pixel font-bold">
        第 {{ player.day }} 天
      </div>
    </div>

    <!-- 职位进度 -->
    <div class="p-3 bg-gradient-to-r from-mc-exp/20 to-transparent border-2 border-mc-exp/50 rounded">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-2">
          <span class="text-2xl">💼</span>
          <div>
            <div class="text-mc-text font-pixel text-sm font-bold">
              {{ levelName }}
            </div>
            <div class="text-[10px] text-mc-text/60">
              {{ levelInfo.next ? `下一级: ${levelInfo.next.name}` : '已到达顶峰' }}
            </div>
          </div>
        </div>
        <div class="text-right">
          <div class="text-mc-text font-pixel text-xs">
            {{ levelProgress.toFixed(0) }}%
          </div>
        </div>
      </div>
      <div class="h-3 bg-black/30 rounded-full overflow-hidden">
        <div
          class="h-full bg-gradient-to-r from-mc-exp to-yellow-400 transition-all duration-500"
          :style="{ width: `${levelProgress}%` }"
        />
      </div>
    </div>

    <!-- 状态描述（隐藏具体数值） -->
    <div class="space-y-2">
      <div
        v-for="stat in stats"
        :key="stat.key"
        class="stat-container p-2 bg-black/5 border border-mc-border/20"
      >
        <div class="flex items-center gap-2">
          <span class="text-xl">{{ stat.statusIcon }}</span>
          <div class="flex-1">
            <div class="flex items-center justify-between">
              <span class="text-mc-border font-pixel text-[10px] font-bold uppercase">{{ stat.label }}</span>
              <span class="text-mc-text font-body text-xs">{{ stat.description }}</span>
            </div>
            <div class="h-1.5 bg-black/20 rounded-full overflow-hidden mt-1">
              <div
                class="h-full transition-all duration-500 ease-out"
                :class="{
                  'bg-cyan-500': stat.key === 'chill',
                  'bg-yellow-400': stat.key === 'progress',
                  'bg-red-500': stat.key === 'suspicion',
                  'bg-yellow-500': stat.key === 'energy',
                }"
                :style="{ width: `${Math.min(100, Math.max(0, stat.value))}%` }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：薪资 -->
    <div class="pt-2 border-t-2 border-mc-light/30 flex justify-between items-center">
      <span class="text-mc-text/60 font-pixel text-[10px]">月薪</span>
      <span class="text-mc-text font-pixel text-sm font-bold">${{ player.salary.toLocaleString() }}</span>
    </div>
  </div>
</template>
