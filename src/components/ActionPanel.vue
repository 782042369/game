<script setup lang="ts">
import { computed } from 'vue'

import type { ActionType } from '../game/types/actions'

import { ACTIONS } from '../game/data/actions'
import { useGameStore } from '../stores/game'
import { usePlayerStore } from '../stores/player'

const emit = defineEmits<{
  (e: 'action', action: ActionType): void
}>()

const playerStore = usePlayerStore()
const gameStore = useGameStore()
const player = computed(() => playerStore.playerState)
const gameState = computed(() => gameStore.gameState)

const actions = computed(() => ACTIONS)

function isDisabled(action: ActionType) {
  if (gameState.value.isGameOver || gameState.value.isInEvent)
    return true
  if (action.cost.energy && action.cost.energy > 0 && player.value.energy < action.cost.energy)
    return true
  return false
}

function handleAction(action: ActionType) {
  if (isDisabled(action))
    return
  emit('action', action)
}
</script>

<template>
  <div class="mc-panel flex flex-col min-h-0">
    <div class="mb-4 flex items-center gap-2 border-b-2 border-mc-border inline-block self-start pb-1">
      <span class="text-xl">🛠️</span>
      <div class="text-mc-text font-pixel font-bold text-lg">
        快捷指令
      </div>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-3 gap-4 overflow-y-auto pr-2 flex-1 custom-scrollbar">
      <button
        v-for="action in actions"
        :key="action.id"
        :disabled="isDisabled(action)"
        class="mc-btn flex flex-col items-center justify-center min-h-32 text-center gap-2 group relative overflow-hidden"
        :class="[
          { 'opacity-40 grayscale pointer-events-none': isDisabled(action) },
        ]" @click="handleAction(action)"
      >
        <!-- 装饰性角标 -->
        <div class="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-white/20 group-hover:border-white/50" />

        <span class="text-4xl group-hover:scale-110 transition-transform duration-200">{{ action.icon }}</span>
        <div class="flex flex-col gap-1">
          <span class="font-pixel text-sm leading-tight font-bold">{{ action.name }}</span>
          <span class="font-body text-xs text-mc-text/60 leading-tight px-1">{{ action.description }}</span>
        </div>

        <div class="mt-auto pt-2 w-full flex justify-center gap-2">
          <span v-if="action.cost.energy" class="text-[10px] px-2 py-0.5 bg-black/10 rounded-none font-bold border border-black/10">
            {{ action.cost.energy > 0 ? '-' : '+' }}{{ Math.abs(action.cost.energy) }}能量
          </span>
        </div>
      </button>
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
