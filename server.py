#!/usr/bin/env python3
"""
FireGuard 智慧工地态势指挥大屏与 Agent 交互服务
采用高可靠内置多线程 HTTP 服务，支持零外部依赖即开即用
提供 RESTful API 与现代 Vue 3 大屏界面
"""

import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

# 加入工程根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core.agent.fire_guard_agent import FireGuardAgent

# 全局 Agent 单例
agent_instance = FireGuardAgent(
    site_map_path=os.path.join(PROJECT_ROOT, "data", "site_maps", "floor_level_3.json")
)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """支持高并发请求的多线程 HTTP 服务器"""
    daemon_threads = True


class FireGuardRequestHandler(SimpleHTTPRequestHandler):
    """FireGuard REST API 与静态资产路由处理器"""

    def end_headers(self):
        # 允许跨域与无缓存开发模式
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        if path in ("/", "/index.html"):
            dist_index = os.path.join(PROJECT_ROOT, "web_dashboard", "dist", "index.html")
            legacy_index = os.path.join(PROJECT_ROOT, "web_dashboard", "index.html")
            target_index = dist_index if os.path.exists(dist_index) else legacy_index
            if os.path.exists(target_index):
                with open(target_index, "rb") as f:
                    content = f.read()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        elif path == "/api/state":
            # 返回全量大屏态势数据
            nodes_list = list(agent_instance.graph.nodes.values())
            edges_list = list(agent_instance.graph.edges.values())
            res = {
                "project_meta": agent_instance.graph.meta,
                "current_act": agent_instance.current_act,
                "nodes": nodes_list,
                "edges": edges_list,
                "workers": agent_instance.graph.workers,
                "sensors": agent_instance.graph.sensors,
                "plan": agent_instance.last_plan_result,
                "perception": agent_instance.last_perception_result or {
                    "fire_detected": False,
                    "smoke_detected": False,
                    "agent_perception_summary": "各传感器读数在正常阈值区间内，施工现场安全巡检合规。"
                },
                "broadcasts": agent_instance._generate_worker_broadcasts(
                    agent_instance.last_plan_result["routes"] if agent_instance.last_plan_result else []
                ),
                "incident_log": agent_instance.incident_log
            }
            self._send_json(res)
            return

        elif path == "/api/report":
            # 一键导出标准应急处置单
            report = agent_instance.export_formal_emergency_report()
            self._send_json(report)
            return

        # 静态文件双层寻址映射：先查 dist，再查原始 web_dashboard 资产
        rel_path = path.lstrip("/")
        candidate_paths = [
            os.path.join(PROJECT_ROOT, "web_dashboard", "dist", rel_path),
            os.path.join(PROJECT_ROOT, "web_dashboard", rel_path)
        ]

        for static_file in candidate_paths:
            if os.path.isfile(static_file):
                mime_type, _ = mimetypes.guess_type(static_file)
                with open(static_file, "rb") as f:
                    content = f.read()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mime_type or "application/octet-stream")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self):
        url = urlparse(self.path)
        path = url.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            req_data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            req_data = {}

        if path == "/api/trigger":
            act_key = req_data.get("act_key", "ACT_1_NORMAL")
            res = agent_instance.handle_incident(act_key=act_key)
            self._send_json(res)
            return

        elif path == "/api/chat":
            question = req_data.get("question", "")
            answer = agent_instance.query_agent_chat(user_question=question)
            self._send_json({"question": question, "answer": answer})
            return

        elif path == "/api/reset":
            res = agent_instance.handle_incident("ACT_1_NORMAL")
            self._send_json(res)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint Not Found")


def run(host: str = "0.0.0.0", port: int = 8000):
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, FireGuardRequestHandler)
    print("=" * 65)
    print("🚀 FireGuard（筑安·火眼）智慧工地态势指挥大屏服务已启动!")
    print(f"👉 本地访问地址: http://127.0.0.1:{port}")
    print(f"👉 局域网访问地址: http://{host}:{port}")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已平稳关闭。")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run(port=port)
