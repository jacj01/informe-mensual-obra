"""Modelos de datos para el informe financiero."""
import calendar
import json
from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Duración en meses de cada plan de suscripción.
PLANES_SUSCRIPCION = {
    "Mensual": 1,
    "Trimestral": 3,
    "Anual": 12,
}


def sumar_meses(fecha, meses):
    """Suma N meses calendario a una fecha (clamp al último día del mes)."""
    if not fecha:
        return None
    total = fecha.year * 12 + (fecha.month - 1) + meses
    anio, mes = divmod(total, 12)
    mes += 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)

COMPONENTES = [
    "Costo Directo", "Gastos Generales", "Gastos de Supervisión",
    "Elaboración de Expediente Técnico", "Liquidación de Obra",
]
CLASIFICADORES = {
    "2.6.2.3.99.3": "PERSONAL",
    "2.6.2.3.99.4": "BIENES",
    "2.6.2.3.99.5": "SERVICIOS",
    "2.6.8.1.3.1": "ELABORACION DE EXPEDIENTE TECNICO",
    "LIQUIDACION": "COSTO DE LIQUIDACION",
}


class Proyecto(db.Model):
    """Datos de cabecera del proyecto (hoja PRESENTACION)."""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(800), nullable=False, default="")
    cui = db.Column(db.String(50), default="")
    meta = db.Column(db.String(50), default="")
    distrito = db.Column(db.String(100), default="")
    provincia = db.Column(db.String(100), default="")
    departamento = db.Column(db.String(100), default="")
    entidad = db.Column(db.String(300), default="")
    unidad_ejecutora = db.Column(db.String(400), default="")
    aprobacion = db.Column(db.String(300), default="")
    fecha_aprobacion = db.Column(db.Date)
    rubro = db.Column(db.String(300), default="")
    fuente = db.Column(db.String(200), default="")
    presupuesto_total = db.Column(db.Float, default=0)
    costo_directo = db.Column(db.Float, default=0)
    gastos_generales = db.Column(db.Float, default=0)
    gastos_supervision = db.Column(db.Float, default=0)
    elaboracion_expediente = db.Column(db.Float, default=0)
    liquidacion_obra = db.Column(db.Float, default=0)
    residente = db.Column(db.String(300), default="")
    supervisor = db.Column(db.String(300), default="")
    asistente = db.Column(db.String(300), default="")
    almacenero = db.Column(db.String(300), default="")
    responsable_almacen = db.Column(db.String(300), default="")
    administrador_obra = db.Column(db.String(300), default="")
    anio = db.Column(db.Integer, default=2026)
    mes_actual = db.Column(db.Integer, default=6)
    incluir_anios_anteriores = db.Column(db.Boolean, default=True)
    num_anios_anteriores = db.Column(db.Integer, default=3)
    meta_ejec2023 = db.Column(db.Float, default=0)
    meta_ejec2024 = db.Column(db.Float, default=0)
    meta_ejec2025 = db.Column(db.Float, default=0)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    dias_ejecucion = db.Column(db.Integer, default=0)
    adicional_obra = db.Column(db.Boolean, default=False)
    adicionales = db.Column(db.Text, default="")
    dias_ampliacion = db.Column(db.Integer, default=0)
    nuevo_final_obra = db.Column(db.Date)
    n_resolucion_adicional = db.Column(db.String(200), default="")
    ampliacion_presupuestal = db.Column(db.Boolean, default=False)
    monto_ampliacion = db.Column(db.Float, default=0)
    clasificador_personal = db.Column(db.String(20), default="2.6.2.3.99.3")
    clasificador_bienes = db.Column(db.String(20), default="2.6.2.3.99.4")
    clasificador_servicios = db.Column(db.String(20), default="2.6.2.3.99.5")
    clasificador_expediente = db.Column(db.String(20), default="2.6.8.1.3.1")
    clasificador_liquidacion = db.Column(db.String(20), default="LIQUIDACION")
    clasificadores_extra = db.Column(db.Text, default="")
    logo_path = db.Column(db.String(500), default="")
    cip_supervisor = db.Column(db.String(50), default="")
    cip_residente = db.Column(db.String(50), default="")
    colegiatura_admin = db.Column(db.String(50), default="")
    dni_responsable_almacen = db.Column(db.String(50), default="")
    asistente_tecnico = db.Column(db.String(300), default="")
    dni_cip_asistente = db.Column(db.String(50), default="")


class Presupuesto(db.Model):
    """Configuracion por componente/clasificador para el formato FE-06."""
    id = db.Column(db.Integer, primary_key=True)
    componente = db.Column(db.String(100))
    clasificador = db.Column(db.String(20))
    detalle = db.Column(db.String(100))
    et = db.Column(db.Float, default=0)
    ejec2023 = db.Column(db.Float, default=0)
    ejec2024 = db.Column(db.Float, default=0)
    ejec2025 = db.Column(db.Float, default=0)
    pim2026 = db.Column(db.Float, default=0)


class Gasto(db.Model):
    """Cabecera del manifiesto de gasto (datos del proveedor por documento)."""
    id = db.Column(db.Integer, primary_key=True)
    orden = db.Column(db.Integer, default=1)
    fecha = db.Column(db.Date)
    siaf = db.Column(db.Integer, default=0)
    tipo_doc = db.Column(db.String(10), default="O/C")  # O/C | O/S
    num_doc = db.Column(db.Integer, default=0)
    proveedor = db.Column(db.String(300), default="")
    clasificador = db.Column(db.String(20), default="2.6.2.3.99.4")
    componente = db.Column(db.String(100), default="Costo Directo")
    pecosa = db.Column(db.String(30), default="")
    mes = db.Column(db.Integer, default=6)
    anio = db.Column(db.Integer, default=2026)
    devengado = db.Column(db.Boolean, default=False)
    nota_pago = db.Column(db.String(100), default="")
    fecha_devengado = db.Column(db.Date)

    detalles = db.relationship(
        "GastoDetalle", backref="gasto", cascade="all, delete-orphan",
        order_by="GastoDetalle.orden, GastoDetalle.id")

    @property
    def importe(self):
        return round(sum(d.importe for d in self.detalles), 2)

    @property
    def es_bien(self):
        return self.clasificador == "2.6.2.3.99.4"


class GastoDetalle(db.Model):
    """Detalle (bien o servicio) de un gasto del manifiesto."""
    id = db.Column(db.Integer, primary_key=True)
    gasto_id = db.Column(db.Integer, db.ForeignKey("gasto.id"))
    detalle = db.Column(db.String(500), default="")
    und = db.Column(db.String(20), default="UND")
    cantidad = db.Column(db.Float, default=1)
    precio_unitario = db.Column(db.Float, default=0)
    orden = db.Column(db.Integer, default=1)

    @property
    def importe(self):
        return round((self.cantidad or 0) * (self.precio_unitario or 0), 2)


class AlmacenMovimiento(db.Model):
    """Movimiento de almacen (formatos FE-07 y FE-08)."""
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(300), default="")
    und = db.Column(db.String(20), default="UND")
    fecha = db.Column(db.Date)
    tipo = db.Column(db.String(1), default="E")  # E = entrada, S = salida
    cantidad = db.Column(db.Float, default=1)
    numero_doc = db.Column(db.String(50), default="")
    numero_siaf = db.Column(db.String(50), default="")
    pecosa_guia = db.Column(db.String(50), default="")
    proveedor = db.Column(db.String(300), default="")
    responsable = db.Column(db.String(300), default="")
    actividad = db.Column(db.String(300), default="")
    precio_unitario = db.Column(db.Float, default=0)
    mes = db.Column(db.Integer, default=6)
    anio = db.Column(db.Integer, default=2026)

    @property
    def importe(self):
        return round((self.cantidad or 0) * (self.precio_unitario or 0), 2)


class ActividadEjecutada(db.Model):
    """Actividad de la seccion II (Actividades Ejecutadas) del Resumen Financiero."""
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(800), default="")
    orden = db.Column(db.Integer, default=1)
    mes = db.Column(db.Integer, default=6)
    anio = db.Column(db.Integer, default=2026)


class Trabajador(db.Model):
    """Personal registrado para el tareo o planilla mensual (obrero o tecnico)."""
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), default="OBRERO")  # OBRERO | TECNICO
    nombre = db.Column(db.String(300), default="")
    dni = db.Column(db.String(8), default="")
    fecha_nacimiento = db.Column(db.Date)
    cargo = db.Column(db.String(200), default="")
    sexo = db.Column(db.String(1), default="M")  # M | F
    fecha_inicio = db.Column(db.Date)
    dias = db.Column(db.String(100), default="")  # dias trabajados del mes (CSV 1..31)
    aporte = db.Column(db.String(10), default="AFP")  # AFP | ONP
    sueldo_mensual = db.Column(db.Float, default=0.0)  # sueldo del tecnico/administrativo (D.L. 728)
    devengado = db.Column(db.Boolean, default=False)  # si el total del panel se incluye en FE-06 Personal
    mes = db.Column(db.Integer, default=6)
    anio = db.Column(db.Integer, default=2026)

    @property
    def dias_lista(self):
        """Dias del mes en los que trabajo, como lista ordenada de enteros."""
        try:
            return sorted({int(x) for x in (self.dias or "").split(",")
                           if x.strip().isdigit()})
        except (ValueError, TypeError):
            return []

    @dias_lista.setter
    def dias_lista(self, valores):
        self.dias = ",".join(str(v) for v in sorted(set(int(v) for v in valores)))


class Usuario(db.Model):
    """Usuario del aplicativo con rol para ingresar al sistema."""
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    clave = db.Column(db.String(255), nullable=False)
    nombres = db.Column(db.String(200), default="")
    rol = db.Column(db.String(30), default="Usuario")  # Administrador | Usuario
    activo = db.Column(db.Boolean, default=True)
    permisos = db.Column(db.String(500), default="[]")  # claves de secciones autorizadas
    # Licencia propia del Administrador. Si susc_activa es None, el
    # Administrador hereda la licencia global de la base maestra.
    susc_plan = db.Column(db.String(20))
    susc_inicio = db.Column(db.Date)
    susc_fin = db.Column(db.Date)
    susc_activa = db.Column(db.Boolean)

    @property
    def permiso_lista(self):
        try:
            lista = json.loads(self.permisos or "[]")
        except (ValueError, TypeError):
            return []
        return lista if isinstance(lista, list) else []

    @permiso_lista.setter
    def permiso_lista(self, lista):
        self.permisos = json.dumps([k for k in lista if isinstance(k, str)])


class Suscripcion(db.Model):
    """Licencia de uso del aplicativo (una sola fila).

    El Super Usuario controla el plan (Mensual, Trimestral o Anual) y su
    vigencia. Cuando vence o se pausa, el aplicativo queda bloqueado para
    todos excepto el Super Usuario.
    """
    id = db.Column(db.Integer, primary_key=True)
    plan = db.Column(db.String(20), default="Mensual")
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    activa = db.Column(db.Boolean, default=True)

    @property
    def dias_restantes(self):
        if not self.fecha_fin:
            return 0
        return (self.fecha_fin - date.today()).days

    @property
    def vigente(self):
        return bool(self.activa and self.fecha_fin
                    and self.fecha_fin >= date.today())


class SuscripcionHistorial(db.Model):
    """Registro de cada renovación, activación o pausa de la suscripción."""
    id = db.Column(db.Integer, primary_key=True)
    plan = db.Column(db.String(20), default="")
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    usuario = db.Column(db.String(120), default="")
    nota = db.Column(db.String(500), default="")
    accion = db.Column(db.String(30), default="Renovación")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)


class LicenciaUtilizada(db.Model):
    """Registro de licencias ya activadas (cada código tiene un solo uso,
    ligado al usuario y al primer equipo que lo activó).

    La serie del código se marca como usada al aplicar, de modo que el mismo
    código no pueda reactivar la suscripción una segunda vez en otro equipo.
    """
    __tablename__ = "licencias_usadas"
    id = db.Column(db.Integer, primary_key=True)
    serie = db.Column(db.String(50), unique=True, nullable=False)
    usuario = db.Column(db.String(80), default="")
    plan = db.Column(db.String(20), default="")
    maquina = db.Column(db.String(80), default="")
    fecha_uso = db.Column(db.DateTime, default=datetime.utcnow)


class LicenciaEmitida(db.Model):
    """Código de licencia alfanumérico emitido por el Super Usuario.

    Cada código queda ligado al Administrador (usuario) para quien se generó
    y a un plan. La serie (única) se incrusta en el código y se marca como
    utilizada al activarla la primera vez, junto con el equipo que la usó.
    """
    __tablename__ = "licencias_emitidas"
    id = db.Column(db.Integer, primary_key=True)
    serie = db.Column(db.String(50), unique=True, nullable=False)
    plan = db.Column(db.String(20), default="Mensual")
    usuario = db.Column(db.String(80), default="")
    emitida = db.Column(db.Date, default=date.today)
    usada = db.Column(db.Boolean, default=False)
    usada_por = db.Column(db.String(80), default="")
    maquina = db.Column(db.String(80), default="")
    fecha_uso = db.Column(db.DateTime)
