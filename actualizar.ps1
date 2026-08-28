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
    [string]$OwnerRepo = "jacj01/informe-mensual-obra",
    [string]$VersionLocal = "",
    [string]$ZipFile = ""  # Ruta local al ZIP ya descargado (evita usar gh)
)

$ErrorActionPreference = "Stop"
$Raiz      = $PSScriptRoot
$fuenteVer = Join-Path $Raiz "informe_web\version.py"
$bakDir    = Join-Path $Raiz "actualizar.bak"
$tmpDir    = Join-Path $env:TEMP ("informe_update_" + [System.Guid]::NewGuid().Guid.Substring(0,8))
$progFile  = Join-Path $Raiz "actualizar.estado"

# --- Detectar Python: embebido (carpeta\python\), PATH, o ruta legacy ---
function Find-Python {
    # 1) Python embebido (junto al script)
    $emb = Join-Path $Raiz "python\python.exe"
    if (Test-Path $emb) { return $emb }
    # 2) PATH del sistema
    $inPath = Get-Command python -ErrorAction SilentlyContinue
    if ($inPath) { return $inPath.Source }
    # 3) Ruta legacy (compatibilidad)
    if (Test-Path "C:\Python314\python.exe") { return "C:\Python314\python.exe" }
    return $null
}
function Find-Pythonw {
    $emb = Join-Path $Raiz "python\pythonw.exe"
    if (Test-Path $emb) { return $emb }
    $inPath = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($inPath) { return $inPath.Source }
    if (Test-Path "C:\Python314\pythonw.exe") { return "C:\Python314\pythonw.exe" }
    return $null
}
$PyExe  = Find-Python
$PyWexe = Find-Pythonw

function Escribir-Progreso([string]$fase, [int]$porcentaje, [string]$mensaje = "") {
    $obj = @{ fase = $fase; porcentaje = $porcentaje; mensaje = $mensaje; ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss") }
    $obj | ConvertTo-Json -Compress | Set-Content -Path $progFile -Encoding UTF8
}

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

try {

if (-not $PyExe) {
    Escribir-Progreso "error" 100 "No se encontro Python (ni embebido, ni en PATH, ni legacy)."
    Write-Warning "No se encontro Python. Instale Python o coloque la carpeta python\ junto al script."
    exit 1
}
Write-Host "Python: $PyExe"

# ─────────────────────────────────────────────────────────────────────────
# MODO 1: ZIP local (descargado por el propio aplicativo, /actualizar).
#   No requiere gh CLI ni conexión para detectar release: la app ya validó
#   que existe una versión nueva y descargó el paquete. Se instala directo.
# ─────────────────────────────────────────────────────────────────────────
if ($ZipFile -and (Test-Path $ZipFile)) {
    Write-Host "Usando ZIP local: $ZipFile"
    $verLocal = if ($VersionLocal) { $VersionLocal } else { Version-Local }
    Escribir-Progreso "descargando" 15 "Usando paquete local..."
    New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
    Copy-Item -Path $ZipFile -Destination (Join-Path $tmpDir "update.zip") -Force
    $zipPath = Join-Path $tmpDir "update.zip"
    Escribir-Progreso "descargando" 30 "Paquete listo. Preparando instalación..."
}
else {
# ─────────────────────────────────────────────────────────────────────────
# MODO 2: verificación manual / sin ZIP (requiere gh CLI).
# ─────────────────────────────────────────────────────────────────────────
# 7) Detectar ultima release publicada en GitHub (usa gh: repo privado requiere auth)
$verLocal = if ($VersionLocal) { $VersionLocal } else { Version-Local }
Write-Host "Local: v$verLocal"

if (-not (gh-ok)) {
    Escribir-Progreso "error" 100 "gh (GitHub CLI) no esta disponible. Instala gh e inicia sesion (gh auth login)."
    Write-Warning "gh (GitHub CLI) no esta disponible. Instala gh e inicia sesion (gh auth login)."
    exit 1
}

# tag de la release mas reciente
$tag = (gh release list -R $OwnerRepo --limit 1 --json tagName --jq ".[0].tagName").Trim()
if (-not $tag) { Escribir-Progreso "listo" 100 "No hay releases disponibles."; Write-Host "No hay releases disponibles."; exit 0 }

$verRem = Version-Tag $tag
Write-Host "GitHub: $tag (v$verRem)"

if ([version]$verLocal -ge [version]$verRem) {
    Escribir-Progreso "listo" 100 "Ya esta actualizado (v$verLocal)."
    "Ya esta actualizado (v$verLocal)."
    exit 0
}

if (-not $Instalar) {
    Write-Host "Hay actualizacion disponible ($tag). Ejecuta con -Instalar para aplicarla."
    exit 0
}

Write-Host "Aplicando actualizacion a $tag ..."
Escribir-Progreso "descargando" 5 "Descargando $tag de GitHub..."

# 8) Descargar paquete: si gh o Invoke-WebRequest con token
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

if (gh-ok) {
    Write-Host "Descargando $tag via gh..."
    Escribir-Progreso "descargando" 10 "Descargando $tag via gh..."
    gh release download "$tag" -R $OwnerRepo --pattern "*.zip" --dir $tmpDir
    $zipPath = (Get-ChildItem $tmpDir -Filter "*.zip" | Select-Object -First 1).FullName
} else {
    # Fallback: Invoke-WebRequest con token (extraer de gh auth o env var)
    Write-Host "gh no disponible para descarga. Usando Invoke-WebRequest..."
    Escribir-Progreso "descargando" 10 "Descargando $tag via web..."
    $token = $env:INFORME_GH_TOKEN
    if (-not $token) {
        # Intentar extraer token de gh auth login
        try {
            $ghAuth = & gh auth token 2>$null
            if ($LASTEXITCODE -eq 0 -and $ghAuth) { $token = $ghAuth.Trim() }
        } catch {}
    }
    if (-not $token) {
        # Intentar leer token del config de la app
        $cfgPy = Join-Path $Raiz "informe_web\app.py"
        if (Test-Path $cfgPy) {
            $cfgContent = Get-Content $cfgPy -Raw
            if ($cfgContent -match 'INFORME_GH_TOKEN.*?"([^"]+)"') { $token = $Matches[1] }
        }
    }
    $headers = @{ "Accept" = "application/vnd.github+json" }
    if ($token) { $headers["Authorization"] = "Bearer $token" }
    $apiUrl = "https://api.github.com/repos/$OwnerRepo/releases/latest"
    $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers -TimeoutSec 15
    $asset = $release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
    if (-not $asset) { Escribir-Progreso "error" 100 "No se encontro asset ZIP en la release."; exit 2 }
    $dlHeaders = @{ "Accept" = "application/octet-stream" }
    if ($token) { $dlHeaders["Authorization"] = "Bearer $token" }
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile (Join-Path $tmpDir "update.zip") -Headers $dlHeaders -TimeoutSec 120
    $zipPath = Join-Path $tmpDir "update.zip"
}
}   # fin MODO 2 (else)

# Común para ambos modos: localizar el ZIP descargado y descomprimir a temp
# (no toca la instalacion viva)
$zipPath = (Get-ChildItem $tmpDir -Filter "*.zip" | Select-Object -First 1).FullName
if (-not $zipPath) { Write-Error "No se encontro el asset zip descargado"; exit 2 }
Escribir-Progreso "descargando" 30 "Descomprimiendo paquete..."
Expand-Archive -LiteralPath $zipPath -DestinationPath $tmpDir -Force
Escribir-Progreso "descargando" 30 "Paquete listo. Preparando instalación..."

# Preservar la base de datos / respaldos / uploads / logs del usuario (no viajan en el zip)
$preservation = @("informe_web/instance", "informe_web/Respaldo BD", "informe_web/static/uploads",
               "informe_web/servidor.log", "informe_web/servidor.pid")
# 8.1) Detener el servidor ANTES de mover informe_web; si no, los .py/.pyc abiertos
#      impiden el Move-Item ("proceso en uso"). El updater corre detached, sobrevive.
Escribir-Progreso "instalando" 35 "Deteniendo servidor..."
$pidfile = Join-Path $Raiz "informe_web\servidor.pid"
$matado = $false
if (Test-Path $pidfile) {
    $old = (Get-Content $pidfile -Raw).Trim()
    if ($old -and $old -match '^\d+$') {
        Write-Host "Deteniendo servidor (PID $old) ..."
        Stop-Process -Id ([int]$old) -Force -ErrorAction SilentlyContinue
        $matado = $true
    }
}
if ($matado) {
    # esperar a que los handles del proceso se liberen
    $espera = 0
    while ($espera -lt 15) {
        try { $proc = Get-Process -Id ([int]$old) -ErrorAction Stop } catch { $proc = $null }
        if (-not $proc) { break }
        Start-Sleep -Seconds 1; $espera++
    }
}

# 8.2) Respaldo de la instalacion actual (rollback)
if (Test-Path $bakDir) { Remove-Item -Recurse -Force $bakDir }
New-Item -ItemType Directory -Force -Path $bakDir | Out-Null   # Move-Item needs parent dir
Start-Sleep -Seconds 2   # dejar que los handles del server detenido se liberen
Escribir-Progreso "instalando" 50 "Respaldando instalacion actual..."
Move-Item -LiteralPath (Join-Path $Raiz "informe_web") -Destination (Join-Path $bakDir "informe_web")

# Copiar la nueva informe_web
Escribir-Progreso "instalando" 70 "Instalando nueva version..."
Copy-Item -Recurse -Force (Join-Path $tmpDir "informe_web") -Destination (Join-Path $Raiz "informe_web") -ErrorAction Stop

# Restaurar los datos preservados (si existian en el backup, copiarlos de vuelta)
foreach ($p in $preservation) {
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
Escribir-Progreso "verificando" 80 "Verificando sintaxis de la nueva version..."
$ok = $true
try {
    & $PyExe -m py_compile "$Raiz/informe_web/app.py" 2>$null
    if ($LASTEXITCODE -ne 0) { $ok = $false }
} catch { $ok = $false }

if ($ok) {
    Write-Host "Actualizacion OK ($tag). Limpiando backup."
    Remove-Item -Recurse -Force $bakDir
    # El servidor ya fue detenido antes del backup. Levantarlo con la nueva version.
    Start-Process -FilePath $PyWexe `
        -ArgumentList "servidor_silencioso.py" `
        -WorkingDirectory "$Raiz/informe_web"
    Write-Host "Servidor iniciado con la nueva version ($tag)."
    Escribir-Progreso "listo" 100 "Actualizacion completada. Servidor iniciado."
} else {
    Write-Warning "Fallo la verificacion: haciendo rollback a la version anterior."
    Escribir-Progreso "rollback" 100 "Error: fallo la verificacion. Haciendo rollback."
    Remove-Item -Recurse -Force (Join-Path $Raiz "informe_web") -ErrorAction SilentlyContinue
    Move-Item -LiteralPath (Join-Path $bakDir "informe_web") -Destination (Join-Path $Raiz "informe_web")
    Write-Host "Rollback completado. Sistema sin cambios."
    # Reactivar el server antiguo (ya que el updater lo mata al instalar)
    Start-Process -FilePath $PyWexe `
        -ArgumentList "servidor_silencioso.py" `
        -WorkingDirectory "$Raiz/informe_web"
    Write-Host "Servidor antiguo restaurado y reiniciado."
    exit 2
}

} catch {
    # Cualquier error inesperado: reportar y, si la instalacion quedo incompleta,
    # restaurar la version anterior desde el respaldo.
    $errMsg = $_.Exception.Message
    Write-Warning "Error durante la actualizacion: $errMsg"
    $bakOld = Join-Path $bakDir "informe_web"
    $liveDir = Join-Path $Raiz "informe_web"
    if ((Test-Path (Join-Path $bakOld "app.py")) -and -not (Test-Path (Join-Path $liveDir "app.py"))) {
        Write-Warning "Instalacion incompleta: restaurando respaldo anterior..."
        Remove-Item -Recurse -Force $liveDir -ErrorAction SilentlyContinue
        Move-Item -LiteralPath $bakOld -Destination $liveDir -ErrorAction SilentlyContinue
        Start-Process -FilePath $PyWexe `
            -ArgumentList "servidor_silencioso.py" `
            -WorkingDirectory "$Raiz/informe_web" -ErrorAction SilentlyContinue
        Escribir-Progreso "rollback" 100 "Se restauro la version anterior tras un error."
    } else {
        Escribir-Progreso "error" 100 ("Error: " + $errMsg)
    }
    exit 1
}
