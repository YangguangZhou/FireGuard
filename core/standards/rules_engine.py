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
