# -*- coding: utf-8 -*-
"""Diagnostico v2: muestra contexto exacto de los decoradores."""
import os

BAK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_patch_backup", "app.py.bak")
with open(BAK, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Buscar lineas con @app.route que contengan "actualizacion" o "actualizar"
for i, line in enumerate(lines):
    s = line.strip()
    if "@app.route" in s and ("actualizacion" in s or "actualizar" in s):
        print("Line %d: %s" % (i+1, s))

# Mostrar 5 lineas antes y despues de api_actualizacion
for i, line in enumerate(lines):
    if "def api_actualizacion" in line:
        print("\n--- Contexto api_actualizacion (line %d) ---" % (i+1))
        for j in range(max(0,i-5), min(len(lines), i+3)):
            print("%d: %s" % (j+1, lines[j].rstrip()))
        break

# Mostrar 5 lineas antes y despues de aplicar_actualizacion
for i, line in enumerate(lines):
    if "def aplicar_actualizacion" in line:
        print("\n--- Contexto aplicar_actualizacion (line %d) ---" % (i+1))
        for j in range(max(0,i-3), min(len(lines), i+3)):
            print("%d: %s" % (j+1, lines[j].rstrip()))
        break

# Mostrar 3 lineas antes de progreso_actualizacion
for i, line in enumerate(lines):
    if "def progreso_actualizacion" in line:
        print("\n--- Contexto progreso_actualizacion (line %d) ---" % (i+1))
        for j in range(max(0,i-5), min(len(lines), i+3)):
            print("%d: %s" % (j+1, lines[j].rstrip()))
        break
