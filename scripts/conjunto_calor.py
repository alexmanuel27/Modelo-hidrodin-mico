#!/usr/bin/env python3
"""16 miembros del conjunto (0-15, bloque A) con flujo de calor + SST OISST frente a los mismos sin calor (revision V1, A1 opcional).
Lectura fijada en docs/protocolo_metricas_conjunto.md (15-nov (2)). Solo numpy.
  python scripts/conjunto_calor.py [runs/conjunto_calor] [runs/conjunto]  -> resultados/conjunto_calor.txt
  python scripts/conjunto_calor.py --prueba"""
import csv, json, os, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
PARAMS = ("carta", "alfa", "semilla", "datum", "cd", "vfac", "vrot", "mfac", "qfac")
ZONAS = ("canal", "cuenca", "Marimelena", "Guasabacoa", "Atares")
N = int(os.environ.get("CALOR_N", 16))   # 16 (15-nov) o 64 (calor64, 16-nov: CALOR_N=64 python scripts/conjunto_calor.py -> resultados/conjunto_calor64.txt)


def rangos(x):
    """Rangos con empates promediados (carta solo toma dos valores)."""
    x = np.asarray(x, float); o = np.argsort(x, kind="stable"); r = np.empty(len(x)); i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]: j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return r


def spearman(x, y):
    return float(np.corrcoef(rangos(x), rangos(y))[0, 1])


def prueba():
    assert abs(spearman([1, 1, 2, 2], [1, 2, 3, 4]) - 0.8944) < 1e-3 and spearman(range(8), np.arange(8) ** 3) == 1.0
    print("prueba ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--prueba"]: prueba(); sys.exit()
    dc = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "runs" / "conjunto_calor"; ds = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "runs" / "conjunto"
    filas = [f for f in csv.DictReader(open(RAIZ / "datos" / "conjunto" / "diseno.csv")) if int(f["miembro"]) < N]
    X = {p: np.array([float(f[p]) for f in filas]) for p in PARAMS}
    R = {c: [json.loads((d / f"m{int(f['miembro']):04d}" / "resumen.json").read_text()) for f in filas] for c, d in (("calor", dc), ("sin", ds))}
    ok = [i for i in range(N) if not R["calor"][i].get("nan", 0) and not R["sin"][i].get("nan", 0)]
    out = [f"{len(ok)}/{N} miembros emparejados validos (calor + OISST, 120 d) frente a los mismos sin calor"]
    age = {c: np.array([R[c][i]["edad_media_d_bahia"] for i in ok]) for c in R}
    for c in ("sin", "calor"):
        a = age[c]; dv = np.array([R[c][i]["deriva_edad_bahia_d_por_d"] for i in ok])
        out.append(f"{c:5s}: edad bahia mediana {np.median(a):.2f} (P5-P95 {np.percentile(a, 5):.2f}-{np.percentile(a, 95):.2f}); P(>7 d) {np.mean(a > 7):.2f}; P(>14 d) {np.mean(a > 14):.2f}; |deriva|<=0,05: {np.sum(np.abs(dv) <= 0.05)}/{len(ok)}")
    d = age["calor"] - age["sin"]
    out.append(f"pareado: diferencia mediana (calor - sin) {np.median(d):+.2f} d; calor > sin en {np.sum(d > 0)}/{len(ok)} miembros")
    young = {c: np.mean([np.argmin([R[c][i][f"edad_media_d_{z}"] for z in ZONAS]) == 0 for i in ok]) for c in R}
    out.append(f"fraccion de miembros en que el canal es la zona mas joven: sin {young['sin']:.2f}, calor {young['calor']:.2f}")
    out.append("Spearman de la edad de la bahia con cada parametro (n = %d; |rho| >= 0,50 ~ p < 0,05):" % len(ok))
    rho = {}
    for p in PARAMS:
        rho[p] = {c: spearman(X[p][ok], age[c]) for c in R}; out.append(f"  {p:8s} sin {rho[p]['sin']:+.2f}   calor {rho[p]['calor']:+.2f}")
    mayor = max(PARAMS, key=lambda p: abs(rho[p]["calor"]))
    out.append(f"parametro con mayor |rho| con calor: {mayor} ({rho[mayor]['calor']:+.2f}); caudal (qfac) con calor {rho['qfac']['calor']:+.2f} -> "
               + ("el caudal sigue dominando (mayor |rho| y >= 0,50)" if mayor == "qfac" and abs(rho["qfac"]["calor"]) >= 0.5 else "el dominio del caudal NO se sostiene con calor en estos miembros"))
    if N > 16:   # lectura del 16-nov (calor64): desplazamiento pareado frente al rango P5-P95 de los MISMOS miembros sin calor
        pw = np.percentile(age["sin"], 95) - np.percentile(age["sin"], 5); dm = np.median(d)
        out.append(f"cociente R = diferencia pareada mediana / ancho P5-P95 sin calor = {dm:.2f} / {pw:.2f} = {dm / pw:.2f}; calor > sin en {np.mean(d > 0):.2f} de los miembros -> "
                   + ("el efecto estructural supera el rango parametrico (R > 1 y >= 0,90 de miembros)" if dm / pw > 1 and np.mean(d > 0) >= 0.9 else "no se cumple R > 1 con >= 0,90 de miembros"))
    # C1-C7 y P(edad > umbral) con las clases del protocolo (robusta >= 0,90, fragil, rechazada <= 0,10), n = 16 en cada condicion;
    # misma logica que analisis_conjunto.conclusiones (lectura fijada: si una clase cambia con calor, se informa tal cual)
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); cz = M["zona"] == 1; w = M["area"][cz]
    def sf(c, i):
        nz = np.load((dc if c == "calor" else ds) / f"m{int(filas[i]['miembro']):04d}" / "resumen.npz")
        return (nz["edad_sup"][cz] * w).sum() / w.sum() > (nz["edad_fondo"][cz] * w).sum() / w.sum()
    e = lambda c, i, z: R[c][i][f"edad_media_d_{z}"]
    C = {"C1 canal < cuenca < Guasabacoa < Atares": lambda c, i: e(c, i, "canal") < e(c, i, "cuenca") < e(c, i, "Guasabacoa") < e(c, i, "Atares"),
         "C2 Atares mas vieja que el canal": lambda c, i: e(c, i, "Atares") > e(c, i, "canal"),
         "C3 Marimelena mas vieja que la cuenca": lambda c, i: e(c, i, "Marimelena") > e(c, i, "cuenca"),
         "C4 Guasabacoa y Atares mas viejas que la cuenca": lambda c, i: min(e(c, i, "Guasabacoa"), e(c, i, "Atares")) > e(c, i, "cuenca"),
         "C5 edad de la bahia < 30 d": lambda c, i: e(c, i, "bahia") < 30, "C6 edad de la bahia < 120 d": lambda c, i: e(c, i, "bahia") < 120,
         "C7 canal: superficie mas vieja que el fondo": sf, "P edad de la bahia > 7 d": lambda c, i: e(c, i, "bahia") > 7,
         "P edad de la bahia > 14 d": lambda c, i: e(c, i, "bahia") > 14, "P edad de la bahia > 30 d": lambda c, i: e(c, i, "bahia") > 30}
    cl = lambda x: "robusta" if x >= 0.9 else "rechazada" if x <= 0.1 else "fragil"
    out.append("clases del protocolo (n = %d): conclusion | sin calor | con calor" % len(ok))
    for nom, fn in C.items():
        a, b = (np.mean([float(fn(c, i)) for i in ok]) for c in ("sin", "calor")); out.append(f"  {nom}: {a:.2f} {cl(a)} | {b:.2f} {cl(b)}" + ("   <-- CAMBIA" if cl(a) != cl(b) else ""))
    # [descriptivo, no pre-registrado] correlaciones entre parametros en estos 16 y correlacion parcial de rangos con qfac y mfac
    rr = lambda a: rangos(np.asarray(a)[ok])
    out.append("[descriptivo] rho entre parametros en estos miembros con |rho| >= 0,5: " + ", ".join(f"{a}-{b} {spearman(X[a][ok], X[b][ok]):+.2f}" for i, a in enumerate(PARAMS) for b in PARAMS[i + 1:] if abs(spearman(X[a][ok], X[b][ok])) >= 0.5))
    def parcial(y, x, z):
        res = lambda a, b: a - np.polyval(np.polyfit(b, a, 1), b)
        return float(np.corrcoef(res(rangos(y), rangos(z)), res(rangos(x), rangos(z)))[0, 1])
    for c in ("sin", "calor"):
        out.append(f"[descriptivo] {c}: rho parcial de la edad con qfac dado mfac {parcial(age[c], X['qfac'][ok], X['mfac'][ok]):+.2f}; con mfac dado qfac {parcial(age[c], X['mfac'][ok], X['qfac'][ok]):+.2f}")
    texto = "\n".join(out); print(texto); (RAIZ / "resultados" / ("conjunto_calor.txt" if N == 16 else f"conjunto_calor{N}.txt")).write_text(texto + "\n")
