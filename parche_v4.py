# -*- coding: utf-8 -*-
"""
Parche v4: Restaura backup + pega el bloque EXACTO del archivo local.
No construye strings manualmente.
"""
import os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_PY = os.path.join(ROOT, "informe_web", "app.py")
BASE_HTML = os.path.join(ROOT, "informe_web", "templates", "base.html")
BACKUP = os.path.join(ROOT, "_patch_backup")

print("=== Parche v4 ===")

# 1. Restaurar desde backup
bak = os.path.join(BACKUP, "app.py.bak")
if not os.path.exists(bak):
    print("ERROR: No hay backup")
    sys.exit(1)
shutil.copy2(bak, APP_PY)
print("[OK] app.py restaurado")

# 2. Leer backup (con funciones viejas)
with open(APP_PY, "r", encoding="utf-8") as f:
    code = f.read()

# 3. Leer bloque correcto del archivo local (copiado directamente)
LOCAL_APP = r"C:\Users\JOHN\Documents\Informe Mensual\informe_web\app.py"
with open(LOCAL_APP, "r", encoding="utf-8") as f:
    local_lines = f.readlines()

# Lineas 1389-1571 (0-indexed: 1388-1570)
correct_block = "".join(local_lines[1388:1571])

# 4. Encontrar y reemplazar en el backup
# Buscar desde el decorador @app.route("/api/actualizacion") hasta justo antes de @app.route("/api/actualizacion/progreso")
import re

# Patron: desde "@app.route(\"/api/actualizacion\")" hasta "@app.route(\"/api/actualizacion/progreso\")"
pattern = re.compile(
    r'    @app\.route\("/api/actualizacion"\).*?'
    r'(?=    @app\.route\("/api/actualizacion/progreso"\))',
    re.DOTALL
)

match = pattern.search(code)
if not match:
    print("ERROR: No se encontro el bloque a reemplazar")
    sys.exit(1)

print(f"[INFO] Bloque encontrado: lineas {code[:match.start()].count(chr(10))+1} - {code[:match.end()].count(chr(10))+1}")

# Reemplazar
new_code = code[:match.start()] + correct_block + code[match.end():]

# 5. Guardar
with open(APP_PY, "w", encoding="utf-8") as f:
    f.write(new_code)
print("[OK] Bloque reemplazado")

# 6. Parchar base.html (error handling)
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

# 7. Verificar indentacion: buscar errores comunes
with open(APP_PY, "r", encoding="utf-8") as f:
    check = f.read()

lines = check.split("\n")
errors = []
for i, line in enumerate(lines[1380:1590], start=1381):
    if line.strip() and not line.startswith(" ") and not line.startswith("#"):
        if i > 1389 and "def " in line and not line.startswith("    def "):
            errors.append(f"Linea {i}: indentacion incorrecta: {line[:60]}")

if errors:
    print("[WARN] Posibles problemas de indentacion:")
    for e in errors:
        print("  " + e)
else:
    print("[OK] Sin problemas de indentacion detectados")

# 8. Verificar regex
test = re.search(r"v?(\d+\.\d+\.\d+)", "v1.1.0-f51baf3")
if test:
    print(f"[OK] Regex: v1.1.0-f51baf3 -> {test.group(1)}")

print("\nListo. Reinicie el servidor.")
