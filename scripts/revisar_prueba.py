#!/usr/bin/env python3
"""Revisa la salida de runs/prueba_idealizada: marea, corrientes en el canal y AGE.
Uso: python scripts/revisar_prueba.py
Referencia (control analitico, prisma_marea.py): corriente mareal en el canal ~4,5 cm/s
(3-6,5), la bahia sube y baja casi en bloque con la marea exterior (0,15 m de amplitud).
"""
from pathlib import Path
import os, sys
import numpy as np
from netCDF4 import Dataset

OUT = Path(__file__).resolve().parent.parent / "runs" / ("prueba_idealizada" + (f"_{sys.argv[1]}" if len(sys.argv) > 1 else "")) / "outputs"


def serie(prefijo, var):
    fs = sorted(OUT.glob(f"{prefijo}_*.nc"), key=lambda p: int(p.stem.split("_")[-1]))
    assert fs, f"no hay {prefijo}_*.nc en {OUT}"
    datos = []
    for f in fs:
        with Dataset(f) as nc:
            datos.append(np.asarray(nc[var][:]))
    return np.concatenate(datos)


with Dataset(OUT / "out2d_1.nc") as nc:
    x, y = nc["SCHISM_hgrid_node_x"][:], nc["SCHISM_hgrid_node_y"][:]
    print("variables 2D:", ", ".join(v for v in nc.variables if not v.startswith("SCHISM")))
t = serie("out2d", "time") / 86400
eta = serie("out2d", "elevation")
u, v = serie("out2d", "depthAverageVelX"), serie("out2d", "depthAverageVelY")
canal = (abs(x) <= 125) & (y > 200) & (y < 1330)
bahia = y < -200
ult = t > t[-1] - 25 / 24                      # ultimo ciclo (evita la rampa inicial)
print(f"{t.size} salidas horarias, hasta el dia {t[-1]:.2f}")
print(f"marea en la bahia (ultimo dia): amplitud {np.ptp(eta[ult][:, bahia].mean(1)) / 2 * 100:.1f} cm  (forzada 15 cm)")
vel = np.hypot(u, v)[ult][:, canal]
print(f"corriente en el canal (ultimo dia): media {vel.mean()*100:.1f} cm/s, max {vel.max()*100:.1f} cm/s  "
      f"(control analitico ~4,5 cm/s, 3-6,5)")
edad = serie("AGE_1", "AGE_1")[:, :, -1]          # superficie; SCHISM ya da la edad en dias
print(f"edad del agua en la bahia (superficie, final): media {edad[-1, bahia].mean():.2f} d, "
      f"p90 {np.percentile(edad[-1, bahia], 90):.2f} d  (renovacion analitica: 16-34 d)")
