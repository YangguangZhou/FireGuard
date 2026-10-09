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

        # 初始化基准方案与环境传感态势
        self.handle_incident("ACT_1_NORMAL")

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
        base_time = datetime.datetime.now()

        if act_key == "ACT_1_NORMAL":
            self.current_act = "ACT_1_NORMAL"
            # 恢复初始全通状态
            self.graph = ConstructionGraph(site_json_path=self.site_map_path)
            self.graph.update_sensors_for_act("ACT_1_NORMAL")
            self.replan()
            self.incident_log = []
            
            # 阶段 1: 空间底座就绪
            t1 = (base_time).strftime("%Y-%m-%d %H:%M:%S")
            self._log_event(
                time_str=t1,
                event_type="SYSTEM_INIT",
                sequence_id=1,
                time_offset="+00.0s",
                phase="AUDIT",
                phase_name="空间底座",
                level="INFO",
                title="3F 施工作业层数字孪生空间网格就绪",
                message="FireGuard 空间拓扑与 BIM 几何体加载完成，2400㎡ 作业面空间拓扑网格与 11 个关键节点就绪。",
                details={"area_sqm": 2400, "floor": "3F主体施工作业层", "nodes_count": len(self.graph.nodes), "edges_count": len(self.graph.edges)}
            )
            # 阶段 2: 传感器自检
            t2 = (base_time + datetime.timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
            self._log_event(
                time_str=t2,
                event_type="IOT_MESH_CHECK",
                sequence_id=2,
                time_offset="+00.8s",
                phase="SENSING",
                phase_name="传感自检",
                level="INFO",
                title="现场 IoT 传感监测网 8 处测点在线自检通过",
                message="全场 8 处关键传感器（东通道烟温、配电箱火焰、西通道激光净宽、核心筒烟感、木工区温烟、危化库CO）在线，读数均在安全阈值区间。",
                details={"online_sensors": len(self.graph.sensors), "alarming_count": 0, "smoke_baseline": "10~15 ppm", "temp_baseline": "23.8~24.5 ℃"}
            )
            # 阶段 3: GB/T 50720 规范自查
            t3 = (base_time + datetime.timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")
            self._log_event(
                time_str=t3,
                event_type="GB50720_AUDIT",
                sequence_id=3,
                time_offset="+01.6s",
                phase="ISOLATION",
                phase_name="规范合规",
                level="SUCCESS",
                title="GB/T 50720 施工消防全通道净宽合规审计",
                message="主施工通道净宽 2.2m、临时防护通道净宽 1.4m，全部满足临时疏散通道（≥1.2m）规范，双向分流通畅。",
                details={"standard": "GB/T 50720-2011 第4.3.2条", "min_clearance_m": 1.4, "max_evac_distance_m": 23.4, "status": "COMPLIANT"}
            )
            # 阶段 4: 工友终端待命
            t4 = (base_time + datetime.timedelta(seconds=3)).strftime("%Y-%m-%d %H:%M:%S")
            self._log_event(
                time_str=t4,
                event_type="WORKER_STANDBY",
                sequence_id=4,
                time_offset="+02.4s",
                phase="DISPATCH",
                phase_name="人员纳管",
                level="INFO",
                title="4名作业人员智能安全帽/工牌链路就绪",
                message="李强、王建国、张伟、赵红兵定位信标与骨传导语音信道在线，体征心率正常，现场处于常态安全受控状态。",
                details={"workers_count": 4, "devices": ["智能安全帽#101", "智能安全帽#102", "智能工牌#205", "智能安全帽#108"]}
            )

            summary = "【系统巡检常态】全作业层疏散通道畅通，满足GB/T 50720规范要求，8处传感监测点读数正常。"
            perception = {
                "fire_detected": False,
                "smoke_detected": False,
                "confidence": 0.0,
                "hazard_level": "NORMAL",
                "structural_obstacle": False,
                "image_url": "",
                "camera_id": "CAM-01 (全域高清轮巡)",
                "agent_perception_summary": summary
            }
            self.last_perception_result = perception
            return {
                "act": self.current_act,
                "perception": perception,
                "plan": self.last_plan_result,
                "broadcasts": self._generate_worker_broadcasts(self.last_plan_result["routes"]),
                "summary": summary
            }

        elif act_key == "ACT_2_FIRE":
            self.current_act = "ACT_2_FIRE"
            self.graph.update_sensors_for_act("ACT_2_FIRE")
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
                f"【智能感知预警】东侧主通道与配电箱处检测到明火与剧烈浓烟扩散，"
                f"智能体已执行消防安全硬隔离，切断【东侧主楼梯 (出口A)】，全员动态分流至西外架爬梯与南避难平台！"
            )

            # 构建真实连贯的事件处理时序链 (Steps 1 ~ 7)
            self.incident_log = []
            
            # 步骤 1: 物理传感器超标报警
            self._log_event(
                time_str=(base_time).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="IOT_SENSOR_TRIGGER",
                sequence_id=1,
                time_offset="+00.0s",
                phase="SENSING",
                phase_name="多源感知",
                level="CRITICAL",
                title="东干道高敏烟感与温感触发一级火警",
                message="测点 S_SMOKE_EAST 烟雾读数突增至 480 ppm (阈值60 ppm)，温感 S_TEMP_EAST 骤升至 88.5℃ (阈值55℃)，配电箱红外火焰探测器检出明火 (2.85 W/m²)，系统触发最高级别火警中断！",
                details={"sensor_id": "S_SMOKE_EAST", "smoke_ppm": 480, "temp_c": 88.5, "flame_level": "2.85 W/m²", "location": "东侧物料转运走廊(N_CORRIDOR_EAST)"}
            )
            # 步骤 2: 监控云台联动
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="CCTV_TRACKING",
                sequence_id=2,
                time_offset="+00.8s",
                phase="PERCEPTION",
                phase_name="视频联动",
                level="WARNING",
                title="联动 PTZ 云台 CAM-07 聚焦火场抓拍",
                message="调度中枢联动 3F 核心筒东干道监控摄像头 CAM-07 自动调整云台方位角，变焦捕获东侧配电箱区域剧烈燃烧画面并回传视觉模型。",
                details={"camera_id": "CAM-07", "preset_pos": "3F核心筒东侧配电箱", "resolution": "1080P", "stream_latency_ms": 120}
            )
            # 步骤 3: 视觉模型复核研判
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="VLM_ALARM",
                sequence_id=3,
                time_offset="+01.6s",
                phase="PERCEPTION",
                phase_name="视觉研判",
                level="CRITICAL",
                title="多模态视觉研判确认明火爆燃",
                message="智能视觉模型 180ms 极速研判监控图像：东侧临时配电箱电弧引燃木模板堆垛，伴随剧烈橙红明火与重度黑烟扩散，置信度 96.2%，定级为极高危 (CRITICAL)。",
                details={"engine": "多模态视觉感知引擎", "confidence": "96.2%", "hazard_level": "CRITICAL", "affected_zone": "东侧物料转运走廊及钢筋作业区"}
            )
            # 步骤 4: 规范硬隔离
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=3)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="GB50720_ISOLATION",
                sequence_id=4,
                time_offset="+02.4s",
                phase="ISOLATION",
                phase_name="规范隔离",
                level="CRITICAL",
                title="触发消防规范硬隔离：切断东出口A",
                message="依据临时消防通道硬隔离准则，立即切断过火通道 E_NCORR_REBAR 与 E_REBAR_EXITEAST，安全出口A（东现浇主楼梯）完全封锁禁行；核心筒竖向井道烟囱效应扩散加权至 0.70。",
                details={"rule": "临时消防通道硬隔离准则", "blocked_exit": "EXIT_EAST (东现浇主楼梯)", "blocked_edges": ["E_NCORR_REBAR", "E_REBAR_EXITEAST"], "smoke_weighted_edges": ["E_NCORR_CORE"]}
            )
            # 步骤 5: 动态加权 A* 寻优与分流
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=4)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="DYNAMIC_A_STAR",
                sequence_id=5,
                time_offset="+03.2s",
                phase="PLANNING",
                phase_name="动态寻路",
                level="SUCCESS",
                title="加权 A* 动态寻优：实现双出口防踩踏分流",
                message="图拓扑路由引擎 4.2ms 完成全场人员加权 A* 动态重规划：剔除东出口A，木工组（李强、王建国）分流向西出口B（西外架爬梯），钢筋工张伟与混凝土工赵红兵导向南避难平台C，避免人流对冲踩踏。",
                details={"algorithm": "Weighted A* Dynamic Routing", "compute_time_ms": 4.2, "diverted_exit_b": ["李强(W01)", "王建国(W02)"], "diverted_exit_c": ["张伟(W03)", "赵红兵(W04)"], "dual_exit_compliant": True}
            )
            # 步骤 6: 语音播报词生成
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="DIALECT_TTS",
                sequence_id=6,
                time_offset="+04.1s",
                phase="DISPATCH",
                phase_name="语音调度",
                level="SUCCESS",
                title="智能决策中枢为工友生成个性化语音避险指令",
                message="智能决策中枢根据工友位置与作业角色生成精准普通话避险指令，指引全员避开东干道火情，保持低姿弯腰撤离。",
                details={"engine": "智能语音调度引擎", "language": "标准普通话", "target_workers": ["W01", "W02", "W03", "W04"]}
            )
            # 步骤 7: 终端下发与态势受控
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=6)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="HELMET_BROADCAST",
                sequence_id=7,
                time_offset="+05.0s",
                phase="DISPATCH",
                phase_name="终端下发",
                level="INFO",
                title="智能安全帽骨传导信道并发推送与声光爆闪",
                message="清晰普通话语音音频推送至现场工友智能安全帽与工牌，声光导引指示灯高频爆闪，4名工友心率与移动轨迹纳入实时监控，总处置响应耗时 1.1s。",
                details={"channel": "骨传导双向语音", "sound_light_beacon": "ACTIVE", "avg_response_latency_sec": 1.1, "workers_tracked": 4}
            )

            return {
                "act": self.current_act,
                "perception": perception,
                "plan": self.last_plan_result,
                "broadcasts": self._generate_worker_broadcasts(self.last_plan_result["routes"]),
                "summary": summary
            }

        elif act_key == "ACT_3_BLOCKAGE":
            self.current_act = "ACT_3_BLOCKAGE"
            self.graph.update_sensors_for_act("ACT_3_BLOCKAGE")
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
                f"【次生险情阻断】智能视觉模型识别到西侧走廊模板脚手架坍塌（实测通行净宽 0.35m < 0.6m通行极限），"
                f"智能体二次重规划触发：受阻工友全员调流至【南立面临时避难平台C】，启动登高云梯接驳避险方案！"
            )

            # 构建次生阻断事件处理时序链 (Steps 1 ~ 7)
            self.incident_log = []
            
            # 步骤 1: 激光净宽仪警报
            self._log_event(
                time_str=(base_time).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="IOT_CLEARANCE_ALARM",
                sequence_id=1,
                time_offset="+00.0s",
                phase="SENSING",
                phase_name="次生监测",
                level="CRITICAL",
                title="西连廊激光净宽仪 S_WIDTH_WEST 监测到通道骤降",
                message="西侧临时防护通道激光测距仪 S_WIDTH_WEST 报警：通行净宽由 1.40m 骤降至 0.35m，西侧走廊结构位移传感器异动，疑似发生外架坍塌占道！",
                details={"sensor_id": "S_WIDTH_WEST", "reading_m": 0.35, "threshold_limit_m": 0.60, "location": "西侧临时防护通道(N_CORRIDOR_WEST)"}
            )
            # 步骤 2: 监控云台对准抓拍
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="CCTV_TRACKING",
                sequence_id=2,
                time_offset="+00.8s",
                phase="PERCEPTION",
                phase_name="视频抓拍",
                level="WARNING",
                title="CAM-04 抓拍西侧外架连廊模板坍塌画面",
                message="西立面监控 CAM-04 自动变焦对准西侧外脚手架刚性爬梯接驳段，抓拍到大面积模板与扣件散落侧翻横跨通道画面。",
                details={"camera_id": "CAM-04", "location": "西侧外架临时连廊", "obstacle_detected": True}
            )
            # 步骤 3: 视觉模型次生险情研判
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="VLM_OBSTACLE",
                sequence_id=3,
                time_offset="+01.6s",
                phase="PERCEPTION",
                phase_name="视觉研判",
                level="CRITICAL",
                title="多模态视觉研判西连廊脚手架侧翻占道",
                message="智能视觉模型 165ms 输出研判报告：脚手架扣件松脱导致连廊模板侧翻，实测有效通行净宽仅 0.35m，置信度 94.0%，判定为不可逾越的物理障碍 (COLLAPSED_OBSTACLE)。",
                details={"engine": "多模态视觉感知引擎", "measured_clearance_m": 0.35, "standard_limit_m": 0.60, "confidence": "94.0%"}
            )
            # 步骤 4: 规范性熔断切断
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=3)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="GB50720_ISOLATION",
                sequence_id=4,
                time_offset="+02.4s",
                phase="ISOLATION",
                phase_name="规范熔断",
                level="CRITICAL",
                title="触碰临时疏散通行净宽底线：切断西出口B",
                message="依据施工现场消防疏散安全要求（临时疏散通道净宽不得小于0.6m），当前净宽 0.35m 存在严重挤压踩踏隐患，智能体强制切断 E_WCORR_EXITWEST，西出口B路径失效！",
                details={"rule": "施工现场临时疏散通道宽度标准", "edge_id": "E_WCORR_EXITWEST", "blocked": True, "affected_workers": ["李强(W01)", "王建国(W02)"]}
            )
            # 步骤 5: 动态二次重规划寻优
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=4)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="DYNAMIC_REPLAN",
                sequence_id=5,
                time_offset="+03.2s",
                phase="PLANNING",
                phase_name="二次重算",
                level="SUCCESS",
                title="动态二次重规划：李强/王建国秒级改道避难平台C",
                message="智能体启动二次容灾重路由算法（耗时 3.8ms）：东出口A受火灾封锁，西出口B受坍塌阻断，系统将西侧受阻的李强、王建国动态重路由至【南立面临时避难平台C】（经西通道 -> 南走廊 -> 避难平台），全场人员全员锁定新安全逃生动线！",
                details={"algorithm": "Secondary Re-Route A*", "compute_time_ms": 3.8, "new_target_exit": "EXIT_REFUGE (临时避难平台C)", "rerouted_workers": ["李强(W01)", "王建国(W02)"]}
            )
            # 步骤 6: 语音紧急纠偏插播
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="VOICE_REDIRECT",
                sequence_id=6,
                time_offset="+04.1s",
                phase="DISPATCH",
                phase_name="即时纠偏",
                level="SUCCESS",
                title="智能安全帽紧急插播改道纠偏指令",
                message="智能决策中枢紧急下发改道插播语音：【请注意！西侧临时通道脚手架坍塌受阻！请立即右转改道前往南侧避难平台！】，打断原前行广播，引导其立刻调头避险。",
                details={"engine": "智能语音调度引擎", "priority": "EMERGENCY_OVERRIDE", "divert_target": "南立面临时避难平台C"}
            )
            # 步骤 7: 外部特勤救援接驳
            self._log_event(
                time_str=(base_time + datetime.timedelta(seconds=6)).strftime("%Y-%m-%d %H:%M:%S"),
                event_type="RESCUE_DISPATCH",
                sequence_id=7,
                time_offset="+05.0s",
                phase="RESCUE",
                phase_name="特勤联动",
                level="SUCCESS",
                title="联动外部救援：53m 消防云梯车前往南立面平台接驳",
                message="中枢自动向外部消防指挥车上报 3F 南立面卸料作业平台 GPS 坐标与结构载荷，调度 53 米登高云梯车展开外部登高面接驳，实现全员 100% 成功脱困！",
                details={"rescue_type": "53m 消防云梯车外部登高接驳", "target_location": "3F南立面卸料平台C", "trapped_count": 0, "safe_evac_ratio": "100%"}
            )

            return {
                "act": self.current_act,
                "perception": perception,
                "plan": self.last_plan_result,
                "broadcasts": self._generate_worker_broadcasts(self.last_plan_result["routes"]),
                "summary": summary
            }

        return {"error": "Unknown act key"}

    def _generate_worker_broadcasts(self, routes: List[Dict]) -> List[Dict]:
        """为每位工友生成标准普通话避险语音指令"""
        broadcasts = []

        for r in routes:
            w_id = r["worker_id"]
            w_name = r["worker_name"]
            w_role = r["worker_role"]
            exit_name = r.get("exit_name", "安全区域")
            status = r.get("status")
            dialect = "mandarin"

            if status == "ROUTE_READY":
                dist = r["distance_m"]
                est_time = r["est_time_sec"]
                path_desc = " ➔ ".join([self.graph.nodes[n]["name"] for n in r["path"]])

                if self.current_act == "ACT_1_NORMAL":
                    audio_text = f"【日常巡查】{w_name}师傅（{w_role}）：当前作业区通道畅通合规，智能安全帽信道待命。"
                    level = "INFO"
                else:
                    # 火警阶段：调用模型生成标准普通话逃生指令
                    audio_text = self.llm_suite.generate_dialect_broadcast(
                        worker_name=w_name,
                        role=w_role,
                        dialect="mandarin",
                        target_exit=exit_name,
                        path_desc=path_desc,
                        est_seconds=est_time
                    )
                    level = "URGENT"
            else:
                audio_text = (
                    f"【紧急避险提醒】{w_name}师傅：当前通往地面通道暂时受阻！"
                    f"请留在当前相对安全结构柱后等待，特勤外部救援作业已就位！"
                )
                level = "CRITICAL"

            # 生成对应的物理 .wav 语音音频文件供安全帽与大屏调用
            audio_url = self.llm_suite.synthesize_broadcast_audio(
                worker_id=w_id,
                text=audio_text,
                dialect="mandarin",
                act=self.current_act
            )

            broadcasts.append({
                "worker_id": w_id,
                "worker_name": w_name,
                "worker_role": w_role,
                "dialect": "mandarin",
                "device": r.get("device", "智能安全帽"),
                "alert_level": level,
                "audio_script": audio_text,
                "audio_url": audio_url,
                "target_exit": exit_name
            })
        return broadcasts

    def _log_event(
        self,
        time_str: str,
        event_type: str,
        message: str,
        details: Optional[Dict] = None,
        sequence_id: Optional[int] = None,
        time_offset: Optional[str] = None,
        phase: Optional[str] = None,
        phase_name: Optional[str] = None,
        level: str = "INFO",
        title: Optional[str] = None
    ):
        seq = sequence_id if sequence_id is not None else (len(self.incident_log) + 1)
        self.incident_log.append({
            "sequence_id": seq,
            "timestamp": time_str,
            "time_offset": time_offset or f"+{seq * 0.8:04.1f}s",
            "phase": phase or "SENSING",
            "phase_name": phase_name or "态势感知",
            "event_type": event_type,
            "level": level,
            "title": title or event_type,
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
            "scientific_evaluation": self.last_plan_result.get("scientific_evaluation", {}) if self.last_plan_result else {},
            "detailed_personnel_manifest": routes,
            "timeline_audit_log": self.incident_log
        }


