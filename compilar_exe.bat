@echo off
chcp 65001 >nul
title Sword - Comprimir en Sword.exe
color 0B

echo.
echo  ==============================================
echo   Sword - Compilador de ejecutable (.exe)
echo   Genera un Sword.exe que NO necesita Python
echo ==============================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo  [ERROR] No se encontro Python. Ejecuta primero instalar_windows.bat
    pause
    exit /b 1
)

if not exist ".venv\Scripts\activate.bat" (
    echo  [ERROR] Parece que Sword no esta instalado.
    echo  Ejecuta primero  instalar_windows.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo  [1/2] Instalando PyInstaller...
pip install pyinstaller >nul
if %errorlevel% neq 0 (
    echo  [ERROR] No se pudo instalar PyInstaller.
    pause
    exit /b 1
)

echo  [2/2] Compilando Sword.exe (puede tardar 1-2 minutos)...
pyinstaller --onefile --name Sword --console sword\cli.py
if %errorlevel% neq 0 (
    echo  [ERROR] Fallo la compilacion.
    pause
    exit /b 1
)

echo.
echo  ==============================================
echo   Listo! Tu ejecutable esta en:
echo     dist\Sword.exe
echo ==============================================
echo.
echo   Ese archivo lo puedes copiar a CUALQUIER PC con
echo   Windows, incluso sin Python instalado.
echo   Para usarlo:  Sword.exe C:\ruta\a\mis_excels
echo.
pause