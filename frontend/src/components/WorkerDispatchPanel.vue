<template>
  <div class="bg-cyberPanelSoft border border-cyberBorder rounded-xl p-3 flex flex-col shadow-glass h-full">
    <!-- 面板标题 -->
    <div class="flex items-center justify-between pb-2 mb-2 border-b border-cyberBorder/60">
      <h2 class="text-xs font-bold text-slate-100 flex items-center gap-1.5">
        <Users :size="14" />
        <span>现场工友智能终端调度</span>
      </h2>
      <span class="text-[9px] px-1.5 py-0.5 rounded bg-blue-950/70 text-cyan-300 border border-cyan-800/60 font-mono">
        qwen3.8-flash 方言语音引擎
      </span>
    </div>

    <!-- 工友卡片列表 -->
    <div class="flex-1 overflow-y-auto space-y-2 pr-1">
      <div
        v-for="w in store.workers"
        :key="w.id"
        class="bg-slate-900/90 border rounded-lg p-2.5 transition-all shadow-sm"
        :class="getCardBorderClass(w.id)"
      >
        <!-- 头部：姓名、工种、方言、心率 -->
        <div class="flex justify-between items-start mb-1.5">
          <div>
            <div class="font-bold text-xs text-white flex items-center gap-1.5">
              <span>{{ w.name }}</span>
              <span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-normal">
                {{ w.role }}
              </span>
              <span class="text-[9px] px-1 py-0.2 rounded bg-amber-950/70 text-amber-300 border border-amber-800/60">
                {{ getDialectTag(w.id) }}
              </span>
            </div>
            <div class="text-[10px] text-slate-400 font-mono mt-0.5">
              {{ w.device }}
            </div>
          </div>

          <div class="text-right">
            <span
              class="text-[11px] font-mono font-bold px-1.5 py-0.5 rounded"
              :class="w.status === 'normal' ? 'bg-emerald-950/50 text-emerald-400 border border-emerald-800/50' : 'bg-rose-950/50 text-rose-400 border border-rose-800/50 animate-pulse'"
            >
              <HeartPulse class="inline-block mr-1" :size="12" />{{ w.heart_rate }} bpm
            </span>
          </div>
        </div>

        <!-- 路径导引分配 -->
        <div class="bg-slate-950/80 rounded p-1.5 text-[11px] border border-slate-800/90 mb-1.5">
          <div class="flex justify-between text-slate-400 mb-0.5">
            <span>分配出口:</span>
            <span class="text-cyan-400 font-semibold">
              {{ store.currentAct === 'ACT_1_NORMAL' ? '🟢 现场巡查中 (通道畅通备用)' : (getRoute(w.id)?.exit_name || '安全避难区域') }}
            </span>
          </div>
          <div class="flex justify-between text-slate-400 text-[10px]">
            <span>疏散距离 / 耗时:</span>
            <span class="text-amber-300 font-mono">
              {{ store.currentAct === 'ACT_1_NORMAL' ? '常态在岗 · 随时受控待命' : `${getRoute(w.id)?.distance_m}m (约 ${getRoute(w.id)?.est_time_sec}s)` }}
            </span>
          </div>
        </div>

        <!-- 骨传导语音播报与物理音频播放 -->
        <div
          class="text-[10px] bg-slate-800/60 rounded p-2 text-slate-300 border-l-2"
          :class="store.currentAct === 'ACT_1_NORMAL' ? 'border-emerald-500' : 'border-rose-500'"
        >
          <div class="flex items-center justify-between text-slate-400 font-semibold mb-1">
            <span class="flex items-center gap-1">
              <AudioLines :size="12" />
              <span>骨传导语音指令:</span>
            </span>

            <!-- 语音播放按钮 -->
            <button
              v-if="store.currentAct !== 'ACT_1_NORMAL'"
              @click="playAudio(w.id)"
              class="px-2 py-0.5 rounded bg-blue-900/70 hover:bg-blue-800 text-cyan-300 border border-cyan-500/40 text-[9px] flex items-center gap-1 shadow transition active:scale-95"
              :class="player.activeWorkerId.value === w.id && player.isPlaying.value ? 'animate-pulse ring-1 ring-cyan-400' : ''"
            >
              <span><span class="flex items-center gap-1"><Volume2 :size="11" />{{ player.activeWorkerId.value === w.id && player.isPlaying.value ? '播报中' : '播放语音' }}</span></span>
            </button>
            <span v-else class="text-emerald-400 text-[9px]">常态待命</span>
          </div>

          <p class="leading-relaxed text-slate-200 font-sans">
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

function getDialectTag(wId: string) {
  if (wId === 'W01' || wId === 'W04') return '湖南方言';
  if (wId === 'W02') return '四川方言';
  return '标准普通话';
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
