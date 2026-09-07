#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
   INDEXADOR RAG LOCAL DEL ESTUDIANTE (CLOUD DEVOPS - EDUCACIONIT)
===============================================================================
Escanea dinámicamente y actualiza la base de datos SQLite FTS5 (data/devops_knowledge.db):
  - 📝 Mis Apuntes de Clase (mis_apuntes/)
  - 📚 Diapositivas, PDFs y Libros (material_clases/)
  - 🎙️ Transcripciones de Grabaciones (transcripciones/)
  - 🧩 Exámenes y Quizzes de Práctica (examenes_y_practicas/)
  - 🛠️ Guías de Instalación y Diagnóstico (01-Guia-*, README.md)
===============================================================================
"""

import os
import sys
import re
import json
import sqlite3

# Configurar salida UTF-8 segura en Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(STUDENT_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "devops_knowledge.db")

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            rel_path TEXT NOT NULL,
            abs_path TEXT NOT NULL,
            clase_num INTEGER,
            modulo TEXT,
            video_url TEXT,
            summary TEXT,
            content TEXT NOT NULL,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    c.execute("DROP TABLE IF EXISTS course_docs_fts;")
    c.execute("""
        CREATE VIRTUAL TABLE course_docs_fts USING fts5(
            title,
            category,
            rel_path,
            modulo,
            tags,
            content,
            content='course_docs',
            content_rowid='id',
            tokenize='porter unicode61'
        );
    """)
    conn.commit()
    return conn

def detect_clase_num(text, filename=""):
    combined = f"{filename} {text[:300]}".lower()
    m = re.search(r'\b(?:clase|c)\s*0?([1-9]|1[0-2])\b', combined)
    if m:
        return int(m.group(1))
    return None

def detect_modulo(clase_num):
    if not clase_num:
        return "General"
    if clase_num in [1, 2]:
        return "M1: Cultura y Fundamentos DevOps"
    elif clase_num in [3, 4]:
        return "M2: Cloud Computing con AWS"
    elif clase_num in [5, 6]:
        return "M3: Infraestructura como Código con Terraform"
    elif clase_num in [7, 8]:
        return "M4: Contenedores con Docker"
    elif clase_num in [9, 10]:
        return "M5: Orquestación con Kubernetes"
    elif clase_num == 11:
        return "M6: CI/CD y GitOps"
    elif clase_num == 12:
        return "M7: Servicios Cloud Containers y Cierre"
    return "General"

def chunk_markdown(content, default_clase_num=None, chunk_size=500):
    lines = content.split('\n')
    chunks = []
    current_chunk = []
    current_title = "General"
    current_clase = default_clase_num
    current_words = 0
    
    for line in lines:
        if line.startswith('#'):
            clean_h = line.lstrip('#').strip()
            if current_words >= 150 and line.startswith(('## ', '# ')):
                chunk_text = "\n".join(current_chunk).strip()
                if chunk_text:
                    detected_c = detect_clase_num(chunk_text) or current_clase or default_clase_num
                    chunks.append((current_title, chunk_text, detected_c))
                current_chunk = []
                current_words = 0
            current_title = clean_h
        
        current_chunk.append(line)
        current_words += len(line.split())
        
        if current_words >= chunk_size:
            chunk_text = "\n".join(current_chunk).strip()
            if chunk_text:
                detected_c = detect_clase_num(chunk_text) or current_clase or default_clase_num
                chunks.append((current_title, chunk_text, detected_c))
            current_chunk = []
            current_words = 0
            
    if current_chunk:
        chunk_text = "\n".join(current_chunk).strip()
        if chunk_text:
            detected_c = detect_clase_num(chunk_text) or current_clase or default_clase_num
            chunks.append((current_title, chunk_text, detected_c))
            
    return chunks

def extract_pdf_chunks(pdf_path, chunk_pages=3):
    if not HAS_PYPDF:
        return []
    chunks = []
    try:
        reader = pypdf.PdfReader(pdf_path)
        total = len(reader.pages)
        accum_text = ""
        start_p = 1
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            accum_text += f"\n--- [Página {i+1}] ---\n" + text
            
            if (i + 1) % chunk_pages == 0 or (i + 1) == total:
                if len(accum_text.strip()) > 80:
                    c_num = detect_clase_num(accum_text, os.path.basename(pdf_path))
                    title = f"Páginas {start_p}-{i+1}"
                    chunks.append((title, accum_text.strip(), c_num))
                accum_text = ""
                start_p = i + 2
    except Exception as e:
        print(f" [!] Error leyendo PDF {pdf_path}: {e}")
    return chunks

def build_student_index():
    print("\n" + "=" * 80)
    print("   INDEXANDO BASE DE CONOCIMIENTO PERSONAL DEL ALUMNO (SQLITE FTS5)")
    print("=" * 80)
    print(f" [+] Destino: {DB_PATH}\n")
    
    conn = init_db(DB_PATH)
    cursor = conn.cursor()
    
    total_docs = 0
    categories = {}
    
    def insert_chunk(title, category, rel_path, abs_path, clase_num, modulo, content, tags=""):
        nonlocal total_docs
        summary = content[:200].replace('\n', ' ').strip() + "..."
        cursor.execute("""
            INSERT INTO course_docs (title, category, rel_path, abs_path, clase_num, modulo, video_url, summary, content, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, category, rel_path, abs_path, clase_num, modulo, "", summary, content, tags))
        
        doc_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO course_docs_fts (rowid, title, category, rel_path, modulo, tags, content)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, title, category, rel_path, modulo, tags, content))
        
        total_docs += 1
        categories[category] = categories.get(category, 0) + 1

    # 1. Indexar Mis Apuntes (mis_apuntes/)
    apuntes_dir = os.path.join(STUDENT_DIR, "mis_apuntes")
    if os.path.isdir(apuntes_dir):
        for f in sorted(os.listdir(apuntes_dir)):
            if f.endswith('.md'):
                abs_p = os.path.join(apuntes_dir, f)
                rel_p = f"mis_apuntes/{f}"
                try:
                    with open(abs_p, 'r', encoding='utf-8') as fh:
                        text = fh.read()
                    c_num = detect_clase_num(text, f)
                    chunks = chunk_markdown(text, default_clase_num=c_num)
                    for t, c_text, c_n in chunks:
                        insert_chunk(
                            title=f"Apuntes Clase {c_n or '?'}: {t}",
                            category="apuntes_alumno",
                            rel_path=rel_p,
                            abs_path=abs_p,
                            clase_num=c_n,
                            modulo=detect_modulo(c_n),
                            content=c_text,
                            tags="apuntes notas estudiante calms dora git aws docker terraform k8s"
                        )
                    print(f" [OK] Indexados apuntes: {f} ({len(chunks)} fragmentos)")
                except Exception as e:
                    print(f" [!] Error en {f}: {e}")

    # 2. Indexar Material de Clases (material_clases/)
    mat_dir = os.path.join(STUDENT_DIR, "material_clases")
    if os.path.isdir(mat_dir):
        for root, _, files in os.walk(mat_dir):
            for f in files:
                abs_p = os.path.join(root, f)
                rel_p = os.path.relpath(abs_p, STUDENT_DIR).replace('\\', '/')
                if f.endswith('.md') or f.endswith('.txt'):
                    try:
                        with open(abs_p, 'r', encoding='utf-8', errors='ignore') as fh:
                            text = fh.read()
                        c_num = detect_clase_num(text, f)
                        chunks = chunk_markdown(text, default_clase_num=c_num)
                        for t, c_text, c_n in chunks:
                            insert_chunk(
                                title=f"Material: {f} - {t}",
                                category="material_clase",
                                rel_path=rel_p,
                                abs_path=abs_p,
                                clase_num=c_n,
                                modulo=detect_modulo(c_n),
                                content=c_text,
                                tags="diapositivas pdf lectura material"
                            )
                        print(f" [OK] Indexado material: {rel_p} ({len(chunks)} fragmentos)")
                    except Exception as e:
                        print(f" [!] Error en {f}: {e}")
                elif f.endswith('.pdf'):
                    pdf_chunks = extract_pdf_chunks(abs_p)
                    for t, c_text, c_n in pdf_chunks:
                        insert_chunk(
                            title=f"PDF: {f} ({t})",
                            category="material_clase",
                            rel_path=rel_p,
                            abs_path=abs_p,
                            clase_num=c_n,
                            modulo=detect_modulo(c_n),
                            content=c_text,
                            tags="pdf libro oficial teoria"
                        )
                    if pdf_chunks:
                        print(f" [OK] Indexado PDF: {f} ({len(pdf_chunks)} fragmentos)")

    # 3. Indexar Transcripciones (transcripciones/)
    trans_dir = os.path.join(STUDENT_DIR, "transcripciones")
    if os.path.isdir(trans_dir):
        for f in sorted(os.listdir(trans_dir)):
            if f.endswith('.md') or f.endswith('.txt'):
                abs_p = os.path.join(trans_dir, f)
                rel_p = f"transcripciones/{f}"
                try:
                    with open(abs_p, 'r', encoding='utf-8', errors='ignore') as fh:
                        text = fh.read()
                    c_num = detect_clase_num(text, f)
                    chunks = chunk_markdown(text, default_clase_num=c_num)
                    for t, c_text, c_n in chunks:
                        insert_chunk(
                            title=f"Transcripción Grabación: {f} ({t})",
                            category="transcripcion",
                            rel_path=rel_p,
                            abs_path=abs_p,
                            clase_num=c_n,
                            modulo=detect_modulo(c_n),
                            content=c_text,
                            tags="transcripcion video audio grabacion profesor clase"
                        )
                    print(f" [OK] Indexada transcripción: {f} ({len(chunks)} fragmentos)")
                except Exception as e:
                    print(f" [!] Error en {f}: {e}")

    # 4. Indexar Exámenes y Prácticas (examenes_y_practicas/)
    exam_dir = os.path.join(STUDENT_DIR, "examenes_y_practicas")
    if os.path.isdir(exam_dir):
        for f in os.listdir(exam_dir):
            abs_p = os.path.join(exam_dir, f)
            rel_p = f"examenes_y_practicas/{f}"
            if f.endswith('.json'):
                try:
                    with open(abs_p, 'r', encoding='utf-8') as jf:
                        data = json.load(jf)
                    if isinstance(data, list):
                        for item in data:
                            c_num = item.get("clase", 1)
                            preg = item.get("pregunta", "")
                            opc = "\n".join(item.get("opciones", []))
                            corr = item.get("correcta", "")
                            just = item.get("justificacion", "")
                            c_text = f"PREGUNTA EXAMEN (Clase {c_num}):\n{preg}\n\nOPCIONES:\n{opc}\n\nRESPUESTA CORRECTA: {corr}\n\nJUSTIFICACION:\n{just}"
                            insert_chunk(
                                title=f"Quiz Clase {c_num}: {preg[:50]}...",
                                category="examen_practica",
                                rel_path=rel_p,
                                abs_path=abs_p,
                                clase_num=c_num,
                                modulo=detect_modulo(c_num),
                                content=c_text,
                                tags="examen quiz practica multiple choice evaluacion"
                            )
                        print(f" [OK] Indexado JSON de exámenes: {f} ({len(data)} preguntas)")
                except Exception as e:
                    print(f" [!] Error en JSON {f}: {e}")
            elif f.endswith('.md'):
                try:
                    with open(abs_p, 'r', encoding='utf-8') as fh:
                        text = fh.read()
                    c_num = detect_clase_num(text, f)
                    chunks = chunk_markdown(text, default_clase_num=c_num)
                    for t, c_text, c_n in chunks:
                        insert_chunk(
                            title=f"Práctica / Examen: {t}",
                            category="examen_practica",
                            rel_path=rel_p,
                            abs_path=abs_p,
                            clase_num=c_n,
                            modulo=detect_modulo(c_n),
                            content=c_text,
                            tags="laboratorio desafio evaluacion"
                        )
                    print(f" [OK] Indexada guía de examen: {f} ({len(chunks)} fragmentos)")
                except Exception as e:
                    print(f" [!] Error en {f}: {e}")

    # 5. Indexar Guías Base y README
    guias = ["01-Guia-Completa-Instalacion-Windows.md", "01-Instalacion-Software-y-Diagnostico.md", "README.md"]
    for g in guias:
        abs_p = os.path.join(STUDENT_DIR, g)
        if os.path.exists(abs_p):
            try:
                with open(abs_p, 'r', encoding='utf-8') as fh:
                    text = fh.read()
                chunks = chunk_markdown(text)
                for t, c_text, _ in chunks:
                    insert_chunk(
                        title=f"Guía: {g} ({t})",
                        category="guia_entorno",
                        rel_path=g,
                        abs_path=abs_p,
                        clase_num=None,
                        modulo="General",
                        content=c_text,
                        tags="instalacion herramientas requisitos entorno windows powershell winget"
                    )
                print(f" [OK] Indexada guía del curso: {g} ({len(chunks)} fragmentos)")
            except Exception as e:
                print(f" [!] Error en {g}: {e}")

    conn.commit()
    conn.close()
    
    print("\n" + "=" * 80)
    print(f"🎉 INDEXACION COMPLETADA CON EXITO: {total_docs} FRAGMENTOS EN TOTAL")
    print("=" * 80)
    for cat, cnt in categories.items():
        print(f"   • {cat.ljust(22)} : {cnt} fragmentos")
    print("=" * 80 + "\n")
    return total_docs

if __name__ == "__main__":
    build_student_index()
