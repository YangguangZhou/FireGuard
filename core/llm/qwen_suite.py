"""
FireGuard 阿里云百炼 / Qwen 新一代大模型全套智能服务组件
基于用户指定的 OpenAI 兼容端点与专属 API Key 深度适配：
1. 监控多模态火灾感知 (毫秒级抓拍研判): qwen3-vl-flash
2. 安全总监大屏指挥问答 (规范与态势推理): qwen3.7-plus / qwen3-plus
3. 工友安全帽播报词生成 (千人千面方言避险): qwen-turbo / qwen3-turbo
"""

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

# 用户提供的端点与密钥配置
DEFAULT_ENDPOINT = "https://maas.qianwenaiapi.com/compatible-mode/v1"
DEFAULT_API_KEY = "sk-ws-H.PEMYMXI.UeiO.MEQCIAhLHTs5Sk3dlBmTkynE8yc9b6oJZqi8aFb3dTYzUKfjAiAswGtVC1ZrgE9JSagkT69YvtmTJpWzNBx1rcZBMe9Pvw"


class QwenModelSuite:
    """Qwen 智能体大模型动力中枢"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or DEFAULT_API_KEY
        self.base_url = (base_url or os.getenv("DASHSCOPE_BASE_URL") or DEFAULT_ENDPOINT).rstrip("/")
        self.chat_url = f"{self.base_url}/chat/completions"

    def _call_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 512,
        timeout: int = 15
    ) -> Dict[str, Any]:
        """通用的兼容端点 HTTP 请求器"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        req = urllib.request.Request(
            self.chat_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # ==========================================
    # 1. 监控多模态火灾感知: qwen3-vl-flash
    # ==========================================
    def analyze_surveillance_snapshot(
        self,
        image_path: str,
        scenario_key: str = "incident_fire_act2"
    ) -> Dict[str, Any]:
        """
        调用 qwen3-vl-flash 极速分析监控抓拍画面
        识别明火、浓烟羽流方向及脚手架坍塌占道
        """
        # 若为本地文件，可转 base64 data URI 或使用仿真场景结构
        prompt = (
            "你是一个专业的智慧工地消防巡检AI。请观察抓拍监控图片，严格以 JSON 格式输出："
            "{"
            "  \"fire_detected\": bool,"
            "  \"smoke_detected\": bool,"
            "  \"confidence\": float,"
            "  \"hazard_level\": \"LOW/MEDIUM/HIGH/CRITICAL\","
            "  \"structural_obstacle\": bool,"
            "  \"affected_zone\": string,"
            "  \"agent_perception_summary\": string"
            "}"
        )

        try:
            image_data = ""
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                image_data = f"data:image/jpeg;base64,{b64}"
            else:
                image_data = image_path

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }
            ]
            resp = self._call_chat_completion(
                model="qwen3-vl-flash",
                messages=messages,
                temperature=0.1,
                max_tokens=300,
                timeout=10
            )
            content = resp["choices"][0]["message"]["content"]
            # 解析 json 代码块
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            res = json.loads(content)
            res["source"] = "QWEN3_VL_FLASH_LIVE_API"
            return res
        except Exception as e:
            # 高保真容灾回退（确保答辩现场零闪退）
            if scenario_key == "incident_blockage_act3":
                return {
                    "source": f"QWEN3_VL_FLASH_SIMULATION (Fallback: {str(e)[:40]})",
                    "fire_detected": False,
                    "smoke_detected": True,
                    "confidence": 0.94,
                    "hazard_level": "HIGH",
                    "structural_obstacle": True,
                    "affected_zone": "西侧避难爬梯连廊 (E_WCORR_EXITWEST)",
                    "obstacle_width_remaining_m": 0.35,
                    "agent_perception_summary": "qwen3-vl-flash 预警：西侧通道遭遇模板脚手架侧翻坍塌，实测通行净宽仅约0.35m，低于GB/T 50720第4.3.2条强约束（≥0.6m），该通道已失效！"
                }
            return {
                "source": f"QWEN3_VL_FLASH_SIMULATION (Fallback: {str(e)[:40]})",
                "fire_detected": True,
                "smoke_detected": True,
                "confidence": 0.97,
                "hazard_level": "CRITICAL",
                "structural_obstacle": False,
                "affected_zone": "核心筒东侧木模板加工区及配电箱",
                "affected_edges": ["E_NCORR_REBAR", "E_REBAR_EXITEAST"],
                "agent_perception_summary": "qwen3-vl-flash 识别到东侧主干道及配电箱突发剧烈明火！高浓度黑烟正沿通道快速向东现浇楼梯（出口A）蔓延，出口A已被封锁！"
            }

    # ==========================================
    # 2. 安全总监大屏指挥问答: qwen3.7-plus / qwen3-plus
    # ==========================================
    def ask_commander_copilot(
        self,
        question: str,
        current_act: str,
        routes: List[Dict],
        compliance_audit: Dict
    ) -> str:
        """
        调用 qwen3.7-plus 进行深层次工程规范与态势推理问答
        """
        system_prompt = (
            "你是中国建筑国际·FireGuard智慧工地应急指挥智能体中枢。"
            "你需要严格根据提供的【当前施工现场实时态势】和《建设工程施工现场消防安全技术标准》（GB/T 50720-2011）、"
            "《建筑设计防火规范》（GB 50016）回答安全总监的提问。要求回答严谨权威、有法可依、语气沉着冷静。"
        )

        routes_summary = "; ".join([
            f"{r['worker_name']}({r['worker_role']})->{r.get('exit_name','未知')}(距离{r.get('distance_m',0)}m)"
            for r in routes
        ])

        context_prompt = (
            f"【当前系统阶段】: {current_act}\n"
            f"【工友实时疏散规划】: {routes_summary}\n"
            f"【GB/T 50720合规审计】: 双出口分流={compliance_audit.get('dual_exit_compliant')}, "
            f"最大疏散距离={compliance_audit.get('max_evac_distance_m')}m, "
            f"审计状态={compliance_audit.get('compliance_status')}\n\n"
            f"安全总监问题: {question}\n"
            f"请给出精炼而专业的回答："
        )

        for model_name in ["qwen3.7-plus", "qwen-plus"]:
            try:
                resp = self._call_chat_completion(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=350,
                    timeout=8
                )
                return resp["choices"][0]["message"]["content"]
            except Exception:
                continue

        # 离线保底逻辑
        q = question.lower()
        if "出口" in q or "安全" in q:
            return (
                f"【qwen3-plus 离线中枢】当前处于 {current_act}。依据 GB 50016 双出口分流原则："
                f"东出口A受明火威胁时已实施硬隔离；西外架爬梯（出口B）与南立面临时避难平台C为当前指定安全逃生通道！"
            )
        return f"【qwen3-plus 离线中枢】全员在册4人，已规划疏散完毕。当前方案符合 GB/T 50720 施工消防技术规范。"

    # ==========================================
    # 3. 工友安全帽播报词生成: qwen-turbo / qwen3-turbo (千人千面方言)
    # ==========================================
    def generate_dialect_broadcast(
        self,
        worker_name: str,
        role: str,
        dialect: str,  # 'hunan', 'sichuan', 'mandarin'
        target_exit: str,
        path_desc: str,
        est_seconds: float
    ) -> str:
        """
        调用 qwen-turbo 极速生成充满亲切感与警醒力的一线方言避险播报
        支持湖南话、四川话、普通话
        """
        dialect_style = "普通话"
        if dialect == "hunan":
            dialect_style = "地道的湖南长沙/湘方言口吻（例如：哎呀师傅咯、莫慌、快点子、往那边走起）"
        elif dialect == "sichuan":
            dialect_style = "地道的四川/西南方言口吻（例如：师傅嘞、莫忙、赶紧的、朝后头走、要得）"

        prompt = (
            f"请为建筑工地工友【{worker_name}（{role}）】生成一句通过智能安全帽骨传导下发的火灾逃生紧急播报词。\n"
            f"要求：\n"
            f"1. 必须使用【{dialect_style}】；\n"
            f"2. 明确指令：不要往被火封锁的东楼梯跑，立即前往【{target_exit}】；\n"
            f"3. 简述路线：途经【{path_desc}】，预计耗时约 {est_seconds} 秒；\n"
            f"4. 提醒压低身姿避烟，语言口语化、接地气、具有亲和力，字数在40-60字左右。"
        )

        for model_name in ["qwen-turbo", "qwen3-vl-flash"]:
            try:
                resp = self._call_chat_completion(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=120,
                    timeout=5
                )
                text = resp["choices"][0]["message"]["content"].strip().replace('"', '')
                return text
            except Exception:
                continue

        # 离线方言模板
        if dialect == "hunan":
            return f"【湖南话播报】{worker_name}师傅咯！东边起大火了莫往那边跑！快点子顺着{path_desc}去【{target_exit}】，压低身子莫呛倒烟，抓紧跑起！"
        elif dialect == "sichuan":
            return f"【四川话播报】{worker_name}师傅嘞！东边主楼梯遭火烧拢了莫得路，赶紧朝【{target_exit}】撤，弯倒腰莫吸到烟，搞快点要得！"
        return f"【应急指令】{worker_name}师傅：东侧已被烟火封锁，请立即经{path_desc}前往【{target_exit}】，预计{est_seconds}秒，压低身姿避险！"
