#!/usr/bin/env python3
"""Estilo comun de las figuras del articulo (Environmental Modelling & Software). Solo matplotlib.
Medidas de docs/figuras_requisitos.md: 90 mm (una columna) o 190 mm (dos columnas) de ancho, 7 pt, sin bbox_inches="tight"."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MM = 1 / 25.4
ANCHO1, ANCHO2 = 90 * MM, 190 * MM                    # pulgadas
PX = {90: 1063, 190: 2244}                            # ancho en pixeles a 300 ppp
ALTO_MAX = {90: 100, 190: 110}                        # mm (120 solo si es la unica figura de la pagina)
SALIDA = Path(__file__).resolve().parent.parent / "docs" / "figuras" / "articulo"
# Okabe-Ito
NEGRO, NARANJA, CELESTE, VERDE, AMARILLO, AZUL, BERMELLON, ROSA, GRIS = (
    "#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#7f7f7f")


def estilo():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.titlesize": 7, "axes.labelsize": 7,
                         "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.linewidth": 0.5,
                         "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
                         "lines.linewidth": 0.8, "patch.linewidth": 0.5, "savefig.dpi": 300, "figure.dpi": 100,
                         "pdf.fonttype": 42})


def letra(ax, s, x=0.02, y=0.98):
    ax.text(x, y, f"({s})", transform=ax.transAxes, ha="left", va="top", fontweight="bold", fontsize=8,
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.8))


def guarda(fig, nombre, ancho_mm, salida=SALIDA, alto_max=None):
    """PNG a 300 ppp y PDF vectorial; comprueba ancho (1063 o 2244 px) y alto maximo."""
    from PIL import Image
    salida.mkdir(parents=True, exist_ok=True)
    png = salida / f"{nombre}.png"
    fig.savefig(png); fig.savefig(salida / f"{nombre}.pdf"); plt.close(fig)
    w, h = Image.open(png).size
    alto_mm = h / 300 * 25.4
    aviso = "" if abs(w - PX[ancho_mm]) <= 2 and alto_mm <= (alto_max or ALTO_MAX[ancho_mm]) + 0.5 else "   <-- REVISAR TAMANO"
    print(f"-> {png.name}: {w} x {h} px = {w / 300 * 25.4:.0f} x {alto_mm:.0f} mm{aviso}")
