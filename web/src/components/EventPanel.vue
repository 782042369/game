<script setup lang="ts">
import { computed } from 'vue'
import { usePlayerStore, type MagicalElement, type TriggeredEvent } from '../stores/player'

const playerStore = usePlayerStore()

const currentMagicalElement = computed(() => playerStore.currentMagicalElement as MagicalElement | null)
const lastTriggeredEvents = computed(() => playerStore.lastTriggeredEvents as TriggeredEvent[])

// 魔幻元素类型图标映射
const magicalTypeIcons: Record<string, string> = {
  object: '📦',
  phenomenon: '🌀',
  ability: '⚡',
}

// 事件类型图标映射
const eventTypeIcons: Record<string, string> = {
  threshold: '📊',
  chain: '🔗',
  time: '⏰',
  random: '🎲',
  magical: '✨',
}

// 事件类型名称映射
const eventTypeNames: Record<string, string> = {
  threshold: '阈值',
  chain: '连锁',
  time: '时间',
  random: '随机',
  magical: '魔幻',
}
</script>

<template>
  <div class="mc-panel space-y-3">
    <!-- 标题栏 -->
    <div class="flex justify-between items-center border-b-4 border-mc-border pb-2">
      <div class="flex items-center gap-2">
        <span class="text-xl">⚡</span>
        <div class="text-mc-text font-pixel font-bold text-lg tracking-tight">
          当前事件
        </div>
      </div>
    </div>

    <!-- 当前魔幻元素 -->
    <div v-if="currentMagicalElement" class="p-3 bg-purple-500/10 border-2 border-purple-500/50 rounded">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xl">{{ magicalTypeIcons[currentMagicalElement.type] || '✨' }}</span>
        <div class="text-mc-border font-pixel text-sm font-bold">
          {{ currentMagicalElement.name }}
        </div>
      </div>
      <div class="text-[10px] text-mc-text/80 mb-1">
        {{ currentMagicalElement.description }}
      </div>
      <div class="text-[10px] text-purple-400">
        影响: {{ currentMagicalElement.effect }}
      </div>
    </div>

    <!-- 触发的事件 -->
    <div v-if="lastTriggeredEvents.length > 0" class="space-y-2">
      <div class="text-mc-border font-pixel text-[10px] font-bold uppercase">
        触发事件
      </div>
      <div
        v-for="(event, index) in lastTriggeredEvents"
        :key="index"
        class="p-2 bg-black/5 border border-mc-border/20 rounded"
      >
        <div class="flex items-start gap-2">
          <span class="text-sm">{{ eventTypeIcons[event.type] || '📌' }}</span>
          <div class="flex-1">
            <div class="text-[10px] text-mc-text">{{ event.message }}</div>
            <div class="text-[9px] text-mc-text/60 mt-1">
              {{ event.effect }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无事件提示 -->
    <div
      v-else
      class="p-4 text-center text-mc-text/40 text-[10px] border-2 border-dashed border-mc-border/20 rounded"
    >
      暂无特殊事件
    </div>
  </div>
</template>
