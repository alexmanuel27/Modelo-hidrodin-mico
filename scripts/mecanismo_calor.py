#!/usr/bin/env python3
"""B2 (V2, 16-nov): mecanismo de la variabilidad de la edad con flujo de calor. Lectura fijada en docs/protocolo_metricas_conjunto.md (16-nov (3)) ANTES de extraer el forzamiento.
  extrae   (en Lemaitre4, necesita netCDF4): media espacial horaria de sflux_air/sflux_rad 2016 -> resultados/forzamiento_2016_horario.csv
  analiza  (local, solo numpy): flujos de calor y esfuerzo del viento por formulas bulk con la SST OISST (PROXY, no el flujo que calculo SCHISM) frente a la edad diaria de
           runs/robustez_largo/{m0000 (sin calor), m0001, m0005} -> resultados/mecanismo_calor.txt
  --prueba formulas y reglas con datos sinteticos."""
import csv, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent)); from conjunto_calor import rangos, spearman    # noqa: E402
RAIZ = Path(__file__).resolve().parent.parent; HOR = RAIZ / "resultados" / "forzamiento_2016_horario.csv"
SIG, RHO_A, CD, CH, CE, CP, LV, ALB, EPS = 5.670e-8, 1.2, 1.3e-3, 1.1e-3, 1.2e-3, 1005.0, 2.5e6, 0.06, 0.97
MES = np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])


def qsat(T, p):   # kg/kg, Tetens sobre agua (T en C, p en Pa)
    es = 611.0 * np.exp(17.27 * T / (T + 237.3)); return 0.622 * es / (p - 0.378 * es)


def flujos(u, v, Ta, qa, p, sw, lw, Ts):
    """Proxy bulk, W/m2 positivo hacia el oceano; Ta, Ts en C. Cd, Ch, Ce constantes: es un proxy, no el flujo del modelo."""
    U = np.hypot(u, v); tau = RHO_A * CD * U ** 2
    SW = (1 - ALB) * sw; LW = EPS * lw - EPS * SIG * (Ts + 273.15) ** 4
    H = RHO_A * CP * CH * U * (Ts - Ta); LE = RHO_A * LV * CE * U * (0.98 * qsat(Ts, p) - qa)
    return dict(U=U, tau=tau, SW=SW, LW=LW, H=H, LE=LE, Qnet=SW + LW - H - LE)


def diario(x, n=365):   # media diaria de n*k muestras equiespaciadas desde el dia 0
    x = np.asarray(x, float); return x[:n * (len(x) // n)].reshape(n, -1).mean(1)


def bloques(x, b=5): return np.asarray(x, float).reshape(-1, b).mean(1)


def reglas(A, C, tau, B=None):
    """A: edad diaria (365). C = -Qnet diaria. tau diaria. B: edad diaria del control (sin calor). Devuelve dict con T1, T2, T3 y veredictos."""
    a, c, t = bloques(A), bloques(C[:365]), bloques(tau[:365]); G = np.diff(a) / 5          # G_b: crecimiento tras el bloque b, b = 0..71
    r = {}
    def rho_k(a_, k):                                                                       # b >= 6 (se descartan los 30 d de arranque desde edad 0)
        b = np.arange(max(6, k), 72); Gb = np.diff(bloques(a_)) / 5; return spearman(c[b - k], Gb[b]), b
    r["rho0"], b0 = rho_k(A, 0); r["rho1"], b1 = rho_k(A, 1); r["T1"] = max(r["rho0"], r["rho1"]); k = 0 if r["rho0"] >= r["rho1"] else 1
    r["T1_ver"] = "confirmada" if r["T1"] >= 0.30 else "contradicha" if max(r["rho0"], r["rho1"]) <= 0.10 else "no concluyente"
    if B is not None:
        rb0, _ = rho_k(B, 0); rb1, _ = rho_k(B, 1); r["ctrl"] = max(rb0, rb1); r["ctrl_ok"] = r["ctrl"] < 0.5 * r["T1"]
    b = np.arange(max(6, k), 72); Gb = G[b]; z = t[b - k]; y = c[b - k]
    res = lambda p, q: p - np.polyval(np.polyfit(q, p, 1), q)
    r["parcial"] = float(np.corrcoef(res(rangos(y), rangos(z)), res(rangos(Gb), rangos(z)))[0, 1]); r["rho_tau"] = spearman(z, Gb); r["k"] = k; r["n1"] = len(b)
    cum = np.concatenate([[0], np.cumsum(MES)]); mes = lambda x: np.array([np.mean(x[cum[i]:cum[i + 1]]) for i in range(12)])
    r["T2"] = spearman(mes(C)[1:], mes(A)[1:])    # Feb-Dic; C = -Qnet, asi que se espera rho(C, edad) >= +0,60 (= rho(Qnet, edad) <= -0,60)
    r["T2_ver"] = "confirmada" if r["T2"] >= 0.60 else "contradicha" if r["T2"] <= 0.30 else "no concluyente"
    r["global"] = ("apoyada (compatible, no prueba el mecanismo)" if r["T1_ver"] == "confirmada" and r["T2_ver"] == "confirmada" and r.get("ctrl_ok", True) and r["parcial"] >= 0.25
                   else "contradicha" if "contradicha" in (r["T1_ver"], r["T2_ver"]) else "no concluyente / parcial")
    return r


def prueba():
    f = flujos(0, 0, 25, 0.01, 101300, 500, 0, 25); assert abs(f["Qnet"] - 0.94 * 500 - f["LW"]) < 1e-6 and f["H"] == 0 and f["LE"] == 0 and f["tau"] == 0
    assert abs(f["LW"] + 0.97 * 5.67e-8 * 298.15 ** 4) < 1 and 0.0215 < qsat(27, 101300) < 0.0230
    assert abs(flujos(5, 0, 25, 0.01, 101300, 0, 0, 25)["tau"] - 1.2 * 1.3e-3 * 25) < 1e-9
    rng = np.random.default_rng(1); d = np.arange(365); C = 100 * np.sin(2 * np.pi * d / 90) + 20 * rng.normal(size=365); tau = rng.random(365)
    A = 8 + np.cumsum(C - C.mean()) * 0.004; B = 7 + 0.3 * rng.normal(size=365)       # edad que crece donde C > 0
    r = reglas(A, C, tau, B); assert r["T1_ver"] == "confirmada" and r["ctrl_ok"] and r["T1"] > 0.5, r
    r2 = reglas(8 + rng.normal(size=365), C, tau, B); assert r2["T1_ver"] != "confirmada" and r2["global"] != "apoyada (compatible, no prueba el mecanismo)", r2
    assert len(diario(np.arange(2190.))) == 365 and bloques(np.arange(365.)).shape == (73,); print("prueba ok")


def extrae():
    import netCDF4 as nc
    from datetime import datetime
    S = RAIZ / "datos" / "forzamiento" / "sflux"; filas = []
    for m in range(1, 13):
        with nc.Dataset(S / f"sflux_air_2016{m:02d}.nc") as a, nc.Dataset(S / f"sflux_rad_2016{m:02d}.nc") as r:
            t = nc.num2date(a["time"][:], a["time"].units, only_use_cftime_datetimes=False, only_use_python_datetimes=True)
            assert len(t) == r["time"].shape[0], (m, len(t), r["time"].shape)
            g = lambda ds, k: np.asarray(ds[k][:], float).reshape(len(t), -1).mean(1)
            Ta = g(a, "stmp"); Ta = Ta - 273.15 if Ta.mean() > 100 else Ta
            for i, ti in enumerate(t): filas.append([ti.strftime("%Y-%m-%d %H:%M"), g(a, "uwind")[i], g(a, "vwind")[i], Ta[i], g(a, "spfh")[i], g(a, "prmsl")[i], g(r, "dswrf")[i], g(r, "dlwrf")[i]])
    HOR.parent.mkdir(exist_ok=True); w = csv.writer(open(HOR, "w", newline="")); w.writerow(["fecha", "u10", "v10", "Ta_C", "q", "p_Pa", "dswrf", "dlwrf"]); w.writerows(filas)
    print(f"{len(filas)} filas -> {HOR}")


def analiza():
    H = list(csv.DictReader(open(HOR))); col = lambda k: np.array([float(h[k]) for h in H])
    d0 = np.datetime64("2016-01-01"); dia = np.array([(np.datetime64(h["fecha"][:10]) - d0).astype(int) for h in H]); assert dia.min() == 0 and dia.max() >= 364, (dia.min(), dia.max())
    sst = {f["fecha"]: float(f["sst_C"]) for f in csv.DictReader(open(RAIZ / "datos" / "forzamiento" / "sst" / "oisst_habana.csv"))}
    Ts = np.array([sst[h["fecha"][:10]] for h in H]); F = flujos(col("u10"), col("v10"), col("Ta_C"), col("q"), col("p_Pa"), col("dswrf"), col("dlwrf"), Ts)
    D = {k: np.array([v[dia == i].mean() for i in range(365)]) for k, v in F.items()}; C = -D["Qnet"]
    A = {}
    for nom, m in (("sin calor (m0000)", "m0000"), ("calor 28 C (m0001)", "m0001"), ("calor + OISST (m0005)", "m0005")):
        z = np.load(RAIZ / "runs" / "robustez_largo" / m / "resumen.npz"); A[nom] = np.array([z["serie_bahia"][np.floor(z["dias"] + 1e-9) == i].mean() for i in range(365)])
    ks = list(A); B = A[ks[0]]
    out = ["PROXY de flujo (formulas bulk con Cd, Ch, Ce constantes y SST OISST diaria; no es el flujo calculado por SCHISM). 365 d de 2016; bloques de 5 d; se descartan los 30 d de arranque."]
    out.append("forzamiento 2016: Qnet medio %+.1f W/m2 (SW %.0f, LW %.0f, H %.0f, LE %.0f), U10 medio %.1f m/s, tau medio %.3f N/m2" % tuple(D[k].mean() for k in ("Qnet", "SW", "LW", "H", "LE", "U", "tau")))
    for nom in ks[1:]:
        r = reglas(A[nom], C, D["tau"], B); out.append(f"{nom}: T1 rho(enfriamiento, crecimiento) lag0 {r['rho0']:+.2f} lag1 {r['rho1']:+.2f} -> {r['T1_ver']}; "
            f"control (sin calor) {r['ctrl']:+.2f} ({'ok' if r['ctrl_ok'] else 'NO ok: no es especifico del flujo de calor'}); parcial dado tau (lag {r['k']}, n = {r['n1']}) {r['parcial']:+.2f}; "
            f"rho(tau, crecimiento) {r['rho_tau']:+.2f}; T2 mensual (feb-dic) rho(enfriamiento, edad) {r['T2']:+.2f} -> {r['T2_ver']}; veredicto B2: {r['global']}")
    cum = np.concatenate([[0], np.cumsum(MES)]); out.append("[descriptivo] mes: Qnet (W/m2), tau (N/m2), U10, edad sin calor, con calor 28 C, con calor + OISST")
    for i in range(12):
        s = slice(cum[i], cum[i + 1]); out.append("  %2d %+7.1f %.3f %4.1f   %5.1f %5.1f %5.1f" % (i + 1, D["Qnet"][s].mean(), D["tau"][s].mean(), D["U"][s].mean(), *(A[k][s].mean() for k in ks)))
    t = "\n".join(out); print(t); (RAIZ / "resultados" / "mecanismo_calor.txt").write_text(t + "\n")


if __name__ == "__main__":
    {"--prueba": prueba, "extrae": extrae, "analiza": analiza}[sys.argv[1] if len(sys.argv) > 1 else "analiza"]()
