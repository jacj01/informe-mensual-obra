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

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] No se encontro Python en el PATH.
  pause
  exit /b 1
)

python -c "import waitress" >nul 2>&1
if errorlevel 1 (
  echo Instalando waitress...
  python -m pip install waitress --quiet --disable-pip-version-check
)

echo.
echo Iniciando servidor... (deje esta ventana abierta)
echo Para detener: presione Ctrl+C
echo.
python -m waitress --host=0.0.0.0 --port=5000 --threads=8 --connection-limit=128 app:app
pause
