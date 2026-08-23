# -*- coding: utf-8 -*-
import os, re

BAK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_patch_backup", "app.py.bak")
with open(BAK, "r", encoding="utf-8") as f:
    c = f.read()

i = c.find("def api_actualizacion")
k = c.find("def aplicar_actualizacion")
j = c.find("def progreso_actualizacion")

print("Total chars:", len(c))
print("api_actualizacion at:", i)
print("aplicar_actualizacion at:", k)
print("progreso_actualizacion at:", j)

if i > 0:
    block = c[i:k] if k > i else c[i:i+500]
    lines = block.split("\n")
    print("\n--- api_actualizacion block (%d lines) ---" % len(lines))
    print("First line:", repr(lines[0][:80]))
    print("Last line:", repr(lines[-1][:80]))

if j > 0:
    print("\n--- 200 chars before progreso ---")
    print(repr(c[j-200:j]))

# Find all route decorators between api_actualizacion and progreso
routes = re.findall(r'@app\.route\([^\n]*\)', c[i:j] if j > i else "")
print("\nRoutes between api_actualizacion and progreso:")
for r in routes:
    print(" ", r)
