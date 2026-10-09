<template>
  <div class="app-shell min-h-screen text-slate-100 flex flex-col font-tech selection:bg-cyan-500 selection:text-slate-950">
    <!-- 顶部统一导航栏 -->
    <TopNavbar />

    <!-- 主展示工作区 -->
    <main class="flex-1 p-4 md:p-5 flex flex-col gap-4 max-w-[1920px] w-full mx-auto">
      <div class="flex flex-wrap items-end justify-between gap-3 px-1">
        <div>
          <div class="mb-1 text-[10px] font-semibold uppercase tracking-[.22em] text-cyan-300/75">FIREGUARD / OPERATIONS</div>
          <h1 class="text-lg font-semibold tracking-wide text-white md:text-xl">现场安全指挥</h1>
        </div>
        <div class="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/[.06] px-3 py-1.5 text-[10px] font-medium text-emerald-200">
          <span class="relative flex h-2 w-2"><span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50"></span><span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-400"></span></span>
          实时监测
        </div>
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
