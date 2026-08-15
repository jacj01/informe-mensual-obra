"""Carga inicial de datos tomados del INFORME FINANCIERO original."""
from datetime import date

from models import db, Proyecto, Presupuesto, Gasto, GastoDetalle, AlmacenMovimiento


def seed():
    if Proyecto.query.first() is not None:
        return

    proyecto = Proyecto(
        nombre=("MEJORAMIENTO DE LOS SERVICIOS DE APOYO AL DESARROLLO PRODUCTIVO "
                "EN LA PRODUCCIÓN Y COMERCIALIZACIÓN DE FRUTALES DE LOS PRODUCTORES "
                "DEL DISTRITO DE TORAYA, DE LA PROVINCIA DE AYMARAES, DEPARTAMENTO DE APURÍMAC."),
        cui="2599315",
        meta="017-2026",
        distrito="TORAYA",
        provincia="AYMARAES",
        departamento="APURIMAC",
        entidad="MUNICIPALIDAD DISTRITAL DE TORAYA",
        unidad_ejecutora="SUB GERENCIA DE INFRAESTRUCTURA PUBLICA Y DESARROLLO URBANO",
        aprobacion="RESOLUCION DE ALCALDIA N° 92-A-2023-MDT/AL",
        rubro="18 - CANON SOBRECANON, REGALIAS, RENTA DE ADUANAS Y PARTICIPACIONES",
        fuente="RECURSOS DETERMINADOS",
        presupuesto_total=1122926.52,
        costo_directo=728394.55,
        gastos_generales=270897.04,
        gastos_supervision=91597.50,
        elaboracion_expediente=25000.00,
        liquidacion_obra=7037.43,
        residente="ING. VICTOR RODRIGUEZ CARRASCO",
        supervisor="ING. ELIO BRICEÑO CALLALI",
        asistente="JOHN A. CONDORI JIMENEZ",
        almacenero="JOHN A. CONDORI JIMENEZ",
        responsable_almacen="ROSENDO AREVALO ANCCO",
        administrador_obra="C.P.C. MIGUEL ANGEL HUAMAN CASTRO",
        anio=2026,
        mes_actual=6,
    )
    db.session.add(proyecto)

    config = [
        # (componente, clasificador, detalle, et, 2023, 2024, 2025, pim2026)
        ("Costo Directo", "2.6.2.3.99.3", "PERSONAL", 24745.28, 1330, 9710, 0, 0),
        ("Costo Directo", "2.6.2.3.99.4", "BIENES", 240855.04, 2758, 81245.40, 12715.96, 9040),
        ("Costo Directo", "2.6.2.3.99.5", "SERVICIOS", 462794.23, 0, 56659.97, 45900, 20000),
        ("Gastos Generales", "2.6.2.3.99.3", "PERSONAL", 0, 0, 0, 0, 0),
        ("Gastos Generales", "2.6.2.3.99.4", "BIENES", 44817.04, 1651, 9602, 0, 0),
        ("Gastos Generales", "2.6.2.3.99.5", "SERVICIOS", 226080.00, 12090, 48120, 102640, 48197),
        ("Gastos de Supervisión", "2.6.2.3.99.3", "PERSONAL", 0, 0, 0, 0, 0),
        ("Gastos de Supervisión", "2.6.2.3.99.4", "BIENES", 1597.50, 0, 194.50, 0, 0),
        ("Gastos de Supervisión", "2.6.2.3.99.5", "SERVICIOS", 90000.00, 2500, 11250, 3416.66, 12500),
        ("Elaboración de Expediente Técnico", "2.6.8.1.3.1",
         "ELABORACION DE EXPEDIENTE TECNICO", 25000.00, 25000, 0, 0, 0),
        ("Liquidación de Obra", "LIQUIDACION", "COSTO DE LIQUIDACION", 7037.43, 0, 0, 0, 0),
    ]
    for c in config:
        db.session.add(Presupuesto(
            componente=c[0], clasificador=c[1], detalle=c[2],
            et=c[3], ejec2023=c[4], ejec2024=c[5], ejec2025=c[6], pim2026=c[7]))

    # ------------------------------------------------------------------
    # Gastos 2026 (reproduccion del informe original)
    # ------------------------------------------------------------------
    def gasto(orden, fecha, siaf, tipo, num, proveedor, detalle, und, cant, pu,
              clasif, comp, mes):
        g = Gasto(
            orden=orden, fecha=date(*fecha), siaf=siaf, tipo_doc=tipo, num_doc=num,
            proveedor=proveedor, clasificador=clasif, componente=comp,
            mes=mes, anio=2026, devengado=True)
        g.detalles.append(GastoDetalle(
            detalle=detalle, und=und, cantidad=cant, precio_unitario=pu, orden=1))
        return g

    # MARZO 2026 - Costo Directo / Bienes (equipamiento de almacen) => 3740.20
    mar_bienes = [
        ("MANDIL DE DRIL BORDADO", 8, 30),
        ("ACEITE VEGETAL COMESTIBLE", 12, 9.2),
        ("ARROZ SUPERIOR", 50, 4.5),
        ("AZUCAR RUBIA DOMESTICA", 50, 4.5),
        ("FIDEO CORTO", 10, 5.8),
        ("CUCHARON DE ACERO INOXIDABLE 60 ML APROX", 1, 11.1),
        ("MANGUERA DE POLIETILENO 3/4 IN X 100M", 10, 141),
        ("OLLA DE ACERO INOXIDABLE 50L", 7, 161),
        ("PALA TIPO CUCHARA DE METAL CON MANGO DE MADERA", 4, 28.8),
        ("MALLA CUADRADA", 1, 149.5),
        ("PORTA CUBIERTOS DE PLASTICO CON TAPA", 6, 11.5),
    ]
    for i, (det, cant, pu) in enumerate(mar_bienes, start=1):
        db.session.add(gasto(i, (2026, 3, 20), 100 + i, "O/C", 20 + i,
                             "INVERSIONES MERYVAL E.I.R.L.", det, "UND", cant, pu,
                             "2.6.2.3.99.4", "Costo Directo", 3))

    # ABRIL 2026
    abr = [
        (1, (2026, 4, 10), 155, "O/S", 55, "TRUJILLO GOMERO GILBERTO",
         "SERVICIO DE MOVILIDAD", "SERV", 1, 2300, "2.6.2.3.99.5", "Costo Directo"),
        (2, (2026, 4, 15), 156, "O/S", 56, "RODRIGUEZ CARRASCO VICTOR",
         "SERVICIO DE RESIDENCIA DE OBRA - ENERO/FEBRERO", "SERV", 1, 24400,
         "2.6.2.3.99.5", "Gastos Generales"),
        (3, (2026, 4, 18), 157, "O/S", 57, "BRICEÑO CALLALLI ELIO",
         "SERVICIO DE SUPERVISION DE OBRA - ENERO/FEBRERO", "SERV", 1, 7500,
         "2.6.2.3.99.5", "Gastos de Supervisión"),
    ]
    for o, f, s, t, n, prov, det, u, ca, pu, cl, co in abr:
        db.session.add(gasto(o, f, s, t, n, prov, det, u, ca, pu, cl, co, 4))

    # MAYO 2026
    may = [
        (1, (2026, 5, 8), 200, "O/S", 60, "TRUJILLO GOMERO GILBERTO",
         "SERVICIO DE MOVILIDAD", "SERV", 1, 500, "2.6.2.3.99.5", "Costo Directo"),
        (2, (2026, 5, 12), 201, "O/S", 61, "RODRIGUEZ CARRASCO VICTOR",
         "SERVICIO DE RESIDENCIA DE OBRA - MARZO", "SERV", 1, 7863.33,
         "2.6.2.3.99.5", "Gastos Generales"),
    ]
    for o, f, s, t, n, prov, det, u, ca, pu, cl, co in may:
        db.session.add(gasto(o, f, s, t, n, prov, det, u, ca, pu, cl, co, 5))

    # JUNIO 2026 (Manifiesto de Gasto del informe)
    jun_bienes = [
        ("BALDE DE PLASTICO CON TAPA X 8 L", 4, 14.5),
        ("CAJA ORGANIZADORA DE PLASTICO PARA VERDURA 38.6 cm X 51.2 cm X 69.7 cm DE 3 NIVELES", 4, 52),
        ("CUCHARA DE ACERO INOXIDABLE 60 mL APROX.", 4, 25),
        ("ESCURRIDOR DE PLASTICO CON TAPA DE 2.5 L", 4, 65),
        ("JARRA DE PLASTICO CON TAPA DE 2.5 L", 4, 14.5),
        ("JUEGO DE COLADORES DE PLASTICO X 5 PIEZAS", 4, 18),
        ("MANGUERA DE POLIETILENO 3/4 in X 100 m", 5, 95),
        ("OLLA DE ACERO INOXIDABLE 50 L", 4, 445),
        ("PALA TIPO CUCHARA DE METAL CON MANGO DE MADERA", 4, 29),
        ("PORTA CUBIERTOS DE PLASTICO CON TAPA", 6, 10),
        ("RASTRILLO DE METAL 14 DIENTES 137 cm", 5, 32),
        ("MANDIL DE DRIL BORDADO", 8, 30),
    ]
    proveedores = {11: "INVERSIONES MERYVAL E.I.R.L.", 12: "RINCON PEREZ SIDO"}
    for i, (det, cant, pu) in enumerate(jun_bienes, start=1):
        prov = proveedores.get(i, "INVERSIONES MERYVAL E.I.R.L.")
        num = 44 if i <= 11 else 47
        siaf = 202 if i <= 11 else 156
        db.session.add(gasto(i, (2026, 6, 21), siaf, "O/C", num, prov, det, "UND",
                             cant, pu, "2.6.2.3.99.4", "Costo Directo", 6))

    jun_serv = [
        (1, (2026, 6, 21), 203, "O/S", 92, "TRUJILLO GOMERO GILBERTO",
         "SERVICIO DE MOVILIDAD", 300),
        (2, (2026, 6, 22), 107, "O/S", 63, "LEON CRUZ ALEXANDER",
         "ALQUILER DE EQUIPO DE SONIDO", 900),
    ]
    for o, f, s, t, n, prov, det, imp in jun_serv:
        db.session.add(gasto(o, f, s, t, n, prov, det, "SERV", 1, imp,
                             "2.6.2.3.99.5", "Costo Directo", 6))

    jun_gg = [
        (1, (2026, 6, 25), 318, "O/S", 146, "RODRIGUEZ CARRASCO VICTOR",
         "SERVICIO DE RESIDENCIA DE OBRA - MARZO", 3500),
        (2, (2026, 6, 25), 317, "O/S", 147, "BRICEÑO CALLALLI ELIO",
         "SERVICIO DE SUPERVISION DE OBRA - MARZO", 2500),
    ]
    for o, f, s, t, n, prov, det, imp in jun_gg:
        db.session.add(gasto(o, f, s, t, n, prov, det, "SERV", 1, imp,
                             "2.6.2.3.99.5", "Gastos Generales", 6))

    # ------------------------------------------------------------------
    # Almacen - Junio 2026 (entradas y salidas)
    # ------------------------------------------------------------------
    for i, (det, cant, pu) in enumerate(jun_bienes, start=1):
        prov = proveedores.get(i, "INVERSIONES MERYVAL E.I.R.L.")
        num = 44 if i <= 11 else 47
        db.session.add(AlmacenMovimiento(
            descripcion=det, und="UND", fecha=date(2026, 6, 21), tipo="E",
            cantidad=cant, numero_doc=str(num), proveedor=prov,
            responsable="JOHN A. CONDORI JIMENEZ", actividad="",
            precio_unitario=pu, mes=6, anio=2026))
        db.session.add(AlmacenMovimiento(
            descripcion=det, und="UND", fecha=date(2026, 6, 26), tipo="S",
            cantidad=cant, numero_doc="PEC-001", proveedor=prov,
            responsable="ROSENDO AREVALO ANCCO",
            actividad="CAPACITACION Y COMERCIALIZACION DE FRUTALES",
            precio_unitario=pu, mes=6, anio=2026))

    db.session.commit()
