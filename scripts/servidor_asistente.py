#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
   SERVIDOR ASISTENTE & HUB DEVOPS UNIVERSAL (ALUMNOS & PLATAFORMA EDUCATIVA)
===============================================================================
Servidor local multihilo ligero y seguro que provee:
  1. Interfaz Web DevOps Hub: devops_hub.html y visor interactivo de apuntes.
  2. Detección y Carga Dinámica de Curso (curso.json) para cualquier materia.
  3. Gestor de Notas y Aportes del Alumno (/mis_apuntes, /practicas).
  4. Exportación en 1-clic a paquete .ZIP para compartir con el docente.
  5. Streaming de Videos Locales (videos/*.mp4 con soporte HTTP Range 206).
  6. Diagnóstico en vivo de herramientas en tu sistema (Multi-OS).
  7. Telemetría y visor de logs del entorno.
  8. Ejecución Standalone binaria (.exe) o con Python estándar.
===============================================================================
"""

import os
import sys
import re
import io
import json
import time
import shutil
import zipfile
import threading
import subprocess
import webbrowser
import urllib.parse
import urllib.request
import urllib.error
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Configurar salida UTF-8 segura en Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8081

# Resolucion inteligente de rutas para soporte binario PyInstaller (sys.frozen) y script normal
if getattr(sys, "frozen", False):
    # Ejecutandose como binario compilado con PyInstaller (.exe)
    # sys._MEIPASS contiene la ruta donde PyInstaller desempacó los archivos empacados
    # (devops_hub.html, scripts/, material/, apuntes/, practicas/): sirve para LEER contenido
    # del curso, pero es una carpeta temporal que PyInstaller borra al cerrar el proceso.
    STUDENT_DIR = sys._MEIPASS
    SCRIPT_DIR = os.path.join(STUDENT_DIR, "scripts")
    # Todo lo que el alumno necesita conservar ENTRE ejecuciones (sus notas, sus videos, el
    # Mapa de Estudio que importó) tiene que vivir junto al .exe real, no en la carpeta
    # temporal — si no, desaparece cada vez que cierra el programa.
    WRITABLE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    # Ejecutandose como script Python normal
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    STUDENT_DIR = os.path.dirname(SCRIPT_DIR)
    WRITABLE_DIR = STUDENT_DIR

# Carpetas que el alumno escribe y que deben persistir entre ejecuciones del .exe, versus
# carpetas que vienen empacadas con el curso (de solo lectura cuando está compilado).
CARPETAS_ESCRIBIBLES = {"mis_apuntes", "aportes", "videos", "mapa_estudio"}

def base_dir_para(carpeta):
    return WRITABLE_DIR if carpeta in CARPETAS_ESCRIBIBLES else STUDENT_DIR

VIDEOS_DIR = os.path.join(WRITABLE_DIR, "videos")
MIS_APUNTES_DIR = os.path.join(WRITABLE_DIR, "mis_apuntes")
PRACTICAS_DIR = os.path.join(STUDENT_DIR, "practicas")
MAPA_ESTUDIO_DIR = os.path.join(WRITABLE_DIR, "mapa_estudio")
LOCAL_RAG_DB = os.path.join(MAPA_ESTUDIO_DIR, "conocimiento_local.db")

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(MIS_APUNTES_DIR, exist_ok=True)
os.makedirs(PRACTICAS_DIR, exist_ok=True)
os.makedirs(MAPA_ESTUDIO_DIR, exist_ok=True)

SYSTEM_LOGS = []

def log_event(level, msg):
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {msg}"
    print(log_entry, flush=True)
    SYSTEM_LOGS.append(log_entry)
    if len(SYSTEM_LOGS) > 200:
        SYSTEM_LOGS.pop(0)

# ==================================================================
# PROXY DE TEMARIO EN VIVO — study.cybercirujas.club (proyecto abierto
# villadalmine/study-cybercirujas). Su API pública no expone CORS, así que
# el navegador no puede leerla directo: este servidor la consulta por vos
# (server-to-server, sin restricción de CORS) y la cachea en memoria para
# no golpearla de más — el propio proyecto pide "cache what you fetch".
# ==================================================================
CYBERCIRUJAS_BASE = "https://study.cybercirujas.club"
CYBERCIRUJAS_CACHE = {}
CYBERCIRUJAS_CACHE_TTL = 600  # 10 minutos

def fetch_cybercirujas(path):
    """GET a study.cybercirujas.club con caché en memoria. Devuelve (ok, data_o_error)."""
    now = time.time()
    cached = CYBERCIRUJAS_CACHE.get(path)
    if cached and (now - cached[0]) < CYBERCIRUJAS_CACHE_TTL:
        return True, cached[1]
    try:
        req = urllib.request.Request(CYBERCIRUJAS_BASE + path, headers={"User-Agent": "CloudDevOpsStudentHub/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        CYBERCIRUJAS_CACHE[path] = (now, data)
        return True, data
    except Exception as e:
        return False, str(e)

log_event("INIT", f"Servidor Hub Universal Alumnos iniciado en {STUDENT_DIR}")
if getattr(sys, "frozen", False):
    log_event("INIT", f"Modo: Standalone Binario Compilado ({sys.executable})")
else:
    log_event("INIT", f"Modo: Python Script ({sys.version.split()[0]})")

# Catalogo completo de las 33 herramientas DevOps del curso
TOOLS_CATALOG = [
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
    {"id": 13, "cat": "TERM", "name": "Gajim (XMPP)", "cmd": "gajim", "tipo": "Optativo"},
    {"id": 14, "cat": "TERM", "name": "Ghostty Terminal", "cmd": "ghostty", "tipo": "Optativo"},
    {"id": 15, "cat": "TERM", "name": "Zed Editor", "cmd": "zed", "tipo": "Optativo"},
    {"id": 16, "cat": "TERM", "name": "Herdr Multiplexer", "cmd": "herdr", "tipo": "Optativo"},
    {"id": 17, "cat": "TERM", "name": "Neovim", "cmd": "nvim", "tipo": "Optativo"},
    {"id": 18, "cat": "TERM", "name": "VLC Media Player", "cmd": "vlc", "tipo": "Optativo"},
    {"id": 19, "cat": "TUI", "name": "fzf (Fuzzy Finder)", "cmd": "fzf", "tipo": "Optativo"},
    {"id": 20, "cat": "TUI", "name": "Lazygit", "cmd": "lazygit", "tipo": "Optativo"},
    {"id": 21, "cat": "TUI", "name": "Yazi (File Manager)", "cmd": "yazi", "tipo": "Optativo"},
    {"id": 22, "cat": "TUI", "name": "Lazydocker", "cmd": "lazydocker", "tipo": "Optativo"},
    {"id": 23, "cat": "TUI", "name": "k9s (K8s Monitor)", "cmd": "k9s", "tipo": "Optativo"},
    {"id": 24, "cat": "EBPF", "name": "nerdctl (containerd)", "cmd": "nerdctl", "tipo": "Optativo"},
    {"id": 25, "cat": "EBPF", "name": "Cilium CLI", "cmd": "cilium", "tipo": "Optativo"},
    {"id": 26, "cat": "EBPF", "name": "Hubble CLI", "cmd": "hubble", "tipo": "Optativo"},
    {"id": 27, "cat": "EBPF", "name": "Trivy (Security Scanner)", "cmd": "trivy", "tipo": "Optativo"},
    {"id": 28, "cat": "LANG", "name": "Go (Golang)", "cmd": "go", "tipo": "Optativo"},
    {"id": 29, "cat": "LANG", "name": "Python 3", "cmd": "python", "tipo": "Optativo"},
    {"id": 30, "cat": "LANG", "name": "Rust (Cargo)", "cmd": "rustc", "tipo": "Optativo"},
    {"id": 31, "cat": "AI", "name": "Claude Code CLI", "cmd": "claude", "tipo": "Optativo"},
    {"id": 32, "cat": "AI", "name": "Shell-GPT (sgpt)", "cmd": "sgpt", "tipo": "Optativo"},
    {"id": 33, "cat": "AI", "name": "OMP (Oh My Pi)", "cmd": "omp", "tipo": "Optativo"}
]

def check_local_tool(t):
    cmd = t["cmd"]
    found = shutil.which(cmd) is not None
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
        elif cmd == "go":
            found = os.path.exists(r"C:\Program Files\Go\bin\go.exe")
        elif cmd == "rustc":
            cargo_p = os.path.expandvars(r"%USERPROFILE%\.cargo\bin\rustc.exe")
            found = os.path.exists(cargo_p)
        elif cmd == "trivy":
            links = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\trivy.exe")
            found = os.path.exists(links)
    return found

def launch_in_terminal(command, as_admin=False, cwd=None):
    """Abre una nueva ventana de terminal independiente para ejecutar comandos."""
    if not cwd:
        cwd = WRITABLE_DIR

    log_event("EXEC", f"Lanzando terminal ({'ADMIN' if as_admin else 'USER'}) en {cwd}: {command}")

    if sys.platform == "win32":
        temp_dir = os.path.join(os.environ.get("TEMP", cwd), "devops_hub_scripts")
        os.makedirs(temp_dir, exist_ok=True)
        ps_file = os.path.join(temp_dir, "ejecutar_instalacion.ps1")
        mode_str = "ADMINISTRADOR (ELEVADO)" if as_admin else "USUARIO ESTANDAR"
        mode_color = "Green" if as_admin else "Cyan"

        full_script = f"""# Script de Ejecución DevOps Hub
Set-Location -LiteralPath '{cwd}'
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$wingetLinks = "$env:LOCALAPPDATA\\Microsoft\\WinGet\\Links"
if (Test-Path $wingetLinks) {{ $env:Path += ";$wingetLinks" }}
$cargoPath = "$env:USERPROFILE\\.cargo\\bin"
if (Test-Path $cargoPath) {{ $env:Path += ";$cargoPath" }}
$goPath = "C:\\Program Files\\Go\\bin"
if (Test-Path $goPath) {{ $env:Path += ";$goPath" }}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   DEVOPS WORKSPACE - COMANDO EN TERMINAL" -ForegroundColor Yellow
Write-Host "   Comando : {command}" -ForegroundColor White
Write-Host "   Modo    : {mode_str}" -ForegroundColor {mode_color}
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

{command}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   PROCESO FINALIZADO. Puedes revisar los resultados arriba." -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
"""
        with open(ps_file, "w", encoding="utf-8-sig") as f:
            f.write(full_script)

        launched = False
        if as_admin:
            try:
                import ctypes
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", "powershell.exe",
                    f'-NoExit -ExecutionPolicy Bypass -File "{ps_file}"',
                    None, 1
                )
                if ret > 32:
                    launched = True
                    log_event("EXEC", f"Terminal elevada abierta vía ShellExecuteW: {ps_file}")
            except Exception as e:
                log_event("WARN", f"Fallo al invocar elevación UAC: {e}")

        if not launched:
            subprocess.Popen(
                ["powershell.exe", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ps_file],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            log_event("EXEC", f"Terminal visible abierta (CREATE_NEW_CONSOLE): {ps_file}")
        return True
    elif sys.platform.startswith("linux"):
        temp_dir = "/tmp/devops_hub_scripts"
        os.makedirs(temp_dir, exist_ok=True)
        sh_file = os.path.join(temp_dir, "ejecutar_instalacion.sh")
        with open(sh_file, "w", encoding="utf-8") as f:
            f.write(f"#!/usr/bin/env bash\ncd '{cwd}'\necho '=== DEVOPS WORKSPACE ==='\necho 'Comando: {command}'\necho ''\n{command}\necho ''\necho '=== FINALIZADO ==='\nexec bash\n")
        os.chmod(sh_file, 0o755)
        for term in ["x-terminal-emulator", "gnome-terminal", "konsole", "xterm"]:
            if shutil.which(term):
                if term == "gnome-terminal":
                    subprocess.Popen([term, "--", "bash", sh_file])
                else:
                    subprocess.Popen([term, "-e", f"bash {sh_file}"])
                return True
        return False
    elif sys.platform == "darwin":
        script = f'tell app "Terminal" to do script "cd \\"{cwd}\\" && echo \\"=== DEVOPS WORKSPACE ===\\" && {command}"'
        subprocess.Popen(["osascript", "-e", script])
        return True
    return False

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

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        log_event("HTTP", f"GET {self.path} desde {self.client_address[0]}")
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        query = urllib.parse.parse_qs(url_parts.query)

        if path == "/api/curso":
            self.handle_api_curso()
            return
        elif path == "/api/diagnostico":
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
        elif path == "/api/videos":
            self.handle_api_videos()
            return
        elif path == "/api/mis_apuntes":
            self.handle_api_mis_apuntes()
            return
        elif path == "/api/materiales":
            self.handle_api_materiales()
            return
        elif path == "/api/mapa_estudio/estado":
            self.handle_mapa_estudio_estado()
            return
        elif path == "/api/mapa_estudio/buscar":
            q = query.get("q", [""])[0]
            limit_raw = query.get("limit", ["8"])[0]
            limit = int(limit_raw) if limit_raw.isdigit() else 8
            self.handle_mapa_estudio_buscar(q, limit)
            return
        elif path == "/api/mapa_estudio/documento":
            doc_id_raw = query.get("id", [""])[0]
            if not doc_id_raw.isdigit():
                self.send_json({"ok": False, "error": "id inválido"}, status=400)
                return
            self.handle_mapa_estudio_documento(int(doc_id_raw))
            return
        elif path == "/api/ollama/modelos":
            self.handle_ollama_modelos()
            return
        elif path == "/api/cybercirujas/catalogo":
            self.handle_cybercirujas_catalogo()
            return
        elif path == "/api/cybercirujas/temario":
            cert_id = query.get("cert", [""])[0]
            self.handle_cybercirujas_temario(cert_id)
            return
        elif path == "/api/cybercirujas/material":
            cert_id = query.get("cert", [""])[0]
            topic_id = query.get("topic", [""])[0]
            lang = query.get("lang", ["es"])[0]
            self.handle_cybercirujas_material(cert_id, topic_id, lang)
            return
        elif path == "/api/exportar_aportes":
            self.handle_exportar_aportes()
            return
        elif path == "/api/file":
            rel_file = query.get("path", [""])[0]
            self.handle_api_file(rel_file)
            return
        elif path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(SYSTEM_LOGS, ensure_ascii=False).encode("utf-8"))
            return
        elif path.startswith("/videos/"):
            filename = urllib.parse.unquote(path[8:])
            self.handle_video_streaming(filename)
            return
        elif path == "/api/biblioteca":
            biblio = os.path.join(STUDENT_DIR, "biblioteca")
            unidades = []
            for tipo, carpeta in (("proyecto", "proyectos"), ("ejercicio", "ejercicios")):
                base = os.path.join(biblio, carpeta)
                if not os.path.isdir(base):
                    continue
                for d in sorted(os.listdir(base)):
                    man = os.path.join(base, d, f"{tipo}.json")
                    if not os.path.exists(man):
                        continue
                    try:
                        with open(man, "r", encoding="utf-8") as fh:
                            m = json.load(fh)
                    except Exception:
                        continue
                    archivos = []
                    for sub in ("lab", "infra", "dependencias", "modules"):
                        subdir = os.path.join(base, d, sub)
                        if os.path.isdir(subdir):
                            for root, _, files in os.walk(subdir):
                                for fn in files:
                                    rel = os.path.relpath(os.path.join(root, fn), os.path.join(base, d)).replace("\\", "/")
                                    archivos.append(rel)
                    unidades.append({"id": m.get("id", d), "tipo": tipo, "nombre": m.get("nombre", d),
                                     "descripcion": m.get("descripcion", ""), "nivel": m.get("nivel", ""),
                                     "tags": m.get("tags", []), "tags_cursos": m.get("tags_cursos", []),
                                     "aplica_a": m.get("aplica_a", []), "depende_de": m.get("depende_de", []),
                                     "requisitos": m.get("requisitos", []), "probado": m.get("probado", False),
                                     "version": m.get("version", ""), "archivos": archivos,
                                     "ruta": f"biblioteca/{carpeta}/{d}"})
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "unidades": unidades, "total": len(unidades)}, ensure_ascii=False).encode("utf-8"))
            return
        elif path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if path in ["/", "/index.html"]:
            self.send_response(302)
            self.send_header("Location", "/devops_hub.html")
            self.end_headers()
            return
        log_event("FILE", f"Sirviendo archivo: {path}")
        filepath = os.path.join(STUDENT_DIR, path.lstrip('/'))
        log_event("FILE", f"Ruta completa: {filepath}")
        log_event("FILE", f"¿Existe?: {os.path.exists(filepath)}")
        super().do_GET()

    def do_POST(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path

        if path == "/api/importar":
            import base64, io, zipfile, tempfile, shutil
            from urllib.request import urlopen
            def _resp(o, code=200):
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(o, ensure_ascii=False).encode("utf-8"))
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
            origen = (body.get("origen_url") or "").strip()
            zip_b64 = body.get("zip_b64") or ""
            try:
                if origen:
                    datos = urlopen(origen, timeout=30).read()
                elif zip_b64:
                    datos = base64.b64decode(zip_b64)
                else:
                    _resp({"ok": False, "error": "falta origen_url o zip_b64"}, 400); return
                tmp = tempfile.mkdtemp()
                with zipfile.ZipFile(io.BytesIO(datos)) as z:
                    z.extractall(tmp)
                man_path = tipo = None
                mejor_prof = 1e9
                for root, _, files in os.walk(tmp):
                    if "dependencias" in root.replace("\\", "/").split("/"):
                        continue
                    for fn in files:
                        if fn in ("ejercicio.json", "proyecto.json"):
                            prof = len(os.path.relpath(root, tmp).replace("\\", "/").split("/"))
                            if prof < mejor_prof:
                                mejor_prof = prof
                                man_path, tipo = os.path.join(root, fn), fn[:-5]
                if not man_path:
                    shutil.rmtree(tmp, ignore_errors=True)
                    _resp({"ok": False, "error": "el paquete no tiene manifiesto (ejercicio/proyecto.json)"}, 400); return
                with open(man_path, encoding="utf-8") as fh:
                    m = json.load(fh)
                uid = m.get("id", "sin-id")
                destino_rel = (m.get("entrega", {}).get("destino_alumno")
                               or f"biblioteca/{'proyectos' if tipo == 'proyecto' else 'ejercicios'}/{uid}/").rstrip("/").lstrip("/")
                destino = os.path.join(STUDENT_DIR, destino_rel.replace("/", os.sep))
                src = os.path.dirname(man_path)
                if os.path.exists(destino):
                    shutil.rmtree(destino)
                shutil.copytree(src, destino)
                shutil.rmtree(tmp, ignore_errors=True)
                n = sum(len(fs) for sub in ("lab", "infra")
                        for _, _, fs in os.walk(os.path.join(destino, sub)) if os.path.isdir(os.path.join(destino, sub)))
                log_event("IMPORTAR", f"{tipo} '{uid}' -> {destino_rel} ({n} archivos de codigo)")
                _resp({"ok": True, "id": uid, "tipo": tipo, "destino": destino_rel, "archivos_codigo": n})
            except Exception as e:
                _resp({"ok": False, "error": str(e)}, 500)
            return

        if path == "/api/ejecutar":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                body = json.loads(post_data)
            except Exception:
                body = {}
            command = body.get("command", "").strip()
            as_admin = bool(body.get("admin", False))
            if not command:
                self.send_json({"ok": False, "error": "No se especificó ningún comando para ejecutar."}, status=400)
                return
            ok = launch_in_terminal(command, as_admin=as_admin, cwd=WRITABLE_DIR)
            self.send_json({
                "ok": ok,
                "admin": as_admin,
                "command": command,
                "message": f"Terminal {'con elevación de Administrador' if as_admin else 'de usuario estándar'} abierta con éxito."
            })
            return

        elif path == "/api/guardar_apunte":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                body = json.loads(post_data)
            except Exception:
                body = {}
            nombre = body.get("nombre", "").strip()
            contenido = body.get("contenido", "")
            if not nombre:
                self.send_json({"ok": False, "error": "Nombre de archivo obligatorio."}, status=400)
                return
            if not nombre.endswith((".md", ".txt", ".json", ".yaml", ".yml", ".sh", ".ps1")):
                nombre += ".md"
            safe_name = os.path.basename(nombre)
            target_path = os.path.join(MIS_APUNTES_DIR, safe_name)
            try:
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(contenido)
                log_event("NOTE", f"Apunte guardado: mis_apuntes/{safe_name}")
                self.send_json({
                    "ok": True,
                    "rel_path": f"mis_apuntes/{safe_name}",
                    "mensaje": f"Archivo '{safe_name}' guardado correctamente en tus apuntes."
                })
            except Exception as e:
                self.send_json({"ok": False, "error": f"Error escribiendo archivo: {str(e)}"}, status=500)
            return

        elif path == "/api/mapa_estudio/importar":
            self.handle_mapa_estudio_importar()
            return

        elif path == "/api/motor_local":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                body = json.loads(post_data)
            except Exception:
                body = {}
            self.handle_motor_local(body)
            return

        self.send_json({"error": "Endpoint no encontrado"}, status=404)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def handle_api_curso(self):
        """Devuelve los metadatos del curso actual leyendo curso.json o esqueleto genérico."""
        curso_file = os.path.join(STUDENT_DIR, "curso.json")
        if os.path.exists(curso_file):
            try:
                with open(curso_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.send_json({"ok": True, "curso": data})
                return
            except Exception as e:
                log_event("ERROR", f"Error parseando curso.json: {e}")
        self.send_json({
            "ok": True,
            "curso": {
                "curso_id": "MODULAR_HUB",
                "titulo": "Plataforma Educativa Universal",
                "institucion": "Comunidad DevOps",
                "descripcion": "Chasis educativo modular adaptable a cualquier materia.",
                "total_clases": 0,
                "total_horas": 0,
                "herramientas_count": len(TOOLS_CATALOG),
                "categorias": []
            }
        })

    def handle_api_mis_apuntes(self):
        """Lista los archivos en mis_apuntes/ y practicas/."""
        apuntes_list = []
        for carpeta in ["mis_apuntes", "practicas", "aportes"]:
            folder_p = os.path.join(base_dir_para(carpeta), carpeta)
            if os.path.exists(folder_p):
                for root, _, files in os.walk(folder_p):
                    for f in sorted(files):
                        abs_p = os.path.join(root, f)
                        rel_p = os.path.relpath(abs_p, base_dir_para(carpeta)).replace("\\", "/")
                        size_kb = round(os.path.getsize(abs_p) / 1024, 2)
                        apuntes_list.append({
                            "archivo": f,
                            "rel_path": rel_p,
                            "tamano_kb": size_kb,
                            "carpeta": carpeta
                        })
        self.send_json({"ok": True, "apuntes": apuntes_list})

    def handle_api_materiales(self):
        """Catálogo de materiales de estudio disponibles para el Bot IA (guías oficiales, apuntes y aportes).
        Selección explícita en vez de RAG: el alumno elige el documento y se envía completo como contexto
        (mismo criterio que el bot de study-cybercirujas, ver docs/STUDY_BOT_DESIGN.md del proyecto)."""
        materiales = []

        guias_raiz = [
            ("01-Guia-Completa-Instalacion-Windows.md", "Guía Instalación Windows", "guia"),
            ("02-Guia-Instalacion-Linux.md", "Guía Instalación Linux", "guia"),
            ("03-Guia-Instalacion-MacOS.md", "Guía Instalación macOS", "guia"),
            ("04-Guia-Linux-en-Windows-WSL2-Grafica.md", "Guía Linux en Windows (WSL2 + WSLg)", "guia"),
            ("01-Instalacion-Software-y-Diagnostico.md", "Instalación de Software y Diagnóstico", "guia"),
            ("README.md", "Introducción al Workspace / Student Hub", "guia"),
        ]
        for rel_name, titulo, cat in guias_raiz:
            abs_p = os.path.join(WRITABLE_DIR, rel_name)
            if not os.path.isfile(abs_p):
                abs_p = os.path.join(STUDENT_DIR, rel_name)
            if os.path.exists(abs_p):
                materiales.append({
                    "titulo": titulo,
                    "rel_path": rel_name,
                    "categoria": cat,
                    "tamano_kb": round(os.path.getsize(abs_p) / 1024, 2)
                })

        carpetas = [
            ("apuntes", "apunte_curso", "Apunte del curso"),
            ("mis_apuntes", "mi_apunte", "Mi apunte"),
            ("practicas", "practica", "Práctica"),
            ("aportes", "aporte", "Aporte"),
        ]
        for carpeta, cat, etiqueta in carpetas:
            folder_p = os.path.join(base_dir_para(carpeta), carpeta)
            if os.path.exists(folder_p):
                for root, _, files in os.walk(folder_p):
                    for f in sorted(files):
                        if f.lower() == "readme.md":
                            continue
                        if not f.lower().endswith((".md", ".markdown", ".txt")):
                            continue
                        abs_p = os.path.join(root, f)
                        rel_p = os.path.relpath(abs_p, base_dir_para(carpeta)).replace("\\", "/")
                        nombre_limpio = os.path.splitext(f)[0].replace("_", " ").replace("-", " ")
                        materiales.append({
                            "titulo": f"{etiqueta}: {nombre_limpio}",
                            "rel_path": rel_p,
                            "categoria": cat,
                            "tamano_kb": round(os.path.getsize(abs_p) / 1024, 2)
                        })

        self.send_json({"ok": True, "materiales": materiales})

    # ==================================================================
    # TEMARIO EN VIVO DE study.cybercirujas.club — otra fuente de material
    # explícito para el Bot IA, además de los archivos locales y el Mapa de
    # Estudio del docente. Mismo criterio "selección explícita" que el resto:
    # el alumno elige certificación + tema y se manda el contenido completo.
    # ==================================================================
    def handle_cybercirujas_catalogo(self):
        ok, data = fetch_cybercirujas("/api/catalog")
        if not ok:
            self.send_json({"ok": False, "error": f"No se pudo contactar a study.cybercirujas.club: {data}"}, status=502)
            return
        certificaciones = [
            {"id": cert_id, "name": info.get("name", cert_id), "vendor": info.get("vendor", ""), "level": info.get("level", ""), "category": info.get("category", "")}
            for cert_id, info in data.items()
        ]
        certificaciones.sort(key=lambda c: (c["vendor"], c["name"]))
        self.send_json({"ok": True, "certificaciones": certificaciones})

    def handle_cybercirujas_temario(self, cert_id):
        if not cert_id:
            self.send_json({"ok": False, "error": "Falta el parámetro cert"}, status=400)
            return
        ok, data = fetch_cybercirujas(f"/api/certs/{urllib.parse.quote(cert_id)}")
        if not ok:
            self.send_json({"ok": False, "error": f"No se pudo obtener el temario de '{cert_id}': {data}"}, status=502)
            return
        topics = [
            {"id": t.get("id"), "title": t.get("title"), "topic": t.get("topic"), "weight": t.get("weight"), "available": t.get("available", False)}
            for t in data.get("topics", [])
        ]
        self.send_json({"ok": True, "cert": data.get("cert", {}).get("name", cert_id), "topics": topics})

    def handle_cybercirujas_material(self, cert_id, topic_id, lang):
        if not cert_id or not topic_id:
            self.send_json({"ok": False, "error": "Faltan los parámetros cert y topic"}, status=400)
            return
        path = f"/api/certs/{urllib.parse.quote(cert_id)}/topics/{urllib.parse.quote(topic_id)}?lang={urllib.parse.quote(lang or 'es')}"
        ok, data = fetch_cybercirujas(path)
        if not ok:
            self.send_json({"ok": False, "error": f"No se pudo obtener el material: {data}"}, status=502)
            return
        titulo = (data.get("topic") or {}).get("title", f"{cert_id} {topic_id}")
        self.send_json({
            "ok": True,
            "titulo": f"{cert_id.upper()} {topic_id} — {titulo}",
            "contenido": data.get("content", ""),
            "generado_por": (data.get("generated_by") or {}).get("model", "desconocido"),
            "lang": data.get("lang", lang)
        })

    # ==================================================================
    # MAPA DE ESTUDIO — RAG local (import del export del docente + búsqueda
    # FTS5) y motor de IA alternativo (Ollama local / CLI instalada).
    # Mismo esquema y filosofía que el RAG del docente (scripts/servidor_docente_rag.py):
    # tabla + tabla virtual FTS5, motor "call_ai_engine" con subprocess/HTTP,
    # adaptado para correr 100% en la máquina del alumno.
    # ==================================================================
    def handle_mapa_estudio_estado(self):
        if not os.path.exists(LOCAL_RAG_DB):
            self.send_json({"ok": True, "importado": False})
            return
        try:
            con = sqlite3.connect(LOCAL_RAG_DB)
            total = con.execute("SELECT COUNT(*) FROM conocimiento").fetchone()[0]
            categorias = [r[0] for r in con.execute("SELECT DISTINCT categoria FROM conocimiento ORDER BY categoria")]
            con.close()
            importado_el = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(LOCAL_RAG_DB)))
            self.send_json({"ok": True, "importado": True, "total": total, "categorias": categorias, "importado_el": importado_el})
        except Exception as e:
            self.send_json({"ok": False, "error": f"Índice local dañado, reimportá: {e}"}, status=500)

    def handle_mapa_estudio_importar(self):
        htmls = []
        if os.path.exists(MAPA_ESTUDIO_DIR):
            htmls = [f for f in os.listdir(MAPA_ESTUDIO_DIR) if f.lower().endswith(".html")]
        if not htmls:
            self.send_json({
                "ok": False,
                "error": "No se encontró ningún .html en la carpeta mapa_estudio/. Pedile al docente el export ('Mapa de Estudio') y colocalo ahí."
            }, status=404)
            return
        htmls.sort(key=lambda f: os.path.getmtime(os.path.join(MAPA_ESTUDIO_DIR, f)), reverse=True)
        origen = htmls[0]
        origen_path = os.path.join(MAPA_ESTUDIO_DIR, origen)
        try:
            with open(origen_path, "r", encoding="utf-8") as f:
                html_text = f.read()
            m = re.search(r'<script type="application/json" id="mapa-estudio-data">(.*?)</script>', html_text, re.DOTALL)
            if not m:
                self.send_json({"ok": False, "error": f"'{origen}' no tiene el formato de Mapa de Estudio esperado (falta el bloque de datos)."}, status=400)
                return
            payload = json.loads(m.group(1))
            documentos = payload.get("documentos", [])

            if os.path.exists(LOCAL_RAG_DB):
                os.remove(LOCAL_RAG_DB)
            con = sqlite3.connect(LOCAL_RAG_DB)
            con.execute("""CREATE TABLE conocimiento (
                id INTEGER PRIMARY KEY, titulo TEXT, categoria TEXT, clase INTEGER,
                modulo TEXT, tags TEXT, resumen TEXT, contenido TEXT, fuente TEXT
            )""")
            con.execute("CREATE VIRTUAL TABLE conocimiento_fts USING fts5(titulo, contenido, tags, content='conocimiento', content_rowid='id')")
            for d in documentos:
                con.execute(
                    "INSERT INTO conocimiento (id, titulo, categoria, clase, modulo, tags, resumen, contenido, fuente) VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        d.get("id"), d.get("titulo", ""), d.get("categoria", ""), d.get("clase"),
                        d.get("modulo", ""), ", ".join(d.get("tags", []) or []), d.get("resumen", ""),
                        d.get("contenido", ""), d.get("fuente", "")
                    )
                )
            con.execute("INSERT INTO conocimiento_fts(conocimiento_fts) VALUES ('rebuild')")
            con.commit()
            total = con.execute("SELECT COUNT(*) FROM conocimiento").fetchone()[0]
            categorias = [r[0] for r in con.execute("SELECT DISTINCT categoria FROM conocimiento ORDER BY categoria")]
            con.close()
            log_event("RAG", f"Mapa de Estudio importado desde {origen}: {total} documentos indexados localmente.")
            self.send_json({"ok": True, "total": total, "categorias": categorias, "origen": origen})
        except Exception as e:
            self.send_json({"ok": False, "error": f"Error importando el mapa de estudio: {e}"}, status=500)

    def handle_mapa_estudio_buscar(self, q, limit=8):
        if not os.path.exists(LOCAL_RAG_DB):
            self.send_json({"ok": False, "error": "Todavía no importaste un Mapa de Estudio. Primero presioná 'Importar / Reindexar'."}, status=404)
            return
        words = re.findall(r"[\w\u00c0-\u017f]+", q, flags=re.UNICODE)
        if not words:
            self.send_json({"ok": True, "resultados": []})
            return
        tokens = [f'"{w}"' for w in words]
        con = sqlite3.connect(LOCAL_RAG_DB)
        con.row_factory = sqlite3.Row
        sql = """
            SELECT c.id, c.titulo, c.categoria, c.clase, c.modulo, c.tags, c.resumen,
                   snippet(conocimiento_fts, 1, '**', '**', '…', 10) AS fragmento
            FROM conocimiento_fts f JOIN conocimiento c ON f.rowid = c.id
            WHERE conocimiento_fts MATCH ? ORDER BY rank LIMIT ?
        """
        try:
            filas = con.execute(sql, (" AND ".join(tokens), limit)).fetchall()
            if not filas:
                filas = con.execute(sql, (" OR ".join(tokens), limit)).fetchall()
        except sqlite3.OperationalError as e:
            con.close()
            self.send_json({"ok": False, "error": f"Consulta inválida: {e}"}, status=400)
            return
        con.close()
        self.send_json({"ok": True, "resultados": [dict(r) for r in filas]})

    def handle_mapa_estudio_documento(self, doc_id):
        if not os.path.exists(LOCAL_RAG_DB):
            self.send_json({"ok": False, "error": "No hay índice local importado."}, status=404)
            return
        con = sqlite3.connect(LOCAL_RAG_DB)
        con.row_factory = sqlite3.Row
        fila = con.execute(
            "SELECT id, titulo, categoria, clase, modulo, tags, contenido, fuente FROM conocimiento WHERE id = ?",
            (doc_id,)
        ).fetchone()
        con.close()
        if not fila:
            self.send_json({"ok": False, "error": f"No existe el documento id={doc_id}"}, status=404)
            return
        self.send_json({"ok": True, "documento": dict(fila)})

    def handle_ollama_modelos(self):
        """Detecta los modelos realmente descargados en el Ollama local del alumno (GET /api/tags),
        para que el selector de la UI ofrezca modelos reales en vez de un nombre adivinado."""
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            modelos = [m.get("name") for m in data.get("models", []) if m.get("name")]
            self.send_json({"ok": True, "disponible": True, "modelos": modelos})
        except Exception:
            self.send_json({"ok": True, "disponible": False, "modelos": []})

    def handle_motor_local(self, body):
        """Motor de IA alternativo a OpenRouter: Ollama local o una CLI de agente instalada
        (claude / gemini / omp / codex). Mismo patrón que call_ai_engine() del servidor RAG
        del docente (scripts/servidor_docente_rag.py), sin dependencias de clave externa."""
        engine = body.get("engine", "")
        system_prompt = body.get("system", "")
        pregunta = (body.get("pregunta") or "").strip()
        historial = body.get("historial", []) or []
        if not pregunta:
            self.send_json({"ok": False, "error": "Falta la pregunta."}, status=400)
            return

        start = time.time()

        if engine == "ollama":
            modelo = (body.get("ollama_model") or "llama3.2").strip()
            mensajes = [{"role": "system", "content": system_prompt}]
            for h in historial[-6:]:
                if h.get("role") in ("user", "assistant") and h.get("content"):
                    mensajes.append({"role": h["role"], "content": h["content"]})
            mensajes.append({"role": "user", "content": pregunta})
            try:
                req = urllib.request.Request(
                    "http://localhost:11434/api/chat",
                    data=json.dumps({"model": modelo, "messages": mensajes, "stream": False}).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=90) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                respuesta = (data.get("message") or {}).get("content", "").strip()
                if not respuesta:
                    self.send_json({"ok": False, "error": f"Ollama respondió vacío para '{modelo}'. ¿Lo descargaste? Probá: ollama pull {modelo}"}, status=502)
                    return
                self.send_json({"ok": True, "respuesta": respuesta, "motor": f"ollama:{modelo}", "elapsed_seg": round(time.time() - start, 1)})
            except urllib.error.HTTPError as e:
                # Ollama SÍ está corriendo (contestó), pero rechazó la request — típicamente
                # el modelo pedido no está descargado. Nunca confundir esto con "no conecta".
                try:
                    detalle = json.loads(e.read().decode("utf-8")).get("error", "")
                except Exception:
                    detalle = ""
                if "not found" in detalle.lower():
                    self.send_json({"ok": False, "error": f"Ollama está corriendo, pero no tenés el modelo '{modelo}' descargado. Ejecutá: ollama pull {modelo}"}, status=404)
                else:
                    self.send_json({"ok": False, "error": f"Ollama rechazó la consulta: {detalle or e.reason}"}, status=502)
            except urllib.error.URLError:
                self.send_json({"ok": False, "error": "No se pudo conectar con Ollama en localhost:11434. ¿Está instalado y corriendo? Ejecutá: ollama serve"}, status=502)
            except Exception as e:
                self.send_json({"ok": False, "error": f"Error consultando Ollama: {e}"}, status=500)
            return

        if engine == "cli":
            cli_id = (body.get("cli") or "").strip()
            # via "stdin": el prompt se manda por entrada estándar (igual que claude -p en el servidor docente).
            # via "arg": el prompt se pasa como argumento de línea de comandos.
            cli_configs = {
                "claude": {"bin": "claude", "args": ["-p"], "via": "stdin"},
                "gemini": {"bin": "gemini", "args": ["-p"], "via": "arg"},
                "omp": {"bin": "omp", "args": [], "via": "arg"},
                "codex": {"bin": "codex", "args": ["exec"], "via": "arg"},
            }
            cfg = cli_configs.get(cli_id)
            if not cfg:
                self.send_json({"ok": False, "error": f"CLI no soportada: {cli_id}"}, status=400)
                return
            binario = shutil.which(cfg["bin"])
            if not binario:
                self.send_json({
                    "ok": False,
                    "error": f"No se encontró '{cfg['bin']}' instalado en tu PATH. Instalalo desde la pestaña 'Instalación & Software' (categoría 🤖 Agentes IA)."
                }, status=404)
                return

            historial_txt = ""
            for h in historial[-6:]:
                if h.get("role") == "user":
                    historial_txt += f"\nAlumno: {h.get('content', '')}\n"
                elif h.get("role") == "assistant":
                    historial_txt += f"Asistente: {h.get('content', '')}\n"
            full_prompt = f"{system_prompt}\n{historial_txt}\nAlumno: {pregunta}\nAsistente:"

            try:
                log_event("CLI", f"Invocando {cfg['bin']} para el Asistente IA del alumno...")
                if cfg["via"] == "stdin":
                    res = subprocess.run([binario] + cfg["args"], input=full_prompt, capture_output=True, text=True, encoding="utf-8", timeout=120)
                else:
                    res = subprocess.run([binario] + cfg["args"] + [full_prompt], capture_output=True, text=True, encoding="utf-8", timeout=120)
                respuesta = (res.stdout or "").strip()
                if res.returncode != 0 or not respuesta:
                    error_txt = (res.stderr or "sin salida").strip()[:300]
                    self.send_json({"ok": False, "error": f"{cfg['bin']} finalizó con error: {error_txt}"}, status=502)
                    return
                self.send_json({"ok": True, "respuesta": respuesta, "motor": f"cli:{cfg['bin']}", "elapsed_seg": round(time.time() - start, 1)})
            except subprocess.TimeoutExpired:
                self.send_json({"ok": False, "error": f"{cfg['bin']} tardó demasiado (más de 120s) y se canceló."}, status=504)
            except Exception as e:
                self.send_json({"ok": False, "error": f"Error ejecutando {cfg['bin']}: {e}"}, status=500)
            return

        self.send_json({"ok": False, "error": f"Motor desconocido: {engine}"}, status=400)

    def handle_exportar_aportes(self):
        """Genera un archivo ZIP con todos los apuntes y prácticas del alumno para compartir."""
        log_event("EXPORT", "Generando paquete ZIP de aportes del alumno...")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            meta = {
                "plataforma": "DevOps Student Hub Universal",
                "exportado_el": time.strftime("%Y-%m-%d %H:%M:%S"),
                "os": sys.platform
            }
            curso_file = os.path.join(STUDENT_DIR, "curso.json")
            if os.path.exists(curso_file):
                try:
                    with open(curso_file, "r", encoding="utf-8") as cf:
                        meta["curso"] = json.load(cf)
                except Exception:
                    pass
            zip_file.writestr("info_exportacion.json", json.dumps(meta, indent=2, ensure_ascii=False))
            carpetas_a_incluir = ["mis_apuntes", "practicas", "aportes", "apuntes"]
            archivos_agregados = 0
            for carpeta in carpetas_a_incluir:
                folder_path = os.path.join(base_dir_para(carpeta), carpeta)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    for root, _, files in os.walk(folder_path):
                        for f in files:
                            full_p = os.path.join(root, f)
                            rel_p = os.path.relpath(full_p, base_dir_para(carpeta))
                            zip_file.write(full_p, arcname=rel_p)
                            archivos_agregados += 1
            if archivos_agregados == 0:
                zip_file.writestr("mis_apuntes/ejemplo_notas.md", "# Mis Notas DevOps\n\nAquí puedes escribir tus apuntes y soluciones de ejercicios.")
        zip_data = zip_buffer.getvalue()
        filename = f"aportes_alumno_{time.strftime('%Y%m%d_%H%M%S')}.zip"
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(zip_data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(zip_data)
        log_event("EXPORT", f"Paquete exportado exitosamente: {filename} ({len(zip_data)} bytes)")

    def handle_api_videos(self):
        videos_list = []
        if os.path.exists(VIDEOS_DIR):
            for root, _, files in os.walk(VIDEOS_DIR):
                for f in sorted(files):
                    if f.lower().endswith((".mp4", ".mkv", ".webm", ".mov", ".avi")):
                        abs_p = os.path.join(root, f)
                        rel_p = os.path.relpath(abs_p, VIDEOS_DIR).replace("\\", "/")
                        size_mb = round(os.path.getsize(abs_p) / (1024 * 1024), 2)
                        clean_title = os.path.splitext(f)[0].replace("_", " ").replace("-", " ").title()
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
        target_path = os.path.join(WRITABLE_DIR, clean_rel)
        if not os.path.isfile(target_path):
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
            self.wfile.write(json.dumps({"error": f"Archivo no encontrado: {rel_path}"}).encode("utf-8"))

def open_browser_after_start():
    time.sleep(1.0)
    url = f"http://localhost:{PORT}/devops_hub.html"
    try:
        webbrowser.open(url)
        log_event("BROWSER", f"Navegador abierto en {url}")
    except Exception as e:
        log_event("WARN", f"Aviso abriendo navegador: {e}")

def run_server():
    os.chdir(WRITABLE_DIR)
    log_event("CHDIR", f"Directorio de trabajo actual: {os.getcwd()}")
    log_event("CHDIR", f"Archivos en ese directorio: {os.listdir('.')[:10]}")
    server_address = ("", PORT)
    httpd = ThreadedHTTPServer(server_address, StudentHubHandler)
    log_event("SERVER", f"Servidor Alumnos activo en http://localhost:{PORT}")
    threading.Thread(target=open_browser_after_start, daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log_event("SERVER", "Deteniendo servidor...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
