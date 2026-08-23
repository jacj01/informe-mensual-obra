# -*- coding: utf-8 -*-
"""Parche v3: restaura desde backup, aplica fix correcto con indentacion."""
import os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_PY = os.path.join(ROOT, "informe_web", "app.py")
BASE_HTML = os.path.join(ROOT, "informe_web", "templates", "base.html")
BACKUP = os.path.join(ROOT, "_patch_backup")

print("=== Parche v3 - Fix indentacion + regex ===")

bak = os.path.join(BACKUP, "app.py.bak")
if not os.path.exists(bak):
    print("ERROR: No hay backup")
    sys.exit(1)

shutil.copy2(bak, APP_PY)
print("[OK] app.py restaurado desde backup")

with open(APP_PY, "r", encoding="utf-8") as f:
    code = f.read()

idx1 = code.find("def api_actualizacion()")
idx2 = code.find("def aplicar_actualizacion()")
if idx1 == -1 or idx2 == -1:
    print("ERROR: No se encontraron las funciones")
    sys.exit(1)

# Encontrar la linea del decorador antes de api_actualizacion
line_start = code.rfind("\n", 0, idx1) + 1
decorator_line = code[line_start:idx1].strip()
# Should be "@app.route(...)\n"

new_api = """    @app.route("/api/actualizacion")
    def api_actualizacion():
        \"\"\"Consulta la release mas reciente publicada en GitHub.
        Estrategia: gh CLI primero; REST API publica como fallback.\"\"\""""
    if not es_admin_actual():
        return jsonify({"error": "No autorizado"}), 403
    repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")
    local_v = app.config.get("INFORME_VERSION", "1.0.0")

    def _vt(s):
        import re
        m = re.search(r"v?(\\d+\\.\\d+\\.\\d+)", s or "")
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0, 0, 0)

    data = None
    tag = ""

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
        data = None

    if data is None:
        try:
            import urllib.request, urllib.error, ssl
            api_url = "https://api.github.com/repos/" + repo + "/releases/latest"
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
            Log('[UPDATE] REST API fallo: ' + str(e))
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

    @app.route("/actualizar", methods=["POST"])
    def aplicar_actualizacion():
        \"\"\"Descarga e instala actualizacion. gh CLI o REST API.\"\"\""""

# Esto es problematico con triple-quoted strings y quotes internas.
# Mejor usar el metodo de lineas individuales con .join
print("Usando metodo alternativo...")

with open(bak, "r", encoding="utf-8") as f:
    code = f.read()

idx1 = code.find("def api_actualizacion()")
idx2 = code.find("def aplicar_actualizacion()")

# Reemplazo simple: buscar el bloque completo y reemplazar
# El viejo bloque va desde el decorador hasta justo antes del siguiente decorador
old_start = code.rfind("@", 0, idx1)
old_end = code.find("@app.route(\"/actualizar\"")

new_block = '''    @app.route("/api/actualizacion")
    def api_actualizacion():
        """Consulta la release mas reciente publicada en GitHub.
        Estrategia: gh CLI primero; REST API publica como fallback."""
        if not es_admin_actual():
            return jsonify({"error": "No autorizado"}), 403
        repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")
        local_v = app.config.get("INFORME_VERSION", "1.0.0")

        def _vt(s):
            import re
            m = re.search(r"v?(\\d+\\.\\d+\\.\\d+)", s or "")
            return tuple(int(x) for x in m.group(1).split(".")) if m else (0, 0, 0)

        data = None
        tag = ""

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
            data = None

        if data is None:
            try:
                import urllib.request, urllib.error, ssl
                api_url = "https://api.github.com/repos/" + repo + "/releases/latest"
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
                Log('[UPDATE] REST API fallo: ' + str(e))
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

    @app.route("/actualizar", methods=["POST"])
    def aplicar_actualizacion():
        """Dispara la actualizacion en el propio equipo.
        Descarga el ZIP via gh release download o REST API directa (repo publico).
        Solo Admin / Super."""
        if not es_admin_actual():
            return jsonify({"error": "No autorizado"}), 403
        try:
            import subprocess, tempfile, urllib.request, ssl
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ps1 = os.path.join(root, "actualizar.ps1")
            repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")
            local_v = app.config.get("INFORME_VERSION", "1.0.0")

            tag = ""
            try:
                cmd = ["gh", "-R", repo, "release", "view", "--json", "tagName"]
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                                     creationflags=0x08000000)
                if out.returncode == 0:
                    tag = json.loads(out.stdout).get("tagName", "")
            except Exception:
                pass
            if not tag:
                try:
                    api_url = "https://api.github.com/repos/" + repo + "/releases/latest"
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
                try:
                    api_dl = "https://api.github.com/repos/" + repo + "/releases/tags/" + tag
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
                        with urllib.request.urlopen(req3, timeout=120, context=ctx2) as dl:
                            zip_path = os.path.join(tmp_dir, zip_asset["name"])
                            with open(zip_path, "wb") as f:
                                while True:
                                    chunk = dl.read(65536)
                                    if not chunk:
                                        break
                                    f.write(chunk)
                except Exception:
                    zip_path = None

            if not zip_path:
                return jsonify({"ok": False,
                                "error": "No se pudo descargar el paquete. "
                                         "Ejecute 'gh auth login' para autenticar."}), 400

            ps_args = ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden",
                       "-ExecutionPolicy", "Bypass", "-File", ps1, "-Instalar",
                       "-VersionLocal", local_v, "-ZipFile", zip_path]
            subprocess.Popen(ps_args, cwd=root,
                             creationflags=0x08000800,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return jsonify({"ok": True, "msg": "Actualizacion iniciada."})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

'''

if old_start == -1 or old_end == -1:
    print("ERROR: No se encontro el bloque a reemplazar")
    sys.exit(1)

code = code[:old_start] + new_block + code[old_end:]
print("[OK] api_actualizacion + aplicar_actualizacion parcheados")

with open(APP_PY, "w", encoding="utf-8") as f:
    f.write(code)

# base.html fix
with open(BASE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

old_h = "if (d.disponible) {"
new_h = ("if (d.error) {\n"
         "            document.getElementById('updErrorMsg').textContent = 'Error: ' + d.error;\n"
         "            _updShow('updEstadoError');\n"
         "            _updBtn('updBtnInstalar', false);\n"
         "          } else if (d.disponible) {")
if old_h in html:
    html = html.replace(old_h, new_h, 1)
    with open(BASE_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] base.html parcheado")
else:
    print("[SKIP] base.html ya parcheado")

# Verificar
import re
test = re.search(r"v?(\d+\.\d+\.\d+)", "v1.1.0-f51baf3")
if test:
    print("[OK] Regex: v1.1.0-f51baf3 -> " + test.group(1))

print("\nListo. Reinicie el servidor.")
