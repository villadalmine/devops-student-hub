@echo off
chcp 65001 >nul
title Actualizador de Base de Conocimiento RAG
cd /d "%~dp0"

echo ======================================================================
echo    ACTUALIZANDO BASE DE CONOCIMIENTO (SQLITE FTS5)
echo ======================================================================
echo.
python scripts\crear_indice_rag.py
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
