<template>
  <div class="panel-glass rounded-2xl p-3 md:p-4 flex flex-col flex-1 min-h-[320px] shadow-glass relative overflow-hidden">
    <!-- 面板标题栏 -->
    <div class="flex flex-wrap items-center justify-between gap-2 pb-2.5 mb-2.5 border-b border-cyberBorder/60">
      <div class="flex items-center gap-2">
        <div class="icon-box-cyan grid h-8 w-8 place-items-center rounded-lg text-sm">
          <Workflow :size="16" />
        </div>
        <div>
          <h2 class="panel-section-title text-xs md:text-sm font-bold text-white flex items-center gap-1.5">
            <span>Agent 决策推演与事件处置时序链</span>
          </h2>
          <p class="panel-subtitle text-[10px] text-slate-400 mt-0.5">
            多源感知 ➔ 视觉研判 ➔ 规范隔离 ➔ 动态规划 ➔ 终端调度全流程追溯
          </p>
        </div>
      </div>

      <!-- 完成步数标识 -->
      <div class="flex items-center gap-2">
        <span class="glow-pulse text-[10px] font-mono px-2.5 py-1 rounded-full bg-slate-900 border border-slate-700/80 text-cyan-300 flex items-center gap-1.5 shadow-[0_0_8px_rgba(34,211,238,0.5)]">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
          <span>已完成 {{ store.logs.length }} 步处置</span>
        </span>
      </div>
    </div>

    <!-- 阶段过滤器切换 -->
    <div class="flex items-center justify-between gap-1 mb-2.5 text-[10px]">
      <div class="flex flex-wrap gap-1">
        <button
          v-for="f in logFilters"
          :key="f.key"
          @click="activeFilter = f.key"
          class="px-3 py-1 rounded-full border transition text-[9px] font-medium tracking-wide"
          :class="activeFilter === f.key ? 'bg-cyan-400/20 border-cyan-400/50 text-cyan-200 shadow-[0_0_8px_rgba(34,211,238,0.3)]' : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'"
        >
          {{ f.label }}
        </button>
      </div>

      <button
        @click="autoScroll = !autoScroll"
        class="text-[9px] font-mono px-3 py-1 rounded-full border transition tracking-wide"
        :class="autoScroll ? 'text-emerald-300 border-emerald-800/80 bg-emerald-950/40 shadow-[0_0_8px_rgba(52,211,153,0.2)]' : 'text-slate-500 border-slate-800 bg-slate-950'"
        title="点击切换自动滚屏"
      >
        {{ autoScroll ? '自动跟踪' : '暂停滚屏' }}
      </button>
    </div>

    <!-- 结构化处置时序链流列表 -->
    <div
      ref="logContainerRef"
      class="flex-1 overflow-y-auto space-y-3 pr-1.5 text-[10px] max-h-[380px] scrollbar-thin relative z-10"
    >
      <div
        v-for="(log, idx) in filteredLogs"
        :key="log.sequence_id || idx"
        class="relative pl-8 group transition-all"
      >
        <!-- 时序垂直连接线 -->
        <div
          v-if="idx < filteredLogs.length - 1"
          class="absolute left-3.5 top-7 bottom-[-16px] w-[2px] bg-gradient-to-b from-cyan-400 via-cyan-500/50 to-transparent group-hover:from-cyan-300 transition-colors"
        ></div>

        <!-- 步骤序号圆环指示器 -->
        <div
          class="absolute left-1 top-1.5 w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-mono font-bold shadow-[0_0_10px_currentColor] ring-2 ring-current/30"
          :class="getStepCircleClass(log)"
        >
          {{ String(log.sequence_id || (idx + 1)).padStart(2, '0') }}
        </div>

        <!-- 事件卡片实体 -->
        <div
          class="hover-lift p-3 rounded-xl border transition-all duration-300 shadow-sm"
          :class="getEventCardClass(log)"
        >
          <!-- 卡片顶栏：时钟戳、耗时偏差、阶段标签、等级 Badge -->
          <div class="flex flex-wrap items-center justify-between gap-1 mb-1.5 text-[9px]">
            <div class="flex items-center gap-1.5 font-mono">
              <span class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700/80 text-cyan-300 font-bold shadow-inner">
                {{ log.time_offset || `+${((log.sequence_id || 1) * 0.8).toFixed(1)}s` }}
              </span>
              <span class="text-slate-400 badge-mono">{{ log.timestamp }}</span>
            </div>

            <div class="flex items-center gap-1.5 font-mono">
              <span
                v-if="log.phase_name"
                class="px-2 py-0.5 rounded-full font-sans text-[8px] font-semibold bg-slate-900 text-slate-300 border border-slate-700 uppercase tracking-widest"
              >
                {{ log.phase_name }}
              </span>
              <span
                class="px-2 py-0.5 rounded-full text-[8px] font-bold font-mono tracking-widest border uppercase shadow-sm"
                :class="getLevelBadgeClass(log.level || 'INFO')"
              >
                {{ log.level || log.event_type }}
              </span>
            </div>
          </div>

          <!-- 事件标题 -->
          <div class="font-bold text-slate-100 text-[12px] mb-1.5 leading-snug flex items-center gap-1.5">
            <component :is="getEventIcon(log.event_type)" :size="14" class="shrink-0 text-cyan-300" />
            <span class="tracking-wide">{{ log.title || log.event_type }}</span>
          </div>

          <!-- 具体事件描述内容 -->
          <div class="text-slate-300 leading-relaxed font-sans text-[10.5px]">
            {{ log.message }}
          </div>

          <!-- 结构化元数据详情胶囊栏 (如果有 details) -->
          <div
            v-if="log.details && Object.keys(log.details).length > 0"
            class="mt-2.5 pt-2 border-t border-slate-700/50 flex flex-wrap gap-1.5 text-[9px]"
          >
            <span
              v-for="(val, key) in formatDetails(log.details)"
              :key="key"
              class="px-2.5 py-0.5 rounded-full bg-slate-950/80 border border-slate-700/80 text-slate-300 font-mono flex items-center gap-1.5 shadow-sm hover:border-cyan-500/40 transition-colors"
            >
              <span class="text-slate-500 font-medium uppercase tracking-wider">{{ key }}:</span>
              <span class="text-cyan-100 font-bold">{{ val }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { useEmergencyStore } from '@/stores/emergencyStore';
import type { IncidentLogItem } from '@/types/emergency';
import { Workflow, RadioTower, Camera, ScanEye, ShieldAlert, Route, Volume2, HardHat, Siren, Pin } from 'lucide-vue-next';

const store = useEmergencyStore();
const logContainerRef = ref<HTMLElement | null>(null);
const autoScroll = ref<boolean>(true);
const activeFilter = ref<'all' | 'sensing' | 'isolation' | 'planning' | 'dispatch'>('all');

const logFilters = [
  { key: 'all', label: '全部时序' },
  { key: 'sensing', label: '传感研判' },
  { key: 'isolation', label: '规范隔离' },
  { key: 'planning', label: '动态规划' },
  { key: 'dispatch', label: '终端调度' },
] as const;

const filteredLogs = computed(() => {
  const all = store.logs || [];
  if (activeFilter.value === 'sensing') {
    return all.filter(l => l.phase === 'SENSING' || l.phase === 'PERCEPTION' || l.event_type.includes('VLM') || l.event_type.includes('IOT') || l.event_type.includes('CCTV'));
  }
  if (activeFilter.value === 'isolation') {
    return all.filter(l => l.phase === 'ISOLATION' || l.event_type.includes('GB') || l.event_type.includes('ISOLATION'));
  }
  if (activeFilter.value === 'planning') {
    return all.filter(l => l.phase === 'PLANNING' || l.event_type.includes('A_STAR') || l.event_type.includes('REPLAN'));
  }
  if (activeFilter.value === 'dispatch') {
    return all.filter(l => l.phase === 'DISPATCH' || l.phase === 'RESCUE' || l.event_type.includes('TTS') || l.event_type.includes('VOICE') || l.event_type.includes('HELMET') || l.event_type.includes('RESCUE'));
  }
  return all;
});

function getEventIcon(eventType: string) {
  if (eventType.includes('IOT')) return RadioTower;
  if (eventType.includes('CCTV')) return Camera;
  if (eventType.includes('VLM')) return ScanEye;
  if (eventType.includes('ISOLATION') || eventType.includes('GB')) return ShieldAlert;
  if (eventType.includes('A_STAR') || eventType.includes('REPLAN')) return Route;
  if (eventType.includes('TTS') || eventType.includes('VOICE')) return Volume2;
  if (eventType.includes('HELMET') || eventType.includes('STANDBY')) return HardHat;
  if (eventType.includes('RESCUE')) return Siren;
  return Pin;
}

function getStepCircleClass(log: IncidentLogItem): string {
  if (log.level === 'CRITICAL') {
    return 'bg-rose-950 text-rose-300 border-rose-500 shadow-glow-red animate-pulse';
  }
  if (log.level === 'WARNING') {
    return 'bg-amber-950 text-amber-300 border-amber-500';
  }
  if (log.level === 'SUCCESS') {
    return 'bg-cyan-950 text-cyan-300 border-cyan-500';
  }
  return 'bg-slate-900 text-slate-300 border-slate-700';
}

function getEventCardClass(log: IncidentLogItem): string {
  if (log.level === 'CRITICAL') {
    return 'bg-rose-950/20 border-rose-800/80 hover:border-rose-600/90 shadow-[0_0_12px_rgba(244,63,94,0.12)]';
  }
  if (log.level === 'WARNING') {
    return 'bg-amber-950/15 border-amber-800/80 hover:border-amber-600/90';
  }
  if (log.level === 'SUCCESS') {
    return 'bg-cyan-950/20 border-cyan-800/80 hover:border-cyan-600/90';
  }
  return 'bg-slate-950/80 border-slate-800/80 hover:border-slate-700/80';
}

function getLevelBadgeClass(level: string): string {
  switch (level) {
    case 'CRITICAL':
      return 'bg-rose-950 text-rose-300 border-rose-700 animate-pulse';
    case 'WARNING':
      return 'bg-amber-950 text-amber-300 border-amber-700';
    case 'SUCCESS':
      return 'bg-emerald-950 text-emerald-300 border-emerald-700';
    case 'INFO':
    default:
      return 'bg-slate-900 text-slate-400 border-slate-800';
  }
}

function formatDetails(details: Record<string, any>): Record<string, string> {
  const result: Record<string, string> = {};
  const labels: Record<string, string> = {
    sensor_id: '测点',
    smoke_ppm: '烟雾',
    temp_c: '温度',
    flame_level: '火焰',
    reading_m: '实测净宽',
    threshold_limit_m: '强制下限',
    camera_id: '联动云台',
    model: '研判模型',
    confidence: '置信度',
    hazard_level: '危险评级',
    rule: '执行条款',
    blocked_exit: '切断出口',
    algorithm: '规划引擎',
    compute_time_ms: '寻优耗时',
    workers_tracked: '纳管人数',
    rescue_type: '特勤调度',
  };

  for (const [key, val] of Object.entries(details)) {
    if (val === undefined || val === null) continue;
    const label = labels[key] || key;
    let strVal = '';
    if (typeof val === 'object') {
      strVal = Array.isArray(val) ? val.join(', ') : JSON.stringify(val);
    } else {
      strVal = String(val);
    }
    result[label] = strVal;
  }
  return result;
}

watch(
  () => store.logs.length,
  async () => {
    if (!autoScroll.value) return;
    await nextTick();
    if (logContainerRef.value) {
      logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight;
    }
  }
);
</script>
