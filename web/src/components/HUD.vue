<script setup lang="ts">
import { computed } from 'vue'

import { PlayerLevel } from '../game/types/player'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()

const player = computed(() => playerStore.playerState)

const levelName = computed(() => {
  switch (player.value.level) {
    case PlayerLevel.INTERN: return '实习生'
    case PlayerLevel.JUNIOR: return '初级民工'
    case PlayerLevel.SENIOR: return '资深裁缝'
    case PlayerLevel.LEAD: return '领头羊'
    case PlayerLevel.CTO: return '首席背锅'
    default: return '外包'
  }
})

const stats = computed(() => [
  {
    key: 'chill',
    label: '摸鱼快乐',
    icon: '🍃',
    value: player.value.chill,
    percentage: player.value.chill,
    unit: '',
    barClass: 'bg-cyan-500 border-r-4 border-cyan-700',
  },
  {
    key: 'progress',
    label: '项目进度',
    icon: '🏗️',
    value: player.value.progress,
    percentage: player.value.progress,
    unit: '%',
    barClass: 'bg-mc-exp border-r-4 border-green-700',
  },
  {
    key: 'suspicion',
    label: '失业风险',
    icon: '🔥',
    value: player.value.suspicion,
    percentage: player.value.suspicion,
    unit: '%',
    barClass: 'bg-red-500 border-r-4 border-red-700',
  },
  {
    key: 'energy',
    label: '剩余体力',
    icon: '⚡',
    value: player.value.energy,
    percentage: player.value.energy,
    unit: '',
    barClass: 'bg-yellow-500 border-r-4 border-yellow-700',
  },
])
</script>

<template>
  <div class="mc-panel space-y-5">
    <!-- 标题栏：增加了图标 -->
    <div class="flex justify-between items-center border-b-4 border-mc-border pb-2">
      <div class="flex items-center gap-2">
        <span class="text-xl">📊</span>
        <div class="text-mc-text font-pixel font-bold text-lg tracking-tight">
          个人数据
        </div>
      </div>
      <div class="text-sm text-mc-border font-pixel font-bold">
        D:{{ player.day }}
      </div>
    </div>

    <div class="space-y-5">
      <div
        v-for="stat in stats"
        :key="stat.key"
        class="stat-container group"
      >
        <div class="flex justify-between items-center mb-1.5 px-1">
          <div class="flex items-center gap-2">
            <span class="text-base">{{ stat.icon }}</span>
            <span class="text-mc-text font-pixel text-xs font-bold uppercase tracking-wider">{{ stat.label }}</span>
          </div>
          <span class="text-mc-text font-pixel text-xs font-bold">{{ stat.value.toFixed(0) }}{{ stat.unit }}</span>
        </div>
        <div class="mc-bar-bg group-hover:scale-[1.01] transition-transform duration-200">
          <div
            class="h-full transition-all duration-500 ease-out relative"
            :class="stat.barClass"
            :style="{ width: `${Math.min(100, Math.max(0, stat.percentage))}%` }"
          >
            <!-- 顶部高光 -->
            <div class="absolute top-0 left-0 w-full h-[25%] bg-white/30" />
            <!-- 底部阴影 -->
            <div class="absolute bottom-0 left-0 w-full h-[15%] bg-black/10" />
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：职业与薪资 -->
    <div class="mt-6 pt-4 border-t-4 border-mc-light bg-black/5 p-2 flex flex-col gap-2">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-5 h-5 bg-mc-exp border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,0.3)]" />
          <span class="text-mc-text font-pixel text-xs font-bold uppercase">{{ levelName }}</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="text-yellow-600 text-sm">💰</span>
          <span class="text-green-800 font-pixel text-base font-bold">$ {{ player.salary }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
