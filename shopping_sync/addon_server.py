#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

INGRESS_PORT = 8099
OPTIONS_PATH = Path("/data/options.json")


def load_options() -> dict[str, Any]:
    if OPTIONS_PATH.exists():
        return json.loads(OPTIONS_PATH.read_text(encoding="utf-8"))
    return {
        "external_host": "",
        "external_port": 8095,
        "api_base_path": "/api/v1",
        "api_token": "",
        "request_timeout_seconds": 10,
    }


def build_base_url(options: dict[str, Any]) -> str:
    host = str(options.get("external_host") or "").strip()
    port = int(options.get("external_port") or 8095)
    base_path = str(options.get("api_base_path") or "/api/v1").strip()

    if not host:
        return ""
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    if ":" not in host.rsplit("/", 1)[-1]:
        host = f"{host}:{port}"
    return urljoin(host.rstrip("/") + "/", base_path.strip("/") + "/")


def tool_request(path: str) -> tuple[int, dict[str, Any]]:
    options = load_options()
    base_url = build_base_url(options)
    if not base_url:
        return 400, {"ok": False, "error": "external_host is not configured"}

    headers = {}
    token = str(options.get("api_token") or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    timeout = int(options.get("request_timeout_seconds") or 10)
    try:
        response = requests.get(
            urljoin(base_url, path.lstrip("/")),
            headers=headers,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return 502, {"ok": False, "error": str(exc)}

    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": response.text}
    return response.status_code, payload


def render_page() -> bytes:
    options = load_options()
    base_url = build_base_url(options) or "not configured"
    html = f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ShoppingSync</title>
  <style>
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f8fb;
      color: #17202a;
    }}
    main {{
      max-width: 960px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1 {{
      font-size: 26px;
      margin: 0 0 16px;
      font-weight: 650;
    }}
    section {{
      background: #fff;
      border: 1px solid #dde3ea;
      border-radius: 8px;
      padding: 18px;
      margin: 0 0 16px;
    }}
    dl {{
      display: grid;
      grid-template-columns: 160px 1fr;
      gap: 8px 16px;
      margin: 0;
    }}
    dt {{
      color: #5d6b7a;
    }}
    dd {{
      margin: 0;
      overflow-wrap: anywhere;
    }}
    button {{
      border: 1px solid #b7c3cf;
      background: #fff;
      border-radius: 6px;
      padding: 8px 12px;
      cursor: pointer;
    }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: #101820;
      color: #e8f1f7;
      padding: 12px;
      border-radius: 6px;
      min-height: 90px;
    }}
  </style>
</head>
<body>
  <main>
    <h1>ShoppingSync</h1>
    <section>
      <dl>
        <dt>Externer Dienst</dt>
        <dd>{base_url}</dd>
        <dt>Standardport</dt>
        <dd>{options.get("external_port", 8095)}</dd>
      </dl>
    </section>
    <section>
      <button type="button" onclick="loadStatus()">Status pruefen</button>
      <button type="button" onclick="loadHealth()">Verbindung testen</button>
      <pre id="output">Noch keine Abfrage ausgefuehrt.</pre>
    </section>
  </main>
  <script>
    async function show(path) {{
      const out = document.getElementById('output');
      out.textContent = 'Lade ...';
      try {{
        const response = await fetch(path);
        out.textContent = JSON.stringify(await response.json(), null, 2);
      }} catch (error) {{
        out.textContent = String(error);
      }}
    }}
    function loadStatus() {{ show('./api/status'); }}
    function loadHealth() {{ show('./api/health'); }}
  </script>
</body>
</html>"""
    return html.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_page())
            return

        if self.path == "/api/status":
            self.write_json(*tool_request("status"))
            return

        if self.path == "/api/health":
            self.write_json(*tool_request("health"))
            return

        self.write_json(404, {"ok": False, "error": "not found"})

    def log_message(self, format: str, *args: Any) -> None:
        return

    def write_json(self, status: int, payload: dict[str, Any]) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"))


def main() -> None:
    port = int(os.environ.get("PORT", INGRESS_PORT))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"ShoppingSync Control listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
