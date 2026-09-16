"""Servidor de Informe Mensual de Obra ejecutado SIN ventana de consola.

Se lanza con pythonw.exe (sin consola) y registra toda la salida en
informe_web/servidor.log. El PID se guarda en informe_web/servidor.pid
para poder detenerlo con detener_servidor.bat.

Abre el navegador por si mismo en cuanto el servidor responde, de modo que
el lanzador (iniciar_sin_consola.vbs) no necesita esperas fijas ni sondeos.

Tambien admite modo CLIENTE (ver config_red.py): el equipo no aloja servidor
ni base de datos, solo abre el navegador apuntando al servidor del Administrador.
"""
import logging
import os
import socket
import subprocess
import sys
import threading
import time
from ctypes import windll, wintypes
from pathlib import Path
from urllib.request import urlopen

BASE = Path(__file__).resolve().parent
LOG = BASE / "servidor.log"
PID = BASE / "servidor.pid"

from red_util import es_cliente, servidor_url  # noqa: E402

logging.basicConfig(
    filename=LOG,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("servidor")

host = os.environ.get("HOST", "0.0.0.0")
port = int(os.environ.get("PORT", "5000"))
URL = f"http://127.0.0.1:{port}"


def servidor_sano():
    """True si ya hay un servidor respondiendo correctamente."""
    try:
        with urlopen(f"{URL}/robots.txt", timeout=1) as r:
            return r.status == 200
    except Exception:
        return False


def abrir_navegador(url):
    # Abre el navegador sin ventana de consola cmd visible.
    # Estrategia (Windows): reusar la instancia del browser ya abierta enviandole
    # la URL como nueva pestaña (--new-tab). Si el browser ya corre, NO se lanza
    # un proceso nuevo -> no aparece cmd/explorer ni la consola lenta del launcher
    # del browser (caso tipico de Edge/Chrome al primer arranque).
    # Si no hay instancia corriendo, se usa ShellExecuteW con SW_HIDE (oculto).
    if os.name == "nt":
        try:
            import subprocess as _sp
            for exe in ("msedge.exe", "chrome.exe", "firefox.exe"):
                cmd = _sp.run(["tasklist", "/FI", "IMAGENAME eq " + exe, "/FO", "CSV", "/NH"],
                              capture_output=True, text=True, timeout=5)
                if exe in (cmd.stdout or ""):
                    args = [exe, "--new-tab", url] if exe != "firefox.exe" else [exe, url]
                    _sp.Popen(args, creationflags=0x08000000)  # CREATE_NO_WINDOW
                    return
        except Exception:
            pass
        try:
            res = windll.shell32.ShellExecuteW(None, "open", url, None, None, 0)
            if res > 32:
                return
        except Exception:
            pass
    try:
        import webbrowser
        webbrowser.open(url, new=2)
    except Exception:
        log.exception("No se pudo abrir el navegador")


def servidor_remoto_sano(url):
    """True si el servidor remoto (modo cliente) responde correctamente."""
    try:
        with urlopen(f"{url}/robots.txt", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def preguntar_reintentar(url):
    """Muestra un aviso al usuario (modo cliente) y devuelve True si reintentar."""
    if os.name != "nt":
        return False
    try:
        mensaje = (
            "No se pudo conectar con el servidor de Informe Mensual de Obra:\n\n"
            f"    {url}\n\n"
            "Asegurese de que el equipo Administrador este encendido y de que\n"
            "ambos equipos esten en la misma red (LAN, Wi-Fi o Tailscale).\n\n"
            "Haga clic en 'Si' para volver a intentarlo."
        )
        res = windll.user32.MessageBoxW(
            0, mensaje, "Informe Mensual de Obra - Cliente",
            0x24)  # MB_YESNO | MB_ICONQUESTION
        return res == 6  # IDYES
    except Exception:
        return False


def abrir_cliente():
    """Modo CLIENTE: espera a que el servidor del Administrador responda y abre
    el navegador. No inicia servidor local ni toca la base de datos."""
    url = servidor_url()
    log.info("Modo CLIENTE: conectando con %s", url)
    while True:
        for _ in range(60):  # hasta ~120 s por intento
            if servidor_remoto_sano(url):
                log.info("Servidor alcanzado; abriendo navegador en %s", url)
                abrir_navegador(url)
                return 0
            time.sleep(2)
        if not preguntar_reintentar(url):
            return 3


def detener_anterior():
    """Detiene una instancia previa del servidor si sigue activa."""
    if PID.exists():
        try:
            old = int(PID.read_text().strip())
        except (ValueError, OSError):
            old = None
        if old and old != os.getpid():
            try:
                subprocess.run(["taskkill", "/PID", str(old), "/F"],
                               capture_output=True, check=False,
                               creationflags=0x08000000)
                log.info("Instancia anterior detenida (PID %s)", old)
            except Exception:
                pass


def puerto_en_uso(host_, port_):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.bind((host_, port_))
            return False
        except OSError:
            return True
        finally:
            s.close()
    except Exception:
        return False


def esperar_y_abrir():
    """Abre el navegador en cuanto el servidor responde (sin demora fija)."""
    for _ in range(120):
        if servidor_sano():
            abrir_navegador(URL)
            return
        time.sleep(0.1)


def main():
    # Modo CLIENTE: este equipo no aloja el servidor ni la BD.
    if es_cliente():
        sys.exit(abrir_cliente())

    # Ya hay un servidor sano: solo abre el navegador (inicio casi instantaneo).
    if servidor_sano():
        log.info("Servidor ya activo; abriendo navegador.")
        abrir_navegador(URL)
        return

    detener_anterior()

    if puerto_en_uso(host, port):
        if servidor_sano():
            abrir_navegador(URL)
            return
        log.error("El puerto %s ya esta en uso (algun servidor previo lo ocupa). "
                  "Cierre los navegadores y ejecute detener_servidor.bat.", port)
        sys.exit(2)

    with open(PID, "w") as f:
        f.write(str(os.getpid()))
    log.info("Arrancando servidor (oculto) PID=%s", os.getpid())

    if str(BASE) not in sys.path:
        sys.path.insert(0, str(BASE))
    from waitress import serve  # noqa: E402
    from app import app  # noqa: E402

    threading.Thread(target=esperar_y_abrir, daemon=True).start()

    log.info("Waitress escuchando en %s:%s", host, port)
    try:
        serve(app, host=host, port=port, threads=8, connection_limit=128)
    except Exception:
        log.exception("El servidor se detuvo por un error")
        sys.exit(1)
    finally:
        try:
            PID.unlink()
        except OSError:
            pass
        log.info("Servidor detenido")


if __name__ == "__main__":
    main()
