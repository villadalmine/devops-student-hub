#!/usr/bin/env bash
# ==============================================================================
#    INICIANDO DEVOPS WORKSPACE & KNOWLEDGE HUB (LINUX / MACOS)
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PORT=8081
URL="http://localhost:${PORT}/devops_hub.html"

echo "======================================================================"
echo "   INICIANDO DEVOPS WORKSPACE & KNOWLEDGE HUB (PUERTO ${PORT})"
echo "======================================================================"
echo ""

if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] No se encontró Python en tu sistema."
    echo "Por favor instala Python 3 o ejecuta ./scripts/instalar-tools-linux.sh --base"
    exit 1
fi

echo "[*] Lanzando servidor local en $URL ..."

# Abrir navegador si está disponible
if command -v xdg-open &>/dev/null; then
    xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open &>/dev/null; then
    open "$URL" >/dev/null 2>&1 &
fi

$PY_CMD scripts/servidor_asistente.py $PORT
