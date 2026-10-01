#!/usr/bin/env python3
"""Busca picos en el forzamiento atmosferico: lo que ve SCHISM (out2d) y lo que hay en el sflux.
Uso: python scripts/diagnostico_forzamiento.py [caso]"""
import sys
from pathlib import Path
import numpy as np
from netCDF4 import Dataset
R = Path(__file__).resolve().parent.parent
run = R / "runs" / ("prueba_idealizada" + (f"_{sys.argv[1]}" if len(sys.argv) > 1 else ""))
fs = sorted((run / "outputs").glob("out2d_*.nc"), key=lambda p: int(p.stem.split("_")[-1]))
V = {k: [] for k in ("windSpeedX", "windSpeedY", "depthAverageVelX", "depthAverageVelY")}
for f in fs:
    with Dataset(f) as nc:
        y = np.asarray(nc["SCHISM_hgrid_node_y"][:])
        for k in V: V[k].append(np.asarray(nc[k][:]))
V = {k: np.concatenate(v) for k, v in V.items()}
w, u = np.hypot(V["windSpeedX"], V["windSpeedY"]), np.hypot(V["depthAverageVelX"], V["depthAverageVelY"])
mar = y >= 1550
print("SCHISM (salida horaria): hora | viento medio / max (m/s) | |u| max en el mar (m/s)")
for i in range(w.shape[0]):
    print(f"{i+1:3d} | {w[i].mean():5.1f} / {w[i].max():6.1f} | {u[i, mar].max():6.2f}")
print("\nsflux (ERA5 convertido), primeros 3 dias de cada variable:")
for tipo, vs in (("air", ("uwind", "vwind", "prmsl", "stmp", "spfh")),):
    with Dataset(run / "sflux" / f"sflux_{tipo}_1.1.nc") as nc:
        t = nc["time"][:]; k = t <= 3
        print(f"  time: {t[0]:.3f} .. {t[-1]:.3f} d, {t.size} registros, paso min {np.diff(t).min()*24:.2f} h, max {np.diff(t).max()*24:.2f} h; base_date {nc['time'].base_date}")
        print(f"  lon {nc['lon'][0,:]}  lat {nc['lat'][:,0]}")
        for v in vs:
            a = np.asarray(nc[v][:])[k]
            print(f"  {v:6s} min {a.min():12.4f}  max {a.max():12.4f}  max salto entre horas {np.abs(np.diff(a, axis=0)).max():10.4f}")
