#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests

INGRESS_PORT = 8099
OPTIONS_PATH = Path("/data/options.json")
ADDON_VERSION = "0.2.7"


def load_options() -> dict[str, Any]:
    if OPTIONS_PATH.exists():
        return json.loads(OPTIONS_PATH.read_text(encoding="utf-8"))
    return {
        "external_host": "",
        "external_port": 8095,
        "api_base_path": "/api/v1",
        "api_token": "",
        "request_timeout_seconds": 30,
    }


def build_base_url(options: dict[str, Any]) -> str:
    host = str(options.get("external_host") or "").strip()
    port = int(options.get("external_port") or 8095)
    base_path = str(options.get("api_base_path") or "/api/v1").strip()

    if not host:
        return ""
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    parsed = urlparse(host)
    netloc = parsed.netloc
    if ":" not in netloc:
        netloc = f"{netloc}:{port}"
    host = f"{parsed.scheme}://{netloc}"
    return urljoin(host.rstrip("/") + "/", base_path.strip("/") + "/")


def tool_request(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    options = load_options()
    base_url = build_base_url(options)
    if not base_url:
        return 400, {"ok": False, "error": "external_host is not configured"}

    headers: dict[str, str] = {}
    token = str(options.get("api_token") or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    timeout = int(options.get("request_timeout_seconds") or 30)
    try:
        response = requests.request(
            method,
            urljoin(base_url, path.lstrip("/")),
            headers=headers,
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return 502, {"ok": False, "error": str(exc), "base_url": base_url}

    try:
        body = response.json()
    except ValueError:
        body = {"ok": False, "raw": response.text}
    return response.status_code, body


def render_page() -> bytes:
    options = load_options()
    base_url = build_base_url(options) or "nicht konfiguriert"
    html = f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shopping Sync</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cpath fill='%232563eb' d='M18 50a6 6 0 1 0 0 12 6 6 0 0 0 0-12Zm30 0a6 6 0 1 0 0 12 6 6 0 0 0 0-12ZM10 8H2V2h12l5 30h31l7-20H22l-1-6h40a3 3 0 0 1 3 4l-9 27a3 3 0 0 1-3 2H20l1 5h35v6H18a3 3 0 0 1-3-2L10 8Z'/%3E%3C/svg%3E">
  <style>
    :root {{ color-scheme: light dark; font-family: Segoe UI, system-ui, sans-serif; }}
    body {{ margin: 0; background: #f5f7f9; color: #1f2933; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 22px; }}
    h1 {{ display: flex; align-items: center; gap: 10px; font-size: 26px; margin: 0 0 16px; }}
    .cart-icon {{ width: 28px; height: 28px; fill: #2563eb; flex: 0 0 auto; }}
    .version-badge {{ font-size: 12px; font-weight: 600; color: #52606d; background: #e8eef5; border-radius: 999px; padding: 4px 8px; }}
    h2 {{ font-size: 17px; margin: 0 0 12px; }}
    section {{ background: #fff; border: 1px solid #d8e0e8; border-radius: 8px; padding: 16px; margin-bottom: 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    .tile {{ border: 1px solid #d8e0e8; border-radius: 6px; padding: 12px; background: #f9fbfd; }}
    .label {{ color: #596673; font-size: 12px; margin-bottom: 4px; }}
    .value {{ font-size: 15px; font-weight: 600; word-break: break-word; }}
    .banner {{ padding: 12px; border-radius: 6px; border: 1px solid #fed7aa; background: #fff7ed; margin: 12px 0; }}
    .banner.ok {{ border-color: #bbf7d0; background: #ecfdf5; }}
    .banner.error {{ border-color: #fecaca; background: #fef2f2; }}
    textarea {{ width: 100%; min-height: 360px; box-sizing: border-box; border: 1px solid #b8c4d0; border-radius: 6px; padding: 10px; font: 13px Consolas, monospace; resize: vertical; }}
    button {{ border: 0; border-radius: 6px; background: #2563eb; color: white; padding: 9px 13px; font: inherit; cursor: pointer; }}
    button.secondary {{ background: #52606d; }}
    button.danger {{ background: #b42318; }}
    .mode-buttons button {{ background: #52606d; }}
    .mode-buttons button.active {{ background: #2563eb; }}
    .actions {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background: #f8fafc; border: 1px solid #d8e0e8; border-radius: 6px; padding: 12px; max-height: 300px; overflow: auto; }}
    #message {{ min-height: 22px; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #11161c; color: #e6edf3; }}
      section, textarea {{ background: #171d24; color: #e6edf3; border-color: #344250; }}
      .tile, pre {{ background: #111820; border-color: #344250; }}
      .label {{ color: #aab6c2; }}
      .version-badge {{ background: #273444; color: #d6e0ea; }}
      .banner {{ background: #332414; border-color: #7a4b18; }}
      .banner.ok {{ background: #133226; border-color: #246b4a; }}
      .banner.error {{ background: #371818; border-color: #7a3030; }}
    }}
  </style>
</head>
<body>
<main>
  <h1><svg class="cart-icon" viewBox="0 0 64 64" aria-hidden="true"><path d="M18 50a6 6 0 1 0 0 12 6 6 0 0 0 0-12Zm30 0a6 6 0 1 0 0 12 6 6 0 0 0 0-12ZM10 8H2V2h12l5 30h31l7-20H22l-1-6h40a3 3 0 0 1 3 4l-9 27a3 3 0 0 1-3 2H20l1 5h35v6H18a3 3 0 0 1-3-2L10 8Z"/></svg>Shopping Sync <span class="version-badge" id="versionBadge">Add-on {ADDON_VERSION}</span></h1>
  <section>
    <div class="grid">
      <div class="tile"><div class="label">Externer Dienst</div><div class="value">{base_url}</div></div>
      <div class="tile"><div class="label">Add-on</div><div class="value">Ingress Control</div></div>
      <div class="tile"><div class="label">Timeout</div><div class="value">{options.get("request_timeout_seconds", 30)} Sekunden fuer API-Antworten</div></div>
    </div>
  </section>
  <section>
    <div class="actions">
      <h2 style="margin-right:auto">Status</h2>
      <button onclick="loadAll()">Aktualisieren</button>
      <button class="secondary" onclick="runAction('test_connection')">Verbindung testen</button>
      <button onclick="runAction('sync_now')">Jetzt synchronisieren</button>
      <button class="secondary" onclick="runAction('reload')">Neu laden</button>
      <button class="danger" onclick="runCritical('restart')">Neustart</button>
      <button class="danger" onclick="runCritical('shutdown')">Beenden</button>
    </div>
    <p id="message"></p>
    <div id="statusBanner" class="banner">Status noch nicht geladen.</div>
    <div class="grid" id="statusTiles">
      <div class="tile"><div class="label">Firebase</div><div class="value" id="tileFirebase">-</div></div>
      <div class="tile"><div class="label">Home Assistant</div><div class="value" id="tileHomeAssistant">-</div></div>
      <div class="tile"><div class="label">Beobachtete Listen</div><div class="value" id="tileWatchedLists">-</div></div>
      <div class="tile"><div class="label">Todo-Listen</div><div class="value" id="tileTodoEntities">-</div></div>
      <div class="tile"><div class="label">Letzter Kontakt</div><div class="value" id="tileLastSeen">-</div></div>
      <div class="tile"><div class="label">Letzter Fehler</div><div class="value" id="tileLastError">-</div></div>
      <div class="tile"><div class="label">Live-Monitor</div><div class="value" id="tileLiveMonitor">-</div></div>
      <div class="tile"><div class="label">Sync</div><div class="value" id="tileSync">-</div></div>
      <div class="tile"><div class="label">Betriebsart</div><div class="value" id="tileMode">-</div></div>
    </div>
    <div class="actions mode-buttons" style="margin-top:12px">
      <button id="modeIdle" type="button" onclick="setSyncMode(true)">Bei Bedarf</button>
      <button id="modeRealtime" type="button" onclick="setSyncMode(false)">Echtzeit</button>
    </div>
    <div class="actions" style="margin-top:12px">
      <h2 style="margin-right:auto">Live-Logs</h2>
      <button class="secondary" onclick="clearLogs()">Log loeschen</button>
    </div>
    <pre id="logs">Noch keine Logs.</pre>
  </section>
  <section>
    <div class="actions">
      <h2 style="margin-right:auto">Konfiguration</h2>
      <button class="secondary" onclick="loadConfig()">Einlesen</button>
      <button onclick="saveConfig()">Speichern</button>
    </div>
    <textarea id="configText" spellcheck="false"></textarea>
  </section>
  <section>
    <div class="actions">
      <h2 style="margin-right:auto">Diagnose</h2>
      <button class="secondary" onclick="loadAll()">Aktualisieren</button>
    </div>
    <pre id="status">Noch keine Daten.</pre>
  </section>
</main>
<script>
async function requestJson(url, options) {{
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok || data.ok === false) throw new Error(data.error || data.message || `HTTP ${{response.status}}`);
  return data;
}}
let currentConfig = null;

async function loadAll() {{
  const [manifest, health, status] = await Promise.all([
    requestJson('./api/manifest').catch(error => ({{error: String(error)}})),
    requestJson('./api/health').catch(error => ({{error: String(error)}})),
    requestJson('./api/status').catch(error => ({{error: String(error)}})),
  ]);
  renderVersion(manifest);
  renderStatusTiles(status);
  document.getElementById('status').textContent = JSON.stringify({{manifest, health, status}}, null, 2);
}}
function renderVersion(manifest) {{
  const toolVersion = manifest.tool_version || manifest.version || '-';
  document.getElementById('versionBadge').textContent = `Add-on {ADDON_VERSION} | Dienst ${{toolVersion}}`;
}}
function renderStatusTiles(status) {{
  const sensor = status.status_sensor || {{}};
  const attrs = sensor.attributes || {{}};
  const state = sensor.state || 'unbekannt';
  const banner = document.getElementById('statusBanner');
  banner.className = state === 'error' ? 'banner error' : (state === 'idle' || state === 'online' ? 'banner ok' : 'banner');
  banner.textContent = `Status: ${{state}}`;
  const message = document.getElementById('message');
  if (
    ['Dienst wird beendet.', 'Neustart wird ausgeloest.'].includes(message.textContent.trim())
    && ['idle', 'online'].includes(state)
  ) {{
    message.textContent = '';
  }}
  document.getElementById('tileFirebase').textContent = attrs.firebase_connected ? 'verbunden' : 'nicht verbunden';
  document.getElementById('tileHomeAssistant').textContent = attrs.home_assistant_connected ? 'verbunden' : 'nicht verbunden';
  document.getElementById('tileWatchedLists').textContent = (attrs.watched_lists || []).join(', ') || 'keine';
  document.getElementById('tileTodoEntities').textContent = (attrs.synced_todo_entities || []).join(', ') || 'keine';
  document.getElementById('tileLastSeen').textContent = formatDate(attrs.last_seen);
  document.getElementById('tileLastError').textContent = status.last_sync_error || attrs.last_error || '-';
  const monitor = status.live_monitor || {{}};
  document.getElementById('tileLiveMonitor').textContent = monitor.connected ? 'verbunden' : (monitor.error || 'nicht verbunden');
  document.getElementById('tileSync').textContent = status.sync_running ? 'laeuft' : 'bereit';
  renderMode();
}}
function formatDate(value) {{
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('de-DE', {{
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }});
}}
async function loadConfig() {{
  const data = await requestJson('./api/config');
  currentConfig = data.config || {{}};
  document.getElementById('configText').value = JSON.stringify(currentConfig, null, 2);
  renderMode();
}}
async function saveConfig() {{
  const message = document.getElementById('message');
  try {{
    const config = JSON.parse(document.getElementById('configText').value || '{{}}');
    const data = await requestJson('./api/config', {{
      method: 'PUT',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{config}}),
    }});
    currentConfig = config;
    renderMode();
    message.textContent = data.message || 'Gespeichert.';
  }} catch (error) {{
    message.textContent = error.message;
  }}
}}
function renderMode() {{
  const idleMode = currentConfig && currentConfig.runtime ? currentConfig.runtime.idle_mode !== false : null;
  const label = idleMode === null ? '-' : (idleMode ? 'Bei Bedarf' : 'Echtzeit');
  document.getElementById('tileMode').textContent = label;
  document.getElementById('modeIdle').classList.toggle('active', idleMode === true);
  document.getElementById('modeRealtime').classList.toggle('active', idleMode === false);
}}
async function setSyncMode(idleMode) {{
  const message = document.getElementById('message');
  try {{
    if (!currentConfig) await loadConfig();
    currentConfig.runtime = currentConfig.runtime || {{}};
    currentConfig.runtime.idle_mode = idleMode;
    document.getElementById('configText').value = JSON.stringify(currentConfig, null, 2);
    const data = await requestJson('./api/config', {{
      method: 'PUT',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{config: currentConfig}}),
    }});
    renderMode();
    message.textContent = (data.message || 'Gespeichert.') + ' Dienst danach neu laden oder neu starten.';
  }} catch (error) {{
    message.textContent = error.message;
  }}
}}
async function runAction(action) {{
  const message = document.getElementById('message');
  try {{
    const data = await requestJson(`./api/actions/${{action}}`, {{method: 'POST'}});
    message.textContent = data.message || JSON.stringify(data);
    await loadAll();
  }} catch (error) {{
    message.textContent = error.message;
  }}
}}
function runCritical(action) {{
  if (confirm(`Aktion wirklich ausfuehren: ${{action}}?`)) runAction(action);
}}
async function clearLogs() {{
  const message = document.getElementById('message');
  try {{
    const data = await requestJson('./api/logs/clear', {{method: 'POST'}});
    document.getElementById('logs').textContent = 'Keine Logs.';
    message.textContent = data.message || 'Logs geloescht.';
  }} catch (error) {{
    message.textContent = error.message;
  }}
}}
async function loadLogs() {{
  const data = await requestJson('./api/logs/recent');
  const lines = [];
  if (data.monitor) {{
    lines.push(`Monitor: ${{data.monitor.connected ? 'verbunden' : 'nicht verbunden'}}`);
    if (data.monitor.error) lines.push(`Fehler: ${{data.monitor.error}}`);
  }}
  for (const event of data.events || []) {{
    const time = event.time
      ? new Date(event.time).toLocaleString('de-DE', {{
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }})
      : '';
    lines.push(`${{time}} | ${{event.kind || '-'}} | ${{event.summary || ''}}`);
  }}
  if ((data.lines || []).length) {{
    if (lines.length) lines.push('');
    lines.push(...data.lines);
  }}
  const logElement = document.getElementById('logs');
  const wasNearBottom =
    logElement.scrollTop + logElement.clientHeight >= logElement.scrollHeight - 24;
  logElement.textContent = lines.join('\\n') || 'Keine Logs.';
  if (wasNearBottom) {{
    logElement.scrollTop = logElement.scrollHeight;
  }}
}}
loadAll();
loadConfig().catch(() => {{}});
loadLogs().catch(() => {{}});
setInterval(loadAll, 10000);
setInterval(loadLogs, 2000);
</script>
</body>
</html>"""
    return html.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self.write_html(render_page())
            return
        if self.path.startswith("/api/"):
            self.proxy_api("GET", self.path.removeprefix("/api/"))
            return
        self.write_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        if self.path.startswith("/api/"):
            self.proxy_api("POST", self.path.removeprefix("/api/"))
            return
        self.write_json(404, {"ok": False, "error": "not found"})

    def do_PUT(self) -> None:
        if self.path.startswith("/api/"):
            self.proxy_api("PUT", self.path.removeprefix("/api/"))
            return
        self.write_json(404, {"ok": False, "error": "not found"})

    def proxy_api(self, method: str, path: str) -> None:
        payload = None
        if method in {"POST", "PUT"}:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw or "{}")
        self.write_json(*tool_request(method, path, payload))

    def log_message(self, format: str, *args: Any) -> None:
        return

    def write_html(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def write_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    port = int(os.environ.get("PORT", INGRESS_PORT))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"ShoppingSync Control listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
