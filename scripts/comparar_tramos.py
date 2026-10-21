#!/usr/bin/env python3
"""Prueba de los tramos con hotstart: compara el ultimo dia de una corrida partida en tramos con la misma corrida
seguida. Uso (en el cluster, con netcdf4-python): python comparar_tramos.py runs/prueba_tramos/m0002 runs/prueba_continua/m0002
Pasa si elevacion, edad y salinidad coinciden (diferencia maxima pequena frente a su rango)."""
import sys
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

a, b = map(Path, sys.argv[1:3])
n = max(int(f.stem.split("_")[-1]) for f in (b / "outputs").glob("out2d_*.nc"))
mal = 0
for fich, var in [("out2d", "elevation"), ("AGE_1", "AGE_1"), ("salinity", "salinity"), ("out2d", "depthAverageVelX")]:
    fa, fb = a / "outputs" / f"{fich}_{n}.nc", b / "outputs" / f"{fich}_{n}.nc"
    if not fb.exists(): print(f"{var}: no hay {fb.name}"); continue
    xa, xb = (np.asarray(Dataset(f)[var][:], float) for f in (fa, fb))
    d, rango = np.nanmax(np.abs(xa - xb)), np.nanmax(xb) - np.nanmin(xb)
    ok = d <= 1e-3 * max(rango, 1e-9) + 1e-6; mal += not ok
    print(f"{var:18s} dia {n}: max |tramos - seguida| = {d:.3g}  (rango {rango:.3g})  {'ok' if ok else 'DIFIERE'}")
print("prueba de tramos:", "ok" if mal == 0 else "FALLA")
