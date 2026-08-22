@echo off
chcp 65001 >nul
title Informe Mensual de Obra - Servidor (red local)
cd /d "%~dp0informe_web"

echo ==================================================
echo  Informe Mensual de Obra - MODO RED LOCAL
echo  Servidor: 0.0.0.0   Puerto: 5000
echo ==================================================
echo.
echo  Recomendado: ejecute una vez "abrir_puerto_firewall.bat"
echo  (como Administrador) para permitir el acceso desde otros
echo  equipos de la misma red.
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

"%PYEXE%" -c "import waitress" >nul 2>&1
if errorlevel 1 (
  echo Instalando waitress...
  "%PYEXE%" -m pip install waitress --quiet --disable-pip-version-check
)

echo.
echo Iniciando servidor... (deje esta ventana abierta)
echo Para detener: presione Ctrl+C
echo.
set "PYTHONPATH=%~dp0informe_web"
"%PYEXE%" -m waitress --host=0.0.0.0 --port=5000 --threads=8 --connection-limit=128 app:app
pause
