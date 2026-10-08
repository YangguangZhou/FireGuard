<template>
  <div class="bg-cyberPanelSoft backdrop-blur-md border border-cyberBorder rounded-xl p-2.5 flex flex-wrap items-center justify-between gap-2 shadow-glass">
    <!-- 步骤选项栏 -->
    <div class="flex items-center gap-2 overflow-x-auto py-0.5">
      <span class="text-xs font-bold text-slate-400 flex items-center gap-1 shrink-0">
        <span class="text-neonBlue">⏱️</span> 演练阶段推演:
      </span>

      <div class="flex items-center gap-1.5">
        <button
          v-for="(st, idx) in store.drillSteps"
          :key="st.id"
          @click="store.jumpToStep(idx)"
          :class="getStepClass(idx)"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 whitespace-nowrap shadow-sm border"
        >
          <span class="font-mono text-[10px] opacity-80">{{ st.tag }}</span>
          <span>{{ st.label }}</span>
        </button>
      </div>
    </div>

    <!-- 控制推演按钮组 -->
    <div class="flex items-center gap-2 shrink-0">
      <button
        @click="store.toggleAutoDrill"
        :class="store.isAutoDrillPlaying ? 'bg-rose-600 text-white animate-pulse shadow-glow-red' : 'bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white shadow-glow-blue'"
        class="px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all shadow"
      >
        <span>{{ store.isAutoDrillPlaying ? '⏸' : '▶' }}</span>
        <span>{{ store.isAutoDrillPlaying ? '暂停自动推演' : '启动全流程推演' }}</span>
      </button>

      <button
        @click="store.resetAllToNormal"
        class="px-2.5 py-1.5 bg-slate-900 border border-slate-700 hover:border-slate-500 hover:bg-slate-800 text-slate-300 rounded-lg text-xs transition flex items-center gap-1"
      >
        <span>↺</span>
        <span>重置清空</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEmergencyStore } from '@/stores/emergencyStore';

const store = useEmergencyStore();

function getStepClass(idx: number) {
  if (store.currentDrillStep === idx) {
    return 'bg-cyan-500 text-slate-950 border-cyan-400 font-bold shadow-glow-blue scale-102';
  }
  return 'bg-slate-950/80 text-slate-400 border-slate-800 hover:border-slate-600 hover:text-slate-200';
}
</script>
