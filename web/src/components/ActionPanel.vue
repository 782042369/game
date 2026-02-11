<script setup lang="ts">
import { computed } from 'vue'

import type { ApiChoice } from '../api/game'

import { usePlayerStore } from '../stores/player'

const emit = defineEmits<{
  (e: 'choice', choiceId: string): void
}>()

const playerStore = usePlayerStore()

const player = computed(() => playerStore.playerState)
const isGameOver = computed(() => playerStore.isGameOver)
const isLoading = computed(() => playerStore.isLoading)

// 从 Store 获取 AI 生成的选项
const choices = computed(() => playerStore.currentChoices)
const storyContext = computed(() => playerStore.storyContext)
const error = computed(() => playerStore.error)

// 选项图标映射（根据 category）
const categoryIcons: Record<string, string> = {
  work: '💼',
  slack: '🍃',
  social: '🍺',
  skill: '📚',
  growth: '🚀',
}

function getIconForCategory(category: string): string {
  return categoryIcons[category] || '🎯'
}

function isDisabled(choice: ApiChoice): boolean {
  if (isGameOver.value || isLoading.value)
    return true
  // 检查精力是否足够
  if (choice.effects?.energy && choice.effects.energy < 0 && player.value.energy < Math.abs(choice.effects.energy))
    return true
  return false
}

function handleChoice(choice: ApiChoice) {
  if (isDisabled(choice))
    return

  // 只发送事件，由父组件处理
  emit('choice', choice.id)
}
</script>

<template>
  <div class="mc-panel flex flex-col min-h-0">
    <!-- 标题栏 -->
    <div class="mb-4 flex items-center gap-2 border-b-2 border-mc-border inline-block self-start pb-1">
      <span class="text-xl">🛠️</span>
      <div class="text-mc-text font-pixel font-bold text-lg">
        快捷指令
      </div>
    </div>

    <!-- 剧情上下文 -->
    <div
      v-if="storyContext && !isLoading"
      class="mb-4 p-3 bg-mc-bg border-2 border-mc-border text-mc-light font-body text-sm leading-relaxed"
    >
      <div class="flex items-start gap-2">
        <span class="text-base">📖</span>
        <p class="flex-1">{{ storyContext }}</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div
      v-if="isLoading"
      class="flex-1 flex items-center justify-center"
    >
      <div class="flex flex-col items-center gap-3">
        <div class="animate-spin text-4xl">⚙️</div>
        <div class="text-mc-text font-pixel text-sm">
          {{ isGameOver ? '游戏已结束' : 'AI 正在思考中...' }}
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div
      v-else-if="error"
      class="flex-1 flex items-center justify-center"
    >
      <div class="flex flex-col items-center gap-3 p-4 bg-red-900/20 border-2 border-red-700">
        <span class="text-3xl">⚠️</span>
        <div class="text-red-300 font-body text-sm text-center">
          {{ error }}
        </div>
      </div>
    </div>

    <!-- 选项列表 -->
    <div
      v-else-if="choices.length > 0"
      class="grid grid-cols-1 lg:grid-cols-2 gap-4 overflow-y-auto pr-2 flex-1 custom-scrollbar"
    >
      <button
        v-for="choice in choices"
        :key="choice.id"
        :disabled="isDisabled(choice)"
        class="mc-btn flex flex-col items-start justify-center min-h-28 text-left gap-2 group relative overflow-hidden p-4"
        :class="[
          { 'opacity-40 grayscale pointer-events-none': isDisabled(choice) },
        ]" @click="handleChoice(choice)"
      >
        <!-- 装饰性角标 -->
        <div class="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-white/20 group-hover:border-white/50" />

        <!-- 头部：图标 + 分类 -->
        <div class="flex items-center gap-2 w-full">
          <span class="text-2xl group-hover:scale-110 transition-transform duration-200">
            {{ getIconForCategory(choice.category) }}
          </span>
          <span class="font-pixel text-xs uppercase font-bold text-mc-text/60">
            {{ choice.category }}
          </span>
        </div>

        <!-- 选项描述 -->
        <div class="font-body text-sm text-mc-text leading-relaxed px-1">
          {{ choice.text }}
        </div>

        <!-- 属性影响提示（简化显示） -->
        <div class="mt-auto pt-2 w-full flex items-center gap-2 text-[10px] text-mc-text/60 font-pixel uppercase">
          <span v-if="choice.effects?.energy" class="flex items-center gap-1">
            <span>{{ choice.effects.energy > 0 ? '⚡' : '🪫' }}</span>
            <span>{{ choice.effects.energy > 0 ? '恢复体力' : '消耗体力' }}</span>
          </span>
          <span v-if="choice.effects?.chill" class="flex items-center gap-1">
            <span>{{ choice.effects.chill > 0 ? '😊' : '😰' }}</span>
            <span>{{ choice.effects.chill > 0 ? '放松身心' : '增加压力' }}</span>
          </span>
          <span v-if="choice.effects?.progress" class="flex items-center gap-1">
            <span>📈</span>
            <span>推进工作</span>
          </span>
        </div>
      </button>
    </div>

    <!-- 无选项提示 -->
    <div
      v-else
      class="flex-1 flex items-center justify-center text-mc-text/60 font-body text-sm"
    >
      <div class="flex flex-col items-center gap-2">
        <span class="text-2xl">🤔</span>
        <p>{{ isLoading ? '加载中...' : '等待游戏开始...' }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 10px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #313131;
  border: 2px solid #555555;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #c6c6c6;
  border: 2px solid #555555;
  box-shadow:
    inset -2px -2px 0px rgba(0, 0, 0, 0.2),
    inset 2px 2px 0px rgba(255, 255, 255, 0.2);
}
</style>
