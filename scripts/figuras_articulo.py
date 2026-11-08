#!/usr/bin/env python3
"""Figuras del artículo, en inglés y con un estilo común (Environmental Modelling & Software: ancho completo 190 mm).
Uso: python scripts/figuras_articulo.py [1 2 3 ...]   (sin argumentos: todas)  ->  docs/figuras/articulo/figNN_*.png
Necesita numpy, scipy y matplotlib. Solo lee datos de entrada versionados (no hacen falta resultados del conjunto).
El recuadro de Cuba de la figura 1 sale si existe datos/mapa/ne_50m_admin_0_countries.geojson
(Natural Earth, dominio público; scripts/descargar_natural_earth.sh)."""
import csv, importlib, json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from scipy.spatial import cKDTree

RAIZ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ / "scripts"), str(RAIZ / "scripts" / "batimetria")]
from zonas import zonas                                          # noqa: E402
from utm import utm                                              # noqa: E402
sup = importlib.import_module("07_superficies")                  # costa OSM
bat = importlib.import_module("08_batimetria_conjunto")          # miembros de batimetría y polígono del canal

SALIDA = RAIZ / "docs" / "figuras" / "articulo"
DSUP = RAIZ / "datos" / "batimetria" / "superficies"
FUENTES = RAIZ / "datos" / "batimetria" / "fuentes"
ANCHO = 190 / 25.4                                               # pulgadas
TIERRA, MAR = "#e3ded3", "#ffffff"
BAHIA = (360.6, 365.3, 2556.3, 2561.2)                           # km UTM 17N
ZONAS = {1: ("Entrance channel", "#56B4E9"), 2: ("Main basin", "#a6d9a0"), 3: ("Marimelena", "#F0E442"),
         4: ("Guasabacoa", "#E69F00"), 5: ("Atarés", "#CC79A7")}
RIOS = {"Río Luyanó": "Luyanó", "Río Martín Pérez": "Martín Pérez", "Arroyo Tadeo": "Tadeo"}


def estilo():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5,
                         "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.linewidth": 0.6,
                         "xtick.major.width": 0.6, "ytick.major.width": 0.6, "savefig.dpi": 300, "figure.dpi": 100})


def letra(ax, s):
    ax.text(0.02, 0.98, f"({s})", transform=ax.transAxes, ha="left", va="top", fontweight="bold", fontsize=8,
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.8))


def ejes_km(ax, lim, etiquetas=(True, True)):
    ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal")
    ax.set_xlabel("Easting (km, UTM 17N)" if etiquetas[0] else ""); ax.set_ylabel("Northing (km)" if etiquetas[1] else "")
    ax.ticklabel_format(useOffset=False, style="plain")


def escala(ax, km=1.0, x=0.06, y=0.06):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); X, Y = x0 + x * (x1 - x0), y0 + y * (y1 - y0)
    ax.plot([X, X + km], [Y, Y], "k-", lw=2, solid_capstyle="butt")
    ax.text(X + km / 2, Y + 0.012 * (y1 - y0), f"{km:g} km", ha="center", va="bottom", fontsize=6.5)


def norte(ax, x=0.93, y=0.86):
    ax.annotate("N", xy=(x, y + 0.08), xytext=(x, y), xycoords="axes fraction", ha="center", va="center", fontsize=7,
                fontweight="bold", arrowprops=dict(arrowstyle="-|>", lw=0.8, color="k"))


def costa_km():
    mar, islas, lineas = sup.costa(FUENTES / "osm_costa_habana.json")
    return mar / 1000, [i / 1000 for i in islas], [l / 1000 for l in lineas]


def fondo(ax, costa):
    """Tierra de fondo y mar (polígono de mar de la costa OSM) encima."""
    mar, islas, lineas = costa
    ax.set_facecolor(TIERRA); ax.fill(mar[:, 0], mar[:, 1], color=MAR, lw=0, zorder=0)
    for i in islas: ax.fill(i[:, 0], i[:, 1], color=TIERRA, lw=0, zorder=0.5)
    for l in lineas + islas: ax.plot(l[:, 0], l[:, 1], color="0.35", lw=0.4, zorder=3)


def rejilla_bahia():
    x, y, h = bat.lee(DSUP / "batimetria_1887.nc", "profundidad"); X, Y = np.meshgrid(x, y)
    return x, y, X, Y, h, bat.bahia(X, Y, h)


def hgrid(f):
    with open(f) as fh:
        fh.readline(); ne, nn = map(int, fh.readline().split())
        nod = np.array([fh.readline().split()[1:4] for _ in range(nn)], float)
        el = np.array([fh.readline().split()[2:5] for _ in range(ne)], int) - 1
        n_ab = int(fh.readline().split()[0]); fh.readline()                 # n.º de bordes abiertos; total de nodos
        abierto = []
        for _ in range(n_ab):
            k = int(fh.readline().split()[0]); abierto += [int(fh.readline().split()[0]) - 1 for _ in range(k)]
    return nod[:, 0], nod[:, 1], nod[:, 2], el, np.array(abierto)


def rios_osm():
    d = json.load(open(FUENTES / "osm_rios_habana.json"))
    out = {}
    for e in d["elements"]:
        n = e.get("tags", {}).get("name")
        if e["type"] == "way" and n in RIOS and "geometry" in e:
            E, N = utm([g["lon"] for g in e["geometry"]], [g["lat"] for g in e["geometry"]])
            out.setdefault(RIOS[n], []).append(np.c_[E, N] / 1000)
    return out


def desembocaduras():
    """Centroides de los elementos fuente del modelo (source_sink.in), en el orden de vsource.th: Luyanó, Martín Pérez, Tadeo."""
    d = RAIZ / "runs" / "robustez" / "m0000"
    x, y, _, el, _ = hgrid(d / "hgrid.gr3")
    ids = [int(l.split()[0]) - 1 for l in (d / "source_sink.in").read_text().splitlines()[1:4]]
    return {n: (x[el[i]].mean() / 1000, y[el[i]].mean() / 1000) for n, i in zip(("Luyanó", "Martín Pérez", "Tadeo"), ids)}


def cuba(ax):
    f = RAIZ / "datos" / "mapa" / "ne_50m_admin_0_countries.geojson"
    if not f.exists():
        ax.text(0.5, 0.5, "Cuba inset:\nrun scripts/\ndescargar_natural_earth.sh", transform=ax.transAxes,
                ha="center", va="center", fontsize=5.5, color="0.4"); ax.set_xticks([]); ax.set_yticks([]); return
    for ft in json.load(open(f))["features"]:
        if ft["properties"].get("ADMIN") not in ("Cuba", "United States of America", "The Bahamas", "Mexico", "Jamaica", "Haiti"):
            continue
        g = ft["geometry"]; pols = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for p in pols:
            a = np.array(p[0]); ax.fill(a[:, 0], a[:, 1], color=TIERRA if ft["properties"]["ADMIN"] != "Cuba" else "0.55", lw=0.3, ec="0.3")
    ax.plot(-82.35, 23.14, "rs", ms=3); ax.set_xlim(-85.5, -73.8); ax.set_ylim(19.5, 25.6); ax.set_facecolor(MAR)
    ax.set_aspect(1 / np.cos(np.radians(22.5))); ax.set_xticks([]); ax.set_yticks([])
    ax.text(-79.6, 21.3, "Cuba", fontsize=6, ha="center"); ax.text(-80.4, 23.85, "Straits of Florida", fontsize=4.5, ha="center", style="italic", color="0.3")


def fig1():
    """Mapa: zonas, canal, ríos y desembocaduras, sitios de turbidez de Sentinel-2; recuadro de Cuba."""
    costa = costa_km(); x, y, X, Y, h, b = rejilla_bahia()
    z = zonas(X, Y, b).astype(float); z[z == 0] = np.nan
    fig = plt.figure(figsize=(ANCHO, ANCHO * 0.6)); ax = fig.add_axes([0.07, 0.08, 0.58, 0.9])
    fondo(ax, costa)
    cm = ListedColormap([ZONAS[k][1] for k in range(1, 6)])
    ax.pcolormesh(x / 1000, y / 1000, z, cmap=cm, norm=BoundaryNorm(np.arange(0.5, 6.5), 5), alpha=0.55, shading="nearest", zorder=1)
    ax.contour(X / 1000, Y / 1000, bat.poligono_canal(X, Y).astype(float), [0.5], colors="k", linewidths=0.6, linestyles="--", zorder=2)
    for n, ls in rios_osm().items():
        for l in ls: ax.plot(l[:, 0], l[:, 1], color="#0072B2", lw=0.9, zorder=4)
    for n, (e, nn) in desembocaduras().items():
        ax.plot(e, nn, "v", color="#0072B2", mec="k", mew=0.4, ms=5, zorder=5)
        off = {"Luyanó": (-0.28, -0.08, "right"), "Martín Pérez": (0.14, -0.05, "left"), "Tadeo": (0.12, -0.14, "left")}[n]
        ax.text(e + off[0], nn + off[1], n, color="#0072B2", fontsize=6.5, ha=off[2], va="center", zorder=6, style="italic")
    lim = (359.3, 366.2, 2555.6, 2562.6)
    with open(RAIZ / "datos" / "sentinel2" / "focos.csv") as f:
        fo = [r for r in csv.DictReader(f) if lim[0] < float(r["E"]) / 1000 < lim[1] and lim[2] < float(r["N"]) / 1000 < lim[3]]
    for r in fo: ax.plot(float(r["E"]) / 1000, float(r["N"]) / 1000, "o", mfc="none", mec="#D55E00", mew=1.2, ms=7, zorder=5)
    etiquetas = {1: (360.55, 2560.15, "Entrance\nchannel"), 2: (363.0, 2559.4, "Main\nbasin"), 3: (364.35, 2559.6, "Marimelena"),
                 4: (362.85, 2557.25, "Guasa-\nbacoa"), 5: (361.25, 2557.35, "Atarés")}
    for k, (e, nn, t) in etiquetas.items():
        ax.text(e, nn, t, fontsize=6.5, ha="center", va="center", fontweight="bold", zorder=6,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.6) if k == 1 else None)
    ax.text(361.0, 2562.0, "Straits of Florida", fontsize=7, style="italic", ha="center", color="0.3")
    ax.text(359.9, 2558.9, "Havana", fontsize=7, ha="center", color="0.3")
    ejes_km(ax, lim); escala(ax); norte(ax)
    leg = [Patch(fc=c, alpha=0.55, label=n) for n, c in ZONAS.values()] + [
        Line2D([], [], color="k", ls="--", lw=0.6, label="Dredged channel (pilots, 2018)"),
        Line2D([], [], color="#0072B2", lw=0.9, marker="v", mec="k", mew=0.4, ms=5, label="River and model inflow"),
        Line2D([], [], ls="none", marker="o", mfc="none", mec="#D55E00", mew=1.2, ms=7, label="Recurrent turbidity site (Sentinel-2)")]
    fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.68, 0.56), frameon=False)
    cuba(fig.add_axes([0.69, 0.6, 0.29, 0.36]))
    guarda(fig, "fig01_map")


def fig2():
    """Batimetría: cartas de 1879 y 1887 con sus sondeos, diferencia donde ambas tienen sondeos, miembro dragado,
    campo de error de carta y volumen de la bahía en el conjunto."""
    costa = costa_km(); x, y, X, Y, h7, b = rejilla_bahia()
    _, _, h9 = bat.lee(DSUP / "batimetria_1879.nc", "profundidad")
    son = {}
    for k, f in (("1879", "sondeos_1889.csv"), ("1887", "sondeos_1898.csv")):
        son[k] = sup.sondeos(RAIZ / "datos" / "batimetria" / "sondeos" / f)[0]
    dz = h7 - h9
    q = np.c_[X.ravel(), Y.ravel()]
    cerca = (cKDTree(son["1879"]).query(q)[0] < 100) & (cKDTree(son["1887"]).query(q)[0] < 100)
    dz = np.where(cerca.reshape(X.shape) & b, dz, np.nan)
    _, _, hdr, m = bat.miembro(DSUP, carta="1887", alfa=1.0, sigma=0)
    eps = bat.campo_aleatorio(h7.shape, 20.0, bat.SIGMA, bat.L, 1)
    fig, axs = plt.subplots(2, 3, figsize=(ANCHO, ANCHO * 0.72), constrained_layout=True)
    kw = dict(cmap="viridis_r", vmin=0, vmax=15, shading="nearest", zorder=1)
    paneles = [("1879 survey (chart ed. 1889)", h9, kw, son["1879"]), ("1887 survey (chart ed. 1898)", h7, kw, son["1887"]),
               ("Difference 1887 − 1879", dz, dict(cmap="RdBu", vmin=-3, vmax=3, shading="nearest", zorder=1), None),
               ("Dredged member (1887, α = 1)", hdr, kw, None),
               ("Chart-error field (one realisation)", np.where(b, eps, np.nan),
                dict(cmap="PuOr", vmin=-2.5, vmax=2.5, shading="nearest", zorder=1), None)]
    for i, (a, (t, v, k, s)) in enumerate(zip(axs.flat, paneles)):
        fondo(a, costa); im = a.pcolormesh(x / 1000, y / 1000, v, **k)
        if s is not None: a.plot(s[:, 0] / 1000, s[:, 1] / 1000, ".", ms=0.6, color="k", alpha=0.5, zorder=2)
        if i in (0, 3):
            a.contour(X / 1000, Y / 1000, m["canal"].astype(float), [0.5], colors="r", linewidths=0.6, zorder=3)
        a.set_title(t); ejes_km(a, BAHIA, (i >= 3, i % 3 == 0)); letra(a, "abcde"[i])
        if i in (1, 2, 4):
            c = fig.colorbar(im, ax=a, shrink=0.85, extend="max" if i == 1 else "both")
            c.set_label({1: "Depth below chart datum (m)", 2: "Depth change (m)", 4: "Depth perturbation (m)"}[i])
    axs[0, 0].legend(handles=[Line2D([], [], color="r", lw=0.6, label="Dredged channel"),
                              Line2D([], [], ls="none", marker=".", color="k", ms=3, label="Soundings")], loc="lower right")
    axs[1, 1].text(0.98, 0.02, f"exponential, σ = {bat.SIGMA} m, L = {bat.L:.0f} m", transform=axs[1, 1].transAxes,
                   ha="right", va="bottom", fontsize=5.5, color="0.3")
    axs[0, 2].text(0.98, 0.02, "only where both surveys\nhave soundings < 100 m", transform=axs[0, 2].transAxes,
                   ha="right", va="bottom", fontsize=5.5, color="0.3")
    a = axs[1, 2]; v = json.load(open(DSUP / "volumenes_conjunto.json"))["volumenes"]
    for j, (carta, col) in enumerate((("1879", "#0072B2"), ("1887", "#D55E00"))):
        al = np.array([0, 0.5, 1]) + (j - 0.5) * 0.04
        med = [v[f"{carta}_alfa{x:.1f}"]["vol_media_hm3"] for x in (0, 0.5, 1)]
        lo = [v[f"{carta}_alfa{x:.1f}"]["vol_p5"] for x in (0, 0.5, 1)]; hi = [v[f"{carta}_alfa{x:.1f}"]["vol_p95"] for x in (0, 0.5, 1)]
        a.errorbar(al, med, yerr=[np.subtract(med, lo), np.subtract(hi, med)], fmt="o-", color=col, ms=3, lw=0.8, capsize=2, label=f"{carta} survey")
    a.set_xlabel("Dredging state α"); a.set_ylabel("Bay volume (hm³)"); a.set_xticks([0, 0.5, 1]); a.set_title("Bay volume across the ensemble")
    a.legend(loc="lower right", title="mean, P5–P95 of\n30 error fields", title_fontsize=6); a.grid(lw=0.3, alpha=0.5); letra(a, "f")
    guarda(fig, "fig02_bathymetry")


def fig3():
    """Malla: dominio completo con profundidad, borde abierto y esponja; bahía; detalle del canal."""
    costa = costa_km()
    x, y, d, el, ab = hgrid(RAIZ / "runs" / "robustez" / "m0000" / "hgrid.gr3")
    xk, yk = x / 1000, y / 1000
    dist = np.min(np.hypot(x[:, None] - x[ab][None], y[:, None] - y[ab][None]), axis=1)
    fig = plt.figure(figsize=(ANCHO, ANCHO * 0.52), constrained_layout=True)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1, 0.75])
    a = fig.add_subplot(gs[0]); fondo(a, costa)
    tp = a.tripcolor(xk, yk, el, np.clip(d, 0.5, 200), norm=LogNorm(0.5, 200), cmap="viridis_r", shading="gouraud", zorder=1)
    a.triplot(xk, yk, el, color="k", lw=0.08, alpha=0.6, zorder=2)
    a.tricontour(xk, yk, el, dist, [1000], colors="r", linewidths=0.7, linestyles="--", zorder=3)
    a.plot(xk[ab], yk[ab], "r-", lw=1.4, zorder=4)
    lim = (xk.min() - 0.2, xk.max() + 0.2, yk.min() - 0.2, yk.max() + 0.2)
    ejes_km(a, lim); a.set_title(f"Model domain ({len(x)} nodes, {len(el)} elements)"); letra(a, "a")
    a.add_patch(Rectangle((BAHIA[0], BAHIA[2]), BAHIA[1] - BAHIA[0], BAHIA[3] - BAHIA[2], fill=False, ec="w", lw=0.8, zorder=5))
    a.legend(handles=[Line2D([], [], color="r", lw=1.4, label="Open boundary (EOT20 tide)"),
                      Line2D([], [], color="r", lw=0.7, ls="--", label="Sponge layer limit (1 km)")], loc="lower left")
    c = fig.colorbar(tp, ax=a, shrink=0.8, location="bottom", pad=0.02); c.set_label("Model depth (m)")
    b = fig.add_subplot(gs[1]); fondo(b, costa)
    b.tripcolor(xk, yk, el, np.clip(d, 0, 15), vmin=0, vmax=15, cmap="viridis_r", shading="gouraud", zorder=1)
    b.triplot(xk, yk, el, color="k", lw=0.12, alpha=0.7, zorder=2)
    det = (361.35, 361.95, 2559.85, 2560.45)
    b.add_patch(Rectangle((det[0], det[2]), det[1] - det[0], det[3] - det[2], fill=False, ec="r", lw=0.8, zorder=5))
    ejes_km(b, BAHIA, (True, False)); b.set_title("Bay: 40 m elements"); letra(b, "b"); escala(b)
    c = fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(0, 15), cmap="viridis_r"), ax=b, shrink=0.8, location="bottom",
                     pad=0.02, extend="max"); c.set_label("Model depth (m)")
    e = fig.add_subplot(gs[2]); fondo(e, costa)
    e.tripcolor(xk, yk, el, np.clip(d, 0, 15), vmin=0, vmax=15, cmap="viridis_r", shading="gouraud", zorder=1)
    e.triplot(xk, yk, el, color="k", lw=0.3, zorder=2)
    ejes_km(e, det, (True, False)); e.set_title("Entrance channel: 25 m"); letra(e, "c"); escala(e, 0.1)
    guarda(fig, "fig03_mesh")


def guarda(fig, nombre):
    SALIDA.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA / f"{nombre}.png"); plt.close(fig); print("->", SALIDA / f"{nombre}.png")


if __name__ == "__main__":
    estilo()
    figs = {1: fig1, 2: fig2, 3: fig3}
    for k in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else figs):
        figs[k]()
