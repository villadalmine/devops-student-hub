# Script de compilación para Student Hub (Windows)
# Genera student-hub.exe empacando todos los archivos necesarios

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  COMPILANDO STUDENT HUB CON PYINSTALLER"
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si PyInstaller está instalado
Write-Host "[*] Verificando PyInstaller..." -ForegroundColor Yellow
$pyinstaller = python -m pip show pyinstaller 2>$null
if (-not $pyinstaller) {
    Write-Host "[!] PyInstaller no está instalado. Instalando..." -ForegroundColor Yellow
    python -m pip install pyinstaller
}

# Verificar que el spec file existe
if (-not (Test-Path "build_student_hub.spec")) {
    Write-Host "[!] ERROR: build_student_hub.spec no encontrado" -ForegroundColor Red
    exit 1
}

# Limpiar builds anteriores
Write-Host "[*] Limpiando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Compilar con PyInstaller
Write-Host "[*] Compilando binario (esto puede tomar 1-2 minutos)..." -ForegroundColor Yellow
Write-Host ""

pyinstaller build_student_hub.spec --distpath ./dist --workpath ./build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  ✓ COMPILACIÓN EXITOSA"
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Binario generado:" -ForegroundColor Cyan
    Write-Host "  dist/student-hub.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Cyan
    Write-Host "  1. Probá: ./dist/student-hub.exe" -ForegroundColor White
    Write-Host "  2. O copia dist/student-hub.exe al repo raíz para distribuir" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Red
    Write-Host "  ✗ ERROR EN LA COMPILACIÓN"
    Write-Host "======================================================================" -ForegroundColor Red
    exit 1
}
