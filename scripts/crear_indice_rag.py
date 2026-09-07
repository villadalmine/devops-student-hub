#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
   INDEXADOR RAG UNIVERSAL & BASE DE CONOCIMIENTO (CLOUD DEVOPS)
===============================================================================
Escanea de forma recursiva CUALQUIER directorio del espacio de trabajo
(apuntes/, material/, videos/, practicas/, o carpetas personalizadas) e indexa
todos los archivos Markdown (.md), texto (.txt) y documentos PDF (.pdf)
en una base de datos SQLite FTS5 (data/devops_knowledge.db).
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
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "devops_knowledge.db")

# Carpetas o archivos que no deben indexarse
EXCLUDE_DIRS = {".git", ".agent", "skills", "scripts", "data", "player", "herdr", "nvim", "__pycache__", "node_modules", ".vscode"}
EXCLUDE_FILES = {"videos.json", "package.json", "package-lock.json"}

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("DROP TABLE IF EXISTS course_docs;")
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            rel_path TEXT NOT NULL,
            abs_path TEXT NOT NULL,
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
            tags,
            content,
            content='course_docs',
            content_rowid='id',
            tokenize='porter unicode61'
        );
    """)
    conn.commit()
    return conn

def chunk_markdown(content, chunk_size=500):
    lines = content.split('\n')
    chunks = []
    current_chunk = []
    current_title = "Documento"
    current_words = 0
    
    for line in lines:
        if line.startswith('#'):
            clean_h = line.lstrip('#').strip()
            if current_words >= 150 and line.startswith(('## ', '# ')):
                chunk_text = "\n".join(current_chunk).strip()
                if chunk_text:
                    chunks.append((current_title, chunk_text))
                current_chunk = []
                current_words = 0
            current_title = clean_h
        
        current_chunk.append(line)
        current_words += len(line.split())
        
        if current_words >= chunk_size:
            chunk_text = "\n".join(current_chunk).strip()
            if chunk_text:
                chunks.append((current_title, chunk_text))
            current_chunk = []
            current_words = 0
            
    if current_chunk:
        chunk_text = "\n".join(current_chunk).strip()
        if chunk_text:
            chunks.append((current_title, chunk_text))
            
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
                if len(accum_text.strip()) > 60:
                    title = f"Páginas {start_p}-{i+1}"
                    chunks.append((title, accum_text.strip()))
                accum_text = ""
                start_p = i + 2
    except Exception as e:
        print(f" [!] Error leyendo PDF {pdf_path}: {e}")
    return chunks

def build_universal_index():
    print("\n" + "=" * 80)
    print("   INDEXANDO BASE DE CONOCIMIENTO DEVOPS UNIVERSAL (SQLITE FTS5)")
    print("================================================================================")
    print(f" [+] Directorio Raíz : {WORKSPACE_DIR}")
    print(f" [+] Base de Datos   : {DB_PATH}\n")
    
    conn = init_db(DB_PATH)
    cursor = conn.cursor()
    
    total_docs = 0
    categories = {}
    
    def insert_chunk(title, category, rel_path, abs_path, content, tags=""):
        nonlocal total_docs
        summary = content[:200].replace('\n', ' ').strip() + "..."
        cursor.execute("""
            INSERT INTO course_docs (title, category, rel_path, abs_path, summary, content, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, category, rel_path, abs_path, summary, content, tags))
        
        doc_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO course_docs_fts (rowid, title, category, rel_path, tags, content)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, title, category, rel_path, tags, content))
        
        total_docs += 1
        categories[category] = categories.get(category, 0) + 1

    # Escaneo recursivo libre de todos los directorios
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        # Filtrar directorios excluidos en tiempo real
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for file in sorted(files):
            if file in EXCLUDE_FILES or file.startswith('.'):
                continue

            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, WORKSPACE_DIR).replace('\\', '/')
            
            # Determinar categoría a partir del directorio contenedor
            parts = rel_path.split('/')
            if len(parts) > 1:
                category = parts[0]
            else:
                category = "general"

            # 1. Archivos Markdown y Texto
            if file.endswith(('.md', '.txt')):
                try:
                    with open(abs_path, 'r', encoding='utf-8', errors='ignore') as fh:
                        text = fh.read()
                    chunks = chunk_markdown(text)
                    for t, c_text in chunks:
                        insert_chunk(
                            title=f"{file} ({t})",
                            category=category,
                            rel_path=rel_path,
                            abs_path=abs_path,
                            content=c_text,
                            tags=f"{category} devops documentacion notas"
                        )
                    print(f" [OK] Indexado: {rel_path} ({len(chunks)} fragmentos)")
                except Exception as e:
                    print(f" [!] Error indexando {rel_path}: {e}")

            # 2. Archivos PDF
            elif file.endswith('.pdf'):
                pdf_chunks = extract_pdf_chunks(abs_path)
                for t, c_text in pdf_chunks:
                    insert_chunk(
                        title=f"{file} ({t})",
                        category=category,
                        rel_path=rel_path,
                        abs_path=abs_path,
                        content=c_text,
                        tags=f"{category} pdf libro manual oficial"
                    )
                if pdf_chunks:
                    print(f" [OK] Indexado PDF: {rel_path} ({len(pdf_chunks)} fragmentos)")

            # 3. Archivos JSON con preguntas o definiciones
            elif file.endswith('.json') and "quiz" in file.lower():
                try:
                    with open(abs_path, 'r', encoding='utf-8') as jf:
                        data = json.load(jf)
                    if isinstance(data, list):
                        for item in data:
                            preg = item.get("pregunta", "")
                            opc = "\n".join(item.get("opciones", []))
                            corr = item.get("correcta", "")
                            just = item.get("justificacion", "")
                            c_text = f"PREGUNTA:\n{preg}\n\nOPCIONES:\n{opc}\n\nRESPUESTA:\n{corr}\n\nJUSTIFICACION:\n{just}"
                            insert_chunk(
                                title=f"Quiz: {preg[:45]}...",
                                category=category,
                                rel_path=rel_path,
                                abs_path=abs_path,
                                content=c_text,
                                tags="quiz examen practica evaluacion"
                            )
                        print(f" [OK] Indexado JSON: {rel_path} ({len(data)} items)")
                except Exception as e:
                    print(f" [!] Error en {rel_path}: {e}")

    conn.commit()
    conn.close()
    
    print("\n" + "=" * 80)
    print(f"🎉 INDEXACION EXITOSA: {total_docs} FRAGMENTOS PROCESADOS")
    print("================================================================================")
    for cat, cnt in sorted(categories.items()):
        print(f"   • Categoría '{cat.ljust(18)}' : {cnt} fragmentos")
    print("=" * 80 + "\n")
    return total_docs

if __name__ == "__main__":
    build_universal_index()
