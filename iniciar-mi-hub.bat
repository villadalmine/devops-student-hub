@echo off
chcp 65001 >nul
title DevOps Workspace - Knowledge Hub
cd /d "%~dp0"

echo ======================================================================
echo    INICIANDO DEVOPS WORKSPACE ^& KNOWLEDGE HUB
echo ======================================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en tu sistema.
    echo Por favor instala Python o ejecuta:
    echo powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1 -SoloBase
    pause
    exit /b 1
)

echo [*] Lanzando servidor local en http://localhost:8080 ...
start "" "http://localhost:8080/devops_hub.html"
python scripts\servidor_asistente.py
pause
