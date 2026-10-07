"""
FireGuard 施工现场动态拓扑图与高可靠加权 A* 寻路算法
确保 100% 绕开火源禁行区、避开高浓烟通道，并满足 GB/T 50720 疏散规范
"""

import heapq
import json
import math
from typing import Dict, List, Optional, Set, Tuple

from core.standards.rules_engine import ConstructionFireStandardsEngine


class ConstructionGraph:
    """施工现场拓扑连通图与动态权值计算"""

    def __init__(self, site_json_path: Optional[str] = None, data_dict: Optional[Dict] = None):
        self.standards_engine = ConstructionFireStandardsEngine()
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

    def get_edge_between(self, u: str, v: str) -> Optional[Dict]:
        for eid in self.adjacency.get(u, []):
            e = self.edges[eid]
            if (e["from"] == u and e["to"] == v) or (e["from"] == v and e["to"] == u):
                return e
        return None

    def calculate_edge_cost(self, edge: Dict) -> Tuple[float, bool]:
        """
        计算单条边的动态综合代价 (Cost)
        若违反国家规范或已被大火切断，返回 (inf, False)
        """
        # 1. 规范与几何合规性校验
        is_ok, reason, penalty = self.standards_engine.evaluate_edge_passability(
            edge_type=edge.get("edge_type", "structure"),
            current_width=edge.get("width_m", 1.2),
            is_blocked=edge.get("is_blocked", False),
            has_guardrail=edge.get("has_guardrail", True)
        )
        if not is_ok:
            return float("inf"), False

        # 2. 火情硬隔离：若该边火灾危险度 >= 0.8，视为直接过火区，绝对禁止通行
        if edge["risk_fire"] >= 0.8:
            return float("inf"), False

        base_l = edge["base_length"]
        # 3. 动态软权重修正：烟雾影响、初期轻微火情、通道拥挤度
        fire_factor = edge["risk_fire"] * 100.0  # 极力规避
        smoke_factor = edge["risk_smoke"] * 6.0   # 烟雾减速与风险倍率
        crowd_factor = (edge["allocated_crowd"] * 0.15)  # 避免出口通道踩踏

        cost = base_l * (1.0 + fire_factor + smoke_factor + crowd_factor) + (penalty - 1.0)
        return cost, True

    def find_shortest_evacuation_path(
        self,
        start_node: str,
        target_exits: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        加权 A* / 多目标 Dijkstra 寻找从起点到任意可用安全出口的最优路径
        返回包含路径节点、总物理距离、总通行代价和健康安全评级的结果
        """
        if start_node not in self.nodes:
            return None

        if target_exits is None:
            target_exits = self.get_exits()

        # 优先队列: (priority_f, current_cost_g, current_node, path, edges_used)
        pq: List[Tuple[float, float, str, List[str], List[str]]] = []
        heapq.heappush(pq, (0.0, 0.0, start_node, [start_node], []))
        visited: Dict[str, float] = {}

        def heuristic(n_id: str) -> float:
            """欧式距离启发式估算到最近出口的物理下界"""
            cur_c = self.nodes[n_id]["coords"]
            min_dist = float("inf")
            for ex in target_exits:
                ex_c = self.nodes[ex]["coords"]
                d = math.hypot(cur_c["x"] - ex_c["x"], cur_c["y"] - ex_c["y"]) * 0.1  # 缩放因子
                if d < min_dist:
                    min_dist = d
            return min_dist

        best_result = None

        while pq:
            f, g, u, path, edges_used = heapq.heappop(pq)

            if u in target_exits:
                best_result = {
                    "start_node": start_node,
                    "target_exit": u,
                    "exit_name": self.nodes[u]["name"],
                    "path_nodes": path,
                    "edge_ids": edges_used,
                    "total_cost": round(g, 2),
                    "total_distance": round(
                        sum(self.edges[eid]["base_length"] for eid in edges_used), 2
                    ),
                    "status": "SUCCESS"
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
                new_f = new_g + heuristic(v)
                heapq.heappush(pq, (new_f, new_g, v, path + [v], edges_used + [eid]))

        return best_result

    def plan_all_workers(self) -> Dict:
        """
        为全楼层工友统一计算逃生路线，并执行出口分流负载均衡
        """
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

                # 估算撤离时间：按烟雾修正后平均步速 1.1 m/s 计算
                est_time = round(res["total_distance"] / 1.1, 1)
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
                    "est_time_sec": est_time,
                    "status": "ROUTE_READY"
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
                    "status": "TRAPPED_REQUEST_RESCUE"
                })

        used_exits = [r["target_exit"] for r in routes if r["target_exit"]]
        compliance = self.standards_engine.generate_safety_compliance_report(
            evac_routes=routes,
            exits_used=used_exits
        )

        return {
            "routes": routes,
            "compliance_audit": compliance,
            "total_workers": len(self.workers),
            "evacuation_ready_count": len([r for r in routes if r["status"] == "ROUTE_READY"])
        }
