<template>
  <div class="app-shell min-h-screen text-slate-100 flex flex-col font-tech selection:bg-cyan-500 selection:text-slate-950">
    <!-- 顶部统一导航栏 -->
    <TopNavbar />

    <!-- 主展示工作区 -->
    <main class="flex-1 p-4 md:p-5 flex flex-col gap-4 max-w-[1920px] w-full mx-auto">
      <!-- 演练推演顺序时间轴控制器 -->
      <DrillTimeline />

      <!-- 三栏响应式大屏网格系统 (3列 - 6列 - 3列) -->
      <div class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-[660px]">
        <!-- 左侧栏：现场工友调度与规范审查 (3列) -->
        <div class="lg:col-span-3 flex flex-col gap-3">
          <WorkerDispatchPanel class="flex-1" />
          <ComplianceAuditCard class="shrink-0" />
        </div>

        <!-- 中间栏：3D 施工作业层数字孪生驾驶舱 (6列) -->
        <div class="lg:col-span-6 flex flex-col">
          <DigitalTwinViewport class="flex-1" />
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
