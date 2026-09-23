# Instalador de Sword para Windows (PowerShell)
# Uso:  botón derecho > Ejecutar con PowerShell
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  =============================================="
Write-Host "   Sword - Limpia y une Excel en segundos"
Write-Host "   Instalador para Windows (PowerShell)"
Write-Host "  =============================================="
Write-Host ""

# 1. Python presente?
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "  [ERROR] No se encontro Python instalado." -ForegroundColor Red
    Write-Host "  Descargalo de  https://www.python.org/downloads/  "
    Write-Host "  y marca la casilla  'Add Python to PATH'  durante la instalacion."
    Read-Host "  Presiona Enter para salir"
    exit 1
}

Write-Host "  [1/4] Creando entorno virtual..."
python -m venv .venv

Write-Host "  [2/4] Actualizando pip..."
& .venv\Scripts\python.exe -m pip install --upgrade pip | Out-Null

Write-Host "  [3/4] Instalando dependencias (primera vez puede tardar)..."
& .venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Fallo la instalacion de dependencias." -ForegroundColor Red
    Read-Host "  Presiona Enter para salir"
    exit 1
}

Write-Host "  [4/4] Instalando Sword..."
& .venv\Scripts\python.exe -m pip install -e . | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Fallo la instalacion de Sword." -ForegroundColor Red
    Read-Host "  Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "  Listo! Sword quedo instalado." -ForegroundColor Green
Write-Host ""
Write-Host "  Uso:  sword C:\ruta\a\mis_excels"
Write-Host "  (o doble clic sobre sword.bat en esta carpeta)"
Write-Host ""
Read-Host "  Presiona Enter para salir"