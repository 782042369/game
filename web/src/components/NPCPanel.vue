<script setup lang="ts">
import { computed, ref } from 'vue'
import { usePlayerStore, type NPCProfile, type NPCReaction } from '../stores/player'

const playerStore = usePlayerStore()
const npcs = computed(() => playerStore.npcs as NPCProfile[])
const selectedNPC = ref<string | null>(null)

// 角色图标映射
const roleIcons: Record<string, string> = {
  boss: '👔',
  colleague: '👨‍💻',
  hr: '📋',
  mentor: '🧙',
  rival: '⚔️',
}

// 角色名称映射
const roleNames: Record<string, string> = {
  boss: '老板',
  colleague: '同事',
  hr: 'HR',
  mentor: '导师',
  rival: '对手',
}

/**
 * 获取好感度颜色类名
 */
function getAttitudeColor(value: number): string {
  if (value >= 70)
    return 'text-green-500'
  if (value >= 40)
    return 'text-yellow-500'
  return 'text-red-500'
}

/**
 * 获取好感度文本描述
 */
function getAttitudeText(value: number): string {
  if (value >= 80)
    return '非常友好'
  if (value >= 60)
    return '好感'
  if (value >= 40)
    return '中立'
  if (value >= 20)
    return '不喜欢'
  return '讨厌'
}

/**
 * 切换NPC详情展开状态
 */
function toggleNPC(npcId: string) {
  selectedNPC.value = selectedNPC.value === npcId ? null : npcId
}
</script>

<template>
  <div class="mc-panel space-y-3">
    <!-- 标题栏 -->
    <div class="flex justify-between items-center border-b-4 border-mc-border pb-2">
      <div class="flex items-center gap-2">
        <span class="text-xl">👥</span>
        <div class="text-mc-text font-pixel font-bold text-lg tracking-tight">
          NPC列表
        </div>
      </div>
      <div class="text-[10px] text-mc-text/60 font-pixel font-bold">
        {{ npcs.length }} 人
      </div>
    </div>

    <!-- NPC列表（紧凑模式） -->
    <div v-if="npcs.length > 0" class="space-y-2 max-h-[400px] overflow-y-auto pr-1 custom-scrollbar">
      <div
        v-for="npc in npcs"
        :key="npc.id"
        class="p-2 bg-black/5 border border-mc-border/20 rounded cursor-pointer hover:bg-mc-exp/10 transition-colors"
        :class="{ 'ring-2 ring-mc-exp': selectedNPC === npc.id }"
        @click="toggleNPC(npc.id)"
      >
        <div class="flex items-center gap-2">
          <span class="text-lg">{{ roleIcons[npc.role] || '👤' }}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <span class="text-mc-border font-pixel text-[10px] font-bold truncate">
                {{ npc.name }}
              </span>
              <span class="text-[9px] text-mc-text/60">{{ roleNames[npc.role] || npc.role }}</span>
            </div>
            <div class="text-[9px] text-mc-text/60 truncate">
              {{ npc.personality }}
            </div>
          </div>
          <div class="text-right">
            <div
              class="text-[10px] font-bold"
              :class="getAttitudeColor(npc.attitude_toward_player)"
            >
              {{ npc.attitude_toward_player }}
            </div>
            <div class="text-[8px] text-mc-text/60">
              {{ getAttitudeText(npc.attitude_toward_player) }}
            </div>
          </div>
        </div>

        <!-- 展开详情 -->
        <div v-if="selectedNPC === npc.id" class="mt-2 pt-2 border-t border-mc-border/20 space-y-1">
          <!-- 背景故事 -->
          <div class="text-[9px] text-mc-text/70">
            <span class="font-bold text-mc-border">背景:</span> {{ npc.background }}
          </div>

          <!-- 外貌 -->
          <div class="text-[9px] text-mc-text/70">
            <span class="font-bold text-mc-border">外貌:</span> {{ npc.appearance }}
          </div>

          <!-- 关系 -->
          <div v-if="Object.keys(npc.relationships).length > 0" class="text-[9px] text-mc-text/70">
            <span class="font-bold text-mc-border">关系:</span>
            <div class="ml-1">
              <div v-for="(rel, targetId) in npc.relationships" :key="targetId" class="truncate">
                → {{ rel }}
              </div>
            </div>
          </div>

          <!-- 秘密 -->
          <div v-if="npc.secrets.length > 0" class="text-[9px] text-red-400">
            <span class="font-bold">秘密:</span>
            <div class="ml-1">
              <div v-for="(secret, idx) in npc.secrets" :key="idx" class="truncate">
                🔒 {{ secret }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- NPC反应（最新） -->
    <div
      v-if="playerStore.lastNPCReactions.length > 0"
      class="pt-2 border-t border-mc-border/20"
    >
      <div class="text-mc-border font-pixel text-[10px] font-bold uppercase mb-1">
        最新反应
      </div>
      <div
        v-for="reaction in playerStore.lastNPCReactions"
        :key="reaction.npc_id"
        class="px-2 py-1 bg-black/5 rounded text-[9px] text-mc-text/70 mb-1 last:mb-0"
      >
        <span class="font-bold text-mc-border">{{ reaction.npc_name }}:</span>
        {{ reaction.reaction }}
        <span
          class="ml-1"
          :class="reaction.attitude_change > 0 ? 'text-green-500' : 'text-red-500'"
        >
          ({{ reaction.attitude_change > 0 ? '+' : '' }}{{ reaction.attitude_change }})
        </span>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="npcs.length === 0" class="p-4 text-center">
      <div class="text-mc-text/40 font-pixel text-xs">
        暂无NPC数据
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #313131;
  border: 1px solid #555555;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #c6c6c6;
  border: 1px solid #555555;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #ffffff;
}
</style>
