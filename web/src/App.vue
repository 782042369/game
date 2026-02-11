<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import type { ApiChoice } from './api/game'

import ActionPanel from './components/ActionPanel.vue'
import CompanyInfo from './components/CompanyInfo.vue'
import EventArea from './components/EventArea.vue'
import EventPanel from './components/EventPanel.vue'
import HUD from './components/HUD.vue'
import NPCPanel from './components/NPCPanel.vue'
import { useGameStore } from './stores/game'
import { usePlayerStore } from './stores/player'

const gameStore = useGameStore()
const playerStore = usePlayerStore()

const eventLogs = ref<any[]>([])
const currentIcon = ref('🧱')
const currentStatusText = ref('加载中...')
const isAnimating = ref(false)
const isShaking = ref(false)
const isGlitching = ref(false)
const floatingPopups = ref<any[]>([])
let popupId = 0

const player = computed(() => playerStore.playerState)
const isLoading = computed(() => playerStore.isLoading)
const isGameOver = computed(() => playerStore.isGameOver)

const isBossNear = computed(() => player.value.suspicion > 60)

async function handleAction(choiceId: string) {
  // 找到对应的选项
  const choice = playerStore.currentChoices.find(c => c.id === choiceId)
  if (!choice)
    return

  // 视觉反馈触发
  isAnimating.value = true
  if (choice.category === 'slack')
    isGlitching.value = true
  if (choice.id === 'work_hard')
    isShaking.value = true

  setTimeout(() => {
    isAnimating.value = false
    isGlitching.value = false
    isShaking.value = false
  }, 300)

  try {
    // 提交选择到后端
    await playerStore.submitChoice(choiceId)

    // 生成浮动数值反馈
    Object.entries(choice.effects || {}).forEach(([stat, value]) => {
      if (value !== 0) {
        addFloatingPopup({ stat, value })
      }
    })

    addLog({
      time: getTimeString(player.value.turn),
      type: choice.category,
      message: `> 执行任务: ${choice.text}`,
      effects: Object.entries(choice.effects || {}).map(([stat, value]) => ({ stat, value })),
    })

    currentIcon.value = getIconForCategory(choice.category)
    currentStatusText.value = choice.text
  }
  catch (error) {
    console.error('提交行动失败:', error)
    addLog({ time: getTimeString(player.value.turn), type: 'error', message: `提交失败: ${error}` })
  }
}

function getIconForCategory(category: string): string {
  const icons: Record<string, string> = {
    work: '💼',
    slack: '🍃',
    social: '🍺',
    skill: '📚',
    growth: '🚀',
  }
  return icons[category] || '📦'
}

function addFloatingPopup(eff: { stat: string, value: number }) {
  const id = popupId++
  const text = `${getStatName(eff.stat)} ${eff.value > 0 ? '+' : ''}${eff.value}`
  const color = eff.value > 0 ? 'text-green-500' : 'text-red-500'

  floatingPopups.value.push({ id, text, color })
  setTimeout(() => {
    floatingPopups.value = floatingPopups.value.filter(p => p.id !== id)
  }, 800)
}

function getStatName(stat: string) {
  const names: Record<string, string> = {
    chill: '快乐',
    progress: '进度',
    suspicion: '风险',
    energy: '体力',
  }
  return names[stat] || stat
}

function addLog(log: any) {
  eventLogs.value.push(log)
  if (eventLogs.value.length > 50)
    eventLogs.value.shift()
}

function getTimeString(turn: number) {
  const startHour = 9
  const t = turn < 0 ? 0 : turn
  return `${(startHour + t).toString().padStart(2, '0')}:00`
}

async function resetGame() {
  try {
    // 重置本地状态
    eventLogs.value = []
    playerStore.reset()

    // 调用后端API重新开始游戏
    await playerStore.startNewGame('normal')

    addLog({ time: '09:00', type: 'info', message: '区块已重新加载。' })
  }
  catch (error) {
    console.error('重置游戏失败:', error)
    addLog({ time: '09:00', type: 'error', message: `重置失败: ${error}` })
  }
}

onMounted(async () => {
  try {
    // 调用后端API初始化游戏
    await playerStore.startNewGame('normal')

    currentStatusText.value = '准备就绪'
    addLog({ time: '09:00', type: 'info', message: '欢迎进入摸鱼服务器。' })
  }
  catch (error) {
    console.error('游戏初始化失败:', error)
    currentStatusText.value = '连接失败'
    addLog({ time: '09:00', type: 'error', message: `无法连接到服务器: ${error}` })
  }
})

// 监听游戏状态变化
watch(() => playerStore.currentMessage, (newMessage) => {
  if (newMessage) {
    currentStatusText.value = newMessage.substring(0, 20)
  }
})
</script>

<template>
  <div
    class="game-container h-screen overflow-hidden p-6 flex flex-col gap-6 bg-[#313131] font-body selection:bg-mc-exp selection:text-black scanlines transition-transform duration-150"
    :class="{ 'animate-screen-shake': isShaking }"
  >
    <!-- Header -->
    <header class="flex-none flex justify-between items-center mc-panel relative z-10">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-mc-exp border-4 border-black flex items-center justify-center text-3xl shadow-[4px_4px_0px_0px_rgba(0,0,0,0.3)]">
          💾
        </div>
        <div class="flex flex-col">
          <h1 class="text-2xl md:text-3xl font-pixel font-bold text-mc-text tracking-tighter mc-text-shadow">
            <span class="text-green-700">摸鱼</span> 大作战 _ <span class="text-mc-border">2026</span>
          </h1>
          <div class="text-[10px] font-pixel text-mc-border uppercase tracking-widest">
            OFFICE_SURVIVAL_SIMULATOR_V1.3
          </div>
        </div>
      </div>
      <div class="flex gap-4">
        <button
          class="mc-btn text-sm uppercase tracking-widest shadow-lg !px-6"
          :disabled="isLoading"
          @click="resetGame"
        >
          {{ isLoading ? '加载中...' : '重置世界' }}
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-12 gap-4 relative z-10">
      <!-- 左栏 (3列): HUD + CompanyInfo + EventArea -->
      <div class="md:col-span-3 flex flex-col gap-4 min-h-0 overflow-y-auto">
        <HUD />
        <CompanyInfo />
        <EventArea :logs="eventLogs" class="flex-1" />
      </div>

      <!-- 中栏 (5列): Visual + ActionPanel -->
      <div class="md:col-span-5 flex flex-col gap-4">
        <!-- Visual Viewport -->
        <div class="bg-[#1e1e1e] border-[12px] border-[#444444] rounded-none p-8 h-80 flex items-center justify-center relative shadow-[inset_0_0_60px_rgba(0,0,0,0.9),0_10px_0_0_#222222] overflow-hidden">
          <div class="absolute inset-0 opacity-5 pointer-events-none" style="background-image: linear-gradient(#ffffff 2px, transparent 2px), linear-gradient(90deg, #ffffff 2px, transparent 2px); background-size: 40px 40px;" />

          <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-cyan-500/5 to-purple-500/5 pointer-events-none" />

          <div class="text-center z-10 transition-all duration-300 transform" :class="{ 'scale-110 blur-[1px]': isAnimating, 'animate-glitch': isGlitching }">
            <div class="text-[120px] mb-8 animate-bounce drop-shadow-[0_15px_30px_rgba(0,0,0,0.8)]">
              {{ currentIcon }}
            </div>
            <div class="text-3xl font-pixel font-bold text-white tracking-[0.2em] neon-text uppercase drop-shadow-[4px_4px_0px_rgba(0,0,0,0.5)]">
              {{ currentStatusText }}
            </div>
          </div>

          <!-- 数值漂浮动画层 -->
          <div class="absolute inset-0 pointer-events-none z-30">
            <div
              v-for="popup in floatingPopups"
              :key="popup.id"
              class="absolute left-1/2 top-1/2 -translate-x-1/2 animate-float-up font-pixel font-bold text-lg whitespace-nowrap"
              :class="popup.color"
            >
              {{ popup.text }}
            </div>
          </div>

          <div v-if="isBossNear" class="absolute inset-0 border-[20px] border-red-600/30 animate-pulse pointer-events-none z-20" />
          <div v-if="isBossNear" class="absolute top-8 right-8 bg-red-600 text-white px-6 py-3 text-xl font-pixel font-bold animate-bounce shadow-[8px_8px_0_0_rgba(0,0,0,0.5)] border-4 border-white/50 z-30">
            !!! 老板预警 !!!
          </div>
        </div>

        <!-- Actions -->
        <ActionPanel class="flex-1" @choice="handleAction" />
      </div>

      <!-- 右栏 (4列): NPCPanel + EventPanel -->
      <div class="md:col-span-4 flex flex-col gap-4 min-h-0 overflow-y-auto">
        <NPCPanel />
        <EventPanel />
      </div>
    </main>

    <!-- 游戏结束提示 -->
    <div
      v-if="isGameOver"
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
    >
      <div class="bg-[#313131] border-4 border-mc-border p-8 text-center max-w-md">
        <h2 class="text-3xl font-pixel font-bold text-mc-text mb-4">游戏结束</h2>
        <p class="text-mc-text mb-6">{{ playerStore.storyContext }}</p>
        <button class="mc-btn !px-8 !py-3" @click="resetGame">
          重新开始
        </button>
      </div>
    </div>

    <footer class="flex justify-between items-center px-6 py-3 bg-black/20 border-t-2 border-mc-border/20 text-[11px] text-mc-border font-pixel font-bold uppercase tracking-widest relative z-10">
      <div class="flex items-center gap-4">
        <span class="flex items-center gap-1"><span class="w-2 h-2" :class="isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'" /> {{ isLoading ? 'LOADING' : 'ONLINE' }}</span>
        <span>SLACK_VER: 1.3.0</span>
      </div>
      <div class="flex gap-6 opacity-60">
        <span>DAY: {{ player.day }}</span>
        <span>TURN: {{ player.turn }}</span>
      </div>
      <div class="text-mc-text/40">
        坐标: x:1024, z:-2048
      </div>
    </footer>
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  background-color: #313131;
}

.neon-text {
  text-shadow:
    0 0 10px rgba(255, 255, 255, 0.4),
    0 0 20px rgba(6, 182, 212, 0.4);
}

.scanlines {
  position: relative;
  overflow: hidden;
}

.scanlines::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    repeating-linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.08) 50%),
    repeating-linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
  background-size:
    100% 4px,
    4px 100%;
  pointer-events: none;
  z-index: 100;
}
</style>
