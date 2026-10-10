<template>
  <div class="panel-glass bg-cyberPanelSoft border-cyberBorder rounded-xl p-3 flex flex-col shadow-glass h-full relative overflow-hidden">
    <!-- 面板标题 -->
    <div class="flex items-center justify-between pb-2 mb-2 border-b border-cyberBorder/60 relative">
      <h2 class="panel-section-title text-xs font-bold text-slate-100 flex items-center gap-2">
        <div class="icon-box-cyan">
          <Users :size="14" />
        </div>
        <span class="tracking-widest uppercase">现场工友智能终端调度</span>
      </h2>
      <span class="badge-mono px-1.5 py-0.5 rounded bg-blue-950/70 text-cyan-300 border border-cyan-800/60 shadow-glow-blue">
        智能语音调度引擎
      </span>
      <div class="absolute bottom-0 left-0 w-1/3 h-[1px] bg-gradient-to-r from-cyan-400/50 to-transparent"></div>
    </div>

    <!-- 工友卡片列表 -->
    <div class="flex-1 overflow-y-auto space-y-2 pr-1">
      <div
        v-for="w in store.workers"
        :key="w.id"
        class="bg-cyberPanelSoft/60 backdrop-blur-sm border rounded-lg p-2.5 transition-all shadow-glass-sm hover-lift relative"
        :class="getCardBorderClass(w.id)"
      >
        <div class="hud-bracket"></div>
        <!-- 头部：姓名、工种、终端、心率 -->
        <div class="flex justify-between items-start mb-2 relative z-10">
          <div>
            <div class="font-bold text-xs text-white flex items-center gap-1.5">
              <span class="text-shimmer">{{ w.name }}</span>
              <span class="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-normal uppercase tracking-wider">
                {{ w.role }}
              </span>
            </div>
            <div class="text-[10px] text-cyan-400/70 font-mono mt-0.5 flex items-center gap-1">
              <div class="w-1 h-1 rounded-full bg-cyan-400 glow-dot"></div>
              {{ w.device }}
            </div>
          </div>

          <div class="text-right">
            <span
              class="text-[11px] font-mono font-bold px-1.5 py-0.5 rounded flex items-center gap-1"
              :class="w.status === 'normal' ? 'bg-emerald-950/50 text-emerald-400 border border-emerald-800/50 shadow-glow-green' : 'bg-rose-950/50 text-rose-400 border border-rose-800/50 animate-pulse shadow-glow-red'"
            >
              <HeartPulse :size="12" />{{ w.heart_rate }} bpm
            </span>
          </div>
        </div>

        <!-- 路径导引分配 -->
        <div class="bg-gradient-to-r from-slate-900/90 to-slate-800/40 rounded p-1.5 text-[11px] border border-slate-700/50 mb-2 divide-y divide-slate-700/50 shadow-inner-glow relative z-10">
          <div class="flex justify-between text-slate-400 pb-1 mb-1">
            <span class="uppercase tracking-wider text-[9px]">分配出口</span>
            <span class="text-cyan-400 font-semibold tracking-wide">
              {{ store.currentAct === 'ACT_1_NORMAL' ? '巡查待命' : (getRoute(w.id)?.exit_name || '安全避难区域') }}
            </span>
          </div>
          <div class="flex justify-between text-slate-400 text-[10px] pt-1">
            <span class="uppercase tracking-wider text-[9px]">疏散距离 / 耗时</span>
            <span class="text-amber-400 font-mono shadow-glow-amber text-xs">
              {{ store.currentAct === 'ACT_1_NORMAL' ? '常态在岗 · 随时受控待命' : `${getRoute(w.id)?.distance_m}m (约 ${getRoute(w.id)?.est_time_sec}s)` }}
            </span>
          </div>
        </div>

        <!-- 骨传导语音播报与物理音频播放 -->
        <div class="text-[10px] bg-slate-900/60 rounded p-2 text-slate-300 relative overflow-hidden shadow-inner-glow z-10">
          <div class="absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b" :class="store.currentAct === 'ACT_1_NORMAL' ? 'from-emerald-400 to-emerald-900/20' : 'from-rose-400 to-rose-900/20'"></div>
          
          <div class="flex items-center justify-between text-slate-400 font-semibold mb-1.5 pl-1.5">
            <span class="flex items-center gap-1.5 text-cyan-300/80 uppercase tracking-widest text-[9px]">
              <AudioLines :size="12" />
              <span>骨传导语音指令</span>
            </span>

            <!-- 语音播放按钮 -->
            <button
              v-if="store.currentAct !== 'ACT_1_NORMAL'"
              @click="playAudio(w.id)"
              class="px-2 py-0.5 rounded bg-blue-900/70 hover:bg-blue-800 text-cyan-300 border border-cyan-500/40 text-[9px] flex items-center gap-1 shadow transition active:scale-95"
              :class="player.activeWorkerId.value === w.id && player.isPlaying.value ? 'glow-pulse ring-1 ring-cyan-400 shadow-glow-blue' : 'hover-lift'"
            >
              <span class="flex items-center gap-1"><Volume2 :size="11" />{{ player.activeWorkerId.value === w.id && player.isPlaying.value ? '播报中' : '播放语音' }}</span>
            </button>
            <span v-else class="text-emerald-400 text-[9px] badge-mono shadow-glow-green">常态待命</span>
          </div>

          <p class="leading-relaxed text-slate-200 font-sans pl-1.5">
            {{ getBroadcast(w.id)?.audio_script || '【日常安全巡查】当前作业区通道畅通合规，智能安全帽信道就绪。' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEmergencyStore } from '@/stores/emergencyStore';
import { useAudioPlayer } from '@/composables/useAudioPlayer';
import { Users, HeartPulse, AudioLines, Volume2 } from 'lucide-vue-next';

const store = useEmergencyStore();
const player = useAudioPlayer();

function getRoute(wId: string) {
  return store.routes.find(r => r.worker_id === wId);
}

function getBroadcast(wId: string) {
  return store.broadcasts.find(b => b.worker_id === wId);
}

function getCardBorderClass(wId: string) {
  const r = getRoute(wId);
  if (store.currentAct === 'ACT_1_NORMAL') {
    return 'border-slate-800/80 hover:border-slate-700';
  }
  if (r?.status === 'ROUTE_READY') {
    return 'border-cyan-900/60 hover:border-cyan-700/80';
  }
  return 'border-rose-900/80 bg-rose-950/20';
}

function playAudio(wId: string) {
  const b = getBroadcast(wId);
  if (b) {
    player.playWorkerVoice(wId, b.audio_url, b.audio_script);
  }
}
</script>
