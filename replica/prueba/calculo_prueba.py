"""Cálculo de prueba: obra PARTIDAS_PLADUR con la Tarifa Pladur marzo 2026 (Zona 1).

PROVISIONAL. Los precios salen de la tarifa. Los consumos por m² son
estimaciones estándar del sector, NO del manual técnico de Pladur: hay que
sustituirlos por los del manual antes de usar esto en un presupuesto real.

Uso: python3 calculo_prueba.py  ->  escribe presupuesto_prueba.xlsx al lado.
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

DTO_PLACAS = 0.48
DTO_RESTO = 0.39

# Materiales: código tarifa, nombre, unidad, precio tarifa Zona 1 por unidad, familia.
# None = no está en la tarifa Pladur (hay que poner el precio del proveedor).
MAT = {
    "N13":   ("161309", "Placa Pladur N 13 (12,5) BA", "m2", 4.71, "placa"),
    "N15":   ("161310", "Placa Pladur N 15 BA", "m2", 5.42, "placa"),
    "H1_13": ("161328", "Placa Pladur H1 13 (12,5) BA", "m2", 8.51, "placa"),
    "H1_15": ("161330", "Placa Pladur H1 15 BA", "m2", 9.63, "placa"),
    "DF25":  ("-", "Placa DF 25 mm (no está en tarifa)", "m2", None, "placa"),
    "M48":   ("296464", "Montante 48/35 Z1", "m", 1.23, "resto"),
    "M70":   ("296483", "Montante 70/35 Z1", "m", 1.50, "resto"),
    "M90":   ("296566", "Montante 90/45 XL Z1", "m", 2.18, "resto"),
    "M100":  ("296568", "Montante 100/45 XL Z1", "m", 2.37, "resto"),
    "M125":  ("296569", "Montante 125/45 XL Z1", "m", 2.74, "resto"),
    "C48":   ("296460", "Canal 48/30 Z1", "m", 1.03, "resto"),
    "C70":   ("296472", "Canal 70/30 Z1", "m", 1.30, "resto"),
    "C90":   ("296574", "Canal 90/47 XL Z2", "m", 2.26, "resto"),
    "C100":  ("296575", "Canal 100/47 XL Z2", "m", 2.55, "resto"),
    "C125":  ("296576", "Canal 125/47 XL Z2", "m", 3.00, "resto"),
    "T45":   ("162073", "Perfil T-45", "m", 0.98, "resto"),
    "HORQ":  ("4071217", "Horquilla T-45", "ud", 0.27, "resto"),
    "VAR":   ("4070864", "Varilla roscada M6 1 m", "ud", 0.80, "resto"),
    "PL75":  ("4070784", "Pieza polivalente PL-75 (arriostramiento)", "ud", 0.47, "resto"),
    "CABA":  ("-", "Pieza de caballete techo (no localizada en tarifa)", "ud", None, "resto"),
    "TOR25": ("4070684", "Tornillo PM 3,5x25", "ud", 9.74 / 1000, "resto"),
    "TOR35": ("4070683", "Tornillo PM 3,5x35", "ud", 12.04 / 1000, "resto"),
    "TOR55": ("4070629", "Tornillo PM 3,9x55", "ud", 10.32 / 500, "resto"),
    "JN":    ("161691", "Pasta JN secado normal", "kg", 21.80 / 18, "resto"),
    "JH":    ("161714", "Pasta JH ambientes húmedos", "kg", 36.13 / 20, "resto"),
    "CINTA": ("4070640", "Cinta de juntas", "m", 6.99 / 150, "resto"),
    "GUARD": ("4070692", "Cinta guardavivos", "m", 16.31 / 30, "resto"),
    "BA50":  ("4070676", "Banda acústica 50 mm", "m", 13.35 / 20, "resto"),
    "BA75":  ("4070677", "Banda acústica 75 mm", "m", 18.67 / 20, "resto"),
    "REG":   ("4070964", "Trampilla Accesso Estándar 15 mm 600x600", "ud", 47.31, "resto"),
    "LM40":  ("-", "Lana mineral 70 kg/m3 40 mm (no Pladur)", "m2", None, "resto"),
    "LM60":  ("-", "Lana mineral 70 kg/m3 60 mm (no Pladur)", "m2", None, "resto"),
    "LM80":  ("-", "Lana mineral 70 kg/m3 80 mm (no Pladur)", "m2", None, "resto"),
}

PERFIL = {48: ("M48", "C48", "BA50"), 70: ("M70", "C70", "BA50"), 90: ("M90", "C90", "BA75"),
          100: ("M100", "C100", "BA75"), 125: ("M125", "C125", "BA75")}
PLACA = {"A": "N13", "H1": "H1_13", "DF": "DF25"}


def cara(tipo, espesor_placa=12.5):
    """Consumos de una cara de 2 placas: placas, tornillos, pasta y cinta (estimación estándar).

    1ª capa: 6 tornillos/m² de longitud >= placa + 10 mm; 2ª capa: 13 tornillos/m² >= 2 placas + 10 mm.
    """
    pasta = "JH" if tipo == "H1" else "JN"
    if espesor_placa <= 12.5:
        tornillos = {"TOR25": 6, "TOR35": 13}
    else:
        tornillos = {"TOR35": 6, "TOR55": 13}
    return sumar({PLACA[tipo]: 2.1, pasta: 0.35, "CINTA": 1.5}, tornillos)


def sumar(*recetas):
    out = {}
    for rec in recetas:
        for k, v in rec.items():
            out[k] = out.get(k, 0) + v
    return out


def tabique(perfil, cara1, cara2, lana, sep=400):
    m, c, banda = PERFIL[perfil]
    estructura = {m: 2.6 if sep == 400 else 1.75, c: 0.95, banda: 0.95, lana: 1.05}
    return sumar(estructura, cara(cara1), cara(cara2))


def trasdosado(perfil, tipo, lana, sep=400, espesor_placa=12.5):
    m, c, banda = PERFIL[perfil]
    estructura = {m: 2.6 if sep == 400 else 1.75, c: 0.95, banda: 0.95, lana: 1.05, "PL75": 1.0}
    return sumar(estructura, cara(tipo, espesor_placa))


def techo(placa, pasta):
    return {placa: 1.05, "T45": 3.1, "C48": 0.4, "HORQ": 1.0, "VAR": 2.0, "CABA": 2.1,
            "TOR25": 17, pasta: 0.35, "CINTA": 1.5}


TABICA = {"N15": 1.05, "C48": 2.0, "M48": 1.7, "TOR25": 15, "JN": 0.35, "CINTA": 1.5, "GUARD": 1.0}

# Partidas de la obra: código, ud, descripción corta, medición, receta (None = precio manual).
PARTIDAS = [
    ("B2010-T123.0980", "m2", "Fachada casetones cubierta F11", 364.37, None),
    ("C1010-T131.2500", "m2", "Tab. 175/400 (2x12.5A+125+2x12.5A) DR04", 133.49, tabique(125, "A", "A", "LM80")),
    ("C1010-T131.2940", "m2", "Tab. 175/400 (2x12.5A+125+2x12.5H1) DR03", 192.82, tabique(125, "A", "H1", "LM80")),
    ("C1010-T131.3040", "m2", "Tab. 120/400 (2x12.5H1+70+2x12.5H1) DR05", 63.27, tabique(70, "H1", "H1", "LM60")),
    ("C1010-T131.3500", "m2", "Tab. 150/400 (2x12.5H1+100+2x12.5H1) DR01", 10.06, tabique(100, "H1", "H1", "LM80")),
    ("C1010-T131.3600", "m2", "Tab. 175/400 (2x12.5H1+125+2x12.5H1) DR02", 28.56, tabique(125, "H1", "H1", "LM80")),
    ("C1010-T131.4501", "m2", "Trasd. 150/400 (100)(2x25DF) EI-60 LI06", 634.78, trasdosado(100, "DF", "LM80", espesor_placa=25)),
    ("C1010-T131.7000", "m2", "Trasd. 73/600 (48)(2x12.5A) LI03", 589.99, trasdosado(48, "A", "LM40", sep=600)),
    ("C1010-T131.7100", "m2", "Trasd. 73/600 (48)(2x12.5H1) LI01", 289.08, trasdosado(48, "H1", "LM40", sep=600)),
    ("C1010-T131.7500", "m2", "Trasd. 95/400 (70)(2x12.5H1) LI02", 283.78, trasdosado(70, "H1", "LM60")),
    ("C1010-T131.7800", "m2", "Trasd. 115/400 (90)(2x12.5A) LI04", 1614.44, trasdosado(90, "A", "LM80")),
    ("C1010-T136.3200", "m2", "Barrera fónica lana mineral MF01", 49.87, None),
    ("C1070-T168.4440", "m2", "F.T. continuo H1 15 mm tipo 10", 130.95, techo("H1_15", "JH")),
    ("C1070-T168.4500", "m2", "F.T. continuo A 15 mm tipo 11", 78.05, techo("N15", "JN")),
    ("C1070-T168.4900", "m", "Tabica en falso techo placa 15 mm", 16.03, TABICA),
    ("C1070-T168.4950", "ud", "Registro F.techo continuo 600x600", 9.00, {"REG": 1}),
]


def precio_neto(clave):
    _, _, _, pvp, fam = MAT[clave]
    if pvp is None:
        return None
    return pvp * (1 - (DTO_PLACAS if fam == "placa" else DTO_RESTO))


def main():
    wb = Workbook()
    res = wb.active
    res.title = "Resumen"
    det = wb.create_sheet("Detalle")
    ped = wb.create_sheet("Materiales")
    bold = Font(bold=True)
    aviso = PatternFill("solid", fgColor="FFF2CC")

    res.append(["PRUEBA PROVISIONAL - consumos estimados, no del manual Pladur. Tarifa marzo 2026 Zona 1. "
                f"Dto placas {DTO_PLACAS:.0%}, resto {DTO_RESTO:.0%}. Solo material, sin mano de obra."])
    res.append([])
    res.append(["Código", "Ud", "Partida", "Medición", "Material €/ud", "Importe material €", "Faltan precios"])
    det.append(["Código", "Material", "Ud", "Consumo/ud partida", "PVP tarifa", "Precio neto", "€ por ud partida"])
    for c in res[3] + det[1]:
        c.font = bold

    total, pedido = 0.0, {}
    for codigo, ud, desc, medicion, receta in PARTIDAS:
        if receta is None:
            res.append([codigo, ud, desc, medicion, None, None, "precio manual (no es sistema Pladur)"])
            for c in res[res.max_row]:
                c.fill = aviso
            continue
        unit, faltan = 0.0, []
        for clave, consumo in receta.items():
            neto = precio_neto(clave)
            nombre, unidad, pvp = MAT[clave][1], MAT[clave][2], MAT[clave][3]
            pedido[clave] = pedido.get(clave, 0) + consumo * medicion
            if neto is None:
                faltan.append(nombre)
            else:
                unit += consumo * neto
            det.append([codigo, nombre, unidad, round(consumo, 3), pvp and round(pvp, 4),
                        neto and round(neto, 4), neto and round(consumo * neto, 3)])
        importe = unit * medicion
        total += importe
        res.append([codigo, ud, desc, medicion, round(unit, 2), round(importe, 2), "; ".join(faltan)])
        if faltan:
            res.cell(res.max_row, 7).fill = aviso
    res.append([])
    res.append(["", "", "TOTAL MATERIAL (con precios disponibles)", "", "", round(total, 2)])
    res.cell(res.max_row, 3).font = res.cell(res.max_row, 6).font = bold

    ped.append(["Código tarifa", "Material", "Ud", "Cantidad total", "Precio neto", "Importe €"])
    for c in ped[1]:
        c.font = bold
    for clave, cant in sorted(pedido.items(), key=lambda kv: MAT[kv[0]][1]):
        neto = precio_neto(clave)
        ped.append([MAT[clave][0], MAT[clave][1], MAT[clave][2], round(cant, 1),
                    neto and round(neto, 4), neto and round(cant * neto, 2)])

    for ws, widths in ((res, [18, 5, 46, 11, 13, 17, 60]), (det, [18, 46, 5, 18, 11, 11, 16]),
                       (ped, [14, 50, 5, 15, 12, 12])):
        for i, w in enumerate(widths):
            ws.column_dimensions[chr(65 + i)].width = w

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presupuesto_prueba.xlsx")
    wb.save(out)
    print(f"Total material con precio: {total:,.2f} €  ->  {out}")
    for r in res.iter_rows(min_row=4, values_only=True):
        if r[0]:
            print(f"{r[0]:17} {r[3]:>9} {r[1]:3} {str(r[4] or '-'):>7} €/ud {str(r[5] or '-'):>10} €  {r[6] or ''}")


if __name__ == "__main__":
    main()
