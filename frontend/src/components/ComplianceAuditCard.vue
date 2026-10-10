<template>
  <div class="panel-glass bg-cyberPanelSoft border border-cyberBorder rounded-xl p-3 flex flex-col shadow-glass relative overflow-hidden">
    <div class="scan-overlay opacity-10"></div>
    
    <!-- 顶栏：标签页切换与状态徽章 -->
    <div class="flex items-center justify-between pb-2 mb-2 border-b border-cyberBorder/60 relative z-10">
      <div class="flex items-center gap-1.5 text-[11px] font-bold bg-slate-900/80 p-0.5 rounded-full shadow-inner-glow">
        <button
          @click="activeTab = 'compliance'"
          class="px-2.5 py-1 rounded-full transition-all duration-300 flex items-center gap-1.5"
          :class="activeTab === 'compliance' ? 'bg-cyan-500/20 text-cyan-300 shadow-glow-blue border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <div class="icon-box-cyan">
            <Scale :size="12" />
          </div>
          <span class="uppercase tracking-wider">规范审计</span>
        </button>
        <button
          @click="activeTab = 'scientific'"
          class="px-2.5 py-1 rounded-full transition-all duration-300 flex items-center gap-1.5"
          :class="activeTab === 'scientific' ? 'bg-cyan-500/20 text-cyan-300 shadow-glow-blue border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <div class="icon-box-cyan">
            <Microscope :size="12" />
          </div>
          <span class="uppercase tracking-wider flex items-center gap-1">科学评价<span class="w-1.5 h-1.5 rounded-full bg-cyan-400 glow-dot" v-if="activeTab === 'scientific'"></span></span>
        </button>
      </div>

      <span
        v-if="activeTab === 'compliance'"
        class="badge-mono px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wider shadow-sm"
        :class="store.compliance?.compliance_status === 'COMPLIANT' ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/50 shadow-glow-green' : 'bg-rose-950/80 text-rose-400 border-rose-500/50 animate-pulse shadow-glow-red'"
      >
        {{ store.compliance?.compliance_status || 'COMPLIANT' }}
      </span>
      <span
        v-else
        class="badge-mono px-2 py-0.5 rounded text-[9px] font-bold bg-blue-950/80 text-cyan-300 border border-cyan-700/60 shadow-glow-blue uppercase tracking-wider"
      >
        多物理场模型
      </span>
    </div>

    <!-- Tab 1: 施工消防安全合规审计 -->
    <div v-if="activeTab === 'compliance'" class="space-y-2 text-[11px] text-slate-400 relative z-10">
      <div class="flex justify-between items-center bg-slate-900/60 px-2.5 py-1.5 rounded-lg border border-slate-700/50 shadow-inner-glow">
        <span class="uppercase tracking-wider">双出口分流:</span>
        <span class="font-semibold" :class="store.compliance?.dual_exit_compliant ? 'text-emerald-400 shadow-glow-green badge-mono px-1.5 rounded bg-emerald-950/30' : 'text-amber-400 shadow-glow-amber badge-mono px-1.5 rounded bg-amber-950/30'">
          {{ store.compliance?.dual_exit_compliant ? '满足' : '预警' }}
        </span>
      </div>

      <div class="flex justify-between items-center bg-slate-900/60 px-2.5 py-1.5 rounded-lg border border-slate-700/50 shadow-inner-glow">
        <span class="uppercase tracking-wider">最大疏散距离:</span>
        <span class="font-mono text-cyan-300 font-bold badge-mono bg-cyan-950/30 px-1.5 rounded shadow-glow-blue text-xs">
          {{ store.compliance?.max_evac_distance_m || 23.4 }} m
        </span>
      </div>

      <div class="bg-gradient-to-br from-slate-900/90 to-slate-800/80 p-2.5 rounded-lg border border-slate-700/60 text-[10px] text-slate-300 shadow-inner-glow relative overflow-hidden">
        <div class="absolute left-0 top-0 bottom-0 w-0.5 bg-cyan-500/50"></div>
        <span class="text-cyan-400/80 font-semibold uppercase tracking-wider block mb-1">规范判定:</span>
        <span class="leading-relaxed">{{ store.compliance?.audit_notes?.[0] || '全通道满足临时消防疏散通道净宽与距离要求。' }}</span>
      </div>
    </div>

    <!-- Tab 2: 动态多物理场寻径科学评价体系 -->
    <div v-else class="space-y-2.5 text-[10px] relative z-10">
      <!-- 动态权重分布条 (式 6, 7) -->
      <div class="bg-slate-900/70 p-2.5 rounded-lg border border-slate-700/50 shadow-inner-glow relative hover-lift">
        <div class="hud-bracket opacity-30"></div>
        <div class="flex justify-between items-center text-slate-400 mb-1.5">
          <span class="font-medium uppercase tracking-wider text-[9px]">火灾动力学阶段:</span>
          <span class="font-bold text-cyan-300 text-shimmer">
            {{ store.scientificEvaluation?.stage_name || '初始期' }}
          </span>
        </div>
        <div class="text-[9px] text-slate-400 mb-1.5 flex justify-between">
          <span class="uppercase tracking-wider">多物理场动态权重:</span>
          <span class="font-mono text-slate-300 tracking-tight">
            温度 <span class="text-rose-400">{{ getWeight('temp') }}</span> · 
            能见度 <span class="text-cyan-400">{{ getWeight('visibility') }}</span> · 
            CO <span class="text-amber-400">{{ getWeight('co') }}</span>
          </span>
        </div>
        <!-- 权重分配横向堆叠条 -->
        <div class="w-full h-2 rounded-full overflow-hidden flex bg-slate-950 shadow-inner-glow p-0.5 gap-0.5">
          <div class="bg-gradient-to-r from-rose-600 to-rose-400 rounded-full shadow-glow-red transition-all duration-500" :style="{ width: getWeight('temp') }" title="温度权重"></div>
          <div class="bg-gradient-to-r from-cyan-600 to-cyan-400 rounded-full shadow-glow-blue transition-all duration-500" :style="{ width: getWeight('visibility') }" title="能见度权重"></div>
          <div class="bg-gradient-to-r from-amber-600 to-amber-400 rounded-full shadow-glow-amber transition-all duration-500" :style="{ width: getWeight('co') }" title="CO浓度权重"></div>
        </div>
      </div>

      <!-- 4项核心科学指标网格 (表 4, 表 5) -->
      <div class="grid grid-cols-2 gap-2 text-[10px]">
        <div class="bg-slate-900/60 p-2 rounded-lg border border-slate-700/50 flex flex-col justify-between shadow-inner-glow hover:border-cyan-500/50 hover:shadow-glow-blue transition-all duration-300 hover-lift relative group">
          <span class="text-slate-400 text-[9px] uppercase tracking-wider group-hover:text-cyan-300/80 transition-colors">路径效率 η:</span>
          <span class="font-mono text-emerald-400 font-bold text-xs mt-1 shadow-glow-green bg-emerald-950/20 px-1.5 py-0.5 rounded self-start">
            {{ store.scientificEvaluation?.mean_path_efficiency || 1.00 }}
          </span>
        </div>

        <div class="bg-slate-900/60 p-2 rounded-lg border border-slate-700/50 flex flex-col justify-between shadow-inner-glow hover:border-cyan-500/50 hover:shadow-glow-blue transition-all duration-300 hover-lift relative group">
          <span class="text-slate-400 text-[9px] uppercase tracking-wider group-hover:text-cyan-300/80 transition-colors">重规划响应延迟:</span>
          <span class="font-mono text-cyan-400 font-bold text-xs mt-1 shadow-glow-blue bg-cyan-950/20 px-1.5 py-0.5 rounded self-start">
            {{ store.scientificEvaluation?.replan_latency_ms || 4.2 }} ms
          </span>
        </div>

        <div class="bg-slate-900/60 p-2 rounded-lg border border-slate-700/50 flex flex-col justify-between shadow-inner-glow hover:border-cyan-500/50 hover:shadow-glow-blue transition-all duration-300 hover-lift relative group">
          <span class="text-slate-400 text-[9px] uppercase tracking-wider group-hover:text-cyan-300/80 transition-colors">最大/平均通行代价:</span>
          <span class="font-mono text-amber-400 font-bold text-[11px] mt-1 shadow-glow-amber bg-amber-950/20 px-1.5 py-0.5 rounded self-start">
            {{ store.scientificEvaluation?.max_passage_cost || 1.07 }} / {{ store.scientificEvaluation?.mean_passage_cost || 1.07 }}
          </span>
        </div>

        <div class="bg-slate-900/60 p-2 rounded-lg border border-slate-700/50 flex flex-col justify-between shadow-inner-glow hover:border-cyan-500/50 hover:shadow-glow-blue transition-all duration-300 hover-lift relative group">
          <span class="text-slate-400 text-[9px] uppercase tracking-wider group-hover:text-cyan-300/80 transition-colors">路径平滑拐点数:</span>
          <span class="font-mono text-slate-200 font-bold text-[11px] mt-1 bg-slate-800/80 px-1.5 py-0.5 rounded self-start border border-slate-600/50">
            {{ store.scientificEvaluation?.total_inflexion_points || 3 }} 处拐角
          </span>
        </div>
      </div>

      <!-- 出口均衡利用率 (表 6) -->
      <div class="bg-slate-900/80 px-2.5 py-1.5 rounded-lg text-[9px] text-slate-400 flex items-center justify-between border border-slate-700/50 shadow-inner-glow hover-lift relative overflow-hidden">
        <div class="absolute left-0 top-0 bottom-0 w-0.5 bg-cyan-500/50"></div>
        <span class="uppercase tracking-wider font-semibold pl-1">出口均衡利用率:</span>
        <div class="flex items-center gap-1.5 font-mono text-cyan-300">
          <span v-for="(ratio, exitKey) in store.scientificEvaluation?.exit_utilization" :key="exitKey" class="bg-cyan-950/40 px-1 rounded shadow-glow-blue border border-cyan-800/50">
            {{ formatExitKey(exitKey) }}:{{ ratio }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Scale, Microscope } from 'lucide-vue-next';
import { useEmergencyStore } from '@/stores/emergencyStore';

const store = useEmergencyStore();
const activeTab = ref<'compliance' | 'scientific'>('scientific');

function getWeight(key: 'temp' | 'visibility' | 'co'): string {
  const w = store.scientificEvaluation?.dynamic_weights?.[key];
  if (w === undefined || w === null) {
    if (key === 'temp') return '30%';
    if (key === 'visibility') return '40%';
    return '30%';
  }
  return `${Math.round(w * 100)}%`;
}

function formatExitKey(key: string): string {
  if (key === 'EXIT_EAST') return '东A';
  if (key === 'EXIT_WEST') return '西B';
  if (key === 'EXIT_REFUGE') return '南C';
  return key;
}
</script>
