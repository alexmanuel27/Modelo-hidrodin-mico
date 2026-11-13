#!/usr/bin/env python3
"""Figura suplementaria de control de los sondeos digitalizados (ingles, UTM 17N, tamano final 190 mm).
(a) 1126 sondeos de la carta H.O. 307 ed. 1889 (levantamientos hasta 1879) sobre esa carta, color = profundidad;
(b) posiciones de 1879 (ed. 1889) y 1887 (ed. 1898) sobre la misma carta (misma plancha).
Fondo: datos/batimetria/vistas/reg_1889_s3.png = GeoTIFF de Harvard (WGS84) reducido x3, reproyectado a UTM por vecino mas cercano.
Uso: python scripts/figura_sondeos.py   -> docs/figuras/articulo/figS_soundings.{png,pdf}"""
import csv, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parent / "batimetria"))
from estilo_figuras import MM, estilo, letra, guarda, plt
from utm import utm, utm_inv

B = Path(__file__).resolve().parent.parent / "datos" / "batimetria"
Image.MAX_IMAGE_PIXELS = None
F = 3                                                                        # reg_1889_s3.png = GeoTIFF / 3


def lee(f):
    r = list(csv.DictReader(open(B / "sondeos" / f))); g = lambda k: np.array([float(x[k]) for x in r])
    E, N = utm(g("lon"), g("lat")); return E / 1000, N / 1000, g("prof_m"), g("dudoso")


def fondo(ext, paso=4.0):
    """Carta reproyectada a una rejilla UTM de 'paso' m que cubre ext (km)."""
    t = Image.open(B / "fuentes" / "carta_1889_harvard.tif").tag_v2; sx, sy = t[33550][:2]; lon0, lat0 = t[33922][3], t[33922][4]
    im = np.asarray(Image.open(B / "vistas" / "reg_1889_s3.png").convert("L"))
    E = np.arange(ext[0] * 1000, ext[1] * 1000, paso); N = np.arange(ext[3] * 1000, ext[2] * 1000, -paso)
    lon, lat = utm_inv(*np.meshgrid(E, N))
    x = np.round((lon - lon0) / sx / F - 0.5).astype(int); y = np.round((lat0 - lat) / sy / F - 0.5).astype(int)
    ok = (x >= 0) & (x < im.shape[1]) & (y >= 0) & (y < im.shape[0])
    out = np.full(x.shape, 255, np.uint8); out[ok] = im[y[ok], x[ok]]; return out


def prueba():
    lon, lat = -82.35, 23.13; E, N = utm(lon, lat); lo, la = utm_inv(E, N)
    assert abs(lo - lon) < 1e-7 and abs(la - lat) < 1e-7 and 360000 < E < 366000, (E, N, lo, la)
    print("autoprueba figura_sondeos: ok")


def figura():
    estilo(); a, b = lee("sondeos_1889.csv"), lee("sondeos_1898.csv")
    ext = [358.4, 364.6, 2556.2, 2561.3]                                     # km UTM 17N: bahia y canal con su salida
    bg = fondo(ext)
    fig, ax = plt.subplots(1, 2, figsize=(190 * MM, 88 * MM), constrained_layout=True, sharey=True)
    for k, axk in enumerate(ax):
        axk.imshow(bg, extent=ext, cmap="gray", vmin=0, vmax=255, alpha=0.45, interpolation="bilinear")
        axk.set_xlim(ext[:2]); axk.set_ylim(ext[2:]); axk.set_aspect("equal"); axk.set_xlabel("Easting (km, UTM 17N)")
        axk.ticklabel_format(useOffset=False, style="plain"); letra(axk, "ab"[k])
    ax[0].set_ylabel("Northing (km)")
    E, N, z, d = a
    sc = ax[0].scatter(E, N, c=np.clip(z, 0, 20), cmap="viridis_r", vmin=0, vmax=20, s=3, lw=0)
    ax[0].scatter(E[d > 0], N[d > 0], s=12, facecolors="none", edgecolors="#D55E00", lw=0.5, label="doubtful or 'no bottom at'")
    ax[0].set_title(f"H.O. 307, ed. 1889 (surveys to 1879): {len(E)} soundings", fontsize=7)
    ax[0].legend(frameon=False, loc="lower left", fontsize=6)
    fig.colorbar(sc, ax=ax[0], shrink=0.7, extend="max").set_label("Depth (m)")
    ax[1].scatter(a[0], a[1], s=3, c="#0072B2", lw=0, label=f"1879 (ed. 1889, n = {len(a[0])})")
    ax[1].scatter(b[0], b[1], s=3, c="#D55E00", marker="x", lw=0.35, label=f"1887 (ed. 1898, n = {len(b[0])})")
    ax[1].set_title("Sounding positions of the two survey epochs", fontsize=7); ax[1].legend(frameon=False, loc="lower left", fontsize=6)
    guarda(fig, "figS_soundings", 190, alto_max=110)


if __name__ == "__main__":
    prueba() if sys.argv[1:] == ["--prueba"] else figura()
