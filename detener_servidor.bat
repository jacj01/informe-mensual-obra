@echo off
chcp 65001 >nul
title Detener servidor Informe Mensual de Obra
cd /d "%~dp0informe_web"

if not exist servidor.pid (
  echo [AVISO] No se encontro servidor.pid. No hay un servidor oculto en ejecucion.
  echo          Si el servidor sigue respondiendo, use el Administrador de tareas
  echo          para finalizar el proceso pythonw.exe relacionado.
  pause
  exit /b 1
)

set /p PID=<servidor.pid
echo Deteniendo servidor (PID %PID%)...
taskkill /PID %PID% /F >nul 2>&1
if errorlevel 1 (
  echo [ERROR] No se pudo detener el proceso. Verifiquelo en el Administrador de tareas.
  pause
  exit /b 1
)
del servidor.pid >nul 2>&1
echo [OK] Servidor detenido.
pause
