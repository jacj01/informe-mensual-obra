# ============================================================
# Parche: actualizacion sin gh CLI (repo publico)
# Maquina目標: v1.0.9
# Uso: powershell -ExecutionPolicy Bypass -File parche_actualizacion.ps1
# ============================================================

$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appPy   = Join-Path $dir 'informe_web\app.py'
$baseHtml = Join-Path $dir 'informe_web\templates\base.html'
$backupDir = Join-Path $dir '_patch_backup'

# --- Verificar que los archivos existen ---
if (!(Test-Path $appPy))       { Write-Host 'ERROR: No se encontro informe_web\app.py' -ForegroundColor Red; exit 1 }
if (!(Test-Path $baseHtml))    { Write-Host 'ERROR: No se encontro informe_web\templates\base.html' -ForegroundColor Red; exit 1 }

# --- Detener servidor ---
Write-Host 'Deteniendo servidor...' -ForegroundColor Yellow
Get-Process -Name pythonw -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name python  -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# --- Crear respaldo ---
if (!(Test-Path $backupDir)) { New-Item -Path $backupDir -ItemType Directory -Force | Out-Null }
Copy-Item $appPy    (Join-Path $backupDir 'app.py.bak') -Force
Copy-Item $baseHtml (Join-Path $backupDir 'base.html.bak') -Force
Write-Host "Respaldos creados en $backupDir" -ForegroundColor Green

# ============================================================
# PARCHE 1: app.py - Reemplazar api_actualizacion
# ============================================================
Write-Host 'Aplicando parche en api_actualizacion...' -ForegroundColor Cyan

$apiOld = @'
    @app.route("/api/actualizacion")
    def api_actualizacion():
        """Consulta la release mas reciente publicada en GitHub y decide si hay
        una version NUEVA disponible (remota > local).
        Solo Administradores y el Super Usuario pueden consultar.

        Estrategia: intenta gh CLI primero; si falla (no instalado / sin auth),
        usa la REST API de GitHub con un PAT embebido como fallback."""
        if not es_admin_actual():
            return jsonify({"error": "No autorizado"}), 403
        repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")
        local_v = app.config.get("INFORME_VERSION", "1.0.0")

        def _vt(s):
            import re
            m = re.search(r"v?(\d+\.\d+\.\d+)", s or "")
            return tuple(int(x) for x in m.group(1).split(".")) if m else (0, 0, 0)

        data = None
        tag = ""

        # --- Estrategia 1: gh CLI ---
        try:
            import subprocess, re
            cmd = ["gh", "-R", repo, "release", "view", "--json",
                   "tagName,name,publishedAt,assets"]
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                                 creationflags=0x08000000)
            if out.returncode == 0 and out.stdout.strip():
                raw = json.loads(out.stdout)
                tag = raw.get("tagName", "")
                asset = next((a for a in raw.get("assets", [])
                              if a.get("name", "").endswith(".zip")), None)
                data = {
                    "tag": tag,
                    "nombre": raw.get("name", ""),
                    "publicada": raw.get("publicatedAt", ""),
                    "asset": asset.get("name") if asset else None,
                    "url": asset.get("url") if asset else None,
                }
        except Exception:
            data = None  # fallback a REST API

        # --- Estrategia 2: gh auth token + REST API ---
        if data is None:
            try:
                import urllib.request, urllib.error, subprocess as _sp
                # Obtener token de gh auth (funciona si el usuario hizo gh auth login)
                token = app.config.get("INFORME_GH_TOKEN", "")
                if not token:
                    try:
                        t_out = _sp.run(["gh", "auth", "token"],
                                        capture_output=True, text=True, timeout=10,
                                        creationflags=0x08000000)
                        if t_out.returncode == 0 and t_out.stdout.strip():
                            token = t_out.stdout.strip()
                    except Exception:
                        pass
                api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                req = urllib.request.Request(api_url)
                req.add_header("Accept", "application/vnd.github+json")
                if token:
                    req.add_header("Authorization", f"Bearer {token}")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                tag = raw.get("tag_name", "")
                asset = next((a for a in raw.get("assets", [])
                              if a.get("name", "").endswith(".zip")), None)
                data = {
                    "tag": tag,
                    "nombre": raw.get("name", ""),
                    "publicada": raw.get("published_at", ""),
                    "asset": asset.get("name") if asset else None,
                    "url": asset.get("browser_download_url") if asset else None,
                }
            except Exception as e:
                return jsonify({"disponible": False, "error": str(e),
                                "version_actual": local_v}), 502

        hay_nueva = _vt(tag) > _vt(local_v)
        return jsonify({
            "disponible": bool(hay_nueva), "tag": tag,
            "nombre": data.get("nombre", ""),
            "publicada": data.get("publicada", ""),
            "asset": data.get("asset"),
            "url": data.get("url"),
            "version_actual": local_v,
        })
'@

$apiNew = @'
    @app.route("/api/actualizacion")
    def api_actualizacion():
        """Consulta la release mas reciente publicada en GitHub y decide si hay
        una version NUEVA disponible (remota > local).
        Solo Administradores y el Super Usuario pueden consultar.

        Estrategia: intenta gh CLI primero; si falla (no instalado / sin auth),
        usa la REST API publica de GitHub directamente (sin token)."""
        if not es_admin_actual():
            return jsonify({"error": "No autorizado"}), 403
        repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")
        local_v = app.config.get("INFORME_VERSION", "1.0.0")

        def _vt(s):
            import re
            m = re.search(r"v?(\d+\.\d+\.\d+)", s or "")
            return tuple(int(x) for x in m.group(1).split(".")) if m else (0, 0, 0)

        data = None
        tag = ""

        # --- Estrategia 1: gh CLI ---
        try:
            import subprocess, re
            cmd = ["gh", "-R", repo, "release", "view", "--json",
                   "tagName,name,publishedAt,assets"]
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                                 creationflags=0x08000000)
            if out.returncode == 0 and out.stdout.strip():
                raw = json.loads(out.stdout)
                tag = raw.get("tagName", "")
                asset = next((a for a in raw.get("assets", [])
                              if a.get("name", "").endswith(".zip")), None)
                data = {
                    "tag": tag,
                    "nombre": raw.get("name", ""),
                    "publicada": raw.get("publicatedAt", ""),
                    "asset": asset.get("name") if asset else None,
                    "url": asset.get("url") if asset else None,
                }
        except Exception:
            data = None  # fallback a REST API

        # --- Estrategia 2: REST API de GitHub (sin auth, repo publico) ---
        if data is None:
            try:
                import urllib.request, urllib.error, ssl
                api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                req = urllib.request.Request(api_url)
                req.add_header("Accept", "application/vnd.github+json")
                req.add_header("User-Agent", "InformeObra/1.0")
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                tag = raw.get("tag_name", "")
                asset = next((a for a in raw.get("assets", [])
                              if a.get("name", "").endswith(".zip")), None)
                data = {
                    "tag": tag,
                    "nombre": raw.get("name", ""),
                    "publicada": raw.get("published_at", ""),
                    "asset": asset.get("name") if asset else None,
                    "url": asset.get("browser_download_url") if asset else None,
                }
            except Exception as e:
                return jsonify({"disponible": None, "error": str(e),
                                "version_actual": local_v}), 502

        hay_nueva = _vt(tag) > _vt(local_v)
        return jsonify({
            "disponible": bool(hay_nueva), "tag": tag,
            "nombre": data.get("nombre", ""),
            "publicada": data.get("publicada", ""),
            "asset": data.get("asset"),
            "url": data.get("url"),
            "version_actual": local_v,
        })
'@

# ============================================================
# PARCHE 2: app.py - Reemplazar aplicar_actualizacion
# ============================================================
Write-Host 'Aplicando parche en aplicar_actualizacion...' -ForegroundColor Cyan

$applyOld = @'
    @app.route("/actualizar", methods=["POST"])
    def aplicar_actualizacion():
        """Dispara la actualizacion en el propio equipo.
        Descarga el ZIP via gh release download y lanza actualizar.ps1.
        Si gh no esta autenticado, intenta REST API con token.
        Solo Admin / Super."""
        if not es_admin_actual():
            return jsonify({"error": "No autorizado"}), 403
        try:
            import subprocess, tempfile, urllib.request
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ps1 = os.path.join(root, "actualizar.ps1")
            repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")
            local_v = app.config.get("INFORME_VERSION", "1.0.0")

            # Obtener token de gh auth
            token = app.config.get("INFORME_GH_TOKEN", "")
            if not token:
                try:
                    t_out = subprocess.run(["gh", "auth", "token"],
                                           capture_output=True, text=True, timeout=10,
                                           creationflags=0x08000000)
                    if t_out.returncode == 0 and t_out.stdout.strip():
                        token = t_out.stdout.strip()
                except Exception:
                    pass

            # Obtener tag de la release remota
            tag = ""
            try:
                cmd = ["gh", "-R", repo, "release", "view", "--json", "tagName"]
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                                     creationflags=0x08000000)
                if out.returncode == 0:
                    tag = json.loads(out.stdout).get("tagName", "")
            except Exception:
                pass
            if not tag and token:
                try:
                    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                    req = urllib.request.Request(api_url)
                    req.add_header("Accept", "application/vnd.github+json")
                    req.add_header("Authorization", f"Bearer {token}")
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        tag = json.loads(resp.read().decode()).get("tag_name", "")
                except Exception:
                    pass

            if not tag:
                return jsonify({"ok": False,
                                "error": "No se pudo obtener la version remota. "
                                         "Ejecute 'gh auth login' para autenticar."}), 400

            # Descargar ZIP via gh release download
            tmp_dir = tempfile.mkdtemp(prefix="informe_upd_")
            zip_path = None
            try:
                r = subprocess.run(["gh", "-R", repo, "release", "download", tag,
                                    "--pattern", "*.zip", "--dir", tmp_dir],
                                   capture_output=True, text=True, timeout=120,
                                   creationflags=0x08000000)
                if r.returncode == 0:
                    zips = [f for f in os.listdir(tmp_dir) if f.endswith(".zip")]
                    if zips:
                        zip_path = os.path.join(tmp_dir, zips[0])
            except Exception:
                zip_path = None

            if not zip_path:
                return jsonify({"ok": False,
                                "error": "No se pudo descargar el paquete. "
                                         "Ejecute 'gh auth login' para autenticar."}), 400
'@

$applyNew = @'
    @app.route("/actualizar", methods=["POST"])
    def aplicar_actualizacion():
        """Dispara la actualizacion en el propio equipo.
        Descarga el ZIP via gh release download (si gh esta disponible) o
        via REST API directa (repo publico). Lanza actualizar.ps1.
        Solo Admin / Super."""
        if not es_admin_actual():
            return jsonify({"error": "No autorizado"}), 403
        try:
            import subprocess, tempfile, urllib.request, ssl
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ps1 = os.path.join(root, "actualizar.ps1")
            repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")
            local_v = app.config.get("INFORME_VERSION", "1.0.0")

            # Obtener tag de la release remota
            tag = ""
            # Estrategia 1: gh CLI
            try:
                cmd = ["gh", "-R", repo, "release", "view", "--json", "tagName"]
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                                     creationflags=0x08000000)
                if out.returncode == 0:
                    tag = json.loads(out.stdout).get("tagName", "")
            except Exception:
                pass
            # Estrategia 2: REST API publica
            if not tag:
                try:
                    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                    req = urllib.request.Request(api_url)
                    req.add_header("Accept", "application/vnd.github+json")
                    req.add_header("User-Agent", "InformeObra/1.0")
                    ctx = ssl.create_default_context()
                    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                        tag = json.loads(resp.read().decode()).get("tag_name", "")
                except Exception:
                    pass

            if not tag:
                return jsonify({"ok": False,
                                "error": "No se pudo obtener la version remota. "
                                         "Verifique su conexion a internet."}), 400

            # Descargar ZIP: intentar gh primero, luego REST API directa
            tmp_dir = tempfile.mkdtemp(prefix="informe_upd_")
            zip_path = None
            # Intento 1: gh release download
            try:
                r = subprocess.run(["gh", "-R", repo, "release", "download", tag,
                                    "--pattern", "*.zip", "--dir", tmp_dir],
                                   capture_output=True, text=True, timeout=120,
                                   creationflags=0x08000000)
                if r.returncode == 0:
                    zips = [f for f in os.listdir(tmp_dir) if f.endswith(".zip")]
                    if zips:
                        zip_path = os.path.join(tmp_dir, zips[0])
            except Exception:
                zip_path = None
            # Intento 2: REST API directa (repo publico)
            if not zip_path:
                try:
                    api_dl = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
                    req2 = urllib.request.Request(api_dl)
                    req2.add_header("Accept", "application/vnd.github+json")
                    req2.add_header("User-Agent", "InformeObra/1.0")
                    ctx2 = ssl.create_default_context()
                    with urllib.request.urlopen(req2, timeout=15, context=ctx2) as resp2:
                        rel = json.loads(resp2.read().decode())
                    zip_asset = next((a for a in rel.get("assets", [])
                                      if a.get("name", "").endswith(".zip")), None)
                    if zip_asset:
                        dl_url = zip_asset.get("browser_download_url")
                        req3 = urllib.request.Request(dl_url)
                        req3.add_header("User-Agent", "InformeObra/1.0")
                        with urllib.request.urlopen(req3, timeout=120, context=ctx2) as dl_resp:
                            zip_path = os.path.join(tmp_dir, zip_asset["name"])
                            with open(zip_path, "wb") as f:
                                while True:
                                    chunk = dl_resp.read(65536)
                                    if not chunk:
                                        break
                                    f.write(chunk)
                except Exception:
                    zip_path = None

            if not zip_path:
                return jsonify({"ok": False,
                                "error": "No se pudo descargar el paquete. "
                                         "Verifique su conexion a internet."}), 400
'@

# ============================================================
# PARCHE 3: base.html - Manejo de errores en update check
# ============================================================
Write-Host 'Aplicando parche en base.html...' -ForegroundColor Cyan

$htmlOld = @'
      fetch('/api/actualizacion', { credentials: 'same-origin' })
        .then(function(r) { if (r.status===403||r.redirected) throw new Error('No autorizado'); return r.json(); })
        .then(function(d) {
          sessionStorage.setItem(_CLAVE_CACHE, JSON.stringify(d));
          if (d.disponible) {
            document.getElementById('updVerActual').textContent = window._tagLimpio(d.version_actual);
            document.getElementById('updVerNueva').textContent = window._tagLimpio(d.tag);
            document.getElementById('updFecha').textContent = d.publicada ? new Date(d.publicada).toLocaleDateString('es-PE') : '-';
            document.getElementById('updAsset').textContent = d.asset || '-';
            document.getElementById('updAssetRow').style.display = d.asset ? '' : 'none';
            _updDownloadUrl = d.url || '';
            _updShow('updEstadoDisponible');
            _updBtn('updBtnInstalar', true);
          } else {
            document.getElementById('updVerLocal').textContent = window._tagLimpio(d.version_actual) || d.version_actual;
            _updShow('updEstadoNoHay');
          }
        })
        .catch(function(e) {
          _updShow('updEstadoError');
          document.getElementById('updErrorMsg').textContent = e.message || 'No se pudo conectar con GitHub';
          _updBtn('updBtnInstalar', false);
        });
'@

$htmlNew = @'
      fetch('/api/actualizacion', { credentials: 'same-origin' })
        .then(function(r) { if (r.status===403||r.redirected) throw new Error('No autorizado'); return r.json(); })
        .then(function(d) {
          sessionStorage.setItem(_CLAVE_CACHE, JSON.stringify(d));
          if (d.error) {
            document.getElementById('updErrorMsg').textContent = 'Error: ' + d.error;
            _updShow('updEstadoError');
            _updBtn('updBtnInstalar', false);
          } else if (d.disponible) {
            document.getElementById('updVerActual').textContent = window._tagLimpio(d.version_actual);
            document.getElementById('updVerNueva').textContent = window._tagLimpio(d.tag);
            document.getElementById('updFecha').textContent = d.publicada ? new Date(d.publicada).toLocaleDateString('es-PE') : '-';
            document.getElementById('updAsset').textContent = d.asset || '-';
            document.getElementById('updAssetRow').style.display = d.asset ? '' : 'none';
            _updDownloadUrl = d.url || '';
            _updShow('updEstadoDisponible');
            _updBtn('updBtnInstalar', true);
          } else {
            document.getElementById('updVerLocal').textContent = window._tagLimpio(d.version_actual) || d.version_actual;
            _updShow('updEstadoNoHay');
          }
        })
        .catch(function(e) {
          _updShow('updEstadoError');
          document.getElementById('updErrorMsg').textContent = e.message || 'No se pudo conectar con GitHub';
          _updBtn('updBtnInstalar', false);
        });
'@

# ============================================================
# APLICAR PARCHES
# ============================================================
$content = Get-Content $appPy -Raw -Encoding UTF8
$changed = $false

# Parche api_actualizacion
if ($content.Contains($apiOld)) {
    $content = $content.Replace($apiOld, $apiNew)
    $changed = $true
    Write-Host '  [OK] api_actualizacion parcheado' -ForegroundColor Green
} else {
    Write-Host '  [SKIP] api_actualizacion ya parcheado o version no compatible' -ForegroundColor DarkYellow
}

# Parche aplicar_actualizacion
if ($content.Contains($applyOld)) {
    $content = $content.Replace($applyOld, $applyNew)
    $changed = $true
    Write-Host '  [OK] aplicar_actualizacion parcheado' -ForegroundColor Green
} else {
    Write-Host '  [SKIP] aplicar_actualizacion ya parcheado o version no compatible' -ForegroundColor DarkYellow
}

if ($changed) {
    [System.IO.File]::WriteAllText($appPy, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host 'app.py guardado correctamente' -ForegroundColor Green
} else {
    Write-Host 'Ningun cambio aplicado en app.py' -ForegroundColor DarkYellow
}

# Parche base.html
$htmlContent = Get-Content $baseHtml -Raw -Encoding UTF8
if ($htmlContent.Contains($htmlOld)) {
    $htmlContent = $htmlContent.Replace($htmlOld, $htmlNew)
    [System.IO.File]::WriteAllText($baseHtml, $htmlContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host '  [OK] base.html parcheado (manejo de errores)' -ForegroundColor Green
} else {
    Write-Host '  [SKIP] base.html ya parcheado o version no compatible' -ForegroundColor DarkYellow
}

# ============================================================
# REINICIAR SERVIDOR
# ============================================================
Write-Host 'Reiniciando servidor...' -ForegroundColor Yellow
$pidFile = Join-Path $dir 'informe_web\servidor.pid'
Remove-Item $pidFile -Force -ErrorAction SilentlyContinue

$srvDir = Join-Path $dir 'informe_web'
Start-Process 'pythonw' -ArgumentList 'servidor_silencioso.py' -WorkingDirectory $srvDir -WindowStyle Hidden
Start-Sleep -Seconds 3

if (Test-Path $pidFile) {
    $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
    Write-Host "Servidor PID: $pid" -ForegroundColor Green
    Write-Host ''
    Write-Host '=== PARCHE APLICADO CON EXITO ===' -ForegroundColor Green
    Write-Host 'Ahora puede usar "Buscar actualizacion" normalmente.' -ForegroundColor White
    Write-Host "Respaldos en: $backupDir" -ForegroundColor DarkGray
} else {
    Write-Host 'Advertencia: servidor puede no haber iniciado. Revisar servidor.log' -ForegroundColor Yellow
}
