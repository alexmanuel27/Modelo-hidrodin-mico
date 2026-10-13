#!/usr/bin/env python3
"""Revisa la salida 2D de un caso sobre la malla real (caso_real.py): estabilidad, marea, corrientes.
Uso: python scripts/revisar_real.py <carpeta con out2d_*.nc>      (por defecto runs/real_prueba/salida_nic5)
Escribe revision.txt y revision.png en esa carpeta.
Referencia (prisma_marea.py): corriente mareal media en el canal ~4 cm/s; la bahia sube y baja en bloque."""
import sys
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "runs/real_prueba/salida_nic5"
fs = sorted(D.glob("out2d_*.nc"), key=lambda p: int(p.stem.split("_")[-1]))
assert fs, f"no hay out2d_*.nc en {D}"
cat = lambda v: np.concatenate([np.asarray(Dataset(f)[v][:]) for f in fs])
with Dataset(fs[0]) as nc:
    x, y = np.asarray(nc["SCHISM_hgrid_node_x"][:]), np.asarray(nc["SCHISM_hgrid_node_y"][:])
    h = np.asarray(nc["depth"][:]) if "depth" in nc.variables else None
t = cat("time") / 86400; eta = cat("elevation"); u, v = cat("depthAverageVelX"), cat("depthAverageVelY")
spd = np.hypot(u, v)
bahia = ((x > 361000) & (y < 2560950)) | ((x > 360500) & (y < 2559000))
tc = np.radians(124.0); uc = np.array([np.sin(tc), np.cos(tc)]); nn = np.array([uc[1], -uc[0]])
d = np.c_[x - 361646, y - 2560188]
canal = (np.abs(d @ uc) <= 700) & (np.abs(d @ nn) <= 100)
borde = np.hypot(x - 361000, y - 2560900) > 4600
# malla del caso (carpeta padre): triangulos reales para las figuras y extremos del borde abierto
g = (D.parent / "hgrid.gr3").read_text().split("\n"); ne, nn_ = map(int, g[1].split()[:2])
tri = np.array([[int(c) - 1 for c in l.split()[2:5]] for l in g[2 + nn_:2 + nn_ + ne]])
i0 = 2 + nn_ + ne; nab = int(g[i0 + 2].split()[0]); ab = [int(g[i0 + 3 + j].split()[0]) - 1 for j in range(nab)]
esq = np.zeros(len(x), bool); esq[[ab[0], ab[-1]]] = True   # nodos donde el borde abierto toca tierra
ult = t > t[-1] - 25 / 24
L = []
p = lambda s: (print(s), L.append(s))
p(f"{len(t)} salidas, dias {t[0]:.2f}-{t[-1]:.2f}; NaN: {int(np.isnan(eta).sum() + np.isnan(spd).sum())}")
p(f"nivel: min {np.nanmin(eta):.3f} m, max {np.nanmax(eta):.3f} m")
eb, ef = eta[ult][:, bahia].mean(1), eta[ult][:, borde].mean(1)
p(f"marea ultimo dia: amplitud bahia {np.ptp(eb) / 2 * 100:.1f} cm, borde {np.ptp(ef) / 2 * 100:.1f} cm (forzada 15 cm)")
p(f"desfase bahia-borde (correlacion maxima): {np.argmax(np.correlate(eb - eb.mean(), ef - ef.mean(), 'full')) - len(eb) + 1} h")
p(f"corriente en el canal (ultimo dia): media {spd[ult][:, canal].mean() * 100:.1f} cm/s, max {spd[ult][:, canal].max() * 100:.1f} cm/s (control ~4 cm/s)")
p(f"corriente en la bahia: media {spd[ult][:, bahia & ~canal].mean() * 100:.2f} cm/s, p99 {np.percentile(spd[ult][:, bahia & ~canal], 99) * 100:.1f} cm/s")
p(f"corriente maxima en todo el dominio: {spd.max():.2f} m/s en x={x[np.argmax(spd.max(0))]:.0f}, y={y[np.argmax(spd.max(0))]:.0f}; junto al borde abierto: {spd[:, borde].max():.2f} m/s")
top = np.argsort(spd.max(0))[::-1][:5]
p("5 nodos mas rapidos: " + "; ".join(f"{spd[:, k].max():.2f} m/s ({x[k]:.0f},{y[k]:.0f}{', esquina' if esq[k] else ''})" for k in top))
p(f"corriente maxima sin las 2 esquinas del borde abierto: {spd[:, ~esq].max():.2f} m/s")
crece = [spd[k].max() for k in range(len(t))]
p(f"velocidad maxima por dia: " + ", ".join(f"d{int(t[k])}: {max(crece[i] for i in range(len(t)) if int(t[i]) == int(t[k])):.2f}" for k in range(len(t)) if k == 0 or int(t[k]) != int(t[k - 1])))
(D / "revision.txt").write_text("\n".join(L) + "\n")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(20, 6))
ax[0].plot(t, eta[:, borde].mean(1), label="borde abierto"); ax[0].plot(t, eta[:, bahia].mean(1), label="bahia")
ax[0].set_xlabel("dias"); ax[0].set_ylabel("nivel (m)"); ax[0].legend()
for a, val, tit, vmax in ((ax[1], spd.max(0), "velocidad maxima (m/s)", 0.3), (ax[2], spd[ult].mean(0), "velocidad media ultimo dia (m/s)", 0.1)):
    s = a.tricontourf(x, y, tri, val, levels=np.linspace(0, vmax, 21), extend="max"); plt.colorbar(s, ax=a)
    a.set_title(tit); a.set_aspect("equal"); a.set_xlim(356000, 366000); a.set_ylim(2556000, 2566000)
fig.tight_layout(); fig.savefig(D / "revision.png", dpi=100)
print(f"guardado {D/'revision.txt'}, {D/'revision.png'}")
