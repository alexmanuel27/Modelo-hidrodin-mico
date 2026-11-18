#!/usr/bin/env python3
"""Parte I de docs/protocolo_salinidad_superficie.md (lecturas fijadas ANTES de calcular): por que el modelo es demasiado salado en superficie.
S11 = media de las dos medias de fase de S superficial en las 11 estaciones JICA (mapas de 16:00 UTC), hueco = mediana(704) - 31,25.
  python scripts/salinidad_superficie.py            -> resultados/salinidad_superficie_parteI.txt
  python scripts/salinidad_superficie.py --prueba"""
import csv, json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from jica_caudales_extra import F, disenyo                              # noqa: E402
from jica_extrae_estaciones import fases                                # noqa: E402

S_MAR, S_OBS, N_MIN_MAPAS, N_MIN_FASE, S_TAB412 = 36.0, (32.2 + 30.3) / 2, 3, 8, 34.3
EXPLICA, PARCIAL = 0.5, 0.25
ZONAS = {1: "Canal de Entrada", 2: "Centro de la Bahia", 3: "Marimelena", 4: "Guasabacoa", 5: "Atares"}


def lectura(c): return "explica" if c >= EXPLICA else "parcial" if c >= PARCIAL else "no explica"


def celdas():
    E = list(csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_estaciones_utm.csv")))
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); ge, gn = M["s2_e"], M["s2_n"]
    return [(np.abs(gn - float(r["N_utm17n"])).argmin(), np.abs(ge - float(r["E_utm17n"])).argmin()) for r in E]


def s11_dir(d, cel):
    """S11 de un directorio con resumen.npz (misma regla que sal_704); NaN si falta una fase."""
    z = np.load(Path(d) / "resumen.npz"); S = S_MAR * (1 - z["s2_dulce"]); q = z["Q"][np.abs(z["dias"][None, :] - z["s2_dias"][:, None]).argmin(1)]
    s = np.nanmean(np.stack([S[:, i, k] for i, k in cel], 1), 1)
    ph = [float(np.nanmean(s[m])) if m.sum() >= N_MIN_MAPAS else np.nan for m in (q > 0, q <= 0)]
    return float(np.mean(ph))


def s11_muestras(npz):
    """S11 con las 175 muestras de jica_extrae_estaciones (nodo principal, nivel sup): medias de fase del ajuste armonico."""
    z = np.load(npz); cr, ba = fases(z["t"], z["eta_bay"]); s = np.nanmean(z["S_n"][:, :, 0], axis=1)
    return float(np.mean([np.nanmean(s[m]) if m.sum() >= N_MIN_FASE else np.nan for m in (cr, ba)]))


def ajusta(filas, y):
    X, lq = disenyo(filas); b = np.linalg.lstsq(X, y, rcond=None)[0]
    return X, lq, b, float(1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def qfac_para(X, b, objetivo):
    """qfac que lleva S11 al objetivo con el resto de parametros en su media. Devuelve (todas las raices con qfac > 0, la menor con qfac >= 1 o None)."""
    a = float(X[:, :-2].mean(0) @ b[:-2]) - objetivo; r = np.roots([b[-1], b[-2], a]) if abs(b[-1]) > 1e-12 else (np.array([-a / b[-2]]) if abs(b[-2]) > 1e-12 else np.array([]))
    q = sorted(float(np.exp(x.real)) for x in np.atleast_1d(r) if abs(x.imag) < 1e-9)
    return q, next((x for x in q if x >= 1.0), None)


def lectura_h1(q):
    return "no es cuestion de caudal" if q is None or q > 4 else "explica" if q <= 2 else "marginal"


def efecto_h4(X, lq, b):
    usa = np.exp(lq) <= 2.0 / F; X1 = X[usa].copy(); X1[:, -2] = lq[usa] + np.log(F); X1[:, -1] = X1[:, -2] ** 2
    return float(np.median(X1 @ b - X[usa] @ b)), int(usa.sum())


def prueba():
    r = np.random.default_rng(2); n = 300
    filas = [dict(carta=1879, alfa=r.random(), datum=r.random(), cd=r.random(), vfac=r.random(), vrot=r.random(), mfac=r.random(), u_semilla=r.random(),
                  qfac=float(np.exp(np.log(.25) + r.random() * np.log(8)))) for _ in range(n)]
    lq = np.log([f["qfac"] for f in filas]); y = 35.0 - 1.5 * lq + 0.2 * lq ** 2            # sin ruido
    X, lq2, b, r2 = ajusta(filas, y); assert r2 > 1 - 1e-9 and abs(b[-2] + 1.5) < 1e-6 and abs(b[-1] - 0.2) < 1e-6
    q, q1 = qfac_para(X, b, 33.0); x = np.log(q1); assert abs(35.0 - 1.5 * x + 0.2 * x ** 2 - 33.0) < 1e-6 and q1 >= 1 and len(q) == 2, (q, q1)
    assert qfac_para(X, b, 31.25)[1] is None                       # discriminante < 0: sin raiz
    assert qfac_para(X, b, 20.0)[1] is None and [lectura_h1(v) for v in (None, 5, 3, 1.5)] == ["no es cuestion de caudal"] * 2 + ["marginal", "explica"]
    d, nu = efecto_h4(X, lq2, b); assert d < 0 and nu == int((np.exp(lq2) <= 2 / F).sum())
    assert [lectura(c) for c in (0.6, 0.3, 0.1, -0.2)] == ["explica", "parcial", "no explica", "no explica"]
    filas704 = list(csv.DictReader(open(RAIZ / "resultados" / "jica_sal_superficie_704.csv"))); cel = celdas()     # reproduce el CSV de los 704
    for f in filas704[:3]:
        d = RAIZ / "runs" / "conjunto" / f"m{int(f['miembro']):04d}"
        if d.exists(): assert abs(s11_dir(d, cel) - (float(f["S_creciente_nodo"]) + float(f["S_bajamar_nodo"])) / 2) < 1e-4, f["miembro"]
    print("autoprueba salinidad_superficie: ok")


def main():
    cel = celdas(); D = list(csv.DictReader(open(RAIZ / "datos" / "conjunto" / "diseno.csv"))); L = []
    P = list(csv.DictReader(open(RAIZ / "resultados" / "jica_sal_superficie_704.csv")))
    s11 = {int(f["miembro"]): (float(f["S_creciente_nodo"]) + float(f["S_bajamar_nodo"])) / 2 for f in P}
    eq = {int(f["miembro"]): f["equilibrio"] == "True" for f in P}
    ok = [m for m in sorted(s11) if not np.isnan(s11[m])]; y = np.array([s11[m] for m in ok]); filas = [D[m] for m in ok]
    med = float(np.median(y)); hueco = med - S_OBS
    L += [f"S11 de los {len(ok)} miembros con dato: mediana {med:.2f}, P5-P95 {np.percentile(y, 5):.2f}-{np.percentile(y, 95):.2f}; observado (32,2 + 30,3)/2 = {S_OBS:.2f}; HUECO = {hueco:+.2f}"]
    X, lq, b, r2 = ajusta(filas, y); q, q1 = qfac_para(X, b, S_OBS); ch, nu = efecto_h4(X, lq, b)
    L += [f"H1 regresion (n {len(ok)}, R2 {r2:.2f}): coef ln qfac {b[-2]:+.3f}, (ln qfac)^2 {b[-1]:+.3f}; raices qfac para S11 = {S_OBS:.2f}: {[round(v, 2) for v in q] or 'ninguna'}; "
              f"menor con qfac >= 1: {q1 if q1 is None else round(q1, 2)} -> {lectura_h1(q1)}"]
    L += [f"H4 (F = {F:.2f}, n {nu}): cambio mediano de S11 {ch:+.3f}; cierre {-ch / hueco:+.3f} -> {lectura(-ch / hueco)}"]
    se = np.array([eq[m] for m in ok]); Xe, lqe, be, r2e = ajusta([f for f, s in zip(filas, se) if s], y[se]); qe, q1e = qfac_para(Xe, be, S_OBS); che, nue = efecto_h4(Xe, lqe, be)
    L += [f"   sensibilidad solo en equilibrio (n {int(se.sum())}, R2 {r2e:.2f}): H1 menor raiz >= 1: {q1e if q1e is None else round(q1e, 2)} ({lectura_h1(q1e)}); H4 cierre {-che / hueco:+.3f}"]
    c0 = s11_dir(RAIZ / "runs" / "robustez" / "m0000", cel); L += [f"H2/H3(i) robustez (120 d, miembro central): control m0000 S11 = {c0:.2f}"]
    for k, nom in ((2, "H2 cierre k-epsilon"), (3, "H2 32 niveles"), (4, "H2 difusividad minima x10"), (1, "H3 calor, borde 28 C"), (5, "H3 calor + OISST")):
        s = s11_dir(RAIZ / "runs" / "robustez" / f"m{k:04d}", cel); c = (c0 - s) / hueco; L += [f"   m{k:04d} {nom:28s} S11 {s:.2f}  cierre {c:+.3f} -> {lectura(c)}"]
    cs = []
    for m in range(64):
        a, bb = RAIZ / "runs" / "conjunto" / f"m{m:04d}", RAIZ / "runs" / "conjunto_calor" / f"m{m:04d}"
        if (a / "resumen.npz").exists() and (bb / "resumen.npz").exists():
            sa, sb = s11_dir(a, cel), s11_dir(bb, cel)
            if not (np.isnan(sa) or np.isnan(sb)): cs.append((sa - sb) / hueco)
    cs = np.array(cs); L += [f"H3(ii) 64 pares calor+OISST vs sin calor: n {len(cs)}, cierre mediano {np.median(cs):+.3f} (P5-P95 {np.percentile(cs, 5):+.3f} a {np.percentile(cs, 95):+.3f}; min {cs.min():+.3f}, max {cs.max():+.3f}) -> {lectura(np.median(cs))}"]
    L += ["Control de muestreo (16:00 UTC vs 175 muestras, miembros 0-2 del conjunto):"]
    for m in range(3):
        a = s11_dir(RAIZ / "runs" / "conjunto" / f"m{m:04d}", cel); b2 = s11_muestras(RAIZ / "resultados" / "jica_estaciones_modelo" / f"conjunto_m{m:04d}_dias91-120.npz")
        L += [f"   m{m:04d}: mapas {a:.2f}, muestras {b2:.2f}, dif {a - b2:+.2f} -> {'NO representativo' if abs(a - b2) >= 0.3 else 'ok'}"]
    # zonas frente a la tabla 4.11 (nov. 2001) y bahia frente a la tabla 4.12
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); zo, ar = M["zona"], M["area"]
    T = list(csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_vol5.csv")))
    obs = {n: [float(r["valor"]) for r in T if r["tabla"] == "4.11" and r["estacion"] == n and r["variable"] == "salinidad" and r["nivel_m"] == "surface" and r["mes"] == "2001-11"] for n in ZONAS.values()}
    Sz = {k: [] for k in ZONAS}; Sb = []
    for m in ok:
        d = RAIZ / "runs" / "conjunto" / f"m{m:04d}"
        if not (d / "resumen.npz").exists(): continue
        ds = np.load(d / "resumen.npz")["dulce_sup"] if "dulce_sup" in np.load(d / "resumen.npz").files else None
        if ds is None: continue
        for k in ZONAS: Sz[k].append(S_MAR * (1 - (ds[zo == k] * ar[zo == k]).sum() / ar[zo == k].sum()))
        Sb.append(S_MAR * (1 - (ds[zo > 0] * ar[zo > 0]).sum() / ar[zo > 0].sum()))
    L += [f"Zonas (superficie, ventana final; 704 miembros n {len(Sb)}) frente a tabla 4.11 nov. 2001 (alta, baja) con margen +-1:"]
    for k, n in ZONAS.items():
        v = np.array(Sz[k]); lo, hi = min(obs[n]) - 1, max(obs[n]) + 1
        L += [f"   {n:19s} obs {obs[n]} -> [{lo:.2f}, {hi:.2f}]; modelo mediana {np.median(v):.2f} (P5-P95 {np.percentile(v, 5):.2f}-{np.percentile(v, 95):.2f}); dentro {100 * np.mean((v >= lo) & (v <= hi)):.0f} %"]
    Sb = np.array(Sb); L += [f"Bahia: S media {np.median(Sb):.2f}; fraccion con S < {S_TAB412} (tabla 4.12, maximo mensual superficie): {100 * np.mean(Sb < S_TAB412):.1f} %"]
    t = "\n".join(L); print(t); (RAIZ / "resultados" / "salinidad_superficie_parteI.txt").write_text(t + "\n")


if __name__ == "__main__":
    prueba() if "--prueba" in sys.argv else main()
