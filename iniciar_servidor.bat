@echo off
chcp 65001 >nul
title Informe Mensual de Obra - Servidor (red local)
cd /d "%~dp0informe_web"

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

:: Detectar modo de instalacion (administrador / cliente) segun config_red.py
set "MODO_RED=administrador"
set "URL_RED=http://127.0.0.1:5000"
for /f "usebackq tokens=1,2 delims=|" %%A in (`""%PYEXE%" "%~dp0informe_web\red_util.py""`) do (
  set "MODO_RED=%%A"
  set "URL_RED=%%B"
)

if /i "%MODO_RED%"=="cliente" goto :modo_cliente

echo ==================================================
echo  Informe Mensual de Obra - MODO RED LOCAL
echo  Servidor: 0.0.0.0   Puerto: 5000
echo ==================================================
echo.
echo  Recomendado: ejecute una vez "abrir_puerto_firewall.bat"
echo  (como Administrador) para permitir el acceso desde otros
echo  equipos de la misma red.
echo.
echo  IPs de esta maquina para que los clientes accedan:
powershell -NoProfile -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' } | ForEach-Object { '{0,-28} {1}' -f $_.InterfaceAlias, $_.IPAddress }"
echo  (Si usa Tailscale, use la IP 100.x.x.x de la interfaz Tailscale.)
echo.

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
"%PYEXE%" -m waitress --host=0.0.0.0 --port=5000 --threads=8 --connection-limit=128 app:app
pause
exit /b 0

:modo_cliente
echo ==================================================
echo  Informe Mensual de Obra - MODO CLIENTE
echo  Este equipo se conecta al servidor del Administrador.
echo ==================================================
echo.
echo  Abriendo: %URL_RED%
echo  Asegurese de que el Administrador este encendido y de
echo  que ambos equipos esten en la misma red (LAN o Tailscale).
echo.
start "" "%URL_RED%"
pause
exit /b 0