; Inno Setup Script - Informe Mensual de Obra
; Genera el instalador .exe que incluye Python Embeddable + la app.
; El usuario final ejecuta el .exe y queda todo listo para usar.

#define MyAppName "Informe Mensual de Obra"
#define MyAppVersion "1.2.1"
#define MyAppPublisher "INGENIERIA DE LA CONSTRUCCION PROYECTOS Y ASESORIA S.A.C."
#define MyAppURL "https://github.com/jacj01/informe-mensual-obra"
#define MyAppExeName "iniciar_sin_consola.vbs"
#define PythonVersion "3.14.0"
#define PythonArch "amd64"
#define PyZip "python-" + PythonVersion + "-embed-" + PythonArch + ".zip"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\InformeObra
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=InformeObra-Setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
SetupLogging=yes
SetupIconFile="Logo.ico"
UninstallDisplayIcon={app}\Logo.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Lanzadores y scripts raiz
Source: "iniciar_servidor.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "iniciar_local.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "iniciar_sin_consola.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "detener_servidor.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "actualizar.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "abrir_puerto_firewall.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "Logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "Logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: ".gitignore"; DestDir: "{app}"; Flags: ignoreversion
; Archivos de datos para combobox
Source: "Rubro.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "Recursos.txt"; DestDir: "{app}"; Flags: ignoreversion
; Codigo fuente Python (solo la raiz de informe_web; *.py coincide con los
; .py de primer nivel y NO baja a subdirectorios, asi NO se empaquetan instance\
; ni __pycache__). Tampoco se incluyen servidor.log ni servidor.pid (runtime).
; ojo: NO usar recursesubdirs aqui, porque en Inno 6.7.3 el parametro Excludes
; no se aplica con recursesubdirs (se comprimiria la BD de desarrollo en instance\).
Source: "informe_web\*.py"; DestDir: "{app}\informe_web"; Flags: ignoreversion
Source: "informe_web\requirements.txt"; DestDir: "{app}\informe_web"; Flags: ignoreversion
Source: "informe_web\INFORMACION_APLICATIVO.txt"; DestDir: "{app}\informe_web"; Flags: ignoreversion
; Plantillas y estaticos (no contienen BD/logs/pycache)
Source: "informe_web\templates\*"; DestDir: "{app}\informe_web\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "informe_web\static\*"; DestDir: "{app}\informe_web\static"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Abrir Informe de Obra"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Logo.ico"
Name: "{group}\Detener Servidor"; Filename: "{app}\detener_servidor.bat"
Name: "{group}\Pagina del Proyecto"; Filename: "http://127.0.0.1:5000"
Name: "{group}\Desinstalar"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Informe de Obra"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\Logo.ico"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Iconos adicionales:"; Flags: checkedonce

[Run]
; instalar_python.bat se ejecuta SIEMPRE (instalacion nueva o actualizacion): es
; idempotente, descarga/instala Python solo si falta y luego asegura las
; dependencias (Flask, openpyxl, Pillow, waitress) desde requirements.txt
Filename: "{app}\instalar_python.bat"; StatusMsg: "Configurando Python..."; Flags: runhidden waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir Informe de Obra ahora"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}\python"
Type: files; Name: "{app}\informe_web\servidor.pid"
Type: files; Name: "{app}\informe_web\servidor.log"
Type: files; Name: "{app}\instalar_python.bat"

[Code]
var
  BackupDir: String;
  NeedRestore: Boolean;

function IsFreshInstall: Boolean;
begin
  // La base de datos maestra vive en instance/informe.db (NO en informe_web\
  // directamente). Revisar la ruta correcta evita que una actualizacion sobre
  // una instalacion existente se trate como instalacion nueva (lo que saltaba
  // el respaldo de la DB y ejecutaba limpiar_usuarios.bat en cada actualizacion).
  Result := not FileExists(ExpandConstant('{app}\informe_web\instance\informe.db'));
end;

function PsExec(const Cmd: String): Boolean;
var
  R: Integer;
begin
  Result := Exec('powershell.exe',
    '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "' + Cmd + '"',
    '', SW_HIDE, ewWaitUntilTerminated, R);
  Log('[PS] Code=' + IntToStr(R) + ' Cmd: ' + Cmd);
end;

// Descarga e instala Python Embeddable si no existe ya en {app}\python.
procedure SetupPython;
var
  DestDir, PyExe, TmpDir, ZipPath, Url: String;
begin
  DestDir := ExpandConstant('{app}\python');
  PyExe := DestDir + '\python.exe';
  if FileExists(PyExe) then
  begin
    Log('[INSTALL] Python ya presente: ' + PyExe);
    Exit;
  end;

  Log('[INSTALL] Descargando Python Embeddable...');
  ForceDirectories(DestDir);
  TmpDir := ExpandConstant('{tmp}');
  ZipPath := TmpDir + '\{#PyZip}';
  Url := 'https://www.python.org/ftp/python/{#PythonVersion}/{#PyZip}';

  if not PsExec('Invoke-WebRequest -Uri ''' + Url + ''' -OutFile ''' + ZipPath + '''') then
  begin
    Log('[INSTALL] ERROR descargando Python. Se reintentara desde instalar_python.bat.');
    Exit;
  end;

  if not PsExec('Expand-Archive -Path ''' + ZipPath + ''' -DestinationPath ''' + DestDir + ''' -Force') then
  begin
    Log('[INSTALL] ERROR descomprimiendo Python.');
    Exit;
  end;

  // Habilitar import site (necesario para que funcione pip)
  PsExec('$pth = Get-ChildItem -Path ''' + DestDir + ''' -Filter ''python*._pth'' | Select-Object -First 1; ' +
         'if ($pth) { $c = Get-Content $pth.FullName -Raw; $c = $c -replace ''#import site'',''import site''; ' +
         'Set-Content -Path $pth.FullName -Value $c -NoNewline }');
  Log('[INSTALL] Python Embeddable listo en: ' + DestDir);
end;

// Escribe instalar_python.bat en {app}\ que asegura pip y las dependencias
// del proyecto desde requirements.txt (idempotente: solo instala lo que falta).
procedure GenerarInstalarBat;
var
  Bat: String;
begin
  Bat :=
    '@echo off' + #13#10 +
    'cd /d "%~dp0python"' + #13#10 +
    'set "PYTHONNOUSERSITE=1"' + #13#10 +
    'echo === Configurando Python e instalando dependencias ===' + #13#10 +
    'set "PIP=no"' + #13#10 +
    'python -c "import sys, pip" >nul 2>&1 && set "PIP=yes"' + #13#10 +
    'if not "%PIP%"=="yes" (' + #13#10 +
    '  echo Descargando get-pip.py...' + #13#10 +
    '  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri ''https://bootstrap.pypa.io/get-pip.py'' -OutFile ''%~dp0get-pip.py''"' + #13#10 +
    '  python "%~dp0get-pip.py" --quiet' + #13#10 +
    '  del "%~dp0get-pip.py"' + #13#10 +
    ')' + #13#10 +
    'echo Instalando dependencias (Flask, openpyxl, Pillow, waitress)...' + #13#10 +
    'python -m pip install -r "%~dp0informe_web\requirements.txt" --quiet --disable-pip-version-check' + #13#10 +
    'echo === Listo ===' + #13#10;
  SaveStringToFile(ExpandConstant('{app}\instalar_python.bat'), Bat, False);
  Log('[INSTALL] instalar_python.bat generado.');
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  R: Integer;
  AppWeb: String;
begin
  Result := '';
  NeedRestore := False;
  BackupDir := ExpandConstant('{app}\_installer_backup');
  AppWeb := ExpandConstant('{app}\informe_web');

  // === DETENER SERVIDOR ===
  Log('[INSTALL] Deteniendo servidor...');
  Exec('taskkill.exe', '/IM pythonw.exe /F', '', SW_HIDE, ewWaitUntilTerminated, R);
  Exec('taskkill.exe', '/IM python.exe /F', '', SW_HIDE, ewWaitUntilTerminated, R);
  DeleteFile(AppWeb + '\servidor.pid');
  Sleep(2000);

  // === GARANTIZAR PYTHON EMBEDDABLE (instalacion nueva o actualizacion) ===
  // Si no existe python.exe se descarga Python Embeddable y se habilita pip.
  SetupPython;

  // === GENERAR instalar_python.bat (idempotente, se ejecuta en [Run]) ===
  // Solo instala pip y las dependencias que falten (Flask, openpyxl, Pillow,
  // waitress) desde requirements.txt. Sirve tanto para instalacion nueva como
  // para actualizaciones que puedan carecer de dependencias.
  GenerarInstalarBat;

  // === UPGRADE: respaldar datos críticos ANTES de copiar ===
  if IsFreshInstall then
  begin
    Log('[INSTALL] Fresh install - no hay DB existente. No se respalda DB.');
    Exit;
  end;

  Log('[INSTALL] Upgrade detectado - iniciando respaldo...');

  // Limpiar respaldo anterior
  PsExec('Remove-Item -Path ''' + BackupDir + ''' -Recurse -Force -ErrorAction SilentlyContinue');

  // Crear directorio raíz del respaldo
  PsExec('New-Item -Path ''' + BackupDir + ''' -ItemType Directory -Force | Out-Null');

  // Respaldar instance/ (base de datos principal + tenants)
  if DirExists(AppWeb + '\instance') then
  begin
    PsExec('Copy-Item -Path ''' + AppWeb + '\instance'' -Destination ''' + BackupDir + '\instance'' -Recurse -Force');
    Log('[INSTALL] Respaldo instance/: OK');
  end;

  // Respaldar static/uploads/ (archivos de usuario)
  if DirExists(AppWeb + '\static\uploads') then
  begin
    PsExec('Copy-Item -Path ''' + AppWeb + '\static\uploads'' -Destination ''' + BackupDir + '\uploads'' -Recurse -Force');
    Log('[INSTALL] Respaldo uploads/: OK');
  end;

  // Respaldar Respaldo BD/ (backups automáticos)
  if DirExists(AppWeb + '\Respaldo BD') then
  begin
    PsExec('Copy-Item -Path ''' + AppWeb + '\Respaldo BD'' -Destination ''' + BackupDir + '\resaldo_bd'' -Recurse -Force');
    Log('[INSTALL] Respaldo Respaldo BD/: OK');
  end;

  // Verificar que el respaldo se creó
  if DirExists(BackupDir + '\instance') then
  begin
    NeedRestore := True;
    Log('[INSTALL] Respaldo completo. Se restaurará después de la instalación.');
  end
  else
    Log('[INSTALL] ERROR: No se pudo crear respaldo. La DB podría perderse.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  AppWeb: String;
begin
  if CurStep <> ssPostInstall then Exit;
  if not NeedRestore then
  begin
    Log('[RESTORE] Sin respaldo que restaurar.');
    Exit;
  end;

  AppWeb := ExpandConstant('{app}\informe_web');
  Log('[RESTORE] Iniciando restauración post-instalación...');

  // 1. Restaurar instance/ (base de datos)
  if DirExists(BackupDir + '\instance') then
  begin
    PsExec('Remove-Item -Path ''' + AppWeb + '\instance'' -Recurse -Force -ErrorAction SilentlyContinue');
    PsExec('Copy-Item -Path ''' + BackupDir + '\instance'' -Destination ''' + AppWeb + '\instance'' -Recurse -Force');
    if FileExists(AppWeb + '\instance\informe.db') then
      Log('[RESTORE] instance/ restaurada OK.')
    else
      Log('[RESTORE] ERROR: instance/ NO se restauró.');
  end;

  // 2. Restaurar static/uploads/
  if DirExists(BackupDir + '\uploads') then
  begin
    PsExec('Remove-Item -Path ''' + AppWeb + '\static\uploads'' -Recurse -Force -ErrorAction SilentlyContinue');
    PsExec('Copy-Item -Path ''' + BackupDir + '\uploads'' -Destination ''' + AppWeb + '\static\uploads'' -Recurse -Force');
    Log('[RESTORE] uploads/ restaurado OK.');
  end;

  // 3. Restaurar Respaldo BD/
  if DirExists(BackupDir + '\resaldo_bd') then
  begin
    PsExec('Remove-Item -Path ''' + AppWeb + '\Respaldo BD'' -Recurse -Force -ErrorAction SilentlyContinue');
    PsExec('Copy-Item -Path ''' + BackupDir + '\resaldo_bd'' -Destination ''' + AppWeb + '\Respaldo BD'' -Recurse -Force');
    Log('[RESTORE] Respaldo BD/ restaurado OK.');
  end;

  // 4. Limpiar directorio de respaldo
  PsExec('Remove-Item -Path ''' + BackupDir + ''' -Recurse -Force -ErrorAction SilentlyContinue');
  Log('[RESTORE] Limpieza completada.');
end;
