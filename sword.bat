@echo off
chcp 65001 >nul
title Sword
setlocal EnableExtensions

rem --- Lanzador de Sword en Windows (no requiere tocar consola) ----------
set "VENV=.venv\Scripts\python.exe"

rem Si ya existe el entorno instalado, lo usamos; si no, usamos python tal cual.
if exist "%VENV%" (
    "%VENV%" -m sword %*
) else (
    python -m sword %*
)
if %errorlevel% neq 0 (
    echo.
    echo  Si este es tu primer uso, ejecuta primero:  instalar_windows.bat
    pause
)