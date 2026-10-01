#!/usr/bin/env python3
"""Diagnostico de la prueba idealizada: nivel y corriente por zonas, hora a hora, y viento ERA5."""
from pathlib import Path
import os, sys
import numpy as np
from netCDF4 import Dataset
R = Path(__file__).resolve().parent.parent
O = Path(__file__).resolve().parent.parent / "runs" / ("prueba_idealizada" + (f"_{sys.argv[1]}" if len(sys.argv) > 1 else "")) / "outputs"
fs = sorted(O.glob("out2d_*.nc"), key=lambda p: int(p.stem.split("_")[-1]))
with Dataset(fs[0]) as nc:
    x, y = nc["SCHISM_hgrid_node_x"][:], nc["SCHISM_hgrid_node_y"][:]
def lee(k):
    out = []
    for f in fs:
        with Dataset(f) as nc:
            out.append(np.asarray(nc[k][:]) if k in nc.variables else None)
    return None if out[0] is None else np.concatenate(out)
eta, u, v = lee("elevation"), lee("depthAverageVelX"), lee("depthAverageVelY")
wx, wy = lee("windSpeedX"), lee("windSpeedY")
if wx is None: wx = wy = np.zeros_like(u)
def nodo(x0, y0): return np.argmin((x - x0) ** 2 + (y - y0) ** 2)
P = {"borde": nodo(0, 3500), "mar": nodo(0, 2500), "boca": nodo(0, 1500), "canal": nodo(0, 765),
     "bahia": nodo(0, -1000), "esq.bahia": nodo(-1300, -1950)}
print("hora | eta (cm): " + " ".join(f"{k:>9}" for k in P) + " | |u| canal cm/s | viento m/s | max|eta| (x,y)")
for i in range(eta.shape[0]):
    k = np.abs(eta[i]).argmax()
    print(f"{i+1:4d} | " + " ".join(f"{eta[i, j]*100:9.1f}" for j in P.values())
          + f" | {np.hypot(u[i], v[i])[P['canal']]*100:6.1f} | {np.hypot(wx[i], wy[i]).mean():5.1f} "
          f"| {eta[i, k]*100:7.1f} ({x[k]:.0f},{y[k]:.0f})")
