#!/usr/bin/env python3
"""Figuras de resultados del articulo, a tamano final (ver docs/figuras_requisitos.md). Solo numpy + matplotlib + PIL.
Uso: python scripts/figuras_resultados.py [mecanismo robustez s2 marea]   (sin argumentos: todas) -> docs/figuras/articulo/
El prisma lo dibuja prisma_marea.py llamando a fig_prisma().  Las figuras 1-3 (mapas) estan en figuras_articulo.py (necesita scipy)."""
import csv, json, sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from estilo_figuras import (MM, ANCHO1, ANCHO2, NEGRO, NARANJA, CELESTE, VERDE, AZUL, BERMELLON, GRIS,    # noqa: E402
                            SALIDA, estilo, letra, guarda)

ZONAS = ["canal", "cuenca", "Marimelena", "Guasabacoa", "Atares"]
ZNOM = ["Channel", "Main basin", "Marimelena", "Guasabacoa", "Atarés"]


def miles(ax):
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1000:g}k" if v else "0"))


def fig_prisma(mc, l_canal):
    """Control analitico: tiempos de renovacion y excursion mareal (mc = muestras del Monte Carlo de prisma_marea.py)."""
    estilo()
    fig, ax = plt.subplots(1, 2, figsize=(ANCHO2, 72 * MM), constrained_layout=True)
    bins = np.linspace(0, 80, 81)
    for k, lab, c, ls in [("Tf_dias", r"no return flow ($\beta=0$)", AZUL, "-"),
                          ("Tr_dias", r"return flow $\beta$ + rivers", BERMELLON, "--")]:
        ax[0].hist(np.clip(mc[k], 0, 80), bins=bins, histtype="step", lw=1.0, color=c, ls=ls, label=lab)
        ax[0].axvline(np.median(mc[k]), color=c, ls=":", lw=0.8)
    ax[0].annotate("JICA (2004): ~4 months", xy=(80, 0.5), xycoords=("data", "axes fraction"), xytext=(-3, 0),
                   textcoords="offset points", ha="right", va="center", fontsize=6.5, arrowprops=None)
    ax[0].set_xlim(0, 80); ax[0].set_xlabel("Flushing time (d; last bin includes > 80 d)"); ax[0].set_ylabel("Samples")
    ax[0].legend(frameon=False, loc="upper right", bbox_to_anchor=(1, 0.92)); miles(ax[0])
    ax[1].hist(mc["excursion_m"], bins=60, color=GRIS)
    ax[1].axvline(l_canal, color=NEGRO, ls="--", lw=0.8)
    ax[1].text(l_canal - 25, 0.97, f"Channel length\n{l_canal:.0f} m", va="top", ha="right", fontsize=6.5,
               transform=ax[1].get_xaxis_transform())
    ax[1].set_xlabel("Tidal excursion in the channel (m)"); ax[1].set_ylabel("Samples"); miles(ax[1])
    for a_, l_ in zip(ax, "ab"): letra(a_, l_, x=0.015)
    guarda(fig, "fig_prisma", 190)


def cargar(base):
    d = np.load(RAIZ / base / "resumen.npz"); r = json.loads((RAIZ / base / "resumen.json").read_text())
    return d, r


def fig_mecanismo():
    """Edad media del agua: marea sola / + viento / + riosy densidad (1 ano). Barras: media ponderada por volumen, ultimos 30 d."""
    estilo()
    exp = [("runs/mecanismo/m0000", "Tide only", GRIS), ("runs/mecanismo/m0001", "Tide + wind", AZUL),
           ("runs/mecanismo/m0002", "Tide + wind + rivers (density)", BERMELLON)]
    fig, (a, b) = plt.subplots(1, 2, figsize=(ANCHO2, 72 * MM), constrained_layout=True,
                               gridspec_kw=dict(width_ratios=[1.25, 1]))
    for base, lab, c in exp:
        d, r = cargar(base)
        a.plot(d["dias"], d["serie_bahia"], color=c, lw=0.8, label=lab)
    a.plot([0, 250], [0, 250], color=NEGRO, ls=":", lw=0.7)
    a.text(200, 172, "no renewal (1 d d$^{-1}$)", fontsize=6.5, ha="left", va="center")
    a.set_xlim(0, 365); a.set_ylim(0, 250)
    a.set_xlabel("Simulated days (from 1 Jan 2016)"); a.set_ylabel("Bay-mean water age (d)")
    a.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.9))
    x = np.arange(len(ZONAS)); w = 0.27
    for i, (base, lab, c) in enumerate(exp):
        _, r = cargar(base)
        b.bar(x + (i - 1) * w, [r[f"edad_media_d_{z}"] for z in ZONAS], w, color=c, label=lab)
    b.set_yscale("log"); b.set_ylim(2, 600)
    b.set_xticks(x); b.set_xticklabels(ZNOM, fontsize=6.5, rotation=25, ha="right", rotation_mode="anchor")
    b.set_ylabel("Mean age, last 30 d (d)")
    letra(a, "a"); letra(b, "b")
    guarda(fig, "fig_mechanism", 190)


def fig_robustez():
    """Edad de la bahia en los 120 d de los experimentos de robustez (una columna)."""
    estilo()
    exp = [("m0000", "base (salinity-driven density)", NEGRO, "-"),
           ("m0001", "+ heat flux (ERA5), fixed 28 °C boundary", BERMELLON, "-"),
           ("m0005", "+ heat flux, OISST boundary", NARANJA, "-"),
           ("m0002", r"k-$\varepsilon$ closure", AZUL, "--"),
           ("m0003", "32 vertical levels", VERDE, ":"),
           ("m0004", "diffusivity $\\times$10", CELESTE, "-.")]
    fig, ax = plt.subplots(figsize=(ANCHO1, 62 * MM), constrained_layout=True)
    ax.axvspan(90, 120, color="0.92", lw=0)
    for m, lab, c, ls in exp:
        f = RAIZ / "runs" / "robustez" / m / "resumen.npz"
        if not f.exists():
            print(f"(sin {m}: no se dibuja)"); continue
        d = np.load(f); ax.plot(d["dias"], d["serie_bahia"], color=c, ls=ls, lw=0.8, label=lab)
    ax.text(105, 0.8, "metric\nwindow", ha="center", va="bottom", fontsize=6, color="0.4")
    ax.set_xlim(0, 120); ax.set_ylim(0, 32)
    ax.set_xlabel("Simulated days (from 1 Jan 2016)"); ax.set_ylabel("Bay-mean water age (d)")
    ax.legend(frameon=False, loc="upper left", fontsize=6, handlelength=2.2, labelspacing=0.25)
    guarda(fig, "fig_robustness", 90)


def fig_s2():
    """Sentinel-2 (frecuencia de anomalias) frente al agua dulce en superficie del modelo, y distribucion nula de rho."""
    import comparacion_s2 as c2
    estilo()
    s2 = np.load(c2.S2); sat = s2["persistencia"][:252]
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz")
    mod = c2.campo_medio(RAIZ / "runs" / "mecanismo" / "m0002", "s2_dulce") * 100        # %
    ok = c2.pixeles(s2, mod); rho = c2.spearman(sat[ok], mod[ok])
    # control (mismo orden de uso del generador que c2.main, para reproducir el JSON)
    rng = np.random.default_rng(20261021); c2.prueba_rho(sat, mod / 100, ok, rng)
    base = c2.pixeles(s2, np.ones_like(sat)); ok0 = base & np.isfinite(mod); nul = []
    while len(nul) < c2.NDESPL:
        dy, dx = rng.integers(-sat.shape[0], sat.shape[0]), rng.integers(-sat.shape[1], sat.shape[1])
        if np.hypot(dy, dx) < c2.DESPL_MIN_PX: continue
        ss, bs_ = np.roll(sat, (dy, dx), (0, 1)), np.roll(base, (dy, dx), (0, 1)); o = bs_ & np.isfinite(mod)
        if o.sum() < c2.SOLAPE_MIN: continue
        nul.append(c2.spearman(ss[o], mod[o]))
    nul = np.array(nul); p = (1 + np.sum(nul >= rho)) / (1 + len(nul)); p95 = np.percentile(nul, 95)
    ref = json.loads((RAIZ / "resultados" / "comparacion_s2" / "m0002_s2_dulce.json").read_text())
    assert abs(p - ref["p_desplazamientos"]) < 1e-9 and abs(p95 - ref["rho_nulo_p95"]) < 1e-9 and abs(rho - ref["rho"]) < 1e-9, \
        (p, p95, rho, ref)                                                              # la figura reproduce el JSON
    e, n = M["s2_e"] / 1000, M["s2_n"] / 1000
    ext = [e[0] - 0.01, e[-1] + 0.01, n[0] - 0.01, n[-1] + 0.01]
    fig = plt.figure(figsize=(ANCHO2, 70 * MM), constrained_layout=True)
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.9])
    a, b, c = (fig.add_subplot(g) for g in gs)
    cm = plt.get_cmap("viridis").copy(); cm.set_bad("white")
    ims = [(a, np.where(np.isfinite(sat), sat * 100, np.nan), "Sentinel-2 anomaly frequency", "% of valid scenes"),
           (b, mod, "Model surface freshwater fraction", "%")]
    for ax, campo, tit, lab in ims:
        im = ax.imshow(np.ma.masked_invalid(campo), origin="lower", extent=ext, cmap=cm, interpolation="nearest",
                       vmin=0, vmax=np.nanpercentile(campo, 99))
        ax.set_title(tit); ax.set_xlabel("Easting (km, UTM 17N)"); ax.set_ylabel("Northing (km)")
        ax.ticklabel_format(useOffset=False, style="plain")
        fig.colorbar(im, ax=ax, fraction=0.05, pad=0.02).set_label(lab)
    c.hist(nul, bins=40, color=GRIS)
    c.axvline(rho, color=BERMELLON, lw=1.0); c.axvline(p95, color=NEGRO, ls="--", lw=0.8)
    c.set_ylim(0, 75)
    c.text(rho - 0.03, 0.97, f"observed\n$\\rho$ = {rho:.2f}", color=BERMELLON, ha="right", va="top", fontsize=6.5,
           transform=c.get_xaxis_transform())
    c.text(p95 + 0.03, 0.97, f"null P95\n{p95:.2f}", ha="left", va="top", fontsize=6.5, transform=c.get_xaxis_transform())
    c.set_xlabel(r"Spearman $\rho$ under cyclic shifts"); c.set_ylabel("Shifts"); c.set_title(f"Null distribution (p = {p:.2f})")
    for ax_, l_ in zip((a, b, c), "abc"): letra(ax_, l_)
    guarda(fig, "fig_sentinel2", 190)


def fig_marea():
    """Marea en el borde: amplitudes FES2022 / EOT20 y diferencia de nivel en enero de 2016 (RMS en cm)."""
    estilo()
    D = {n: json.loads((RAIZ / "datos" / "marea" / f"{n}_habana.json").read_text()) for n in ("fes2022", "eot20")}
    comunes = [k for k in D["eot20"] if k in D["fes2022"]]
    vel = dict(m2=28.9841042, s2=30.0, n2=28.4397295, k2=30.0821373, k1=15.0410686, o1=13.9430356, p1=14.9589314,
               q1=13.3986609, m4=57.9682084)                                  # deg/h
    def punto(n, k, lon=-82.36, lat=23.20):                              # celda valida mas cercana, como prisma_marea.py
        d = D[n][k]; A = np.array(d["amp_m"]); G = np.radians(np.array(d["fase_grados"]))
        LA, LO = np.meshgrid(d["lat"], d["lon"], indexing="ij"); ok = np.isfinite(A) & (A > 0)
        j, i = np.unravel_index(np.where(ok, np.hypot(LA - lat, LO - lon), 9).argmin(), A.shape)
        return A[j, i] * 100 * np.exp(-1j * G[j, i])
    z = {n: np.array([punto(n, k) for k in comunes]) for n in D}
    amp = {n: np.abs(z[n]) for n in D}; fas = {n: -np.degrees(np.angle(z[n])) for n in D}   # cm; lag de Greenwich (grados)
    rms_ex = float(np.sqrt(0.5 * np.sum(np.abs(z["eot20"] - z["fes2022"]) ** 2)))          # RMS exacto (registro largo)
    # argumento astronomico (sin correccion nodal: igual en los dos modelos, solo ilustra el mes)
    t = np.arange(0, 31 * 24 + 0.1, 0.5); d = 5843.5 + t / 24
    s, h, p = (218.3165 + 13.17639648 * d), (280.4661 + 0.98564736 * d), (83.3535 + 0.11140353 * d); T = 15 * t
    V0 = dict(m2=2 * (T + h - s), s2=2 * T, n2=2 * (T + h - s) - s + p, k2=2 * T + 2 * h, k1=T + h + 90,
              o1=T + h - 2 * s - 90, p1=T - h + 90, q1=T + h - 3 * s + p - 90, m4=4 * (T + h - s))
    def nivel(n):
        return sum(amp[n][i] * np.cos(np.radians(vel[k] * t + V0[k] - fas[n][i])) for i, k in enumerate(comunes))
    eot, dif = nivel("eot20"), nivel("eot20") - nivel("fes2022")
    rms_mes = float(np.sqrt(np.mean(dif ** 2)))
    print(f"marea: RMS de la diferencia EOT20-FES2022 = {rms_ex:.2f} cm (exacto), {rms_mes:.2f} cm (enero 2016); "
          f"constituyentes comunes: {', '.join(comunes)}")
    fig, (a, b) = plt.subplots(1, 2, figsize=(ANCHO2, 70 * MM), constrained_layout=True, gridspec_kw=dict(width_ratios=[1, 1.35]))
    x = np.arange(len(comunes)); w = 0.4
    a.bar(x - w / 2, amp["fes2022"], w, color=AZUL, label="FES2022"); a.bar(x + w / 2, amp["eot20"], w, color=NARANJA, label="EOT20")
    a.set_xticks(x); a.set_xticklabels([k.upper() for k in comunes]); a.set_ylabel("Amplitude (cm)"); a.legend(frameon=False)
    b.plot(t / 24, eot, color=GRIS, lw=0.6, label="EOT20 level")
    b.plot(t / 24, dif, color=BERMELLON, lw=0.9, label="EOT20 $-$ FES2022")
    b.axhline(0, color=NEGRO, lw=0.4)
    b.text(0.99, 0.05, f"RMS of the difference: {rms_mes:.1f} cm", transform=b.transAxes, ha="right", va="bottom")
    b.set_xlim(0, 31); b.set_ylim(-40, 46); b.set_xlabel("Days from 1 Jan 2016"); b.set_ylabel("Water level (cm)")
    b.legend(frameon=False, loc="upper right", ncol=2)
    letra(a, "a"); letra(b, "b")
    guarda(fig, "fig_tide", 190)


PARAM = dict(carta="Chart edition", alfa="Dredging state", semilla="Chart-error field", datum="Datum offset",
             cd="Bottom drag $C_d$", vfac="Wind speed", vrot="Wind direction", mfac="Tide amplitude", qfac="River discharge")
ZNOM6 = ZNOM + ["Bay"]
CONJUNTO = RAIZ / "resultados" / "conjunto"


def _raster(M, campo):
    """Campo por nodo -> rejilla Sentinel-2 de 20 m (igual que posproceso.py)."""
    si, sw = M["s2_i"], M["s2_w"]
    return np.where(si[:, 0] < 0, np.nan, (campo[si] * sw).sum(1)).reshape(M["s2_forma"])


def fig_conjunto(dir=CONJUNTO, salida=SALIDA):
    """Fig. 5: edad media por zona entre los miembros (mediana, P5-P95) y mapas de P(edad en superficie > 7 y 14 d)."""
    estilo()
    filas = list(csv.DictReader(open(Path(dir) / "prob_zonas.csv"))); p = np.load(Path(dir) / "prob_edad_sup.npz")
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); e, n = M["s2_e"] / 1000, M["s2_n"] / 1000
    ext = [e[0] - 0.01, e[-1] + 0.01, n[0] - 0.01, n[-1] + 0.01]
    fig = plt.figure(figsize=(ANCHO2, 72 * MM), constrained_layout=True)
    a, b, c = (fig.add_subplot(g) for g in fig.add_gridspec(1, 3, width_ratios=[1.15, 1, 1]))
    x = np.arange(len(zonas)); med = np.array([np.median(sin[z]) for z in zonas]); lo, hi = (np.array([np.percentile(sin[z], q) for z in zonas]) for q in (5, 95))   # 17-nov (V3 X6): sin calor, los MISMOS 64 miembros
    a.errorbar(x, med, yerr=[med - lo, hi - med], fmt="o", color=AZUL, ms=3, capsize=2, lw=0.8)
    for u, ls in ((7, "--"), (14, ":")):
        a.axhline(u, color=NEGRO, ls=ls, lw=0.6); a.text(-0.45, u + 0.25, f"{u} d", ha="left", va="bottom", fontsize=6)
    a.set_xlim(-0.5, len(x) - 0.5); a.set_xticks(x); a.set_xticklabels(ZNOM6[:len(x)], rotation=25, ha="right", rotation_mode="anchor")
    a.set_ylim(0, max(16, hi.max() * 1.1)); a.set_ylabel("Mean age, last 30 d (d)")
    for ax, u in ((b, 7), (c, 14)):
        im = ax.imshow(np.ma.masked_invalid(_raster(M, p[f"p_mayor_{u:g}d"])), origin="lower", extent=ext, vmin=0, vmax=1,
                       cmap="viridis", interpolation="nearest")
        ax.set_title(f"P(surface age > {u} d)"); ax.set_xlabel("Easting (km, UTM 17N)")
        ax.ticklabel_format(useOffset=False, style="plain")
    b.set_ylabel("Northing (km)"); c.set_yticklabels([])
    fig.colorbar(im, ax=[b, c], fraction=0.04, pad=0.02).set_label("Probability across members")
    letra(a, "a"); letra(b, "b", x=0.84); letra(c, "c", x=0.84)      # en los mapas, arriba a la derecha (el NO tiene mar abierto)
    guarda(fig, "fig_ensemble", 190, salida)


def fig_sobol(dir=CONJUNTO, salida=SALIDA):
    """Fig. 6: indices de Sobol (Jansen) de la edad media: S1 y ST con IC 95 % para la bahia y ST por zona."""
    estilo()
    filas = list(csv.DictReader(open(Path(dir) / "sobol.csv"))); params = list(dict.fromkeys(r["parametro"] for r in filas))
    g = lambda m, p, k: float(next(r[k] for r in filas if r["metrica"] == m and r["parametro"] == p) or "nan")
    zon = ["canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(ANCHO2, 80 * MM), constrained_layout=True, gridspec_kw=dict(width_ratios=[1, 1.15]))
    y = np.arange(len(params))[::-1]; m = "edad_media_d_bahia"
    for off, k, lo, hi, c, mk, lab in ((0.16, "ST", "ST_lo", "ST_hi", AZUL, "o", "$S_T$"), (-0.16, "S1", "S1_lo", "S1_hi", BERMELLON, "s", "$S_1$")):
        v = np.array([g(m, q, k) for q in params]); l = np.array([g(m, q, lo) for q in params]); h = np.array([g(m, q, hi) for q in params])
        a.errorbar(v, y + off, xerr=[v - l, h - v], fmt=mk, color=c, mfc=c if mk == "o" else "white", ms=3, capsize=1.5, lw=0.8, label=lab)
    a.axvline(0, color=NEGRO, lw=0.4); a.set_yticks(y); a.set_yticklabels([PARAM.get(q, q) for q in params])
    a.set_xlabel("Sobol index (bay-mean age; bars: 95 % CI)"); a.legend(frameon=False, loc="upper right")
    T = np.array([[g(f"edad_media_d_{z}", q, "ST") for z in zon] for q in params])
    im = b.imshow(T, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            if np.isfinite(T[i, j]): b.text(j, i, f"{T[i, j]:.2f}", ha="center", va="center", fontsize=6, color="white" if T[i, j] > 0.55 else "black")
    b.set_xticks(range(len(zon))); b.set_xticklabels(ZNOM6, rotation=25, ha="right", rotation_mode="anchor")
    b.set_yticks(range(len(params))); b.set_yticklabels([PARAM.get(q, q) for q in params])
    fig.colorbar(im, ax=b, fraction=0.04, pad=0.02).set_label("Total Sobol index $S_T$")
    letra(a, "a", x=0.01); letra(b, "b", x=-0.02, y=1.075)
    guarda(fig, "fig_sobol", 190, salida)


TRAZ = RAIZ / "runs" / "trazadores"
RIOS_NOM = ["Luyanó", "Martín Pérez", "Tadeo"]; ZONAS_TRAZ = ["canal", "cuenca", "Marimelena", "Guasabacoa", "Atarés"]


def fig_rios(dir=TRAZ, salida=SALIDA):
    """Fig. 8: agua de cada rio (trazador pasivo por rio, protocolo del 8-nov). (a-c) fraccion en superficie, caso T0, escala comun;
    (d) T_i = M_i/Q_i por rio (T0 en circulo; T1-T3 en puntos grises); (e) reparto de M_i por zona (T0; barras: rango de los 4 casos)."""
    estilo(); dir = Path(dir)
    R = [json.loads((dir / f"m000{k}" / "trazadores.json").read_text()) for k in range(4)]; mp = np.load(dir / "m0000" / "trazadores.npz")
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); e, n = M["s2_e"] / 1000, M["s2_n"] / 1000
    ext = [e[0] - 0.01, e[-1] + 0.01, n[0] - 0.01, n[-1] + 0.01]
    from matplotlib.colors import LogNorm
    fig = plt.figure(figsize=(ANCHO2, 108 * MM), constrained_layout=True)
    g = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 0.06], height_ratios=[1.25, 1])
    mapas = [fig.add_subplot(g[0, i]) for i in range(3)]; d = fig.add_subplot(g[1, 0]); r = fig.add_subplot(g[1, 1:3])
    for i, ax in enumerate(mapas):
        z = 100 * _raster(M, mp[f"sup_{i}"].astype(float)); z = np.where(z > 0, z, np.nan)
        im = ax.imshow(np.ma.masked_invalid(z), origin="lower", extent=ext, cmap="viridis", norm=LogNorm(0.01, 10), interpolation="nearest")
        ax.set_title(RIOS_NOM[i]); ax.set_xlabel("Easting (km, UTM 17N)"); ax.ticklabel_format(useOffset=False, style="plain")
        ax.set_aspect("equal"); letra(ax, "abc"[i], x=0.02)
        if i: ax.set_yticklabels([])
    mapas[0].set_ylabel("Northing (km)")
    fig.colorbar(im, cax=fig.add_subplot(g[0, 3])).set_label("River water in surface layer (%)")
    x = np.arange(3); T = np.array([q["T_d"] for q in R])                                  # (caso, rio)
    d.axhline(7, color=NEGRO, ls="--", lw=0.6); d.text(-0.4, 7.15, "7 d", ha="left", va="bottom", fontsize=6)
    d.plot(x, T[0], "o", color=AZUL, ms=4, label="T0 (central)")
    for k, (mk, c) in enumerate((("v", NARANJA), ("^", BERMELLON), ("s", VERDE)), 1): d.plot(x, T[k], mk, color=c, ms=3, label=("T1 Q×0.25", "T2 Q×2", "T3 heat flux")[k - 1])
    d.set_xticks(x); d.set_xticklabels(RIOS_NOM, rotation=20, ha="right", rotation_mode="anchor"); d.set_xlim(-0.5, 2.5)
    d.set_ylim(0, max(10, T.max() * 1.15)); d.set_ylabel("Renewal time $T_i=M_i/Q_i$ (d)"); d.legend(frameon=False, fontsize=5.5, loc="upper right", ncol=2, handletextpad=0.2, columnspacing=0.8)
    letra(d, "d", x=0.02)
    rep = np.array([[q[f"reparto_{z.replace('é', 'e')}"] for z in ZONAS_TRAZ] for q in R])   # (caso, zona, rio)
    w = 0.26
    for i, c in enumerate((AZUL, NARANJA, VERDE)):
        y = 100 * rep[0, :, i]; lo, hi = 100 * rep[:, :, i].min(0), 100 * rep[:, :, i].max(0)
        r.bar(np.arange(len(ZONAS_TRAZ)) + (i - 1) * w, y, w, color=c, label=RIOS_NOM[i], yerr=[y - lo, hi - y], error_kw=dict(lw=0.6, capsize=1.2))
    r.set_xticks(range(len(ZONAS_TRAZ))); r.set_xticklabels(["Channel", "Main basin", "Marimelena", "Guasabacoa", "Atarés"])
    r.set_ylabel("Share of each river's water (%)"); r.set_ylim(0, r.get_ylim()[1] * 1.18); r.legend(frameon=False, fontsize=5.5, ncol=3, loc="upper right"); letra(r, "e", x=0.01)
    guarda(fig, "fig_rivers", 190, salida, alto_max=115)


def fig_borde(dir=RAIZ / "runs" / "conjunto", salida=SALIDA):
    """S1: velocidades espurias en los 704 miembros. (a) donde esta la velocidad maxima (media en la vertical, maximo en los
    120 d) de cada miembro; (b) esa velocidad frente a la edad de la bahia; (c) lo mismo con la maxima dentro de la bahia
    (nodos someros que tocan el limite rmaxvel = 5 m/s por componente). Spearman en (b) y (c)."""
    estilo(); L = (dir / "m0000" / "hgrid.gr3").read_text().split("\n"); ne, nn = map(int, L[1].split()[:2])
    xy = np.array([[float(v) for v in l.split()[1:3]] for l in L[2:2 + nn]]) / 1000
    tri = np.array([[int(c) - 1 for c in l.split()[2:5]] for l in L[2 + nn:2 + nn + ne]])
    k = 2 + nn + ne; nb = int(L[k + 2].split()[0]); borde = np.array([int(L[k + 3 + i].split()[0]) - 1 for i in range(nb)])
    R = [json.loads(f.read_text()) for f in sorted(dir.glob("m[0-9]*/resumen.json"))]
    v = np.array([r["vmax"] for r in R]); e = np.array([r["edad_media_d_bahia"] for r in R]); nod = np.array([r["vmax_nodo"] for r in R]) - 1
    zona = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz")["zona"]
    vb = np.array([r["vmax_bahia"] for r in R]); rk = lambda a: np.argsort(np.argsort(a))
    rho, rhob = (float(np.corrcoef(rk(x), rk(e))[0, 1]) for x in (v, vb))
    fig, (a, b, c3) = plt.subplots(1, 3, figsize=(ANCHO2, 66 * MM), constrained_layout=True, gridspec_kw=dict(width_ratios=[1.3, 1, 1]))
    a.triplot(xy[:, 0], xy[:, 1], tri, color=GRIS, lw=0.1)
    a.tripcolor(xy[:, 0], xy[:, 1], tri, np.where(zona > 0, 1.0, np.nan), cmap="Blues", vmin=0, vmax=2.5)
    a.plot(xy[borde, 0], xy[borde, 1], color=NEGRO, lw=1.2, label="Open boundary")
    u, c = np.unique(nod, return_counts=True)
    a.scatter(xy[u, 0], xy[u, 1], s=4 + 60 * c / c.max(), color=BERMELLON, zorder=3, label="Location of max. speed\n(size: no. of members)")
    a.set_aspect("equal"); a.set_xlabel("Easting (km, UTM 17N)"); a.set_ylabel("Northing (km)"); a.ticklabel_format(useOffset=False, style="plain")
    a.legend(frameon=False, loc="lower left", fontsize=6); letra(a, "a")
    b.scatter(v, e, s=3, color=AZUL, lw=0)
    b.set_xlabel("Max. speed in the domain (m s$^{-1}$)"); b.set_ylabel("Bay mean age, last 30 d (d)")
    c3.scatter(vb, e, s=3, color=AZUL, lw=0); c3.set_xlabel("Max. speed inside the bay (m s$^{-1}$)"); c3.set_yticklabels([])
    c3.set_ylim(b.get_ylim()); c3.text(0.97, 0.97, f"Spearman $\\rho$ = {rhob:.2f}", transform=c3.transAxes, ha="right", va="top", fontsize=6, bbox=dict(fc="white", ec="none", alpha=0.85, pad=1)); letra(c3, "c")
    b.text(0.97, 0.97, f"Spearman $\\rho$ = {rho:.2f}\nn = {len(v)}", transform=b.transAxes, ha="right", va="top", fontsize=6, bbox=dict(fc="white", ec="none", alpha=0.85, pad=1)); letra(b, "b")
    print(f"S1: {np.isin(nod, borde).mean():.0%} de los maximos en nodos del borde abierto; rho = {rho:.3f}; vmax P5-P50-P95 {np.percentile(v, [5, 50, 95]).round(2)}; "
          f"bahia: rho = {rhob:.3f}, P50 {np.median(vb):.2f}, > 3 m/s en {(vb > 3).sum()} miembros")
    guarda(fig, "figS_boundary", 190, salida, alto_max=80)


def fig_resumen(dir=CONJUNTO, salida=SALIDA):
    """Resumen grafico (Elsevier: >= 1328 x 531 px; 15 x 6,2 cm), 17-nov (V3 X6) titular «One structural choice weighs as much as nine uncertain inputs»: mapa de la edad mediana (conjunto sin calor),
    edad por zona (mediana y P5-P95) del conjunto (128 miembros) y de los 64 miembros con flujo de calor + OISST, e indices S_T; el flujo de calor va aparte, en dias."""
    estilo(); plt.rcParams.update({"font.size": 7.5, "axes.titlesize": 7.5})
    filas = list(csv.DictReader(open(Path(dir) / "prob_zonas.csv"))); p = np.load(Path(dir) / "prob_edad_sup.npz")
    sob = [r for r in csv.DictReader(open(Path(dir) / "sobol.csv")) if r["metrica"] == "edad_media_d_bahia"]
    sob.sort(key=lambda r: float(r["ST"]))
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); e, n = M["s2_e"] / 1000, M["s2_n"] / 1000
    ext = [e[0] - 0.01, e[-1] + 0.01, n[0] - 0.01, n[-1] + 0.01]
    zonas = ["canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia"]
    lee = lambda d, k, z: json.loads((RAIZ / "runs" / d / f"m{k:04d}" / "resumen.json").read_text())[f"edad_media_d_{z}"]
    cal = {z: np.array([lee("conjunto_calor", k, z) for k in range(64)]) for z in zonas}; sin = {z: np.array([lee("conjunto", k, z) for k in range(64)]) for z in zonas}; sin64 = sin["bahia"]
    desp = float(np.median(cal["bahia"] - sin64)); rango = float(np.percentile(sin64, 95) - np.percentile(sin64, 5))   # 17-nov: 64 miembros, diferencia pareada y rango de los MISMOS 64 sin calor (R = desp / rango)
    print(f"calor (n=64): bahia mediana {np.median(cal['bahia']):.2f} d, P5-P95 {np.percentile(cal['bahia'], 5):.2f}-{np.percentile(cal['bahia'], 95):.2f}; sin calor (mismos 64) {np.median(sin64):.2f}; desplazamiento pareado {desp:.2f} d; rango P5-P95 sin calor (mismos 64) {rango:.2f} d")
    fig = plt.figure(figsize=(150 * MM, 62 * MM), constrained_layout=True)
    g = fig.add_gridspec(1, 3, width_ratios=[0.85, 1.15, 1.25])
    a, b = fig.add_subplot(g[0]), fig.add_subplot(g[1]); cc = g[2].subgridspec(2, 1, height_ratios=[3.2, 1.25]); c, d = fig.add_subplot(cc[0]), fig.add_subplot(cc[1])
    im = a.imshow(np.ma.masked_invalid(_raster(M, p["p50"])), origin="lower", extent=ext, cmap="viridis", vmin=0, vmax=14, interpolation="nearest")
    a.set_xticks([]); a.set_yticks([]); a.set_title("Median surface age\n(no heat flux)")
    fig.colorbar(im, ax=a, fraction=0.05, pad=0.02, ticks=[0, 7, 14]).set_label("d", labelpad=1)
    x = np.arange(len(filas)); med, lo, hi = (np.array([float(r[k]) for r in filas]) for k in ("p50", "p5", "p95"))
    b.errorbar(x - 0.13, med, yerr=[med - lo, hi - med], fmt="o", color=AZUL, ms=3.2, capsize=2, lw=1, label="No heat flux (64)")
    mc = np.array([np.median(cal[z]) for z in zonas]); lc, hc = (np.array([np.percentile(cal[z], q) for z in zonas]) for q in (5, 95))
    b.errorbar(x + 0.13, mc, yerr=[mc - lc, hc - mc], fmt="s", color=NARANJA, ms=3.0, capsize=2, lw=1, label="With heat flux (64)")
    for v, t in ((7, "1 week"), (14, "2 weeks")):
        b.axhline(v, color=NEGRO, ls="--", lw=0.6); b.text(-1.05, v + 0.3, t, ha="left", va="bottom", fontsize=5.8)
    b.legend(frameon=False, loc="upper left", fontsize=5.4, handletextpad=0.2, borderaxespad=0.1)
    b.set_xticks(x); b.set_xticklabels(["Channel", "Basin", "Marimelena", "Guasabacoa", "Atarés", "Bay"], rotation=35, ha="right", rotation_mode="anchor", fontsize=6.5)
    b.set_ylim(0, 24); b.set_xlim(-1.1, len(x) - 0.4); b.set_ylabel("Mean age (d)"); b.set_title("Age by zone")
    y = np.arange(len(sob)); st = np.array([float(r["ST"]) for r in sob])
    c.barh(y, st, color=[BERMELLON if r["parametro"] == "qfac" else GRIS for r in sob], height=0.7)
    c.set_yticks(y); c.set_yticklabels([PARAM.get(r["parametro"], r["parametro"]) for r in sob], fontsize=5.8)
    c.set_xlim(0, 1); c.set_xlabel("Total Sobol index $S_T$", labelpad=1); c.set_title("Parameter effects")
    d.barh([1, 0], [desp, rango], color=[NARANJA, GRIS], height=0.7); d.set_yticks([1, 0]); d.set_yticklabels(["Heat flux (structural):\npaired median shift", "Parameters: P5–P95\nrange (same 64)"], fontsize=5.8)
    d.set_xlim(0, 9); d.set_xticks([0, 3, 6, 9]); d.set_xlabel("Bay age (d)", labelpad=1)
    for yy, v in ((1, desp), (0, rango)): d.text(v + 0.15, yy, f"{v:.1f}", va="center", fontsize=6)
    fig.suptitle("One structural choice weighs as much as nine uncertain inputs", fontsize=8, fontweight="bold")
    png = salida / "graphical_abstract.png"; fig.savefig(png, dpi=300); fig.savefig(salida / "graphical_abstract.pdf"); plt.close(fig)
    from PIL import Image
    w, h = Image.open(png).size; assert w >= 1328 and h >= 531, (w, h); print(f"-> {png.name}: {w} x {h} px")


TODAS = dict(mecanismo=fig_mecanismo, robustez=fig_robustez, s2=fig_s2, marea=fig_marea)
CONJ = dict(conjunto=fig_conjunto, sobol=fig_sobol, rios=fig_rios, borde=fig_borde, resumen=fig_resumen)      # solo con el conjunto terminado: python scripts/figuras_resultados.py conjunto sobol

if __name__ == "__main__":
    for k in (sys.argv[1:] or TODAS): {**TODAS, **CONJ}[k]()
