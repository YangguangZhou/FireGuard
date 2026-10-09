"""
FireGuard 施工现场动态拓扑图与高可靠加权 A* 寻路算法
确保 100% 绕开火源禁行区、避开高浓烟通道，并满足 GB/T 50720 疏散规范
"""

import heapq
import json
import math
import time
from typing import Dict, List, Optional, Set, Tuple

from core.standards.rules_engine import ConstructionFireStandardsEngine, DynamicFireCostNetwork


class ConstructionGraph:
    """施工现场拓扑连通图与动态权值计算"""

    def __init__(self, site_json_path: Optional[str] = None, data_dict: Optional[Dict] = None):
        self.standards_engine = ConstructionFireStandardsEngine()
        self.cost_network = DynamicFireCostNetwork(current_stage="initial")
        self.nodes: Dict[str, Dict] = {}
        self.edges: Dict[str, Dict] = {}
        self.adjacency: Dict[str, List[str]] = {}  # node_id -> list of edge_ids
        self.workers: List[Dict] = []
        self.sensors: List[Dict] = []
        self.meta: Dict = {}

        if site_json_path:
            with open(site_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._load_from_dict(data)
        elif data_dict:
            self._load_from_dict(data_dict)

    def _load_from_dict(self, data: Dict):
        self.meta = data.get("project_meta", {})
        self.workers = data.get("workers", [])
        self.sensors = data.get("sensors", [])

        for n in data.get("nodes", []):
            self.nodes[n["id"]] = n
            self.adjacency[n["id"]] = []

        for e in data.get("edges", []):
            self.edges[e["id"]] = {
                **e,
                "risk_fire": 0.0,       # 0.0 ~ 1.0 (1.0表示火源吞噬，禁行)
                "risk_smoke": 0.0,      # 0.0 ~ 1.0 (烟雾浓度权重)
                "is_blocked": e.get("current_status") == "blocked",
                "allocated_crowd": 0    # 当前分配经过此通道的人数
            }
            u, v = e["from"], e["to"]
            if u in self.adjacency:
                self.adjacency[u].append(e["id"])
            if v in self.adjacency:
                self.adjacency[v].append(e["id"])

    def get_exits(self) -> List[str]:
        """获取所有安全出口及避难平台节点ID"""
        return [
            nid for nid, node in self.nodes.items()
            if node.get("zone_type") in ("safe_exit", "refuge_platform")
        ]

    def update_edge_hazard(
        self,
        edge_id: str,
        fire_risk: float = 0.0,
        smoke_risk: float = 0.0,
        is_blocked: bool = False
    ):
        """动态更新通道危险度"""
        if edge_id in self.edges:
            self.edges[edge_id]["risk_fire"] = max(0.0, min(1.0, fire_risk))
            self.edges[edge_id]["risk_smoke"] = max(0.0, min(1.0, smoke_risk))
            self.edges[edge_id]["is_blocked"] = is_blocked

    def update_sensors_for_act(self, act_key: str):
        """根据当前演练幕态势动态模拟物联网传感器读数与告警状态"""
        self.cost_network.set_stage_by_act(act_key)
        for s in self.sensors:
            sid = s.get("id")
            if act_key == "ACT_1_NORMAL":
                if sid == "S_SMOKE_EAST":
                    s["current_value"] = 10.0
                    s["ppm"] = 10.0
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_TEMP_EAST":
                    s["current_value"] = 23.8
                    s["value"] = 23.8
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_FLAME_REBAR":
                    s["current_value"] = 0.02
                    s["value"] = 0.02
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_SMOKE_CORE":
                    s["current_value"] = 15.0
                    s["ppm"] = 15.0
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_WIDTH_WEST":
                    s["current_value"] = 1.40
                    s["value"] = 1.40
                    s["status"] = "NORMAL"
                    s["status_text"] = "合规"
                elif sid == "S_TEMP_WOOD":
                    s["current_value"] = 24.5
                    s["value"] = 24.5
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_SMOKE_WOOD":
                    s["current_value"] = 12.0
                    s["ppm"] = 12.0
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_CO_PAINT":
                    s["current_value"] = 4.0
                    s["ppm"] = 4.0
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"

            elif act_key == "ACT_2_FIRE":
                if sid == "S_SMOKE_EAST":
                    s["current_value"] = 480.0
                    s["ppm"] = 480.0
                    s["status"] = "ALARM"
                    s["status_text"] = "极高危浓烟"
                elif sid == "S_TEMP_EAST":
                    s["current_value"] = 88.5
                    s["value"] = 88.5
                    s["status"] = "ALARM"
                    s["status_text"] = "高温过火"
                elif sid == "S_FLAME_REBAR":
                    s["current_value"] = 2.85
                    s["value"] = 2.85
                    s["status"] = "ALARM"
                    s["status_text"] = "明火爆燃"
                elif sid == "S_SMOKE_CORE":
                    s["current_value"] = 86.0
                    s["ppm"] = 86.0
                    s["status"] = "WARNING"
                    s["status_text"] = "烟囱扩散"
                elif sid == "S_WIDTH_WEST":
                    s["current_value"] = 1.38
                    s["value"] = 1.38
                    s["status"] = "NORMAL"
                    s["status_text"] = "合规"
                elif sid == "S_TEMP_WOOD":
                    s["current_value"] = 25.2
                    s["value"] = 25.2
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_SMOKE_WOOD":
                    s["current_value"] = 18.0
                    s["ppm"] = 18.0
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_CO_PAINT":
                    s["current_value"] = 8.0
                    s["ppm"] = 8.0
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"

            elif act_key == "ACT_3_BLOCKAGE":
                if sid == "S_WIDTH_WEST":
                    s["current_value"] = 0.35
                    s["value"] = 0.35
                    s["status"] = "BLOCKED"
                    s["status_text"] = "通道阻断 (净宽违背GB/T 50720)"
                elif sid == "S_SMOKE_EAST":
                    s["current_value"] = 390.0
                    s["ppm"] = 390.0
                    s["status"] = "ALARM"
                    s["status_text"] = "持续浓烟"
                elif sid == "S_TEMP_EAST":
                    s["current_value"] = 76.0
                    s["value"] = 76.0
                    s["status"] = "ALARM"
                    s["status_text"] = "持续高温"
                elif sid == "S_FLAME_REBAR":
                    s["current_value"] = 1.20
                    s["value"] = 1.20
                    s["status"] = "ALARM"
                    s["status_text"] = "局部明火"
                elif sid == "S_SMOKE_CORE":
                    s["current_value"] = 92.0
                    s["ppm"] = 92.0
                    s["status"] = "WARNING"
                    s["status_text"] = "烟囱警戒"
                elif sid == "S_TEMP_WOOD":
                    s["current_value"] = 25.8
                    s["value"] = 25.8
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_SMOKE_WOOD":
                    s["current_value"] = 20.0
                    s["ppm"] = 20.0
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"
                elif sid == "S_CO_PAINT":
                    s["current_value"] = 11.0
                    s["ppm"] = 11.0
                    s["status"] = "NORMAL"
                    s["status_text"] = "正常"


    def get_edge_between(self, u: str, v: str) -> Optional[Dict]:
        for eid in self.adjacency.get(u, []):
            e = self.edges[eid]
            if (e["from"] == u and e["to"] == v) or (e["from"] == v and e["to"] == u):
                return e
        return None

    def find_static_shortest_distance(self, start_node: str, target_exits: Optional[List[str]] = None) -> float:
        """计算无火灾理想状态下的理论静态最短物理距离 (论文路径效率基准分母)"""
        if start_node not in self.nodes:
            return 1.0
        if target_exits is None:
            target_exits = self.get_exits()

        pq = [(0.0, start_node)]
        dist = {start_node: 0.0}
        while pq:
            d, u = heapq.heappop(pq)
            if u in target_exits:
                return round(d, 2)
            if d > dist.get(u, float("inf")):
                continue
            for eid in self.adjacency.get(u, []):
                e = self.edges[eid]
                v = e["to"] if e["from"] == u else e["from"]
                w = e["base_length"]
                if d + w < dist.get(v, float("inf")):
                    dist[v] = d + w
                    heapq.heappush(pq, (d + w, v))
        return 1.0

    def calculate_edge_cost(self, edge: Dict) -> Tuple[float, bool]:
        """
        基于田傲、张健钦等 (2026)《系统仿真学报》多物理场综合风险场与动态代价网络模型
        计算单条边的动态综合代价 (Cost) (式 5, 8, 9)
        """
        # 1. 规范与几何合规性校验 (GB/T 50720 强制性标准)
        is_ok, reason, penalty = self.standards_engine.evaluate_edge_passability(
            edge_type=edge.get("edge_type", "structure"),
            current_width=edge.get("width_m", 1.2),
            is_blocked=edge.get("is_blocked", False),
            has_guardrail=edge.get("has_guardrail", True)
        )
        if not is_ok:
            edge["dynamic_cost_density"] = float("inf")
            edge["composite_risk"] = 1.0
            return float("inf"), False

        # 2. 火情硬隔离阈值拦截 (论文 Table 2: 皮肤耐受极限65℃ / 火灾危险度>=0.8视为直接过火区)
        if edge.get("risk_fire", 0.0) >= 0.8:
            edge["dynamic_cost_density"] = float("inf")
            edge["composite_risk"] = 1.0
            return float("inf"), False

        # 3. 关联传感器实测物理量提取 (温度 T, 能见度 V, 一氧化碳 CO)
        u, v = edge["from"], edge["to"]
        t_val = 23.5
        v_val = 30.0
        co_val = 5.0

        for s in self.sensors:
            nid = s.get("node_id")
            if nid in (u, v):
                stype = s.get("type")
                sval = float(s.get("current_value", s.get("value", s.get("ppm", 0.0))))
                if stype == "temp_c":
                    t_val = max(t_val, sval)
                elif stype == "smoke":
                    # 烟雾浓度 ppm 越高，能见度越低 (8m 为疏散识别临界下限)
                    est_vis = max(4.0, 30.0 - (sval / 20.0))
                    v_val = min(v_val, est_vis)
                elif stype == "co_ppm":
                    co_val = max(co_val, sval)

        # 叠加边火灾与烟雾扩散插值
        if edge.get("risk_fire", 0.0) > 0.0:
            t_val = max(t_val, 24.0 + edge["risk_fire"] * 70.0)
        if edge.get("risk_smoke", 0.0) > 0.0:
            v_val = min(v_val, max(4.0, 30.0 - edge["risk_smoke"] * 24.0))
            co_val = max(co_val, edge["risk_smoke"] * 480.0)

        # 4. 调用论文动态代价网络模型计算综合风险场与动态代价 (式 5, 8, 9)
        node_cost, comp_risk, dyn_w, impassable = self.cost_network.compute_composite_risk_field(
            temp_c=t_val,
            visibility_m=v_val,
            co_ppm=co_val
        )

        if impassable:
            edge["dynamic_cost_density"] = float("inf")
            edge["composite_risk"] = 1.0
            edge["dynamic_weights"] = dyn_w
            return float("inf"), False

        # 5. 出口防踩踏人流负载因子 (动态调节)
        crowd_factor = (edge.get("allocated_crowd", 0) * 0.15)

        # 6. 综合路径代价值计算 (物理长度 * 动态代价因子 * 人流修正 + 规范惩罚)
        base_l = edge["base_length"]
        total_edge_cost = base_l * node_cost * (1.0 + crowd_factor) + (penalty - 1.0)

        edge["dynamic_cost_density"] = node_cost
        edge["composite_risk"] = comp_risk
        edge["dynamic_weights"] = dyn_w
        edge["temp_c"] = round(t_val, 1)
        edge["visibility_m"] = round(v_val, 1)
        edge["co_ppm"] = round(co_val, 1)

        return round(total_edge_cost, 2), True

    def find_shortest_evacuation_path(
        self,
        start_node: str,
        target_exits: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        基于改进动态 A* 算法寻找逃生路径 (论文式 10 改进启发函数)
        返回包含路径节点、7项科学指标在内的完整决策结果
        """
        if start_node not in self.nodes:
            return None

        if target_exits is None:
            target_exits = self.get_exits()

        # 计算地图当前最大通行代价 max(cost)，用于启发函数归一化 (论文式 10)
        valid_densities = [
            e.get("dynamic_cost_density", 1.0) for e in self.edges.values()
            if not math.isinf(e.get("dynamic_cost_density", 1.0))
        ]
        max_cost_in_map = max(valid_densities, default=1.0)

        # 优先队列: (priority_f, current_cost_g, current_node, path, edges_used)
        pq: List[Tuple[float, float, str, List[str], List[str]]] = []
        heapq.heappush(pq, (0.0, 0.0, start_node, [start_node], []))
        visited: Dict[str, float] = {}

        def base_heuristic(n_id: str) -> float:
            """欧式距离基础启发式下界"""
            cur_c = self.nodes[n_id]["coords"]
            min_dist = float("inf")
            for ex in target_exits:
                ex_c = self.nodes[ex]["coords"]
                d = math.hypot(cur_c["x"] - ex_c["x"], cur_c["y"] - ex_c["y"]) * 0.1
                if d < min_dist:
                    min_dist = d
            return min_dist

        best_result = None

        while pq:
            f, g, u, path, edges_used = heapq.heappop(pq)

            if u in target_exits:
                # 收集沿线各边参数
                edge_objs = [self.edges[eid] for eid in edges_used]
                tot_dist = round(sum(e["base_length"] for e in edge_objs), 2)

                # 论文 7 项科学评价指标计算
                # 1) 静态最短理论距离与路径效率 eta (论文式 4)
                static_best_dist = self.find_static_shortest_distance(start_node, target_exits)
                path_efficiency = round(tot_dist / max(1.0, static_best_dist), 2)

                # 2) 最大通行代价与平均通行代价 (论文表 4, 表 5)
                densities = [e.get("dynamic_cost_density", 1.0) for e in edge_objs]
                max_passage_cost = round(max(densities, default=1.0), 2)
                avg_passage_cost = round(sum(densities) / max(1, len(densities)), 2)

                # 3) 能见度削减步速模型下的真实逃生时间 (论文第 2.3 节基准步速 1.2m/s)
                est_time = 0.0
                for e in edge_objs:
                    vis = e.get("visibility_m", 30.0)
                    c_v, _ = self.cost_network.normalize_physical_field(vis, "visibility")
                    speed = 1.2 * max(0.4, 1.0 - 0.5 * c_v)  # 浓烟降速模型
                    est_time += e["base_length"] / speed
                est_time = round(est_time, 1)

                # 4) 路径平滑度：转向角 >= 35° 的拐点数量 (论文第 3 节)
                path_coords = [(self.nodes[nid]["coords"]["x"], self.nodes[nid]["coords"]["y"]) for nid in path]
                inflexion_count = self.cost_network.calculate_path_inflexion_points(path_coords, threshold_deg=35.0)

                best_result = {
                    "start_node": start_node,
                    "target_exit": u,
                    "exit_name": self.nodes[u]["name"],
                    "path_nodes": path,
                    "edge_ids": edges_used,
                    "total_cost": round(g, 2),
                    "total_distance": tot_dist,
                    "est_time_sec": est_time,
                    "status": "SUCCESS",
                    "scientific_metrics": {
                        "path_efficiency": path_efficiency,
                        "static_shortest_m": static_best_dist,
                        "max_cost": max_passage_cost,
                        "avg_cost": avg_passage_cost,
                        "inflexion_points": inflexion_count,
                        "speed_reduction_ratio": round(tot_dist / (1.2 * max(0.1, est_time)), 2)
                    }
                }
                break

            if u in visited and visited[u] <= g:
                continue
            visited[u] = g

            # 遍历邻接边
            for eid in self.adjacency.get(u, []):
                edge = self.edges[eid]
                v = edge["to"] if edge["from"] == u else edge["from"]

                cost, passable = self.calculate_edge_cost(edge)
                if not passable or math.isinf(cost):
                    continue

                new_g = g + cost

                # 论文式 10 核心创新：代价感知改进启发函数 h_d(n)
                # h_d(n) = h(n) * (1 + cost(n) / max(cost))
                node_cost_v = edge.get("dynamic_cost_density", 1.0)
                improved_h = self.cost_network.compute_improved_heuristic(
                    h_euclidean=base_heuristic(v),
                    current_node_cost=node_cost_v,
                    max_map_cost=max_cost_in_map
                )

                new_f = new_g + improved_h
                heapq.heappush(pq, (new_f, new_g, v, path + [v], edges_used + [eid]))

        return best_result

    def evaluate_local_replanning_trigger(
        self,
        current_path_edge_ids: List[str],
        risk_threshold: float = 0.5
    ) -> Tuple[bool, str]:
        """
        局部火险变化检测 (论文第1.3节 局部重规划):
        对当前规划路径前方的边代价值变化进行比对。若超出安全容差则触发局部增量重规划。
        """
        for eid in current_path_edge_ids:
            e = self.edges.get(eid)
            if not e:
                continue
            if e.get("is_blocked", False) or e.get("risk_fire", 0.0) >= 0.8:
                return True, f"通道 {eid} 发生物理阻断或极高危过火，强制触发重规划"
            if e.get("composite_risk", 0.0) >= risk_threshold:
                return True, f"通道 {eid} 综合风险场升至警戒值({e['composite_risk']:.2f})，触发局部路径优化"
        return False, "沿途火险在容差阈值内，无需重规划，维持原路径"

    def plan_all_workers(self) -> Dict:
        """
        基于动态代价网络与改进 A* 统一计算全场工友逃生路线，输出 7 项科学指标与合规报告
        """
        start_replan_clock = time.perf_counter()

        # 清除已分配人流
        for e in self.edges.values():
            e["allocated_crowd"] = 0

        routes = []
        for worker in self.workers:
            res = self.find_shortest_evacuation_path(worker["current_node"])
            if res:
                # 增加沿途边的拥挤度，促使后续工友自动负载均衡至备选出口
                for eid in res["edge_ids"]:
                    self.edges[eid]["allocated_crowd"] += 1

                routes.append({
                    "worker_id": worker["id"],
                    "worker_name": worker["name"],
                    "worker_role": worker["role"],
                    "device": worker.get("device", "智能工牌"),
                    "start_node": worker["current_node"],
                    "target_exit": res["target_exit"],
                    "exit_name": res["exit_name"],
                    "path": res["path_nodes"],
                    "edge_ids": res["edge_ids"],
                    "distance_m": res["total_distance"],
                    "est_time_sec": res["est_time_sec"],
                    "status": "ROUTE_READY",
                    "scientific_metrics": res["scientific_metrics"]
                })
            else:
                routes.append({
                    "worker_id": worker["id"],
                    "worker_name": worker["name"],
                    "worker_role": worker["role"],
                    "device": worker.get("device", "智能工牌"),
                    "start_node": worker["current_node"],
                    "target_exit": None,
                    "exit_name": "无可用通路 (请求外部特勤救援)",
                    "path": [],
                    "edge_ids": [],
                    "distance_m": 0.0,
                    "est_time_sec": 0.0,
                    "status": "TRAPPED_REQUEST_RESCUE",
                    "scientific_metrics": {
                        "path_efficiency": 0.0,
                        "static_shortest_m": 0.0,
                        "max_cost": float("inf"),
                        "avg_cost": float("inf"),
                        "inflexion_points": 0,
                        "speed_reduction_ratio": 0.0
                    }
                })

        compute_latency_ms = round((time.perf_counter() - start_replan_clock) * 1000, 3)

        # 统计出口人流分布与出口利用率
        used_exits = [r["target_exit"] for r in routes if r["target_exit"]]
        exits_summary = {}
        for ex in used_exits:
            exits_summary[ex] = exits_summary.get(ex, 0) + 1

        compliance = self.standards_engine.generate_safety_compliance_report(
            evac_routes=routes,
            exits_used=used_exits
        )

        ready_routes = [r for r in routes if r["status"] == "ROUTE_READY"]
        avg_efficiency = round(
            sum(r["scientific_metrics"]["path_efficiency"] for r in ready_routes) / max(1, len(ready_routes)), 2
        )
        max_cost_all = round(
            max([r["scientific_metrics"]["max_cost"] for r in ready_routes], default=1.0), 2
        )
        avg_cost_all = round(
            sum(r["scientific_metrics"]["avg_cost"] for r in ready_routes) / max(1, len(ready_routes)), 2
        )
        total_inflexions = sum(r["scientific_metrics"]["inflexion_points"] for r in ready_routes)

        # 7 项科学评价体系汇总
        scientific_evaluation = {
            "methodology_reference": "面向室内火灾应急疏散的动态代价网络模型",
            "algorithm": "改进动态 A* 算法 (代价感知启发函数 hd(n) + 动态权重综合风险场)",
            "fire_stage": self.cost_network.current_stage,
            "stage_name": {"initial": "初始期", "spread": "蔓延期", "fully_developed": "全面期"}[self.cost_network.current_stage],
            "dynamic_weights": self.cost_network.STAGE_WEIGHTS[self.cost_network.current_stage],
            "replan_latency_ms": compute_latency_ms,
            "mean_path_efficiency": avg_efficiency,
            "max_passage_cost": max_cost_all,
            "mean_passage_cost": avg_cost_all,
            "total_inflexion_points": total_inflexions,
            "exit_utilization": {
                ex: f"{round(count / len(routes) * 100, 1)}%" for ex, count in exits_summary.items()
            }
        }

        return {
            "routes": routes,
            "compliance_audit": compliance,
            "scientific_evaluation": scientific_evaluation,
            "total_workers": len(self.workers),
            "evacuation_ready_count": len(ready_routes)
        }
