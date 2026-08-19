# -*- coding: utf-8 -*-
"""Calculos de planilla de pagos de personal (obreros de Construccion Civil
y tecnicos/administrativos). Las tablas salariales estan organizadas por anio:
el sistema elige automaticamente la tabla del anio de la planilla y, si ese
anio aun no tiene tabla publicada, usa la mas reciente disponible. Cada anio
se agrega la nueva tabla oficial (Resolucion Ministerial) a este archivo.
"""

TABLA_CIVIL_POR_ANIO = {
    2026: {
        "norma": "R.M. N° 197-2025-TR (vigencia del 01/01/2026 al 31/12/2026)",
        "jornales": {
            "OPERARIO": 89.30,
            "OFICIAL": 69.75,
            "PEON": 62.80,
            "GUARDIAN": 69.75,
        },
        "buc": {  # Bonificacion Unificada de Construccion (% del jornal)
            "OPERARIO": 0.32,
            "OFICIAL": 0.30,
            "PEON": 0.30,
            "GUARDIAN": 0.30,
        },
        "movilidad": 8.60,        # movilidad por dia trabajado (S/)
        "onp": 0.13,              # descuento SNP/ONP 13%
        "afp": 0.13,              # aporte base AFP (referencial)
        "conafovicer": 0.02,      # CONAFOVICER 2%
        "vacaciones": 0.10,       # vacaciones: 10% del jornal por dia trabajado
        "cts": 0.15,              # indemnizacion por CTS: 15% del jornal por dia
        "gratif_fp": 40 / 210,    # gratif. Fiestas Patrias: 40 jornales / 210 dias (ene-jul)
        "gratif_navidad": 40 / 150,  # gratif. Navidad: 40 jornales / 150 dias (ago-dic)
        "bonif_30334": 0.09,      # bonificacion extraordinaria 9% de la gratificacion
        "dsd": 1 / 6,             # descanso semanal dominical: jornal/6 por dia trabajado
        "feriado_recargo": 2.0,   # feriado trabajado = jornal x 2 (recargo 100%)
        "nota": ("Jornales y BUC segun el Convenio CAPECO-FTCCP 2026 aprobado por la "
                 "Resolucion Ministerial N° 197-2025-TR. Los descuentos ONP/AFP se "
                 "aplican sobre el jornal + descanso semanal + BUC y la "
                 "CONAFOVICER (2%) sobre el jornal + descanso semanal."),
    },
}

# Beneficios de ley para personal tecnico/administrativo (D.L. 728) expresados
# como provision mensual sobre el sueldo.
DL728_GRATIF_MENSUAL = 1 / 6    # gratificacion: 1 sueldo por semestre -> 1/6 mensual
DL728_CTS_MENSUAL = 1 / 12      # CTS: 1 sueldo anual -> 1/12 mensual
DL728_VAC_MENSUAL = 1 / 12      # vacaciones: 1 sueldo anual -> 1/12 mensual


def red2(x):
    return round(x, 2)


def tabla_civil(anio):
    """Tabla salarial vigente para el anio dado. Si el anio no tiene tabla
    publicada aun, se devuelve la tabla del anio anterior mas reciente."""
    disponibles = sorted(TABLA_CIVIL_POR_ANIO)
    vigente = disponibles[0]
    for a in disponibles:
        if a <= anio:
            vigente = a
        else:
            break
    return TABLA_CIVIL_POR_ANIO[vigente]


def contar_dias(t, calendario):
    """Cuenta dias trabajados (lunes-sabado), domingos y feriados del tareo."""
    trabajados = domingos = feriados = 0
    for d in calendario:
        if d["dia"] not in t.dias_lista:
            continue
        if d["es_domingo"]:
            domingos += 1
        elif d["es_feriado"]:
            feriados += 1
        else:
            trabajados += 1
    return trabajados, domingos, feriados


def calcular_obrero(t, calendario, anio, mes, con_beneficios):
    """Calcula la planilla de un obrero de construccion civil."""
    tab = tabla_civil(anio)
    cargo = (t.cargo or "").strip().upper()
    jornal = tab["jornales"].get(cargo) or tab["jornales"]["PEON"]
    buc_pct = tab["buc"].get(cargo) or tab["buc"]["PEON"]
    trab, dom, fer = contar_dias(t, calendario)
    laborados = trab + fer  # dias efectivos de trabajo (el descanso D se paga via DSD)

    jornal_basico = jornal * trab
    dsd = tab["dsd"] * jornal * trab          # descanso semanal dominical
    feriados = tab["feriado_recargo"] * jornal * fer
    buc = buc_pct * jornal * laborados
    movilidad = tab["movilidad"] * laborados

    total_dias_rem = trab + dom + fer

    if con_beneficios:
        vacaciones = tab["vacaciones"] * jornal * trab
        cts = tab["cts"] * jornal * trab
        gratif_diario = tab["gratif_fp"] if mes <= 7 else tab["gratif_navidad"]
        gratificacion = gratif_diario * jornal * total_dias_rem
        bonif = tab["bonif_30334"] * gratificacion

        base_pension = jornal_basico + dsd + buc
        pension = tab["onp" if t.aporte == "ONP" else "afp"] * base_pension
        base_conaf = jornal_basico + dsd
        conaf = tab["conafovicer"] * base_conaf

        ingresos = (jornal_basico + dsd + feriados + buc + movilidad
                    + vacaciones + cts + gratificacion + bonif)
        descuentos = pension + conaf
    else:
        vacaciones = cts = gratificacion = bonif = 0
        ingresos = jornal_basico + dsd + feriados + buc + movilidad
        descuentos = 0

    return {
        "t": t,
        "cargo": cargo,
        "trab": trab, "dom": dom, "fer": fer,
        "total_dias": total_dias_rem,
        "jornal": jornal,
        "jornal_basico": red2(jornal_basico),
        "dsd": red2(dsd),
        "feriados": red2(feriados),
        "buc": red2(buc),
        "movilidad": red2(movilidad),
        "vacaciones": red2(vacaciones),
        "cts": red2(cts),
        "gratificacion": red2(gratificacion),
        "bonif": red2(bonif),
        "ingresos": red2(ingresos),
        "pension": red2(pension) if con_beneficios else 0,
        "conaf": red2(conaf) if con_beneficios else 0,
        "descuentos": red2(descuentos),
        "neto": red2(ingresos - descuentos),
    }


def calcular_tecnico(t, calendario, anio, con_beneficios):
    """Calcula la planilla de un tecnico/administrativo (D.L. 728)."""
    tab = tabla_civil(anio)
    sueldo = float(t.sueldo_mensual or 0)
    trab, dom, fer = contar_dias(t, calendario)

    if con_beneficios:
        gratif = DL728_GRATIF_MENSUAL * sueldo
        cts = DL728_CTS_MENSUAL * sueldo
        vacaciones = DL728_VAC_MENSUAL * sueldo
        pension = tab["onp" if t.aporte == "ONP" else "afp"] * sueldo
        ingresos = sueldo + gratif + cts + vacaciones
        descuentos = pension
    else:
        gratif = cts = vacaciones = 0
        ingresos = sueldo
        descuentos = 0

    return {
        "t": t,
        "cargo": (t.cargo or "").strip().upper() or "TECNICO",
        "trab": trab, "dom": dom, "fer": fer,
        "total_dias": trab + dom + fer,
        "sueldo": sueldo,
        "gratif": red2(gratif),
        "cts": red2(cts),
        "vacaciones": red2(vacaciones),
        "pension": red2(descuentos),
        "ingresos": red2(ingresos),
        "descuentos": red2(descuentos),
        "neto": red2(ingresos - descuentos),
    }
