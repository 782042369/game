<script setup lang="ts">
import { computed } from 'vue'

import { type CompanyProfile, type GameMeta, usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()

const companyInfo = computed(() => playerStore.companyInfo as CompanyProfile | null)
const gameMeta = computed(() => playerStore.gameMeta as GameMeta | null)

// 魔幻程度配置
const magicalLevelConfig: Record<string, { color: string, icon: string }> = {
  现实: { color: 'bg-gray-500', icon: '🏢' },
  轻度魔幻: { color: 'bg-cyan-500', icon: '✨' },
  中度魔幻: { color: 'bg-purple-500', icon: '🔮' },
  重度魔幻: { color: 'bg-pink-500', icon: '🌟' },
}

const magicalLevelStyle = computed(() => {
  if (!gameMeta.value)
    return { color: '', icon: '' }
  return magicalLevelConfig[gameMeta.value.magical_level] || magicalLevelConfig['现实']
})
</script>

<template>
  <div v-if="companyInfo" class="mc-panel space-y-3">
    <!-- 标题栏 -->
    <div class="flex justify-between items-center border-b-4 border-mc-border pb-2">
      <div class="flex items-center gap-2">
        <span class="text-xl">🏢</span>
        <div class="text-mc-text font-pixel font-bold text-lg tracking-tight">
          公司信息
        </div>
      </div>
      <!-- 魔幻程度标签 -->
      <div
        v-if="gameMeta"
        class="flex items-center gap-1 px-2 py-1 rounded text-[10px] font-pixel font-bold text-white"
        :class="magicalLevelStyle.color"
      >
        <span>{{ magicalLevelStyle.icon }}</span>
        <span>{{ gameMeta.magical_level }}</span>
      </div>
    </div>

    <!-- 公司名称和类型 -->
    <div class="p-3 bg-gradient-to-r from-mc-exp/20 to-transparent border-2 border-mc-exp/50 rounded">
      <div class="text-mc-text font-pixel text-sm font-bold mb-1">
        {{ companyInfo.name }}
      </div>
      <div class="text-[10px] text-mc-text/60">
        类型: {{ companyInfo.type }}
      </div>
    </div>

    <!-- 公司文化 -->
    <div class="p-3 bg-black/5 border border-mc-border/20 rounded">
      <div class="text-mc-border font-pixel text-[10px] font-bold uppercase mb-1">
        公司文化
      </div>
      <div class="text-[10px] text-mc-text/80 leading-relaxed">
        {{ companyInfo.culture }}
      </div>
    </div>

    <!-- 办公氛围 -->
    <div class="p-3 bg-black/5 border border-mc-border/20 rounded">
      <div class="text-mc-border font-pixel text-[10px] font-bold uppercase mb-1">
        办公氛围
      </div>
      <div class="text-[10px] text-mc-text/80 leading-relaxed">
        {{ companyInfo.atmosphere }}
      </div>
    </div>

    <!-- 特殊规则 -->
    <div v-if="companyInfo.special_rules && companyInfo.special_rules.length > 0" class="space-y-1">
      <div class="text-mc-border font-pixel text-[10px] font-bold uppercase">
        特殊规则
      </div>
      <div
        v-for="(rule, index) in companyInfo.special_rules"
        :key="index"
        class="px-2 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded text-[10px] text-mc-text/70"
      >
        ⚠️ {{ rule }}
      </div>
    </div>

    <!-- 魔幻元素 -->
    <div v-if="companyInfo.magical_elements && companyInfo.magical_elements.length > 0" class="space-y-1">
      <div class="text-mc-border font-pixel text-[10px] font-bold uppercase">
        魔幻元素
      </div>
      <div
        v-for="(element, index) in companyInfo.magical_elements"
        :key="index"
        class="px-2 py-1 bg-purple-500/10 border border-purple-500/30 rounded text-[10px] text-mc-text/70"
      >
        ✨ {{ element }}
      </div>
    </div>

    <!-- 文案风格 -->
    <div v-if="gameMeta" class="pt-2 border-t border-mc-border/20">
      <div class="text-[10px] text-mc-text/60">
        文案风格: <span class="text-mc-border font-bold">{{ gameMeta.style_type }}</span>
      </div>
    </div>
  </div>

  <!-- 加载中占位 -->
  <div v-else class="mc-panel p-4 text-center">
    <div class="text-mc-text/40 font-pixel text-xs">
      等待公司数据加载...
    </div>
  </div>
</template>
