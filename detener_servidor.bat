@echo off
setlocal enabledelayedexpansion

:: Detener servidor por PID si existe
if exist "%~dp0informe_web\servidor.pid" (
    set /p PID=<"%~dp0informe_web\servidor.pid"
    if not "!PID!"=="" (
        taskkill /PID !PID! /F >nul 2>&1
    )
    del "%~dp0informe_web\servidor.pid" >nul 2>&1
)

:: Forzar cierre de pythonw.exe y python.exe
taskkill /IM pythonw.exe /F >nul 2>&1
taskkill /IM python.exe /F >nul 2>&1

:: Esperar a que liberen archivos
ping -n 3 127.0.0.1 >nul 2>&1

exit /b 0
