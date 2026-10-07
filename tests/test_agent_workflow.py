"""
FireGuard 智能体端到端决策工作流自动化测试套件
验证三幕剧场景演变下的确定性寻路、避障与合规性
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.agent.fire_guard_agent import FireGuardAgent
from core.graph.topology import ConstructionGraph


class TestFireGuardWorkflow(unittest.TestCase):

    def setUp(self):
        self.agent = FireGuardAgent(
            site_map_path=os.path.join(PROJECT_ROOT, "data", "site_maps", "floor_level_3.json")
        )

    def test_act1_normal_evacuation(self):
        """测试第一幕：常态作业巡检，所有工友均有安全出口且符合GB/T 50720"""
        res = self.agent.handle_incident("ACT_1_NORMAL")
        self.assertEqual(res["act"], "ACT_1_NORMAL")
        self.assertFalse(res["perception"]["fire_detected"])
        routes = res["plan"]["routes"]
        self.assertEqual(len(routes), 4)

        # 检查所有人员都已规划完成
        for r in routes:
            self.assertEqual(r["status"], "ROUTE_READY")
            self.assertGreater(len(r["path"]), 1)
            self.assertIn(r["target_exit"], ["EXIT_EAST", "EXIT_WEST", "EXIT_REFUGE"])

        # 检查GB/T 50720 合规性
        compliance = res["plan"]["compliance_audit"]
        self.assertEqual(compliance["compliance_status"], "COMPLIANT")
        self.assertTrue(compliance["dual_exit_compliant"])

    def test_act2_fire_rerouting(self):
        """测试第二幕：东干道突发火情，出口A必须被完全切断，人员自动避难至出口B或避难平台"""
        res = self.agent.handle_incident("ACT_2_FIRE")
        self.assertEqual(res["act"], "ACT_2_FIRE")
        self.assertTrue(res["perception"]["fire_detected"])

        routes = res["plan"]["routes"]
        for r in routes:
            if r["status"] == "ROUTE_READY":
                # 严禁任何人继续前往被火封锁的 EXIT_EAST
                self.assertNotEqual(r["target_exit"], "EXIT_EAST", f"Worker {r['worker_id']} was directed to fire-blocked EXIT_EAST!")
                self.assertNotIn("E_REBAR_EXITEAST", r["edge_ids"])

        # 确认语音指令已生成
        broadcasts = res["broadcasts"]
        self.assertEqual(len(broadcasts), 4)
        for b in broadcasts:
            self.assertIn("audio_script", b)
            self.assertIn("师傅", b["audio_script"])

    def test_act3_scaffold_blockage_secondary_reroute(self):
        """测试第三幕：西侧外架爬梯坍塌受阻，智能体二次重规划调流至南立面避难平台C"""
        # 先触发火情，再触发次生阻断
        self.agent.handle_incident("ACT_2_FIRE")
        res = self.agent.handle_incident("ACT_3_BLOCKAGE")
        self.assertEqual(res["act"], "ACT_3_BLOCKAGE")

        routes = res["plan"]["routes"]
        for r in routes:
            if r["status"] == "ROUTE_READY":
                # 西侧通道已塌陷，禁止走 EXIT_WEST 的通道
                self.assertNotIn("E_WCORR_EXITWEST", r["edge_ids"])

        # 生成正式报告验证
        report = self.agent.export_formal_emergency_report()
        self.assertIn("report_id", report)
        self.assertEqual(report["current_scenario_state"], "ACT_3_BLOCKAGE")


if __name__ == "__main__":
    unittest.main()
