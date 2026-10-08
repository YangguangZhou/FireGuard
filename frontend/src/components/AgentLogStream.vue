<template>
  <div class="bg-cyberPanelSoft border border-cyberBorder rounded-xl p-3 flex flex-col shadow-glass flex-1 min-h-[160px]">
    <div class="flex items-center justify-between pb-1.5 mb-2 border-b border-cyberBorder/60">
      <h2 class="text-xs font-bold text-slate-100 flex items-center gap-1.5">
        <span>🧠</span>
        <span>Agent 决策推演与事件日志</span>
      </h2>
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
    </div>

    <!-- 日志流列表 -->
    <div
      ref="logContainerRef"
      class="flex-1 overflow-y-auto space-y-2 pr-1 font-mono text-[9px] max-h-36"
    >
      <div
        v-for="(log, idx) in store.logs"
        :key="idx"
        class="p-2 rounded bg-slate-950/80 border border-slate-800/80 hover:border-slate-700 transition"
      >
        <div class="flex justify-between items-center text-[9px] text-slate-500 mb-1">
          <span>{{ log.timestamp }}</span>
          <span
            class="font-semibold px-1.5 py-0.2 rounded font-mono"
            :class="getLogBadgeClass(log.event_type)"
          >
            {{ log.event_type }}
          </span>
        </div>
        <div class="text-slate-200 leading-relaxed font-sans text-[10px]">
          {{ log.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useEmergencyStore } from '@/stores/emergencyStore';

const store = useEmergencyStore();
const logContainerRef = ref<HTMLElement | null>(null);

function getLogBadgeClass(type: string) {
  if (type.includes('ALARM') || type.includes('HAZARD')) return 'bg-rose-950 text-rose-300 border border-rose-800';
  if (type.includes('A_STAR') || type.includes('REPLAN')) return 'bg-cyan-950 text-cyan-300 border border-cyan-800';
  if (type.includes('TTS') || type.includes('VOICE')) return 'bg-purple-950 text-purple-300 border border-purple-800';
  return 'bg-slate-900 text-slate-400 border border-slate-800';
}

watch(
  () => store.logs.length,
  async () => {
    await nextTick();
    if (logContainerRef.value) {
      logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight;
    }
  }
);
</script>
