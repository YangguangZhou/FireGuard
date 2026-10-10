<template>
  <section class="panel-glass overflow-hidden rounded-2xl flex flex-col border border-cyberBorder">
    <div class="flex flex-wrap items-start justify-between gap-4 border-b border-cyberBorder/60 px-4 py-4 md:px-5 relative">
      <div class="scan-overlay absolute inset-0 pointer-events-none opacity-20"></div>
      <div class="relative z-10">
        <div class="mb-1 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.2em] text-cyan-300 text-shimmer">
          <span class="h-1.5 w-1.5 rounded-full bg-cyan-400 glow-dot"></span>
          Guided demo · 约 40 秒
        </div>
        <h2 class="panel-section-title">现场应急处置演示</h2>
        <p class="panel-subtitle mt-1">按「常态巡检 → 火情识别 → 通道阻断 → 处置复盘」依次观察系统决策。</p>
      </div>
      <div class="flex items-center gap-2 relative z-10">
        <button @click="store.toggleAutoDrill" :class="store.isAutoDrillPlaying ? 'border-rose-400/40 bg-rose-500/15 text-rose-200 hover:bg-rose-500/25' : 'btn-primary'" class="rounded-xl border px-4 py-2 text-xs font-bold shadow-lg transition">
          <span class="inline-flex items-center gap-1.5"><Pause v-if="store.isAutoDrillPlaying" :size="13" /><Play v-else :size="13" />{{ store.isAutoDrillPlaying ? '暂停演示' : '自动播放' }}</span>
        </button>
        <button @click="store.resetAllToNormal" class="btn-ghost rounded-xl border px-3 py-2 text-xs font-semibold transition">重新开始</button>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-2 p-3 md:grid-cols-4 md:gap-3 md:p-4 bg-cyberBg/30">
      <button v-for="(step, idx) in store.drillSteps" :key="step.id" @click="store.jumpToStep(idx)" :class="[stepClass(idx), idx === store.currentDrillStep ? 'gradient-border hover-lift' : '']" class="group relative min-h-[108px] rounded-xl border p-3 text-left transition duration-200 hover:-translate-y-0.5 md:p-4 bg-cyberPanelSoft">
        <div class="mb-3 flex items-center justify-between">
          <span class="font-mono text-[10px] font-bold tracking-widest opacity-70" :class="idx === store.currentDrillStep ? 'text-cyan-300 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]' : ''">{{ String(idx + 1).padStart(2, '0') }}</span>
          <span v-if="idx < store.currentDrillStep" class="badge-mono text-[10px] font-semibold text-emerald-300">完成</span>
          <span v-else-if="idx === store.currentDrillStep" class="badge-mono rounded-full bg-cyan-400/20 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-cyan-200 shadow-glow-blue animate-pulse">当前</span>
          <span v-else class="text-[10px] opacity-50">待开始</span>
        </div>
        <div class="text-xs font-bold leading-snug md:text-sm">{{ step.label }}</div>
        <div class="mt-1.5 line-clamp-2 text-[10px] leading-relaxed opacity-70">{{ shortDescription(idx) }}</div>
        <div v-if="idx < store.drillSteps.length - 1" class="absolute -right-2.5 top-1/2 z-10 hidden h-px w-3 border-t-2 border-dashed border-cyan-500/50 md:block"></div>
      </button>
    </div>

    <div class="flex flex-wrap items-center justify-between gap-3 border-t border-cyberBorder/60 bg-cyberPanelSoft/80 px-4 py-3 md:px-5">
      <div class="flex min-w-0 items-start gap-3">
        <div class="icon-box-cyan mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg text-xs font-bold">{{ String(store.currentDrillStep + 1).padStart(2, '0') }}</div>
        <div class="min-w-0">
          <div class="text-xs font-semibold text-slate-100 uppercase tracking-wide">{{ store.drillSteps[store.currentDrillStep]?.label }}</div>
          <p class="mt-0.5 text-[10px] leading-relaxed text-slate-400">{{ store.drillSteps[store.currentDrillStep]?.desc }}</p>
        </div>
      </div>
      <button v-if="store.currentDrillStep < store.drillSteps.length - 1" @click="store.jumpToStep(store.currentDrillStep + 1)" class="btn-ghost shrink-0 rounded-lg px-3 py-2 text-[10px] font-semibold transition uppercase tracking-wider">
        下一步 <span aria-hidden="true" class="ml-1">→</span>
      </button>
      <span v-else class="shrink-0 text-[10px] font-semibold text-emerald-300 uppercase tracking-widest font-mono shadow-glow-green/20">流程已完成 · 可重新开始</span>
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
