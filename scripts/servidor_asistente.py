#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
   SERVIDOR ASISTENTE & HUB DEVOPS UNIVERSAL
===============================================================================
Servidor local multihilo que provee:
  1. Interfaz Web DevOps Hub: course_hub.html y reproductor de video local.
  2. Streaming de Videos Locales (videos/*.mp4 con soporte HTTP Range 206).
  3. Motor de Búsqueda RAG sobre la base SQLite FTS5 (data/devops_knowledge.db).
  4. Tutor IA con modos: Tutor DevOps, Laboratorio/Terminal, Exámenes/Certificaciones.
  5. Re-indexación dinámica en 1 clic de cualquier carpeta (apuntes, material, etc.).
===============================================================================
"""

import os
import sys
import re
import json
import sqlite3
import urllib.request
import urllib.parse
import subprocess
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
DATA_DIR = os.path.join(STUDENT_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "devops_knowledge.db")
VIDEOS_DIR = os.path.join(STUDENT_DIR, "videos")
CHATS_FILE = os.path.join(DATA_DIR, "chats_guardados.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)

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

    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        query = urllib.parse.parse_qs(url_parts.query)

        # 1. API: Estadísticas de la Base de Conocimiento
        if path == "/api/stats":
            self.handle_api_stats()
            return

        # 2. API: Catálogo dinámico de videos locales
        elif path == "/api/videos":
            self.handle_api_videos()
            return

        # 3. API: Búsqueda RAG en SQLite FTS5
        elif path == "/api/search":
            q = query.get("q", [""])[0]
            cat = query.get("category", [None])[0]
            self.handle_api_search(q, category_filter=cat)
            return

        # 4. API: Historial de Chats Guardados
        elif path == "/api/saved_chats":
            self.handle_get_saved_chats()
            return

        # 5. Streaming de Videos Locales (/videos/<filename>)
        elif path.startswith("/videos/"):
            filename = urllib.parse.unquote(path[8:])
            self.handle_video_streaming(filename)
            return

        # 6. Favicon 204
        elif path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        # Redirigir raíz al portal principal
        if path in ["/", "/index.html"]:
            self.send_response(302)
            self.send_header("Location", "/course_hub.html")
            self.end_headers()
            return

        super().do_GET()

    def do_POST(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            body = json.loads(post_data.decode("utf-8"))
        except Exception:
            body = {}

        # 1. API: Consulta al Tutor IA (/api/ask)
        if path == "/api/ask":
            self.handle_api_ask(body)
            return

        # 2. API: Re-indexación RAG (/api/reindex)
        elif path == "/api/reindex":
            self.handle_api_reindex()
            return

        # 3. API: Guardar Chat (/api/saved_chats)
        elif path == "/api/saved_chats":
            self.handle_save_chat(body)
            return

        self.send_response(404)
        self.end_headers()

    # -------------------------------------------------------------------------
    # HANDLERS DE APIS
    # -------------------------------------------------------------------------

    def handle_api_stats(self):
        if not os.path.exists(DB_PATH):
            self.send_json({"ok": False, "error": "Base de datos no inicializada. Ejecuta actualizar-mi-base.bat", "total_docs": 0})
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM course_docs;")
            total = c.fetchone()[0]

            c.execute("SELECT category, COUNT(*) FROM course_docs GROUP BY category;")
            cats = dict(c.fetchall())

            conn.close()

            # Contar videos disponibles en videos/
            video_files = []
            if os.path.exists(VIDEOS_DIR):
                for root, _, files in os.walk(VIDEOS_DIR):
                    for f in files:
                        if f.lower().endswith(('.mp4', '.mkv', '.webm', '.avi', '.mov')):
                            video_files.append(f)

            self.send_json({
                "ok": True,
                "total_docs": total,
                "categories": cats,
                "total_videos": len(video_files),
                "db_path": DB_PATH
            })
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)})

    def handle_api_videos(self):
        videos_list = []
        if os.path.exists(VIDEOS_DIR):
            for root, _, files in os.walk(VIDEOS_DIR):
                for f in sorted(files):
                    if f.lower().endswith(('.mp4', '.mkv', '.webm', '.mov', '.avi')):
                        abs_p = os.path.join(root, f)
                        rel_p = os.path.relpath(abs_p, VIDEOS_DIR).replace('\\', '/')
                        size_mb = round(os.path.getsize(abs_p) / (1024 * 1024), 2)
                        
                        # Generar título amigable a partir del nombre del archivo
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

                with open(video_path, "rb") as vf:
                    vf.seek(start)
                    bytes_remaining = length
                    while bytes_remaining > 0:
                        chunk_size = min(bytes_remaining, 64 * 1024)
                        data = vf.read(chunk_size)
                        if not data:
                            break
                        try:
                            self.wfile.write(data)
                            bytes_remaining -= len(data)
                        except (ConnectionResetError, ConnectionAbortedError):
                            break
                return

        # Solicitud normal completa
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()

        with open(video_path, "rb") as vf:
            try:
                while True:
                    data = vf.read(64 * 1024)
                    if not data:
                        break
                    self.wfile.write(data)
            except (ConnectionResetError, ConnectionAbortedError):
                pass

    def handle_api_search(self, query_str, category_filter=None):
        if not os.path.exists(DB_PATH) or not query_str.strip():
            self.send_json({"ok": True, "results": []})
            return

        results = search_in_db(query_str, category_filter=category_filter, limit=10)
        self.send_json({"ok": True, "query": query_str, "results": results})

    def handle_api_ask(self, body):
        question = body.get("question", "").strip()
        mode = body.get("mode", "tutor")  # tutor | lab_assistant | quiz_practice | doc_qa
        cat_filter = body.get("category")

        if not question:
            self.send_json({"ok": False, "error": "Pregunta vacía."})
            return

        # 1. Recuperación RAG de fragmentos relevantes
        results = search_in_db(question, category_filter=cat_filter, limit=6)

        # 2. Construcción del Prompt Pedagógico
        system_prompt = build_student_prompt(mode)
        context_text = build_context_snippet(results)

        # 3. Invocación del Modelo (Gemini -> Ollama -> RAG Offline Fallback)
        response_text, provider = execute_ai_query(system_prompt, question, context_text)

        self.send_json({
            "ok": True,
            "answer": response_text,
            "provider": provider,
            "mode": mode,
            "sources": results
        })

    def handle_api_reindex(self):
        index_script = os.path.join(SCRIPT_DIR, "crear_indice_rag.py")
        try:
            out = subprocess.check_output([sys.executable, index_script], stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
            self.send_json({"ok": True, "message": "Base de conocimiento actualizada con éxito.", "output": out})
        except Exception as e:
            self.send_json({"ok": False, "error": f"Error re-indexando: {e}"})

    def handle_get_saved_chats(self):
        if os.path.exists(CHATS_FILE):
            try:
                with open(CHATS_FILE, "r", encoding="utf-8") as f:
                    chats = json.load(f)
                self.send_json({"ok": True, "chats": chats})
                return
            except Exception:
                pass
        self.send_json({"ok": True, "chats": []})

    def handle_save_chat(self, body):
        chats = []
        if os.path.exists(CHATS_FILE):
            try:
                with open(CHATS_FILE, "r", encoding="utf-8") as f:
                    chats = json.load(f)
            except Exception:
                pass

        chats.insert(0, body)
        chats = chats[:50]  # Mantener últimos 50

        try:
            with open(CHATS_FILE, "w", encoding="utf-8") as f:
                json.dump(chats, f, indent=2, ensure_ascii=False)
            self.send_json({"ok": True})
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)})

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

# -----------------------------------------------------------------------------
# MOTOR DE BÚSQUEDA RAG & PROMPTS
# -----------------------------------------------------------------------------

def search_in_db(query_str, category_filter=None, limit=6):
    if not os.path.exists(DB_PATH):
        return []

    clean_q = re.sub(r'[^\w\s]', ' ', query_str)
    tokens = [w for w in clean_q.split() if len(w) > 2 and w.lower() not in ["como", "para", "este", "esta", "sobre", "cual", "quiero", "puedo"]]
    if not tokens:
        tokens = clean_q.split()
    if not tokens:
        return []

    fts_match = " OR ".join(tokens)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    results = []
    try:
        if category_filter and category_filter != "all":
            sql = """
                SELECT cd.id, cd.title, cd.category, cd.rel_path, cd.content, rank
                FROM course_docs_fts fts
                JOIN course_docs cd ON fts.rowid = cd.id
                WHERE course_docs_fts MATCH ? AND cd.category = ?
                ORDER BY rank
                LIMIT ?;
            """
            c.execute(sql, (fts_match, category_filter, limit))
        else:
            sql = """
                SELECT cd.id, cd.title, cd.category, cd.rel_path, cd.content, rank
                FROM course_docs_fts fts
                JOIN course_docs cd ON fts.rowid = cd.id
                WHERE course_docs_fts MATCH ?
                ORDER BY rank
                LIMIT ?;
            """
            c.execute(sql, (fts_match, limit))

        for row in c.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "category": row[2],
                "rel_path": row[3],
                "content": row[4][:600],
                "score": round(row[5], 3) if row[5] is not None else 0
            })
    except Exception as e:
        print(f" [!] Error en búsqueda FTS5: {e}")
    finally:
        conn.close()

    return results

def build_student_prompt(mode):
    if mode == "quiz_practice":
        return """Eres el Entrenador de Certificaciones y Entrevistas Técnicas Cloud DevOps.
Tu objetivo es ayudar al usuario a evaluar sus conocimientos técnicos (AWS, Docker, Kubernetes, Terraform, Git, CI/CD).
- Plantea de 1 a 3 preguntas desafiantes de opción múltiple con escenarios reales de producción.
- Si el usuario responde, califica con rigor técnico: explica detalladamente por qué la opción correcta es óptima y por qué las demás fallan o no son mejores prácticas."""

    elif mode == "lab_assistant":
        return """Eres el Asistente de Laboratorio, Terminal y Depuración DevOps.
Tu misión es asistir en la solución de errores en consola, comandos bash/powershell, sintaxis de Dockerfiles, Terraform HCL, Kubernetes manifests y pipelines de CI/CD.
- Da explicaciones paso a paso con los comandos exactos para resolver el problema.
- Muestra ejemplos prácticos y advierte sobre errores comunes."""

    elif mode == "doc_qa":
        return """Eres el Asistente de Documentación y Material Técnico.
Tu función es responder preguntas basándote estrictamente en las notas, guías, libros o apuntes indexados en el espacio de trabajo local del usuario."""

    # Default: tutor
    return """Eres un Mentor y Arquitecto Experto en Cloud DevOps e Infraestructura moderna.
Tu objetivo es que el usuario comprenda cada concepto técnico con profundidad conceptual, entusiasmo y aplicabilidad práctica real.
- Explica temas complejos con analogías claras antes de profundizar en la sintaxis.
- Proporciona ejemplos prácticos con comandos explicados.
- Integra las mejores prácticas de la industria (DORA, 12 Factors, IaC, GitOps, Observabilidad)."""

def build_context_snippet(results):
    if not results:
        return "No se encontraron fragmentos locales directamente relacionados. Utiliza tus conocimientos de ingeniería DevOps general."
    text = "=== FUENTES DE DOCUMENTACION Y APUNTES LOCALES ===\n\n"
    for r in results:
        text += f"--- [{r['category'].upper()}] {r['title']} (Archivo: {r['rel_path']}) ---\n"
        text += f"{r['content']}\n\n"
    return text

def execute_ai_query(system_prompt, question, context_text):
    full_prompt = f"{system_prompt}\n\n{context_text}\n\nConsulta:\n{question}\n\nRespuesta estructurada (usa formato Markdown claro con títulos, viñetas y bloques de código):"

    # 1. Probar Google Gemini si existe GEMINI_API_KEY
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1500}
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text, "Google Gemini 2.0 Flash"
        except Exception as e:
            print(f" [!] Falló Gemini API: {e}")

    # 2. Probar Ollama Local si está corriendo
    try:
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "qwen2.5:latest",
            "prompt": full_prompt,
            "stream": False
        }
        req = urllib.request.Request(ollama_url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["response"], "Ollama Local (qwen2.5)"
    except Exception:
        pass

    # 3. Fallback Inteligente RAG Offline
    fallback_text = f"### 💡 Respuesta Basada en tu Documentación Local:\n\n"
    fallback_text += f"He consultado tu base de datos SQLite y correlacionado los siguientes fragmentos para responder tu consulta sobre **'{question}'**:\n\n"
    
    if "No se encontraron" in context_text:
        fallback_text += "No encontré notas específicas en tus carpetas para este término. Puedes crear notas en `apuntes/` o colocar material en `material/` y re-indexar con un clic.\n\n"
        fallback_text += "> 💡 **Tip:** Puedes configurar una API Key gratuita de Gemini (`set GEMINI_API_KEY=...`) o ejecutar `ollama run qwen2.5` en tu máquina para habilitar razonamiento conversacional autónomo 100% offline."
    else:
        fallback_text += context_text.replace("=== FUENTES DE DOCUMENTACION Y APUNTES LOCALES ===", "").strip()
        fallback_text += "\n\n---\n*Para activar respuestas redactadas con modelos de lenguaje generativo, agrega tu `GEMINI_API_KEY` o inicia Ollama localmente.*"

    return fallback_text, "Motor RAG Offline (SQLite FTS5)"

def main():
    print("\n" + "=" * 80)
    print("   INICIANDO SERVIDOR DEL DEVOPS WORKSPACE & KNOWLEDGE HUB")
    print("======================================================================")
    print(f" [*] Directorio Raíz : {STUDENT_DIR}")
    print(f" [*] Base de Datos   : {DB_PATH}")
    print(f" [*] Carpeta Videos  : {VIDEOS_DIR}")
    print(f" [*] URL de Acceso   : http://localhost:{PORT}/course_hub.html")
    print("=" * 80)
    print("Presiona Ctrl + C para detener el servidor.\n")

    server = ThreadedHTTPServer(("127.0.0.1", PORT), StudentHubHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n [!] Servidor detenido por el usuario.")
        server.server_close()

if __name__ == "__main__":
    main()
