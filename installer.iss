; Inno Setup Script - Informe Mensual de Obra
; Genera el instalador .exe que incluye Python Embeddable + la app.
; El usuario final ejecuta el .exe y queda todo listo para usar.

#define MyAppName "Informe Mensual de Obra"
#define MyAppVersion "1.0.8"
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
DefaultDirName={autopf}\InformeObra
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=InformeObra-Setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
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
; La app completa
Source: "informe_web\*"; DestDir: "{app}\informe_web"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Abrir Informe de Obra"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Logo.ico"
Name: "{group}\Detener Servidor"; Filename: "{app}\detener_servidor.bat"
Name: "{group}\Pagina del Proyecto"; Filename: "http://127.0.0.1:5000"
Name: "{group}\Desinstalar"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Informe de Obra"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\Logo.ico"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Iconos adicionales:"; Flags: checkedonce

[Run]
Filename: "{app}\instalar_python.bat"; StatusMsg: "Configurando Python..."; Flags: runhidden waituntilterminated; Check: IsFreshInstall
Filename: "{app}\limpiar_usuarios.bat"; StatusMsg: "Configurando usuarios..."; Flags: runhidden waituntilterminated; Check: IsFreshInstall
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir Informe de Obra ahora"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}\python"
Type: files; Name: "{app}\informe_web\servidor.pid"
Type: files; Name: "{app}\informe_web\servidor.log"
Type: files; Name: "{app}\instalar_python.bat"
Type: files; Name: "{app}\limpiar_usuarios.bat"
Type: files; Name: "{app}\limpiar_usuarios.py"

[Code]
var
  BackupDir: String;
  NeedRestore: Boolean;

function IsFreshInstall: Boolean;
begin
  Result := not FileExists(ExpandConstant('{app}\informe_web\informe.db'));
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

  // === FRESH INSTALL: solo instalar Python, NO tocar DB ===
  if IsFreshInstall then
  begin
    Log('[INSTALL] Fresh install - no hay DB existente.');
    Exit;
  end;

  // === UPGRADE: respaldar datos críticos ANTES de copiar ===
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
