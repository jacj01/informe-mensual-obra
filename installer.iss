; Inno Setup Script - Informe Mensual de Obra
; Genera el instalador .exe que incluye Python Embeddable + la app.
; El usuario final ejecuta el .exe y queda todo listo para usar.

#define MyAppName "Informe Mensual de Obra"
#define MyAppVersion "1.0.6"
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
; Launchers y scripts raiz
Source: "iniciar_servidor.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "iniciar_local.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "iniciar_sin_consola.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "detener_servidor.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "actualizar.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "abrir_puerto_firewall.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "Logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "Logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: ".gitignore"; DestDir: "{app}"; Flags: ignoreversion
; La app completa (excluye instance/, uploads/, Respaldo BD/ via .gitignore del zip)
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
Filename: "{app}\instalar_python.bat"; StatusMsg: "Configurando Python e instalando dependencias..."; Flags: runhidden waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir Informe de Obra ahora"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}\python"
Type: filesandordirs; Name: "{app}\informe_web\instance"
Type: filesandordirs; Name: "{app}\informe_web\Respaldo BD"
Type: filesandordirs; Name: "{app}\informe_web\static\uploads"
Type: files; Name: "{app}\informe_web\servidor.log"
Type: files; Name: "{app}\informe_web\servidor.pid"
Type: files; Name: "{app}\instalar_python.bat"

[Code]
// Descarga e instala Python Embeddable antes de la instalacion principal.
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  DestDir: String;
  PyExe: String;
  ResultCode: Integer;
  TmpDir: String;
  ZipPath: String;
  Url: String;
begin
  Result := '';
  DestDir := ExpandConstant('{app}\python');
  PyExe := DestDir + '\python.exe';

  // Si Python ya esta instalado, no hacer nada
  if FileExists(PyExe) then
    Exit;

  // Crear directorio temporal para descargar
  TmpDir := ExpandConstant('{tmp}');
  ZipPath := TmpDir + '\{#PyZip}';
  Url := 'https://www.python.org/ftp/python/{#PythonVersion}/{#PyZip}';

  // Descargar Python Embeddable
  Exec('powershell.exe',
    '-NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri ''' + Url + ''' -OutFile ''' + ZipPath + '''"',
    '', SW_SHOW, ewWaitUntilTerminated, ResultCode);

  if ResultCode <> 0 then
  begin
    Result := 'Error al descargar Python. Verifique su conexion a internet.';
    Exit;
  end;

  // Crear directorio destino
  ForceDirectories(DestDir);

  // Descomprimir
  Exec('powershell.exe',
    '-NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path ''' + ZipPath + ''' -DestinationPath ''' + DestDir + ''' -Force"',
    '', SW_SHOW, ewWaitUntilTerminated, ResultCode);

  if ResultCode <> 0 then
  begin
    Result := 'Error al descomprimir Python.';
    Exit;
  end;

  // Habilitar import site (para pip)
  Exec('powershell.exe',
    '-NoProfile -ExecutionPolicy Bypass -Command "' +
    '$pth = Get-ChildItem -Path ''' + DestDir + ''' -Filter ''python*._pth'' | Select-Object -First 1; ' +
    'if ($pth) { ' +
    '  $c = Get-Content $pth.FullName -Raw; ' +
    '  $c = $c -replace ''#import site'', ''import site''; ' +
    '  Set-Content -Path $pth.FullName -Value $c -NoNewline ' +
    '}"',
    '', SW_SHOW, ewWaitUntilTerminated, ResultCode);

  // Crear script de instalacion de paquetes (se ejecuta en [Run])
  SaveStringToFile(ExpandConstant('{app}\instalar_python.bat'),
    '@echo off' + #13#10 +
    'cd /d "%~dp0python"' + #13#10 +
    'echo Instalando pip...' + #13#10 +
    'python -c "import pip" 2>nul' + #13#10 +
    'if errorlevel 1 (' + #13#10 +
    '  python -m ensurepip --upgrade >nul 2>&1' + #13#10 +
    '  python -m pip install --upgrade pip --quiet --disable-pip-version-check' + #13#10 +
    ')' + #13#10 +
    'echo Instalando Flask, Flask-SQLAlchemy, waitress...' + #13#10 +
    'python -m pip install Flask Flask-SQLAlchemy waitress --quiet --disable-pip-version-check' + #13#10 +
    'echo Listo.' + #13#10 +
    'del "%~f0"', False);
end;
