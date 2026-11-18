#!/usr/bin/env python3
"""Comparacion del modelo con JICA 2004 (vol. V), segun docs/protocolo_jica_observaciones.md (A1 y A2). Dos partes:
 1. Salinidad en superficie con los 704 miembros (resumen.npz: mapas s2_dulce a las 16:00 UTC, dias 91-120): fraccion de miembros dentro de la
    observada +- 1 desviacion (tabla 4.19), diciembre de 2002 (referencia) y octubre (informativo). Sin veredicto (A2).
 2. (b) con los campos completos (jica_estaciones.npz de scripts/jica_extrae_estaciones.py, cluster), por miembro y fase. Veredicto con las reglas de A1
    sobre la MEDIA DE LAS DOS FASES (decision tomada antes de ver ningun valor: el rango observado [3,7; 5,5] abarca las dos fases); cada fase se
    informa aparte con la misma regla. Posicion principal = nodo mas cercano; si la media de nodos a <= 300 m da otro veredicto, el veredicto es «parcial».
Escribe resultados/jica_comparacion.txt, resultados/jica_sal_superficie_704.csv y docs/figuras/articulo/fig_jica_comparison.{png,pdf}.
  python scripts/jica_compara_modelo.py [carpetas de miembros con jica_estaciones.npz]     python scripts/jica_compara_modelo.py --prueba"""
import csv, json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from jica_extrae_estaciones import fases                         # noqa: E402
S_MAR, R_SENS, N_MIN_MAPAS, N_MIN_FASE = 36.0, 300.0, 3, 8


def observado():
    """Valores de la tabla 4.19 (CSV transcrito): {(mes, fase, nivel): (media, sd)}."""
    f = list(csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_vol5.csv"))); o = {}
    for r in f:
        if r["tabla"] == "4.19" and r["variable"] in ("salinidad_media", "salinidad_sd"):
            k = (r["mes"], r["fase"], r["nivel_m"]); m, s = o.get(k, (None, None))
            o[k] = (float(r["valor"]), s) if r["variable"] == "salinidad_media" else (m, float(r["valor"]))
    return o


def rango_b(o, mes="2002-12"):
    """Rango observado de dS = S(10 m) - S(superficie): por fase, la banda dS +- sqrt(sd_sup^2 + sd_10^2), y [min, max] de las dos medias (A1)."""
    d = {fa: (o[(mes, fa, "10")][0] - o[(mes, fa, "superficie")][0], float(np.hypot(o[(mes, fa, "10")][1], o[(mes, fa, "superficie")][1]))) for fa in ("creciente", "bajamar")}
    medias = [v[0] for v in d.values()]
    return d, (min(medias), max(medias))


def veredicto(x, lo, hi):
    """Reglas de A1 (b): confirma si el signo coincide y x esta en [lo, hi]; contradice si el signo es opuesto o |x| > 2 hi o < lo / 2; parcial en el resto."""
    if np.isnan(x): return "sin dato"
    if x <= 0 or abs(x) > 2 * hi or abs(x) < lo / 2: return "CONTRADICE"
    return "CONFIRMA" if lo <= x <= hi else "PARCIAL"


def analiza_miembro(z):
    """dS_b = S(fondo) - S(sup) medio sobre las estaciones, por fase y media de las dos, para la posicion principal (n) y la sensibilidad (r); y dS con 10 m."""
    cr, ba = fases(z["t"], z["eta_bay"]); r = {"n_creciente": int(cr.sum()), "n_bajamar": int(ba.sum())}
    for v in ("n", "r"):
        S = z[f"S_{v}"]
        for nom, (a, b) in {"b": (4, 0), "b10": (2, 0)}.items():
            d = np.nanmean(S[:, :, a] - S[:, :, b], axis=1) if not np.isnan(S[:, :, a] - S[:, :, b]).all() else np.full(len(S), np.nan)
            ph = [np.nanmean(d[m]) if m.sum() >= N_MIN_FASE and not np.isnan(d[m]).all() else np.nan for m in (cr, ba)]
            r[f"{nom}_{v}"] = dict(creciente=float(ph[0]), bajamar=float(ph[1]), media=float(np.mean(ph)))
    return r


def sal_704():
    """Salinidad en superficie con los 704 miembros. Devuelve filas (miembro, equilibrio, S_creciente_n, S_bajamar_n, S_creciente_r, S_bajamar_r)."""
    E = list(csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_estaciones_utm.csv")))
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); ge, gn = M["s2_e"], M["s2_n"]
    pos = [(float(r["E_utm17n"]), float(r["N_utm17n"])) for r in E]
    cel_n = [(np.abs(gn - n).argmin(), np.abs(ge - e).argmin()) for e, n in pos]
    cel_r = [np.where(np.hypot(ge[None, :] - e, gn[:, None] - n) <= R_SENS) for e, n in pos]
    filas = []
    for m in range(704):
        d = RAIZ / "runs" / "conjunto" / f"m{m:04d}"
        if not (d / "resumen.json").exists(): continue
        j = json.loads((d / "resumen.json").read_text())
        if j.get("nan", 1) != 0: continue
        z = np.load(d / "resumen.npz"); D = z["s2_dulce"]; q = z["Q"][np.abs(z["dias"][None, :] - z["s2_dias"][:, None]).argmin(1)]
        S = S_MAR * (1 - D)
        sn = np.nanmean(np.stack([S[:, i, k] for i, k in cel_n], 1), 1); sr = np.nanmean(np.stack([np.nanmean(S[:, ii, kk], 1) for ii, kk in cel_r], 1), 1)
        f = lambda s, mk: float(np.nanmean(s[mk])) if mk.sum() >= N_MIN_MAPAS else np.nan
        filas.append([m, abs(j["deriva_edad_bahia_d_por_d"]) <= 0.05, f(sn, q > 0), f(sn, q <= 0), f(sr, q > 0), f(sr, q <= 0)])
    return filas


def prueba():
    o = {("2002-12", "creciente", "10"): (35.9, .1), ("2002-12", "creciente", "superficie"): (32.2, 1.0), ("2002-12", "bajamar", "10"): (35.8, .1), ("2002-12", "bajamar", "superficie"): (30.3, 3.5)}
    d, (lo, hi) = rango_b(o); assert abs(lo - 3.7) < 1e-9 and abs(hi - 5.5) < 1e-9 and abs(d["bajamar"][1] - np.hypot(.1, 3.5)) < 1e-9
    assert [veredicto(x, lo, hi) for x in (4.6, 3.0, 6.0, -1, 12, 1.0, np.nan)] == ["CONFIRMA", "PARCIAL", "PARCIAL", "CONTRADICE", "CONTRADICE", "CONTRADICE", "sin dato"]
    t = np.arange(1, 31, 1 / 6); T = 12.4206012 / 24; eta = 0.3 * np.cos(2 * np.pi * t / T)
    S = np.full((len(t), 3, 5), 36.0); S[:, :, 0] = 36 - 4.0; S[:, :, 2] = 35.0                      # dS_b = 4 en todo instante; dS_10 = 3
    r = analiza_miembro(dict(t=t, eta_bay=eta, S_n=S, S_r=S + 0.5))
    assert abs(r["b_n"]["media"] - 4.0) < 1e-9 and abs(r["b10_n"]["creciente"] - 3.0) < 1e-9 and r["n_creciente"] >= 8
    print("autoprueba jica_compara_modelo: ok")


def main(miembros):
    import matplotlib
    from estilo_figuras import ANCHO2, estilo, letra, guarda, AZUL, NARANJA, GRIS, BERMELLON, NEGRO
    import matplotlib.pyplot as plt
    o = observado(); o_dic = {f: o[("2002-12", f, "superficie")] for f in ("creciente", "bajamar")}; o_oct = {f: o[("2002-10", f, "superficie")] for f in ("creciente", "bajamar")}
    L = []
    # --- 1. salinidad en superficie con los 704 miembros
    fl = sal_704(); eq = np.array([f[1] for f in fl]); A = np.array([[f[2], f[3], f[4], f[5]] for f in fl], float)
    with open(RAIZ / "resultados" / "jica_sal_superficie_704.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["miembro", "equilibrio", "S_creciente_nodo", "S_bajamar_nodo", "S_creciente_300m", "S_bajamar_300m"]); w.writerows(fl)
    L.append(f"1. Salinidad en superficie (media de las 11 estaciones; creciente = Q > 0 a las 16:00 UTC; bajamar = Q <= 0), {len(fl)} miembros validos, {int(eq.sum())} en equilibrio")
    for k, nom in enumerate(("creciente, nodo", "bajamar, nodo", "creciente, 300 m", "bajamar, 300 m")):
        fa = "creciente" if k % 2 == 0 else "bajamar"; x = A[:, k]; ok = ~np.isnan(x)
        for mes, ob in (("dic 2002", o_dic[fa]), ("oct 2002", o_oct[fa])):
            dentro = lambda mk: float(((np.abs(x - ob[0]) <= ob[1]) & ok & mk).sum() / max((ok & mk).sum(), 1))
            L.append(f"  {nom:17s} obs {mes} {ob[0]:.1f} +- {ob[1]:.1f}: modelo P5/P50/P95 {np.nanpercentile(x, 5):.1f}/{np.nanpercentile(x, 50):.1f}/{np.nanpercentile(x, 95):.1f}, "
                     f"dentro: {100 * dentro(np.ones(len(x), bool)):.0f} % de {int(ok.sum())} | en equilibrio: {100 * dentro(eq):.0f} %")
    L.append("  (abril de 2016 frente a diciembre/octubre de 2002; una sola hora del dia; sin veredicto, A2)")
    # --- 2. (b) con campos completos
    d, (lo, hi) = rango_b(o); L.append(f"2. (b) dS = S(fondo) - S(sup), observado (dic 2002, S(10 m) - S(sup)): creciente {d['creciente'][0]:+.1f} +- {d['creciente'][1]:.1f}, "
                                      f"bajamar {d['bajamar'][0]:+.1f} +- {d['bajamar'][1]:.1f}; rango [{lo:.1f}, {hi:.1f}]; contradice si el signo es opuesto, > {2 * hi:.1f} o < {lo / 2:.2f}")
    res = {}
    for dm in miembros:
        p = Path(dm) / "jica_estaciones.npz"
        if p.exists(): res[str(Path(dm))] = analiza_miembro(np.load(p))
    for g in sorted({str(Path(k).parent) for k in res}):
        ks = [k for k in res if str(Path(k).parent) == g]; L.append(f"  {g}: {len(ks)} miembros")
        for k in ks: r = res[k]; L.append(f"    {Path(k).name}: n fases {r['n_creciente']}/{r['n_bajamar']}; dS_b nodo cr {r['b_n']['creciente']:+.2f} ba {r['b_n']['bajamar']:+.2f} media {r['b_n']['media']:+.2f} | 300 m media {r['b_r']['media']:+.2f} | dS_10 nodo media {r['b10_n']['media']:+.2f}")
        for v, nom in (("n", "nodo"), ("r", "300 m")):
            med = {c: float(np.nanmedian([res[k]["b_" + v][c] for k in ks])) for c in ("creciente", "bajamar", "media")}
            L.append(f"    mediana de {len(ks)} ({nom}): cr {med['creciente']:+.2f} -> {veredicto(med['creciente'], lo, hi)}; ba {med['bajamar']:+.2f} -> {veredicto(med['bajamar'], lo, hi)}; media {med['media']:+.2f} -> {veredicto(med['media'], lo, hi)}")
        vn, vr = (veredicto(float(np.nanmedian([res[k]["b_" + v]["media"] for k in ks])), lo, hi) for v in ("n", "r"))
        L.append(f"    VEREDICTO (b) {g}: {vn if vn == vr else 'PARCIAL (nodo: ' + vn + ', 300 m: ' + vr + ')'}")
    if not res: L.append("  sin jica_estaciones.npz: falta ejecutar scripts/jica_extrae_estaciones.py en el cluster (fase A)")
    t = "\n".join(L); print(t); (RAIZ / "resultados" / "jica_comparacion.txt").write_text(t + "\n")
    # --- figura
    estilo(); fig, ax = plt.subplots(1, 3, figsize=(ANCHO2, 62 / 25.4), gridspec_kw=dict(width_ratios=[1, 1, 1.15]))
    for a, k, fa in ((ax[0], 0, "creciente"), (ax[1], 1, "bajamar")):
        x = A[:, k][~np.isnan(A[:, k])]; a.hist(x, bins=np.arange(25, 37.01, 0.25), color=GRIS, lw=0)
        a.axvspan(o_dic[fa][0] - o_dic[fa][1], o_dic[fa][0] + o_dic[fa][1], color=AZUL, alpha=.3, lw=0, label="JICA dic 2002 ± 1 sd")
        a.axvspan(o_oct[fa][0] - o_oct[fa][1], o_oct[fa][0] + o_oct[fa][1], facecolor="none", edgecolor=NARANJA, hatch="///", lw=.5, label="JICA oct 2002 ± 1 sd")
        a.set(xlim=(25, 37), xlabel="Surface salinity, mean of 11 stations", title=("Flood (Q > 0)" if fa == "creciente" else "Ebb (Q ≤ 0, low-water proxy)")); letra(a, "ab"[k])
    ax[0].set_ylabel("Ensemble members (of 704)"); ax[0].legend(loc="upper left", frameon=False, bbox_to_anchor=(0, .9))
    b = ax[2]; letra(b, "c"); b.axhspan(lo, hi, color=AZUL, alpha=.3, lw=0, label="JICA dic 2002 range")
    for i, fa in enumerate(("creciente", "bajamar")): b.errorbar([i], [d[fa][0]], yerr=[d[fa][1]], color=AZUL, marker="o", ms=3, capsize=2, lw=.8)
    colores = {"conjunto": GRIS, "termico": BERMELLON}
    for k, r in res.items():
        c = colores.get(Path(k).parent.name, NEGRO)
        b.plot([0, 1, 2], [r["b_n"]["creciente"], r["b_n"]["bajamar"], r["b_n"]["media"]], "o", color=c, ms=2.5, label=Path(k).parent.name if Path(k).name.endswith("0") else None)
    if not res: b.text(.5, .75, "model: pending\n(phase A, cluster)", transform=b.transAxes, ha="center", fontsize=6.5)
    b.set(xlim=(-.5, 2.5), ylim=(0, 10), xticks=[0, 1, 2], xticklabels=["flood", "ebb", "mean"], ylabel="ΔS: bottom − surface (model)\n≈ 10 m − surface (JICA)"); b.legend(loc="upper right", frameon=False)
    fig.subplots_adjust(left=.07, right=.99, bottom=.2, top=.9, wspace=.33); guarda(fig, "fig_jica_comparison", 190)


if __name__ == "__main__":
    prueba() if sys.argv[1:] == ["--prueba"] else main(sys.argv[1:] or [str(p) for g in ("conjunto", "termico") for p in sorted((RAIZ / "runs" / g).glob("m000[0-2]"))])
