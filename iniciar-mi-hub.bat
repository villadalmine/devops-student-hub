@echo off
chcp 65001 >nul
title Cloud DevOps - Campus Personal del Alumno
cd /d "%~dp0"

echo ======================================================================
echo    INICIANDO CAMPUS PERSONAL DEL ALUMNO (CLOUD DEVOPS 2026)
echo ======================================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en tu sistema.
    echo Por favor instala Python o ejecuta:
    echo powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1 -SoloObligatorio
    pause
    exit /b 1
)

echo [*] Verificando base de datos de conocimiento SQLite...
if not exist "data\devops_knowledge.db" (
    echo [*] Primera ejecucion detectada: construyendo indice RAG local...
    python scripts\crear_indice_rag.py
)

echo [*] Lanzando servidor local en http://localhost:8080 ...
start "" "http://localhost:8080/course_hub.html"
python scripts\servidor_asistente.py
pause
