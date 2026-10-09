<template>
  <div class="bg-cyberPanelSoft border border-cyberBorder rounded-xl p-3 flex flex-col shadow-glass">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between pb-1.5 mb-2 border-b border-cyberBorder/60">
      <h2 class="text-xs font-bold text-slate-100 flex items-center gap-1.5">
        <Camera :size="14" />
        <span>现场监控实时视频抓拍</span>
      </h2>
      <span class="text-[9px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 font-mono border border-slate-800">
        {{ store.perception?.camera_id || 'CAM-01 (全域高清轮巡)' }}
      </span>
    </div>

    <!-- 视频抓拍图像显示区 -->
    <div class="relative w-full rounded-lg overflow-hidden border border-slate-800 bg-slate-950 min-h-[145px] flex items-center justify-center">
      <img
        v-if="store.perception?.image_url"
        :src="store.perception.image_url"
        alt="CCTV Snapshot"
        class="w-full h-auto object-cover max-h-[160px] transition-all duration-500"
      />
      <div v-else class="text-center p-4 text-slate-500 text-xs">
        <Camera class="mx-auto mb-1 opacity-60" :size="22" />
        <div class="text-[11px] text-slate-400">监控摄像头常态巡检中</div>
        <div class="text-[9px] text-slate-500 mt-0.5">全域各测点未检出异常明火或占道</div>
      </div>

      <!-- 视觉识别浮动角标 -->
      <div
        v-if="store.perception?.fire_detected"
        class="absolute top-2 left-2 bg-rose-600/95 text-white text-[9px] px-2 py-0.5 rounded font-mono font-bold shadow-glow-red animate-pulse flex items-center gap-1"
      >
        <Flame :size="12" />
        <span>FLAME_DETECTED: 96.2%</span>
      </div>

      <div
        v-if="store.perception?.structural_obstacle"
        class="absolute top-2 left-2 bg-amber-600/95 text-white text-[9px] px-2 py-0.5 rounded font-mono font-bold shadow animate-pulse flex items-center gap-1"
      >
        <TriangleAlert :size="12" />
        <span>COLLAPSED_OBSTACLE: 94.0%</span>
      </div>
    </div>

    <!-- qwen3-vl-flash 视觉研判简报 -->
    <div class="mt-2.5 bg-slate-950/90 p-2 rounded-lg border border-slate-800/80 text-[10px]">
      <div class="text-cyan-400 font-semibold mb-1 flex items-center justify-between">
        <span class="flex items-center gap-1">
          <ScanEye :size="13" />
          <span>qwen3-vl-flash 研判:</span>
        </span>
        <span
          class="font-mono px-1.5 py-0.2 rounded text-[9px] font-bold"
          :class="getHazardBadgeClass(store.perception?.hazard_level)"
        >
          {{ store.perception?.hazard_level || 'NORMAL' }}
        </span>
      </div>
      <p class="text-slate-300 leading-relaxed font-sans">
        {{ store.perception?.agent_perception_summary || '系统运行平稳，全作业面未检出火情或通道坍塌障碍。' }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEmergencyStore } from '@/stores/emergencyStore';
import { Camera, Flame, TriangleAlert, ScanEye } from 'lucide-vue-next';

const store = useEmergencyStore();

function getHazardBadgeClass(level?: string) {
  if (level === 'CRITICAL' || level === '极高危') return 'bg-rose-950 text-rose-300 border border-rose-800';
  if (level === 'HIGH' || level === '高风险') return 'bg-amber-950 text-amber-300 border border-amber-800';
  return 'bg-emerald-950 text-emerald-300 border border-emerald-800';
}
</script>
