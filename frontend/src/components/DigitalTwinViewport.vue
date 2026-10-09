<template>
  <section class="relative flex h-full min-h-[540px] flex-col overflow-hidden rounded-2xl border border-slate-700/70 bg-slate-900/75 p-3 shadow-glass backdrop-blur-xl md:p-4">
    <div class="mb-3 flex flex-wrap items-center justify-between gap-3 border-b border-slate-700/60 pb-3">
      <div class="flex items-center gap-3">
        <div class="grid h-10 w-10 place-items-center rounded-xl border border-cyan-300/20 bg-gradient-to-br from-cyan-400/20 to-blue-500/10 text-cyan-200 shadow-inner">⌂</div>
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <h2 class="text-sm font-bold tracking-wide text-white md:text-base">3F 施工现场 · 数字孪生</h2>
            <span class="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-0.5 text-[9px] font-semibold tracking-wide text-cyan-200">LIVE MODEL</span>
          </div>
          <p class="mt-0.5 text-[10px] text-slate-400">楼层结构、人员位置与动态疏散路径</p>
        </div>
      </div>

      <div class="flex items-center gap-1 rounded-xl border border-slate-700/80 bg-slate-950/65 p-1">
        <button v-for="view in views" :key="view.key" @click="selectView(view.key)" :class="activeView === view.key ? 'border-cyan-300/30 bg-cyan-300/10 text-cyan-100' : 'border-transparent text-slate-400 hover:bg-white/5 hover:text-white'" class="rounded-lg border px-2.5 py-1.5 text-[9px] font-semibold transition md:text-[10px]">
          {{ view.label }}
        </button>
      </div>
    </div>

    <div class="relative min-h-[460px] flex-1 overflow-hidden rounded-xl border border-slate-700/70 bg-[#07111f]">
      <div class="pointer-events-none absolute inset-0 z-[1] bg-[radial-gradient(ellipse_at_50%_45%,rgba(14,116,144,.11),transparent_65%)]"></div>
      <div ref="containerRef" class="absolute inset-0"></div>

      <!-- Orientation + legend make the 3D scene legible without relying on color alone. -->
      <div class="pointer-events-none absolute left-3 top-3 z-[2] flex items-start gap-2">
        <div class="rounded-xl border border-slate-700/80 bg-slate-950/75 px-3 py-2.5 shadow-lg backdrop-blur-md">
          <div class="text-[9px] font-bold uppercase tracking-[.18em] text-slate-500">楼层图例</div>
          <div class="mt-2 grid grid-cols-2 gap-x-3 gap-y-1.5 text-[9px] text-slate-300">
            <span class="flex items-center gap-1.5"><i class="h-2 w-2 rounded-sm bg-sky-300"></i>施工通道</span>
            <span class="flex items-center gap-1.5"><i class="h-2 w-2 rounded-sm bg-amber-400"></i>作业区域</span>
            <span class="flex items-center gap-1.5"><i class="h-2 w-2 rounded-full bg-cyan-300"></i>现场人员</span>
            <span class="flex items-center gap-1.5"><i class="h-2 w-2 rounded-full bg-emerald-400"></i>安全出口</span>
            <span class="flex items-center gap-1.5"><i class="h-2 w-2 rounded-sm bg-rose-400"></i>危险区域</span>
            <span class="flex items-center gap-1.5"><i class="h-[3px] w-3 rounded-full bg-emerald-300"></i>疏散方向</span>
            <span class="flex items-center gap-1.5 col-span-2 text-rose-300"><i class="h-2 w-2 rounded-full bg-rose-500 animate-pulse"></i>IoT 告警测点</span>
          </div>
        </div>
      </div>

      <div class="pointer-events-none absolute right-3 top-3 z-[2] flex h-[58px] w-[58px] flex-col items-center justify-center rounded-full border border-slate-600/80 bg-slate-950/75 shadow-lg backdrop-blur-md">
        <span class="text-[9px] font-black text-cyan-200">N</span>
        <span class="-mt-0.5 text-[15px] leading-none text-cyan-300">↑</span>
        <span class="text-[7px] tracking-widest text-slate-500">北向</span>
      </div>

      <div class="pointer-events-none absolute bottom-3 left-3 right-3 z-[2] flex flex-wrap items-end justify-between gap-2">
        <div class="max-w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2.5 shadow-lg backdrop-blur-md">
          <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
            <span class="flex items-center gap-1.5 text-[10px] font-bold" :class="hudStatusColor"><i class="h-1.5 w-1.5 animate-pulse rounded-full bg-current"></i>{{ hudStatusText }}</span>
            <span class="hidden h-3 w-px bg-slate-700 sm:block"></span>
            <span class="text-[9px] text-slate-400">{{ store.currentAct === 'ACT_1_NORMAL' ? '路线计算待命' : `A* 路径已生成 · ${store.routes.length} 组人员` }}</span>
            <span v-if="store.alarmingSensorsCount > 0" class="text-[9px] px-1.5 py-0.2 rounded bg-rose-950/80 text-rose-300 border border-rose-700/80 font-mono animate-pulse flex items-center gap-1">
              <TriangleAlert :size="12" />{{ store.alarmingSensorsCount }} 测点越限
            </span>
          </div>
        </div>
        <div class="rounded-lg border border-slate-700/70 bg-slate-950/65 px-2.5 py-1.5 text-[9px] text-slate-400 backdrop-blur-md">
          拖动旋转 <span class="mx-1 text-slate-600">·</span> 滚轮缩放 <span class="mx-1 text-slate-600">·</span> 右键平移
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { useEmergencyStore } from '@/stores/emergencyStore';
import { useThreeDigitalTwin } from '@/composables/useThreeDigitalTwin';
import { TriangleAlert } from 'lucide-vue-next';

type CameraView = 'iso' | 'fire' | 'exitB';
const store = useEmergencyStore();
const twin = useThreeDigitalTwin();
const containerRef = ref<HTMLElement | null>(null);
const activeView = ref<CameraView>('iso');
const views: { key: CameraView; label: string }[] = [
  { key: 'iso', label: '全层鸟瞰' },
  { key: 'fire', label: '火情位置' },
  { key: 'exitB', label: '西侧出口' },
];

let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  if (!containerRef.value) return;
  twin.init(containerRef.value);
  twin.updateScene(store.currentAct, store.nodes, store.workers, store.routes, store.sensors);
  resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) twin.handleResize(entry.contentRect.width, entry.contentRect.height);
  });
  resizeObserver.observe(containerRef.value);
});

onUnmounted(() => {
  resizeObserver?.disconnect();
  twin.destroy();
});

watch(
  [() => store.currentAct, () => store.nodes, () => store.workers, () => store.routes, () => store.sensors],
  () => twin.updateScene(store.currentAct, store.nodes, store.workers, store.routes, store.sensors),
  { deep: true }
);

function selectView(view: CameraView) {
  activeView.value = view;
  twin.setCameraPreset(view);
}

const hudStatusText = computed(() => {
  switch (store.currentAct) {
    case 'ACT_1_NORMAL': return '常态巡检 · 通道畅通';
    case 'ACT_2_FIRE': return '火情响应 · 人员沿安全路线撤离';
    case 'ACT_3_BLOCKAGE': return '通道受阻 · 路线已重新规划';
    default: return '现场态势巡检中';
  }
});

const hudStatusColor = computed(() => {
  switch (store.currentAct) {
    case 'ACT_1_NORMAL': return 'text-emerald-300';
    case 'ACT_2_FIRE': return 'text-rose-300';
    case 'ACT_3_BLOCKAGE': return 'text-amber-300';
    default: return 'text-slate-300';
  }
});
</script>
