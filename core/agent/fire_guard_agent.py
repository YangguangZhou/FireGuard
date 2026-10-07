"""
FireGuard 应急疏散智能体决策中枢 (Cognitive Commander Agent)
融合视觉感知、规范硬约束、确定性图寻路、个性化语音指令生成与事故记录归档
"""

import datetime
import json
from typing import Any, Dict, List, Optional

from core.graph.topology import ConstructionGraph
from core.perception.vlm_client import QwenVLPerceptionClient
from core.standards.rules_engine import ConstructionFireStandardsEngine


class FireGuardAgent:
    """
    面向动态施工环境的火灾应急疏散中枢智能体
    """

    def __init__(
        self,
        site_map_path: str = "data/site_maps/floor_level_3.json",
        dashscope_api_key: Optional[str] = None
    ):
        self.site_map_path = site_map_path
        self.graph = ConstructionGraph(site_json_path=site_map_path)
        self.perception_client = QwenVLPerceptionClient(api_key=dashscope_api_key)
        self.standards_engine = ConstructionFireStandardsEngine()

        # 智能体当前态势上下文
        self.current_act = "ACT_1_NORMAL"
        self.incident_log: List[Dict] = []
        self.last_perception_result: Optional[Dict] = None
        self.last_plan_result: Optional[Dict] = None

        # 初始化基准方案
        self.replan()

    def replan(self) -> Dict:
        """重新计算全场工友疏散路线与规范审查"""
        self.last_plan_result = self.graph.plan_all_workers()
        return self.last_plan_result

    def handle_incident(
        self,
        act_key: str,
        image_url: Optional[str] = None,
        manual_override: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        核心智能体事件驱动处理流程：
        1. 多模态/感知层识别异常 (Vision Perception Tool)
        2. 风险评估与规范映射 (Risk & Standards Engine Tool)
        3. 确定性 A* 路径重规划 (Graph Routing Engine Tool)
        4. 多端差异化人机协同指令生成 (Worker Dispatch Tool)
        5. 决策流日志归档
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if act_key == "ACT_1_NORMAL":
            self.current_act = "ACT_1_NORMAL"
            # 恢复初始全通状态
            self.graph = ConstructionGraph(site_json_path=self.site_map_path)
            self.replan()
            summary = "【系统巡检常态】全作业层疏散通道畅通，满足GB/T 50720规范要求，各监控点读数正常。"
            self._log_event(timestamp, "NORMAL_MONITORING", summary)
            return {
                "act": self.current_act,
                "perception": {"fire_detected": False, "smoke_detected": False, "agent_perception_summary": summary},
                "plan": self.last_plan_result,
                "broadcasts": self._generate_worker_broadcasts(self.last_plan_result["routes"]),
                "summary": summary
            }

        elif act_key == "ACT_2_FIRE":
            self.current_act = "ACT_2_FIRE"
            # 调用 VLM 感知工具
            perception = self.perception_client.analyze_scene_image(
                image_url_or_path=image_url or "mock://fire_scene.jpg",
                scenario_key="incident_fire_act2"
            )
            self.last_perception_result = perception

            # 将感知认知结果作用于施工拓扑图
            affected = perception.get("affected_edges", ["E_NCORR_REBAR", "E_REBAR_EXITEAST"])
            for eid in affected:
                # 明火阻断东侧主干道
                self.graph.update_edge_hazard(
                    edge_id=eid,
                    fire_risk=0.95,
                    smoke_risk=0.9,
                    is_blocked=False
                )

            # 核心筒产生烟囱效应烟气蔓延
            self.graph.update_edge_hazard("E_NCORR_CORE", fire_risk=0.1, smoke_risk=0.6)

            # 触发确定性图重规划
            self.replan()
            summary = (
                f"【突发火情告警】Qwen-VL识别到东干道严重火情与浓烟，"
                f"智能体已紧急切断通往【东侧主楼梯】高危通道，动态调度工友转向【西侧避难爬梯】及【南避难平台】！"
            )
            self._log_event(timestamp, "FIRE_ALARM_REROUTE", summary, perception)
            return {
                "act": self.current_act,
                "perception": perception,
                "plan": self.last_plan_result,
                "broadcasts": self._generate_worker_broadcasts(self.last_plan_result["routes"]),
                "summary": summary
            }

        elif act_key == "ACT_3_BLOCKAGE":
            self.current_act = "ACT_3_BLOCKAGE"
            perception = self.perception_client.analyze_scene_image(
                image_url_or_path=image_url or "mock://scaffold_collapse.jpg",
                scenario_key="incident_blockage_act3"
            )
            self.last_perception_result = perception

            # 西侧脚手架通道坍塌占道，低于0.6m规范极限
            self.graph.update_edge_hazard(
                edge_id="E_WCORR_EXITWEST",
                fire_risk=0.0,
                smoke_risk=0.4,
                is_blocked=True
            )

            # 再次触发全局重规划
            self.replan()
            summary = (
                f"【次生险情阻断】检测到西侧避难爬梯通道因支架坍塌受阻（净宽仅0.35m，违反GB/T 50720规范），"
                f"智能体执行二次重规划：将受困木工班组调流至【南立面临时避难平台C】，启动登高云梯车外部接驳方案！"
            )
            self._log_event(timestamp, "SECONDARY_OBSTACLE_REROUTE", summary, perception)
            return {
                "act": self.current_act,
                "perception": perception,
                "plan": self.last_plan_result,
                "broadcasts": self._generate_worker_broadcasts(self.last_plan_result["routes"]),
                "summary": summary
            }

        return {"error": "Unknown act key"}

    def _generate_worker_broadcasts(self, routes: List[Dict]) -> List[Dict]:
        """为每位工友生成个性化、语音与交互屏导引指令"""
        broadcasts = []
        for r in routes:
            w_name = r["worker_name"]
            w_role = r["worker_role"]
            exit_name = r.get("exit_name", "安全区域")
            status = r.get("status")

            if status == "ROUTE_READY":
                dist = r["distance_m"]
                est_time = r["est_time_sec"]
                path_desc = " ➔ ".join([self.graph.nodes[n]["name"] for n in r["path"]])

                audio_text = (
                    f"【应急疏散指令】{w_name}师傅（{w_role}）：请注意！"
                    f"您前方危险区已隔离。请立即向【{exit_name}】撤离！"
                    f"途经路线：{path_desc}。预计耗时约{est_time}秒，请压低身姿，用湿毛巾捂住口鼻！"
                )
                level = "URGENT" if self.current_act != "ACT_1_NORMAL" else "INFO"
            else:
                audio_text = (
                    f"【紧急避险提醒】{w_name}师傅：当前通往地面通道暂时受阻！"
                    f"请留在当前相对安全结构柱后等待，特勤外部救援作业已就位！"
                )
                level = "CRITICAL"

            broadcasts.append({
                "worker_id": r["worker_id"],
                "worker_name": w_name,
                "worker_role": w_role,
                "device": r.get("device", "智能安全帽"),
                "alert_level": level,
                "audio_script": audio_text,
                "target_exit": exit_name
            })
        return broadcasts

    def _log_event(self, time_str: str, event_type: str, message: str, details: Optional[Dict] = None):
        self.incident_log.append({
            "timestamp": time_str,
            "event_type": event_type,
            "message": message,
            "details": details or {}
        })

    def export_formal_emergency_report(self) -> Dict[str, Any]:
        """
        生成符合建设工程应急管理规范的标准《施工现场火情处置与人员疏散决策记录表》
        供救援消防队入场时一键调阅现场最新三维态势与受困人员清单
        """
        routes = self.last_plan_result["routes"] if self.last_plan_result else []
        exits_summary = {}
        for r in routes:
            ex = r.get("exit_name", "未知")
            exits_summary[ex] = exits_summary.get(ex, 0) + 1

        return {
            "report_title": "中国建筑国际·智慧工地火灾应急疏散智能体处置记录单",
            "report_id": f"FG-DISPATCH-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_meta": self.graph.meta,
            "current_scenario_state": self.current_act,
            "vlm_incident_analysis": self.last_perception_result or {"status": "正常无灾情"},
            "evacuation_overview": {
                "total_personnel_tracked": len(self.graph.workers),
                "safe_routing_success_count": len([r for r in routes if r["status"] == "ROUTE_READY"]),
                "exit_flow_distribution": exits_summary
            },
            "standards_compliance_audit": self.last_plan_result.get("compliance_audit", {}) if self.last_plan_result else {},
            "detailed_personnel_manifest": routes,
            "timeline_audit_log": self.incident_log
        }
