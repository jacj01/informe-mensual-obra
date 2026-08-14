@echo off
chcp 65001 >nul
net session >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Ejecute este archivo COMO ADMINISTRADOR
  echo         (clic derecho - "Ejecutar como administrador").
  pause
  exit /b 1
)
echo Abriendo el puerto 5000 en el Firewall de Windows...
netsh advfirewall firewall delete rule name="Informe Mensual de Obra (5000)" >nul 2>&1
netsh advfirewall firewall add rule name="Informe Mensual de Obra (5000)" dir=in action=allow protocol=TCP localport=5000 profile=any
if errorlevel 1 (
  echo [ERROR] No se pudo crear la regla del firewall.
) else (
  echo [OK] Regla creada. Otros equipos de la red ya pueden conectarse.
)
pause
