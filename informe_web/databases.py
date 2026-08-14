"""Gestión de bases de datos del aplicativo (multi-base).

Estructura:
  - BASE MAESTRA (instance/informe.db): cuentas globales (Super Usuario y
    Administradores) y la suscripción/licencia.
  - BASE POR ADMINISTRADOR (instance/datos/admin_<id>/informe.db): los datos
    de proyecto de cada Administrador (cabecera, presupuesto, gastos, almacén
    y planilla) junto con sus operadores (rol Usuario).

La base maestra también respeta INFORME_DB (usado en pruebas) y los datos de
cada administrador se guardan en INFORME_DATOS_DIR (también aislable en
pruebas).
"""
import os

from sqlalchemy import create_engine, text
import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker

from models import db

# Base por Administrador: las columnas nuevas de las tablas de negocio se
# alinean en cada base tenant con _alinear_tabla (según el modelo SQLAlchemy).

_BASE = os.path.dirname(os.path.abspath(__file__))
_DEFECTO_MAESTRA = "sqlite:///" + os.path.join(_BASE, "instance", "informe.db")
DATOS_DIR = (os.environ.get("INFORME_DATOS_DIR")
             or os.path.join(_BASE, "instance", "datos"))

# Tablas que solo existen en la base maestra (globales).
TABLAS_MAESTRAS = {"usuario", "suscripcion", "suscripcion_historial",
                   "licencias_usadas"}
# Tablas de negocio: propias de cada Administrador (se descubren una sola vez).
TABLAS_NEGOCIO = []

master_engine = None
master_session = None
_tenants = {}


def master_url():
    """URI SQLite de la base maestra (INFORME_DB permite otra, p.ej. en pruebas)."""
    return os.environ.get("INFORME_DB") or _DEFECTO_MAESTRA


def master_path():
    """Ruta del archivo de la base maestra."""
    uri = master_url()
    if uri.startswith("sqlite:///"):
        return uri[len("sqlite:///"):]
    return uri


def _descubrir_tablas():
    if not TABLAS_NEGOCIO:
        for t in db.metadata.tables:
            if t not in TABLAS_MAESTRAS:
                TABLAS_NEGOCIO.append(t)
    return TABLAS_NEGOCIO


def tablas_negocio():
    """Nombres de las tablas de negocio (las que se aíslan por Administrador)."""
    return _descubrir_tablas()


def tablas_tenant():
    """Objetos Table que debe contener la base de un Administrador."""
    _descubrir_tablas()
    return [db.metadata.tables[t] for t in TABLAS_NEGOCIO
            if t != "usuario"] + [db.metadata.tables["usuario"]]


def tablas_maestras():
    """Objetos Table que viven solo en la base maestra (cuentas y suscripción)."""
    return [db.metadata.tables[t] for t in sorted(TABLAS_MAESTRAS)
            if t in db.metadata.tables]


def tenant_path(admin_id):
    """Ruta del archivo SQLite de un Administrador."""
    return os.path.join(DATOS_DIR, f"admin_{admin_id}", "informe.db")


def init_databases():
    """Prepara el motor maestra y una sesión dedicada a cuentas/suscripción.

    Debe llamarse dentro de un contexto de aplicación tras db.init_app().
    """
    global master_engine, master_session
    if master_engine is None:
        master_engine = db.engine
        master_session = scoped_session(sessionmaker(bind=master_engine))
    return master_engine, master_session


def tenant_engine(admin_id):
    """Motor (en caché) de la base de datos de un Administrador."""
    eng = _tenants.get(admin_id)
    if eng is None:
        ruta = tenant_path(admin_id)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        eng = create_engine("sqlite:///" + ruta)
        _tenants[admin_id] = eng
    return eng


def _migrar_esquema_usuario(eng):
    """Alinea la tabla usuario del tenant con el modelo Usuario.

    Las bases creadas antes de la licencia por Administrador carecen de estas
    columnas y las consultas ORM del modelo Usuario (p.ej. la búsqueda de
    operadores al iniciar sesión) fallarían al seleccionarlas.
    """
    _alinear_tabla(eng, "usuario")


def _migrar_esquema_trabajador(eng):
    """Alinea la tabla trabajador del tenant con el modelo Trabajador.

    Las bases creadas antes de la planilla de pagos (sueldo mensual del
    personal técnico/administrativo, D.L. 728) carecen de estas columnas y las
    consultas ORM del modelo Trabajador fallarían al seleccionarlas.
    """
    _alinear_tabla(eng, "trabajador")


def _migrar_esquema_proyecto(eng):
    """Alinea la tabla proyecto del tenant con el modelo Proyecto.

    Las bases creadas con versiones anteriores del aplicativo pueden carecer de
    columnas añadidas posteriormente (p.ej. clasificadores, personal técnico,
    fecha de resolución de aprobación). Se agregan las columnas faltantes con
    su tipo y valor por defecto según el modelo, para que las consultas ORM no
    fallen al seleccionarlas.
    """
    _alinear_tabla(eng, "proyecto")


def _alinear_tabla(eng, nombre):
    """Agrega a la tabla indicada las columnas del modelo que le falten.

    Compara el esquema real de la tabla del tenant contra el modelo SQLAlchemy
    y ejecuta ALTER TABLE ADD COLUMN por cada columna ausente, usando el tipo y
    el valor por defecto definidos en el modelo. Es idempotente.
    """
    if nombre not in db.metadata.tables:
        return
    tabla = db.metadata.tables[nombre]
    with eng.connect() as con:
        existe = con.execute(text(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=:t"
        ), {"t": nombre}).first()
        if not existe:
            return
        cols = [r[1] for r in con.execute(text(f"PRAGMA table_info({nombre})"))]
        faltan = [c for c in tabla.columns if c.name not in cols]
        if not faltan:
            return
        for col in faltan:
            tipo = _tipo_sql(col)
            dflt = col.default.arg if col.default is not None else None
            extra = ""
            if dflt is not None and isinstance(dflt, str):
                extra = f" DEFAULT '{dflt}'"
            elif dflt is not None:
                extra = f" DEFAULT {dflt}"
            con.execute(text(
                f"ALTER TABLE {nombre} ADD COLUMN {col.name} {tipo}{extra}"))
        con.commit()


def _migrar_esquema_resto(eng):
    """Alinea las demás tablas de negocio del tenant con sus modelos.

    Cubre las tablas de negocio que no tienen migración propia (gasto,
    gasto_detalle, presupuesto, almacen_movimiento, etc.) para que las bases
    restauradas de versiones anteriores queden sincronizadas con el esquema
    actual.
    """
    for nombre in db.metadata.tables:
        if nombre in TABLAS_MAESTRAS or nombre in ("usuario", "trabajador",
                                                    "proyecto"):
            continue
        _alinear_tabla(eng, nombre)


def _tipo_sql(col):
    """Tipo SQLite correspondiente a la columna del modelo SQLAlchemy."""
    t = col.type
    if isinstance(t, sa.String):
        return f"VARCHAR({t.length or 300})"
    if isinstance(t, sa.Text):
        return "TEXT"
    if isinstance(t, sa.Integer):
        return "INTEGER"
    if isinstance(t, sa.Float):
        return "REAL"
    if isinstance(t, sa.Boolean):
        return "BOOLEAN"
    if isinstance(t, sa.Date):
        return "DATE"
    return "TEXT"


def ensure_tenant(admin_id):
    """Crea (si no existe) la base del Administrador con sus tablas."""
    eng = tenant_engine(admin_id)
    db.metadata.create_all(bind=eng, tables=tablas_tenant())
    _migrar_esquema_usuario(eng)
    _migrar_esquema_trabajador(eng)
    _migrar_esquema_proyecto(eng)
    _migrar_esquema_resto(eng)
    return eng


def tenant_session(admin_id):
    """Sesión SQLAlchemy aislada para la base de un Administrador."""
    return sessionmaker(bind=tenant_engine(admin_id))()


def dispose_tenant(admin_id):
    """Libera el motor de la base de un Administrador (p.ej. tras restaurar)."""
    eng = _tenants.pop(admin_id, None)
    if eng is not None:
        eng.dispose()


def bind_session(engine):
    """Apunta la sesión ORM por defecto a un motor.

    Se invoca al inicio de cada petición con el motor correcto según la sesión
    del navegador (base del administrador o maestra).

    Flask-SQLAlchemy resuelve el bind de cada modelo desde ``db.engines``
    (ignora el ``bind`` del sessionmaker), por eso se reemplaza el motor por
    defecto (clave ``None``) y se descarta la sesión del hilo.
    """
    if engine is None:
        return
    try:
        db.engines[None] = engine
    except (RuntimeError, TypeError):
        pass
    db.session.remove()
