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
    # Ejecutandose como binario compilado (.exe)
    base_exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    if not os.path.exists(os.path.join(base_exe_dir, "devops_hub.html")) and os.path.exists(os.path.join(os.path.dirname(base_exe_dir), "devops_hub.html")):
        STUDENT_DIR = os.path.dirname(base_exe_dir)
        SCRIPT_DIR = base_exe_dir
    else:
        STUDENT_DIR = base_exe_dir
        SCRIPT_DIR = os.path.join(STUDENT_DIR, "scripts")
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    STUDENT_DIR = os.path.dirname(SCRIPT_DIR)

VIDEOS_DIR = os.path.join(STUDENT_DIR, "videos")
MIS_APUNTES_DIR = os.path.join(STUDENT_DIR, "mis_apuntes")
PRACTICAS_DIR = os.path.join(STUDENT_DIR, "practicas")

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(MIS_APUNTES_DIR, exist_ok=True)
os.makedirs(PRACTICAS_DIR, exist_ok=True)

SYSTEM_LOGS = []

def log_event(level, msg):
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {msg}"
    print(log_entry, flush=True)
    SYSTEM_LOGS.append(log_entry)
    if len(SYSTEM_LOGS) > 200:
        SYSTEM_LOGS.pop(0)

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
        cwd = STUDENT_DIR

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
        elif path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if path in ["/", "/index.html"]:
            self.send_response(302)
            self.send_header("Location", "/devops_hub.html")
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path

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
            ok = launch_in_terminal(command, as_admin=as_admin, cwd=STUDENT_DIR)
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
            folder_p = os.path.join(STUDENT_DIR, carpeta)
            if os.path.exists(folder_p):
                for root, _, files in os.walk(folder_p):
                    for f in sorted(files):
                        abs_p = os.path.join(root, f)
                        rel_p = os.path.relpath(abs_p, STUDENT_DIR).replace("\\", "/")
                        size_kb = round(os.path.getsize(abs_p) / 1024, 2)
                        apuntes_list.append({
                            "archivo": f,
                            "rel_path": rel_p,
                            "tamano_kb": size_kb,
                            "carpeta": carpeta
                        })
        self.send_json({"ok": True, "apuntes": apuntes_list})

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
                folder_path = os.path.join(STUDENT_DIR, carpeta)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    for root, _, files in os.walk(folder_path):
                        for f in files:
                            full_p = os.path.join(root, f)
                            rel_p = os.path.relpath(full_p, STUDENT_DIR)
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
