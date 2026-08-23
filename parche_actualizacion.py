# -*- coding: utf-8 -*-
import os, shutil, sys, time, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_PY = os.path.join(ROOT, "informe_web", "app.py")
BASE_HTML = os.path.join(ROOT, "informe_web", "templates", "base.html")
BACKUP = os.path.join(ROOT, "_patch_backup")

print("=== Parche de actualizacion v1.0.9 ===")

for f in [APP_PY, BASE_HTML]:
    if not os.path.exists(f):
        print("ERROR: " + f + " no encontrado")
        sys.exit(1)
print("Archivos OK")

os.makedirs(BACKUP, exist_ok=True)
shutil.copy2(APP_PY, os.path.join(BACKUP, "app.py.bak"))
shutil.copy2(BASE_HTML, os.path.join(BACKUP, "base.html.bak"))
print("Respaldos OK")

with open(APP_PY, "r", encoding="utf-8") as f:
    code = f.read()

changes = 0

idx1 = code.find("def api_actualizacion()")
idx2 = code.find("def aplicar_actualizacion()")
if idx1 != -1 and idx2 != -1 and idx1 < idx2:
    new_api = 'def api_actualizacion():\n'
    new_api += '        """Consulta la release mas reciente publicada en GitHub.\n'
    new_api += '        Estrategia: gh CLI primero; REST API publica como fallback."""\n'
    new_api += '        if not es_admin_actual():\n'
    new_api += '            return jsonify({"error": "No autorizado"}), 403\n'
    new_api += '        repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")\n'
    new_api += '        local_v = app.config.get("INFORME_VERSION", "1.0.0")\n'
    new_api += '\n'
    new_api += '        def _vt(s):\n'
    new_api += '            import re\n'
    new_api += '            m = re.search(r"v?(\\\\d+\\\\.\\\\d+\\\\.\\\\d+)", s or "")\n'
    new_api += '            return tuple(int(x) for x in m.group(1).split(".")) if m else (0, 0, 0)\n'
    new_api += '\n'
    new_api += '        data = None\n'
    new_api += '        tag = ""\n'
    new_api += '\n'
    new_api += '        try:\n'
    new_api += '            import subprocess, re\n'
    new_api += '            cmd = ["gh", "-R", repo, "release", "view", "--json",\n'
    new_api += '                   "tagName,name,publishedAt,assets"]\n'
    new_api += '            out = subprocess.run(cmd, capture_output=True, text=True, timeout=15,\n'
    new_api += '                                 creationflags=0x08000000)\n'
    new_api += '            if out.returncode == 0 and out.stdout.strip():\n'
    new_api += '                raw = json.loads(out.stdout)\n'
    new_api += '                tag = raw.get("tagName", "")\n'
    new_api += '                asset = next((a for a in raw.get("assets", [])\n'
    new_api += '                              if a.get("name", "").endswith(".zip")), None)\n'
    new_api += '                data = {\n'
    new_api += '                    "tag": tag,\n'
    new_api += '                    "nombre": raw.get("name", ""),\n'
    new_api += '                    "publicada": raw.get("publicatedAt", ""),\n'
    new_api += '                    "asset": asset.get("name") if asset else None,\n'
    new_api += '                    "url": asset.get("url") if asset else None,\n'
    new_api += '                }\n'
    new_api += '        except Exception:\n'
    new_api += '            data = None\n'
    new_api += '\n'
    new_api += '        if data is None:\n'
    new_api += '            try:\n'
    new_api += '                import urllib.request, urllib.error, ssl\n'
    new_api += '                api_url = "https://api.github.com/repos/" + repo + "/releases/latest"\n'
    new_api += '                req = urllib.request.Request(api_url)\n'
    new_api += '                req.add_header("Accept", "application/vnd.github+json")\n'
    new_api += '                req.add_header("User-Agent", "InformeObra/1.0")\n'
    new_api += '                ctx = ssl.create_default_context()\n'
    new_api += '                with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:\n'
    new_api += '                    raw = json.loads(resp.read().decode("utf-8"))\n'
    new_api += '                tag = raw.get("tag_name", "")\n'
    new_api += '                asset = next((a for a in raw.get("assets", [])\n'
    new_api += '                              if a.get("name", "").endswith(".zip")), None)\n'
    new_api += '                data = {\n'
    new_api += '                    "tag": tag,\n'
    new_api += '                    "nombre": raw.get("name", ""),\n'
    new_api += '                    "publicada": raw.get("published_at", ""),\n'
    new_api += '                    "asset": asset.get("name") if asset else None,\n'
    new_api += '                    "url": asset.get("browser_download_url") if asset else None,\n'
    new_api += '                }\n'
    new_api += '            except Exception as e:\n'
    new_api += '                return jsonify({"disponible": None, "error": str(e),\n'
    new_api += '                                "version_actual": local_v}), 502\n'
    new_api += '\n'
    new_api += '        hay_nueva = _vt(tag) > _vt(local_v)\n'
    new_api += '        return jsonify({\n'
    new_api += '            "disponible": bool(hay_nueva), "tag": tag,\n'
    new_api += '            "nombre": data.get("nombre", ""),\n'
    new_api += '            "publicada": data.get("publicada", ""),\n'
    new_api += '            "asset": data.get("asset"),\n'
    new_api += '            "url": data.get("url"),\n'
    new_api += '            "version_actual": local_v,\n'
    new_api += '        })\n'
    new_api += '\n'
    code = code[:idx1] + new_api + code[idx2:]
    changes += 1
    print("[OK] api_actualizacion")

idx3 = code.find("def aplicar_actualizacion()")
idx4 = code.find("def progreso_actualizacion()")
if idx3 != -1 and idx4 != -1 and idx3 < idx4:
    new_apply = 'def aplicar_actualizacion():\n'
    new_apply += '        """Descarga e instala actualizacion. gh CLI o REST API."""\n'
    new_apply += '        if not es_admin_actual():\n'
    new_apply += '            return jsonify({"error": "No autorizado"}), 403\n'
    new_apply += '        try:\n'
    new_apply += '            import subprocess, tempfile, urllib.request, ssl\n'
    new_apply += '            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n'
    new_apply += '            ps1 = os.path.join(root, "actualizar.ps1")\n'
    new_apply += '            repo = app.config.get("INFORME_REPO", "jacj01/informe-mensual-obra")\n'
    new_apply += '            local_v = app.config.get("INFORME_VERSION", "1.0.0")\n'
    new_apply += '\n'
    new_apply += '            tag = ""\n'
    new_apply += '            try:\n'
    new_apply += '                cmd = ["gh", "-R", repo, "release", "view", "--json", "tagName"]\n'
    new_apply += '                out = subprocess.run(cmd, capture_output=True, text=True, timeout=15,\n'
    new_apply += '                                     creationflags=0x08000000)\n'
    new_apply += '                if out.returncode == 0:\n'
    new_apply += '                    tag = json.loads(out.stdout).get("tagName", "")\n'
    new_apply += '            except Exception:\n'
    new_apply += '                pass\n'
    new_apply += '            if not tag:\n'
    new_apply += '                try:\n'
    new_apply += '                    api_url = "https://api.github.com/repos/" + repo + "/releases/latest"\n'
    new_apply += '                    req = urllib.request.Request(api_url)\n'
    new_apply += '                    req.add_header("Accept", "application/vnd.github+json")\n'
    new_apply += '                    req.add_header("User-Agent", "InformeObra/1.0")\n'
    new_apply += '                    ctx = ssl.create_default_context()\n'
    new_apply += '                    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:\n'
    new_apply += '                        tag = json.loads(resp.read().decode()).get("tag_name", "")\n'
    new_apply += '                except Exception:\n'
    new_apply += '                    pass\n'
    new_apply += '\n'
    new_apply += '            if not tag:\n'
    new_apply += '                return jsonify({"ok": False, "error": "No se pudo conectar con GitHub."}), 400\n'
    new_apply += '\n'
    new_apply += '            tmp_dir = tempfile.mkdtemp(prefix="informe_upd_")\n'
    new_apply += '            zip_path = None\n'
    new_apply += '            try:\n'
    new_apply += '                r = subprocess.run(["gh", "-R", repo, "release", "download", tag,\n'
    new_apply += '                                    "--pattern", "*.zip", "--dir", tmp_dir],\n'
    new_apply += '                                   capture_output=True, text=True, timeout=120,\n'
    new_apply += '                                   creationflags=0x08000000)\n'
    new_apply += '                if r.returncode == 0:\n'
    new_apply += '                    zips = [f for f in os.listdir(tmp_dir) if f.endswith(".zip")]\n'
    new_apply += '                    if zips:\n'
    new_apply += '                        zip_path = os.path.join(tmp_dir, zips[0])\n'
    new_apply += '            except Exception:\n'
    new_apply += '                zip_path = None\n'
    new_apply += '            if not zip_path:\n'
    new_apply += '                try:\n'
    new_apply += '                    api_dl = "https://api.github.com/repos/" + repo + "/releases/tags/" + tag\n'
    new_apply += '                    req2 = urllib.request.Request(api_dl)\n'
    new_apply += '                    req2.add_header("Accept", "application/vnd.github+json")\n'
    new_apply += '                    req2.add_header("User-Agent", "InformeObra/1.0")\n'
    new_apply += '                    ctx2 = ssl.create_default_context()\n'
    new_apply += '                    with urllib.request.urlopen(req2, timeout=15, context=ctx2) as resp2:\n'
    new_apply += '                        rel = json.loads(resp2.read().decode())\n'
    new_apply += '                    zip_asset = next((a for a in rel.get("assets", [])\n'
    new_apply += '                                      if a.get("name", "").endswith(".zip")), None)\n'
    new_apply += '                    if zip_asset:\n'
    new_apply += '                        dl_url = zip_asset.get("browser_download_url")\n'
    new_apply += '                        req3 = urllib.request.Request(dl_url)\n'
    new_apply += '                        req3.add_header("User-Agent", "InformeObra/1.0")\n'
    new_apply += '                        with urllib.request.urlopen(req3, timeout=120, context=ctx2) as dl:\n'
    new_apply += '                            zip_path = os.path.join(tmp_dir, zip_asset["name"])\n'
    new_apply += '                            with open(zip_path, "wb") as f:\n'
    new_apply += '                                while True:\n'
    new_apply += '                                    chunk = dl.read(65536)\n'
    new_apply += '                                    if not chunk:\n'
    new_apply += '                                        break\n'
    new_apply += '                                    f.write(chunk)\n'
    new_apply += '                except Exception:\n'
    new_apply += '                    zip_path = None\n'
    new_apply += '\n'
    new_apply += '            if not zip_path:\n'
    new_apply += '                return jsonify({"ok": False, "error": "No se pudo descargar."}), 400\n'
    new_apply += '\n'
    new_apply += '            ps_args = ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden",\n'
    new_apply += '                       "-ExecutionPolicy", "Bypass", "-File", ps1, "-Instalar",\n'
    new_apply += '                       "-VersionLocal", local_v, "-ZipFile", zip_path]\n'
    new_apply += '            subprocess.Popen(ps_args, cwd=root,\n'
    new_apply += '                             creationflags=0x08000800,\n'
    new_apply += '                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,\n'
    new_apply += '                             stderr=subprocess.DEVNULL)\n'
    new_apply += '            return jsonify({"ok": True, "msg": "Actualizacion iniciada."})\n'
    new_apply += '        except Exception as e:\n'
    new_apply += '            return jsonify({"ok": False, "error": str(e)}), 500\n'
    new_apply += '\n'
    code = code[:idx3] + new_apply + code[idx4:]
    changes += 1
    print("[OK] aplicar_actualizacion")

with open(APP_PY, "w", encoding="utf-8") as f:
    f.write(code)

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
    changes += 1
    print("[OK] base.html")
else:
    print("[SKIP] base.html ya parcheado")

print("Cambios: " + str(changes))
print("Listo. Reinicie el servidor manualmente.")
