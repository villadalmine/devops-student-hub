@echo off
chcp 65001 >nul
title DevOps Workspace - Student Hub
cd /d "%~dp0"

echo ======================================================================
echo    INICIANDO DEVOPS WORKSPACE & STUDENT HUB
echo ======================================================================
echo.

:: 1. Si existe el ejecutable binario nativo, arrancarlo directamente (no requiere Python)
if exist "student-hub.exe" (
    echo [*] Modo detectado: Standalone Binario (Sin dependencias externas)
    echo [*] Lanzando servidor local en http://localhost:8081 ...
    student-hub.exe 8081
    pause
    exit /b 0
)

:: 2. Si no esta el binario, buscar Python en el sistema
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Modo detectado: Python Runtime del sistema
    echo [*] Lanzando servidor local en http://localhost:8081 ...
    start "" "http://localhost:8081/devops_hub.html"
    python scripts\servidor_asistente.py 8081
    pause
    exit /b 0
)

:: 3. Si no existe ni el exe ni Python
echo [ERROR] No se encontro 'student-hub.exe' ni Python instalado en tu sistema.
echo.
echo Para solucionarlo:
echo   - Descarga 'student-hub.exe' desde los Releases de GitHub.
echo   - O instala Python con: winget install Python.Python.3.12
echo.
pause
exit /b 1
