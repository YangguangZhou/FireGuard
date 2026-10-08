import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { 
  ActType, 
  SiteNode, 
  SiteEdge, 
  WorkerInfo, 
  EvacuationRoute, 
  WorkerBroadcast, 
  PerceptionResult, 
  ComplianceAudit, 
  IncidentLogItem, 
  ProjectMeta 
} from '@/types/emergency';
import { fireguardApi } from '@/api/fireguardApi';

export interface DrillStep {
  id: number;
  act: ActType | 'REPORT';
  label: string;
  tag: string;
  desc: string;
  color: string;
}

export const useEmergencyStore = defineStore('emergency', () => {
  // 基础响应式态势
  const currentAct = ref<ActType>('ACT_1_NORMAL');
  const currentDrillStep = ref<number>(0);
  const isAutoDrillPlaying = ref<boolean>(false);
  const isLoading = ref<boolean>(false);
  const showReportModal = ref<boolean>(false);
  const reportData = ref<any>(null);

  const projectMeta = ref<ProjectMeta>({
    project_name: '长沙市某超高层建筑结构主体施工现场',
    floor_level: '3F 施工作业层 (现浇主体)',
    standard_applied: 'GB/T 50720-2011 建设工程施工现场消防安全技术规范',
  });

  const nodes = ref<SiteNode[]>([]);
  const edges = ref<SiteEdge[]>([]);
  const workers = ref<WorkerInfo[]>([]);
  const routes = ref<EvacuationRoute[]>([]);
  const broadcasts = ref<WorkerBroadcast[]>([]);
  const logs = ref<IncidentLogItem[]>([]);

  const perception = ref<PerceptionResult>({
    fire_detected: false,
    smoke_detected: false,
    confidence: 0,
    hazard_level: 'NORMAL',
    structural_obstacle: false,
    camera_id: 'CAM-01 (全域高清轮巡)',
    agent_perception_summary: '系统全域巡检中，3F全通道净宽合规，未见异常读数。',
  });

  const compliance = ref<ComplianceAudit>({
    compliance_status: 'COMPLIANT',
    dual_exit_compliant: true,
    max_evac_distance_m: 23.4,
    min_passage_width_m: 1.2,
    audit_notes: ['全通道疏散净宽满足临时消防通道 ≥1.2m 规定。'],
  });

  // 演练推演序列定义
  const drillSteps: DrillStep[] = [
    {
      id: 0,
      act: 'ACT_1_NORMAL',
      label: '常态安全巡检',
      tag: '阶段 0',
      desc: '全通道净宽合规 · 安全帽信道待命',
      color: 'emerald',
    },
    {
      id: 1,
      act: 'ACT_2_FIRE',
      label: '东干道突发火情',
      tag: '阶段 1',
      desc: '配电箱引燃木模 · VLM识别 · A*生成双分流光流',
      color: 'rose',
    },
    {
      id: 2,
      act: 'ACT_3_BLOCKAGE',
      label: '西外架次生坍塌',
      tag: '阶段 2',
      desc: '爬梯连廊侧翻受阻 · 净宽0.35m违规 · 秒级重定向避难平台',
      color: 'amber',
    },
    {
      id: 3,
      act: 'REPORT',
      label: '全员避险处置记录',
      tag: '阶段 3',
      desc: '全员脱困 · 导出 GB/T 50720 规范应急记录单',
      color: 'cyan',
    },
  ];

  let autoDrillTimer: any = null;

  // 计算属性
  const isFireScene = computed(() => {
    return currentAct.value === 'ACT_2_FIRE' || currentAct.value === 'ACT_3_BLOCKAGE';
  });

  const isBlockageScene = computed(() => {
    return currentAct.value === 'ACT_3_BLOCKAGE';
  });

  // 动作与业务流
  async function fetchState() {
    try {
      isLoading.value = true;
      const data = await fireguardApi.getState();
      currentAct.value = data.current_act;
      projectMeta.value = data.project_meta;
      nodes.value = data.nodes || [];
      edges.value = data.edges || [];
      workers.value = data.workers || [];
      routes.value = data.plan?.routes || [];
      broadcasts.value = data.broadcasts || [];
      perception.value = data.perception || perception.value;
      compliance.value = data.plan?.compliance_audit || compliance.value;
      logs.value = data.incident_log || [];
    } catch (err) {
      console.error('获取现场态势失败:', err);
    } finally {
      isLoading.value = false;
    }
  }

  async function triggerAct(actKey: ActType) {
    try {
      isLoading.value = true;
      await fireguardApi.triggerAct(actKey);
      await fetchState();
    } catch (err) {
      console.error('触发情景失败:', err);
    } finally {
      isLoading.value = false;
    }
  }

  async function jumpToStep(stepIdx: number) {
    currentDrillStep.value = stepIdx;
    const step = drillSteps[stepIdx];
    if (step.act === 'REPORT') {
      showReportModal.value = true;
      await fetchReport();
    } else {
      showReportModal.value = false;
      await triggerAct(step.act);
    }
  }

  function toggleAutoDrill() {
    if (isAutoDrillPlaying.value) {
      clearInterval(autoDrillTimer);
      isAutoDrillPlaying.value = false;
    } else {
      isAutoDrillPlaying.value = true;
      jumpToStep(0);
      autoDrillTimer = setInterval(() => {
        if (currentDrillStep.value < drillSteps.length - 1) {
          jumpToStep(currentDrillStep.value + 1);
        } else {
          jumpToStep(0);
        }
      }, 9500);
    }
  }

  async function resetAllToNormal() {
    if (autoDrillTimer) {
      clearInterval(autoDrillTimer);
      autoDrillTimer = null;
    }
    isAutoDrillPlaying.value = false;
    showReportModal.value = false;
    currentDrillStep.value = 0;
    await triggerAct('ACT_1_NORMAL');
  }

  async function fetchReport() {
    try {
      reportData.value = await fireguardApi.getFormalReport();
    } catch (err) {
      console.error('获取处置记录失败:', err);
    }
  }

  return {
    currentAct,
    currentDrillStep,
    isAutoDrillPlaying,
    isLoading,
    showReportModal,
    reportData,
    projectMeta,
    nodes,
    edges,
    workers,
    routes,
    broadcasts,
    perception,
    compliance,
    logs,
    drillSteps,
    isFireScene,
    isBlockageScene,
    fetchState,
    triggerAct,
    jumpToStep,
    toggleAutoDrill,
    resetAllToNormal,
    fetchReport,
  };
});
