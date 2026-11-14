#!/usr/bin/env python3
"""Convergencia de Sobol (revision V1, A2; lectura fijada en protocolo_metricas_conjunto.md, 14-nov): S1 y S_T de Jansen con
los j < N de cada bloque (N = 16, 32, 64) sobre las mismas 704 corridas, y S1 "dado los datos" por intervalos de cuantiles
con los 128 miembros A y B (muestras independientes; los AB_i repiten filas de A y sesgan este estimador) como comprobacion
cruzada, con el P95 de una nula por permutacion (el estimador tiene sesgo positivo con pocos datos). Solo numpy + matplotlib.
  python scripts/sobol_convergencia.py [runs/conjunto]  -> resultados/conjunto/sobol_convergencia.csv, docs/figuras/articulo/figS_sobol_convergence.*
  python scripts/sobol_convergencia.py --prueba         -> autoprueba sobre Ishigami (analisis_conjunto.prueba ya valida jansen)"""
import csv, json, sys
from pathlib import Path
import numpy as np
from analisis_conjunto import lee_diseno, sobol, SALIDA, RAIZ

NS, ZONAS, NBIN, NPERM = (16, 32, 64), ["canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia"], 8, 500
RNGP = np.random.default_rng(20261114)


def s1_bins(x, y, nb=NBIN):
    """S1 = Var(E[y|x]) / Var(y) con nb intervalos de cuantiles de x (estimador 'given data')."""
    ok = np.isfinite(y); x, y = x[ok], y[ok]
    b = np.minimum((np.argsort(np.argsort(x)) * nb) // len(x), nb - 1)
    m = np.array([y[b == k].mean() for k in range(nb)]); n = np.array([(b == k).sum() for k in range(nb)])
    return float((n * (m - y.mean()) ** 2).sum() / n.sum() / y.var())


def calcula(runs):
    filas, params = lee_diseno()
    res = []
    for f in filas:
        try: r = json.loads((runs / f"m{int(f['miembro']):04d}" / "resumen.json").read_text())
        except (OSError, ValueError): r = None
        res.append(r if r and not r.get("nan", 0) else None)
    bl = np.array([f["bloque"] for f in filas]); j = np.array([int(f["j"]) for f in filas])
    U = np.array([[float(f[f"u_{p}"]) for p in params] for f in filas])
    out = []
    for z in ZONAS:
        y = np.array([r.get(f"edad_media_d_{z}", np.nan) if r else np.nan for r in res], float)
        for N in NS:
            s = j < N
            for p, S, slo, shi, T, tlo, thi, n in sobol(y[s], bl[s], j[s], params, N):
                out.append(dict(zona=z, N=N, parametro=p, S1=S, S1_lo=slo, S1_hi=shi, ST=T, ST_lo=tlo, ST_hi=thi, n=n))
        ab = np.isin(bl, ["A", "B"]) & np.isfinite(y)
        for i, p in enumerate(params):   # semilla y carta no son continuas: su S1 por intervalos no tiene sentido
            if p in ("semilla", "carta"): s1 = nulo = np.nan
            else:
                s1 = s1_bins(U[ab, i], y[ab])
                nulo = float(np.percentile([s1_bins(U[ab, i], RNGP.permutation(y[ab])) for _ in range(NPERM)], 95))
            out.append(dict(zona=z, N="AB_intervalos", parametro=p, S1=s1, S1_lo=np.nan, S1_hi=nulo, ST=np.nan, ST_lo=np.nan,
                            ST_hi=np.nan, n=int(ab.sum())))   # S1_hi = P95 de la nula por permutacion
    return out, params


def orden(out, z="bahia"):
    for N in NS:
        r = sorted((o for o in out if o["zona"] == z and o["N"] == N), key=lambda o: -o["ST"])
        print(f"{z} N={N}: " + ", ".join(f"{o['parametro']} {o['ST']:.3f} [{o['ST_lo']:.3f}-{o['ST_hi']:.3f}]" for o in r[:3]))


def figura(out, params):
    sys.path.insert(0, str(Path(__file__).parent))
    from estilo_figuras import MM, ANCHO2, AZUL, BERMELLON, VERDE, NARANJA, CELESTE, ROSA, GRIS, NEGRO, AMARILLO, estilo, letra, guarda, plt
    from figuras_resultados import PARAM
    estilo(); col = dict(zip(params, [GRIS, AMARILLO, VERDE, CELESTE, ROSA, NARANJA, AZUL, NEGRO, BERMELLON]))
    fig, axs = plt.subplots(1, 2, figsize=(ANCHO2, 80 * MM), constrained_layout=True)
    for ax, k, lab in ((axs[0], "ST", "Total index $S_T$ (bay-mean age)"), (axs[1], "S1", "First-order index $S_1$ (bay-mean age)")):
        for i, p in enumerate(params):
            r = [next(o for o in out if o["zona"] == "bahia" and o["N"] == N and o["parametro"] == p) for N in NS]
            v = np.array([o[k] for o in r]); lo = np.array([o[k + "_lo"] for o in r]); hi = np.array([o[k + "_hi"] for o in r])
            x = np.log2(NS) + (i - 4) * 0.035
            ax.errorbar(x, v, yerr=[v - lo, hi - v], color=col[p], marker="o", ms=2.5, lw=0.7, capsize=1.2, elinewidth=0.5, label=PARAM.get(p, p))
        ax.set_xticks(np.log2(NS)); ax.set_xticklabels([str(N) for N in NS]); ax.set_xlabel("Base sample size $N$ (members = 11 $N$)")
        ax.set_ylabel(lab); ax.axhline(0, color=NEGRO, lw=0.4)
    fig.legend(*axs[0].get_legend_handles_labels(), loc="outside lower center", ncol=5, frameon=False, fontsize=6)
    letra(axs[0], "a"); letra(axs[1], "b")
    guarda(fig, "figS_sobol_convergence", 190)


def prueba():
    import tempfile
    from analisis_conjunto import jansen
    rng = np.random.default_rng(0); x = rng.uniform(-np.pi, np.pi, (20000, 3))
    y = np.sin(x[:, 0]) + 7 * np.sin(x[:, 1]) ** 2 + 0.1 * x[:, 2] ** 4 * np.sin(x[:, 0])
    assert abs(s1_bins(x[:, 0], y, 50) - 0.314) < 0.03 and abs(s1_bins(x[:, 1], y, 50) - 0.442) < 0.03 and s1_bins(x[:, 2], y, 50) < 0.03
    print("prueba ok: S1 por intervalos reproduce Ishigami (0,31 / 0,44 / 0)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--prueba"]: prueba(); sys.exit()
    runs = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "runs" / "conjunto"
    out, params = calcula(runs)
    with open(SALIDA / "sobol_convergencia.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader()
        for o in out: w.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in o.items()})
    for z in ZONAS: orden(out, z)
    print("S1 por intervalos (A y B, 128; entre corchetes P95 de la nula), bahia: " + ", ".join(
        f"{o['parametro']} {o['S1']:.3f} [{o['S1_hi']:.3f}]" for o in out if o["zona"] == "bahia" and o["N"] == "AB_intervalos"))
    figura(out, params)
