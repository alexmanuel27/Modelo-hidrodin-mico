#!/usr/bin/env python3
"""Transcripcion de JICA 2004, vol. V, cap. 4 (tablas 4.8, 4.11, 4.19, 4.20, 4.18 y posiciones de la fig. 4.25)
a datos/observaciones/jica2004_vol5.csv. Protocolo: docs/protocolo_jica_observaciones.md, seccion 1.
Los valores se guardan tal como estan impresos (texto, sin convertir). pagina_pdf = "parte:pagina" del PDF
datos/batimetria/fuentes/jica_2004_vol5_<parte>.pdf (capa de texto, `pdftotext -layout`).
  python scripts/obs_jica_transcribir.py              -> escribe el CSV y lo comprueba contra la capa de texto
  python scripts/obs_jica_transcribir.py --comprobar  -> solo comprueba el CSV existente"""
import csv, re, subprocess, sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "datos" / "observaciones" / "jica2004_vol5.csv"
PDFS = RAIZ / "datos" / "batimetria" / "fuentes"
COLS = ["tabla", "pagina_informe", "pagina_pdf", "estacion", "variable", "nivel_m", "fase", "mes", "valor", "unidad", "nota"]
PAG = {"4.8": ("M4-13", "02:13"), "4.11": ("M4-16", "02:16"), "4.18": ("M4-42", "03:1"), "Fig. 4.25": ("M4-43", "03:2"),
       "4.19": ("M4-44", "03:6"), "4.20": ("M4-48", "03:7")}
filas = []


def f(tabla, estacion, variable, nivel, fase, mes, valor, unidad, nota=""):
    filas.append(dict(tabla=tabla, pagina_informe=PAG[tabla][0], pagina_pdf=PAG[tabla][1], estacion=estacion, variable=variable,
                      nivel_m=nivel, fase=fase, mes=mes, valor=valor, unidad=unidad, nota=nota))


# --- Tabla 4.19: salinidad de toda la bahia (resumen de las 11 estaciones), sup / 5 m / 10 m, creciente y bajamar
N19 = "rotulada 'maxima' en la tabla; por los valores es el minimo"
T419 = [("superficie", "creciente", (("30.2", "31.4"), ("34.8", "34.3"), ("32.4", "32.2"), ("1.5", "1.0"))),
        ("superficie", "bajamar", (("32.0", "23.1"), ("35.2", "34.0"), ("33.3", "30.3"), ("0.9", "3.5"))),
        ("5", "creciente", (None, None, ("35.8", "35.7"), ("0.1", "0.2"))), ("5", "bajamar", (None, None, ("35.9", "35.5"), ("0.1", "0.3"))),
        ("10", "creciente", (None, None, ("35.9", "35.9"), ("0.1", "0.1"))), ("10", "bajamar", (None, None, ("36.0", "35.8"), ("0.1", "0.1")))]
def f419(nivel, fase, var, mes, x, nota=""):
    n = nota + ("; " if nota else "") + "unidad impresa mg/kg, sin convertir"
    if nivel == "10" and fase == "bajamar": n += "; rotulada 'Capa media (10 m)' en la tabla; por posicion es 10 m"
    f("4.19", "bahia", "salinidad_" + var, nivel, fase, mes, x, "mg/kg", n)


for nivel, fase, (bajo, alto, media, sd) in T419:
    for var, v, nota in (("extremo_bajo", bajo, N19), ("extremo_alto", alto, "")):
        for mes, x in zip(("2002-10", "2002-12"), v or ()): f419(nivel, fase, var, mes, x, nota)
    for mes, m, d in zip(("2002-10", "2002-12"), media, sd):
        f419(nivel, fase, "media", mes, m); f419(nivel, fase, "sd", mes, d)

# --- Tabla 4.20: velocidades medias (modulo, sin sentido) por nivel; bahia en creciente/bajamar y estaciones 1, 3, 5 en 24 h
T420 = [("bahia", "creciente", "superficie", (("8.6", "6.5"), ("4.5", "2.0"))), ("bahia", "creciente", "5", (("7.2", "6.6"), ("8.4", "4.8"))),
        ("bahia", "creciente", "10", (("5.0", "5.0"), ("5.3", "2.7"))), ("bahia", "bajamar", "superficie", (("5.2", "3.4"), ("8.7", "3.7"))),
        ("bahia", "bajamar", "5", (("4.5", "2.4"), ("6.2", "2.3"))), ("bahia", "bajamar", "10", (("2.5", "1.8"), ("4.8", "3.3"))),
        ("1", "media_24h", "superficie", (("11.5", "5.2"), ("15.9", "7.8"))), ("1", "media_24h", "5", (("11.0", "7.3"), ("16.3", "5.6"))),
        ("1", "media_24h", "10", (("11.2", "6.6"), ("17.1", "7.0"))), ("3", "media_24h", "superficie", (("6.7", "2.3"), ("5.2", "2.2"))),
        ("3", "media_24h", "5", (("4.1", "1.3"), ("6.5", "5.9"))), ("3", "media_24h", "10", (("4.5", "1.7"), ("3.6", "4.3"))),
        ("5", "media_24h", "superficie", (("8.2", "4.9"), ("5.6", "2.0"))), ("5", "media_24h", "5", (("7.9", "5.1"), ("5.8", "5.2"))),
        ("5", "media_24h", "10", (("7.7", "5.0"), ("3.9", "4.3")))]
for est, fase, nivel, (o, d) in T420:
    for mes, (m, sd) in zip(("2002-10", "2002-12"), (o, d)):
        nota = "solo modulo: la tabla no da el sentido" + ("; tercera fila de la estacion 5 rotulada '5 m' (repetida); asignada a 10 m por posicion; dudoso" if (est, nivel) == ("5", "10") else "")
        f("4.20", est, "velocidad_media", nivel, fase, mes, m, "cm/s", nota)
        f("4.20", est, "velocidad_sd", nivel, fase, mes, sd, "cm/s", nota)

# --- Tabla 4.8: fuentes del modelo de JICA (x, y en celdas de 30 m de su malla de 130 x 130; z = capa)
T48 = [("Luyano", "S1", 80, 19, 3, "1.329"), ("Martin Perez", "S2", 129, 19, 3, "0.719"), ("Tadeo", "S3", 116, 82, 3, "0.093"),
       ("San Nicolas", "S4", 41, 12, 3, "0.099"), ("Arroyo Matadero", "S5", 43, 10, 3, "0.900"), ("Agua Dulce", "S6", 51, 1, 3, "0.500"),
       ("Refineria Nico Lopez (1)", "S7", 115, 91, 3, "0.010"), ("Refineria Nico Lopez (2)", "S8", 112, 99, 3, "0.037"),
       ("Refineria Nico Lopez (3)", "S9", 112, 101, 3, "0.037"), ("Refineria Nico Lopez (4)", "S10", 110, 115, 3, "0.010")]
for nombre, sid, x, y, z, q in T48:
    e = f"{sid} {nombre}"
    f("4.8", e, "x_celda", "", "", "", str(x), "celda"); f("4.8", e, "y_celda", "", "", "", str(y), "celda")
    f("4.8", e, "z_capa", "", "", "", str(z), "capa"); f("4.8", e, "caudal", "", "", "", q, "m3/s"); f("4.8", e, "temperatura", "", "", "", "27", "C"); f("4.8", e, "salinidad", "", "", "", "1", "per mil")

# --- Tabla 4.11: temperatura y salinidad por zona y posicion vertical (2001-06 sin fase; 2001-11 pleamar y bajamar)
T411 = [("Canal de Entrada", "surface 28.3 33.37 27.0 35.46 26.2 34.53 / middle 28.2 35.33 26.8 36.27 27.0 36.41 / bottom 28.6 36.41 26.4 36.25 27.0 36.29"),
        ("Atares", "surface 28.3 29.93 27.0 27.11 26.4 21.37 / middle 28.6 35.86 27.0 36.09 26.8 36.33 / bottom 28.1 36.21 27.0 36.19 27.0 35.16"),
        ("Guasabacoa", "surface 28.1 34.12 27.2 36.03 27.0 35.57 / middle 28.6 36.00 27.0 36.19 26.8 35.52 / bottom 28.7 36.13 27.0 36.33 26.6 35.87"),
        ("Marimelena", "surface 28.3 35.15 27.0 36.15 26.8 35.77 / middle 28.4 35.55 27.0 36.22 27.0 36.00 / bottom 28.8 35.46 27.0 36.11 27.0 36.26"),
        ("Centro de la Bahia", "surface 28.7 33.57 27.0 35.02 26.8 34.87 / middle 28.9 33.99 26.8 36.00 27.0 35.97 / bottom 28.6 36.13 26.8 35.92 26.8 36.32"),
        ("P. del Chivo", "surface 28.3 35.56 - - - - 27.0 35.46 / middle 28.4 33.09 - - - - 26.8 36.35 / bottom 28.5 36.74 - - - - 26.8 36.41"),
        ("Caleta de San Lazaro", "surface 28.3 36.00 - - - - 27.0 36.10 / middle 28.6 36.41 - - - - 27.0 36.33 / bottom 28.8 36.36 - - - - 27.0 36.43")]
for est, s in T411:
    for bloque in s.split(" / "):
        t = bloque.split(); nivel, v = t[0], t[1:]
        if "-" in v: v = v[:2] + [None] * 2 + v[6:]          # sin pleamar: 4 guiones
        for (mes, fase), (T, S) in zip((("2001-06", "otra"), ("2001-11", "creciente"), ("2001-11", "bajamar")), zip(v[0::2], v[1::2])):
            if T is None: continue
            f("4.11", est, "temperatura", nivel, fase, mes, T, "C"); f("4.11", est, "salinidad", nivel, fase, mes, S, "per mil")

# --- Tabla 4.18 (especificacion de niveles) y fig. 4.25 (posiciones de las 12 estaciones en la malla de la figura)
f("4.18", "todas", "nivel_superficie", "0.5", "", "", "0.5", "m bajo la superficie", "la tabla 4.19/4.20 rotula los niveles 'superficie', '5 m' y '10 m'")
f("4.18", "todas", "nivel_fondo", "", "", "", "1.0", "m sobre el fondo", "la tabla 4.19/4.20 rotula '10 m'; nivel medio sin profundidad numerica")
F425 = {1: ("7.13", "42.57", "circulo"), 2: ("35.98", "46.72", "circulo"), 3: ("37.33", "42.86", "circulo"), 4: ("43.45", "45.04", "azul"),
        5: ("30.47", "36.07", "circulo"), 6: ("34.58", "37.86", "circulo"), 7: ("36.67", "30.55", "azul"), 8: ("31.57", "23.79", "circulo"),
        9: ("26.91", "14.20", "azul"), 10: ("38.82", "23.16", "circulo"), 11: ("46.42", "15.40", "circulo")}
for k, (x, y, tipo) in F425.items():
    n = f"posicion leida por deteccion de pixeles en la pagina (marco x 0-60, y 0-65), +-0.2 u; marcador {tipo} ({'cerca de punto PNUD-PNUMA-UNESCO 1985' if tipo == 'circulo' else 'punto adicional'}); unidad de la figura sin escala impresa"
    f("Fig. 4.25", str(k), "x_figura", "", "", "", x, "u_fig", n); f("Fig. 4.25", str(k), "y_figura", "", "", "", y, "u_fig", n)
f("Fig. 4.25", "12", "posicion", "", "", "", "aprox. 500 m de la boca de la bahia", "texto", "sin coordenadas en la figura; lugar de referencia")


def texto(parte, pag):
    p = PDFS / f"jica_2004_vol5_{parte}.pdf"
    return subprocess.run(["pdftotext", "-layout", "-f", str(pag), "-l", str(pag), str(p), "-"], capture_output=True, text=True, check=True).stdout


NUM = re.compile(r"(?<![A-Za-z\d])\d+(?:\.\d+)?")
BLOQUES = {"4.8": (r"Luyano", r"\* Net discharge", []), "4.11": (r"Canal de Entrada", r"Tabla 4\.12", []),
           "4.19": (r"Capa de superficie- crecida", r"Las Figuras 4\.27", [r"\(\d+ m\)"]),
           "4.20": (r"Marea de Crecida", r"En general", [r"\b\d+ ?m\b", r"Estaci[oó]n \d", r"de \d+ horas"])}


def comprobar():
    leidas = list(csv.DictReader(open(CSV)))
    assert all(set(r) == set(COLS) for r in leidas)
    for tabla, (ini, fin, quitar) in BLOQUES.items():
        parte, pag = PAG[tabla][1].split(":")
        t = texto(parte, int(pag)); a, b = re.search(ini, t).start(), re.search(fin, t).start()
        blq = t[a:b]
        for q in quitar: blq = re.sub(q, "", blq)
        esperado = NUM.findall(blq)                              # en el orden impreso
        obtenido = [r["valor"] for r in leidas if r["tabla"] == tabla]
        ok = esperado == obtenido
        print(f"tabla {tabla}: {len(obtenido)} valores en el CSV, {len(esperado)} numeros en el texto impreso, mismo orden -> {'ok' if ok else 'DISTINTO'}")
        if not ok:
            print("  solo en el texto:", dict(Counter(esperado) - Counter(obtenido))); print("  solo en el CSV:", dict(Counter(obtenido) - Counter(esperado))); sys.exit(1)


if __name__ == "__main__":
    if sys.argv[1:] != ["--comprobar"]:
        with open(CSV, "w", newline="") as fh:
            w = csv.DictWriter(fh, COLS); w.writeheader(); w.writerows(filas)
        print(f"{len(filas)} filas -> {CSV.relative_to(RAIZ)}")
    comprobar()
