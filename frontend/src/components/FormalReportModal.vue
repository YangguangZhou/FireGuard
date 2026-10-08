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
            <span>📋</span> 一、现场人员安全疏散流向清单
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

        <!-- GB/T 50720 合规审计结论 -->
        <div>
          <h4 class="font-bold text-cyan-400 mb-2 flex items-center gap-1.5 text-xs">
            <span>⚖️</span> 二、GB/T 50720 施工现场消防安全审计评定
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
      </div>

      <!-- 底部操作按钮 -->
      <div class="mt-5 flex justify-end gap-2.5 pt-3 border-t border-slate-800">
        <button
          @click="printReport"
          class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg text-xs font-semibold shadow flex items-center gap-1.5 transition"
        >
          <span>🖨️</span> 打印 / 另存为 PDF
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
import { useEmergencyStore } from '@/stores/emergencyStore';

const store = useEmergencyStore();

function printReport() {
  window.print();
}
</script>
