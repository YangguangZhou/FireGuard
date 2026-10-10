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

        # 检查物联网传感器与事件日志时序
        self.assertEqual(len(self.agent.graph.sensors), 8)
        self.assertEqual(len(self.agent.incident_log), 4)
        for s in self.agent.graph.sensors:
            self.assertEqual(s["status"], "NORMAL")

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

        # 检查火灾传感器异动与事件处置时序链
        smoke_east = next(s for s in self.agent.graph.sensors if s["id"] == "S_SMOKE_EAST")
        self.assertEqual(smoke_east["status"], "ALARM")
        self.assertEqual(smoke_east["current_value"], 480.0)

        temp_east = next(s for s in self.agent.graph.sensors if s["id"] == "S_TEMP_EAST")
        self.assertEqual(temp_east["status"], "ALARM")
        self.assertEqual(temp_east["current_value"], 88.5)

        self.assertEqual(len(self.agent.incident_log), 7)
        self.assertEqual(self.agent.incident_log[0]["event_type"], "IOT_SENSOR_TRIGGER")
        self.assertEqual(self.agent.incident_log[0]["sequence_id"], 1)
        self.assertEqual(self.agent.incident_log[6]["event_type"], "HELMET_BROADCAST")

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

        # 检查西连廊净宽传感器超标阻断与二次处置时序链
        width_west = next(s for s in self.agent.graph.sensors if s["id"] == "S_WIDTH_WEST")
        self.assertEqual(width_west["status"], "BLOCKED")
        self.assertEqual(width_west["current_value"], 0.35)

        self.assertEqual(len(self.agent.incident_log), 7)
        self.assertEqual(self.agent.incident_log[0]["event_type"], "IOT_CLEARANCE_ALARM")
        self.assertEqual(self.agent.incident_log[4]["event_type"], "DYNAMIC_REPLAN")
        self.assertEqual(self.agent.incident_log[6]["event_type"], "RESCUE_DISPATCH")

        # 生成正式报告验证
        report = self.agent.export_formal_emergency_report()
        self.assertIn("report_id", report)
        self.assertEqual(report["current_scenario_state"], "ACT_3_BLOCKAGE")

    def test_agent_copilot_chat(self):
        """测试安全总监 Copilot 自然语言对话交互 (Qwen 引擎驱动)"""
        ans1 = self.agent.query_agent_chat("当前哪个出口最安全？")
        self.assertTrue(any(k in ans1 for k in ["出口", "安全", "疏散", "GB"]))

        ans2 = self.agent.query_agent_chat("木工李伟班组撤离到了哪里？")
        self.assertTrue(len(ans2) > 10)

        ans3 = self.agent.query_agent_chat("当前方案是否符合GB/T 50720？")
        self.assertTrue(any(k in ans3 for k in ["50720", "规范", "合规", "标准"]))


if __name__ == "__main__":
    unittest.main()
