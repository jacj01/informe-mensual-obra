<#
.SYNOPSIS
    Actualizador automatico del aplicativo Informe Mensual de Obra.

.DESCRIPTION
    Detecta la ultima release publicada en GitHub (paso 7), descarga el paquete,
    lo instala preservando la base de datos del usuario (pasos 8) y, si el
    proceso falla, restaura la version anterior (paso 9).

    Uso:  .\actualizar.ps1 [-Instalar]
      Sin -Instalar: solo verifica e informa.
      Con  -Instalar: aplica la actualizacion con rollback automatico.

    Se recomienda ejecutarlo desde la carpeta del proyecto
    (informe_web\...) = C:\Users\JOHN\Documents\Informe Mensual
#>
param(
    [switch]$Instalar,
    [string]$OwnerRepo = "jacj01/informe-mensual-obra"
)

$ErrorActionPreference = "Stop"
$Raiz      = $PSScriptRoot
$fuenteVer = Join-Path $Raiz "informe_web\version.py"
$bakDir    = Join-Path $Raiz "actualizar.bak"
$tmpDir    = Join-Path $env:TEMP ("informe_update_" + [System.Guid]::NewGuid().Guid.Substring(0,8))

function Version-Local {
    $txt = Get-Content $fuenteVer -Raw
    if ($txt -match '__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"') { return $Matches[1] }
    return "0.0.0"
}
function Version-Tag([string]$tag) {
    if ($tag -match 'v?([0-9]+\.[0-9]+\.[0-9]+)') { return $Matches[1] }
    return "0.0.0"
}

function gh-ok { $null = Get-Command gh -ErrorAction SilentlyContinue; return $?}

# 7) Detectar ultima release publicada en GitHub (usa gh: repo privado requiere auth)
$verLocal = Version-Local
Write-Host "Local: v$verLocal"

if (-not (gh-ok)) {
    Write-Warning "gh (GitHub CLI) no esta disponible. Instala gh e inicia sesion (gh auth login)."
    exit 1
}

# tag de la release mas reciente
$tag = (gh release list -R $OwnerRepo --limit 1 --json tagName --jq ".[0].tagName").Trim()
if (-not $tag) { Write-Host "No hay releases disponibles."; exit 0 }

$verRem = Version-Tag $tag
Write-Host "GitHub: $tag (v$verRem)"

if ([version]$verLocal -ge [version]$verRem) {
    "Ya esta actualizado (v$verLocal)."
    exit 0
}

if (-not $Instalar) {
    Write-Host "Hay actualizacion disponible ($tag). Ejecuta con -Instalar para aplicarla."
    exit 0
}

Write-Host "Aplicando actualizacion a $tag ..."

# 8) Descargar paquete (gh usa tu token del keyring: funciona en repo privado)
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
Write-Host "Descargando $tag ..."
gh release download "$tag" -R $OwnerRepo --pattern "*.zip" --dir $tmpDir

$zipPath = (Get-ChildItem $tmpDir -Filter "*.zip" | Select-Object -First 1).FullName
if (-not $zipPath) { Write-Error "No se encontro el asset zip descargado"; exit 2 }

# Descomprimir a temp
Expand-Archive -LiteralPath $zipPath -DestinationPath $tmpDir -Force

# Preservar la base de datos / respaldos / uploads / logs del usuario (no viajan en el zip)
$preservar = @("informe_web/instance", "informe_web/Respaldo BD", "informe_web/static/uploads",
               "informe_web/servidor.log", "informe_web/servidor.pid")

# Respaldo de la instalacion actual (rollback)
if (Test-Path $bakDir) { Remove-Item -Recurse -Force $bakDir }
Move-Item -LiteralPath (Join-Path $Raiz "informe_web") -Destination (Join-Path $bakDir "informe_web")

# Copiar la nueva informe_web
Copy-Item -Recurse -Force (Join-Path $tmpDir "informe_web") -Destination (Join-Path $Raiz "informe_web") -ErrorAction Stop

# Restaurar los datos preservados (si existian en el backup, copiarlos de vuelta)
foreach ($p in $preservar) {
    $src = Join-Path $bakDir $p
    if (Test-Path $src) {
        $dst = Join-Path $Raiz $p
        Copy-Item -Path $src -Destination $dst -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Reemplazar tambien los launchers y logo raiz del paquete
Copy-Item -Force (Join-Path $tmpDir "*.bat") -Destination $Raiz -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $tmpDir "iniciar_sin_consola.vbs") -Destination $Raiz -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $tmpDir "Logo.png") -Destination $Raiz -ErrorAction SilentlyContinue

# 9) Verificar; rollback si falla
Write-Host "Verificando sintaxis de la nueva version ..."
$ok = $true
try {
    & "C:\Python314\python.exe" -m py_compile "$Raiz/informe_web/app.py" 2>$null
    if ($LASTEXITCODE -ne 0) { $ok = $false }
} catch { $ok = $false }

if ($ok) {
    Write-Host "Actualizacion OK ($tag). Limpiando backup."
    Remove-Item -Recurse -Force $bakDir
    # Reiniciar el servidor silencioso con la nueva version
    $pidfile = Join-Path $Raiz "informe_web\servidor.pid"
    if (Test-Path $pidfile) {
        $old = Get-Content $pidfile -Raw
        Stop-Process -Id ([int]$old) -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
    Start-Process -FilePath "C:\Python314\pythonw.exe" `
        -ArgumentList "servidor_silencioso.py" `
        -WorkingDirectory "$Raiz/informe_web"
    Write-Host "Servidor reiniciado con la nueva version."
} else {
    Write-Warning "Fallo la verificacion: haciendo rollback a la version anterior."
    Remove-Item -Recurse -Force (Join-Path $Raiz "informe_web") -ErrorAction SilentlyContinue
    Move-Item -LiteralPath (Join-Path $bakDir "informe_web") -Destination (Join-Path $Raiz "informe_web")
    Write-Host "Rollback completado. Sistema sin cambios."
    # Reactivar el server antiguo (ya que el updater lo mata al instalar)
    Start-Process -FilePath "C:\Python314\pythonw.exe" `
        -ArgumentList "servidor_silencioso.py" `
        -WorkingDirectory "$Raiz/informe_web"
    Write-Host "Servidor antiguo restaurado y reiniciado."
    exit 2
}
