#!/usr/bin/env python3
"""Figura del efecto del flujo de calor (B1 de la revision V2). Lee el repo tecnico (solo lectura) y escribe en --salida.
  python scripts/fig_heatflux.py [<raiz_repo_tecnico> <carpeta_salida>]   (por defecto: este repo y docs/figuras/articulo)
Copiado el 16-nov de fig_trabajo/fig_heatflux.py del repo del articulo (V2); sin cambios en la figura. La salida impresa se guarda en
resultados/heatflux_cifras.txt.
(a) edad media de la bahia, 365 d: base, calor + borde 28 C, calor + OISST (runs/robustez_largo/m0001, m0005 y la base m0000).
(b) 16 miembros del bloque A (0-15): edad en los ultimos 30 d de 120 sin y con calor+OISST, color = factor de caudal.
Imprime tambien las cifras anuales y mensuales (B3)."""
import csv, json, sys
from pathlib import Path
import numpy as np
RAIZ = Path(sys.argv[1]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent
SAL = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "docs" / "figuras" / "articulo"; sys.path.insert(0, str(RAIZ / "scripts"))
import estilo_figuras as E
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
E.estilo()
MES = np.cumsum([0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])           # 2016 bisiesto


def diaria(s):
    dd = np.floor(np.arange(len(s)) / (len(s) / 365)).astype(int)
    return np.array([s[dd == k].mean() for k in range(365)])


def media_movil(x, n=30):
    return np.array([x[max(0, k - n + 1):k + 1].mean() if k >= n - 1 else np.nan for k in range(len(x))])


casos = (("m0000", "No heat flux (base)", "#000000", RAIZ / "runs" / "largo"),
         ("m0001", "Heat flux, boundary 28 °C", E.BERMELLON, RAIZ / "runs" / "robustez_largo"),
         ("m0005", "Heat flux, OISST boundary", E.NARANJA, RAIZ / "runs" / "robustez_largo"))
fig = plt.figure(figsize=(E.ANCHO2, 80 * E.MM))
ax = fig.add_axes([0.065, 0.14, 0.56, 0.82]); bx = fig.add_axes([0.715, 0.14, 0.205, 0.82]); cx = fig.add_axes([0.94, 0.14, 0.012, 0.82])
for m, nom, col, d in casos:
    p = (d / m / "resumen.npz") if (d / m / "resumen.npz").exists() else RAIZ / "runs" / "robustez_largo" / m / "resumen.npz"
    md = diaria(np.load(p)["serie_bahia"])
    ax.plot(np.arange(1, 366), md, color=col, lw=0.4, alpha=0.45)
    ax.plot(np.arange(1, 366), media_movil(md), color=col, lw=1.4, label=nom)
    mm = [md[MES[i]:MES[i + 1]].mean() for i in range(12)]
    r30 = media_movil(md)[29:]
    print(m, nom, f"media anual {md.mean():.2f}; mensual min {min(mm):.1f} (mes {int(np.argmin(mm)) + 1}), max {max(mm):.1f} (mes {int(np.argmax(mm)) + 1}); diaria min {md.min():.1f} max {md.max():.1f}")
    print(f"   medias mensuales ene..dic: {' '.join(f'{x:.1f}' for x in mm)}; media movil de 30 d {r30.min():.1f}-{r30.max():.1f}; dias con media diaria > 14 d: {int((md > 14).sum())}/365")
ax.axvspan(90, 120, color="#e8e8e8", zorder=0); ax.text(105, 0.6, "metric\nwindow", ha="center", va="bottom", fontsize=6, color="#555555")
for v, ls in ((7, "--"), (14, ":")): ax.axhline(v, color="#555555", lw=0.6, ls=ls)
ax.text(364, 7.3, "7 d", ha="right", fontsize=6, color="#555555"); ax.text(364, 14.3, "14 d", ha="right", fontsize=6, color="#555555")
ax.set_xlim(1, 365); ax.set_ylim(0, 30); ax.set_xticks(MES + 1, minor=False); ax.set_xticklabels([]); ax.set_xticks((MES[:-1] + MES[1:]) / 2 + 1, minor=True); ax.set_xticklabels(list("JFMAMJJASOND"), minor=True); ax.tick_params(axis="x", which="minor", length=0)
ax.set_xlabel("2016"); ax.set_ylabel("Bay-mean water age (d)"); ax.legend(loc="upper left", frameon=False, bbox_to_anchor=(0.06, 1.0))
E.letra(ax, "a")
# (b)
filas = [f for f in csv.DictReader(open(RAIZ / "datos" / "conjunto" / "diseno.csv")) if int(f["miembro"]) < 16]
sin = np.array([json.loads((RAIZ / "runs" / "conjunto" / f"m{int(f['miembro']):04d}" / "resumen.json").read_text())["edad_media_d_bahia"] for f in filas])
cal = np.array([json.loads((RAIZ / "runs" / "conjunto_calor" / f"m{int(f['miembro']):04d}" / "resumen.json").read_text())["edad_media_d_bahia"] for f in filas])
q = np.array([float(f["qfac"]) for f in filas])
sc = bx.scatter(sin, cal, c=q, cmap="viridis", norm=LogNorm(q.min(), q.max()), s=14, edgecolor="k", linewidth=0.3, zorder=3)
bx.plot([0, 25], [0, 25], color="#555555", lw=0.6); bx.set_xlim(3, 14); bx.set_ylim(3, 22)
for v, ls in ((14, ":"),): bx.axhline(v, color="#555555", lw=0.6, ls=ls)
bx.set_xlabel("Age without heat flux (d)"); bx.set_ylabel("Age with heat flux and OISST (d)")
cb = fig.colorbar(sc, cax=cx); cb.set_ticks([0.3, 0.5, 1, 2]); cb.set_ticklabels(["0.3", "0.5", "1", "2"]); cb.ax.minorticks_off(); cb.set_label("River discharge factor", fontsize=6.5); cb.ax.tick_params(labelsize=6)
E.letra(bx, "b")
print("16 miembros: sin mediana", np.median(sin).round(2), "calor", np.median(cal).round(2), "calor>sin", int((cal > sin).sum()))
E.guarda(fig, "fig_heatflux", 190, salida=SAL, alto_max=110)
