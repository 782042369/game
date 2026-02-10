<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'

interface LogEntry {
  time: string
  type: string
  message: string
  effects?: { stat: string, value: number }[]
}

const props = defineProps<{
  logs: LogEntry[]
}>()

const logContainer = ref<HTMLElement | null>(null)

function getLogClass(type: string) {
  switch (type) {
    case 'work': return 'border-l-4 border-l-cyan-600'
    case 'slack': return 'border-l-4 border-l-mc-exp'
    case 'social': return 'border-l-4 border-l-yellow-600'
    case 'boss': return 'border-l-4 border-l-red-600'
    default: return 'border-l-4 border-l-mc-border'
  }
}

function getTypeText(type: string) {
  switch (type) {
    case 'work': return '搬砖'
    case 'slack': return '摸鱼'
    case 'social': return '社交'
    case 'boss': return '突发'
    default: return '情报'
  }
}

function getStatText(stat: string) {
  switch (stat) {
    case 'chill': return '快乐'
    case 'progress': return '进度'
    case 'suspicion': return '风险'
    case 'energy': return '电量'
    default: return stat
  }
}

watch(() => props.logs.length, async () => {
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
})
</script>

<template>
  <div class="mc-panel flex flex-col min-h-0">
    <div class="mb-4 flex items-center justify-between border-b-4 border-mc-border pb-2">
      <h2 class="text-mc-text font-pixel font-bold text-lg uppercase tracking-tight">
        生存日志
      </h2>
      <div class="flex gap-1">
        <div class="w-2 h-2 bg-red-600 animate-pulse rounded-none" />
        <div class="text-[10px] text-mc-border font-pixel font-bold uppercase">
          RECORDING
        </div>
      </div>
    </div>

    <div ref="logContainer" class="event-content flex-1 overflow-y-auto flex flex-col gap-4 font-body text-xl pr-2 custom-scrollbar">
      <div
        v-for="(log, index) in logs"
        :key="index"
        class="log-item p-3 border-2 border-mc-border bg-black/5 relative group transition-all duration-150 hover:bg-black/10"
        :class="getLogClass(log.type)"
      >
        <div class="flex justify-between text-[11px] text-mc-border mb-2 font-pixel font-bold uppercase tracking-widest border-b border-mc-border/20 pb-1">
          <span>[{{ log.time }}]</span>
          <span>{{ getTypeText(log.type) }}</span>
        </div>
        <div class="text-mc-text leading-tight break-words font-bold">
          {{ log.message }}
        </div>

        <div v-if="log.effects" class="mt-3 flex gap-3 flex-wrap">
          <span
            v-for="(eff, i) in log.effects"
            :key="i"
            class="text-xs font-pixel font-bold px-1.5 py-0.5 border border-current bg-white/30"
            :class="eff.value > 0 ? 'text-green-700' : 'text-red-700'"
          >
            {{ getStatText(eff.stat) }}{{ eff.value > 0 ? '++' : '--' }}
          </span>
        </div>
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
  box-shadow: inset 2px 2px 0px rgba(0, 0, 0, 0.2);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #c6c6c6;
  border: 2px solid #555555;
  box-shadow:
    inset -2px -2px 0px rgba(0, 0, 0, 0.2),
    inset 2px 2px 0px rgba(255, 255, 255, 0.2);
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #ffffff;
}
</style>
