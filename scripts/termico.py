#!/usr/bin/env python3
"""V3 X1 y X2: freno termico. Lecturas fijadas en docs/protocolo_metricas_conjunto.md (17-nov (1) y (2)) ANTES de lanzar las corridas y de ver ningun resultado.
  reduce <carpeta_corrida>   (cluster, netCDF4) medias diarias de T, S, densidad del canal, flujos de calor y esfuerzo del viento -> <carpeta>/termico_diario.csv
  analiza                    (local, numpy) aplica las lecturas -> resultados/termico.txt
  --prueba                   datos sinteticos (UNESCO, reduccion diaria y las dos lecturas)"""
import csv, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conjunto_calor import spearman    # noqa: E402
from mecanismo_calor import reglas, MES    # noqa: E402
RAIZ = Path(__file__).resolve().parent.parent; CUM = np.concatenate([[0], np.cumsum(MES)])
COLS = ["dia", "T_bahia_sup", "T_canal_sup", "S_canal_sup", "S_canal_fondo", "rho_canal_sup", "rho_canal_fondo", "drho", "SW", "H", "LE", "LWup", "LWdw", "Qdown", "tau"]


def unesco(T, S):
    """Densidad UNESCO 1980 a presion 0 (kg/m3); la de SCHISM con ieos_type = 0. Valor de prueba: S = 35, T = 5 -> 1027,67547."""
    rw = 999.842594 + 6.793952e-2 * T - 9.095290e-3 * T ** 2 + 1.001685e-4 * T ** 3 - 1.120083e-6 * T ** 4 + 6.536332e-9 * T ** 5
    A = 8.24493e-1 - 4.0899e-3 * T + 7.6438e-5 * T ** 2 - 8.2467e-7 * T ** 3 + 5.3875e-9 * T ** 4
    B = -5.72466e-3 + 1.0227e-4 * T - 1.6546e-6 * T ** 2
    return rw + A * S + B * S ** 1.5 + 4.8314e-4 * S ** 2


def reducir_dia(T, S, sol, sen, lat, ul, dl, tx, ty, zona, area):
    """T, S (nt, nodo, nivel; nivel 0 = fondo, -1 = superficie); 2D (nt, nodo). Medias de todos los instantes del dia; bahia = zona > 0 ponderada por area, canal = zona 1."""
    b, c = zona > 0, zona == 1; w = area[b] / area[b].sum()
    bm = lambda x: float((x[:, b].mean(0) * w).sum()); cm = lambda x: float(x[:, c].mean())
    rs, rf = unesco(T[:, :, -1], S[:, :, -1]), unesco(T[:, :, 0], S[:, :, 0])
    r = dict(T_bahia_sup=bm(T[:, :, -1]), T_canal_sup=cm(T[:, :, -1]), S_canal_sup=cm(S[:, :, -1]), S_canal_fondo=cm(S[:, :, 0]), rho_canal_sup=cm(rs), rho_canal_fondo=cm(rf),
             drho=cm(rf) - cm(rs), SW=bm(sol), H=bm(sen), LE=bm(lat), LWup=bm(ul), LWdw=bm(dl), tau=bm(np.hypot(tx, ty)))
    r["Qdown"] = r["SW"] + r["LWdw"] - r["LWup"] - r["H"] - r["LE"]       # positivo hacia el oceano; solar y LW descendente ya vienen hacia abajo; H, LE y LW ascendente, hacia arriba (param.nml de SCHISM)
    return r


def reduce(dirm):
    from netCDF4 import Dataset
    out = Path(dirm) / "outputs"; M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); n = len(list(out.glob("out2d_*.nc"))); filas = []
    for d in range(1, n + 1):
        try:
            with Dataset(out / f"temperature_{d}.nc") as a, Dataset(out / f"salinity_{d}.nc") as s, Dataset(out / f"out2d_{d}.nc") as o:
                g = lambda ds, k: np.asarray(ds[k][:], float)
                f = reducir_dia(g(a, "temperature"), g(s, "salinity"), g(o, "solarRadiation"), g(o, "sensibleHeat"), g(o, "latentHeat"), g(o, "upwardLongwave"),
                                g(o, "downwardLongwave"), g(o, "windStressX"), g(o, "windStressY"), M["zona"], M["area"])
        except (OSError, IndexError) as e:
            print(f"dia {d}: {e}"); break
        filas.append([d] + [f[k] for k in COLS[1:]])
    w = csv.writer(open(Path(dirm) / "termico_diario.csv", "w", newline="")); w.writerow(COLS); w.writerows(filas); print(f"{len(filas)} dias -> {dirm}/termico_diario.csv")


def mensual(x): return np.array([np.mean(x[CUM[i]:CUM[i + 1]]) for i in range(12)])


def edad(p):
    z = np.load(p); return np.array([z["serie_bahia"][np.floor(z["dias"] + 1e-9) == i].mean() for i in range(365)])


def lectura_x1(Bn, A0, B0, f, sst):
    """Bn: edad diaria de la repeticion con T (calor + OISST, viento real); A0: sin calor (mismo viento); B0: la m0005 original; f: dict de columnas diarias; sst: OISST diaria (365)."""
    o = []; an = mensual(Bn) - mensual(A0); i = slice(1, 12)
    dd = np.abs(mensual(Bn) - mensual(B0)).max(); o.append(f"validacion: la repeticion con salidas frente a la m0005 original, diferencia maxima de la media mensual {dd:.3f} d -> " + ("reproduce (<= 0,05 d)" if dd <= 0.05 else "NO reproduce: las salidas o el reparto cambiaron la corrida; se lee igualmente, con esta salvedad"))
    drho, dT = mensual(f["drho"]), mensual(f["T_bahia_sup"]) - mensual(sst)
    r1, r2 = spearman(drho[i], an[i]), spearman(dT[i], an[i]); o_ = np.argsort(an[i]); top, bot = o_[-3:], o_[:3]; ratio = float(np.median(drho[i][top]) / np.median(drho[i][bot]))
    v = lambda r: "confirma" if r <= -0.60 else "contradice" if r >= -0.30 else "no concluyente"
    v3 = "confirma" if ratio < 0.5 else "contradice" if ratio >= 1.0 else "no concluyente"
    o.append("mes: anomalia de edad (calor - sin calor, d), drho del canal (kg/m3), T_bahia - T_borde (C)")
    o += [f"  {m + 1:2d} {an[m]:+6.2f} {drho[m]:6.3f} {dT[m]:+6.2f}" for m in range(12)]
    o.append(f"R1 rho(drho canal, anomalia), feb-dic (n = 11): {r1:+.2f} -> {v(r1)}; R2 rho(T_bahia - T_borde, anomalia): {r2:+.2f} -> {v(r2)}; R3 drho mediano de los 3 meses de mayor anomalia / los 3 de menor: {ratio:.2f} -> {v3}")
    ver = "FRENO TERMICO APOYADO" if (v(r1), v(r2), v3) == ("confirma",) * 3 else "FRENO TERMICO CONTRADICHO" if "contradice" in (v(r1), v3) else "PARCIAL / NO CONCLUYENTE"
    o.append(f"veredicto X1: {ver}")
    r = reglas(Bn, -f["Qdown"], f["tau"], A0)
    o.append(f"T1-T3 de 16-nov con el flujo del MODELO en lugar del proxy: T1 {r['T1']:+.2f} ({r['T1_ver']}), control {r['ctrl']:+.2f}, parcial dado tau {r['parcial']:+.2f}, T2 {r['T2']:+.2f} ({r['T2_ver']}) -> {r['global']}")
    return o


def lectura_x2(A, B, C, D, ratio_viento=None):
    m = lambda x: float(np.mean(x[30:])); n14 = lambda x: int((x[30:] > 14).sum()); o = []
    for nom, x in (("A sin calor, viento real", A), ("B calor, viento real", B), ("C sin calor, viento climatologico", C), ("D calor, viento climatologico", D)):
        o.append(f"  {nom}: edad media dias 31-365 {m(x):.2f} d; dias > 14 d {n14(x)}; media movil de 30 d {np.convolve(x[30:], np.ones(30) / 30, 'valid').min():.1f}-{np.convolve(x[30:], np.ones(30) / 30, 'valid').max():.1f} d")
    hr, hc = m(B) - m(A), m(D) - m(C); o.append(f"efecto del calor con viento real {hr:+.2f} d; con viento climatologico {hc:+.2f} d; efecto del viento sin calor {m(C) - m(A):+.2f} d, con calor {m(D) - m(B):+.2f} d; interaccion {hc - hr:+.2f} d")
    if hr <= 0: ver = "no aplicable: el calor no sube la edad con viento real"
    else: ver = "el efecto termico SE MANTIENE sin viento sinoptico (>= 50 %)" if hc >= 0.5 * hr else "el efecto depende de los frentes (< 25 %)" if hc < 0.25 * hr else "PARCIAL (entre 25 % y 50 %)"
    o.append(f"veredicto X2: {ver} (efecto con viento climatologico = {100 * hc / hr:.0f} % del efecto con viento real)" if hr > 0 else f"veredicto X2: {ver}")
    if ratio_viento is not None and ratio_viento < 0.6: o.append(f"aviso: la rapidez media climatologica es {ratio_viento:.2f} de la real (< 0,6); el contraste mezcla quitar la variabilidad y bajar la rapidez media")
    return o


def analiza():
    R = RAIZ / "runs"; T = [R / "termico" / f"m000{k}" for k in range(3)]
    A0, B0 = edad(R / "robustez_largo" / "m0000" / "resumen.npz"), edad(R / "robustez_largo" / "m0005" / "resumen.npz")
    Bn, D, C = (edad(t / "resumen.npz") for t in T)
    cols = lambda p: {k: np.array([float(r[k]) for r in csv.DictReader(open(p))]) for k in COLS}
    f = cols(T[0] / "termico_diario.csv"); fd = cols(T[1] / "termico_diario.csv")
    ss = {r["fecha"]: float(r["sst_C"]) for r in csv.DictReader(open(RAIZ / "datos" / "forzamiento" / "sst" / "oisst_habana.csv"))}
    sst = np.array([ss[str(np.datetime64("2016-01-01") + i)] for i in range(365)])
    rv = None
    try: rv = float(open(RAIZ / "resultados" / "viento_climatologico.txt").read().split("= ")[-1].split()[0])
    except (OSError, ValueError): pass
    o = ["X1 (repeticion con T y flujos, calor + OISST, viento real, 365 d):"] + lectura_x1(Bn, A0, B0, f, sst) + ["", "X2 (factorial 2x2, 365 d; A y B son las corridas ya existentes de robustez_largo m0000 y m0005):"] + lectura_x2(A0, B0, C, D, rv)
    o.append(f"[descriptivo] drho mediano del canal: viento real {np.median(f['drho']):.3f}, viento climatologico {np.median(fd['drho']):.3f} kg/m3; Qdown medio {f['Qdown'].mean():+.1f} W/m2 (viento real), {fd['Qdown'].mean():+.1f} (climatologico)")
    t = "\n".join(o); print(t); (RAIZ / "resultados" / "termico.txt").write_text(t + "\n")


def prueba():
    assert abs(unesco(5.0, 35.0) - 1027.67547) < 1e-3 and abs(unesco(0.0, 0.0) - 999.842594) < 1e-6
    nt, n, nv = 6, 4, 16; zona = np.array([1, 1, 2, 0]); area = np.ones(n)
    T = np.full((nt, n, nv), 25.0); S = np.full((nt, n, nv), 30.0); S[:, :, 0] = 33.0; z2 = np.zeros((nt, n))
    r = reducir_dia(T, S, z2 + 200, z2 + 10, z2 + 100, z2 + 400, z2 + 380, z2 + 3, z2 + 4, zona, area)
    assert r["drho"] > 1.5 and abs(r["Qdown"] - (200 + 380 - 400 - 10 - 100)) < 1e-9 and abs(r["tau"] - 5) < 1e-9, r
    rng = np.random.default_rng(3); d = np.arange(365); fr = 100 * np.sin(2 * np.pi * (d - 60) / 365 * 1.0) + 20 * rng.normal(size=365); tau = 0.04 + 0.01 * rng.random(365)
    A0 = 6.5 + 0.2 * rng.normal(size=365); an = np.maximum(0, np.cumsum(fr - fr.mean()) * 0.002); Bn = A0 + an
    drho_d = 1.5 - 0.15 * an + 0.02 * rng.normal(size=365); Tb = 26 - 0.02 * an + 0.05 * rng.normal(size=365)
    f = dict(drho=drho_d, T_bahia_sup=Tb, Qdown=-fr, tau=tau)
    o = lectura_x1(Bn, A0, Bn, f, np.full(365, 26.0)); assert any("FRENO TERMICO APOYADO" in x for x in o), o
    f2 = dict(f, drho=1.5 + 0.02 * rng.normal(size=365)); o2 = lectura_x1(Bn, A0, Bn, f2, np.full(365, 26.0)); assert not any("APOYADO" in x for x in o2), o2
    x2 = lectura_x2(A0, A0 + 4.0, A0 + 0.3, A0 + 0.3 + 3.0); assert "SE MANTIENE" in x2[-1], x2
    x3 = lectura_x2(A0, A0 + 4.0, A0, A0 + 0.5); assert "depende de los frentes" in x3[-1], x3
    print("prueba ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    prueba() if a == ["--prueba"] else reduce(a[1]) if a[:1] == ["reduce"] else analiza()
