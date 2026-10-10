<template>
  <div class="app-shell min-h-screen text-slate-100 flex flex-col font-tech selection:bg-cyan-500 selection:text-slate-950 relative">
    <!-- Animated Grid Overlay Background -->
    <div class="fixed inset-0 pointer-events-none opacity-[0.04] bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] z-[-1]"></div>
    <div class="fixed inset-0 pointer-events-none bg-gradient-to-b from-slate-950 via-slate-900/95 to-slate-950 -z-20"></div>

    <!-- 顶部统一导航栏 -->
    <TopNavbar />

    <!-- 主展示工作区 -->
    <main class="flex-1 p-4 md:p-5 flex flex-col gap-4 max-w-[1920px] w-full mx-auto relative z-10">
      
      <!-- Header Section -->
      <div class="flex flex-wrap items-end justify-between gap-4 px-2 py-1 mb-1 border-l-4 border-cyan-500/50 pl-4 bg-gradient-to-r from-cyan-900/20 to-transparent rounded-r-lg">
        <div>
          <div class="mb-1.5 text-[11px] font-bold uppercase tracking-[.25em] text-cyan-400/80">FIREGUARD <span class="mx-1 opacity-50">/</span> OPERATIONS</div>
          <h1 class="text-xl font-bold tracking-widest text-white md:text-2xl text-shimmer">现场安全指挥</h1>
        </div>
        <div class="flex items-center gap-2.5 rounded-full border border-emerald-400/30 bg-emerald-950/40 px-4 py-2 text-xs font-bold tracking-wider text-emerald-300 shadow-glow-green backdrop-blur-sm">
          <span class="relative flex h-2 w-2">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60"></span>
            <span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-400 glow-dot"></span>
          </span>
          实时监测
        </div>
      </div>
      
      <!-- Decorative Divider -->
      <div class="w-full h-px bg-gradient-to-r from-cyan-500/0 via-cyan-500/20 to-cyan-500/0 mb-2 relative">
        <div class="absolute left-1/4 top-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-[2px] bg-cyan-400/40 blur-[1px]"></div>
      </div>

      <!-- 演练推演顺序时间轴控制器 -->
      <DrillTimeline />

      <!-- 三栏响应式大屏网格系统 (3列 - 6列 - 3列) -->
      <div class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-[660px]">
        <!-- 左侧栏：现场工友调度与规范审查 (3列) -->
        <div class="lg:col-span-3 flex flex-col gap-3">
          <WorkerDispatchPanel class="flex-1" />
          <ComplianceAuditCard class="shrink-0" />
        </div>

        <!-- 中间栏：3D 施工作业层数字孪生驾驶舱与 IoT 传感网络 (6列) -->
        <div class="lg:col-span-6 flex flex-col gap-3">
          <DigitalTwinViewport class="flex-1 min-h-[480px]" />
          <SensorMonitoringPanel class="shrink-0" />
        </div>

        <!-- 右侧栏：监控抓拍、Copilot 智能问答与决策日志流 (3列) -->
        <div class="lg:col-span-3 flex flex-col gap-3">
          <CCTVSurveillanceCard class="shrink-0" />
          <SafetyDirectorCopilot class="shrink-0" />
          <AgentLogStream class="flex-1" />
        </div>
      </div>
    </main>

    <!-- 应急处置记录单弹窗 -->
    <FormalReportModal />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useEmergencyStore } from '@/stores/emergencyStore';

import TopNavbar from '@/components/TopNavbar.vue';
import DrillTimeline from '@/components/DrillTimeline.vue';
import DigitalTwinViewport from '@/components/DigitalTwinViewport.vue';
import SensorMonitoringPanel from '@/components/SensorMonitoringPanel.vue';
import WorkerDispatchPanel from '@/components/WorkerDispatchPanel.vue';
import CCTVSurveillanceCard from '@/components/CCTVSurveillanceCard.vue';
import SafetyDirectorCopilot from '@/components/SafetyDirectorCopilot.vue';
import ComplianceAuditCard from '@/components/ComplianceAuditCard.vue';
import AgentLogStream from '@/components/AgentLogStream.vue';
import FormalReportModal from '@/components/FormalReportModal.vue';

const store = useEmergencyStore();

onMounted(() => {
  store.fetchState();
});
</script>
