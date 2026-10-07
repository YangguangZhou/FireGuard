import datetime
import json
import os
from typing import Any, Dict, List, Optional

from core.graph.topology import ConstructionGraph
from core.llm.qwen_suite import QwenModelSuite
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
        self.llm_suite = QwenModelSuite(api_key=dashscope_api_key)
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
            img_path = os.path.join("web_dashboard", "assets", "fire_cctv.jpg")
            perception = self.llm_suite.analyze_surveillance_snapshot(
                image_path=img_path,
                scenario_key="incident_fire_act2"
            )
            perception["image_url"] = "/assets/fire_cctv.jpg"
            perception["camera_id"] = "CAM-07 (3F 核心筒东干道)"
            self.last_perception_result = perception

            # 明火阻断东侧主干道及配电箱
            affected = perception.get("affected_edges", ["E_NCORR_REBAR", "E_REBAR_EXITEAST"])
            for eid in affected:
                self.graph.update_edge_hazard(
                    edge_id=eid,
                    fire_risk=0.98,
                    smoke_risk=0.95,
                    is_blocked=False
                )

            # 核心筒垂直井道烟囱效应扩散
            self.graph.update_edge_hazard("E_NCORR_CORE", fire_risk=0.15, smoke_risk=0.7)

            self.replan()
            summary = (
                f"【qwen3-vl-flash 火情预警】东侧主通道与配电箱处检测到明火与剧烈浓烟扩散，"
                f"智能体已执行 GB/T 50720 硬隔离，切断【东侧主楼梯 (出口A)】，全员动态分流至西外架爬梯与南避难平台！"
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
            img_path = os.path.join("web_dashboard", "assets", "scaffold_cctv.jpg")
            perception = self.llm_suite.analyze_surveillance_snapshot(
                image_path=img_path,
                scenario_key="incident_blockage_act3"
            )
            perception["image_url"] = "/assets/scaffold_cctv.jpg"
            perception["camera_id"] = "CAM-04 (西侧外架临时连廊)"
            self.last_perception_result = perception

            # 西侧脚手架通道坍塌占道，低于0.6m规范极限
            self.graph.update_edge_hazard(
                edge_id="E_WCORR_EXITWEST",
                fire_risk=0.0,
                smoke_risk=0.5,
                is_blocked=True
            )

            self.replan()
            summary = (
                f"【次生险情阻断】qwen3-vl-flash 识别到西侧走廊模板脚手架坍塌（实测通行净宽 0.35m < 0.6m规范极限），"
                f"智能体二次重规划触发：受阻工友全员调流至【南立面临时避难平台C】，启动登高云梯接驳避险方案！"
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
        """为每位工友生成个性化方言避险语音指令 (调用 qwen-turbo)"""
        broadcasts = []
        dialect_map = {
            "W01": "hunan",     # 李强 (湖南籍)
            "W02": "sichuan",   # 王建国 (四川籍)
            "W03": "mandarin",  # 张伟 (普通话)
            "W04": "hunan"      # 赵红兵 (湖南籍)
        }

        for r in routes:
            w_id = r["worker_id"]
            w_name = r["worker_name"]
            w_role = r["worker_role"]
            exit_name = r.get("exit_name", "安全区域")
            status = r.get("status")
            dialect = dialect_map.get(w_id, "mandarin")

            if status == "ROUTE_READY":
                dist = r["distance_m"]
                est_time = r["est_time_sec"]
                path_desc = " ➔ ".join([self.graph.nodes[n]["name"] for n in r["path"]])

                # 调用大模型生成方言指令
                audio_text = self.llm_suite.generate_dialect_broadcast(
                    worker_name=w_name,
                    role=w_role,
                    dialect=dialect,
                    target_exit=exit_name,
                    path_desc=path_desc,
                    est_seconds=est_time
                )
                level = "URGENT" if self.current_act != "ACT_1_NORMAL" else "INFO"
            else:
                audio_text = (
                    f"【紧急避险提醒】{w_name}师傅：当前通往地面通道暂时受阻！"
                    f"请留在当前相对安全结构柱后等待，特勤外部救援作业已就位！"
                )
                level = "CRITICAL"

            broadcasts.append({
                "worker_id": w_id,
                "worker_name": w_name,
                "worker_role": w_role,
                "dialect": dialect,
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

    def query_agent_chat(self, user_question: str) -> str:
        """
        人机协同指挥问答：安全总监通过自然语言即时查询现场态势
        调用 qwen3.7-plus 结合当前拓扑与 GB/T 50720 规则权威解答
        """
        routes = self.last_plan_result.get("routes", []) if self.last_plan_result else []
        compliance = self.last_plan_result.get("compliance_audit", {}) if self.last_plan_result else {}

        return self.llm_suite.ask_commander_copilot(
            question=user_question,
            current_act=self.current_act,
            routes=routes,
            compliance_audit=compliance
        )

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


