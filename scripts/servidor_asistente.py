#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
   SERVIDOR ASISTENTE & CAMPUS PERSONAL DEL ALUMNO (CLOUD DEVOPS 2026)
===============================================================================
Servidor local multihilo que provee:
  1. Interfaz Web del Estudiante: course_hub.html y reproductor de clases.
  2. Streaming de Videos Locales (mis_videos/*.mp4 con soporte de HTTP Range 206).
  3. Motor de Búsqueda RAG sobre la base SQLite FTS5 (data/devops_knowledge.db).
  4. Tutor IA con modos: Tutor de Estudio, Simulador de Quizzes, Asistente de Terminal.
  5. Re-indexación dinámica en 1 clic de apuntes, PDFs y transcripciones.
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
VIDEOS_DIR = os.path.join(STUDENT_DIR, "mis_videos")
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

        # 2. API: Catálogo de Videos de las 12 Clases
        elif path == "/api/videos":
            self.handle_api_videos()
            return

        # 3. API: Búsqueda RAG en SQLite FTS5
        elif path == "/api/search":
            q = query.get("q", [""])[0]
            c_filter = query.get("clase", [None])[0]
            self.handle_api_search(q, c_filter)
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

        # Redirigir raíz al portal del estudiante
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

            c.execute("SELECT clase_num, COUNT(*) FROM course_docs WHERE clase_num IS NOT NULL GROUP BY clase_num;")
            classes = dict(c.fetchall())

            conn.close()
            self.send_json({
                "ok": True,
                "total_docs": total,
                "categories": cats,
                "classes": classes,
                "db_path": DB_PATH
            })
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)})

    def handle_api_videos(self):
        json_file = os.path.join(VIDEOS_DIR, "clases.json")
        clases_list = []
        if os.path.exists(json_file):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    clases_list = json.load(f)
            except Exception:
                pass

        # Validar qué archivos locales existen en disco
        for item in clases_list:
            loc = item.get("archivo_local", "")
            full_p = os.path.join(VIDEOS_DIR, loc)
            item["existe_local"] = os.path.exists(full_p) and os.path.getsize(full_p) > 1000
            if item["existe_local"]:
                item["stream_endpoint"] = f"/videos/{urllib.parse.quote(loc)}"
            elif item.get("url_stream"):
                item["stream_endpoint"] = item["url_stream"]
            else:
                item["stream_endpoint"] = None

        self.send_json({"ok": True, "clases": clases_list})

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
            # Manejo de Range Requests (HTTP 206 Partial Content) para scrub/seek fluido
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

    def handle_api_search(self, query_str, clase_filter=None):
        if not os.path.exists(DB_PATH) or not query_str.strip():
            self.send_json({"ok": True, "results": []})
            return

        results = search_in_db(query_str, clase_filter=clase_filter, limit=10)
        self.send_json({"ok": True, "query": query_str, "results": results})

    def handle_api_ask(self, body):
        question = body.get("question", "").strip()
        mode = body.get("mode", "tutor")  # tutor | quiz_practice | lab_assistant | video_review
        clase_num = body.get("clase")

        if not question:
            self.send_json({"ok": False, "error": "Pregunta vacía."})
            return

        # 1. Recuperación RAG de fragmentos relevantes
        results = search_in_db(question, clase_filter=clase_num, limit=6)

        # 2. Construcción del Prompt Pedagógico para el Alumno
        system_prompt = build_student_prompt(mode, clase_num)
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

def search_in_db(query_str, clase_filter=None, limit=6):
    if not os.path.exists(DB_PATH):
        return []

    # Limpieza básica de términos para FTS5
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
        if clase_filter:
            sql = """
                SELECT cd.id, cd.title, cd.category, cd.rel_path, cd.clase_num, cd.modulo, cd.content, rank
                FROM course_docs_fts fts
                JOIN course_docs cd ON fts.rowid = cd.id
                WHERE course_docs_fts MATCH ? AND cd.clase_num = ?
                ORDER BY rank
                LIMIT ?;
            """
            c.execute(sql, (fts_match, int(clase_filter), limit))
        else:
            sql = """
                SELECT cd.id, cd.title, cd.category, cd.rel_path, cd.clase_num, cd.modulo, cd.content, rank
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
                "clase_num": row[4],
                "modulo": row[5],
                "content": row[6][:600],
                "score": round(row[7], 3) if row[7] is not None else 0
            })
    except Exception as e:
        print(f" [!] Error en búsqueda FTS5: {e}")
    finally:
        conn.close()

    return results

def build_student_prompt(mode, clase_num):
    clase_context = f" enfocándote especialmente en los temas de la Clase {clase_num}" if clase_num else ""
    
    if mode == "quiz_practice":
        return f"""Eres el Evaluador y Entrenador de Exámenes de Cloud DevOps (EducaciónIT){clase_context}.
Tu objetivo es ayudar al alumno a prepararse para las evaluaciones oficiales.
- Si el alumno solicita una trivia o pregunta, plantéale de 1 a 3 preguntas desafiantes de opción múltiple (A, B, C, D) con contexto práctico real.
- Si el alumno responde una opción, evalúa con rigurosidad técnica: felicítalo si acertó o explica detalladamente por qué la opción correcta es la adecuada y por qué las demás son trampas conceptuales.
- Basa tus preguntas en los apuntes y exámenes indexados."""

    elif mode == "lab_assistant":
        return f"""Eres el Asistente de Laboratorio y Terminal de Cloud DevOps (EducaciónIT){clase_context}.
Tu misión es asistir al alumno en la resolución de errores en consola, sintaxis de Dockerfiles, Terraform HCL, Kubernetes YAML y comandos de Git.
- Da explicaciones paso a paso con los comandos exactos para solucionar el fallo.
- Utiliza la regla 'Show, Don't Tell': muestra la terminal esperada y advierte sobre errores comunes."""

    elif mode == "video_review":
        return f"""Eres el Asistente de Grabaciones y Repaso de Clase de Cloud DevOps (EducaciónIT){clase_context}.
Tu función es resumir lo tratado en las grabaciones de clase, rescatar los consejos del profesor, responder dudas frecuentes de compañeros y señalar los minutos clave para volver a ver."""

    # Default: tutor
    return f"""Eres el Tutor Personal de IA del alumno en el curso Cloud DevOps: Automatización y Despliegue (EducaciónIT){clase_context}.
Tu objetivo es que el alumno comprenda cada concepto técnico con profundidad, entusiasmo y solidez conceptual.
- Explica los temas abstractos utilizando analogías claras de la vida real antes de la sintaxis técnica.
- Proporciona comandos de terminal prácticos con explicaciones de sus flags.
- Apóyate en el contexto de apuntes, transcripciones y materiales adjuntos."""

def build_context_snippet(results):
    if not results:
        return "No se encontraron fragmentos locales directamente relacionados. Utiliza tus conocimientos de ingeniería DevOps general."
    text = "=== FUENTES DE TUS APUNTES Y MATERIALES LOCALES ===\n\n"
    for r in results:
        text += f"--- [{r['category'].upper()}] {r['title']} (Archivo: {r['rel_path']}) ---\n"
        text += f"{r['content']}\n\n"
    return text

def execute_ai_query(system_prompt, question, context_text):
    full_prompt = f"{system_prompt}\n\n{context_text}\n\nPregunta del alumno:\n{question}\n\nRespuesta estructurada para el alumno (usa formato Markdown claro con títulos, viñetas y bloques de código):"

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
    fallback_text = f"### 🎓 Respuesta Basada en tus Apuntes y Materiales Locales:\n\n"
    fallback_text += f"He consultado tu base de datos SQLite y correlacionado los siguientes fragmentos para responder tu consulta sobre **'{question}'**:\n\n"
    
    if "No se encontraron" in context_text:
        fallback_text += "No encontré notas específicas en tus carpetas para este término. Te sugiero anotar lo que vayas aprendiendo en tu archivo de apuntes (`mis_apuntes/`) y volver a consultar.\n\n"
        fallback_text += "> 💡 **Tip:** Puedes configurar una API Key gratuita de Gemini (`set GEMINI_API_KEY=...`) o ejecutar `ollama run qwen2.5` en tu máquina para habilitar razonamiento conversacional autónomo 100% offline."
    else:
        fallback_text += context_text.replace("=== FUENTES DE TUS APUNTES Y MATERIALES LOCALES ===", "").strip()
        fallback_text += "\n\n---\n*Para activar respuestas redactadas con modelos de lenguaje generativo, agrega tu `GEMINI_API_KEY` o inicia Ollama localmente.*"

    return fallback_text, "Motor RAG Offline (SQLite FTS5)"

def main():
    print("\n" + "=" * 80)
    print("   INICIANDO SERVIDOR DEL CAMPUS PERSONAL DEL ALUMNO")
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
