#!/usr/bin/env python3
"""Cuatro analisis de docs/protocolo_analisis_x.md (lecturas fijadas el 19-nov-2026 ANTES de calcular nada).
  python scripts/analisis_x.py dst | bajoaporte | convergencia | mapa | perfil | todo     -> resultados/analisis_x_*.txt y figuras en docs/figuras/articulo/
  python scripts/analisis_x.py --prueba"""
import csv, json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from conjunto_calor import spearman, rangos            # noqa: E402
from mecanismo_calor import MES                        # noqa: E402
from termico import unesco                             # noqa: E402
from analisis_conjunto import lee_diseno               # noqa: E402

SEED, NB = 20261119, 1000
CUM = np.concatenate([[0], np.cumsum(MES)]); RES = RAIZ / "resultados"
ZONAS = ("canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia")
RHO_CRIT, T_CRIB, UMB_IND, UMB_RANK, UMB_SCR = 0.59, 0.05, 0.05, 1.0, 0.05
Q_RIOS_TOTAL = (114860 + 62105 + 8004) / 86400         # m3/s, suma de Q_RIOS de caso_real.py (qfac = 1)
VENTANA, TOL_PERFIL = 30.0, 1.0


def escribe(nombre, lineas):
    t = "\n".join(lineas); print(t); (RES / nombre).write_text(t + "\n")


def lee_miembro(carpeta, m):
    d = RAIZ / "runs" / carpeta / f"m{m:04d}"
    try: j = json.loads((d / "resumen.json").read_text())
    except (OSError, ValueError): return None, d
    return (j if not j.get("nan", 1) else None), d


# ---------------------------------------------------------------- 1. diagrama dS-dT
def crecimiento_mensual(diaria):
    """G_m = (media de los 5 ultimos dias del mes m - la del mes m-1) / dias del mes, m = febrero..diciembre (enero se descarta)."""
    fin = np.array([np.mean(diaria[CUM[m + 1] - 5:CUM[m + 1]]) for m in range(12)])
    return np.array([(fin[m] - fin[m - 1]) / MES[m] for m in range(1, 12)])


def lectura_dst(drho, G):
    """Una corrida: rho de Spearman (Drho_m, G_m) con los 11 meses, y G medio en meses con Drho > 0 (hipotermicos) y en los demas."""
    hip = np.asarray(drho) > 0; ev = hip.sum() >= 2 and (~hip).sum() >= 2
    return dict(evaluable=bool(ev), rho=spearman(drho, G), m_hip=float(np.mean(G[hip])) if hip.any() else np.nan,
                m_otros=float(np.mean(G[~hip])) if (~hip).any() else np.nan, n_hip=int(hip.sum()))


def veredicto_dst(r1, r2):
    if not (r1["evaluable"] and r2["evaluable"]): return "INCONCLUSO (todos los meses de una corrida tienen el mismo signo de Drho)"
    rs = (r1, r2)
    if any(r["rho"] <= -RHO_CRIT for r in rs) or all(r["m_hip"] < r["m_otros"] and r["rho"] < 0 for r in rs): return "CONTRADICE"
    if all(r["rho"] >= RHO_CRIT and r["m_hip"] > r["m_otros"] for r in rs): return "CONFIRMA"
    return "INCONCLUSO"


def mensual(csv_path, borde_T):
    """Medias mensuales de S_z, T_z y Drho = rho(T, S) - rho(T_b, 36) a partir de delta_st_diario.csv. borde_T: serie diaria (365) de T del borde."""
    f = list(csv.DictReader(open(csv_path))); dia = np.array([int(r["dia"]) for r in f]); out = {}
    for z in ("bahia", "canal", "cuenca", "Marimelena", "Guasabacoa", "Atares"):
        for a in ("S", "T"):
            x = np.array([float(r[f"{a}_{z}"]) for r in f]); out[f"{a}_{z}"] = np.array([np.nanmean(x[(dia >= CUM[m]) & (dia < CUM[m + 1])]) for m in range(12)])
    Tb = np.array([np.mean(borde_T[CUM[m]:CUM[m + 1]]) for m in range(12)]); out["Tb"] = Tb
    for z in ("bahia", "canal", "cuenca", "Marimelena", "Guasabacoa", "Atares"):
        out[f"dS_{z}"] = out[f"S_{z}"] - 36.0; out[f"dT_{z}"] = out[f"T_{z}"] - Tb
        out[f"drho_{z}"] = unesco(out[f"T_{z}"], out[f"S_{z}"]) - unesco(Tb, 36.0)
    return out


def dst():
    corridas = [("sin calor (m0000)", "m0000", RAIZ / "runs" / "robustez_largo" / "m0000", None), ("calor, borde a 28 C (m0001)", "m0001", RAIZ / "runs" / "borde28" / "m0000", None),
                ("calor + OISST (m0005)", "m0005", RAIZ / "runs" / "termico" / "m0000", "oisst")]
    sst = {r["fecha"]: float(r["sst_C"]) for r in csv.DictReader(open(RAIZ / "datos" / "forzamiento" / "sst" / "oisst_habana.csv"))}
    oisst = np.array([sst[str(np.datetime64("2016-01-01") + int(d))] for d in range(365)])
    L = ["Diagrama dS-dT (protocolo_analisis_x.md, 1). Crecimiento mensual de la edad de la bahia G_m (d/d), feb-dic de 2016, de runs/robustez_largo:"]
    G, datos = {}, {}
    for nom, m, ruta, borde in corridas:
        s = np.load(RAIZ / "runs" / "robustez_largo" / m / "resumen.npz")["serie_bahia"]; dia = s[:365 * 6].reshape(365, 6).mean(1); G[nom] = crecimiento_mensual(dia)
        L.append(f"  {nom:30s} " + " ".join(f"{g:+.3f}" for g in G[nom]))
        c = ruta / "delta_st_diario.csv"; datos[nom] = mensual(c, oisst if borde else np.full(365, 28.0)) if c.exists() else None
        if datos[nom] is not None and not np.isfinite(datos[nom]["T_bahia"]).all():     # sin calor: T = 28 por construccion (supuesto del protocolo)
            if m == "m0000": datos[nom] = mensual_t28(c)
    falta = [n for n, d in datos.items() if d is None and "calor" in n and not n.startswith("sin ")]    # el control sin calor se informa y no entra en el veredicto (protocolo 1): su falta no impide la lectura
    if falta:
        L += ["T y S medias mensuales NO disponibles para: " + "; ".join(falta) + ". No se aplica la lectura (INCONCLUSO por falta de datos, no por resultado).",
              "Que hay que repetir/reducir: (1) m0001 (calor, borde 28 C) con TERMICO=1, 365 d, ~133 h-nucleo medidas en runs/robustez_largo/coste.txt (python scripts/conjunto.py deltast); "
              "(2) python scripts/delta_st.py reduce <carpeta> en el cluster para runs/robustez_largo/m0000, runs/borde28/m0000 y runs/termico/m0000 (= m0005 repetido con salidas)."]
    else:
        r = {n: lectura_dst(datos[n]["drho_bahia"][1:], G[n]) for n in G if datos[n] is not None}
        L += [f"  (sin T ni S medias para el control: {n}; se informa solo su crecimiento de edad)" for n, d in datos.items() if d is None]
        for n, x in r.items(): L.append(f"  {n:30s} rho(Drho, G) = {x['rho']:+.2f}; G en meses hipotermicos {x['m_hip']:+.3f} (n {x['n_hip']}) frente a {x['m_otros']:+.3f} en los demas")
        L.append("VEREDICTO (solo las dos corridas con calor): " + veredicto_dst(r["calor, borde a 28 C (m0001)"], r["calor + OISST (m0005)"]))
    escribe("analisis_x_dst.txt", L); return G, datos


def mensual_t28(c):
    f = list(csv.DictReader(open(c)))
    for r in f:
        for z in ("bahia", "canal", "cuenca", "Marimelena", "Guasabacoa", "Atares"): r[f"T_{z}"] = 28.0
    import tempfile, os
    p = Path(tempfile.mkdtemp()) / "x.csv"
    with open(p, "w", newline="") as fh: w = csv.DictWriter(fh, f[0].keys()); w.writeheader(); w.writerows(f)
    return mensual(p, np.full(365, 28.0))


# ---------------------------------------------------------------- 2. indice de bajo aporte
def u_t_de_Q(q, A):
    """Sustituto de la velocidad cuadratica media de marea en el canal: rms(Q - media)/A (canal_un no existe, protocolo 2)."""
    q = np.asarray(q, float); return float(np.std(q) / A)


def area_canal():
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); L = (RAIZ / "datos" / "malla" / "hgrid.gr3").read_text().split("\n"); nn = int(L[1].split()[1])
    h = np.array([float(l.split()[3]) for l in L[2:2 + nn]]); dn = float(M["sec_dn"]); return float((h[M["sec_i"]] * M["sec_w"]).sum(1).sum() * dn), len(M["sec_i"]) * dn


def ic_diferencia(x_i, x_q, y, rng, n=2000):
    """D = |rho(I, y)| - |rho(qfac, y)| con IC95% por bootstrap emparejado."""
    n_ = len(y); f = lambda ii: abs(spearman(x_i[ii], y[ii])) - abs(spearman(x_q[ii], y[ii])); D = f(np.arange(n_))
    bs = np.array([f(rng.integers(0, n_, n_)) for _ in range(n)]); lo, hi = np.percentile(bs, [2.5, 97.5]); return D, lo, hi


def lectura_D(lo, hi): return "I mejora a qfac" if lo > 0 else "I es peor" if hi < 0 else "no mejora"


def bajoaporte():
    A, W = area_canal(); filas, params = lee_diseno(); rng = np.random.default_rng(SEED); reg = []
    for f in filas:
        m = int(f["miembro"]); j, d = lee_miembro("conjunto", m)
        if j is None or not (d / "resumen.npz").exists(): continue
        z = np.load(d / "resumen.npz"); q = z["Q"][z["dias"] > z["dias"][-1] - VENTANA]; ut = u_t_de_Q(q, A); qr = Q_RIOS_TOTAL * float(f["qfac"])
        reg.append((m, float(f["qfac"]), qr / (W * ut ** 3), ut, j["edad_media_d_bahia"], abs(j["deriva_edad_bahia_d_por_d"]) <= 0.05))
    R = np.array(reg, float); L = [f"Indice de bajo aporte I = Qr / (W u_t^3) (EXPLORATORIO). W = {W:.0f} m, A = {A:.0f} m2, u_t = rms(Q - media)/A en los ultimos {VENTANA:.0f} d (sustituto de canal_un). {len(R)} miembros validos.",
                                    f"  u_t: mediana {np.median(R[:, 3]):.3f} m/s (P5-P95 {np.percentile(R[:, 3], 5):.3f}-{np.percentile(R[:, 3], 95):.3f}); I: P5-P95 {np.percentile(R[:, 2], 5):.3g}-{np.percentile(R[:, 2], 95):.3g}"]
    res = {}
    for nom, sel in (("todos los validos", np.ones(len(R), bool)), ("solo en equilibrio", R[:, 5] > 0)):
        r = R[sel]; D, lo, hi = ic_diferencia(r[:, 2], r[:, 1], r[:, 4], rng)
        L.append(f"  edad media de la bahia, {nom} (n {len(r)}): rho(I) {spearman(r[:, 2], r[:, 4]):+.3f}, rho(qfac) {spearman(r[:, 1], r[:, 4]):+.3f}; D = {D:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {lectura_D(lo, hi)}"); res[nom] = (D, lo, hi)
    par = []                                                                         # desplazamiento por calor, 64 pares
    for f in filas:
        m = int(f["miembro"])
        if m >= 64: continue
        a, _ = lee_miembro("conjunto", m); b, _ = lee_miembro("conjunto_calor", m)
        if a is None or b is None: continue
        i = np.where(R[:, 0] == m)[0]
        if len(i): par.append((R[i[0], 2], R[i[0], 1], b["edad_media_d_bahia"] - a["edad_media_d_bahia"], b["edad_media_d_bahia"] / a["edad_media_d_bahia"]))
    P = np.array(par, float); L.append(f"Desplazamiento por calor + OISST (n {len(P)} pares, conjunto_calor frente a conjunto, miembros 0-63):")
    for k, nom in ((2, "en dias (calor - sin)"), (3, "en cociente (calor / sin)")):
        D, lo, hi = ic_diferencia(P[:, 0], P[:, 1], P[:, k], rng); L.append(f"  {nom}: rho(I) {spearman(P[:, 0], P[:, k]):+.3f}, rho(qfac) {spearman(P[:, 1], P[:, k]):+.3f}; D = {D:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {lectura_D(lo, hi)}")
    escribe("analisis_x_bajoaporte.txt", L); np.save(RES / "analisis_x_bajoaporte.npy", R); return R, P


# ---------------------------------------------------------------- 3. convergencia de Sarrazin et al. (2016)
def stat_rank_de_S(S):
    """S (d, B): indices por remuestreo. Eq. 2-3: cuantil 0,95 de r_jk = sum_i |R_j,i - R_k,i| max(S_j,i, S_k,i)^2 / sum_i max(...)^2 sobre los pares j < k."""
    R = (-S).argsort(0).argsort(0) + 1; vals = []
    for j in range(S.shape[1] - 1):
        w = np.maximum(S[:, j:j + 1], S[:, j + 1:]) ** 2; num = (np.abs(R[:, j:j + 1] - R[:, j + 1:]) * w).sum(0); den = w.sum(0)
        vals.append(np.where(den > 0, num / np.where(den > 0, den, 1), 0.0))
    return float(np.quantile(np.concatenate(vals), 0.95))


def estadisticos(fA, fB, fAB, rng, B=NB):
    """fA, fB (n,), fAB (d, n), filas completas. Devuelve (Stat_ind, Stat_rank, Stat_scr, n_X0, S medio, S_inf, S_sup)."""
    n = len(fA); ii = rng.integers(0, n, (B, n)); a, b = fA[ii], fB[ii]; ab = fAB[:, ii]
    V = np.var(np.concatenate([a, b], 1), axis=1); S = 0.5 * np.mean((a[None] - ab) ** 2, axis=2) / V[None]
    lo, hi = np.percentile(S, [2.5, 97.5], axis=1); m = S.mean(1); x0 = m < T_CRIB
    return float((hi - lo).max()), stat_rank_de_S(S), float((hi - lo)[x0].max()) if x0.any() else np.nan, int(x0.sum()), m, lo, hi


def tabla_sobol(y, bloque, j, d, N):
    """Arrays por bloque con las filas j < N; devuelve fA, fB, fAB (d, N) y la mascara de filas completas."""
    t = {b: np.full(N, np.nan) for b in ["A", "B"] + [f"AB{i + 1}" for i in range(d)]}
    for v, b, k in zip(y, bloque, j):
        if k < N: t[b][k] = v
    fAB = np.stack([t[f"AB{i + 1}"] for i in range(d)]); ok = np.isfinite(t["A"]) & np.isfinite(t["B"]) & np.isfinite(fAB).all(0)
    return t["A"], t["B"], fAB, ok


def primer_N(vals, ns, ok_fn):
    """Menor N con la condicion en N y en todos los mayores (None si ni el mayor la cumple)."""
    for i in range(len(ns)):
        if all(ok_fn(v) for v in vals[i:]): return ns[i]
    return None


def convergencia():
    filas, params = lee_diseno(); d = len(params); bloque = [f["bloque"] for f in filas]; jj = [int(f["j"]) for f in filas]; ns = (16, 32, 48, 64); rng = np.random.default_rng(SEED)
    res = {z: [lee_miembro("conjunto", int(f["miembro"]))[0] for f in filas] for z in ("_",)}["_"]
    L = ["Convergencia de S_T (Sarrazin et al. 2016; protocolo_analisis_x.md, 3): 1000 remuestreos, IC95 %, T = 0,05. Edad media por zona, N = filas j < N de cada bloque.", ""]
    filas_csv, resumen = [], {}
    for z in ZONAS:
        y = np.array([r[f"edad_media_d_{z}"] if r else np.nan for r in res], float); st = []
        for N in ns:
            fA, fB, fAB, ok = tabla_sobol(y, bloque, jj, d, N); e = estadisticos(fA[ok], fB[ok], fAB[:, ok], rng); st.append(e)
            filas_csv.append([z, N, int(ok.sum()), e[0], e[1], e[2], e[3]] + [float(v) for v in e[4]])
        resumen[z] = (st, [primer_N([s[k] for s in st], ns, f) for k, f in ((0, lambda v: v < UMB_IND), (1, lambda v: v < UMB_RANK), (2, lambda v: np.isfinite(v) and v < UMB_SCR))])
        L.append(f"{z}:")
        for N, e in zip(ns, st):
            ord_ = ", ".join(f"{params[i]} {e[4][i]:.2f}" for i in np.argsort(-e[4])[:3])
            L.append(f"  N = {N:2d}: Stat_ind {e[0]:.3f} {'(<0,05)' if e[0] < UMB_IND else '(no)'}; Stat_rank {e[1]:.2f} {'(<1)' if e[1] < UMB_RANK else '(no)'}; "
                     f"Stat_scr {e[2]:.3f} (X0 = {e[3]} factores) ; S_T mayores: {ord_}")
        pn = resumen[z][1]; L.append(f"  -> converge con N = indices {pn[0]}, orden {pn[1]}, cribado {pn[2]} (None = no converge ni con 64)")
    with open(RES / "analisis_x_convergencia.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["zona", "N", "n_filas", "Stat_ind", "Stat_rank", "Stat_scr", "n_X0"] + [f"ST_{p}" for p in params]); w.writerows(filas_csv)
    escribe("analisis_x_convergencia.txt", L); return resumen, params, ns


# ---------------------------------------------------------------- 4. mapa de S_T por nodo y perfil del canal
def st_nodos(Y, valido, bloque, j, d, N=64):
    """Jansen S_T por nodo. Y (n_miembros, nn); valido: miembros con resumen sin NaN. Devuelve (d, nn)."""
    t = {b: np.full((N, Y.shape[1]), np.nan) for b in ["A", "B"] + [f"AB{i + 1}" for i in range(d)]}
    for y, v, b, k in zip(Y, valido, bloque, j):
        if v and k < N: t[b][k] = y
    out = np.full((d, Y.shape[1]), np.nan)
    for i in range(d):
        fA, fB, fAB = t["A"], t["B"], t[f"AB{i + 1}"]; ok = np.isfinite(fA[:, 0]) & np.isfinite(fB[:, 0]) & np.isfinite(fAB[:, 0])
        V = np.var(np.concatenate([fA[ok], fB[ok]]), axis=0); out[i] = 0.5 * np.mean((fA[ok] - fAB[ok]) ** 2, axis=0) / np.where(V > 0, V, np.nan)
    return out


def mapa():
    filas, params = lee_diseno(); d = len(params); bloque = [f["bloque"] for f in filas]; jj = [int(f["j"]) for f in filas]
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); zona, area = M["zona"], M["area"]; nn = len(zona); Y, val, edad_bahia = {}, [], []
    for c in ("edad_sup", "edad_fondo"): Y[c] = np.full((len(filas), nn), np.nan)
    for k, f in enumerate(filas):
        j, dd = lee_miembro("conjunto", int(f["miembro"])); ok = j is not None and (dd / "resumen.npz").exists(); val.append(ok); edad_bahia.append(j["edad_media_d_bahia"] if ok else np.nan)
        if ok:
            z = np.load(dd / "resumen.npz")
            for c in Y: Y[c][k] = z[c]
    val = np.array(val); eb = np.array(edad_bahia, float)
    fA, fB, fAB, ok = tabla_sobol(eb, bloque, jj, d, 64); V = np.var(np.concatenate([fA[ok], fB[ok]])); st_bahia = 0.5 * np.mean((fA[ok] - fAB[:, ok]) ** 2, axis=1) / V
    top3 = [params[i] for i in np.argsort(-st_bahia)[:3]]
    L = [f"Mapa de S_T por nodo (Jansen, N = 64, {int(val.sum())} miembros validos). S_T de la edad media de la bahia, N = 64 (punto, sin IC): " + ", ".join(f"{p} {s:.2f}" for p, s in sorted(zip(params, st_bahia), key=lambda t: -t[1])),
         "Tres parametros dibujados (regla fijada): " + ", ".join(top3)]
    ST = {c: st_nodos(Y[c], val, bloque, jj, d) for c in Y}; bahia = zona > 0
    for c in ST:
        for zi, zn in enumerate(("canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia")):
            m = (zona == zi + 1) if zn != "bahia" else bahia; w = area[m]; mm = ST[c][:, m]
            ponderada = np.array([np.nansum(mm[i] * w) / w[np.isfinite(mm[i])].sum() for i in range(d)])
            L.append(f"  {c:10s} {zn:10s} S_T medio ponderado por area: " + ", ".join(f"{p} {s:.2f}" for p, s in zip(params, ponderada)) + f"  | dominante: {params[int(np.nanargmax(ponderada))]}")
    np.savez_compressed(RES / "conjunto" / "st_nodos.npz", params=np.array(params), edad_sup=ST["edad_sup"], edad_fondo=ST["edad_fondo"], zona=zona)
    escribe("analisis_x_mapa.txt", L); return ST, params, top3


def dentro(x, obs, tol=TOL_PERFIL): return abs(x - obs) <= tol


def perfil():
    """Salinidad del canal en superficie, nivel medio y fondo (jica_estaciones.npz, miembros 0-2) frente a la tabla 4.11 de JICA."""
    from jica_extrae_estaciones import fases
    T = [r for r in csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_vol5.csv")) if r["tabla"] == "4.11" and r["estacion"] == "Canal de Entrada" and r["variable"] == "salinidad"]
    nivel = {"surface": 0, "middle": 3, "bottom": 4}; obs = {(r["nivel_m"], r["fase"], r["mes"]): float(r["valor"]) for r in T}
    L = ["Perfil del canal frente a JICA, tabla 4.11 (Canal de Entrada; junio y noviembre de 2001). Modelo: media de los nodos de zona 1, dias 91-120, niveles sup / mid / fondo.", f"Dentro = |modelo - observado| <= {TOL_PERFIL:g}."]
    tot = n = 0; M = {}
    for m in range(3):
        z = np.load(RES / "jica_estaciones_modelo" / f"conjunto_m{m:04d}_dias91-120.npz"); cr, ba = fases(z["t"], z["eta_bay"]); S = z["canal_S"]
        mod = {(lv, ph): float(np.nanmean(S[mk, k])) for lv, k in nivel.items() for ph, mk in (("creciente", cr), ("bajamar", ba))}; M[m] = mod; hecho = 0
        for lv in nivel:
            for (l2, fa, mes), v in obs.items():
                if l2 != lv: continue
                x = (mod[(lv, "creciente")] + mod[(lv, "bajamar")]) / 2 if fa == "otra" else mod[(lv, fa)]; hecho += dentro(x, v); n += 1
        tot += hecho; L.append(f"  m000{m}: " + "; ".join(f"{lv} cre {mod[(lv, 'creciente')]:.2f} baj {mod[(lv, 'bajamar')]:.2f}" for lv in nivel) + f" | dentro {hecho}/9")
        L.append(f"          fondo - superficie: modelo {np.mean([mod[('bottom', p)] - mod[('surface', p)] for p in ('creciente', 'bajamar')]):+.2f}")
    L.append("  observado (nov. 2001, pleamar / bajamar; jun. 2001): " + "; ".join(f"{lv} {obs[(lv, 'creciente', '2001-11')]:.2f} / {obs[(lv, 'bajamar', '2001-11')]:.2f}; {obs[(lv, 'otra', '2001-06')]:.2f}" for lv in nivel))
    L.append(f"  fondo - superficie observado: pleamar {obs[('bottom', 'creciente', '2001-11')] - obs[('surface', 'creciente', '2001-11')]:+.2f}, bajamar {obs[('bottom', 'bajamar', '2001-11')] - obs[('surface', 'bajamar', '2001-11')]:+.2f}, junio {obs[('bottom', 'otra', '2001-06')] - obs[('surface', 'otra', '2001-06')]:+.2f}")
    L.append(f"  TOTAL dentro {tot}/{n} (3 miembros x 3 niveles x 3 observaciones)"); L.append("  Velocidad por nivel (estacion 1): NO evaluable, falta la velocidad 3D (runs/salinidad). GEF: no se usa (sin fuente publica).")
    escribe("analisis_x_perfil.txt", L); return M, obs


# ---------------------------------------------------------------- figuras
def figuras(G, datos, R, P, conv, mapas, perf):
    sys.path.insert(0, str(RAIZ / "scripts"))
    from estilo_figuras import MM, ANCHO2, AZUL, BERMELLON, VERDE, NARANJA, CELESTE, ROSA, GRIS, NEGRO, AMARILLO, estilo, letra, guarda, plt
    from figuras_resultados import PARAM
    from matplotlib.tri import Triangulation
    estilo(); col = [GRIS, AMARILLO, VERDE, CELESTE, ROSA, NARANJA, AZUL, NEGRO, BERMELLON]
    # edad mensual; con T y S medias disponibles, tambien el diagrama dS-dT (fig_dst_diagram). Sin ellas solo se dibuja la edad: fig_age_growth_monthly
    en = {"sin calor (m0000)": "No heat (m0000)", "calor, borde a 28 C (m0001)": "Heat, boundary 28 \u00b0C (m0001)", "calor + OISST (m0005)": "Heat + OISST (m0005)"}
    hay = all(dd is not None for dd in datos.values()); meses = np.arange(2, 13); colores = dict(zip(G, (GRIS, AZUL, BERMELLON)))
    fig, axs = plt.subplots(1, 2 if hay else 1, figsize=(ANCHO2 if hay else 90 * MM, 75 * MM), constrained_layout=True); axs = np.atleast_1d(axs); axb = axs[-1]
    for nom, g in G.items(): axb.plot(meses, g, marker="o", ms=2.5, color=colores[nom], label=en[nom])
    axb.axhline(0, color=NEGRO, lw=0.4); axb.set_xlabel("Month of 2016"); axb.set_ylabel("Bay-mean age growth $G_m$ (d d$^{-1}$)"); axb.set_xticks(meses); axb.legend(frameon=False, fontsize=5.5, loc="lower left")
    if hay:
        x = np.linspace(-6, 0.5, 60); y = np.linspace(-4, 4, 60); XX, YY = np.meshgrid(x, y)
        axs[0].contour(XX, YY, unesco(27.5 + YY, 36 + XX) - unesco(27.5, 36), levels=np.arange(-5, 6, 1), colors=GRIS, linewidths=0.4)
        for nom, dd in datos.items(): axs[0].scatter(dd["dS_bahia"], dd["dT_bahia"], s=8, color=colores[nom], label=en[nom], zorder=3)
        axs[0].set_xlabel(r"$\Delta S$ (bay \u2212 boundary)"); axs[0].set_ylabel(r"$\Delta T$ (K)"); axs[0].legend(frameon=False, fontsize=5.5); letra(axs[0], "a"); letra(axb, "b")
    guarda(fig, "fig_dst_diagram" if hay else "fig_age_growth_monthly", 190 if hay else 90)
    # indice de bajo aporte
    fig, axs = plt.subplots(2, 2, figsize=(ANCHO2, 100 * MM), constrained_layout=True)
    for (ax, x, y, xl, yl) in ((axs[0, 0], R[:, 1], R[:, 4], "River discharge factor", "Bay-mean age (d)"), (axs[0, 1], R[:, 2], R[:, 4], r"Low-inflow index $Q_r/(W u_t^3)$", "Bay-mean age (d)"),
                              (axs[1, 0], P[:, 1], P[:, 2], "River discharge factor", "Heat displacement (d)"), (axs[1, 1], P[:, 0], P[:, 2], r"Low-inflow index $Q_r/(W u_t^3)$", "Heat displacement (d)")):
        ax.plot(x, y, ".", ms=2, color=AZUL); ax.set_xscale("log"); ax.set_xlabel(xl); ax.set_ylabel(yl); ax.text(0.97, 0.95, rf"$\rho_s$ = {spearman(x, y):+.2f}", transform=ax.transAxes, ha="right", va="top")
    for ax, s in zip(axs.flat, "abcd"): letra(ax, s)
    guarda(fig, "fig_low_inflow_index", 190)
    # convergencia
    resumen, params, ns = conv; fig, axs = plt.subplots(1, 3, figsize=(ANCHO2, 65 * MM), constrained_layout=True)
    for k, (tit, umb) in enumerate((("Index width, max CI95 (S_T)", UMB_IND), ("Ranking statistic (Eq. 3)", UMB_RANK), ("Screening width (S_T < 0.05)", UMB_SCR))):
        for z, c in zip(ZONAS, (GRIS, VERDE, CELESTE, ROSA, NARANJA, BERMELLON)):
            axs[k].plot(ns, [s[k] for s in resumen[z][0]], marker="o", ms=2.5, color=c, lw=1.2 if z == "bahia" else 0.6, label="bay" if z == "bahia" else z)
        axs[k].axhline(umb, color=NEGRO, ls="--", lw=0.6); axs[k].set_xticks(ns); axs[k].set_xlabel("Base sample size $N$"); axs[k].set_ylabel(tit); letra(axs[k], "abc"[k])
    axs[0].legend(frameon=False, fontsize=5.5, loc="upper right"); guarda(fig, "fig_sobol_convergence_stats", 190)
    # mapa de S_T
    ST, params2, top3 = mapas; Mm = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); zona = Mm["zona"]; Lh = (RAIZ / "datos" / "malla" / "hgrid.gr3").read_text().split("\n"); ne, nn = map(int, Lh[1].split()[:2])
    xy = np.array([l.split()[1:3] for l in Lh[2:2 + nn]], float); tri = np.array([l.split()[2:5] for l in Lh[2 + nn:2 + nn + ne]], int) - 1
    mask = ~(zona[tri] > 0).all(1); tr = Triangulation(xy[:, 0], xy[:, 1], tri, mask=mask); b = zona > 0
    fig, axs = plt.subplots(2, 4, figsize=(ANCHO2, 100 * MM), constrained_layout=True); idx = {p: i for i, p in enumerate(params2)}
    for r, c in enumerate(("edad_sup", "edad_fondo")):
        for k, p in enumerate(top3):
            im = axs[r, k].tripcolor(tr, np.where(b, ST[c][idx[p]], np.nan), vmin=0, vmax=1, cmap="viridis", shading="gouraud"); axs[r, k].set_title(PARAM.get(p, p), fontsize=6.5)
        mx = np.nanmax(ST[c], axis=0); dom = np.where(b & (mx >= T_CRIB), np.nanargmax(np.nan_to_num(ST[c], nan=-1), axis=0), np.nan)
        from matplotlib.colors import ListedColormap
        axs[r, 3].tripcolor(tr, dom, vmin=-0.5, vmax=len(params2) - 0.5, cmap=ListedColormap(col), shading="flat" if False else "gouraud"); axs[r, 3].set_title("Dominant ($S_T \\geq 0.05$)", fontsize=6.5)
        for ax in axs[r]: ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlim(xy[b, 0].min(), xy[b, 0].max()); ax.set_ylim(xy[b, 1].min(), xy[b, 1].max())
        axs[r, 0].set_ylabel("Surface age" if c == "edad_sup" else "Bottom age")
    from matplotlib.patches import Patch
    presentes = sorted({int(v) for c in ST for v in np.unique(np.where(b & (np.nanmax(ST[c], axis=0) >= T_CRIB), np.nanargmax(np.nan_to_num(ST[c], nan=-1), axis=0), -1)) if v >= 0})
    fig.legend([Patch(color=col[i]) for i in presentes], [PARAM.get(params2[i], params2[i]) for i in presentes], loc="outside lower center", ncol=len(presentes), frameon=False, fontsize=5.5, title="Dominant parameter", title_fontsize=5.5)
    fig.colorbar(im, ax=axs[:, :3], shrink=0.6, label="$S_T$"); guarda(fig, "fig_st_map", 190)
    # perfil del canal
    M, obs = perf; fig, ax = plt.subplots(figsize=(90 * MM, 70 * MM), constrained_layout=True); yy = {"surface": 0, "middle": 1, "bottom": 2}
    for m, c in zip(M, (AZUL, VERDE, NARANJA)):
        for ph, mk in (("creciente", "o"), ("bajamar", "s")): ax.plot([M[m][(lv, ph)] for lv in yy], list(yy.values()), marker=mk, ms=3, color=c, lw=0.6, label=f"m000{m} {'flood' if ph == 'creciente' else 'ebb'}")
    for (fa, mes), mk in ((("creciente", "2001-11"), "^"), (("bajamar", "2001-11"), "v"), (("otra", "2001-06"), "D")):
        ax.plot([obs[(lv, fa, mes)] for lv in yy], list(yy.values()), marker=mk, ms=4, color=NEGRO, lw=0, label={"creciente": "JICA Nov 2001 high", "bajamar": "JICA Nov 2001 low", "otra": "JICA Jun 2001"}[fa])
    ax.set_yticks([0, 1, 2], ["Surface", "Middle", "Bottom"]); ax.invert_yaxis(); ax.set_xlabel("Salinity (channel mean)"); ax.legend(frameon=False, fontsize=5, ncol=2); guarda(fig, "fig_canal_profile", 90)


# ---------------------------------------------------------------- autoprueba
def diseno_sint(f, N, d, rng):
    A, B = rng.random((N, d)), rng.random((N, d)); X, bl, jj = [A, B], ["A"] * N + ["B"] * N, list(range(N)) * 2
    for i in range(d): ABi = A.copy(); ABi[:, i] = B[:, i]; X.append(ABi); bl += [f"AB{i + 1}"] * N; jj += list(range(N))
    return np.concatenate([f(x) for x in X]), bl, jj


def prueba():
    d = np.linspace(0.1, 1.0, 365); assert np.allclose(crecimiento_mensual(d), 0.1 * 0 + np.diff(np.array([np.mean(d[CUM[m + 1] - 5:CUM[m + 1]]) for m in range(12)]))[0:] / MES[1:]) and abs(crecimiento_mensual(0.1 * np.arange(365))[3] - 0.1) < 1e-9
    a = dict(evaluable=True, rho=0.7, m_hip=0.2, m_otros=0.1, n_hip=4); b = dict(a); assert veredicto_dst(a, b) == "CONFIRMA"
    assert veredicto_dst(a, dict(a, rho=-0.7)) == "CONTRADICE" and veredicto_dst(a, dict(a, rho=0.3)) == "INCONCLUSO" and veredicto_dst(a, dict(a, evaluable=False)).startswith("INCONCLUSO")
    assert veredicto_dst(dict(a, rho=-0.3, m_hip=0.0), dict(a, rho=-0.2, m_hip=0.0)) == "CONTRADICE"
    r = lectura_dst(np.array([-1.0, 1, 2, -1, 1]), np.array([0.0, 1, 1, 0, 1])); assert r["evaluable"] and r["m_hip"] == 1.0 and r["m_otros"] == 0.0 and r["n_hip"] == 3 and r["rho"] > 0.8
    assert not lectura_dst(np.array([-1.0, -2, -3]), np.array([1.0, 2, 3]))["evaluable"]
    assert abs(u_t_de_Q(100 * np.sin(np.linspace(0, 20 * np.pi, 4000, endpoint=False)), 2.0) - 100 / np.sqrt(2) / 2.0) < 1e-6
    rng = np.random.default_rng(1); x = rng.random(300); y = x + 0.05 * rng.random(300); ruido = rng.random(300)
    D, lo, hi = ic_diferencia(x, ruido, y, rng, n=300); assert lectura_D(lo, hi) == "I mejora a qfac" and D > 0.5
    D, lo, hi = ic_diferencia(x ** 3, x, y, rng, n=300); assert lectura_D(lo, hi) == "no mejora"                 # monotona: mismo rho
    S = np.array([[0.6, 0.3], [0.3, 0.6], [0.1, 0.1]]); assert abs(stat_rank_de_S(S) - 0.72 / 0.73) < 1e-9, stat_rank_de_S(S)    # ejemplo a mano (protocolo, Eq. 2)
    assert stat_rank_de_S(np.array([[0.6, 0.6], [0.3, 0.3], [0.1, 0.1]])) == 0.0
    f = lambda X: X[:, 0] + 2 * X[:, 1]; yv, bl, jj = diseno_sint(f, 16000, 3, rng); fA, fB, fAB, ok = tabla_sobol(yv, bl, jj, 3, 16000)     # con N = 4000 el IC de S_T = 0,8 mide ~0,055 > 0,05: se necesita N grande para que la prueba pueda cumplir el umbral
    e = estadisticos(fA[ok], fB[ok], fAB[:, ok], rng, B=200); assert np.allclose(e[4], [0.2, 0.8, 0.0], atol=0.04) and e[0] < 0.05 and e[1] < 1 and e[3] == 1 and e[2] < 0.05, e[:4]   # S_T exactos 0,2 / 0,8 / 0
    yv, bl, jj = diseno_sint(f, 16, 3, rng); fA, fB, fAB, ok = tabla_sobol(yv, bl, jj, 3, 16); assert estadisticos(fA[ok], fB[ok], fAB[:, ok], rng, B=200)[0] > 0.05        # N pequeno: no converge
    assert primer_N([3, 2, 0.5, 0.4], (16, 32, 48, 64), lambda v: v < 1) == 48 and primer_N([0.5, 2, 0.5, 0.4], (16, 32, 48, 64), lambda v: v < 1) == 48 and primer_N([2, 2], (48, 64), lambda v: v < 1) is None
    g = lambda X: np.stack([X[:, 0] + 2 * X[:, 1], X[:, 2]], 1); yv, bl, jj = diseno_sint(g, 4000, 3, rng)
    s = st_nodos(yv, np.ones(len(yv), bool), bl, jj, 3, N=4000); assert np.allclose(s[:, 0], [0.2, 0.8, 0.0], atol=0.04) and np.allclose(s[:, 1], [0, 0, 1], atol=0.04)
    assert dentro(35.0, 35.9) and not dentro(33.0, 35.9)
    print("autoprueba analisis_x: ok")


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    if a == "--prueba": prueba()
    elif a in ("dst", "bajoaporte", "convergencia", "mapa", "perfil"): {"dst": dst, "bajoaporte": bajoaporte, "convergencia": convergencia, "mapa": mapa, "perfil": perfil}[a]()
    elif a == "todo":
        G, datos = dst(); R, P = bajoaporte(); conv = convergencia(); mapas = mapa(); perf = perfil(); figuras(G, datos, R, P, conv, mapas, perf)
    else: sys.exit(__doc__)
