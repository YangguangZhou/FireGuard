<template>
  <div class="panel-glass rounded-xl p-3 flex flex-col">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between pb-1.5 mb-2 border-b border-cyberBorder/60">
      <h2 class="panel-section-title flex items-center gap-1.5">
        <div class="icon-box-cyan">
          <Camera :size="14" />
        </div>
        <span>现场监控实时视频抓拍</span>
      </h2>
      <span class="badge-mono bg-slate-900 text-slate-400 border border-slate-800">
        {{ store.perception?.camera_id || 'CAM-01 (全域高清轮巡)' }}
      </span>
    </div>

    <!-- 视频抓拍图像显示区 -->
    <div class="relative w-full rounded-lg overflow-hidden border border-cyberBorder bg-slate-950 min-h-[145px] flex items-center justify-center hud-bracket">
      <!-- 扫描线效果 -->
      <div class="scan-overlay absolute inset-0 pointer-events-none z-10"></div>
      
      <img
        v-if="store.perception?.image_url"
        :src="store.perception.image_url"
        alt="CCTV Snapshot"
        class="w-full h-auto object-cover max-h-[160px] transition-all duration-500 relative z-0"
      />
      <div v-else class="text-center p-4 text-slate-500 text-xs relative z-0">
        <Camera class="mx-auto mb-1 opacity-60 glow-pulse" :size="22" />
        <div class="text-[11px] text-slate-400 tracking-wider">监控摄像头常态巡检中</div>
        <div class="text-[9px] text-slate-500 mt-0.5">全域各测点未检出异常明火或占道</div>
      </div>

      <!-- 视觉识别浮动角标 -->
      <div
        v-if="store.perception?.fire_detected"
        class="absolute top-2 left-2 bg-rose-900/90 text-rose-300 text-[9px] px-2 py-0.5 rounded font-mono font-bold shadow-glow-red border border-rose-500/50 animate-pulse flex items-center gap-1 z-20"
      >
        <Flame :size="12" />
        <span>FLAME_DETECTED: 96.2%</span>
      </div>

      <div
        v-if="store.perception?.structural_obstacle"
        class="absolute top-2 left-2 bg-amber-900/90 text-amber-300 text-[9px] px-2 py-0.5 rounded font-mono font-bold shadow-glow-amber border border-amber-500/50 animate-pulse flex items-center gap-1 z-20"
      >
        <TriangleAlert :size="12" />
        <span>COLLAPSED_OBSTACLE: 94.0%</span>
      </div>
    </div>

    <!-- 智能视觉研判简报 -->
    <div class="mt-2.5 bg-cyberPanelSoft p-2.5 rounded-lg border border-cyberBorder/50 shadow-inner-glow">
      <div class="text-cyan-400 font-semibold mb-1.5 flex items-center justify-between text-[10px]">
        <span class="flex items-center gap-1.5 tracking-wider uppercase">
          <ScanEye :size="13" />
          <span>智能视觉研判</span>
        </span>
        <span
          class="badge-mono font-bold shadow-sm"
          :class="getHazardBadgeClass(store.perception?.hazard_level)"
        >
          {{ store.perception?.hazard_level || 'NORMAL' }}
        </span>
      </div>
      <p class="text-slate-300 text-[10px] leading-relaxed font-sans tracking-wide">
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
  if (level === 'CRITICAL' || level === '极高危') return 'bg-rose-950 text-rose-300 border border-rose-800 shadow-glow-red';
  if (level === 'HIGH' || level === '高风险') return 'bg-amber-950 text-amber-300 border border-amber-800 shadow-glow-amber';
  return 'bg-emerald-950 text-emerald-300 border border-emerald-800 shadow-glow-green';
}
</script>
