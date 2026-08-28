@echo off
chcp 65001 >nul
title Informe Mensual de Obra - Modo local
cd /d "%~dp0informe_web"

echo ==================================================
echo  Informe Mensual de Obra - SOLO ESTA MAQUINA
echo  Abrir en el navegador: http://127.0.0.1:5000
echo  (Otros equipos NO podran acceder en este modo)
echo ==================================================
echo.

:: Detectar Python: primero embebido, luego PATH del sistema
set "PYEXE=%~dp0python\python.exe"
if not exist "%PYEXE%" (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] No se encontro Python ni en la carpeta python\ ni en el PATH.
    pause
    exit /b 1
  )
  set "PYEXE=python"
)

:: Verificar/instalar dependencias de la app (Flask, openpyxl, Pillow, waitress)
"%PYEXE%" -c "import flask, flask_sqlalchemy, openpyxl, PIL, waitress" >nul 2>&1
if errorlevel 1 (
  echo Instalando dependencias faltantes...
  "%PYEXE%" -m pip install -r requirements.txt --quiet --disable-pip-version-check
)

echo.
echo Iniciando servidor... (deje esta ventana abierta)
echo Para detener: presione Ctrl+C
echo.
set "PYTHONPATH=%~dp0informe_web"
"%PYEXE%" -m waitress --host=127.0.0.1 --port=5000 --threads=8 --connection-limit=128 app:app
pause
