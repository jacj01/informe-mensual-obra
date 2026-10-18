"""Paletas de color del aplicativo.

Cada tema redefine las variables CSS de marca (--azul, --azul-osc,
--azul-claro/--super-azul, --oro y --bg) para que se apliquen a toda la
interfaz y a las hojas de impresion, que comparten esas variables.  La misma
paleta alimenta los colores de las hojas exportadas a Excel (ver paleta_excel).

La clave "" corresponde al aspecto institucional por defecto (los mismos
valores que ya traia style.css y print.css), de modo que las instalaciones
existentes no cambian de color salvo que el usuario elija otra paleta.
"""

# Orden de aparicion en el selector: primero el predeterminado.
# Cada paleta son 5 muestras: [mas oscuro, oscuro, acento, tinte, mas claro].
TEMAS = {
    "": {
        "nombre": "Azul institucional",
        "swatches": ["#1E3A5F", "#2C527A", "#C9A227"],
        "azul_osc": "#162D45",
        "azul": "#1E3A5F",
        "azul_claro": "#2C527A",
        "oro": "#C9A227",
        "bg": "#F8FAFC",
    },
    "libro_mayor": {
        "nombre": "Azul marino libro mayor",
        "swatches": ["#0B1F3B", "#123A63", "#2F5D8C", "#C9D6E5", "#F2F5F8"],
        "azul_osc": "#0B1F3B",
        "azul": "#123A63",
        "azul_claro": "#2F5D8C",
        "oro": "#2F5D8C",
        "bg": "#F2F5F8",
    },
    "boveda": {
        "nombre": "Verde bóveda",
        "swatches": ["#0E3B2E", "#1F6F54", "#5FB88A", "#D7E7DD", "#F6FBF7"],
        "azul_osc": "#0E3B2E",
        "azul": "#1F6F54",
        "azul_claro": "#5FB88A",
        "oro": "#5FB88A",
        "bg": "#F6FBF7",
    },
    "cobre": {
        "nombre": "Auditoría cobre",
        "swatches": ["#2C2A28", "#6B5A4D", "#B87333", "#E7D4C2", "#FBF4EE"],
        "azul_osc": "#2C2A28",
        "azul": "#6B5A4D",
        "azul_claro": "#B87333",
        "oro": "#B87333",
        "bg": "#FBF4EE",
    },
    "platino": {
        "nombre": "Estado de platino",
        "swatches": ["#0F172A", "#4B5563", "#9CA3AF", "#E5E7EB", "#FFFFFF"],
        "azul_osc": "#0F172A",
        "azul": "#4B5563",
        "azul_claro": "#9CA3AF",
        "oro": "#9CA3AF",
        "bg": "#FFFFFF",
    },
    "arenisca": {
        "nombre": "Presupuesto arenisca",
        "swatches": ["#3A2F2A", "#7A6A5A", "#C2B59B", "#E8E1D4", "#FAF7F1"],
        "azul_osc": "#3A2F2A",
        "azul": "#7A6A5A",
        "azul_claro": "#C2B59B",
        "oro": "#C2B59B",
        "bg": "#FAF7F1",
    },
    "medianoche": {
        "nombre": "Hoja de cálculo medianoche",
        "swatches": ["#0A0F1E", "#1B2A41", "#3B82F6", "#94A3B8", "#E2E8F0"],
        "azul_osc": "#0A0F1E",
        "azul": "#1B2A41",
        "azul_claro": "#3B82F6",
        "oro": "#3B82F6",
        "bg": "#E2E8F0",
    },
    "esmeralda": {
        "nombre": "Equidad esmeralda",
        "swatches": ["#052E2B", "#0F766E", "#34D399", "#A7F3D0", "#ECFDF5"],
        "azul_osc": "#052E2B",
        "azul": "#0F766E",
        "azul_claro": "#34D399",
        "oro": "#34D399",
        "bg": "#ECFDF5",
    },
    "grafito": {
        "nombre": "Reserva grafito",
        "swatches": ["#111827", "#374151", "#6B7280", "#D1D5DB", "#F9FAFB"],
        "azul_osc": "#111827",
        "azul": "#374151",
        "azul_claro": "#6B7280",
        "oro": "#6B7280",
        "bg": "#F9FAFB",
    },
    "bluechip": {
        "nombre": "Pizarra Bluechip",
        "swatches": ["#0F1B2D", "#1E3A8A", "#60A5FA", "#E0F2FE", "#F8FAFF"],
        "azul_osc": "#0F1B2D",
        "azul": "#1E3A8A",
        "azul_claro": "#60A5FA",
        "oro": "#60A5FA",
        "bg": "#F8FAFF",
    },
    "oliva": {
        "nombre": "Enlace Oliva",
        "swatches": ["#1F2A1E", "#3E5A3C", "#8AAE6D", "#DCE6D6", "#F6FAF3"],
        "azul_osc": "#1F2A1E",
        "azul": "#3E5A3C",
        "azul_claro": "#8AAE6D",
        "oro": "#8AAE6D",
        "bg": "#F6FAF3",
    },
    "oro_rosado": {
        "nombre": "Pronóstico Oro Rosado",
        "swatches": ["#2A1F25", "#7A4B57", "#D08C9B", "#F1D6DC", "#FFF6F8"],
        "azul_osc": "#2A1F25",
        "azul": "#7A4B57",
        "azul_claro": "#D08C9B",
        "oro": "#D08C9B",
        "bg": "#FFF6F8",
    },
    "plateado": {
        "nombre": "Interés Plateado",
        "swatches": ["#0B1220", "#334155", "#94A3B8", "#E2E8F0", "#FFFFFF"],
        "azul_osc": "#0B1220",
        "azul": "#334155",
        "azul_claro": "#94A3B8",
        "oro": "#94A3B8",
        "bg": "#FFFFFF",
    },
    "portafolio": {
        "nombre": "Portafolio Dorado",
        "swatches": ["#101418", "#2C3E50", "#B08D57", "#DCC9A6", "#FBF6EE"],
        "azul_osc": "#101418",
        "azul": "#2C3E50",
        "azul_claro": "#B08D57",
        "oro": "#B08D57",
        "bg": "#FBF6EE",
    },
    "puerto": {
        "nombre": "Balance Puerto",
        "swatches": ["#061A24", "#0B3A53", "#0FA3B1", "#B5E2FA", "#F3FAFF"],
        "azul_osc": "#061A24",
        "azul": "#0B3A53",
        "azul_claro": "#0FA3B1",
        "oro": "#0FA3B1",
        "bg": "#F3FAFF",
    },
}


def _rgb(hexcolor):
    """'#3B82F6' -> '59, 130, 246' (para usar dentro de rgba(var(--x), a))."""
    h = (hexcolor or "").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "%d, %d, %d" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def variables(clave):
    """Diccionario {variable_css: valor} del tema indicado."""
    t = TEMAS.get(clave) or TEMAS[""]
    return {
        "--azul-osc": t["azul_osc"],
        "--azul": t["azul"],
        "--azul-claro": t["azul_claro"],
        "--super-azul": t["azul_claro"],
        "--oro": t["oro"],
        "--bg": t["bg"],
        "--azul-rgb": _rgb(t["azul"]),
        "--oro-rgb": _rgb(t["oro"]),
    }


def css(clave):
    """Bloque <style> con las variables del tema, para inyectar en el <head>."""
    cuerpo = "".join("%s:%s;" % (k, v) for k, v in variables(clave).items())
    return "<style id=\"tema-app\">:root{%s}</style>" % cuerpo


def ui():
    """Lista de temas para dibujar el selector: clave, nombre y muestras."""
    return [{"clave": k, "nombre": t["nombre"], "swatches": t["swatches"]}
            for k, t in TEMAS.items()]


def datos_js():
    """Mapa para aplicar el tema en vivo desde JavaScript sin recargar."""
    salida = {}
    for k, t in TEMAS.items():
        v = variables(k)
        salida[k] = {
            "nombre": t["nombre"],
            "swatches": t["swatches"],
            "azul": v["--azul"],
            "azul_osc": v["--azul-osc"],
            "azul_claro": v["--azul-claro"],
            "oro": v["--oro"],
            "bg": v["--bg"],
            "azul_rgb": v["--azul-rgb"],
            "oro_rgb": v["--oro-rgb"],
            "grafico": grafico(k),
        }
    return salida


# ---- Colores para las hojas exportadas a Excel (openpyxl) ----------------

# Valores del aspecto institucional por defecto (identicos a los que ya usaban
# los exportadores, para no alterar el Excel del tema predeterminado).
_EXCEL_DEFAULT = {
    "AZUL": "1E3A5F",
    "AZUL_OSC": "162D45",
    "AZUL_CLARO": "2C527A",
    "BG": "F8FAFC",
    "BLANCO": "FFFFFF",
    "BORDE": "CBD5E1",
    "TEXTO2": "64748B",
    "BORDE2": "E2E8F0",
    "TINTE": "E8EDF3",
    "TINTE_FUERTE": "D9E1E8",
}


def _to_rgb(h):
    """'#0B1F3B' -> (11, 31, 59)."""
    h = (h or "").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _blend(base, otro, peso):
    """Mezcla dos colores hex; 'peso' (0..1) es el peso del segundo color."""
    a, b = _to_rgb(base), _to_rgb(otro)
    vals = [round(a[i] * (1 - peso) + b[i] * peso) for i in range(3)]
    return "%02X%02X%02X" % tuple(vals)


def paleta_excel(clave):
    """Colores del tema listos para openpyxl (hex sin '#', en mayusculas).

    Deriva los tonos suaves (tintes y bordes) de la propia paleta para que la
    hoja de calculo combine con el color elegido en la aplicacion.
    """
    if clave not in TEMAS or clave == "":
        return dict(_EXCEL_DEFAULT)
    t = TEMAS[clave]
    azul = t["azul"].lstrip("#").upper()
    osc = t["azul_osc"].lstrip("#").upper()
    claro = t["azul_claro"].lstrip("#").upper()
    bg = t["bg"].lstrip("#").upper()
    return {
        "AZUL": azul,
        "AZUL_OSC": osc,
        "AZUL_CLARO": claro,
        "BG": bg,
        "BLANCO": "FFFFFF",
        "BORDE": _blend(osc, "#FFFFFF", 0.80),
        "TEXTO2": _blend(osc, "#FFFFFF", 0.45),
        "BORDE2": _blend(osc, "#FFFFFF", 0.86),
        "TINTE": _blend(azul, "#FFFFFF", 0.88),
        "TINTE_FUERTE": _blend(azul, "#FFFFFF", 0.78),
    }


# Paleta categorica original de las graficas (tema predeterminado).  Se
# conserva intacta para no alterar el aspecto de las instalaciones existentes.
_GRAFICO_DEFAULT = ["#1F4E79", "#C9A227", "#2E8B57", "#8E44AD", "#E67E22"]


def grafico(clave):
    """Paleta categorica derivada del tema, para las graficas.

    Siempre devuelve 8 colores distintos.  En varias paletas ``azul_claro`` y
    ``oro`` son el mismo tono; en ese caso se generan tonos intermedios para
    que ninguna tajada del grafico quede del mismo color que su vecina.
    """
    if clave == "":
        return list(_GRAFICO_DEFAULT)
    t = TEMAS.get(clave) or TEMAS[""]
    azul, claro, oro, osc = t["azul"], t["azul_claro"], t["oro"], t["azul_osc"]
    mismo = claro.upper() == oro.upper()
    c2 = "#" + _blend(azul, oro, 0.55) if mismo else oro
    c6 = "#" + _blend(oro, "#FFFFFF", 0.30) if mismo else "#" + _blend(oro, "#FFFFFF", 0.45)
    c8 = "#" + _blend(osc, oro, 0.45) if mismo else "#" + _blend(oro, "#000000", 0.30)
    return [
        azul,
        c2,
        claro,
        osc,
        "#" + _blend(azul, "#FFFFFF", 0.45),
        c6,
        "#" + _blend(claro, "#000000", 0.30),
        c8,
    ]
