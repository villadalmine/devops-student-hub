#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
   SERVIDOR ASISTENTE & HUB DEVOPS UNIVERSAL (ALUMNOS)
===============================================================================
Servidor local multihilo ligero y seguro que provee:
  1. Interfaz Web DevOps Hub: devops_hub.html y visor interactivo de apuntes.
  2. Streaming de Videos Locales (videos/*.mp4 con soporte HTTP Range 206).
  3. Diagnóstico en vivo de las 31 herramientas DevOps en tu sistema.
  4. Telemetría y visor de logs del entorno.
===============================================================================
"""

import os
import sys
import re
import json
import time
import shutil
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Configurar salida UTF-8 segura en Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PORT = 8080
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENT_DIR = os.path.dirname(SCRIPT_DIR)
VIDEOS_DIR = os.path.join(STUDENT_DIR, "videos")

os.makedirs(VIDEOS_DIR, exist_ok=True)

SYSTEM_LOGS = []

def log_event(level, msg):
    timestamp = time.strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {msg}"
    print(log_entry, flush=True)
    SYSTEM_LOGS.append(log_entry)
    if len(SYSTEM_LOGS) > 200:
        SYSTEM_LOGS.pop(0)

log_event("INIT", f"Servidor DevOps Hub Alumnos inicializado en {STUDENT_DIR}")

# Catálogo completo de las 31 herramientas del curso
TOOLS_CATALOG = [
    # BASE
    {"id": 1,  "cat": "BASE", "name": "Zoom Workplace", "cmd": "zoom", "tipo": "Obligatorio"},
    {"id": 2,  "cat": "BASE", "name": "Git", "cmd": "git", "tipo": "Obligatorio"},
    {"id": 3,  "cat": "BASE", "name": "GitHub CLI (gh)", "cmd": "gh", "tipo": "Obligatorio"},
    {"id": 4,  "cat": "BASE", "name": "Visual Studio Code", "cmd": "code", "tipo": "Obligatorio"},
    {"id": 5,  "cat": "BASE", "name": "Docker Engine / Desktop", "cmd": "docker", "tipo": "Obligatorio"},
    {"id": 6,  "cat": "BASE", "name": "HashiCorp Terraform", "cmd": "terraform", "tipo": "Obligatorio"},
    {"id": 7,  "cat": "BASE", "name": "AWS CLI v2", "cmd": "aws", "tipo": "Obligatorio"},
    {"id": 8,  "cat": "BASE", "name": "Azure CLI (az)", "cmd": "az", "tipo": "Obligatorio"},
    {"id": 9,  "cat": "BASE", "name": "Kubernetes CLI (kubectl)", "cmd": "kubectl", "tipo": "Obligatorio"},
    {"id": 10, "cat": "BASE", "name": "Helm", "cmd": "helm", "tipo": "Obligatorio"},
    {"id": 11, "cat": "BASE", "name": "Minikube", "cmd": "minikube", "tipo": "Obligatorio"},
    {"id": 12, "cat": "BASE", "name": "jq (JSON Processor)", "cmd": "jq", "tipo": "Obligatorio"},
    # TERM
    {"id": 13, "cat": "TERM", "name": "Gajim (XMPP)", "cmd": "gajim", "tipo": "Optativo"},
    {"id": 14, "cat": "TERM", "name": "Ghostty Terminal", "cmd": "ghostty", "tipo": "Optativo"},
    {"id": 15, "cat": "TERM", "name": "Zed Editor", "cmd": "zed", "tipo": "Optativo"},
    {"id": 16, "cat": "TERM", "name": "Herdr Multiplexer", "cmd": "herdr", "tipo": "Optativo"},
    {"id": 17, "cat": "TERM", "name": "Neovim", "cmd": "nvim", "tipo": "Optativo"},
    {"id": 18, "cat": "TERM", "name": "VLC Media Player", "cmd": "vlc", "tipo": "Optativo"},
    # TUI
    {"id": 19, "cat": "TUI", "name": "fzf (Fuzzy Finder)", "cmd": "fzf", "tipo": "Optativo"},
    {"id": 20, "cat": "TUI", "name": "Lazygit", "cmd": "lazygit", "tipo": "Optativo"},
    {"id": 21, "cat": "TUI", "name": "Yazi (File Manager)", "cmd": "yazi", "tipo": "Optativo"},
    {"id": 22, "cat": "TUI", "name": "Lazydocker", "cmd": "lazydocker", "tipo": "Optativo"},
    {"id": 23, "cat": "TUI", "name": "k9s (K8s Monitor)", "cmd": "k9s", "tipo": "Optativo"},
    # EBPF
    {"id": 24, "cat": "EBPF", "name": "nerdctl (containerd)", "cmd": "nerdctl", "tipo": "Optativo"},
    {"id": 25, "cat": "EBPF", "name": "Cilium CLI", "cmd": "cilium", "tipo": "Optativo"},
    {"id": 26, "cat": "EBPF", "name": "Hubble CLI", "cmd": "hubble", "tipo": "Optativo"},
    # LANG
    {"id": 27, "cat": "LANG", "name": "Go (Golang)", "cmd": "go", "tipo": "Optativo"},
    {"id": 28, "cat": "LANG", "name": "Python 3", "cmd": "python", "tipo": "Optativo"},
    # AI
    {"id": 29, "cat": "AI", "name": "Claude Code CLI", "cmd": "claude", "tipo": "Optativo"},
    {"id": 30, "cat": "AI", "name": "Shell-GPT (sgpt)", "cmd": "sgpt", "tipo": "Optativo"},
    {"id": 31, "cat": "AI", "name": "OMP (Oh My Pi)", "cmd": "omp", "tipo": "Optativo"}
]

def check_local_tool(t):
    cmd = t["cmd"]
    found = shutil.which(cmd) is not None

    # Verificaciones adicionales en Windows para rutas estándar
    if not found and sys.platform == "win32":
        if cmd == "az":
            found = os.path.exists(r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd")
        elif cmd == "jq":
            links = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\jq.exe")
            found = os.path.exists(links)
        elif cmd == "vlc":
            found = os.path.exists(r"C:\Program Files\VideoLAN\VLC\vlc.exe") or os.path.exists(r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe")
        elif cmd == "gajim":
            found = os.path.exists(r"C:\Program Files\Gajim\bin\Gajim.exe")
        elif cmd == "zoom":
            appdata = os.path.expandvars(r"%APPDATA%\Zoom\bin\Zoom.exe")
            localapp = os.path.expandvars(r"%LOCALAPPDATA%\Zoom\bin\Zoom.exe")
            prog = r"C:\Program Files\Zoom\bin\Zoom.exe"
            found = os.path.exists(appdata) or os.path.exists(localapp) or os.path.exists(prog)
        elif cmd == "zed":
            zed_p = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Zed\Zed.exe")
            found = os.path.exists(zed_p)
    return found

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class StudentHubHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STUDENT_DIR, **kwargs)

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        query = urllib.parse.parse_qs(url_parts.query)

        # 1. API: Diagnóstico en vivo de herramientas instaladas
        if path == "/api/diagnostico":
            results = []
            installed_count = 0
            for t in TOOLS_CATALOG:
                is_inst = check_local_tool(t)
                if is_inst:
                    installed_count += 1
                results.append({
                    "id": t["id"],
                    "cat": t["cat"],
                    "name": t["name"],
                    "cmd": t["cmd"],
                    "tipo": t["tipo"],
                    "installed": is_inst
                })
            self.send_json({
                "ok": True,
                "os": sys.platform,
                "installed_count": installed_count,
                "total_tools": len(TOOLS_CATALOG),
                "tools": results
            })
            return

        # 2. API: Catálogo dinámico de videos locales
        elif path == "/api/videos":
            self.handle_api_videos()
            return

        # 3. API: Servir archivos locales de forma segura (/api/file?path=...)
        elif path == "/api/file":
            rel_file = query.get("path", [""])[0]
            self.handle_api_file(rel_file)
            return

        # 4. API: Telemetría y logs en vivo (/api/telemetry)
        elif path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(SYSTEM_LOGS, ensure_ascii=False).encode('utf-8'))
            return

        # 5. Streaming de Videos Locales (/videos/<filename>)
        elif path.startswith("/videos/"):
            filename = urllib.parse.unquote(path[8:])
            self.handle_video_streaming(filename)
            return

        # Favicon 204
        elif path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        # Redirigir raíz al portal principal
        if path in ["/", "/index.html"]:
            self.send_response(302)
            self.send_header("Location", "/devops_hub.html")
            self.end_headers()
            return

        super().do_GET()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def handle_api_videos(self):
        videos_list = []
        if os.path.exists(VIDEOS_DIR):
            for root, _, files in os.walk(VIDEOS_DIR):
                for f in sorted(files):
                    if f.lower().endswith(('.mp4', '.mkv', '.webm', '.mov', '.avi')):
                        abs_p = os.path.join(root, f)
                        rel_p = os.path.relpath(abs_p, VIDEOS_DIR).replace('\\', '/')
                        size_mb = round(os.path.getsize(abs_p) / (1024 * 1024), 2)
                        clean_title = os.path.splitext(f)[0].replace('_', ' ').replace('-', ' ').title()
                        videos_list.append({
                            "id": rel_p,
                            "titulo": clean_title,
                            "archivo": f,
                            "rel_path": rel_p,
                            "tamano_mb": size_mb,
                            "stream_url": f"/videos/{urllib.parse.quote(rel_p)}"
                        })
        self.send_json({"ok": True, "videos": videos_list})

    def handle_video_streaming(self, filename):
        video_path = os.path.join(VIDEOS_DIR, filename)
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Video no encontrado.")
            return

        file_size = os.path.getsize(video_path)
        range_header = self.headers.get("Range")

        content_type = "video/mp4"
        if filename.endswith(".mkv"):
            content_type = "video/x-matroska"
        elif filename.endswith(".webm"):
            content_type = "video/webm"

        if range_header:
            m = re.search(r"bytes=(\d+)-(\d*)", range_header)
            if m:
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else file_size - 1
                length = end - start + 1

                self.send_response(206)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()

                with open(video_path, "rb") as f:
                    f.seek(start)
                    self.wfile.write(f.read(length))
                return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()

        with open(video_path, "rb") as f:
            shutil.copyfileobj(f, self.wfile)

    def handle_api_file(self, rel_path):
        clean_rel = os.path.normpath(rel_path).lstrip("\\/.")
        target_path = os.path.join(STUDENT_DIR, clean_rel)

        if os.path.exists(target_path) and os.path.isfile(target_path):
            ext = os.path.splitext(target_path)[1].lower()
            mime_type = "text/plain; charset=utf-8"
            if ext in [".md", ".markdown"]:
                mime_type = "text/markdown; charset=utf-8"
            elif ext == ".pdf":
                mime_type = "application/pdf"
            elif ext == ".png":
                mime_type = "image/png"
            elif ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif ext == ".json":
                mime_type = "application/json; charset=utf-8"

            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(target_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Archivo no encontrado: {rel_path}"}).encode('utf-8'))

def run_server():
    server_address = ('', PORT)
    httpd = ThreadedHTTPServer(server_address, StudentHubHandler)
    log_event("SERVER", f"Servidor Alumnos activo en http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log_event("SERVER", "Deteniendo servidor...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
