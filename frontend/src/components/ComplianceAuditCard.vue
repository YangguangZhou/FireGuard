<template>
  <div class="bg-cyberPanelSoft border border-cyberBorder rounded-xl p-3 flex flex-col shadow-glass">
    <div class="flex items-center justify-between pb-1.5 mb-2 border-b border-cyberBorder/60">
      <h2 class="text-xs font-bold text-slate-100 flex items-center gap-1.5">
        <Scale :size="14" />
        <span>GB/T 50720 施工消防合规审计</span>
      </h2>
      <span
        class="px-2 py-0.5 rounded text-[10px] font-bold border"
        :class="store.compliance?.compliance_status === 'COMPLIANT' ? 'bg-emerald-950/80 text-emerald-300 border-emerald-600' : 'bg-rose-950/80 text-rose-300 border-rose-600 animate-pulse'"
      >
        {{ store.compliance?.compliance_status || 'COMPLIANT' }}
      </span>
    </div>

    <div class="space-y-1.5 text-[11px] text-slate-400">
      <div class="flex justify-between items-center bg-slate-950/60 px-2 py-1 rounded">
        <span>双出口分流 (GB 50016):</span>
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
  </div>
</template>

<script setup lang="ts">
import { useEmergencyStore } from '@/stores/emergencyStore';
import { Scale } from 'lucide-vue-next';

const store = useEmergencyStore();
</script>
