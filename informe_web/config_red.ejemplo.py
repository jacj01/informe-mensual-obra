# Configuracion de red del aplicativo (Administrador / Cliente).
# EJEMPLO de configuracion: copie este archivo como "config_red.py" y ajuste
# los valores. El instalador (Inno Setup) genera config_red.py automaticamente
# segun el tipo de instalacion elegida (Administrador o Cliente).

# MODO = "administrador" -> equipo principal: aloja la base de datos y el servidor.
# MODO = "cliente"       -> equipo que solo se conecta al servidor del Administrador.
MODO = "administrador"

# URL del servidor. Solo se usa en modo cliente. Ejemplos:
#   http://127.0.0.1:5000            (misma maquina, por defecto)
#   http://192.168.1.70:5000         (otro equipo de la misma red local)
#   http://100.64.0.3:5000           (otro equipo por Tailscale)
# En el Administrador esta URL se ignora (el servidor siempre escucha en 0.0.0.0).
SERVIDOR_URL = "http://127.0.0.1:5000"