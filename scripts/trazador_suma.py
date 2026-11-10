#!/usr/bin/env python3
"""Comprobacion del control de la suma (10-nov-2026): corrida T1 con un cuarto trazador GEN_4 que entra con 1 por los tres rios a la vez.
Pregunta: por que la suma de los tres trazadores por rio (GEN_1..3) suma menos agua dulce que la salinidad (1 - S/36), un 5,4 % en T1?
  a = (sum M_i - Vf) / Vf   suma de los tres trazadores separados frente al agua dulce de la salinidad (debe reproducir el desajuste de T1)
  b = (M_4 - Vf) / Vf       el trazador de la suma frente a la salinidad
  c = (sum M_i - M_4) / M_4 los tres separados frente al de la suma
LECTURA FIJADA ANTES DE VER LOS DATOS (docs/protocolo_trazadores_rios.md, 10-nov):
  |a| < 2 %                      el desajuste no se reproduce: no concluyente.
  |a| >= 2 % y |b| < 1 %         consistente con la no linealidad del limitador TVD (el trazador de la suma sigue a la salinidad;
                                 los tres por separado no suman lo mismo).
  |a| >= 2 % y |b - a| < 1 %     el trazador de la suma tiene el mismo deficit que los tres separados: no es el limitador, es una
                                 diferencia entre el modulo de trazadores y la salinidad (fuentes, borde, ...).
  resto                          intermedio: se informan los numeros, sin conclusion.
  python trazador_suma.py <caso> [dia]      (en el cluster, con netcdf4-python)      |      python trazador_suma.py --prueba"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from trazadores_rios import S_MAR, ZONAS, VENTANA, carga

UMBRAL_REPRODUCE, UMBRAL_IGUAL = 0.02, 0.01


def compara(t, eta, C, S, prof, M):
    """C (tiempo, nodo, nivel, 4): GEN_1..3 por rio y GEN_4 = suma. Devuelve a, b, c (inventario medio de la bahia, ultimos 30 d), por zona y la lectura."""
    z, area = M["zona"], M["area"]; vol = np.maximum(prof[None] + eta, 0.0) * area[None]; Cm = C.mean(2)
    inv = lambda x, s: float((x[:, s] * vol[:, s]).sum(1).mean())                      # m3 de agua dulce en la zona/bahia, media de los instantes
    Vf = 1 - S / S_MAR; Vf = Vf.mean(2)                                                 # sin recorte (en los datos no hay S > 36)
    r = {}
    for nom, s in (("bahia", z > 0), *((nom, z == k) for k, nom in ZONAS.items())):
        v, m3, m4 = inv(Vf, s), inv(Cm[:, :, :3].sum(-1), s), inv(Cm[:, :, 3], s)
        r[nom] = dict(a=m3 / v - 1, b=m4 / v - 1, c=m3 / m4 - 1)
    a, b = r["bahia"]["a"], r["bahia"]["b"]
    r["lectura"] = ("no concluyente: el desajuste no se reproduce" if abs(a) < UMBRAL_REPRODUCE else
                    "consistente con la no linealidad del limitador TVD" if abs(b) < UMBRAL_IGUAL else
                    "el trazador de la suma tiene el mismo deficit que los tres separados: diferencia modulo de trazadores vs salinidad" if abs(b - a) < UMBRAL_IGUAL else
                    "intermedio: sin conclusion")
    return r


def prueba(M):
    n = len(M["zona"]); b = M["zona"] > 0; nt = 30; t = np.arange(nt) / 6.0
    f = np.array([0.004, 0.002, 0.0005]); C = np.zeros((nt, n, 4, 4), np.float32); C[:, b, :, :3] = f; C[:, b, :, 3] = f.sum()
    S = np.full((nt, n, 4), S_MAR, np.float32); S[:, b] = S_MAR * (1 - f.sum()); args = (t, np.zeros((nt, n)), None, S, np.full(n, 8.0), M)
    r = compara(args[0], args[1], C, *args[3:]); assert abs(r["bahia"]["a"]) < 1e-5 and r["lectura"].startswith("no concluyente"), r
    C2 = C.copy(); C2[:, :, :, :3] *= 0.95                                              # los tres separados pierden un 5 %, el de la suma sigue a la salinidad
    r = compara(args[0], args[1], C2, *args[3:]); assert abs(r["bahia"]["a"] + 0.05) < 1e-4 and abs(r["bahia"]["b"]) < 1e-5 and "TVD" in r["lectura"], r
    C3 = C * 0.95                                                                       # los cuatro pierden un 5 %: es el modulo, no el limitador
    r = compara(args[0], args[1], C3, *args[3:]); assert "modulo de trazadores" in r["lectura"], r
    print("autoprueba trazador_suma: ok")


if __name__ == "__main__":
    M = dict(np.load(Path(__file__).resolve().parent.parent / "datos" / "conjunto" / "posproceso_malla.npz"))
    if sys.argv[1] == "--prueba": prueba(M); sys.exit()
    dirm = Path(sys.argv[1]); eta, C, S, prof, n = carga(dirm, int(sys.argv[2]) if len(sys.argv) > 2 else None, ntr=4)
    t = np.arange(len(eta)) / 6.0 + (n - VENTANA); r = compara(t, eta, C, S, prof, M)
    (dirm / "trazador_suma.json").write_text(json.dumps(r, indent=1))
    print(f"dia {n}; bahia: a (suma de 3 vs salinidad) {r['bahia']['a']:+.2%}, b (trazador suma vs salinidad) {r['bahia']['b']:+.2%}, c (3 vs suma) {r['bahia']['c']:+.2%}")
    for k, v in r.items():
        if k not in ("bahia", "lectura"): print(f"  {k:11s} a {v['a']:+.2%}  b {v['b']:+.2%}  c {v['c']:+.2%}")
    print("LECTURA:", r["lectura"])
