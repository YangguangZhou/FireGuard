<template>
  <header class="bg-cyberPanel/80 backdrop-blur-xl border-b border-cyberBorder px-4 py-2.5 flex items-center justify-between shadow-glass sticky top-0 z-40 relative group">
    <!-- Subtle top edge reflection -->
    <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-white/0 via-white/10 to-white/0"></div>
    
    <!-- Animated bottom accent line -->
    <div class="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-cyan-500/0 via-cyan-500/50 to-cyan-500/0 opacity-70 group-hover:opacity-100 transition-opacity duration-700">
      <div class="absolute top-0 left-0 h-full w-1/4 bg-gradient-to-r from-transparent via-cyan-300 to-transparent scan-overlay"></div>
    </div>

    <!-- 左侧：中建国际赛事标识与系统标题 -->
    <div class="flex items-center gap-4">
      <div class="relative">
        <div class="absolute inset-0 bg-cyan-500/20 blur-md rounded-lg animate-pulse"></div>
        <div class="relative w-10 h-10 rounded-lg bg-gradient-to-br from-blue-700 via-indigo-600 to-cyan-500 flex items-center justify-center font-bold text-lg text-white shadow-glow-blue border border-cyan-300/40">
          <ShieldCheck :size="22" :stroke-width="1.8" />
        </div>
      </div>
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-lg font-black tracking-widest bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-cyan-300 drop-shadow-sm">
            筑安·火眼 FireGuard
          </h1>
          <span class="text-[10px] px-2 py-0.5 rounded-sm bg-indigo-950/60 text-cyan-300 border border-cyan-500/40 font-mono tracking-wider shadow-inner-glow">
            3F 动态施工作业层
          </span>
        </div>
        <div class="h-[1px] w-full bg-gradient-to-r from-slate-700/50 to-transparent my-1"></div>
        <p class="text-[10px] text-slate-400 font-sans tracking-wide hidden sm:block opacity-80">
          面向动态施工环境的多模态火灾应急疏散智能体系统 · 规范驱动与智能避险引导
        </p>
      </div>
    </div>

    <!-- 中间：当前态势状态指示灯 -->
    <div class="hidden lg:flex flex-col items-center justify-center absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
      <div class="flex items-center gap-3 px-4 py-1.5 rounded-full bg-slate-950/80 border border-slate-700/50 shadow-glass-sm hud-bracket">
        <div class="flex items-center gap-2 text-xs font-bold tracking-widest uppercase">
          <span class="relative flex h-3 w-3">
            <span :class="pulseClass" class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"></span>
            <span :class="dotClass" class="relative inline-flex rounded-full h-3 w-3 glow-dot shadow-[0_0_8px_currentColor]"></span>
          </span>
          <span :class="titleColorClass">{{ statusTitle }}</span>
        </div>
        <div class="h-3.5 w-px bg-slate-700"></div>
        <div class="text-xs text-slate-400 font-mono tracking-widest badge-mono">
          {{ currentTime }}
        </div>
      </div>
    </div>

    <!-- 右侧：快捷操作与导出记录单 -->
    <div class="flex items-center gap-3 relative z-10">
      <button 
        @click="store.showReportModal = true; store.fetchReport()"
        class="px-4 py-2 bg-gradient-to-br from-slate-800 to-slate-900 hover:from-slate-700 hover:to-slate-800 border border-slate-600/50 hover:border-cyan-400/60 rounded-md text-xs font-bold tracking-wider text-slate-200 hover:text-white flex items-center gap-2 transition-all duration-300 shadow-glass hover:shadow-glow-blue hover-lift group">
        <FileText :size="16" class="text-slate-400 group-hover:text-cyan-300 transition-colors" />
        <span class="uppercase">应急处置记录单</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ShieldCheck, FileText } from 'lucide-vue-next';
import { useEmergencyStore } from '@/stores/emergencyStore';

const store = useEmergencyStore();
const currentTime = ref('');
let timer: any = null;

function updateTime() {
  const d = new Date();
  currentTime.value = d.toLocaleTimeString('zh-CN', { hour12: false });
}

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});

const statusTitle = computed(() => {
  switch (store.currentAct) {
    case 'ACT_1_NORMAL':
      return '常态安全巡检 · 通道顺畅合规';
    case 'ACT_2_FIRE':
      return '突发火情 · 动态避险光流引导中';
    case 'ACT_3_BLOCKAGE':
      return '次生坍塌 · 二次重路由至避难平台';
    default:
      return '态势监控中';
  }
});

const dotClass = computed(() => {
  switch (store.currentAct) {
    case 'ACT_1_NORMAL': return 'bg-emerald-500';
    case 'ACT_2_FIRE': return 'bg-rose-500';
    case 'ACT_3_BLOCKAGE': return 'bg-amber-500';
    default: return 'bg-slate-500';
  }
});

const pulseClass = computed(() => {
  switch (store.currentAct) {
    case 'ACT_1_NORMAL': return 'bg-emerald-400';
    case 'ACT_2_FIRE': return 'bg-rose-400';
    case 'ACT_3_BLOCKAGE': return 'bg-amber-400';
    default: return 'bg-slate-400';
  }
});

const titleColorClass = computed(() => {
  switch (store.currentAct) {
    case 'ACT_1_NORMAL': return 'text-emerald-400';
    case 'ACT_2_FIRE': return 'text-rose-400';
    case 'ACT_3_BLOCKAGE': return 'text-amber-400';
    default: return 'text-slate-400';
  }
});
</script>
