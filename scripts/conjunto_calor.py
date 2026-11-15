#!/usr/bin/env python3
"""16 miembros del conjunto (0-15, bloque A) con flujo de calor + SST OISST frente a los mismos sin calor (revision V1, A1 opcional).
Lectura fijada en docs/protocolo_metricas_conjunto.md (15-nov (2)). Solo numpy.
  python scripts/conjunto_calor.py [runs/conjunto_calor] [runs/conjunto]  -> resultados/conjunto_calor.txt
  python scripts/conjunto_calor.py --prueba"""
import csv, json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
PARAMS = ("carta", "alfa", "semilla", "datum", "cd", "vfac", "vrot", "mfac", "qfac")
ZONAS = ("canal", "cuenca", "Marimelena", "Guasabacoa", "Atares")
N = 16


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
    texto = "\n".join(out); print(texto); (RAIZ / "resultados" / "conjunto_calor.txt").write_text(texto + "\n")
