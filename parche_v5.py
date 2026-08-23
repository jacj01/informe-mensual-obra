# -*- coding: utf-8 -*-
"""
Parche v5: Restaura backup + reemplaza funciones desde archivo de texto.
Requiere: parche_v5.py y bloque_update.txt en C:\InformeObra\
"""
import os, shutil, sys, re

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_PY = os.path.join(ROOT, "informe_web", "app.py")
BASE_HTML = os.path.join(ROOT, "informe_web", "templates", "base.html")
BACKUP = os.path.join(ROOT, "_patch_backup")
BLOCK_FILE = os.path.join(ROOT, "bloque_update.txt")

print("=== Parche v5 ===")

# 1. Verificar archivos
bak = os.path.join(BACKUP, "app.py.bak")
if not os.path.exists(bak):
    print("ERROR: No hay backup en _patch_backup/app.py.bak")
    sys.exit(1)
if not os.path.exists(BLOCK_FILE):
    print("ERROR: Falta bloque_update.txt en " + ROOT)
    sys.exit(1)

# 2. Restaurar desde backup
shutil.copy2(bak, APP_PY)
print("[OK] app.py restaurado desde backup")

# 3. Leer bloque correcto
with open(BLOCK_FILE, "r", encoding="utf-8") as f:
    correct_block = f.read()

# 4. Leer app.py restaurado
with open(APP_PY, "r", encoding="utf-8") as f:
    code = f.read()

# 5. Encontrar el bloque viejo: desde @app.route("/api/actualizacion") hasta justo antes de @app.route("/api/actualizacion/progreso")
pattern = re.compile(
    r'    @app\.route\("/api/actualizacion"\).*?(?=\n    @app\.route\("/api/actualizacion/progreso"\))',
    re.DOTALL
)

match = pattern.search(code)
if not match:
    print("ERROR: No se encontro el bloque a reemplazar")
    print("Intentando busqueda alternativa...")
    idx1 = code.find('def api_actualizacion()')
    idx2 = code.find('def progreso_actualizacion()')
    if idx1 == -1 or idx2 == -1:
        print("ERROR: No se encontraron las funciones")
        sys.exit(1)
    # Encontrar inicio del decorador
    start = code.rfind("\n@", 0, idx1) + 1
    end = idx2
    while end > 0 and code[end - 1] in (" ", "\n", "\r"):
        end -= 1
    # Retroceder hasta el salto de linea anterior al decorador
    start = code.rfind("\n", 0, start) + 1
    old_block = code[start:end]
    line_start = code[:start].count("\n") + 1
    line_end = code[:end].count("\n") + 1
    print("[INFO] Bloque encontrado (alt): lineas %d - %d (%d chars)" % (line_start, line_end, len(old_block)))
    code = code[:start] + correct_block + code[end:]
else:
    line_start = code[:match.start()].count("\n") + 1
    line_end = code[:match.end()].count("\n") + 1
    print("[OK] Bloque encontrado: lineas %d - %d" % (line_start, line_end))
    code = code[:match.start()] + correct_block + code[match.end():]

# 6. Guardar
with open(APP_PY, "w", encoding="utf-8") as f:
    f.write(code)
print("[OK] Bloque reemplazado")

# 7. Parchar base.html
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

# 8. Verificar compilacion sintactica
import py_compile
try:
    py_compile.compile(APP_PY, doraise=True)
    print("[OK] app.py compila sin errores de sintaxis")
except py_compile.PyCompileError as e:
    print("[ERROR] Error de sintaxis: " + str(e))
    sys.exit(1)

# 9. Verificar regex
test = re.search(r"v?(\d+\.\d+\.\d+)", "v1.1.0-f51baf3")
if test:
    print("[OK] Regex: v1.1.0-f51baf3 -> " + test.group(1))

print("\nListo. Reinicie el servidor.")
