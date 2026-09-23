@echo off
chcp 65001 >nul
title Sword - Instalador para Windows
color 0A

echo.
echo  ==============================================
echo   Sword - Limpia y une Excel en segundos
echo   Instalador para Windows
echo  ==============================================
echo.

rem --- 1. Verificar Python -----------------------------------------------
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo  [ERROR] No se encontro Python instalado.
    echo.
    echo  Para instalar Sword necesitas Python, y es muy facil:
    echo   1. Entra a  https://www.python.org/downloads/
    echo   2. Descarga la ultima version y ejecuta el instalador
    echo   3. IMPORTANTE: marca la casilla  "Add Python to PATH"
    echo   4. Cierra esta ventana y vuelve a ejecutar este archivo
    echo.
    pause
    exit /b 1
)

echo  [1/3] Creando entorno virtual...
python -m venv .venv
if %errorlevel% neq 0 (
    echo  [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

echo  [2/3] Instalando dependencias (tarda un poco en la primera vez)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>nul
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo  [ERROR] Fallo la instalacion de dependencias.
    echo  Revisa tu conexion a internet y vuelve a intentarlo.
    pause
    exit /b 1
)

echo  [3/3] Instalando Sword...
pip install -e . >nul
if %errorlevel% neq 0 (
    echo  [ERROR] Fallo la instalacion final.
    pause
    exit /b 1
)

echo.
echo  ==============================================
echo   Listo! Sword quedo instalado correctamente.
echo  ==============================================
echo.
echo   Para usarlo:
echo     1. Pon tus archivos Excel en una carpeta
echo        (ej: C:\Users\TuNombre\Escritorio\mis_excels)
echo     2. Abre una terminal en esta carpeta y ejecuta:
echo.
echo        sword C:\ruta\a\mis_excels
echo.
echo   O mas facil: doble clic en sword.bat de esta carpeta
echo   (te pedira la carpeta con los Excel).
echo.
pause