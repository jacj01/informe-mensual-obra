# ============================================================================
# Configuracion SMTP para el envio de reportes de errores (Bugs).
#
# Copie este archivo como:  config_correo.py
# y complete los datos reales. config_correo.py (sin 'ejemplo') NO se sube a
# GitHub, por lo que sus credenciales quedan privadas en esta maquina.
#
# Para enviar por Gmail necesita una "contrasena de aplicacion" de Google:
#   Account > Seguridad > Verificacion en 2 pasos > Contrasenas de aplicaciones
# ============================================================================

# Servidor SMTP (Gmail por defecto)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Correo remitente (usuario SMTP) y su contrasena de aplicacion.
SMTP_USUARIO = ""   # ej: mi.correo@gmail.com
SMTP_CLAVE = ""     # contrasena de aplicacion de 16 caracteres

# Correo al que se envian los reportes de errores.
CORREO_DESTINO = "ingcpa.sac@gmail.com"
