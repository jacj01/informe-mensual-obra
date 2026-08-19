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
python -c "import waitress" >nul 2>&1
if errorlevel 1 (
  echo Instalando waitress...
  python -m pip install waitress --quiet --disable-pip-version-check
)

echo.
echo Iniciando servidor... (deje esta ventana abierta)
echo Para detener: presione Ctrl+C
echo.
python -m waitress --host=127.0.0.1 --port=5000 --threads=8 --connection-limit=128 app:app
pause
