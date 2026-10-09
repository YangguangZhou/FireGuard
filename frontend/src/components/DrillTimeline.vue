<template>
  <section class="overflow-hidden rounded-2xl border border-slate-700/70 bg-slate-900/75 shadow-glass backdrop-blur-xl">
    <div class="flex flex-wrap items-start justify-between gap-4 border-b border-slate-700/60 px-4 py-4 md:px-5">
      <div>
        <div class="mb-1 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.2em] text-cyan-300">
          <span class="h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-[0_0_10px_#22d3ee]"></span>
          Guided demo · 约 40 秒
        </div>
        <h2 class="text-base font-bold text-white md:text-lg">现场应急处置演示</h2>
        <p class="mt-1 text-xs text-slate-400">按「常态巡检 → 火情识别 → 通道阻断 → 处置复盘」依次观察系统决策。</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="store.toggleAutoDrill" :class="store.isAutoDrillPlaying ? 'border-rose-400/40 bg-rose-500/15 text-rose-200 hover:bg-rose-500/25' : 'border-cyan-400/30 bg-cyan-400 text-slate-950 hover:bg-cyan-300'" class="rounded-xl border px-4 py-2 text-xs font-bold shadow-lg transition">
          <span class="inline-flex items-center gap-1.5"><Pause v-if="store.isAutoDrillPlaying" :size="13" /><Play v-else :size="13" />{{ store.isAutoDrillPlaying ? '暂停演示' : '自动播放' }}</span>
        </button>
        <button @click="store.resetAllToNormal" class="rounded-xl border border-slate-700 bg-slate-950/70 px-3 py-2 text-xs font-semibold text-slate-300 transition hover:border-slate-500 hover:text-white">重新开始</button>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-2 p-3 md:grid-cols-4 md:gap-3 md:p-4">
      <button v-for="(step, idx) in store.drillSteps" :key="step.id" @click="store.jumpToStep(idx)" :class="stepClass(idx)" class="group relative min-h-[108px] rounded-xl border p-3 text-left transition duration-200 hover:-translate-y-0.5 md:p-4">
        <div class="mb-3 flex items-center justify-between">
          <span class="font-mono text-[10px] font-bold tracking-widest opacity-70">{{ String(idx + 1).padStart(2, '0') }}</span>
          <span v-if="idx < store.currentDrillStep" class="text-[10px] font-semibold text-emerald-300">完成</span>
          <span v-else-if="idx === store.currentDrillStep" class="rounded-full bg-white/10 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider">当前</span>
          <span v-else class="text-[10px] opacity-50">待开始</span>
        </div>
        <div class="text-xs font-bold leading-snug md:text-sm">{{ step.label }}</div>
        <div class="mt-1.5 line-clamp-2 text-[10px] leading-relaxed opacity-70">{{ shortDescription(idx) }}</div>
        <div v-if="idx < store.drillSteps.length - 1" class="absolute -right-2.5 top-1/2 z-10 hidden h-px w-3 bg-slate-600 md:block"></div>
      </button>
    </div>

    <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-700/60 bg-slate-950/40 px-4 py-3 md:px-5">
      <div class="flex min-w-0 items-start gap-3">
        <div class="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-cyan-400/10 text-xs font-bold text-cyan-300">{{ String(store.currentDrillStep + 1).padStart(2, '0') }}</div>
        <div class="min-w-0">
          <div class="text-xs font-semibold text-slate-100">{{ store.drillSteps[store.currentDrillStep]?.label }}</div>
          <p class="mt-0.5 text-[10px] leading-relaxed text-slate-400">{{ store.drillSteps[store.currentDrillStep]?.desc }}</p>
        </div>
      </div>
      <button v-if="store.currentDrillStep < store.drillSteps.length - 1" @click="store.jumpToStep(store.currentDrillStep + 1)" class="shrink-0 rounded-lg border border-slate-700 px-3 py-2 text-[10px] font-semibold text-slate-200 transition hover:border-cyan-400/60 hover:text-cyan-200">
        下一步 <span aria-hidden="true">→</span>
      </button>
      <span v-else class="shrink-0 text-[10px] font-semibold text-emerald-300">流程已完成 · 可重新开始</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useEmergencyStore } from '@/stores/emergencyStore';
import { Pause, Play } from 'lucide-vue-next';

const store = useEmergencyStore();
const activeClasses = [
  'border-emerald-400/60 bg-emerald-400/10 text-emerald-100 ring-1 ring-emerald-400/20',
  'border-rose-400/60 bg-rose-400/10 text-rose-100 ring-1 ring-rose-400/20',
  'border-amber-400/60 bg-amber-400/10 text-amber-100 ring-1 ring-amber-400/20',
  'border-cyan-400/60 bg-cyan-400/10 text-cyan-100 ring-1 ring-cyan-400/20',
];

function stepClass(idx: number) {
  const active = idx === store.currentDrillStep;
  const done = idx < store.currentDrillStep;
  if (active) return activeClasses[idx];
  if (done) return 'border-emerald-500/20 bg-emerald-500/[.04] text-slate-300';
  return 'border-slate-700/80 bg-slate-950/40 text-slate-300 hover:border-slate-500 hover:bg-slate-800/70';
}

function shortDescription(idx: number) {
  return [
    '确认人员、出口与通道处于安全状态',
    '识别东侧火情并生成疏散路线',
    '发现西侧阻断，重新规划避险路线',
    '回顾处置结果并查看规范记录单',
  ][idx];
}
</script>
