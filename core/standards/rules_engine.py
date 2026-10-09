"""
GB/T 50720-2011 建设工程施工现场消防安全技术标准 规则引擎
包含规范条文约束校验、烟火动态风险评估模型与合规性判定
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class CorridorStandard:
    """临时疏散通道规范参数 (GB/T 50720-2011 第4.3.2条)"""
    MIN_WIDTH_GROUND: float = 1.5       # 地面设置临时疏散通道净宽 >= 1.5m
    MIN_WIDTH_STRUCTURE: float = 1.0    # 利用已施工结构、楼梯净宽 >= 1.0m
    MIN_WIDTH_SCAFFOLD: float = 0.6     # 爬梯及脚手架临时通道净宽 >= 0.6m
    MAX_ROOM_EVAC_DIST: float = 15.0    # 临时用房房间任一点至最近疏散门 <= 15m
    MAX_HAZARD_EVAC_DIST: float = 10.0  # 易燃易爆/危险品用房疏散门距离 <= 10m
    MIN_GUARDRAIL_HEIGHT: float = 1.2   # 临空面防护栏杆高度 >= 1.2m


class ConstructionFireStandardsEngine:
    """
    施工现场消防规范规则引擎
    将国家强制性标准转化为智能体路径权值与决策约束
    """

    def __init__(self):
        self.std = CorridorStandard()

    def evaluate_edge_passability(
        self,
        edge_type: str,
        current_width: float,
        is_blocked: bool,
        has_guardrail: bool = True
    ) -> Tuple[bool, str, float]:
        """
        根据GB/T 50720校验通道通行合规性
        
        Args:
            edge_type: 通道类型 ('ground', 'structure', 'scaffold_ladder', 'temporary_bridge')
            current_width: 当前实测有效净宽 (米)
            is_blocked: 是否存在建筑垃圾/模板堆放阻断
            has_guardrail: 临空面是否有防护栏杆
            
        Returns:
            (is_compliant, reason_description, penalty_factor)
        """
        if is_blocked:
            return False, "通道被建材/施工机械完全阻断，禁止通行", float("inf")

        min_req_width = self.std.MIN_WIDTH_STRUCTURE
        if edge_type == "ground":
            min_req_width = self.std.MIN_WIDTH_GROUND
        elif edge_type in ("scaffold_ladder", "climbing_ladder"):
            min_req_width = self.std.MIN_WIDTH_SCAFFOLD

        if current_width < min_req_width:
            return (
                False,
                f"通道净宽({current_width}m)低于GB/T 50720强制标准({min_req_width}m)，存在挤压窒息隐患",
                float("inf")
            )

        if edge_type in ("scaffold_ladder", "temporary_bridge") and not has_guardrail:
            return (
                False,
                f"临空面未设不小于{self.std.MIN_GUARDRAIL_HEIGHT}m防护栏杆，禁止作为主力疏散通道",
                100.0  # 极高惩罚，仅在绝境下备用
            )

        # 净宽充裕度良好
        return True, "符合GB/T 50720疏散通道净宽与防护标准", 1.0

    def calculate_smoke_diffusion_risk(
        self,
        distance_to_fire: float,
        elapsed_seconds: float,
        is_shaft_or_opening: bool = False,
        wind_direction_align: float = 0.0
    ) -> float:
        """
        施工现场烟气蔓延简易物理模型
        水平方向扩散速度: 0.5 - 0.8 m/s
        竖向空洞/未封堵井道烟囱效应扩散速度: 3.0 - 5.0 m/s
        
        Returns:
            smoke_risk: 0.0 (无烟) ~ 1.0 (重度浓烟窒息区)
        """
        if is_shaft_or_opening:
            spread_velocity = 3.5  # 烟囱效应强扩散
        else:
            spread_velocity = 0.6 * (1.0 + max(0.0, wind_direction_align) * 0.5)

        estimated_front = spread_velocity * elapsed_seconds
        
        if distance_to_fire <= estimated_front * 0.6:
            return 1.0  # 核心浓烟区
        elif distance_to_fire <= estimated_front:
            # 烟羽前锋区
            decay = (estimated_front - distance_to_fire) / (estimated_front * 0.4 + 1e-5)
            return min(1.0, max(0.0, 0.4 + 0.6 * decay))
        elif distance_to_fire <= estimated_front + 8.0:
            # 潜在扩散威胁区
            return 0.2
        return 0.0

    def generate_safety_compliance_report(
        self,
        evac_routes: List[Dict],
        exits_used: List[str]
    ) -> Dict:
        """
        依据GB 50016与GB/T 50720生成疏散合规性审计摘要
        """
        num_exits = len(set(exits_used))
        dual_exit_compliant = num_exits >= 2 if len(evac_routes) > 2 else True

        max_dist = max([r.get("distance_m", r.get("total_distance", 0.0)) for r in evac_routes], default=0.0)

        issues = []
        if not dual_exit_compliant:
            issues.append("警告：当前方案所有人员汇流至单一安全出口，违反GB 50016双出口分流原则")
        if max_dist > 35.0:
            issues.append(f"注意：最大疏散距离({max_dist:.1f}m)接近在建工程安全冗余阈值，需加速下撤")

        return {
            "standards_version": "GB/T 50720-2011 / GB 50016-2014(2018版)",
            "dual_exit_compliant": dual_exit_compliant,
            "max_evac_distance_m": round(max_dist, 2),
            "compliance_status": "COMPLIANT" if not issues else "WARNING",
            "audit_notes": issues if issues else ["全部规划路线均满足施工现场安全疏散净宽与分流规范"]
        }


# =========================================================================
# 基于田傲、张健钦等 (2026)《系统仿真学报》论文
# 面向室内火灾应急疏散的动态代价网络与智能体寻径科学计算模型
# =========================================================================

class DynamicFireCostNetwork:
    """
    火灾多物理场综合风险场与动态代价网络引擎
    参考文献: 田傲, 张健钦, 文政, 等. 面向室内火灾应急疏散的智能体寻径方法研究[J]. 系统仿真学报, 2026, 38(2): 532-543.
    """

    # 火灾三阶段静态权重参考值 (Table 1)
    STAGE_WEIGHTS = {
        "initial": {"temp": 0.25, "visibility": 0.55, "co": 0.20, "alpha": 0.5},       # 初始期 (能见度主导)
        "spread": {"temp": 0.50, "visibility": 0.30, "co": 0.20, "alpha": 1.2},        # 蔓延期 (温度主导)
        "fully_developed": {"temp": 0.30, "visibility": 0.20, "co": 0.50, "alpha": 2.0} # 全面期 (有毒CO主导)
    }

    # 物理量极差归一化区间 (Section 1.2.1, Table 2)
    LIMITS = {
        "temp": {"min": 20.0, "max": 65.0, "critical": 65.0},      # ℃ (皮肤耐受极限65℃，超此极限禁行)
        "visibility": {"min": 8.0, "max": 30.0, "critical": 8.0},  # m (路径识别临界值8m，低于此极限禁行)
        "co": {"min": 0.0, "max": 550.0, "critical": 550.0}        # ppm (CO中毒致死临界值550ppm，超此极限禁行)
    }

    def __init__(self, current_stage: str = "initial"):
        self.current_stage = current_stage if current_stage in self.STAGE_WEIGHTS else "initial"

    def set_stage_by_act(self, act_key: str):
        """映射系统当前演练阶段至火灾动力学阶段"""
        if act_key == "ACT_1_NORMAL":
            self.current_stage = "initial"
        elif act_key == "ACT_2_FIRE":
            self.current_stage = "spread"
        elif act_key == "ACT_3_BLOCKAGE":
            self.current_stage = "fully_developed"
        else:
            self.current_stage = "initial"

    def normalize_physical_field(self, value: float, field_type: str) -> Tuple[float, bool]:
        """
        对物理场进行极差归一化计算 (式 4)
        Returns: (normalized_risk_value [0, 1], is_impassable)
        """
        lim = self.LIMITS[field_type]
        if field_type == "temp":
            if value >= lim["critical"]:
                return 1.0, True
            val = max(lim["min"], min(lim["max"], value))
            return (val - lim["min"]) / (lim["max"] - lim["min"]), False

        elif field_type == "co":
            if value >= lim["critical"]:
                return 1.0, True
            val = max(lim["min"], min(lim["max"], value))
            return (val - lim["min"]) / (lim["max"] - lim["min"]), False

        elif field_type == "visibility":
            # 能见度为负向风险 (式 4): 越低越危险
            if value <= lim["critical"]:
                return 1.0, True
            val = max(lim["min"], min(lim["max"], value))
            return (lim["max"] - val) / (lim["max"] - lim["min"]), False

        return 0.0, False

    def calculate_dynamic_weights(
        self,
        c_temp: float,
        c_vis: float,
        c_co: float
    ) -> Dict[str, float]:
        """
        基于初始权重与动态风险场计算各风险因子的动态权重 (式 6, 7)
        \\varpi_z = \\omega^i_z * s_z, \\omega_z = \\varpi_z / sum(\\varpi)
        """
        base_w = self.STAGE_WEIGHTS[self.current_stage]
        varpi_t = base_w["temp"] * (c_temp + 1e-4)
        varpi_v = base_w["visibility"] * (c_vis + 1e-4)
        varpi_co = base_w["co"] * (c_co + 1e-4)

        total_varpi = varpi_t + varpi_v + varpi_co
        if total_varpi <= 1e-5:
            return {"temp": base_w["temp"], "visibility": base_w["visibility"], "co": base_w["co"]}

        return {
            "temp": round(varpi_t / total_varpi, 4),
            "visibility": round(varpi_v / total_varpi, 4),
            "co": round(varpi_co / total_varpi, 4)
        }

    def compute_composite_risk_field(
        self,
        temp_c: float = 24.0,
        visibility_m: float = 30.0,
        co_ppm: float = 5.0
    ) -> Tuple[float, float, Dict[str, float], bool]:
        """
        计算综合风险场 S(x,y,t) 与动态路径代价值 cost[i,j,t] (式 5, 8, 9)
        Returns:
            (cost, composite_risk, dynamic_weights, is_impassable)
        """
        # 1. 极差归一化
        c_t, imp_t = self.normalize_physical_field(temp_c, "temp")
        c_v, imp_v = self.normalize_physical_field(visibility_m, "visibility")
        c_co, imp_co = self.normalize_physical_field(co_ppm, "co")

        # 若达到任一致命阈值，判定为绝对禁行 (式 8, Table 2)
        if imp_t or imp_v or imp_co:
            return float("inf"), 1.0, {"temp": 0.33, "visibility": 0.33, "co": 0.34}, True

        # 2. 动态权重分配 (式 6, 7)
        dyn_w = self.calculate_dynamic_weights(c_t, c_v, c_co)

        # 3. 综合风险场 S(x,y,t) (式 5)
        composite_risk = dyn_w["temp"] * c_t + dyn_w["visibility"] * c_v + dyn_w["co"] * c_co
        composite_risk = max(0.0, min(1.0, composite_risk))

        # 4. 全局调节因子与环境紧急度系数 (式 9)
        alpha = self.STAGE_WEIGHTS[self.current_stage]["alpha"]
        max_physical_risk = max(c_t, c_v, c_co)
        lam = 1.0 + alpha * max_physical_risk

        # 5. 动态路径代价值 (式 8, 基础代价为1.0)
        node_cost = 1.0 + lam * composite_risk
        return round(node_cost, 4), round(composite_risk, 4), dyn_w, False

    def compute_improved_heuristic(
        self,
        h_euclidean: float,
        current_node_cost: float,
        max_map_cost: float
    ) -> float:
        """
        代价感知改进启发函数 (式 10)
        h_d(n) = h(n) * (1 + cost(n) / max(cost))
        """
        max_c = max(1.0, max_map_cost)
        ratio = max(0.0, current_node_cost / max_c)
        return h_euclidean * (1.0 + ratio)

    def calculate_path_inflexion_points(self, coords_list: List[Tuple[float, float]], threshold_deg: float = 35.0) -> int:
        """
        统计路径平滑度指标：转向角 >= 35° 的拐点数量 (论文第3节指标)
        """
        if len(coords_list) < 3:
            return 0

        inflexion_count = 0
        import math
        for i in range(1, len(coords_list) - 1):
            p_prev = coords_list[i - 1]
            p_curr = coords_list[i]
            p_next = coords_list[i + 1]

            v1 = (p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])
            v2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])

            mag1 = math.hypot(v1[0], v1[1])
            mag2 = math.hypot(v2[0], v2[1])
            if mag1 < 1e-4 or mag2 < 1e-4:
                continue

            dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (mag1 * mag2)
            dot = max(-1.0, min(1.0, dot))
            angle_deg = math.degrees(math.acos(dot))
            if angle_deg >= threshold_deg:
                inflexion_count += 1

        return inflexion_count

