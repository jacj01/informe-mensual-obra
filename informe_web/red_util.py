# Utilidades para el modo red del aplicativo (Administrador / Cliente).

# El aplicativo puede instalarse en dos modos:
#   - "administrador": equipo principal que aloja la base de datos y el
#     servidor web. Todos los demas equipos (clientes) se conectan a este.
#   - "cliente": equipo terminal que solo abre el navegador apuntando al
#     servidor del Administrador (en la misma red local o por Tailscale);
#     en modo cliente NO se crea base de datos ni se inicia un servidor local.

# La configuracion se lee de "config_red.py", que es generado por el
# instalador (Inno Setup) segun el tipo de instalacion elegida. Si el archivo
# no existe o esta mal formado, se asume modo administrador (comportamiento
# historico del aplicativo).
from pathlib import Path

_BASE = Path(__file__).resolve().parent
_CONFIG = _BASE / "config_red.py"

_DEFECTO = {
    "MODO": "administrador",
    "SERVIDOR_URL": "http://127.0.0.1:5000",
}


def config_red():
    """Devuelve el dict {MODO, SERVIDOR_URL} vigente (con valores seguros)."""
    cfg = dict(_DEFECTO)
    if _CONFIG.exists():
        try:
            ns = {}
            exec(compile(_CONFIG.read_text(encoding="utf-8-sig"), str(_CONFIG), "exec"), ns)
            modo = str(ns.get("MODO", "")).strip().lower()
            if modo in ("administrador", "cliente"):
                cfg["MODO"] = modo
            url = str(ns.get("SERVIDOR_URL", "")).strip().rstrip("/")
            if url:
                cfg["SERVIDOR_URL"] = url
        except Exception:
            pass  # configuracion invalida: usar valores por defecto
    return cfg


def es_cliente():
    """True si esta instalacion esta configurada como equipo cliente."""
    return config_red()["MODO"] == "cliente"


def servidor_url():
    """URL a la que debe conectarse este equipo (modo cliente)."""
    return config_red()["SERVIDOR_URL"]


if __name__ == "__main__":
    # Salida para los lanzadores .bat: "modo|url" (sin comillas anidadas).
    cfg = config_red()
    print(f"{cfg['MODO']}|{cfg['SERVIDOR_URL']}")