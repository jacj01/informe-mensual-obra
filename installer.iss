; Inno Setup Script - Informe Mensual de Obra
; Genera el instalador .exe que incluye Python Embeddable + la app.
; El usuario final ejecuta el .exe y queda todo listo para usar.

#define MyAppName "Informe Mensual de Obra"
#ifndef MyAppVersion
#define MyAppVersion "1.3.1"
#endif
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
Source: "informe_web\*.py"; DestDir: "{app}\informe_web"; Flags: ignoreversion; Excludes: "config_correo.py,config_red.py,requirements.txt"
Source: "informe_web\requirements.txt"; DestDir: "{app}\informe_web"; Flags: ignoreversion
Source: "informe_web\INFORMACION_APLICATIVO.txt"; DestDir: "{app}\informe_web"; Flags: ignoreversion
; Plantillas y estaticos (no contienen BD/logs/pycache)
Source: "informe_web\templates\*"; DestDir: "{app}\informe_web\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "informe_web\static\*"; DestDir: "{app}\informe_web\static"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Abrir Informe de Obra"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Logo.ico"; Check: EsModoAdmin
Name: "{group}\Conectar al Servidor"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Logo.ico"; Check: EsModoCliente
Name: "{group}\Detener Servidor"; Filename: "{app}\detener_servidor.bat"; Check: EsModoAdmin
Name: "{group}\Pagina del Proyecto"; Filename: "http://127.0.0.1:5000"; Check: EsModoAdmin
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
Type: files; Name: "{app}\informe_web\config_red.py"
Type: files; Name: "{app}\LEEME_RED.txt"

[Code]
var
  BackupDir: String;
  NeedRestore: Boolean;
  ModoCliente: Boolean;
  IpLocal: String;
  PaginaTipo: TWizardPage;
  rAdm: TNewRadioButton;
  rCli: TNewRadioButton;
  eUrl: TNewComboBox;
  lblUrl: TNewStaticText;
  lblInfo: TNewStaticText;
  btnBuscar: TNewButton;
  lblResultado: TNewStaticText;

function EsModoAdmin: Boolean;
begin
  Result := not ModoCliente;
end;

function EsModoCliente: Boolean;
begin
  Result := ModoCliente;
end;

procedure CambioModo(Sender: TObject);
begin
  if rCli.Checked then
  begin
    lblUrl.Enabled := True;
    eUrl.Enabled := True;
    btnBuscar.Enabled := True;
    lblResultado.Enabled := True;
    lblInfo.Caption := 'Pulse "Buscar servidor" para detectar automaticamente los equipos Administrador de esta subred y elegir una URL; o escribala a mano.';
  end
  else
  begin
    lblUrl.Enabled := False;
    eUrl.Enabled := False;
    btnBuscar.Enabled := False;
    lblResultado.Enabled := False;
    if IpLocal <> '' then
      lblInfo.Caption := 'IP de red de este equipo: ' + IpLocal + #13#10 +
        'Los equipos CLIENTES entraran a: http://' + IpLocal + ':5000'
    else
      lblInfo.Caption := 'El instalador detectara automaticamente el IP de red de este equipo.';
  end;
end;

function NormalizarUrl(S: String): String;
begin
  Result := Trim(S);
  if Pos('://', Result) = 0 then
    Result := 'http://' + Result;
  while (Length(Result) > 0) and (Result[Length(Result)] = '/') do
    Delete(Result, Length(Result), 1);
end;

procedure GenerarScriptsRed;
var
  IpFile, ScanFile, IpTxt, ScanTxt: String;
begin
  // Scripts PowerShell usados por el wizard: deteccion del IP local y
  // busqueda de servidores en la subred (puerto 5000). Se ejecutan con
  // "powershell.exe -MTA -File" (WaitAll requiere MTA).
  IpFile := ExpandConstant('{tmp}\ip_red.ps1');
  ScanFile := ExpandConstant('{tmp}\scan_red.ps1');
  IpTxt := ExpandConstant('{tmp}\ip_red.txt');
  ScanTxt := ExpandConstant('{tmp}\scan_red.txt');

  SaveStringToFile(IpFile,
    '$file = ''' + IpTxt + '''' + #13#10 +
    '$ip = (Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null } | Select-Object -First 1).IPv4Address.IPAddress' + #13#10 +
    'if (-not $ip) { $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch ''^(127\.|169\.254\.)'' } | Select-Object -First 1).IPAddress }' + #13#10 +
    'if (-not $ip) { $ip = ''127.0.0.1'' }' + #13#10 +
    '$ip | Out-File -FilePath $file -Encoding ascii -NoNewline' + #13#10,
    False);

  SaveStringToFile(ScanFile,
    '$file = ''' + ScanTxt + '''' + #13#10 +
    '$puerto = 5000' + #13#10 +
    '$ip = (Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null } | Select-Object -First 1).IPv4Address.IPAddress' + #13#10 +
    'if (-not $ip) { $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch ''^(127\.|169\.254\.)'' } | Select-Object -First 1).IPAddress }' + #13#10 +
    'if (-not $ip) { $ip = ''127.0.0.1'' }' + #13#10 +
    '$octs = $ip -split ''\.'' | ForEach-Object { $_ }' + #13#10 +
    '$base = ($octs[0..2] -join ''.'') + ''.''' + #13#10 +
    '$ips = 1..254 | ForEach-Object { $base + $_ }' + #13#10 +
    '$encontrados = @()' + #13#10 +
    'for ($i = 0; $i -lt $ips.Count; $i += 60) {' + #13#10 +
    '  $fin = [math]::Min($i + 59, $ips.Count - 1)' + #13#10 +
    '  $chunk = $ips[$i..$fin]' + #13#10 +
    '  $cand = @{}' + #13#10 +
    '  $handles = @()' + #13#10 +
    '  foreach ($addr in $chunk) {' + #13#10 +
    '    $cl = New-Object System.Net.Sockets.TcpClient' + #13#10 +
    '    $ar = $cl.BeginConnect($addr, $puerto, $null, $null)' + #13#10 +
    '    $cand[$addr] = $cl' + #13#10 +
    '    $handles += $ar.AsyncWaitHandle' + #13#10 +
    '  }' + #13#10 +
    '  [System.Threading.WaitHandle]::WaitAll($handles, 2500) | Out-Null' + #13#10 +
    '  foreach ($addr in $cand.Keys) {' + #13#10 +
    '    try {' + #13#10 +
    '      if ($cand[$addr].Connected) { $encontrados += $addr }' + #13#10 +
    '    } catch {}' + #13#10 +
    '    try { $cand[$addr].Close() } catch {}' + #13#10 +
    '  }' + #13#10 +
    '}' + #13#10 +
    '$urls = $encontrados | ForEach-Object { ''http://'' + $_ + '':'' + $puerto } | Sort-Object -Unique' + #13#10 +
    'if ($urls.Count -eq 0) { $urls = @('''') }' + #13#10 +
    '$urls -join ''|'' | Out-File -FilePath $file -Encoding ascii -NoNewline' + #13#10,
    False);

  Log('[RED] Scripts PowerShell generados en {tmp}.');
end;

function EjecutarPSFile(const ScriptFile: String): Boolean;
var
  R: Integer;
begin
  Result := Exec('powershell.exe',
    '-NoProfile -MTA -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + ScriptFile + '"',
    '', SW_HIDE, ewWaitUntilTerminated, R);
  Log('[RED] PS ' + ScriptFile + ' -> code ' + IntToStr(R));
end;

function DetectarIpLocal: String;
var
  FilePath: String;
  S: AnsiString;
begin
  Result := '';
  FilePath := ExpandConstant('{tmp}\ip_red.txt');
  DeleteFile(FilePath);
  if EjecutarPSFile(ExpandConstant('{tmp}\ip_red.ps1')) and FileExists(FilePath) then
  begin
    if LoadStringFromFile(FilePath, S) then
      Result := Trim(S);
  end;
  DeleteFile(FilePath);
end;

procedure BuscarServidor(Sender: TObject);
var
  OutFile: String;
  S: AnsiString;
  Items: TStringList;
  i: Integer;
  Txt: String;
begin
  btnBuscar.Enabled := False;
  lblResultado.Caption := 'Buscando servidores en la subred... espere unos segundos.';
  try
    OutFile := ExpandConstant('{tmp}\scan_red.txt');
    DeleteFile(OutFile);
    if EjecutarPSFile(ExpandConstant('{tmp}\scan_red.ps1')) and FileExists(OutFile) then
    begin
      if LoadStringFromFile(OutFile, S) then
      begin
        Items := TStringList.Create;
        try
          Items.Delimiter := '|';
          Items.DelimitedText := Trim(S);
          eUrl.Items.Clear;
          for i := 0 to Items.Count - 1 do
          begin
            Txt := Trim(Items[i]);
            if Txt <> '' then eUrl.Items.Add(Txt);
          end;
          if eUrl.Items.Count > 0 then
          begin
            eUrl.ItemIndex := 0;
            if eUrl.Items.Count > 1 then
              lblResultado.Caption := 'Se encontraron varios servidores: elija el del equipo Administrador.'
            else
              lblResultado.Caption := 'Servidor encontrado. Puede corregir la URL si hace falta.';
          end
          else
            lblResultado.Caption := 'No se encontro servidor en esta subred. Escriba la URL a mano o revise el firewall del Administrador.';
        finally
          Items.Free;
        end;
      end
      else
        lblResultado.Caption := 'No se pudo leer el resultado del escaneo. Escriba la URL a mano.';
    end
    else
      lblResultado.Caption := 'No se pudo ejecutar la busqueda. Escriba la URL a mano.';
    DeleteFile(OutFile);
  finally
    btnBuscar.Enabled := True;
  end;
end;

procedure InitializeWizard;
begin
  // Pagina "Tipo de instalacion": Administrador (servidor con BD) o Cliente.
  GenerarScriptsRed;

  PaginaTipo := CreateCustomPage(wpSelectDir,
    'Tipo de instalacion',
    'Elija como se usara este equipo dentro de la red de la obra.');

  rAdm := TNewRadioButton.Create(PaginaTipo);
  rAdm.Parent := PaginaTipo.Surface;
  rAdm.Caption := 'Administrador (servidor con base de datos)';
  rAdm.Left := 0;
  rAdm.Top := 0;
  rAdm.Width := PaginaTipo.Surface.Width;
  rAdm.Checked := True;
  rAdm.OnClick := @CambioModo;

  rCli := TNewRadioButton.Create(PaginaTipo);
  rCli.Parent := PaginaTipo.Surface;
  rCli.Caption := 'Cliente (equipo que se conecta al servidor)';
  rCli.Left := 0;
  rCli.Top := rAdm.Top + rAdm.Height + 8;
  rCli.Width := PaginaTipo.Surface.Width;
  rCli.OnClick := @CambioModo;

  lblInfo := TNewStaticText.Create(PaginaTipo);
  lblInfo.Parent := PaginaTipo.Surface;
  lblInfo.Left := 0;
  lblInfo.Top := rCli.Top + rCli.Height + 12;
  lblInfo.Width := PaginaTipo.Surface.Width;
  lblInfo.Height := 40;
  lblInfo.AutoSize := False;
  lblInfo.WordWrap := True;

  lblUrl := TNewStaticText.Create(PaginaTipo);
  lblUrl.Parent := PaginaTipo.Surface;
  lblUrl.Caption := 'Direccion del servidor (ej.: http://192.168.1.70:5000 o el IP Tailscale 100.x.x.x):';
  lblUrl.Left := 8;
  lblUrl.Top := lblInfo.Top + lblInfo.Height + 8;
  lblUrl.Width := PaginaTipo.Surface.Width - 16;
  lblUrl.WordWrap := True;

  eUrl := TNewComboBox.Create(PaginaTipo);
  eUrl.Parent := PaginaTipo.Surface;
  eUrl.Left := 8;
  eUrl.Top := lblUrl.Top + lblUrl.Height + 6;
  eUrl.Width := PaginaTipo.Surface.Width - 90;
  eUrl.Style := csDropDown;

  btnBuscar := TNewButton.Create(PaginaTipo);
  btnBuscar.Parent := PaginaTipo.Surface;
  btnBuscar.Caption := 'Buscar servidor';
  btnBuscar.Left := eUrl.Left + eUrl.Width + 8;
  btnBuscar.Top := eUrl.Top - 2;
  btnBuscar.Width := 74;

  lblResultado := TNewStaticText.Create(PaginaTipo);
  lblResultado.Parent := PaginaTipo.Surface;
  lblResultado.Left := 8;
  lblResultado.Top := eUrl.Top + eUrl.Height + 8;
  lblResultado.Width := PaginaTipo.Surface.Width - 16;
  lblResultado.Height := 32;
  lblResultado.AutoSize := False;
  lblResultado.WordWrap := True;

  btnBuscar.OnClick := @BuscarServidor;
  CambioModo(nil);
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = PaginaTipo.ID then
  begin
    if IpLocal = '' then
      IpLocal := DetectarIpLocal;
    CambioModo(nil);
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Url: String;
begin
  Result := True;
  if CurPageID = PaginaTipo.ID then
  begin
    ModoCliente := rCli.Checked;
    if ModoCliente then
    begin
      Url := NormalizarUrl(eUrl.Text);
      if Url = '' then
      begin
        MsgBox('Indique la direccion del servidor.', mbError, MB_OK);
        Result := False;
        Exit;
      end;
      eUrl.Text := Url;
    end;
  end;
end;

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

procedure RestaurarDatos;
var
  AppWeb: String;
begin
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

// Escribe config_red.py segun el tipo de instalacion elegido en el wizard.
// En modo cliente la URL del servidor queda en SERVIDOR_URL; en modo
// administrador se ignora (el servidor escucha en 0.0.0.0:5000).
procedure EscribirConfigRed;
var
  Txt, Url: String;
begin
  if ModoCliente then
  begin
    Url := NormalizarUrl(eUrl.Text);
    Txt := 'MODO = "cliente"' + #13#10 +
           'SERVIDOR_URL = "' + Url + '"' + #13#10;
  end
  else
  begin
    Txt := 'MODO = "administrador"' + #13#10 +
           'SERVIDOR_URL = "http://127.0.0.1:5000"' + #13#10;
  end;
  SaveStringToFile(ExpandConstant('{app}\informe_web\config_red.py'), Txt, False);
  if ModoCliente then
    Log('[RED] config_red.py escrito en modo cliente.')
  else
    Log('[RED] config_red.py escrito en modo administrador.');
end;

procedure EscribirLeeme;
var
  Txt: String;
begin
  if ModoCliente then
  begin
    Txt :=
      'LEEME - MODO CLIENTE (Informe Mensual de Obra)' + #13#10 + #13#10 +
      'Este equipo NO guarda la base de datos: se conecta al equipo' + #13#10 +
      'ADMINISTRADOR (el servidor). Para entrar, el Administrador debe estar' + #13#10 +
      'encendido y ambos equipos deben verse entre si (misma red local o Tailscale).' + #13#10 + #13#10 +
      '- Durante la instalacion se eligio la URL del servidor; el boton' + #13#10 +
      '  "Buscar servidor" ayuda a detectarla automaticamente en la subred.' + #13#10 + #13#10 +
      '- Doble clic en "Abrir Informe de Obra": espere unos segundos y se abrira' + #13#10 +
      '  el navegador con el servidor.' + #13#10 + #13#10 +
      '- Si no se conecta, revise: que el Administrador este encendido y con el' + #13#10 +
      '  servidor activo, y que la direccion grabada en informe_web\config_red.py' + #13#10 +
      '  (SERVIDOR_URL) sea la correcta.' + #13#10 + #13#10 +
      '- Entre equipos en redes distintas (oficina / casa / obra) use Tailscale:' + #13#10 +
      '    1) Instale Tailscale en este equipo y en el Administrador.' + #13#10 +
      '    2) Inicie sesion con la misma cuenta en ambos.' + #13#10 +
      '    3) En el Administrador, su IP privada es 100.x.x.x (interfaz Tailscale);' + #13#10 +
      '       se ve en "iniciar_servidor.bat" o en la bandeja de Tailscale.' + #13#10 +
      '    4) En este cliente escriba esa IP como URL: http://100.x.x.x:5000' + #13#10 + #13#10 +
      '- Si instalo el modo equivocado, vuelva a ejecutar el instalador y elija' + #13#10 +
      '  el otro modo (los datos del Administrador se conservan).' + #13#10;
  end
  else
  begin
    Txt :=
      'LEEME - MODO ADMINISTRADOR (Informe Mensual de Obra)' + #13#10 + #13#10 +
      'Este equipo es el SERVIDOR: contiene la base de datos y atiende a los' + #13#10 +
      'equipos CLIENTES de la red.' + #13#10 + #13#10 +
      '- El servidor debe estar encendido para que los clientes puedan entrar.' + #13#10;
    if IpLocal <> '' then
      Txt := Txt +
        '- IP de red de este equipo: ' + IpLocal + #13#10 +
        '  Los clientes entraran a: http://' + IpLocal + ':5000' + #13#10 + #13#10;
    Txt := Txt +
      '- Si cambio de red, vea las IP vigentes ejecutando "iniciar_servidor.bat".' + #13#10 + #13#10 +
      '- Misma red local (Wi-Fi/LAN):' + #13#10 +
      '    1) Ejecute una vez "abrir_puerto_firewall.bat" como Administrador.' + #13#10 +
      '    2) Comparta la IP local (ej.: http://192.168.1.70:5000) con los clientes.' + #13#10 + #13#10 +
      '- Equipos en redes distintas (oficina / casa / obra) use Tailscale:' + #13#10 +
      '    1) Instale Tailscale en ESTE equipo y en los equipos cliente.' + #13#10 +
      '    2) Inicie sesion con la misma cuenta en todos.' + #13#10 +
      '    3) Este equipo queda con una IP privada 100.x.x.x (interfaz Tailscale).' + #13#10 +
      '    4) Comparta http://100.x.x.x:5000 con los clientes. El trafico viaja' + #13#10 +
      '       cifrado aunque los equipos esten en redes distintas.' + #13#10 + #13#10 +
      '- Para instalar un equipo cliente, ejecute el instalador en la otra' + #13#10 +
      '  maquina y elija el modo CLIENTE (allí podra usar "Buscar servidor").' + #13#10;
  end;
  SaveStringToFile(ExpandConstant('{app}\LEEME_RED.txt'), Txt, False);
  Log('[RED] LEEME_RED.txt escrito.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep <> ssPostInstall then Exit;
  RestaurarDatos;
  EscribirConfigRed;
  EscribirLeeme;
end;
