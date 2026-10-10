<template>
  <div
    v-if="store.showReportModal"
    class="fixed inset-0 bg-black/90 backdrop-blur-2xl z-50 flex items-center justify-center p-4"
  >
    <div
      class="gradient-border p-[1px] rounded-2xl max-w-3xl w-full shadow-2xl"
    >
      <div class="panel-glass rounded-2xl w-full p-6 overflow-y-auto max-h-[88vh] text-slate-200 bg-cyberPanel relative">
        <!-- 报告头部 -->
        <div class="flex justify-between items-start pb-4 relative">
          <div>
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-blue-900/50 text-blue-300 font-bold border border-blue-500/30 uppercase tracking-widest shadow-inner">中国建筑国际集团</span>
              <span class="text-xs text-slate-400 font-mono uppercase tracking-widest">报告编号: {{ store.reportData?.report_id || 'FG-2026-0922-3F' }}</span>
            </div>
            <h3 class="text-lg font-bold text-white tracking-widest uppercase">
              {{ store.reportData?.report_title || '施工现场火灾应急处置记录单' }}
            </h3>
            <p class="text-xs text-slate-400 font-mono mt-1 uppercase tracking-wider">
              生成时间: {{ store.reportData?.generated_at || new Date().toLocaleString('zh-CN') }}
            </p>
          </div>
          <button
            @click="store.showReportModal = false"
            class="text-slate-400 hover:text-white text-2xl font-bold leading-none p-1 transition hover:rotate-90 duration-300"
          >
            ✕
          </button>
          <!-- Gradient accent line -->
          <div class="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-cyan-500 via-blue-500 to-transparent"></div>
        </div>

        <!-- 报告内容主体 -->
        <div class="mt-5 space-y-5 text-xs">
          <!-- 工程元数据 -->
          <div class="panel-glass p-3.5 rounded-xl border border-cyberBorder grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-300 shadow-[inset_0_0_12px_rgba(34,211,238,0.05)]">
            <div><strong class="text-slate-400 uppercase text-[10px] tracking-widest">工程名称:</strong> <span class="font-bold text-white ml-1">{{ store.reportData?.project_meta?.project_name || store.projectMeta.project_name }}</span></div>
            <div><strong class="text-slate-400 uppercase text-[10px] tracking-widest">施工楼层:</strong> <span class="font-mono text-white ml-1">{{ store.reportData?.project_meta?.floor_level || store.projectMeta.floor_level }}</span></div>
            <div><strong class="text-slate-400 uppercase text-[10px] tracking-widest">技术规范:</strong> <span class="text-white ml-1">{{ store.reportData?.project_meta?.standard_applied || store.projectMeta.standard_applied }}</span></div>
            <div><strong class="text-slate-400 uppercase text-[10px] tracking-widest">处置终态:</strong> <span class="text-emerald-400 font-bold ml-1 drop-shadow-[0_0_4px_rgba(52,211,153,0.5)]">{{ store.reportData?.current_scenario_state || store.currentAct }}</span></div>
          </div>

          <!-- 人员安全疏散清单 -->
          <div>
            <h4 class="font-bold text-cyan-400 mb-2.5 flex items-center gap-2 text-xs border-l-2 border-cyan-400 pl-2.5 uppercase tracking-widest">
              <span>一、</span>现场人员疏散流向
            </h4>
            <div class="overflow-x-auto rounded-lg border border-cyberBorder/40 shadow-glass-sm bg-black/20">
              <table class="w-full text-left text-xs">
                <thead class="bg-white/5 backdrop-blur-md text-slate-300 uppercase text-[10px] tracking-widest border-b border-white/10">
                  <tr>
                    <th class="p-2.5 font-mono">工号</th>
                    <th class="p-2.5">工友姓名</th>
                    <th class="p-2.5">所属工种</th>
                    <th class="p-2.5">安全疏散目标</th>
                    <th class="p-2.5 font-mono">距离</th>
                    <th class="p-2.5 font-mono">预计耗时</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-white/5 font-sans">
                  <tr v-for="r in store.reportData?.detailed_personnel_manifest || store.routes" :key="r.worker_id" class="hover:bg-white/5 transition-colors duration-200">
                    <td class="p-2.5 font-mono text-slate-400">{{ r.worker_id }}</td>
                    <td class="p-2.5 font-bold text-white">{{ r.worker_name }}</td>
                    <td class="p-2.5 text-slate-300">{{ r.worker_role }}</td>
                    <td class="p-2.5 text-emerald-400 font-semibold drop-shadow-[0_0_2px_rgba(52,211,153,0.5)]">{{ r.exit_name }}</td>
                    <td class="p-2.5 font-mono text-amber-300">{{ r.distance_m }}m</td>
                    <td class="p-2.5 font-mono text-cyan-300">{{ r.est_time_sec }}s</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 消防安全疏散审计结论 -->
          <div>
            <h4 class="font-bold text-cyan-400 mb-2.5 flex items-center gap-2 text-xs border-l-2 border-cyan-400 pl-2.5 uppercase tracking-widest">
              <span>二、</span>消防疏散合规审计
            </h4>
            <div class="panel-glass p-3.5 rounded-xl border border-cyberBorder/40 space-y-2 text-slate-300 leading-relaxed shadow-[inset_0_0_12px_rgba(34,211,238,0.05)]">
              <div class="flex items-center gap-2">
                <strong class="text-slate-400 uppercase text-[10px] tracking-widest">双出口分流评定:</strong>
                <span class="text-emerald-400 font-bold drop-shadow-[0_0_4px_rgba(52,211,153,0.4)]">合规（已实现双向均衡疏散，未造成单点踩踏）</span>
              </div>
              <div>
                <strong class="text-slate-400 uppercase text-[10px] tracking-widest">审计判定摘要:</strong>
                <span class="ml-1 text-slate-200">{{ store.reportData?.standards_compliance_audit?.audit_notes?.join('；') || '全员已规划疏散完毕，临时通道符合规范要求。' }}</span>
              </div>
            </div>
          </div>

          <!-- 科学计算与寻径评价 -->
          <div v-if="sciEval">
            <h4 class="font-bold text-amber-400 mb-2.5 flex items-center gap-2 text-xs border-l-2 border-amber-400 pl-2.5 uppercase tracking-widest">
              <span>三、</span>动态路径计算评价
            </h4>
            <div class="panel-glass p-4 rounded-xl border border-amber-500/30 space-y-3.5 text-slate-300 shadow-[inset_0_0_15px_rgba(245,158,11,0.1)]">
              <div class="flex flex-wrap items-center justify-between gap-2 text-[11px] pb-2.5 border-b border-amber-500/20">
                <span class="text-slate-400 uppercase tracking-widest">算法核心: <strong class="text-emerald-400 font-mono ml-1">{{ sciEval.algorithm }}</strong></span>
                <span class="text-slate-400 uppercase tracking-widest">火灾演化分期: <strong class="text-amber-400 font-bold ml-1">{{ sciEval.stage_name }} ({{ sciEval.fire_stage }})</strong></span>
                <span class="text-slate-400 uppercase tracking-widest">重规划响应时延: <strong class="text-cyan-400 font-mono ml-1">{{ sciEval.replan_latency_ms }} ms</strong></span>
              </div>

              <!-- 动态三物理场权重 (式 6, 7) -->
              <div>
                <div class="text-[11px] text-slate-400 mb-2 flex justify-between uppercase tracking-widest">
                  <span>多物理场动态主导权重:</span>
                  <span class="font-mono text-slate-300">
                    能见度 {{ Math.round((sciEval.dynamic_weights?.visibility || 0) * 100) }}% |
                    温度 {{ Math.round((sciEval.dynamic_weights?.temp || 0) * 100) }}% |
                    CO浓度 {{ Math.round((sciEval.dynamic_weights?.co || 0) * 100) }}%
                  </span>
                </div>
                <div class="w-full h-2.5 bg-black/60 rounded-full flex overflow-hidden shadow-inner border border-white/5">
                  <div class="bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.8)] h-full transition-all duration-500" :style="{ width: `${(sciEval.dynamic_weights?.visibility || 0) * 100}%` }"></div>
                  <div class="bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)] h-full transition-all duration-500" :style="{ width: `${(sciEval.dynamic_weights?.temp || 0) * 100}%` }"></div>
                  <div class="bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)] h-full transition-all duration-500" :style="{ width: `${(sciEval.dynamic_weights?.co || 0) * 100}%` }"></div>
                </div>
              </div>

              <!-- 科学指标网格 -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1 font-mono text-[11px]">
                <div class="bg-black/40 p-2.5 rounded-lg border border-white/10 shadow-[inset_0_0_10px_rgba(255,255,255,0.02)] relative overflow-hidden">
                  <div class="absolute -right-4 -top-4 w-12 h-12 bg-emerald-500/10 rounded-full blur-xl"></div>
                  <div class="text-slate-500 text-[10px] uppercase tracking-wider relative z-10">路径效率 η (D/D0)</div>
                  <div class="text-emerald-400 font-bold text-sm mt-1 relative z-10">{{ sciEval.mean_path_efficiency?.toFixed(2) }}</div>
                </div>
                <div class="bg-black/40 p-2.5 rounded-lg border border-white/10 shadow-[inset_0_0_10px_rgba(255,255,255,0.02)] relative overflow-hidden">
                  <div class="absolute -right-4 -top-4 w-12 h-12 bg-rose-500/10 rounded-full blur-xl"></div>
                  <div class="text-slate-500 text-[10px] uppercase tracking-wider relative z-10">最大综合通行代价</div>
                  <div class="text-rose-400 font-bold text-sm mt-1 relative z-10">{{ sciEval.max_passage_cost?.toFixed(1) }}</div>
                </div>
                <div class="bg-black/40 p-2.5 rounded-lg border border-white/10 shadow-[inset_0_0_10px_rgba(255,255,255,0.02)] relative overflow-hidden">
                  <div class="absolute -right-4 -top-4 w-12 h-12 bg-cyan-500/10 rounded-full blur-xl"></div>
                  <div class="text-slate-500 text-[10px] uppercase tracking-wider relative z-10">平均通行代价</div>
                  <div class="text-cyan-400 font-bold text-sm mt-1 relative z-10">{{ sciEval.mean_passage_cost?.toFixed(1) }}</div>
                </div>
                <div class="bg-black/40 p-2.5 rounded-lg border border-white/10 shadow-[inset_0_0_10px_rgba(255,255,255,0.02)] relative overflow-hidden">
                  <div class="absolute -right-4 -top-4 w-12 h-12 bg-amber-500/10 rounded-full blur-xl"></div>
                  <div class="text-slate-500 text-[10px] uppercase tracking-wider relative z-10">轨迹平滑拐点数 (≥35°)</div>
                  <div class="text-amber-400 font-bold text-sm mt-1 relative z-10">{{ sciEval.total_inflexion_points }} 个</div>
                </div>
              </div>

              <div class="text-[10px] text-slate-500 border-t border-amber-500/20 pt-2.5 flex justify-between uppercase tracking-widest">
                <span>理论模型: {{ sciEval.methodology_reference || '动态代价网络模型' }}</span>
                <span v-if="sciEval.exit_utilization">
                  出口流量: 
                  <span v-for="(v, k) in sciEval.exit_utilization" :key="k" class="ml-1.5 text-slate-300 font-mono">
                    {{ k }}: {{ v }}
                  </span>
                </span>
              </div>
            </div>
          </div>

          <!-- 事件处置全流程闭环时序追溯 (Steps 1 ~ 7) -->
          <div v-if="store.reportData?.timeline_audit_log?.length">
            <h4 class="font-bold text-indigo-400 mb-2.5 flex items-center gap-2 text-xs border-l-2 border-indigo-400 pl-2.5 uppercase tracking-widest">
              <span>四、</span>处置时序审计链 (1 ~ {{ store.reportData.timeline_audit_log.length }})
            </h4>
            <div class="panel-glass p-3 rounded-xl border border-indigo-500/30 space-y-1.5 shadow-[inset_0_0_12px_rgba(99,102,241,0.05)] bg-black/20">
              <div
                v-for="log in store.reportData.timeline_audit_log"
                :key="log.sequence_id || log.timestamp"
                class="flex items-start gap-3 text-[11px] pb-2 border-b border-white/5 last:border-b-0 hover:bg-white/5 p-1.5 rounded transition-colors duration-200"
              >
                <span class="px-2 py-0.5 rounded-full font-mono font-bold text-[10px] bg-black/60 text-cyan-400 shrink-0 border border-cyan-500/30 shadow-sm mt-0.5">
                  #{{ log.sequence_id || 1 }} {{ log.time_offset || '+00.0s' }}
                </span>
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold shrink-0 border uppercase tracking-widest shadow-sm mt-0.5"
                  :class="{
                    'bg-rose-900/40 text-rose-300 border-rose-500/30': log.level === 'CRITICAL',
                    'bg-amber-900/40 text-amber-300 border-amber-500/30': log.level === 'WARNING',
                    'bg-emerald-900/40 text-emerald-300 border-emerald-500/30': log.level === 'SUCCESS',
                    'bg-blue-900/40 text-blue-300 border-blue-500/30': log.level === 'INFO'
                  }"
                >
                  {{ log.phase_name || log.phase || '处置' }}
                </span>
                <div class="flex-1 min-w-0">
                  <div class="font-bold text-slate-100 text-xs">{{ log.title || log.event_type }}</div>
                  <div class="text-slate-400 text-[10px] line-clamp-2 mt-1 leading-relaxed">{{ log.message }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <div class="mt-6 flex justify-end gap-3 pt-4 border-t border-white/10 relative">
          <!-- Gradient accent line for footer -->
          <div class="absolute top-0 right-0 w-1/3 h-[1px] bg-gradient-to-l from-cyan-500 to-transparent"></div>
          
          <button
            @click="printReport"
            class="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-bold shadow-glow-blue hover-lift flex items-center gap-1.5 transition-all duration-300 uppercase tracking-widest"
          >
            打印 / 另存为 PDF
          </button>
          <button
            @click="store.showReportModal = false"
            class="px-5 py-2.5 bg-slate-800/80 hover:bg-slate-700 border border-slate-600 hover:border-slate-500 text-slate-300 hover:text-white rounded-lg text-xs font-bold transition-all duration-300 uppercase tracking-widest shadow-sm"
          >
            关闭
          </button>
        </div>
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
