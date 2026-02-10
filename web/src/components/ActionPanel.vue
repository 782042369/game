<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'

import { useGameStore } from '../stores/game'
import { usePlayerStore } from '../stores/player'

const emit = defineEmits<{
  (e: 'choice', choiceId: string): void
}>()

const playerStore = usePlayerStore()
const gameStore = useGameStore()

const player = computed(() => playerStore.playerState)
const gameState = computed(() => gameStore.gameState)

// 从 Store 获取 AI 生成的选项
const choices = computed(() => playerStore.currentChoices)
const storyContext = computed(() => playerStore.storyContext)
const isLoading = computed(() => playerStore.isLoading)
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

function isDisabled(choice: any) {
  if (gameState.value.isGameOver || gameState.value.isInEvent)
    return true
  if (choice.effects?.energy && choice.effects.energy > 0 && player.value.energy < choice.effects.energy)
    return true
  return false
}

async function handleChoice(choice: any) {
  if (isDisabled(choice))
    return

  try {
    // 提交选择到后端
    await playerStore.submitChoice(choice.id)

    // 通知父组件
    emit('choice', choice.id)

    // 获取下一轮选项
    await fetchNextChoices()
  }
  catch (err) {
    console.error('提交选择失败:', err)
  }
}

async function fetchNextChoices() {
  try {
    await playerStore.fetchChoices()
  }
  catch (err) {
    console.error('获取选项失败:', err)
  }
}

// 组件挂载时获取选项
onMounted(async () => {
  // 如果已经有会话 ID，则获取选项
  if (playerStore.sessionId) {
    await fetchNextChoices()
  }
})

// 监听会话 ID 变化，自动获取选项
watch(() => playerStore.sessionId, async (newSessionId) => {
  if (newSessionId) {
    await fetchNextChoices()
  }
})
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
          AI 正在思考中...
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
        <button
          class="mc-btn text-xs px-3 py-1"
          @click="fetchNextChoices"
        >
          重试
        </button>
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

        <!-- 属性影响 -->
        <div class="mt-auto pt-2 w-full flex flex-wrap gap-1">
          <span
            v-if="choice.effects?.energy"
            class="text-[10px] px-2 py-0.5 rounded-none font-bold border"
            :class="choice.effects.energy > 0 ? 'bg-green-900/30 border-green-700 text-green-300' : 'bg-red-900/30 border-red-700 text-red-300'"
          >
            {{ choice.effects.energy > 0 ? '+' : '' }}{{ choice.effects.energy }}能量
          </span>
          <span
            v-if="choice.effects?.chill"
            class="text-[10px] px-2 py-0.5 bg-cyan-900/30 border border-cyan-700 text-cyan-300 rounded-none font-bold"
          >
            {{ choice.effects.chill > 0 ? '+' : '' }}{{ choice.effects.chill }}摸鱼
          </span>
          <span
            v-if="choice.effects?.progress"
            class="text-[10px] px-2 py-0.5 bg-mc-exp/80 border border-green-700 text-green-900 rounded-none font-bold"
          >
            {{ choice.effects.progress > 0 ? '+' : '' }}{{ choice.effects.progress }}进度
          </span>
          <span
            v-if="choice.effects?.suspicion"
            class="text-[10px] px-2 py-0.5 bg-red-900/30 border border-red-700 text-red-300 rounded-none font-bold"
          >
            {{ choice.effects.suspicion > 0 ? '+' : '' }}{{ choice.effects.suspicion }}怀疑
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
        <p>等待 AI 生成选项...</p>
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
