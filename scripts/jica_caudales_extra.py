#!/usr/bin/env python3
"""JICA vol. V, tabla 4.8: ¿cambian algo los tres drenajes que faltan (Matadero 0,9; Agua Dulce 0,5; San Nicolas 0,099 m3/s)?
Lectura fijada en docs/protocolo_jica_observaciones.md (seccion 4) ANTES de calcular nada.
Estimacion con los 704 miembros ya corridos: ln(edad) = b0 + sum b_i x_i + c (ln qfac)^2; efecto de multiplicar el caudal total por
F = (2,14 + 1,499) / 2,14 sobre los miembros con qfac <= 2/F (sin extrapolar fuera del rango 0,25-2), R = efecto / (P5-P95 de los 704).
  python scripts/jica_caudales_extra.py            -> resultados/jica_caudales_extra.txt
  python scripts/jica_caudales_extra.py --prueba"""
import csv, json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
F = (2.14 + 0.9 + 0.5 + 0.099) / 2.14
ZONAS = ["bahia", "canal", "cuenca", "Marimelena", "Guasabacoa", "Atares"]
CAMBIA, NO_CAMBIA = 0.25, 0.10


def disenyo(filas):
    """Matriz de regresion: carta (0/1), alfa, datum, cd, vfac, vrot, mfac, u_semilla, ln qfac, (ln qfac)^2 y constante."""
    g = lambda k: np.array([float(f[k]) for f in filas])
    lq = np.log(g("qfac"))
    X = np.c_[np.ones(len(filas)), g("carta") == 1887, g("alfa"), g("datum"), g("cd"), g("vfac"), g("vrot"), g("mfac"), g("u_semilla"), lq, lq ** 2]
    return X.astype(float), lq


def efecto(filas, edad):
    """edad (dias, uno por miembro). Devuelve (efecto mediano en dias, R, n miembros usados, R^2 del ajuste, coef de ln qfac)."""
    X, lq = disenyo(filas); y = np.log(edad)
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    r2 = 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    usa = np.exp(lq) <= 2.0 / F
    X1 = X[usa].copy(); X1[:, -2] = lq[usa] + np.log(F); X1[:, -1] = (lq[usa] + np.log(F)) ** 2
    d = np.exp(X1 @ b) - np.exp(X[usa] @ b)
    ancho = np.percentile(edad, 95) - np.percentile(edad, 5)
    return float(np.median(d)), float(np.median(d) / ancho), int(usa.sum()), float(r2), float(b[-2])


def lectura(R):
    return "CAMBIA" if abs(R) >= CAMBIA else "NO CAMBIA" if abs(R) < NO_CAMBIA else "PARCIAL"


def prueba():
    r = np.random.default_rng(1); n = 704
    filas = [dict(carta=1879 + 8 * int(r.random() < .5), alfa=r.random(), datum=r.random() / 2, cd=.001 + .004 * r.random(), vfac=.8 + .4 * r.random(),
                  vrot=-15 + 30 * r.random(), mfac=.9 + .2 * r.random(), u_semilla=r.random(), qfac=float(np.exp(np.log(.25) + r.random() * np.log(8)))) for _ in range(n)]
    lq = np.log([f["qfac"] for f in filas]); edad = np.exp(2.5 - 0.9 * lq)            # sin ruido: efecto exacto conocido
    e, R, nu, r2, bq = efecto(filas, edad)
    q = np.array([f["qfac"] for f in filas]); u = q <= 2 / F
    esperado = float(np.median(np.exp(2.5 - 0.9 * (np.log(q[u]) + np.log(F))) - np.exp(2.5 - 0.9 * np.log(q[u]))))
    assert abs(e - esperado) < 1e-6 and r2 > 0.999999 and abs(bq + 0.9) < 1e-6 and nu == int(u.sum()), (e, esperado, r2, bq)
    assert e < 0 and lectura(-0.3) == "CAMBIA" and lectura(0.05) == "NO CAMBIA" and lectura(0.15) == "PARCIAL"
    print("prueba ok")


def main():
    D = list(csv.DictReader(open(RAIZ / "datos" / "conjunto" / "diseno.csv")))
    filas, res = [], []
    for f in D:
        p = RAIZ / "runs" / "conjunto" / f"m{int(f['miembro']):04d}" / "resumen.json"
        if p.exists():
            r = json.loads(p.read_text())
            if r.get("nan", 1) == 0: filas.append(f); res.append(r)
    eq = np.array([abs(r["deriva_edad_bahia_d_por_d"]) <= 0.05 for r in res])
    o = [f"miembros del diseno {len(D)}; con resumen y sin NaN {len(filas)}; en equilibrio (deriva <= 0,05 d/d) {int(eq.sum())}",
         f"F = (2,14 + 0,9 + 0,5 + 0,099) / 2,14 = {F:.3f}; qfac muestreado 0,25-2 (log-uniforme): F cae dentro, miembros con qfac <= {2 / F:.3f}: "
         f"{sum(float(f['qfac']) <= 2 / F for f in filas)}"]
    for etiqueta, sel in (("todos los validos", np.ones(len(filas), bool)), ("solo en equilibrio", eq)):
        o.append(f"--- {etiqueta} (n = {int(sel.sum())})")
        for z in ZONAS:
            e = np.array([r[f"edad_media_d_{z}"] for r in res])[sel]; fs = [f for f, s in zip(filas, sel) if s]
            d, R, nu, r2, bq = efecto(fs, e)
            o.append(f"  {z:11s} P5-P95 {np.percentile(e, 5):6.2f}-{np.percentile(e, 95):6.2f} d | efecto mediano {d:+6.2f} d | R = {R:+.3f} | "
                     f"coef ln qfac {bq:+.2f} | R2 {r2:.2f} | n {nu} | {lectura(R)}")
    t = "\n".join(o); print(t); (RAIZ / "resultados" / "jica_caudales_extra.txt").write_text(t + "\n")


if __name__ == "__main__":
    prueba() if sys.argv[1:] == ["--prueba"] else main()
