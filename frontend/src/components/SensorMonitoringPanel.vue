<template>
  <div class="bg-cyberPanelSoft border border-cyberBorder rounded-2xl p-3 md:p-4 flex flex-col shadow-glass">
    <!-- 面板顶部标题与状态摘要 -->
    <div class="flex flex-wrap items-center justify-between gap-2 pb-2.5 mb-3 border-b border-cyberBorder/60">
      <div class="flex items-center gap-2.5 min-w-0">
        <div class="grid h-8 w-8 place-items-center rounded-lg border border-cyan-400/30 bg-cyan-400/10 text-cyan-300 text-sm shadow-inner shrink-0">
          <RadioTower :size="16" />
        </div>
        <div class="min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <h2 class="text-xs md:text-sm font-bold text-white tracking-wide whitespace-nowrap">
              现场 IoT 智能传感监测网
            </h2>
            <span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-semibold bg-cyan-950/70 text-cyan-300 border border-cyan-800/60 whitespace-nowrap">
              8 测点实时物联遥测
            </span>
          </div>
          <p class="text-[10px] text-slate-400 mt-0.5 whitespace-nowrap overflow-hidden text-ellipsis">
            温感 · 光电烟感 · 红外火焰 · 激光净宽 · 有毒可燃气体多源传感矩阵
          </p>
        </div>
      </div>

      <!-- 快速状态统计胶囊 (防止异常换行) -->
      <div class="flex items-center gap-1.5 text-[10px] font-mono shrink-0 whitespace-nowrap">
        <span class="px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 flex items-center gap-1">
          <i class="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0"></i>
          正常: {{ store.normalSensorsCount }}
        </span>
        <span
          v-if="store.warningSensorsCount > 0"
          class="px-2 py-0.5 rounded-full bg-amber-950/60 border border-amber-800/60 text-amber-300 flex items-center gap-1"
        >
          <i class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse shrink-0"></i>
          警戒: {{ store.warningSensorsCount }}
        </span>
        <span
          v-if="store.alarmingSensorsCount > 0"
          class="px-2 py-0.5 rounded-full bg-rose-950/80 border border-rose-600/80 text-rose-300 flex items-center gap-1 shadow-glow-red animate-pulse"
        >
          <i class="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping shrink-0"></i>
          告警/阻断: {{ store.alarmingSensorsCount }}
        </span>
      </div>
    </div>

    <!-- 突发告警浮动横幅 -->
    <div
      v-if="store.alarmingSensorsCount > 0"
      class="mb-3 px-3 py-1.5 rounded-xl bg-gradient-to-r from-rose-950/80 via-rose-900/40 to-slate-900/80 border border-rose-600/70 text-[10px] text-rose-200 flex items-center justify-between gap-2 shadow-glow-red animate-pulse"
    >
      <div class="flex items-center gap-2 min-w-0">
        <TriangleAlert class="shrink-0" :size="14" />
        <span class="font-bold shrink-0">物理传感熔断触发：</span>
        <span class="truncate">关键测点物理量突破安全阈值极限，已自动激活云台追踪与智能决策中枢！</span>
      </div>
      <span class="font-mono text-[9px] px-2 py-0.5 rounded bg-rose-900/80 text-rose-100 uppercase tracking-wider font-bold shrink-0 whitespace-nowrap">
        INTERRUPT ACTIVE
      </span>
    </div>

    <!-- 过滤器切换标签 -->
    <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5">
      <div class="flex items-center gap-1 text-[10px]">
        <button
          v-for="filter in filters"
          :key="filter.key"
          @click="currentFilter = filter.key"
          class="px-2 py-1 rounded-lg border transition font-medium whitespace-nowrap"
          :class="currentFilter === filter.key ? 'bg-cyan-400/15 border-cyan-400/40 text-cyan-200' : 'bg-slate-950/50 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900'"
        >
          {{ filter.label }}
        </button>
      </div>

      <div class="text-[9px] text-slate-500 font-mono flex items-center gap-1 shrink-0 whitespace-nowrap">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping shrink-0"></span>
        <span>采样率: 100ms · 现场总线在线</span>
      </div>
    </div>

    <!-- 传感器卡片响应式网格 (防止列宽压缩引起异常换行) -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5">
      <div
        v-for="s in filteredSensors"
        :key="s.id"
        class="rounded-xl p-2.5 border transition-all duration-300 flex flex-col justify-between min-w-0"
        :class="getSensorCardClass(s)"
      >
        <!-- 卡片头部：图标、名称、状态 Badge -->
        <div class="flex items-start justify-between gap-1 mb-1.5 min-w-0">
          <div class="flex items-center gap-1.5 min-w-0 flex-1">
            <component :is="getSensorIcon(s.type)" class="shrink-0 text-cyan-300" :size="15" />
            <div class="min-w-0 flex-1">
              <div class="text-[11px] font-bold text-slate-100 leading-tight truncate" :title="s.name">
                {{ s.name }}
              </div>
              <div class="text-[9px] text-slate-400 font-mono mt-0.5 truncate" :title="`${s.id} · ${s.node_name}`">
                {{ s.id }} · {{ s.node_name }}
              </div>
            </div>
          </div>

          <span
            class="px-1.5 py-0.5 rounded text-[8px] font-bold font-mono tracking-wide border shrink-0 whitespace-nowrap"
            :class="getStatusBadgeClass(s.status)"
          >
            {{ s.status_text }}
          </span>
        </div>

        <!-- 卡片主体：实时数值与阈值对比 (彻底杜绝异常换行) -->
        <div class="my-1.5 bg-slate-950/60 rounded-lg p-2 border border-slate-800/80 min-w-0">
          <div class="flex items-baseline justify-between mb-1 gap-1">
            <div class="flex items-baseline gap-1 shrink-0 whitespace-nowrap">
              <span class="font-mono text-base md:text-lg font-black tracking-tight" :class="getValueColorClass(s.status)">
                {{ s.current_value }}
              </span>
              <span class="text-[10px] font-mono text-slate-400 font-bold">
                {{ s.unit }}
              </span>
            </div>

            <div class="text-[9px] font-mono text-slate-400 text-right shrink-0 whitespace-nowrap">
              <span class="text-slate-500">{{ s.threshold_operator === '>' ? '报警线' : '下限' }}:</span>
              <span class="text-slate-300 font-semibold ml-0.5">
                {{ s.threshold_operator }}{{ s.threshold }}{{ s.unit }}
              </span>
            </div>
          </div>

          <!-- 迷你动态进度条 -->
          <div class="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="getProgressBarClass(s)"
              :style="{ width: `${getGaugePercentage(s)}%` }"
            ></div>
          </div>
        </div>

        <!-- 卡片底部说明 -->
        <div class="text-[9px] leading-snug flex items-center justify-between text-slate-400 min-w-0 pt-0.5">
          <span class="truncate flex-1 min-w-0 mr-1" :title="getSensorNote(s)">{{ getSensorNote(s) }}</span>
          <span v-if="s.status === 'ALARM' || s.status === 'BLOCKED'" class="text-rose-400 font-bold text-[8px] animate-pulse shrink-0 whitespace-nowrap">
            越限
          </span>
          <span v-else class="text-emerald-400 font-medium text-[8px] shrink-0 whitespace-nowrap">
            ✓ 正常
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useEmergencyStore } from '@/stores/emergencyStore';
import type { SensorItem } from '@/types/emergency';
import { RadioTower, TriangleAlert, Wind, Thermometer, Flame, Ruler, Biohazard } from 'lucide-vue-next';

const store = useEmergencyStore();

const currentFilter = ref<'all' | 'fire' | 'passage' | 'alarm'>('all');

const filters = [
  { key: 'all', label: '全部测点 (8)' },
  { key: 'fire', label: '火灾监测' },
  { key: 'passage', label: '通道监测' },
  { key: 'alarm', label: '异常' },
] as const;

const filteredSensors = computed(() => {
  const all = store.sensors || [];
  if (currentFilter.value === 'fire') {
    return all.filter(s => s.type === 'smoke' || s.type === 'temp_c' || s.type === 'flame');
  }
  if (currentFilter.value === 'passage') {
    return all.filter(s => s.type === 'width_m' || s.type === 'co_ppm');
  }
  if (currentFilter.value === 'alarm') {
    return all.filter(s => s.status !== 'NORMAL');
  }
  return all;
});

function getSensorIcon(type: string) {
  switch (type) {
    case 'smoke': return Wind;
    case 'temp_c': return Thermometer;
    case 'flame': return Flame;
    case 'width_m': return Ruler;
    case 'co_ppm': return Biohazard;
    default: return RadioTower;
  }
}

function getSensorCardClass(s: SensorItem): string {
  if (s.status === 'ALARM' || s.status === 'BLOCKED') {
    return 'bg-rose-950/25 border-rose-600/70 shadow-[0_0_15px_rgba(244,63,94,0.18)] ring-1 ring-rose-500/30';
  }
  if (s.status === 'WARNING') {
    return 'bg-amber-950/20 border-amber-500/60 shadow-[0_0_12px_rgba(245,158,11,0.12)]';
  }
  return 'bg-slate-900/70 border-slate-800/80 hover:border-slate-700/90';
}

function getStatusBadgeClass(status: string): string {
  switch (status) {
    case 'ALARM':
      return 'bg-rose-950 text-rose-200 border-rose-600 animate-pulse';
    case 'BLOCKED':
      return 'bg-rose-950 text-rose-200 border-rose-600 animate-pulse';
    case 'WARNING':
      return 'bg-amber-950 text-amber-200 border-amber-600';
    case 'NORMAL':
    default:
      return 'bg-emerald-950/80 text-emerald-300 border-emerald-700';
  }
}

function getValueColorClass(status: string): string {
  switch (status) {
    case 'ALARM':
    case 'BLOCKED':
      return 'text-rose-400 drop-shadow-[0_0_8px_rgba(244,63,94,0.5)]';
    case 'WARNING':
      return 'text-amber-300 drop-shadow-[0_0_8px_rgba(245,158,11,0.4)]';
    case 'NORMAL':
    default:
      return 'text-emerald-300';
  }
}

function getGaugePercentage(s: SensorItem): number {
  if (s.type === 'width_m') {
    const pct = Math.min(100, Math.max(10, (s.current_value / 1.6) * 100));
    return Math.round(pct);
  }
  if (s.threshold_operator === '>') {
    const pct = Math.min(100, Math.max(5, (s.current_value / (s.threshold * 1.5)) * 100));
    return Math.round(pct);
  }
  return 50;
}

function getProgressBarClass(s: SensorItem): string {
  if (s.status === 'ALARM' || s.status === 'BLOCKED') {
    return 'bg-gradient-to-r from-rose-500 to-red-600 animate-pulse';
  }
  if (s.status === 'WARNING') {
    return 'bg-gradient-to-r from-amber-400 to-amber-500';
  }
  return 'bg-gradient-to-r from-emerald-500 to-cyan-500';
}

function getSensorNote(s: SensorItem): string {
  if (s.id === 'S_SMOKE_EAST' && s.status === 'ALARM') return '配电箱引燃浓烟爆表 (+700%)';
  if (s.id === 'S_TEMP_EAST' && s.status === 'ALARM') return '明火辐射剧烈过火 (+60.9%)';
  if (s.id === 'S_FLAME_REBAR' && s.status === 'ALARM') return '检出持续明火电弧 (极高危)';
  if (s.id === 'S_WIDTH_WEST' && s.status === 'BLOCKED') return '模板侧翻坍塌 (低于通行净宽极限)';
  if (s.id === 'S_SMOKE_CORE' && s.status === 'WARNING') return '核心筒竖向烟囱效应扩散';
  if (s.status === 'NORMAL') return '测点读数符合安全标准';
  return '运行正常';
}
</script>
