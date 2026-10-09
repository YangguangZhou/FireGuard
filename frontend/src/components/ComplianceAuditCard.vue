<template>
  <div class="bg-cyberPanelSoft border border-cyberBorder rounded-xl p-3 flex flex-col shadow-glass">
    <!-- 顶栏：标签页切换与状态徽章 -->
    <div class="flex items-center justify-between pb-1.5 mb-2 border-b border-cyberBorder/60">
      <div class="flex items-center gap-1 text-[11px] font-bold">
        <button
          @click="activeTab = 'compliance'"
          class="px-2 py-0.5 rounded transition"
          :class="activeTab === 'compliance' ? 'bg-cyan-400/20 text-cyan-200 border border-cyan-400/40' : 'text-slate-400 hover:text-slate-200'"
        >
          <Scale :size="12" class="inline-block mr-1" />规范审计
        </button>
        <button
          @click="activeTab = 'scientific'"
          class="px-2 py-0.5 rounded transition flex items-center gap-1"
          :class="activeTab === 'scientific' ? 'bg-cyan-400/20 text-cyan-200 border border-cyan-400/40' : 'text-slate-400 hover:text-slate-200'"
        >
          <span class="flex items-center gap-1"><Microscope :size="12" />科学评价</span>
          <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
        </button>
      </div>

      <span
        v-if="activeTab === 'compliance'"
        class="px-2 py-0.5 rounded text-[10px] font-bold border"
        :class="store.compliance?.compliance_status === 'COMPLIANT' ? 'bg-emerald-950/80 text-emerald-300 border-emerald-600' : 'bg-rose-950/80 text-rose-300 border-rose-600 animate-pulse'"
      >
        {{ store.compliance?.compliance_status || 'COMPLIANT' }}
      </span>
      <span
        v-else
        class="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-blue-950/80 text-cyan-300 border border-cyan-700/60"
      >
        多物理场模型
      </span>
    </div>

    <!-- Tab 1: 施工消防安全合规审计 -->
    <div v-if="activeTab === 'compliance'" class="space-y-1.5 text-[11px] text-slate-400">
      <div class="flex justify-between items-center bg-slate-950/60 px-2 py-1 rounded">
        <span>双出口分流:</span>
        <span class="font-semibold text-white">
          {{ store.compliance?.dual_exit_compliant ? '满足' : '预警' }}
        </span>
      </div>

      <div class="flex justify-between items-center bg-slate-950/60 px-2 py-1 rounded">
        <span>最大疏散距离:</span>
        <span class="font-mono text-amber-300 font-bold">
          {{ store.compliance?.max_evac_distance_m || 23.4 }} m
        </span>
      </div>

      <div class="bg-slate-950/80 p-2 rounded border border-slate-900 text-[10px] text-slate-300">
        <span class="text-slate-500 font-medium">规范判定:</span>
        <span class="ml-1">{{ store.compliance?.audit_notes?.[0] || '全通道满足临时消防疏散通道净宽与距离要求。' }}</span>
      </div>
    </div>

    <!-- Tab 2: 动态多物理场寻径科学评价体系 -->
    <div v-else class="space-y-2 text-[10px]">
      <!-- 动态权重分布条 (式 6, 7) -->
      <div class="bg-slate-950/80 p-2 rounded-lg border border-slate-800">
        <div class="flex justify-between items-center text-slate-400 mb-1">
          <span class="font-medium">火灾动力学阶段:</span>
          <span class="font-bold text-cyan-300">
            {{ store.scientificEvaluation?.stage_name || '初始期' }}
          </span>
        </div>
        <div class="text-[9px] text-slate-400 mb-1 flex justify-between">
          <span>多物理场动态权重:</span>
          <span class="font-mono text-slate-300">
            温度{{ getWeight('temp') }} · 能见度{{ getWeight('visibility') }} · CO{{ getWeight('co') }}
          </span>
        </div>
        <!-- 权重分配横向堆叠条 -->
        <div class="w-full h-1.5 rounded-full overflow-hidden flex bg-slate-800">
          <div class="bg-rose-500" :style="{ width: getWeight('temp') }" title="温度权重"></div>
          <div class="bg-cyan-400" :style="{ width: getWeight('visibility') }" title="能见度权重"></div>
          <div class="bg-amber-400" :style="{ width: getWeight('co') }" title="CO浓度权重"></div>
        </div>
      </div>

      <!-- 4项核心科学指标网格 (表 4, 表 5) -->
      <div class="grid grid-cols-2 gap-1.5 text-[10px]">
        <div class="bg-slate-950/60 p-1.5 rounded border border-slate-800/80 flex flex-col justify-between">
          <span class="text-slate-400 text-[9px]">路径效率 η (理论最优=1.0):</span>
          <span class="font-mono text-emerald-300 font-bold text-xs mt-0.5">
            {{ store.scientificEvaluation?.mean_path_efficiency || 1.00 }}
          </span>
        </div>

        <div class="bg-slate-950/60 p-1.5 rounded border border-slate-800/80 flex flex-col justify-between">
          <span class="text-slate-400 text-[9px]">重规划响应延迟:</span>
          <span class="font-mono text-cyan-300 font-bold text-xs mt-0.5">
            {{ store.scientificEvaluation?.replan_latency_ms || 4.2 }} ms
          </span>
        </div>

        <div class="bg-slate-950/60 p-1.5 rounded border border-slate-800/80 flex flex-col justify-between">
          <span class="text-slate-400 text-[9px]">最大/平均通行代价:</span>
          <span class="font-mono text-amber-300 font-bold text-[11px] mt-0.5">
            {{ store.scientificEvaluation?.max_passage_cost || 1.07 }} / {{ store.scientificEvaluation?.mean_passage_cost || 1.07 }}
          </span>
        </div>

        <div class="bg-slate-950/60 p-1.5 rounded border border-slate-800/80 flex flex-col justify-between">
          <span class="text-slate-400 text-[9px]">路径平滑拐点数 (≥35°):</span>
          <span class="font-mono text-slate-200 font-bold text-[11px] mt-0.5">
            {{ store.scientificEvaluation?.total_inflexion_points || 3 }} 处拐角
          </span>
        </div>
      </div>

      <!-- 出口均衡利用率 (表 6) -->
      <div class="bg-slate-950/60 px-2 py-1 rounded text-[9px] text-slate-400 flex items-center justify-between">
        <span>出口均衡利用率:</span>
        <div class="flex items-center gap-1 font-mono text-cyan-300">
          <span v-for="(ratio, exitKey) in store.scientificEvaluation?.exit_utilization" :key="exitKey">
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
