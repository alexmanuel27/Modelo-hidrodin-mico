#!/usr/bin/env python3
"""
Control analitico: prisma de marea y tiempo de renovacion de la Bahia de La Habana.

Nivel 1 del proyecto. Aritmetica, no modelo. Sirve para una sola cosa: fijar el ORDEN
DE MAGNITUD que el modelo numerico tiene que reproducir. Si el 2D/3D cae fuera de la
banda que sale aqui, hay que buscar el error antes de seguir.

La marea ya no es un rango supuesto: se sintetiza un ano de nivel con los armonicos de EOT20
frente a la boca (datos/marea/eot20_habana.json) y se muestrean DIAS reales de esa serie
(marea mixta: dias con una o dos llenantes de tamano distinto). El resto de entradas se propaga
como distribuciones triangulares.

Uso:  python3 scripts/prisma_marea.py     -> tabla en pantalla + resultados/prisma_*.{csv,png}
"""
import numpy as np
from pathlib import Path

RNG = np.random.default_rng(20260916)
N = 200_000
MAREA = Path(__file__).resolve().parent.parent / "datos" / "marea" / "eot20_habana.json"
FREC = dict(m2=1.405189e-4, s2=1.454441e-4, n2=1.378797e-4, k2=1.458423e-4, k1=7.292117e-5, o1=6.759774e-5,
            p1=7.251056e-5, q1=6.495854e-5, m4=2.810378e-4)   # rad/s
L_CANAL = 1530.0               # m, longitud del canal de entrada (practicos, Puerto de La Habana)

# ---------------------------------------------------------------------------
# Entradas: (caso central, minimo, maximo) y de donde salen
# ---------------------------------------------------------------------------
ENTRADAS = {
    # area de la lamina de agua: 4.91 km2 con la costa actual de OSM (bahia + canal; 07_superficies.py).
    # Antes (hasta 13-oct-2026): 5.2 km2 (4.7-5.7) de fuentes divulgativas.
    "A_km2":   (4.91, 4.7, 5.2),
    # profundidad media: 5.2 m (carta 1887, sin dragado) a 7.3 m (1879 + dragado a calados de practicos);
    # moda 6.2 m = estado de dragado intermedio (08_batimetria_conjunto.py, volumenes_conjunto.json).
    # Antes: 9 m (7-11) de fuentes divulgativas (47 hm3), que las cartas no sostienen (ver docs, sec. 19).
    "h_m":     (6.2, 5.2, 7.3),
    # canal: ancho minimo 220 m (maximo 330 m); calado del canal 12.8 m, pero las margenes
    # son mas someras -> profundidad efectiva de la seccion 9-12.8 m
    "b_canal_m": (220.0, 220.0, 280.0),
    "h_canal_m": (11.0, 9.0, 12.8),
    # fraccion de retorno: agua que sale en vaciante y vuelve a entrar en llenante.
    # Valores de la literatura 0.2-0.8; aqui alta porque la excursion mareal es menor
    # que el canal (ver resultado). SUPUESTO, no dato.
    "beta":    (0.6, 0.3, 0.85),
    # aporte fluvial total: Luyano + Martin Perez + Tadeo = 2.14 m3/s (JICA 2004, tabla 1.1, CIMAB ago-2002;
    # una sola campana, sin aforos permanentes) -> rango amplio, hasta ~5 con aguas residuales
    "Q_m3s":   (2.14, 1.0, 5.0),
}


def marea_diaria(lon=-82.36, lat=23.20, dias=365, dt=600.0):
    """Serie de un ano con los armonicos EOT20 en la celda valida mas cercana a (lon, lat); por dia:
    suma de las subidas (llenantes que culminan ese dia, m), mayor subida (m) y max |deta/dt| (m/s).
    shortcut: sin factores nodales ni argumento astronomico (cambian el calendario y +-4 % las amplitudes,
    no la estadistica anual de rangos); usar pyTMD si se quiere una prediccion fechada."""
    import json
    t = np.arange(0, dias * 86400, dt); eta = np.zeros_like(t)
    for c, d in json.loads(MAREA.read_text()).items():
        A = np.array(d["amp_m"]); G = np.radians(np.array(d["fase_grados"]))
        LA, LO = np.meshgrid(d["lat"], d["lon"], indexing="ij"); ok = np.isfinite(A) & (A > 0)
        j, i = np.unravel_index(np.where(ok, np.hypot(LA - lat, LO - lon), 9).argmin(), A.shape)
        eta += A[j, i] * np.cos(FREC[c] * t - G[j, i])
    de = np.diff(eta); ext = np.where(np.sign(de[1:]) != np.sign(de[:-1]))[0] + 1   # extremos
    alto = de[ext - 1] > 0                                                           # pleamares
    sub, dia = [], []
    for k in range(1, len(ext)):
        if alto[k] and not alto[k - 1]: sub.append(eta[ext[k]] - eta[ext[k - 1]]); dia.append(int(t[ext[k]] // 86400))
    sub, dia = np.array(sub), np.array(dia)
    S = np.bincount(dia, sub, minlength=dias); Rmax = np.array([sub[dia == k].max() if (dia == k).any() else 0 for k in range(dias)])
    W = np.abs(np.append(de, de[-1]) / dt).reshape(dias, -1).max(1)
    return S, Rmax, W, len(sub) / dias


def muestrea(c, lo, hi):
    """Triangular con moda en el caso central."""
    if lo == hi:
        return np.full(N, c)
    return RNG.triangular(lo, c, hi, N)


def calcula(A_km2, h_m, S_m, Rmax_m, W_ms, b_canal_m, h_canal_m, beta, Q_m3s):
    """S_m: suma de las subidas del dia (m); Rmax_m: mayor subida del dia; W_ms: max |deta/dt| del dia."""
    A = A_km2 * 1e6
    V = A * h_m
    Pd = A * S_m                                 # prisma diario: agua que entra en llenante en un dia (m3/d)
    Ac = b_canal_m * h_canal_m                   # seccion del canal (m2)
    Tf_dias = V / Pd                             # renovacion ideal, mezcla completa, beta=0
    Tr_dias = V / ((1 - beta) * Pd / 86400 + Q_m3s) / 86400   # con retorno + rio
    Tq_dias = V / Q_m3s / 86400                  # solo rio
    Umax = A * W_ms / Ac                         # velocidad maxima media en la seccion (continuidad)
    excursion = A * Rmax_m / Ac                  # desplazamiento en la mayor llenante = volumen / seccion (m)
    return dict(V_hm3=V / 1e6, P_hm3=A * Rmax_m / 1e6, frac_pct=100 * Pd / V,
                Tf_dias=Tf_dias, Tr_dias=Tr_dias, Tq_dias=Tq_dias,
                Umax_cms=100 * Umax, excursion_m=excursion,
                excursion_sobre_canal=excursion / L_CANAL)


def main():
    out = Path(__file__).resolve().parent.parent / "resultados"
    out.mkdir(exist_ok=True)

    S, Rmax, W, llen = marea_diaria()
    print(f"marea EOT20: {llen:.2f} llenantes por dia; subida diaria total p5/p50/p95 = "
          f"{np.percentile(S, 5):.2f}/{np.median(S):.2f}/{np.percentile(S, 95):.2f} m; mayor llenante del dia "
          f"{np.percentile(Rmax, 5):.2f}/{np.median(Rmax):.2f}/{np.percentile(Rmax, 95):.2f} m")
    k = RNG.integers(0, len(S), N)                                   # dias reales al azar
    central = calcula(S_m=np.median(S), Rmax_m=np.median(Rmax), W_ms=np.median(W), **{q: v[0] for q, v in ENTRADAS.items()})
    mc = calcula(S_m=S[k], Rmax_m=Rmax[k], W_ms=W[k], **{q: muestrea(*v) for q, v in ENTRADAS.items()})

    unidades = dict(V_hm3="hm3", P_hm3="hm3 (mayor llenante)", frac_pct="% por dia", Tf_dias="d", Tr_dias="d",
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
    bins = np.linspace(0, 80, 81)
    for k, lab, c in [("Tf_dias", r"no return flow ($\beta=0$)", "C0"), ("Tr_dias", r"return flow $\beta$ + rivers", "C1")]:
        ax[0].hist(np.clip(mc[k], 0, 80), bins=bins, histtype="step", lw=1.5, color=c, label=lab)
        ax[0].axvline(np.median(mc[k]), color=c, ls=":", lw=1)
    ax[0].text(79, 0.55, "JICA (2004):\n~4 months \u2192", transform=ax[0].get_xaxis_transform(), ha="right", va="center", fontsize=8)
    ax[0].set_xlim(0, 80); ax[0].set_xlabel("flushing time (days; last bin includes > 80)"); ax[0].set_ylabel("samples")
    ax[0].legend(frameon=False, fontsize=8)
    ax[1].hist(mc["excursion_m"], bins=60, color="0.6")
    ax[1].axvline(L_CANAL, color="k", ls="--")
    ax[1].text(L_CANAL - 30, ax[1].get_ylim()[1] * .95, f"channel length\n{L_CANAL:.0f} m", va="top", ha="right", fontsize=8)
    ax[1].set_xlabel("tidal excursion in channel (m)")
    for a_, l_ in zip(ax, "ab"): a_.text(0.01, 0.98, f"({l_})", transform=a_.transAxes, va="top", fontweight="bold")
    fig.tight_layout(); fig.savefig(out / "prisma_marea.png", dpi=200)
    print(f"guardado: {out/'prisma_marea.csv'}, {out/'prisma_marea.png'}")


if __name__ == "__main__":
    main()
