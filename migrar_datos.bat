@echo off
setlocal enabledelayedexpansion
title Migrar datos de Informe de Obra (Program Files -> AppData)

rem ============================================================
rem Migra los datos de una instalacion anterior instalada en
rem C:\Program Files\InformeObra (u otra ruta) a la instalacion
rem nueva por-usuario en %LocalAppData%\Programs\InformeObra.
rem
rem Copia: instance\ (base de datos + tenants), Respaldo BD\ y
rem static\uploads\ (archivos subidos). NO toca los datos de
rem origen (los deja intactos como respaldo).
rem ============================================================

set "ORIGEN_PROG=C:\Program Files\InformeObra\informe_web"
set "ORIGEN_PF86=C:\Program Files (x86)\InformeObra\informe_web"
set "DESTINO=%LocalAppData%\Programs\InformeObra\informe_web"

if not exist "%DESTINO%" (
  echo [ERROR] No se encontro la instalacion nueva en:
  echo         %DESTINO%
  echo.
  echo Instala primero el nuevo InformeObra-Setup-1.1.8.exe antes de migrar.
  echo.
  pause
  exit /b 1
)

rem --- Detectar origen ---
set "ORIGEN="
if exist "%ORIGEN_PROG%" set "ORIGEN=%ORIGEN_PROG%"
if "!ORIGEN!"=="" if exist "%ORIGEN_PF86%" set "ORIGEN=%ORIGEN_PF86%"

if "!ORIGEN!"=="" (
  echo [INFO] No se encontro ninguna instalacion anterior en Program Files.
  echo        Si ya tienes los datos en otro sitio, cancela y copia manualmente.
  echo.
  set /p ORIGEN="Escribe la ruta completa de la carpeta informe_web anterior (o Enter para salir): "
  if "!ORIGEN!"=="" exit /b 0
  if not exist "!ORIGEN!\instance" (
    echo [ERROR] No se encontro 'instance' en la ruta indicada.
    pause
    exit /b 1
  )
)

echo.
echo Origen : !ORIGEN!
echo Destino: %DESTINO%
echo.
echo Se migraran las siguientes carpetas (si existen):
echo   - instance        (base de datos principal y por-usuario)
echo   - Respaldo BD     (respaldos automaticos)
echo   - static\uploads  (archivos subidos)
echo.
choice /M "Quieres continuar con la migracion"
if errorlevel 2 exit /b 0

rem --- Detener el servidor si esta corriendo ---
echo.
echo Deteniendo el servidor si esta en ejecucion...
taskkill /IM pythonw.exe /F 2>nul
taskkill /IM python.exe /F 2>nul
if exist "%DESTINO%\servidor.pid" del "%DESTINO%\servidor.pid" /q
timeout /t 2 /nobreak >nul

rem --- Copiar instance (solo si el destino no tiene datos o siempre con respaldo) ---
set "COPIADO0="
if exist "!ORIGEN!\instance" (
  echo.
  echo [1/3] Copiando instance...
  if exist "%DESTINO%\instance" (
    echo   El destino ya tiene 'instance'. Haciendo respaldo del destino antes de continuar...
    robocopy "%DESTINO%\instance" "%DESTINO%\instance_backup" /E /R:1 /W:1 /NFL /NDL /NJH /NJS >nul
  )
  robocopy "!ORIGEN!\instance" "%DESTINO%\instance" /E /R:1 /W:1 /NFL /NDL /NJH /NJS
  set COPIADO0=1
) else (
  echo [1/3] instance no existia en el origen, se omite.
)

rem --- Copiar Respaldo BD ---
if exist "!ORIGEN!\Respaldo BD" (
  echo.
  echo [2/3] Copiando Respaldo BD...
  robocopy "!ORIGEN!\Respaldo BD" "%DESTINO%\Respaldo BD" /E /R:1 /W:1 /NFL /NDL /NJH /NJS >nul
) else (
  echo [2/3] Respaldo BD no existia en el origen, se omite.
)

rem --- Copiar static\uploads ---
if exist "!ORIGEN!\static\uploads" (
  echo.
  echo [3/3] Copiando static\uploads...
  robocopy "!ORIGEN!\static\uploads" "%DESTINO%\static\uploads" /E /R:1 /W:1 /NFL /NDL /NJH /NJS >nul
) else (
  echo [3/3] static\uploads no existia en el origen, se omite.
)

echo.
echo ============================================================
echo  MIGRACION COMPLETADA.
echo.
if defined COPIADO0 (
  echo  IMPORTANTE: Revisa que el servidor abra correctamente y
  echo  que los datos (proyectos, usuarios, licencias) aparezcan.
  echo  Si algo falla, la instalacion vieja sigue intacta en:
  echo    !ORIGEN!
) else (
  echo  No se copio instance (no habia datos en el origen).
  echo  Se trata de una instalacion en blanco: crea el Super
  echo  Usuario de nuevo.
)
echo.
echo  Puedes cerrar esta ventana. Abre la app con el icono
echo  "Informe de Obra" del Escritorio o Menu Inicio.
echo ============================================================
echo.
pause
endlocal
