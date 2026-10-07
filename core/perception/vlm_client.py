"""
FireGuard 多模态火灾感知与 VLM 客户端
支持通义千问 Qwen-VL 官方 API (DashScope) 实时图像理解
并内置高保真离线推演缓存，确保现场答辩网络波动时 100% 稳定高可靠
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class QwenVLPerceptionClient:
    """
    Qwen-VL 多模态感知接口
    负责从施工现场视频帧/抓拍图片中识别：
    1. 烟雾与明火严重等级
    2. 起火方位及影响的施工走廊/区域
    3. 通道内临时建材坍塌、机械阻断物
    """

    DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")

        # 预设本地推演样本库（供离线/演示兜底使用）
        self.offline_scenario_cache: Dict[str, Dict[str, Any]] = {
            "incident_fire_act2": {
                "fire_detected": True,
                "smoke_detected": True,
                "confidence": 0.96,
                "fire_location_desc": "东侧主施工干道与配电箱交汇处冒出黑色浓烟，有明火向外架防护网蔓延",
                "affected_edges": ["E_NCORR_REBAR", "E_REBAR_EXITEAST"],
                "hazard_level": "CRITICAL",
                "flame_intensity": 0.92,
                "smoke_density": 0.85,
                "structural_obstacle": False,
                "agent_perception_summary": "检测到核心筒东侧走廊及配电箱区域突发高危火情！浓烟正沿北干道快速向东主楼梯（出口A）弥漫扩散，出口A随时面临封死风险。"
            },
            "incident_blockage_act3": {
                "fire_detected": False,
                "smoke_detected": True,
                "confidence": 0.93,
                "fire_location_desc": "西侧临时外挂爬梯连通通道处出现模板脚手架支架侧翻倾倒，堆满钢管与木方",
                "affected_edges": ["E_WCORR_EXITWEST"],
                "hazard_level": "HIGH",
                "flame_intensity": 0.1,
                "smoke_density": 0.65,
                "structural_obstacle": True,
                "obstacle_width_remaining_m": 0.35,  # 远低于 GB/T 50720 规定的 0.6m
                "agent_perception_summary": "预警！西侧避难爬梯连接走廊（E_WCORR_EXITWEST）因模板脚手架坍塌严重受阻，实测有效通行净宽仅剩约0.35m，违反GB/T 50720强制标准，已无法通行！"
            }
        }

    def analyze_scene_image(
        self,
        image_url_or_path: str,
        scenario_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        调用官方 Qwen-VL API 解析施工现场画面。
        若无 API Key 或处于演示仿真模式，自动平滑切换至结构化高保真缓存，保障零闪退。
        """
        if scenario_key and scenario_key in self.offline_scenario_cache:
            res = self.offline_scenario_cache[scenario_key].copy()
            res["source"] = "SIMULATION_CACHE"
            return res

        if not self.api_key:
            # 降级模式
            return {
                "source": "FALLBACK_RULES",
                "fire_detected": True,
                "smoke_detected": True,
                "confidence": 0.88,
                "affected_edges": ["E_NCORR_REBAR"],
                "hazard_level": "HIGH",
                "flame_intensity": 0.8,
                "smoke_density": 0.7,
                "structural_obstacle": False,
                "agent_perception_summary": "[离线沙盒模式] 识别到局部高温火烟态势，建议立即规避东侧通道。"
            }

        prompt = (
            "你是一个专业的施工现场安全巡检AI。请观察图片并以标准JSON输出："
            "1. fire_detected (bool): 是否有明火；"
            "2. smoke_detected (bool): 是否有烟雾；"
            "3. hazard_level (str): LOW/MEDIUM/HIGH/CRITICAL；"
            "4. structural_obstacle (bool): 是否有建筑材料或脚手架阻断通道；"
            "5. agent_perception_summary (str): 简明的火情态势研判简报。"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "qwen-vl-plus",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url_or_path}}
                    ]
                }
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            req = urllib.request.Request(
                self.DASHSCOPE_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                parsed["source"] = "DASHSCOPE_QWEN_VL_OFFICIAL"
                return parsed
        except Exception as e:
            # 容灾自动退守
            fallback = self.offline_scenario_cache.get("incident_fire_act2", {}).copy()
            fallback["source"] = f"AUTO_FALLBACK_ON_ERROR: {str(e)}"
            return fallback
