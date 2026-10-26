#!/usr/bin/env python3
"""Analisis del conjunto de Saltelli: indices de Sobol (Jansen) con IC por bootstrap, distribucion de cada metrica
y robustez de las conclusiones cualitativas. Solo numpy + matplotlib (corre en el Mac/VM sobre los resumen.* bajados).

  python scripts/analisis_conjunto.py [runs/conjunto]   -> resultados/conjunto/{sobol.csv, metricas.csv, orden_zonas.csv,
                                                            prob_edad_sup.npz, conclusiones.csv, sobol.png}
  python scripts/analisis_conjunto.py --prueba          -> autoprueba con un conjunto sintetico de indices conocidos

Entradas: datos/conjunto/diseno.csv y <runs>/mNNNN/resumen.json (+ resumen.npz para el mapa). Los miembros que faltan
o fallaron se descartan por indice: S_i usa solo los j con A_j, B_j y AB_i_j disponibles.
Distribuciones y probabilidades: solo bloques A y B (2N muestras independientes); los AB_i entran solo en Sobol."""
import csv, json, sys, tempfile
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
DISENO = RAIZ / "datos" / "conjunto" / "diseno.csv"
SALIDA = RAIZ / "resultados" / "conjunto"
ZONAS = ["canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia"]
UMBRALES = (7.0, 14.0, 30.0)          # dias; fijados el 27-oct antes de ver el conjunto (docs/protocolo_metricas_conjunto.md)
DERIVA_MAX = 0.05                     # d/d en los ultimos 10 dias: por encima, el miembro no llego al equilibrio
NBOOT, RNG = 1000, np.random.default_rng(20261021)


def lee_diseno():
    with open(DISENO) as f: filas = list(csv.DictReader(f))
    params = [k[2:] for k in filas[0] if k.startswith("u_")]
    return filas, params


def metricas(r):
    """Escalares de resumen.json que interesan para el articulo."""
    return {k: v for k, v in r.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
            and k.startswith(("edad_media_d_", "frac_vol_", "Q_", "deriva_", "vmax_bahia", "marea_"))
            and "nodo" not in k}


def jansen(fA, fB, fABi):
    V = np.var(np.r_[fA, fB])
    return (V - 0.5 * np.mean((fB - fABi) ** 2)) / V, 0.5 * np.mean((fA - fABi) ** 2) / V


def sobol(y, bloque, j, params, N):
    """y: valor por miembro (nan = falta). Devuelve filas (param, S1, lo, hi, ST, lo, hi, n)."""
    tab = {b: np.full(N, np.nan) for b in ["A", "B"] + [f"AB{i + 1}" for i in range(len(params))]}
    for v, b, k in zip(y, bloque, j): tab[b][k] = v
    out = []
    for i, p in enumerate(params):
        fA, fB, fAB = tab["A"], tab["B"], tab[f"AB{i + 1}"]
        ok = np.isfinite(fA) & np.isfinite(fB) & np.isfinite(fAB); idx = np.where(ok)[0]
        if len(idx) < 8 or np.var(np.r_[fA[ok], fB[ok]]) == 0: out.append((p, *[np.nan] * 6, len(idx))); continue
        S, ST = jansen(fA[idx], fB[idx], fAB[idx])
        bs = np.array([jansen(fA[b], fB[b], fAB[b]) for b in (RNG.choice(idx, len(idx)) for _ in range(NBOOT))])
        lo, hi = np.nanpercentile(bs, [2.5, 97.5], axis=0)
        out.append((p, S, lo[0], hi[0], ST, lo[1], hi[1], len(idx)))
    return out


def analiza(runs, salida=SALIDA, figura=True):
    filas, params = lee_diseno(); N = sum(f["bloque"] == "A" for f in filas)
    bloque = [f["bloque"] for f in filas]; j = [int(f["j"]) for f in filas]
    res, mapas, canal_sf = [], {}, {}
    try:
        Mm = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); zona, area = Mm["zona"], Mm["area"]
    except OSError: zona = area = None
    for f in filas:
        d = runs / f"m{int(f['miembro']):04d}"
        try: r = json.loads((d / "resumen.json").read_text())
        except (OSError, ValueError): r = None
        if r and r.get("nan", 0): r = None                       # miembro inestable: fuera
        res.append(metricas(r) if r else {})
        if r and f["bloque"] in "AB" and (d / "resumen.npz").exists():
            nz = np.load(d / "resumen.npz"); mapas[int(f["miembro"])] = nz["edad_sup"]
            if zona is not None and len(nz["edad_sup"]) == len(zona):          # edad sup y fondo en el canal (zona 1)
                c = zona == 1; w = area[c]
                canal_sf[int(f["miembro"])] = ((nz["edad_sup"][c] * w).sum() / w.sum(), (nz["edad_fondo"][c] * w).sum() / w.sum())
    nombres = sorted({k for r in res for k in r})
    ok = sum(bool(r) for r in res); print(f"{ok}/{len(filas)} miembros con resumen valido; {len(nombres)} metricas")
    salida.mkdir(parents=True, exist_ok=True); AB = np.isin(bloque, ["A", "B"])
    with open(salida / "sobol.csv", "w", newline="") as fs, open(salida / "metricas.csv", "w", newline="") as fm:
        ws, wm = csv.writer(fs), csv.writer(fm)
        ws.writerow(["metrica", "parametro", "S1", "S1_lo", "S1_hi", "ST", "ST_lo", "ST_hi", "n"])
        wm.writerow(["metrica", "n", "media", "p5", "p50", "p95", "parametro_dominante", "ST_dominante"])
        S = {}
        for m in nombres:
            y = np.array([r.get(m, np.nan) for r in res], float)
            S[m] = sobol(y, bloque, j, params, N)
            for fila in S[m]: ws.writerow([m] + [f"{v:.4g}" if isinstance(v, float) else v for v in fila])
            ya = y[AB & np.isfinite(y)]
            dom = max(S[m], key=lambda q: -1 if np.isnan(q[4]) else q[4])
            wm.writerow([m, len(ya)] + [f"{v:.4g}" for v in (ya.mean(), *np.percentile(ya, [5, 50, 95]))] + [dom[0], f"{dom[4]:.3g}"]
                        if len(ya) else [m, 0] + [""] * 6)
    # robustez del orden entre zonas: fraccion de miembros (A, B) en que la zona de la fila es mas vieja que la de la columna
    E = np.array([[r.get(f"edad_media_d_{z}", np.nan) for z in ZONAS] for r, a in zip(res, AB) if a and r])
    with open(salida / "orden_zonas.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["P(fila mas vieja que columna)"] + ZONAS)
        for a, za in enumerate(ZONAS): w.writerow([za] + [f"{np.mean(E[:, a] > E[:, b]):.3f}" if len(E) else "" for b in range(len(ZONAS))])
    if mapas:
        M = np.array(list(mapas.values()))
        np.savez_compressed(salida / "prob_edad_sup.npz", n=len(M), umbrales_d=np.array(UMBRALES), p50=np.median(M, 0).astype(np.float32),
                            **{f"p_mayor_{u:g}d": (M > u).mean(0).astype(np.float32) for u in UMBRALES})
    conclusiones(res, AB, filas, canal_sf, S, salida)
    if figura: dibuja(S, params, salida)
    return S


def conclusiones(res, AB, filas, canal_sf, S, salida):
    """Conclusiones declaradas el 27-oct (docs/protocolo_metricas_conjunto.md): fraccion de miembros A y B en que se cumple
    cada una; robusta >= 90 %, fragil 10-90 %, rechazada <= 10 %. Se repite con solo los miembros en equilibrio."""
    ed = lambda r, z: r.get(f"edad_media_d_{z}", np.nan)
    C = {"C1 orden canal < cuenca < Guasabacoa < Atares": lambda r, m: ed(r, "canal") < ed(r, "cuenca") < ed(r, "Guasabacoa") < ed(r, "Atares"),
         "C2 Atares mas vieja que el canal": lambda r, m: ed(r, "Atares") > ed(r, "canal"),
         "C3 Marimelena mas vieja que la cuenca": lambda r, m: ed(r, "Marimelena") > ed(r, "cuenca"),
         "C4 Guasabacoa y Atares mas viejas que la cuenca": lambda r, m: min(ed(r, "Guasabacoa"), ed(r, "Atares")) > ed(r, "cuenca"),
         "C5 edad de la bahia < 30 d": lambda r, m: ed(r, "bahia") < 30,
         "C6 edad de la bahia < 120 d (JICA ~4 meses)": lambda r, m: ed(r, "bahia") < 120,
         "C7 canal: superficie mas vieja que el fondo (circulacion estuarina)": lambda r, m: canal_sf[m][0] > canal_sf[m][1] if m in canal_sf else np.nan}
    for u in UMBRALES:
        C[f"P edad de la bahia > {u:g} d"] = (lambda uu: lambda r, m: ed(r, "bahia") > uu)(u)
    miembros = [(r, int(f["miembro"])) for r, f, a in zip(res, filas, AB) if a and r]
    eq = [(r, m) for r, m in miembros if abs(r.get("deriva_edad_bahia_d_por_d", np.nan)) <= DERIVA_MAX]
    clase = lambda x: "" if np.isnan(x) else "robusta" if x >= 0.9 else "rechazada" if x <= 0.1 else "fragil"
    with open(salida / "conclusiones.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["conclusion", "frac_todos", "clase", "frac_en_equilibrio", "clase_eq", "n_todos", "n_eq"])
        for nom, fn in C.items():
            fr = [np.nanmean([float(fn(r, m)) for r, m in grupo]) if grupo else np.nan for grupo in (miembros, eq)]
            w.writerow([nom, f"{fr[0]:.3f}", clase(fr[0]), f"{fr[1]:.3f}", clase(fr[1]), len(miembros), len(eq)])
        m = "edad_media_d_bahia"
        if m in S:
            dom = max(S[m], key=lambda q: -1 if np.isnan(q[4]) else q[4])
            w.writerow([f"C8 parametro con mayor ST en la edad de la bahia: {dom[0]} (ST {dom[4]:.2f}, IC {dom[5]:.2f}-{dom[6]:.2f})", "", "", "", "", "", ""])
    print(f"{len(miembros)} miembros A/B, {len(eq)} en equilibrio (|deriva| <= {DERIVA_MAX} d/d) -> {salida / 'conclusiones.csv'}")


def dibuja(S, params, salida):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    ms = [m for m in (f"edad_media_d_{z}" for z in ZONAS) if m in S]
    if not ms: return
    fig, ax = plt.subplots(figsize=(8, 3.6)); w = 0.8 / len(params); x = np.arange(len(ms))
    for i, p in enumerate(params):
        st = np.array([S[m][i][4] for m in ms]); lo = np.array([S[m][i][5] for m in ms]); hi = np.array([S[m][i][6] for m in ms])
        ax.bar(x + (i - len(params) / 2 + 0.5) * w, st, w, yerr=[st - lo, hi - st], capsize=1.5, label=p)
    ax.set_xticks(x, [m.replace("edad_media_d_", "") for m in ms]); ax.set_ylabel("total Sobol index $S_T$")
    ax.set_title("Sensitivity of mean water age (last 30 days)"); ax.legend(ncol=4, frameon=False, fontsize=8)
    ax.set_ylim(0, None); fig.tight_layout(); fig.savefig(salida / "sobol.png", dpi=200); plt.close(fig)


def prueba():
    """Conjunto sintetico sobre el diseno real: edad = 20 + 4 u_alfa + 2 u_cd + 1 u_vfac (aditivo) -> S_i = ST_i =
    c_i^2 / sum c^2 = 0,762 / 0,190 / 0,048 y 0 en el resto. Se borran 10 miembros para probar los huecos."""
    filas, params = lee_diseno(); c = dict(alfa=4.0, cd=2.0, vfac=1.0)
    with tempfile.TemporaryDirectory() as tmp:
        runs = Path(tmp)
        for f in filas[10:]:
            u = {p: float(f[f"u_{p}"]) for p in params}; e = 20 + sum(c.get(p, 0) * u[p] for p in params)
            d = runs / f"m{int(f['miembro']):04d}"; d.mkdir()
            (d / "resumen.json").write_text(json.dumps({"nan": 0, "deriva_edad_bahia_d_por_d": 0.01 if int(f["miembro"]) % 2 else 0.2,
                                                        **{f"edad_media_d_{z}": e * (1 + k / 10) for k, z in enumerate(ZONAS)}}))
            np.savez(d / "resumen.npz", edad_sup=np.full(4832, e + 9), edad_fondo=np.full(4832, e + 8))
        S = analiza(runs, Path(tmp) / "salida", figura=False)
        exacto = {p: c.get(p, 0) ** 2 / 21 for p in params}
        for p, S1, _, _, ST, lo, hi, n in S["edad_media_d_bahia"]:
            # con N = 64 el error de Jansen es de ~0,1 en ST y ~0,2 en S1: se comprueba que el IC lo cubre, no un margen fijo
            assert abs(ST - exacto[p]) < 0.15 and abs(S1 - exacto[p]) < 0.3, (p, S1, ST, exacto[p])
            assert lo - 0.02 <= exacto[p] <= hi + 0.02, (p, lo, hi, exacto[p])
        o = list(csv.reader(open(Path(tmp) / "salida" / "orden_zonas.csv")))
        assert o[6][1] == "1.000" and o[1][6] == "0.000", o          # bahia (x1,5) siempre mas vieja que canal
        p = np.load(Path(tmp) / "salida" / "prob_edad_sup.npz")["p_mayor_30d"]; assert 0 < p[0] < 1
        cc = {r[0]: r for r in csv.reader(open(Path(tmp) / "salida" / "conclusiones.csv"))}
        assert cc["C2 Atares mas vieja que el canal"][2] == "robusta", cc
        assert cc["C7 canal: superficie mas vieja que el fondo (circulacion estuarina)"][1] == "1.000", cc
        k1 = cc["C1 orden canal < cuenca < Guasabacoa < Atares"]
        assert cc["C5 edad de la bahia < 30 d"][2] == "rechazada" and 0 < int(k1[6]) < int(k1[5]), cc
    print("autoprueba Sobol/Jansen sobre el diseno real con huecos: ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--prueba"]: prueba()
    else: analiza(RAIZ / (sys.argv[1] if len(sys.argv) > 1 else "runs/conjunto"))
