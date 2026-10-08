<template>
  <header class="bg-cyberPanel/90 backdrop-blur-md border-b border-cyberBorder px-4 py-2.5 flex items-center justify-between shadow-glass sticky top-0 z-40">
    <!-- 左侧：中建国际赛事标识与系统标题 -->
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center font-bold text-lg text-white shadow-glow-blue border border-cyan-400/30">
        🛡️
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-base font-extrabold tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-cyan-400">
            筑安·火眼 FireGuard
          </h1>
          <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-950/80 text-cyan-300 border border-cyan-500/30 font-medium">
            3F 动态施工作业层
          </span>
          <span class="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono hidden md:inline-block">
            第一届“海之子”杯参赛作品
          </span>
        </div>
        <p class="text-[10px] text-slate-400 font-sans hidden sm:block">
          面向动态施工环境的多模态火灾应急疏散智能体系统 · 规范驱动与千人千面避险
        </p>
      </div>
    </div>

    <!-- 中间：当前态势状态指示灯 -->
    <div class="hidden lg:flex items-center gap-3 px-3 py-1 rounded-full bg-slate-950/70 border border-slate-800">
      <div class="flex items-center gap-1.5 text-xs font-semibold">
        <span class="relative flex h-2.5 w-2.5">
          <span :class="pulseClass" class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"></span>
          <span :class="dotClass" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
        </span>
        <span :class="titleColorClass">{{ statusTitle }}</span>
      </div>
      <div class="h-3 w-px bg-slate-800"></div>
      <div class="text-[11px] text-slate-400 font-mono">
        {{ currentTime }}
      </div>
    </div>

    <!-- 右侧：快捷操作与导出记录单 -->
    <div class="flex items-center gap-2">
      <button 
        @click="store.showReportModal = true; store.fetchReport()"
        class="px-3 py-1.5 bg-gradient-to-r from-slate-900 to-slate-800 hover:from-slate-800 hover:to-slate-700 border border-slate-700 hover:border-cyan-500/50 rounded-lg text-xs font-semibold text-slate-200 hover:text-white flex items-center gap-1.5 transition shadow">
        <span>📄</span>
        <span>应急处置记录单</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
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
      return '常态安全巡检 · 满足GB/T 50720';
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
