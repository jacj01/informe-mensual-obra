"""Funciones auxiliares de calculo compartidas por rutas y exportadores."""
import calendar
import re
from datetime import date, timedelta

from models import (Proyecto, Presupuesto, Gasto, GastoDetalle,
                    AlmacenMovimiento, ActividadEjecutada, Trabajador,
                    Suscripcion, db)
import databases as _bd

MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
         "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]

DIAS_LETRA = {0: "L", 1: "M", 2: "M", 3: "J", 4: "V", 5: "S", 6: "D"}
DIAS_NOMBRE = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
               4: "Viernes", 5: "Sábado", 6: "Domingo"}

COMPONENTES_FE06 = [
    "Costo Directo", "Gastos Generales", "Gestion de Supervisión",
    "Elaboración de Expediente Técnico", "Liquidación de Obra",
]

# Actividades por defecto de la seccion II del Resumen Financiero (PANEL).
ACTIVIDADES_DEFECTO = [
    "Elaboración de requerimiento de bienes y servicios.",
    "Seguimiento de informes recibidos y emitidos para su ejecución.",
    "Elaboración de informes financieros mensuales.",
    "Coordinación con las diferentes áreas de la Municipalidad Distrital de Toraya "
    "para la correcta ejecución administrativa del proyecto.",
    "Requerimiento de modificaciones presupuestales según lo programado en el plan "
    "operativo institucional con la finalidad de garantizar la ejecución "
    "presupuestal en los diferentes componentes del proyecto.",
    "Elaboración de conformidades de orden de servicio para efectuar el pago "
    "correspondiente a los proveedores.",
]


def get_proyecto():
    """Devuelve el Proyecto en uso; lo crea en cero si la base aún no tiene."""
    p = Proyecto.query.first()
    if p is None:
        p = Proyecto()
        p.anio = date.today().year
        p.mes_actual = date.today().month
        db.session.add(p)
        db.session.commit()
    return p


def get_suscripcion():
    """Estado actual de la suscripción (fila única).

    La suscripción es global y vive en la base maestra, independientemente del
    administrador o de la base a la que apunte la sesión de la petición.
    """
    return _bd.master_session.query(Suscripcion).first()


def suscripcion_usuario(u):
    """Suscripción efectiva (dict) de un usuario.

    Un Administrador con licencia propia (susc_activa definida) usa sus propios
    datos; si aún no la tiene (susc_activa NULL) hereda la licencia global de
    la base maestra. Para operadores se debe pasar la cuenta de su
    Administrador (el propietario de la licencia).
    """
    hoy = date.today()
    if u is not None and getattr(u, "rol", None) == "Super Usuario":
        # El Super Usuario (cuenta principal) no tiene límites de licencia.
        return {
            "plan": "Cuenta Principal",
            "fecha_inicio": None,
            "fecha_fin": None,
            "activa": True,
            "vigente": True,
            "dias_restantes": 9999,
            "es_super": True,
        }
    if u is not None and getattr(u, "rol", None) == "Administrador" \
            and u.susc_activa is not None:
        fin = u.susc_fin
        return {
            "plan": u.susc_plan or "",
            "fecha_inicio": u.susc_inicio,
            "fecha_fin": fin,
            "activa": bool(u.susc_activa),
            "vigente": bool(u.susc_activa and fin and fin >= hoy),
            "dias_restantes": (fin - hoy).days if fin else 0,
            "es_super": False,
        }
    s = get_suscripcion()
    return {
        "plan": s.plan if s else "",
        "fecha_inicio": s.fecha_inicio if s else None,
        "fecha_fin": s.fecha_fin if s else None,
        "activa": bool(s and s.activa),
        "vigente": bool(s and s.vigente),
        "dias_restantes": s.dias_restantes if s else 0,
        "es_super": bool(u and getattr(u, "rol", None) == "Super Usuario"),
    }


def suscripcion_vigente(u=None):
    """True si la licencia efectiva del usuario (o la global) está vigente."""
    if u is not None:
        return bool(suscripcion_usuario(u)["vigente"])
    s = get_suscripcion()
    return bool(s and s.vigente)


def fmt(n):
    if n is None:
        return "0.00"
    return f"{n:,.2f}"


def gastos_mes(mes, anio, devengado=None):
    """Gastos de un periodo. Si devengado es True/False filtra por ese estado."""
    q = Gasto.query.filter(Gasto.mes == mes, Gasto.anio == anio)
    if devengado is not None:
        q = q.filter(Gasto.devengado == devengado)
    return q.order_by(Gasto.orden, Gasto.id).all()


def total_gastos_mes(mes, anio, devengado=None):
    return round(sum(g.importe for g in gastos_mes(mes, anio, devengado)), 2)


def mes_inicio_manifiesto(anio):
    """Primer mes del anio con gastos devengados (mes en que se inicio el
    ingreso de datos). Sirve de base para el correlativo del manifiesto."""
    m = db.session.query(db.func.min(Gasto.mes)).filter(
        Gasto.anio == anio, Gasto.devengado == True).scalar()
    return m if m else 1


def ejecucion_por_mes(anio):
    """Suma de importes devengados por mes (1-12) para el anio dado."""
    out = [0.0] * 12
    rows = (db.session.query(Gasto.mes,
                             db.func.sum(GastoDetalle.cantidad * GastoDetalle.precio_unitario))
            .join(GastoDetalle, GastoDetalle.gasto_id == Gasto.id)
            .filter(Gasto.anio == anio, Gasto.devengado == True)
            .group_by(Gasto.mes).all())
    for mes, total in rows:
        out[mes - 1] = round(total or 0, 2)
    return out


def meses_con_ejecucion(anio):
    """Indices (1-12) de los meses con gastos devengados en el anio dado."""
    rows = (db.session.query(Gasto.mes,
                             db.func.sum(GastoDetalle.cantidad * GastoDetalle.precio_unitario))
            .join(GastoDetalle, GastoDetalle.gasto_id == Gasto.id)
            .filter(Gasto.anio == anio, Gasto.devengado == True)
            .group_by(Gasto.mes).all())
    return sorted({mes for mes, total in rows if (total or 0) > 0})


def mes_inicio_obra():
    """Mes (1-12) en que inicio la obra, segun la 'Fecha de inicio de obra'
    registrada en Datos del Proyecto; 1 (enero) si no esta definida."""
    f = get_proyecto().fecha_inicio
    return f.month if f else 1


def meses_visibles(anio, mes):
    """Meses a mostrar en el FE-06: desde el mes de inicio de obra hasta el mes
    seleccionado, mas los meses con ejecucion que queden fuera de ese rango."""
    inicio = mes_inicio_obra()
    activos = [m for m in meses_con_ejecucion(anio) if m >= inicio]
    return sorted(set(activos) | set(range(inicio, mes + 1)))


def incluir_anios():
    """True si se deben mostrar los anos anteriores (2023-2025)."""
    p = get_proyecto()
    return p.incluir_anios_anteriores if p.incluir_anios_anteriores is not None else True


def clasificadores_proyecto():
    """Clasificadores configurados en la cabecera: codigo -> etiqueta."""
    p = get_proyecto()
    return {
        (p.clasificador_personal or "2.6.2.3.99.3"): "PERSONAL",
        (p.clasificador_bienes or "2.6.2.3.99.4"): "BIENES",
        (p.clasificador_servicios or "2.6.2.3.99.5"): "SERVICIOS",
        (p.clasificador_expediente or "2.6.8.1.3.1"): "ELABORACION DE EXPEDIENTE TECNICO",
    }


def ejecucion_por_componente(anio):
    # Incluye TODOS los componentes presentes en la config de Presupuesto
    # (Costo Directo, Gastos Generales, Gestion de Supervision,
    #  Elaboracion de Expediente Tecnico, Liquidacion de Obra).
    comps = [c[0] for c in db.session.query(Presupuesto.componente.distinct())
             if c[0] not in (None, "")]
    out = {c: 0.0 for c in comps}
    rows = (db.session.query(Gasto.componente,
                             db.func.sum(GastoDetalle.cantidad * GastoDetalle.precio_unitario))
            .join(GastoDetalle, GastoDetalle.gasto_id == Gasto.id)
            .filter(Gasto.anio == anio, Gasto.devengado == True)
            .group_by(Gasto.componente).all())
    for comp, total in rows:
        out[comp] = round(total or 0, 2)
    return out


def ampliacion_presupuestal():
    """Monto de la ampliacion presupuestal activa (0 si no hay)."""
    p = get_proyecto()
    if p and p.ampliacion_presupuestal:
        return round(p.monto_ampliacion or 0, 2)
    return 0.0


def pim_total():
    """PIM efectivo del ano actual incluyendo la ampliacion presupuestal si existe."""
    return round(sum(p.pim2026 or 0 for p in Presupuesto.query.all())
                 + ampliacion_presupuestal(), 2)


def et_total():
    """Presupuesto total segun Expediente Tecnico (suma de configuraciones)."""
    return round(sum(p.et or 0 for p in Presupuesto.query.all()), 2)


def ejecutado_anio(anio):
    return round(sum(g.importe for g in
                     Gasto.query.filter(Gasto.anio == anio, Gasto.devengado == True).all()), 2)


def ejecutado_acumulado_anterior():
    """Ejecucion 2023 + 2024 + 2025 desde la configuracion presupuestal."""
    rows = Presupuesto.query.all()
    return round(sum((p.ejec2023 or 0) + (p.ejec2024 or 0) + (p.ejec2025 or 0) for p in rows), 2)


def kpis(anio=None, mes=None):
    p = get_proyecto()
    anio = anio or p.anio
    mes = mes or p.mes_actual
    pim = pim_total()
    ejec = ejecutado_anio(anio)
    anterior = ejecutado_acumulado_anterior()
    return {
        "pim": pim,
        "ejecutado_anio": ejec,
        "porc_anio": (ejec / pim * 100) if pim else 0,
        "saldo_anio": round(pim - ejec, 2),
        "gasto_mes": total_gastos_mes(mes, anio, devengado=True),
        "presupuesto_total": et_total(),
        "acumulado_total": round(ejec + anterior, 2),
        "saldo_proyecto": round(et_total() - (ejec + anterior), 2),
    }


def fe06_rows():
    """Filas para el formato FE-06 con calculo de ejecucion 2026 desde gastos."""
    anio = get_proyecto().anio
    orden_detalle = {"PERSONAL": 0, "BIENES": 1, "SERVICIOS": 2,
                     "ELABORACION DE EXPEDIENTE TECNICO": 3,
                     "COSTO DE LIQUIDACION": 4}
    rows = []
    for comp in COMPONENTES_FE06:
        configs = sorted(Presupuesto.query.filter_by(componente=comp).all(),
                         key=lambda c: orden_detalle.get(c.detalle, 99))
        for cfg in configs:
            if cfg.clasificador == "LIQUIDACION":
                clasif = "LIQUIDACION"
            else:
                clasif = cfg.clasificador
            mensual = [0.0] * 12
            gastos = Gasto.query.filter(Gasto.anio == anio, Gasto.componente == comp,
                                        Gasto.clasificador == clasif,
                                        Gasto.devengado == True).all()
            for g in gastos:
                mensual[g.mes - 1] = round(mensual[g.mes - 1] + g.importe, 2)
            total_anio = round(sum(mensual), 2)
            acum_total = round((cfg.ejec2023 or 0) + (cfg.ejec2024 or 0) +
                               (cfg.ejec2025 or 0) + total_anio, 2)
            rows.append({
                "componente": comp,
                "clasificador": cfg.clasificador,
                "detalle": cfg.detalle,
                "et": cfg.et or 0,
                "e2023": cfg.ejec2023 or 0,
                "e2024": cfg.ejec2024 or 0,
                "e2025": cfg.ejec2025 or 0,
                "pim": cfg.pim2026 or 0,
                "mensual": mensual,
                "total_anio": total_anio,
                "porc_pim": (total_anio / cfg.pim2026 * 100) if cfg.pim2026 else 0,
                "saldo_pim": round((cfg.pim2026 or 0) - total_anio, 2),
                "acum_total": acum_total,
                "porc_et": (acum_total / cfg.et * 100) if cfg.et else 0,
                "saldo_et": round((cfg.et or 0) - acum_total, 2),
            })
    return rows


def fe06_resumen(rows):
    """Totales por componente para FE-06."""
    resumen = {}
    for comp in COMPONENTES_FE06:
        items = [r for r in rows if r["componente"] == comp]
        resumen[comp] = {
            "et": round(sum(r["et"] for r in items), 2),
            "e2023": round(sum(r["e2023"] for r in items), 2),
            "e2024": round(sum(r["e2024"] for r in items), 2),
            "e2025": round(sum(r["e2025"] for r in items), 2),
            "pim": round(sum(r["pim"] for r in items), 2),
            "mensual": [round(sum(r["mensual"][i] for r in items), 2) for i in range(12)],
            "total_anio": round(sum(r["total_anio"] for r in items), 2),
            "saldo_pim": round(sum(r["saldo_pim"] for r in items), 2),
            "acum_total": round(sum(r["acum_total"] for r in items), 2),
            "saldo_et": round(sum(r["saldo_et"] for r in items), 2),
        }
    return resumen


def panel_cuadro1(anio=None):
    """Filas del CUADRO No 1 (Balance de Ejecución del Ejercicio) para el
    Resumen Financiero (hoja PANEL), usando los datos del proyecto y la
    ejecución real registrada en el aplicativo."""
    p = get_proyecto()
    anio = anio or p.anio
    resumen = fe06_resumen(fe06_rows())
    ejec = ejecucion_por_componente(anio)
    cd = resumen["Costo Directo"]
    gg = resumen["Gastos Generales"]

    def fila(n, concepto, pi, pa, ea):
        pct = round(ea / pa * 100, 2) if (pa or 0) > 0 else None
        saldo = round(pa - ea, 2) if (pa is not None and ea is not None) else None
        return {"n": n, "concepto": concepto, "pi": pi, "pa": pa,
                "ea": ea, "pct": pct, "saldo": saldo}

    rows = [
        fila(1, "COSTO DIRECTO", p.costo_directo, cd["pim"], ejec["Costo Directo"]),
        fila(2, "GASTOS GENERALES", p.gastos_generales, gg["pim"], ejec["Gastos Generales"]),
        fila(3, "UTILIDAD", 0.0, None, None),
        fila(4, "", None, None, None),
        fila(5, "GASTOS NO ELEGIBLES", 0.0, None, None),
    ]
    for n in range(6, 16):
        rows.append(fila(n, "", None, None, None))
    return rows


def numero_a_letras(n):
    """Numero entero positivo en letras (espanol)."""
    U = ["", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
    D = ["", "diez", "veinte", "treinta", "cuarenta", "cincuenta",
         "sesenta", "setenta", "ochenta", "noventa"]
    E = {11: "once", 12: "doce", 13: "trece", 14: "catorce", 15: "quince",
         16: "dieciseis", 17: "diecisiete", 18: "dieciocho", 19: "diecinueve"}
    C = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos",
         "seiscientos", "setecientos", "ochocientos", "novecientos"]

    def tres(n):
        partes = []
        c = n // 100
        if c:
            partes.append("cien" if c == 1 and n % 100 == 0 else C[c])
        n %= 100
        if 10 < n < 20:
            partes.append(E[n])
        elif n:
            d, u = n // 10, n % 10
            if d == 2 and u:
                partes.append("veinti" + U[u])
            elif d:
                partes.append(D[d])
                if u:
                    partes.append("y " + U[u])
            elif u:
                partes.append(U[u])
        return " ".join(partes)

    n = int(n or 0)
    if n == 0:
        return "cero"
    millones = n // 1000000
    miles = (n % 1000000) // 1000
    cientos = n % 1000
    partes = []
    if millones:
        partes.append("un millon" if millones == 1 else tres(millones) + " millones")
    if miles:
        partes.append("mil" if miles == 1 else tres(miles) + " mil")
    if cientos:
        partes.append(tres(cientos))
    return " ".join(partes)


def monto_letras(monto):
    """Monto en letras: 'un millon ciento veinte y dos mil ... con 52/100 soles'."""
    monto = round(monto or 0, 2)
    enteros = int(monto)
    cent = int(round((monto - enteros) * 100))
    return f"{numero_a_letras(enteros)} con {cent:02d}/100 soles"


def actividades_mes(mes, anio=None):
    """Actividades ejecutadas de la seccion II del Resumen Financiero para un
    mes/anio. Si el mes aun no tiene actividades registradas, devuelve la lista
    por defecto (sin persistir)."""
    anio = anio or get_proyecto().anio
    filas = (ActividadEjecutada.query
             .filter(ActividadEjecutada.mes == mes,
                     ActividadEjecutada.anio == anio)
             .order_by(ActividadEjecutada.orden, ActividadEjecutada.id)
             .all())
    if filas:
        return filas
    return [ActividadEjecutada(descripcion=t, orden=i + 1, mes=mes, anio=anio)
            for i, t in enumerate(ACTIVIDADES_DEFECTO)]


def panel_datos(mes, anio=None):
    """Datos completos de la hoja PANEL (Resumen Financiero mensual) para su
    replica fiel en HTML: todos los cuadros, titulos, textos y calculos."""
    p = get_proyecto()
    anio = anio or p.anio
    incluir = incluir_anios()
    rows = fe06_rows()
    resumen = fe06_resumen(rows)
    meses_col = list(range(1, mes + 1))
    meses_prev = [m for m in meses_col if m < mes]
    prev = MESES[mes - 2] if mes > 1 else ""

    def get(comp, clas):
        for r in rows:
            if r["componente"] == comp and r["clasificador"] == clas:
                return r
        return None

    NUM = ("et", "e2023", "e2024", "e2025", "pim", "total_anio",
           "saldo_pim", "acum_total")
    tot = {kk: round(sum(resumen[c][kk] for c in resumen), 2) for kk in NUM}
    if not incluir:
        tot["e2023"] = tot["e2024"] = tot["e2025"] = 0.0
    amp = ampliacion_presupuestal()
    pim = round(tot["pim"] + amp, 2)
    saldo_pim = round(pim - tot["total_anio"], 2)
    et = tot["et"]
    ejec_anio = tot["total_anio"]
    acum_total = tot["acum_total"] if incluir else ejec_anio

    et_comp = {c: 0.0 for c in COMPONENTES_FE06}
    for r in rows:
        et_comp[r["componente"]] = round(et_comp.get(r["componente"], 0.0) + (r["et"] or 0), 2)

    def sum_key(key, clas):
        return round(sum(r[key] or 0 for r in rows if r["clasificador"] == clas), 2)

    m = re.match(r"\s*(\d+)", p.meta or "")
    meta_num = int(m.group(1)) if m else 0

    # ---------------- I. RESUMEN DE LA EJECUCION PRESUPUESTAL ----------------
    resumen_i = [{"concepto": "Presupuesto total", "monto": et, "meta": 0}]
    if incluir:
        resumen_i.append({"concepto": "Avance Acumulado gastos devengado 2023",
                          "monto": tot["e2023"], "meta": 46})
        resumen_i.append({"concepto": "Avance Acumulado gastos devengado 2024",
                          "monto": tot["e2024"], "meta": 29})
        resumen_i.append({"concepto": "Avance Acumulado gastos devengado 2025",
                          "monto": tot["e2025"], "meta": 17})
    resumen_i.append({"concepto": f"Avance Acumulado gastos devengado {anio}",
                      "monto": ejec_anio, "meta": meta_num})
    resumen_i.append({"concepto": (f"Gasto acumulado desde 2023 hasta {anio}"
                                   if incluir else f"Gasto acumulado hasta {anio}"),
                      "monto": acum_total, "meta": 0})
    resumen_i.append({"concepto": f"Saldo al {anio} (Ppto - Acumulado)",
                      "monto": round(et - acum_total, 2), "meta": 0})
    resumen_i.append({"concepto": f"Presupuesto Anual (PIN {anio}) (S/)",
                      "monto": pim, "meta": meta_num})
    resumen_i.append({"concepto": f"Gasto Devengado {MESES[0]} a {MESES[mes-1]} (S/)",
                      "monto": ejec_anio, "meta": 0})
    resumen_i.append({"concepto": f"SALDO {anio}", "monto": saldo_pim, "meta": 0})

    # ---------------- Sub-cuadro PIN / BASE DE CALCULO ----------------
    monto_prev = round(sum(r["mensual"][m - 1] for r in rows for m in meses_prev), 2)
    monto_mes = round(sum(r["mensual"][mes - 1] for r in rows), 2)
    total_pin = round(monto_prev + monto_mes, 2)
    pct = lambda x: round(x / pim * 100, 2) if pim else 0.0
    pin_rows = [
        {"concepto": f"PIN Aprobado para {anio}", "monto": pim,
         "pct": pct(saldo_pim),
         "base": f"Monto vigente para la meta {meta_num:03d}"},
        {"concepto": (f"Avance Acumulado anterior ({MESES[0]} - {prev})"
                      if meses_prev else "Avance Acumulado anterior"),
         "monto": monto_prev, "pct": pct(monto_prev),
         "base": (f"Gasto devengado {MESES[0]} - {prev} {anio}" if meses_prev else "")},
        {"concepto": f"Avance al mes de {MESES[mes-1]}", "monto": monto_mes,
         "pct": pct(monto_mes), "base": f"Gasto devengado {MESES[mes-1]} {anio}"},
        {"concepto": "Avance Acumulado Total", "monto": total_pin,
         "pct": pct(total_pin), "base": ""},
    ]

    # ---------------- III. DEVENGADO MENSUAL / IV. ACUMULADO ----------------
    # Construido desde la config real de Presupuesto: incluye los 5 componentes
    # con SUS propios clasificadores (p.ej. Elaboracion de Expediente = 2.6.8.1.3.1,
    # Liquidacion de Obra = LIQUIDACION), no solo Personal/Bienes/Servicios.
    _orden_det = {"PERSONAL": 0, "BIENES": 1, "SERVICIOS": 2,
                  "ELABORACION DE EXPEDIENTE TECNICO": 3, "COSTO DE LIQUIDACION": 4}
    grupos3 = []
    for comp in COMPONENTES_FE06:
        configs = sorted(Presupuesto.query.filter_by(componente=comp).all(),
                         key=lambda c: _orden_det.get((c.detalle or "").upper(), 99))
        for cfg in configs:
            grupos3.append((comp, cfg.clasificador, cfg.detalle or cfg.clasificador))

    def filas_dev(grupos):
        out = []
        for comp, clas, det in grupos:
            r = get(comp, clas) or {}
            out.append({
                "clas": r.get("clasificador", clas),
                "detalle": det,
                "valores": [round(r["mensual"][m - 1], 2) if r else 0.0 for m in meses_col],
                "acum": round(r["total_anio"], 2) if r else 0.0,
            })
        return out

    dev_mensual = [{"grupo": comp,
                    "filas": filas_dev([g for g in grupos3 if g[0] == comp])}
                   for comp in COMPONENTES_FE06]
    dev_mensual_total = [round(sum(r["mensual"][m - 1] for r in rows), 2) for m in meses_col]
    dev_acum_total = round(sum(r["total_anio"] for r in rows), 2)

    # ---------------- V. RESUMEN GASTO DEVENGADO ----------------
    resumen_dev = []
    for clas, det in (("2.6.2.3.99.3", "Personal"),
                      ("2.6.2.3.99.4", "Bienes"),
                      ("2.6.2.3.99.5", "Servicios"),
                      ("2.6.8.1.3.1", "Elaboración de Expediente Técnico"),
                      ("LIQUIDACION", "Liquidación de Obra")):
        pin = round(sum((get(c, clas) or {}).get("pim", 0) for c in COMPONENTES_FE06), 2)
        gas = round(sum((get(c, clas) or {}).get("total_anio", 0) for c in COMPONENTES_FE06), 2)
        resumen_dev.append({"clas": clas, "detalle": det, "pin": pin, "gas": gas,
                            "pct": round(gas / pin * 100, 2) if pin else 0.0})
    pin5 = round(sum(f["pin"] for f in resumen_dev), 2)
    gas5 = round(sum(f["gas"] for f in resumen_dev), 2)
    resumen_dev_total = {"pin": pin5, "gas": gas5,
                         "pct": round(gas5 / pin5 * 100, 2) if pin5 else 0.0}

    # ---------------- EJECUCION PRESUPUESTAL ----------------
    CLAS_ORDER = [
        ("2.6.8.1.3.1", "Elaboración de Expediente Técnico."),
        ("2.6.2.3.99.3", "Costo de Construccion por Administracion directa - Personal"),
        ("2.6.2.3.99.4", "Costo de Construccion por Administracion directa - Bienes"),
        ("2.6.2.3.99.5", "Costo de Construccion por Administracion directa - Servicios"),
    ]

    ejec_anuales = []
    if incluir:
        for anio_txt, meta_hist, num in (("2023", "0046", "2.1"),
                                         ("2024", "0029", "2.2"),
                                         ("2025", "0017", "2.3")):
            filas = [{"clas": clas, "detalle": det, "monto": sum_key(f"e{anio_txt}", clas)}
                     for clas, det in CLAS_ORDER]
            filas = [f for f in filas if f["monto"] > 0]
            ejec_anuales.append({
                "num": num, "anio": anio_txt, "meta": meta_hist,
                "titulo": (f"{num}. RESUMEN DE EJECUCION PRESUPUESTAL AL MES DE "
                           f"DICIEMBRE DEL AÑO {anio_txt}"),
                "filas": filas,
                "total": round(sum(resumen[c][f"e{anio_txt}"] for c in resumen), 2),
            })

    gen = []
    for anio_txt in (("2023", "2024", "2025") if incluir else ()):
        for clas, det in CLAS_ORDER:
            monto = sum_key(f"e{anio_txt}", clas)
            if monto > 0:
                gen.append({"clas": clas, "detalle": det, "monto": monto, "anio": anio_txt})
    for clas, det in CLAS_ORDER:
        monto = sum_key("total_anio", clas)
        if monto > 0:
            gen.append({"clas": clas, "detalle": det, "monto": monto, "anio": str(anio)})

    resumen_general = []
    for clas, det in CLAS_ORDER:
        monto = round(sum((r["acum_total"] if incluir else r["total_anio"]) or 0
                          for r in rows if r["clasificador"] == clas), 2)
        if monto > 0:
            resumen_general.append({"clas": clas, "detalle": det, "monto": monto})

    componentes_presupuesto = [
        ("Costo Directo", "Costo Directo"),
        ("Gastos Generales", "Gastos Generales"),
        ("Gestion de Supervisión", "Gastos de Supervisión"),
        ("Elaboración de Expediente Técnico", "Elaboración de Expediente"),
        ("Liquidación de Obra", "Gastos de Liquidación"),
    ]
    ejec_fin = [{"label": lab, "presupuesto": et_comp[comp],
                 "ejecutado": (resumen[comp]["acum_total"] if incluir
                               else resumen[comp]["total_anio"])}
                for comp, lab in componentes_presupuesto]
    ejec_fin.append({"label": "Presupuesto total segun expediente tecnico",
                     "presupuesto": et, "ejecutado": acum_total})

    narrativas = []
    for titulo, comp in (("3. COSTO DIRECTO", "Costo Directo"),
                         ("4. GASTOS GENERALES", "Gastos Generales"),
                         ("5. GASTOS DE SUPERVISION", "Gestion de Supervisión")):
        ejec_comp = (resumen[comp]["acum_total"] if incluir
                     else resumen[comp]["total_anio"])
        narrativas.append({
            "titulo": titulo,
            "texto": (f"El presupuesto total en este componente es de S/. "
                      f"{fmt(et_comp[comp])} soles, referido a lo presupuestado en el "
                      f"expediente tecnico aprobado, donde la ejecucion con cargo a desembolso "
                      f"y/o transferencia hasta el mes de {MESES[mes-1]} del {anio} es de: S/. "
                      f"{fmt(ejec_comp)} soles.")})
    def narrativa_componente(titulo, comp):
        ejec_comp = (resumen[comp]["acum_total"] if incluir
                     else resumen[comp]["total_anio"])
        return {"titulo": titulo,
                "texto": (f"El presupuesto total en este componente es de S/. "
                          f"{fmt(et_comp[comp])} soles, referido a lo presupuestado en el "
                          f"expediente tecnico aprobado, donde la ejecucion con cargo a "
                          f"desembolso y/o transferencia hasta el mes de {MESES[mes-1]} del "
                          f"{anio} es de: S/. {fmt(ejec_comp)} soles.")}

    narrativas.append(narrativa_componente(
        "6. ELABORACION Y EVALUACION DEL EXPEDIENTE TECNICO",
        "Elaboración de Expediente Técnico"))
    narrativas.append(narrativa_componente(
        "7. GASTOS DE LIQUIDACION", "Liquidación de Obra"))

    # ---------------- GRAFICOS PANEL ----------------
    graf_mensual = [{"label": mn[:3], "monto": round(sum(r["mensual"][mi] for r in rows), 2)}
                    for mi, mn in enumerate(MESES)]
    graf_circular = ejecucion_por_componente(anio)
    graf_componentes = [
        {"label": "Costo Directo", "presupuesto": et_comp["Costo Directo"],
         "ejecutado": (resumen["Costo Directo"]["acum_total"] if incluir
                       else resumen["Costo Directo"]["total_anio"])},
        {"label": "Gastos Generales", "presupuesto": et_comp["Gastos Generales"],
         "ejecutado": (resumen["Gastos Generales"]["acum_total"] if incluir
                       else resumen["Gastos Generales"]["total_anio"])},
        {"label": "Gastos de Supervisión", "presupuesto": et_comp["Gestion de Supervisión"],
         "ejecutado": (resumen["Gestion de Supervisión"]["acum_total"] if incluir
                       else resumen["Gestion de Supervisión"]["total_anio"])},
        {"label": "Expediente Técnico", "presupuesto": et_comp["Elaboración de Expediente Técnico"],
         "ejecutado": (resumen["Elaboración de Expediente Técnico"]["acum_total"] if incluir
                       else resumen["Elaboración de Expediente Técnico"]["total_anio"])},
        {"label": "Liquidación de Obra", "presupuesto": et_comp["Liquidación de Obra"],
         "ejecutado": (resumen["Liquidación de Obra"]["acum_total"] if incluir
                       else resumen["Liquidación de Obra"]["total_anio"])},
    ]

    return {
        "p": p,
        "mes": mes, "anio": anio,
        "mes_nombre": MESES[mes - 1],
        "periodo": f"{MESES[mes-1]} - {anio}",
        "meta_num": meta_num,
        "incluir_anios": incluir,
        "ubicacion": (f"DISTRITO: {p.distrito or ''}; PROVINCIA: {p.provincia or ''}; "
                      f"DEPARTAMENTO: {p.departamento or ''}."),
        "presupuesto_et": et,
        "costo_directo": p.costo_directo or et_comp.get("Costo Directo", 0),
        "pim": pim,
        "saldo_pim": saldo_pim,
        "ejec_anio": ejec_anio,
        "acum_total": acum_total,
        "meses_col": meses_col,
        "resumen_i": resumen_i,
        "pin_rows": pin_rows,
        "monto_prev": monto_prev,
        "monto_mes": monto_mes,
        "dev_mensual": dev_mensual,
        "dev_mensual_total": dev_mensual_total,
        "dev_acum": dev_mensual,
        "dev_acum_total": dev_acum_total,
        "resumen_dev": resumen_dev,
        "resumen_dev_total": resumen_dev_total,
        "presupuesto_letras": monto_letras(et),
        "componentes_presupuesto": [{"label": lab, "monto": et_comp[comp]}
                                    for comp, lab in componentes_presupuesto]
                                    + [{"label": "Ppto total segun exp. Tecnico", "monto": et}],
        "ejec_anuales": ejec_anuales,
        "gen": gen,
        "gen_total": acum_total,
        "resumen_general": resumen_general,
        "resumen_general_total": acum_total,
        "ejec_fin_texto": (f"La ejecucion presupuestal total hasta {MESES[mes-1]} del {anio} "
                           f"es de S/. {fmt(acum_total)} ({monto_letras(acum_total)})"),
        "ejec_fin": ejec_fin,
        "narrativas": narrativas,
        "actividades": actividades_mes(mes, anio),
        "graf_mensual": graf_mensual,
        "graf_circular": graf_circular,
        "graf_componentes": graf_componentes,
    }


def f05_datos(mes, anio):
    """Secciones del formato FE-05 agrupadas por (tipo, componente) con numerador por proveedor.

    Devuelve (secciones, total, clasif_cols): clasif_cols son los clasificadores presentes
    en el periodo ordenados personal -> bienes -> servicios -> otros, para mostrarlos en
    columnas propias (2.6.2.3.99.3, 2.6.2.3.99.4, 2.6.2.3.99.5, otros...).
    Se mantienen las claves n/o por compatibilidad con exportadores existentes."""
    gastos = gastos_mes(mes, anio, devengado=True)
    cls_proy = clasificadores_proyecto()
    p = get_proyecto()
    cod_personal = p.clasificador_personal or "2.6.2.3.99.3"
    cod_bienes = p.clasificador_bienes or "2.6.2.3.99.4"
    cod_servicios = p.clasificador_servicios or "2.6.2.3.99.5"

    def tipo_de(clas):
        return cls_proy.get(clas) or (clas or "")

    clasif_cols = []
    vistos = set()
    for g in gastos:
        c = (g.clasificador or "").strip()
        if c and c not in vistos:
            vistos.add(c)
            clasif_cols.append(c)
    prio = {cod_personal: 0, cod_bienes: 1, cod_servicios: 2}
    clasif_cols.sort(key=lambda c: (prio.get(c, 9), c))

    grupos = {}
    for g in gastos:
        grupos.setdefault((tipo_de(g.clasificador), g.componente or ""), []).append(g)

    orden = []
    for g in gastos:
        key = (tipo_de(g.clasificador), g.componente or "")
        if key not in orden:
            orden.append(key)

    secciones = []
    for key in orden:
        label, componente = key
        lista = grupos[key]
        totales = {"n": 0.0, "o": 0.0, "directos": 0.0, "generales": 0.0,
                   "supervision": 0.0, "total": 0.0,
                   "clasif": {c: 0.0 for c in clasif_cols}}
        filas = []
        prov_cont = 0
        prev = None
        for g in lista:
            if g.proveedor != prev:
                prov_cont += 1
                prev = g.proveedor
                header = True
            else:
                header = False
            es_bien = g.clasificador == cod_bienes
            es_serv = g.clasificador == cod_servicios
            for idx_d, d in enumerate(g.detalles):
                n = d.importe if es_bien else 0.0
                o = d.importe if es_serv else 0.0
                directos = d.importe if g.componente == "Costo Directo" else 0.0
                generales = d.importe if g.componente == "Gastos Generales" else 0.0
                supervision = d.importe if g.componente == "Gestion de Supervisión" else 0.0
                por_clasif = {}
                for c in clasif_cols:
                    por_clasif[c] = d.importe if g.clasificador == c else 0.0
                filas.append({"g": g, "d": d, "n": n, "o": o,
                              "clasif": por_clasif,
                              "directos": directos,
                              "generales": generales, "supervision": supervision,
                              "prov_num": prov_cont,
                              "prov_first": header and idx_d == 0})
                totales["n"] += n
                totales["o"] += o
                for c in clasif_cols:
                    totales["clasif"][c] += por_clasif[c]
                totales["directos"] += directos
                totales["generales"] += generales
                totales["supervision"] += supervision
                totales["total"] += d.importe
        secciones.append({"label": label, "componente": componente,
                          "filas": filas, "totales": totales})
    total_gral = {"n": 0.0, "o": 0.0, "directos": 0.0, "generales": 0.0, "supervision": 0.0,
                  "total": 0.0, "clasif": {c: 0.0 for c in clasif_cols}}
    for s in secciones:
        for k in total_gral:
            if k == "clasif":
                for c in clasif_cols:
                    total_gral["clasif"][c] += s["totales"]["clasif"][c]
            else:
                total_gral[k] = round(total_gral[k] + s["totales"][k], 2)
    return secciones, total_gral, clasif_cols


def almacen_diario(mes, anio):
    """Movimiento diario de almacen por insumo con saldo corrido para FE-07."""
    movs = (AlmacenMovimiento.query
            .filter(AlmacenMovimiento.mes == mes, AlmacenMovimiento.anio == anio)
            .order_by(AlmacenMovimiento.fecha, AlmacenMovimiento.id).all())
    running = {}
    orden = []
    for m in movs:
        key = (m.descripcion, m.und)
        if key not in running:
            running[key] = {"balance": 0.0, "rows": []}
            orden.append(key)
        bal = running[key]["balance"]
        nuevo = bal + (m.cantidad or 0) if m.tipo == "E" else bal - (m.cantidad or 0)
        running[key]["rows"].append({"mov": m, "saldo_anterior": round(bal, 2),
                                     "saldo": round(nuevo, 2)})
        running[key]["balance"] = nuevo
    items = []
    total_ent = total_sal = 0.0
    for key in orden:
        info = running[key]
        rows = info["rows"]
        ent = sum(r["mov"].cantidad or 0 for r in rows if r["mov"].tipo == "E")
        sal = sum(r["mov"].cantidad or 0 for r in rows if r["mov"].tipo == "S")
        total_ent += ent
        total_sal += sal
        items.append({
            "descripcion": key[0], "und": key[1], "movs": len(rows),
            "cant_in": round(ent, 2), "cant_out": round(sal, 2),
            "saldo": round(ent - sal, 2), "rows": rows,
        })
    return {
        "insumos": len(items),
        "total_entradas": round(total_ent, 2),
        "total_salidas": round(total_sal, 2),
        "movimientos": len(movs),
        "items": items,
    }


def saldo_insumo(descripcion, excluir_id=None):
    """Saldo disponible (entradas - salidas) de un insumo, en todos los periodos."""
    q = AlmacenMovimiento.query.filter(
        AlmacenMovimiento.descripcion == (descripcion or ""))
    if excluir_id:
        q = q.filter(AlmacenMovimiento.id != excluir_id)
    saldo = 0.0
    for mv in q.all():
        saldo += (mv.cantidad or 0) if mv.tipo == "E" else -(mv.cantidad or 0)
    return round(saldo, 2)


def almacen_valorizado(mes, anio):
    """Reporte FE-08 valorizado a partir del movimiento diario de almacen."""
    movs = (AlmacenMovimiento.query
            .filter(AlmacenMovimiento.mes == mes, AlmacenMovimiento.anio == anio)
            .order_by(AlmacenMovimiento.fecha, AlmacenMovimiento.id).all())
    items = {}
    orden = []
    for m in movs:
        key = (m.descripcion, m.und)
        it = items.get(key)
        if it is None:
            it = {"descripcion": m.descripcion, "und": m.und, "oc": "",
                  "cant_in": 0.0, "cant_out": 0.0, "valor_in": 0.0,
                  "valor_out": 0.0, "filas": []}
            items[key] = it
            orden.append(key)
        pu = m.precio_unitario or 0
        cant = m.cantidad or 0
        it["filas"].append({"fecha": m.fecha, "tipo": m.tipo, "cantidad": cant,
                            "pu": pu, "valor": round(cant * pu, 2),
                            "numero_doc": m.numero_doc or "",
                            "proveedor": m.proveedor or "",
                            "responsable": m.responsable or "",
                            "actividad": m.actividad or ""})
        if m.tipo == "E":
            it["cant_in"] += cant
            it["valor_in"] += cant * pu
            if not it["oc"] and m.numero_doc:
                it["oc"] = m.numero_doc
        else:
            it["cant_out"] += cant
            it["valor_out"] += cant * pu
    result = []
    for key in orden:
        it = items[key]
        cant_in = round(it["cant_in"], 2)
        cant_out = round(it["cant_out"], 2)
        saldo = round(cant_in - cant_out, 2)
        valor_in = round(it["valor_in"], 2)
        valor_out = round(it["valor_out"], 2)
        pu = round(valor_in / cant_in, 2) if cant_in else 0
        result.append({
            "descripcion": it["descripcion"], "und": it["und"], "oc": it["oc"],
            "cant_in": cant_in, "cant_out": cant_out, "saldo": saldo,
            "pu": pu, "valor_in": valor_in, "valor_out": valor_out,
            "valor_saldo": round(valor_in - valor_out, 2),
            "filas": it["filas"],
        })
    return result


def almacen_items(mes, anio):
    """Agrupa movimientos por descripcion/und con saldos para FE-08."""
    movs = (AlmacenMovimiento.query
            .filter(AlmacenMovimiento.mes == mes, AlmacenMovimiento.anio == anio)
            .order_by(AlmacenMovimiento.fecha, AlmacenMovimiento.id).all())
    items = {}
    for m in movs:
        key = (m.descripcion, m.und)
        item = items.setdefault(key, {"descripcion": m.descripcion, "und": m.und,
                                      "entradas": [], "salidas": [], "pu": m.precio_unitario})
        if m.tipo == "E":
            item["entradas"].append(m)
        else:
            item["salidas"].append(m)
    result = []
    for key, item in items.items():
        q_in = sum(m.cantidad for m in item["entradas"])
        q_out = sum(m.cantidad for m in item["salidas"])
        pu = item["pu"] or 0
        result.append({
            "descripcion": item["descripcion"],
            "und": item["und"],
            "entradas": item["entradas"],
            "salidas": item["salidas"],
            "cant_in": q_in,
            "cant_out": q_out,
            "saldo": round(q_in - q_out, 2),
            "valor_in": round(q_in * pu, 2),
            "valor_out": round(q_out * pu, 2),
            "valor_saldo": round((q_in - q_out) * pu, 2),
        })
    return result


def pascua(anio):
    """Fecha del Domingo de Pascua segun el algoritmo de Meeus/Jones/Butcher."""
    a = anio % 19
    b, c = divmod(anio, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(anio, mes, dia)


def feriados_anio(anio):
    """Feriados nacionales del Peru para el anio dado (tuplas (mes, dia))."""
    feriados = {(1, 1), (5, 1), (6, 29), (7, 28), (7, 29),
                (8, 30), (10, 8), (11, 1), (12, 8), (12, 25)}
    pasc = pascua(anio)
    ju_santo = pasc - timedelta(days=3)
    vi_santo = pasc - timedelta(days=2)
    feriados.add((ju_santo.month, ju_santo.day))
    feriados.add((vi_santo.month, vi_santo.day))
    if anio == 2026:
        feriados.add((12, 24))
        feriados.add((12, 31))
    return feriados


def calendario_mes(anio, mes):
    """Dias del mes con su dia de semana y marcado de domingo/feriado.

    Devuelve lista de dicts: {dia, letra, nombre, es_domingo, es_feriado}.
    """
    n_dias = calendar.monthrange(anio, mes)[1]
    feriados = feriados_anio(anio)
    out = []
    for dia in range(1, n_dias + 1):
        weekday = date(anio, mes, dia).weekday()
        out.append({
            "dia": dia,
            "letra": DIAS_LETRA[weekday],
            "nombre": DIAS_NOMBRE[weekday],
            "es_domingo": weekday == 6,
            "es_feriado": (mes, dia) in feriados,
        })
    return out


def resumen_tareo(trabajadores, calendario):
    """Asistencias por cargo por dia + total general, para el resumen del tareo."""
    cargos = []
    por_cargo = {}
    totales = [0] * len(calendario)
    for t in trabajadores:
        cargo = (t.cargo or "").strip().upper() or "SIN CARGO"
        if cargo not in por_cargo:
            por_cargo[cargo] = [0] * len(calendario)
            cargos.append(cargo)
        marcados = t.dias_lista
        for dia in marcados:
            if 1 <= dia <= len(calendario):
                por_cargo[cargo][dia - 1] += 1
                totales[dia - 1] += 1
    filas = [{"cargo": c, "por_dia": por_cargo[c]} for c in cargos]
    return filas, totales
