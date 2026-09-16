#!/usr/bin/env python3
"""
Control analitico: prisma de marea y tiempo de renovacion de la Bahia de La Habana.

Nivel 1 del proyecto. Aritmetica, no modelo. Sirve para una sola cosa: fijar el ORDEN
DE MAGNITUD que el modelo numerico tiene que reproducir. Si el 2D/3D cae fuera de la
banda que sale aqui, hay que buscar el error antes de seguir.

Todas las entradas son provisionales (fuentes secundarias) hasta tener batimetria de
carta y armonicos de FES/TPXO. Por eso se propagan como distribuciones, no como numeros.

Uso:  python3 scripts/prisma_marea.py     -> tabla en pantalla + resultados/prisma_*.{csv,png}
"""
import numpy as np
from pathlib import Path

RNG = np.random.default_rng(20260916)
N = 200_000
T_M2 = 12.42 * 3600.0          # s, periodo semidiurno lunar
L_CANAL = 1530.0               # m, longitud del canal de entrada (practicos, Puerto de La Habana)

# ---------------------------------------------------------------------------
# Entradas: (caso central, minimo, maximo) y de donde salen
# ---------------------------------------------------------------------------
ENTRADAS = {
    # area de la lamina de agua. 5.2 km2 (fuentes divulgativas). +-10 % hasta digitalizar la carta
    "A_km2":   (5.2, 4.7, 5.7),
    # profundidad media. 9 m (fuentes divulgativas; 47 hm3 / 5.2 km2 = 9.0 m, coherente)
    "h_m":     (9.0, 7.0, 11.0),
    # rango mareal. Practicos: pleamar superior media 0.4 m, bajamar inferior media 0.1 m
    # -> rango diurno mayor ~0.3 m. Predicciones publicas: 0.3-0.45 m en sicigias.
    "R_m":     (0.30, 0.20, 0.50),
    # canal: ancho minimo 220 m (maximo 330 m); calado del canal 12.8 m, pero las margenes
    # son mas someras -> profundidad efectiva de la seccion 9-12.8 m
    "b_canal_m": (220.0, 220.0, 280.0),
    "h_canal_m": (11.0, 9.0, 12.8),
    # fraccion de retorno: agua que sale en vaciante y vuelve a entrar en llenante.
    # Valores de la literatura 0.2-0.8; aqui alta porque la excursion mareal es menor
    # que el canal (ver resultado). SUPUESTO, no dato.
    "beta":    (0.6, 0.3, 0.85),
    # aporte fluvial total (Luyano, Martin Perez y arroyos) - estimacion gruesa, sin aforo
    "Q_m3s":   (2.0, 0.5, 5.0),
}


def muestrea(c, lo, hi):
    """Triangular con moda en el caso central."""
    if lo == hi:
        return np.full(N, c)
    return RNG.triangular(lo, c, hi, N)


def calcula(A_km2, h_m, R_m, b_canal_m, h_canal_m, beta, Q_m3s):
    A = A_km2 * 1e6
    V = A * h_m
    P = A * R_m                                  # prisma de marea (m3)
    Ac = b_canal_m * h_canal_m                   # seccion del canal (m2)
    frac = P / V                                 # fraccion renovada por ciclo (sin retorno)
    Tf_dias = V / P * T_M2 / 86400               # renovacion ideal, mezcla completa, beta=0
    Tr_dias = V / ((1 - beta) * P / T_M2 + Q_m3s) / 86400   # con retorno + rio
    Tq_dias = V / Q_m3s / 86400                  # solo rio
    Umax = np.pi * P / (Ac * T_M2)               # velocidad maxima media en el canal (seno)
    excursion = P / Ac                           # excursion mareal, onda senoidal: Umax*T/pi = P/Ac (m)
    return dict(V_hm3=V / 1e6, P_hm3=P / 1e6, frac_pct=100 * frac,
                Tf_dias=Tf_dias, Tr_dias=Tr_dias, Tq_dias=Tq_dias,
                Umax_cms=100 * Umax, excursion_m=excursion,
                excursion_sobre_canal=excursion / L_CANAL)


def main():
    out = Path(__file__).resolve().parent.parent / "resultados"
    out.mkdir(exist_ok=True)

    central = calcula(**{k: v[0] for k, v in ENTRADAS.items()})
    mc = calcula(**{k: muestrea(*v) for k, v in ENTRADAS.items()})

    unidades = dict(V_hm3="hm3", P_hm3="hm3", frac_pct="%", Tf_dias="d", Tr_dias="d",
                    Tq_dias="d", Umax_cms="cm/s", excursion_m="m", excursion_sobre_canal="-")
    print(f"{'magnitud':24s}{'central':>10s}{'p5':>10s}{'p50':>10s}{'p95':>10s}  ud")
    lineas = ["magnitud,central,p5,p50,p95,unidad"]
    for k in central:
        p5, p50, p95 = np.percentile(mc[k], [5, 50, 95])
        print(f"{k:24s}{central[k]:10.2f}{p5:10.2f}{p50:10.2f}{p95:10.2f}  {unidades[k]}")
        lineas.append(f"{k},{central[k]:.4g},{p5:.4g},{p50:.4g},{p95:.4g},{unidades[k]}")
    frac_exc = np.mean(mc["excursion_sobre_canal"] < 1) * 100
    print(f"\nexcursion < longitud del canal en el {frac_exc:.0f} % de las muestras")
    (out / "prisma_marea.csv").write_text("\n".join(lineas) + "\n")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    bins = np.linspace(0, 120, 61)
    ax[0].hist(mc["Tf_dias"], bins=bins, alpha=.6, label=r"no return flow ($\beta=0$)")
    ax[0].hist(mc["Tr_dias"], bins=bins, alpha=.6, label=r"return flow $\beta$ + rivers")
    ax[0].set_xlabel("flushing time (days)"); ax[0].set_ylabel("samples")
    ax[0].legend(frameon=False)
    ax[1].hist(mc["excursion_m"], bins=60, color="0.5")
    ax[1].axvline(L_CANAL, color="k", ls="--"); ax[1].text(L_CANAL, ax[1].get_ylim()[1]*.9,
                                                            " channel 1530 m", va="top")
    ax[1].set_xlabel("tidal excursion in channel (m)")
    fig.tight_layout(); fig.savefig(out / "prisma_marea.png", dpi=200)
    print(f"guardado: {out/'prisma_marea.csv'}, {out/'prisma_marea.png'}")


if __name__ == "__main__":
    main()
