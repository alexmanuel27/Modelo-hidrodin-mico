#!/usr/bin/env python3
"""Reduccion de T y S para el diagrama dS-dT (docs/protocolo_analisis_x.md, 1). Media diaria PONDERADA POR VOLUMEN
(area del nodo x (h + eta) x media de los 16 niveles sigma, de espesor relativo igual) de la bahia y de cada ensenada.
  reduce <carpeta_corrida>   (cluster, netCDF4) -> <carpeta>/delta_st_diario.csv   (T = NaN si no se guardo temperature_N.nc)
  --prueba                   datos sinteticos"""
import csv, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
ZONAS = ("bahia", "canal", "cuenca", "Marimelena", "Guasabacoa", "Atares")     # zona 1..5 de posproceso_malla.npz; bahia = zona > 0


def masc(zona, z): return zona > 0 if z == "bahia" else zona == ZONAS.index(z)


def reduce_arrays(h, eta, S, T, zona, area, t_dias):
    """h (nn), eta (nt, nn), S y T (nt, nn, nv) o None, t_dias (nt). Devuelve (dia, {col: valor diario})."""
    w = area[None, :] * (h[None, :] + eta); out = {}
    for z in ZONAS:
        m = masc(zona, z)[None, :] * w
        for nom, F in (("S", S), ("T", T)):
            out[f"{nom}_{z}"] = np.full(len(t_dias), np.nan) if F is None else (m * F.mean(2)).sum(1) / m.sum(1)
    dia = np.floor(np.asarray(t_dias, float)).astype(int); ud = np.unique(dia)
    return ud, {k: np.array([np.nanmean(v[dia == d]) if not np.isnan(v[dia == d]).all() else np.nan for d in ud]) for k, v in out.items()}


def reduce(dirm):
    from netCDF4 import Dataset
    dirm = Path(dirm); out = dirm / "outputs"; M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); zona, area = M["zona"], M["area"]
    num = lambda p: int(p.stem.split("_")[-1]); filas = []
    for f in sorted(out.glob("out2d_*.nc"), key=num):
        n = num(f)
        try:
            with Dataset(f) as o, Dataset(out / f"salinity_{n}.nc") as s:
                t = np.asarray(o["time"][:], float) / 86400; h = np.asarray(o["depth"][:], float); eta = np.asarray(o["elevation"][:], float); S = np.asarray(s["salinity"][:], float)
            T = None
            if (out / f"temperature_{n}.nc").exists():
                with Dataset(out / f"temperature_{n}.nc") as a: T = np.asarray(a["temperature"][:], float)
        except (OSError, KeyError, IndexError) as e:
            print("dia", n, "no legible, se omite:", e); continue
        d, v = reduce_arrays(h, eta, S, T, zona, area, t)
        filas += [[int(dd)] + [v[c][i] for c in v] for i, dd in enumerate(d)]
    assert filas, f"sin dias en {out}"
    cols = [f"{a}_{z}" for z in ZONAS for a in ("S", "T")]
    with open(dirm / "delta_st_diario.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["dia"] + cols); w.writerows(filas)
    print(dirm / "delta_st_diario.csv", len(filas), "dias")


def prueba():
    nn, nv = 4, 3; zona = np.array([1, 1, 2, 0]); area = np.array([1.0, 3.0, 2.0, 5.0]); h = np.array([2.0, 4.0, 1.0, 9.0])
    eta = np.zeros((2, nn)); S = np.zeros((2, nn, nv)); S[:, 0] = 30; S[:, 1] = 36; S[:, 2] = 20; S[:, 3] = 0
    d, v = reduce_arrays(h, eta, S, None, zona, area, np.array([0.1, 0.6]))
    assert list(d) == [0] and abs(v["S_canal"][0] - (1 * 2 * 30 + 3 * 4 * 36) / (1 * 2 + 3 * 4)) < 1e-12              # canal: pesos area x h
    assert abs(v["S_cuenca"][0] - 20) < 1e-12 and abs(v["S_bahia"][0] - (2 * 30 + 12 * 36 + 2 * 20) / 16) < 1e-12 and np.isnan(v["T_bahia"][0])   # el nodo 3 (mar) no cuenta
    T = np.full((2, nn, nv), 15.0); eta2 = np.full((2, nn), 1.0); T[:, :, 0] = 12; d, v = reduce_arrays(h, eta2, S, T, zona, area, np.array([0.1, 1.2]))
    assert list(d) == [0, 1] and abs(v["T_bahia"][0] - 14.0) < 1e-12                                                      # media de 3 niveles: (12 + 15 + 15) / 3
    print("autoprueba delta_st: ok")


if __name__ == "__main__":
    prueba() if sys.argv[1:] == ["--prueba"] else reduce(sys.argv[2]) if sys.argv[1:2] == ["reduce"] else sys.exit(__doc__)
