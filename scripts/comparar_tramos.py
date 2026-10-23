#!/usr/bin/env python3
"""Prueba de los tramos con hotstart: compara una corrida partida en tramos con la misma corrida seguida.
Uso (en el cluster, con netcdf4-python): python comparar_tramos.py runs/prueba_tramos/m0002 runs/prueba_continua/m0002
Un reinicio no es identico bit a bit (la diferencia de redondeo crece en un flujo no lineal), asi que el criterio no es
el maximo puntual sino lo que usa el articulo: las metricas de resumen.json (edad por zona, caudales, agua dulce).
Pasa si todas difieren menos del 1 %."""
import json, sys
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

a, b = map(Path, sys.argv[1:3])
n = max(int(f.stem.split("_")[-1]) for f in (b / "outputs").glob("out2d_*.nc"))
print(f"campos del dia {n} (tramos - seguida):")
for fich, var in [("out2d", "elevation"), ("AGE_1", "AGE_1"), ("salinity", "salinity"), ("out2d", "depthAverageVelX")]:
    fa, fb = a / "outputs" / f"{fich}_{n}.nc", b / "outputs" / f"{fich}_{n}.nc"
    if not fb.exists(): continue
    xa, xb = (np.asarray(Dataset(f)[var][:], float) for f in (fa, fb))
    d = np.abs(xa - xb)
    print(f"  {var:18s} max {np.nanmax(d):.3g}  p99 {np.nanpercentile(d, 99):.3g}  media {np.nanmean(d):.3g}  "
          f"(media |campo| {np.nanmean(np.abs(xb)):.3g})")
ra, rb = (json.loads((x / "resumen.json").read_text()) for x in (a, b))
print("metricas de resumen.json:")
peor = 0.0
for k, vb in rb.items():
    va = ra.get(k)
    if not isinstance(vb, float) or not isinstance(va, float) or "nodo" in k or not np.isfinite(vb) or not np.isfinite(va): continue
    if not k.startswith(("edad_media", "frac_", "Q_", "marea_", "vmax_bahia")): continue
    rel = abs(va - vb) / max(abs(vb), 1e-9); peor = max(peor, rel) if not k.startswith("Q_neto") else peor
    print(f"  {k:32s} tramos {va:10.4g}  seguida {vb:10.4g}  dif {100 * rel:6.2f} %")
print(f"peor diferencia relativa (sin Q_neto, que es ~0): {100 * peor:.2f} % ->", "ok" if peor < 0.01 else "REVISAR")
