<template>
  <div class="bg-cyberPanelSoft border border-cyberBorder rounded-xl p-2.5 flex flex-col shadow-glass relative overflow-hidden h-full min-h-[540px]">
    <!-- 顶部状态栏与视口工具 -->
    <div class="flex items-center justify-between pb-2 mb-2 border-b border-cyberBorder/60">
      <div class="flex items-center gap-2">
        <h2 class="text-xs font-bold text-white flex items-center gap-1.5">
          <span class="text-cyan-400">🧊</span>
          <span>3F 现浇主体作业层 3D 数字孪生驾驶舱</span>
        </h2>
        <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-950/60 text-cyan-300 border border-cyan-800/60 font-mono hidden sm:inline-block">
          Three.js WebGL 引擎
        </span>
      </div>

      <!-- 视角切换预设 -->
      <div class="flex items-center gap-1.5 text-[10px]">
        <button
          @click="twin.setCameraPreset('iso')"
          class="px-2 py-1 rounded bg-slate-900/90 border border-slate-700/80 hover:border-cyan-500 text-slate-300 hover:text-white transition flex items-center gap-1"
        >
          <span>🎥</span> 全景鸟瞰
        </button>
        <button
          @click="twin.setCameraPreset('fire')"
          class="px-2 py-1 rounded bg-slate-900/90 border border-slate-700/80 hover:border-rose-500 text-slate-300 hover:text-white transition flex items-center gap-1"
        >
          <span>🔥</span> 火情特写
        </button>
        <button
          @click="twin.setCameraPreset('exitB')"
          class="px-2 py-1 rounded bg-slate-900/90 border border-slate-700/80 hover:border-emerald-500 text-slate-300 hover:text-white transition flex items-center gap-1"
        >
          <span>🚪</span> 西外架爬梯
        </button>
      </div>
    </div>

    <!-- 3D 渲染容器 -->
    <div class="flex-1 bg-slate-950 rounded-lg relative overflow-hidden border border-slate-800/90">
      <div ref="containerRef" class="w-full h-full absolute inset-0"></div>

      <!-- 操作指南浮层 -->
      <div class="absolute top-2.5 left-2.5 bg-slate-900/80 backdrop-blur border border-slate-800 rounded px-2.5 py-1 text-[9px] text-slate-400 pointer-events-none flex items-center gap-1">
        <span>🖱️</span>
        <span>鼠标左键旋转 · 滚轮自由缩放 · 右键平移</span>
      </div>

      <!-- 左下角浮动状态 HUD (随推演动态变化) -->
      <div class="absolute bottom-2.5 left-2.5 bg-slate-900/90 border border-slate-700/80 rounded-lg p-2.5 text-[10px] backdrop-blur flex items-center gap-3 shadow-glass">
        <div>
          <span class="text-slate-400">现场态势:</span>
          <span class="font-bold ml-1.5" :class="hudStatusColor">
            {{ hudStatusText }}
          </span>
        </div>
        <div class="h-3 w-px bg-slate-700"></div>
        <div>
          <span class="text-slate-400">加权 A* 寻优:</span>
          <span class="text-cyan-400 font-mono font-bold ml-1.5">
            {{ store.currentAct === 'ACT_1_NORMAL' ? '待命就绪' : '4.2 ms (全员分流)' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { useEmergencyStore } from '@/stores/emergencyStore';
import { useThreeDigitalTwin } from '@/composables/useThreeDigitalTwin';

const store = useEmergencyStore();
const twin = useThreeDigitalTwin();
const containerRef = ref<HTMLElement | null>(null);

let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  if (containerRef.value) {
    twin.init(containerRef.value);
    twin.updateScene(store.currentAct, store.nodes, store.workers, store.routes);

    resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        twin.handleResize(width, height);
      }
    });
    resizeObserver.observe(containerRef.value);
  }
});

onUnmounted(() => {
  resizeObserver?.disconnect();
  twin.destroy();
});

// 监听态势变化自动刷新 3D 渲染
watch(
  [() => store.currentAct, () => store.nodes, () => store.workers, () => store.routes],
  () => {
    twin.updateScene(store.currentAct, store.nodes, store.workers, store.routes);
  },
  { deep: true }
);

const hudStatusText = computed(() => {
  switch (store.currentAct) {
    case 'ACT_1_NORMAL':
      return '🟢 施工常态受控 · 通道合规畅通';
    case 'ACT_2_FIRE':
      return '🔥 突发火情 · 西爬梯B / 南避难平台C 绿色光流引导';
    case 'ACT_3_BLOCKAGE':
      return '🚧 次生坍塌 · 动态重规划转向南立面避难平台C';
    default:
      return '态势巡检中';
  }
});

const hudStatusColor = computed(() => {
  switch (store.currentAct) {
    case 'ACT_1_NORMAL': return 'text-emerald-400';
    case 'ACT_2_FIRE': return 'text-rose-400';
    case 'ACT_3_BLOCKAGE': return 'text-amber-400';
    default: return 'text-slate-300';
  }
});
</script>
