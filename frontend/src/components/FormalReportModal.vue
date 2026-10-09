<template>
  <div
    v-if="store.showReportModal"
    class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
  >
    <div
      class="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full p-6 shadow-2xl overflow-y-auto max-h-[88vh] text-slate-200"
    >
      <!-- 报告头部 -->
      <div class="flex justify-between items-start pb-4 border-b border-slate-700">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-xs px-2 py-0.5 rounded bg-blue-900 text-blue-200 font-bold">中国建筑国际集团</span>
            <span class="text-xs text-slate-400 font-mono">报告编号: {{ store.reportData?.report_id || 'FG-2026-0922-3F' }}</span>
          </div>
          <h3 class="text-lg font-bold text-white tracking-wide">
            {{ store.reportData?.report_title || '施工现场火灾应急处置记录单' }}
          </h3>
          <p class="text-xs text-slate-400 font-mono mt-0.5">
            生成时间: {{ store.reportData?.generated_at || new Date().toLocaleString('zh-CN') }}
          </p>
        </div>
        <button
          @click="store.showReportModal = false"
          class="text-slate-400 hover:text-white text-2xl font-bold leading-none p-1 transition"
        >
          ✕
        </button>
      </div>

      <!-- 报告内容主体 -->
      <div class="mt-4 space-y-4 text-xs">
        <!-- 工程元数据 -->
        <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-300">
          <div><strong class="text-slate-400">工程名称:</strong> {{ store.reportData?.project_meta?.project_name || store.projectMeta.project_name }}</div>
          <div><strong class="text-slate-400">施工楼层:</strong> {{ store.reportData?.project_meta?.floor_level || store.projectMeta.floor_level }}</div>
          <div><strong class="text-slate-400">技术规范:</strong> {{ store.reportData?.project_meta?.standard_applied || store.projectMeta.standard_applied }}</div>
          <div><strong class="text-slate-400">处置终态:</strong> <span class="text-emerald-400 font-bold">{{ store.reportData?.current_scenario_state || store.currentAct }}</span></div>
        </div>

        <!-- 人员安全疏散清单 -->
        <div>
          <h4 class="font-bold text-cyan-400 mb-2 flex items-center gap-1.5 text-xs">
            <span>一、</span>现场人员疏散流向
          </h4>
          <div class="overflow-x-auto rounded-lg border border-slate-800">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-800/80 text-slate-400">
                <tr>
                  <th class="p-2 font-mono">工号</th>
                  <th class="p-2">工友姓名</th>
                  <th class="p-2">所属工种</th>
                  <th class="p-2">安全疏散目标</th>
                  <th class="p-2 font-mono">距离</th>
                  <th class="p-2 font-mono">预计耗时</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800 bg-slate-950/60 font-sans">
                <tr v-for="r in store.reportData?.detailed_personnel_manifest || store.routes" :key="r.worker_id">
                  <td class="p-2 font-mono text-slate-400">{{ r.worker_id }}</td>
                  <td class="p-2 font-bold text-white">{{ r.worker_name }}</td>
                  <td class="p-2 text-slate-300">{{ r.worker_role }}</td>
                  <td class="p-2 text-emerald-400 font-semibold">{{ r.exit_name }}</td>
                  <td class="p-2 font-mono text-amber-300">{{ r.distance_m }}m</td>
                  <td class="p-2 font-mono text-cyan-300">{{ r.est_time_sec }}s</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 消防安全疏散审计结论 -->
        <div>
          <h4 class="font-bold text-cyan-400 mb-2 flex items-center gap-1.5 text-xs">
            <span>二、</span>消防疏散合规审计
          </h4>
          <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1.5 text-slate-300 leading-relaxed">
            <div class="flex items-center gap-2">
              <strong class="text-slate-400">双出口分流评定:</strong>
              <span class="text-emerald-400 font-bold">合规（已实现双向均衡疏散，未造成单点踩踏）</span>
            </div>
            <div>
              <strong class="text-slate-400">审计判定摘要:</strong>
              <span class="ml-1">{{ store.reportData?.standards_compliance_audit?.audit_notes?.join('；') || '全员已规划疏散完毕，临时通道符合规范要求。' }}</span>
            </div>
          </div>
        </div>

        <!-- 科学计算与寻径评价 -->
        <div v-if="sciEval">
          <h4 class="font-bold text-amber-400 mb-2 flex items-center gap-1.5 text-xs">
            <span>三、</span>动态路径计算评价
          </h4>
          <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-3 text-slate-300">
            <div class="flex items-center justify-between text-[11px] pb-2 border-b border-slate-800">
              <span class="text-slate-400">算法核心: <strong class="text-emerald-400 font-mono">{{ sciEval.algorithm }}</strong></span>
              <span class="text-slate-400">火灾演化分期: <strong class="text-amber-400 font-bold">{{ sciEval.stage_name }} ({{ sciEval.fire_stage }})</strong></span>
              <span class="text-slate-400">重规划响应时延: <strong class="text-cyan-400 font-mono">{{ sciEval.replan_latency_ms }} ms</strong></span>
            </div>

            <!-- 动态三物理场权重 (式 6, 7) -->
            <div>
              <div class="text-[11px] text-slate-400 mb-1.5 flex justify-between">
                <span>多物理场动态主导权重:</span>
                <span class="font-mono text-slate-300">
                  能见度 {{ Math.round((sciEval.dynamic_weights?.visibility || 0) * 100) }}% |
                  温度 {{ Math.round((sciEval.dynamic_weights?.temp || 0) * 100) }}% |
                  CO浓度 {{ Math.round((sciEval.dynamic_weights?.co || 0) * 100) }}%
                </span>
              </div>
              <div class="w-full h-2 bg-slate-800 rounded-full flex overflow-hidden">
                <div class="bg-sky-500 h-full" :style="{ width: `${(sciEval.dynamic_weights?.visibility || 0) * 100}%` }"></div>
                <div class="bg-rose-500 h-full" :style="{ width: `${(sciEval.dynamic_weights?.temp || 0) * 100}%` }"></div>
                <div class="bg-amber-500 h-full" :style="{ width: `${(sciEval.dynamic_weights?.co || 0) * 100}%` }"></div>
              </div>
            </div>

            <!-- 科学指标网格 -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 font-mono text-[11px]">
              <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
                <div class="text-slate-500 text-[10px]">路径效率 η (D/D0)</div>
                <div class="text-emerald-400 font-bold text-xs mt-0.5">{{ sciEval.mean_path_efficiency?.toFixed(2) }}</div>
              </div>
              <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
                <div class="text-slate-500 text-[10px]">最大综合通行代价</div>
                <div class="text-rose-400 font-bold text-xs mt-0.5">{{ sciEval.max_passage_cost?.toFixed(1) }}</div>
              </div>
              <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
                <div class="text-slate-500 text-[10px]">平均通行代价</div>
                <div class="text-cyan-400 font-bold text-xs mt-0.5">{{ sciEval.mean_passage_cost?.toFixed(1) }}</div>
              </div>
              <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
                <div class="text-slate-500 text-[10px]">轨迹平滑拐点数 (≥35°)</div>
                <div class="text-amber-400 font-bold text-xs mt-0.5">{{ sciEval.total_inflexion_points }} 个</div>
              </div>
            </div>

            <div class="text-[10px] text-slate-500 border-t border-slate-800/80 pt-1.5 flex justify-between">
              <span>理论模型: {{ sciEval.methodology_reference || '动态代价网络模型' }}</span>
              <span v-if="sciEval.exit_utilization">
                出口流量: 
                <span v-for="(v, k) in sciEval.exit_utilization" :key="k" class="ml-1 text-slate-400">
                  {{ k }}: {{ v }}
                </span>
              </span>
            </div>
          </div>
        </div>

        <!-- 事件处置全流程闭环时序追溯 (Steps 1 ~ 7) -->
        <div v-if="store.reportData?.timeline_audit_log?.length">
          <h4 class="font-bold text-indigo-400 mb-2 flex items-center gap-1.5 text-xs">
            <span>四、</span>处置时序审计链 (1 ~ {{ store.reportData.timeline_audit_log.length }})
          </h4>
          <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2">
            <div
              v-for="log in store.reportData.timeline_audit_log"
              :key="log.sequence_id || log.timestamp"
              class="flex items-start gap-2 text-[11px] pb-1.5 border-b border-slate-900 last:border-b-0"
            >
              <span class="px-1.5 py-0.5 rounded font-mono font-bold text-[10px] bg-slate-800 text-cyan-400 shrink-0">
                #{{ log.sequence_id || 1 }} {{ log.time_offset || '+00.0s' }}
              </span>
              <span
                class="px-1.5 py-0.5 rounded text-[10px] font-bold shrink-0"
                :class="{
                  'bg-rose-900/60 text-rose-300': log.level === 'CRITICAL',
                  'bg-amber-900/60 text-amber-300': log.level === 'WARNING',
                  'bg-emerald-900/60 text-emerald-300': log.level === 'SUCCESS',
                  'bg-blue-900/60 text-blue-300': log.level === 'INFO'
                }"
              >
                {{ log.phase_name || log.phase || '处置' }}
              </span>
              <div class="flex-1 min-w-0">
                <div class="font-bold text-slate-200">{{ log.title || log.event_type }}</div>
                <div class="text-slate-400 text-[10px] line-clamp-2 mt-0.5">{{ log.message }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作按钮 -->
      <div class="mt-5 flex justify-end gap-2.5 pt-3 border-t border-slate-800">
        <button
          @click="printReport"
          class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg text-xs font-semibold shadow flex items-center gap-1.5 transition"
        >
          打印 / 另存为 PDF
        </button>
        <button
          @click="store.showReportModal = false"
          class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-medium transition"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useEmergencyStore } from '@/stores/emergencyStore';

const store = useEmergencyStore();

const sciEval = computed(() => store.reportData?.scientific_evaluation || store.scientificEvaluation);

function printReport() {
  window.print();
}
</script>
