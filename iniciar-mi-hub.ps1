<#
.SYNOPSIS
    Inicia el Servidor Web Local y el Hub DevOps del Alumno en el puerto 8081.
#>
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$port = 8081
$url = "http://localhost:$port/devops_hub.html"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   INICIANDO DEVOPS WORKSPACE & STUDENT HUB (PUERTO $port)" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$pythonCmd = (Get-Command "python" -ErrorAction SilentlyContinue)
if (-not $pythonCmd) {
    $pythonCmd = (Get-Command "python3" -ErrorAction SilentlyContinue)
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] No se encontro Python en tu sistema." -ForegroundColor Red
    Write-Host "Instala Python ejecutando: powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1 -SoloBase" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host " [*] Abriendo navegador en $url ..." -ForegroundColor Green
Start-Process $url

Write-Host " [*] Servidor activo en puerto $port. Presiona Ctrl+C para detener." -ForegroundColor Cyan
& $pythonCmd.Source ".\scripts\servidor_asistente.py" $port
