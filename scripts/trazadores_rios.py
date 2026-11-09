#!/usr/bin/env python3
"""Destino del agua de cada rio (figura 8): posproceso de los trazadores pasivos GEN_1..3, uno por rio (orden de caso_real.Q_RIOS:
Luyano, Martin Perez, Tadeo). Protocolo congelado el 8-nov-2026: docs/protocolo_trazadores_rios.md.

Por caso (ultimos 30 d): T_i = M_i / Q_i (M_i = volumen de agua del rio i en la bahia), fraccion de cada zona que es agua del rio i y
reparto de M_i por zona (volumen y superficie / fondo), mapas, equilibrio (M_i crece <= 1 % de su media por dia en los ultimos 10 d)
y control: la suma de los tres trazadores contra el agua dulce de la salinidad (1 - S/36), diferencia del inventario < 5 %.
  python trazadores_rios.py <caso>               -> <caso>/trazadores.json y trazadores.npz (mapas)
  python trazadores_rios.py --clasifica <dir>    -> lee <dir>/m0000..m0003/trazadores.json y clasifica R1-R4 (robusta si se cumple en los 4)
  python trazadores_rios.py --prueba             -> autoprueba con solucion conocida
Necesita GEN_i_*.nc, salinity_*.nc y out2d_*.nc (netCDF4: solo en el cluster o en el entorno bahia del Mac)."""
import json, sys
from pathlib import Path
import numpy as np

VENTANA, S_MAR = 30, 36.0                        # como posproceso.py y renovacion_dulce.py
RIOS = ["Luyano", "Martin Perez", "Tadeo"]
ZONAS = {1: "canal", 2: "cuenca", 3: "Marimelena", 4: "Guasabacoa", 5: "Atares"}
UMBRAL_T, EQ_MAX, CONTROL_MAX = 7.0, 0.01, 0.05  # protocolo: T_i < 7 d; 1 %/d; 5 %


def caudales(dirm):
    """Caudal medio de cada rio (m3/s), de vsource.th."""
    return np.loadtxt(Path(dirm) / "vsource.th", ndmin=2)[:, 1:].mean(0)


def metricas(t, eta, C, S, prof, M, Q):
    """t (d), eta (tiempo, nodo), C (tiempo, nodo, nivel, rio), S (tiempo, nodo, nivel), prof (nodo), Q (rio, m3/s).
    Medias verticales con niveles S casi uniformes (como posproceso.py)."""
    z, area = M["zona"], M["area"]; b = z > 0
    vol = np.maximum(prof[None] + eta, 0.0) * area[None]                              # (tiempo, nodo)
    Cm = C.mean(2)                                                                    # (tiempo, nodo, rio)
    Mi = np.einsum("tnr,tn->tr", Cm[:, b], vol[:, b])                                # m3 de agua del rio i en la bahia, por instante
    d10 = t > t[-1] - 10
    r = dict(dias=float(t[-1]), rios=RIOS, V_hm3=float(vol[:, b].sum(1).mean() / 1e6), Q_m3s=[float(q) for q in Q],
             M_hm3=[float(m / 1e6) for m in Mi.mean(0)], T_d=[float(m / q / 86400) for m, q in zip(Mi.mean(0), Q)])
    r["deriva_rel_por_d"] = [float(np.polyfit(t[d10], Mi[d10, i], 1)[0] / Mi[d10, i].mean()) for i in range(len(RIOS))]
    r["equilibrio"] = [bool(abs(x) <= EQ_MAX) for x in r["deriva_rel_por_d"]]
    for k, nom in ZONAS.items():
        s = z == k; vz = vol[:, s]
        r[f"frac_zona_{nom}"] = [float((Cm[:, s, i] * vz).sum(1).mean() / vz.sum(1).mean()) for i in range(len(RIOS))]   # agua del rio i / agua de la zona
        r[f"reparto_{nom}"] = [float((Cm[:, s, i] * vz).sum(1).mean() / Mi[:, i].mean()) for i in range(len(RIOS))]       # parte de M_i que esta en la zona
        for niv, nn in ((-1, "sup"), (0, "fondo")):                                  # media ponderada por area en superficie y fondo
            r[f"frac_zona_{nom}_{nn}"] = [float((C[:, s, niv, i] * area[s]).sum(1).mean() / area[s].sum()) for i in range(len(RIOS))]
    Vf = (np.clip(1 - S / S_MAR, 0, 1).mean(2)[:, b] * vol[:, b]).sum(1)              # inventario de agua dulce por salinidad
    r["control_dif_rel"] = float(abs(Mi.sum(1).mean() - Vf.mean()) / Vf.mean()); r["control_ok"] = bool(r["control_dif_rel"] < CONTROL_MAX)
    mapas = {f"sup_{i}": C[:, :, -1, i].mean(0).astype(np.float32) for i in range(len(RIOS))}
    mapas.update({f"fondo_{i}": C[:, :, 0, i].mean(0).astype(np.float32) for i in range(len(RIOS))})
    return r, mapas


def reglas(r):
    """R1-R4 del protocolo en un caso."""
    sob = lambda nom: sum(r[f"frac_zona_{nom}"])                                      # agua de los tres rios / agua de la zona
    rep = lambda i, noms: sum(r[f"reparto_{n}"][i] for n in noms)
    return {"R1 T_i < 7 d en los tres rios": all(x < UMBRAL_T for x in r["T_d"]),
            "R2 agua de rios: menos fraccion en Atares que en Guasabacoa": sob("Atares") < sob("Guasabacoa"),
            "R3 Luyano y Martin Perez: > 50 % de M_i en Guasabacoa y cuenca": all(rep(i, ("Guasabacoa", "cuenca")) > 0.5 for i in (0, 1)),
            "R4 Tadeo: > 50 % de M_Tadeo en Marimelena": r["reparto_Marimelena"][2] > 0.5}


def clasifica(dirc):
    casos = sorted(Path(dirc).glob("m000[0-3]/trazadores.json")); R = {c.parent.name: json.loads(c.read_text()) for c in casos}
    if len(R) < 4: print(f"faltan casos: {len(R)}/4 (m0000..m0003)")
    malos = [k for k, r in R.items() if not r["control_ok"]]
    if malos: print(f"!! control de la suma > {CONTROL_MAX:.0%} en {malos}: no se usa ningun resultado hasta entenderlo")
    tabla = {k: reglas(r) for k, r in R.items()}
    for nom in next(iter(tabla.values())):
        falla = [k for k, v in tabla.items() if not v[nom]]
        print(f"{nom}: {'ROBUSTA' if not falla and len(R) == 4 else 'FRAGIL' if falla else 'incompleta'}"
              + (f" (falla en {', '.join(falla)})" if falla else ""))
    return tabla


def carga(dirm):
    from netCDF4 import Dataset
    out = Path(dirm) / "outputs"; n = max(int(f.stem.split("_")[-1]) for f in out.glob("salinity_*.nc"))
    eta, S, C = [], [], []
    for k in range(n - VENTANA + 1, n + 1):
        with Dataset(out / f"out2d_{k}.nc") as d:
            eta.append(np.asarray(d["elevation"][:], np.float32)); prof = np.asarray(d["depth"][:]); t = np.asarray(d["time"][:], float)
        with Dataset(out / f"salinity_{k}.nc") as d: S.append(np.asarray(d["salinity"][:], np.float32))
        C.append(np.stack([np.asarray(Dataset(out / f"GEN_{i + 1}_{k}.nc")[f"GEN_{i + 1}"][:], np.float32) for i in range(len(RIOS))], -1))
    return np.concatenate([t / 86400 for t in [np.asarray(x) for x in []]] or [np.arange(0)]) if False else (
        np.concatenate(eta), np.concatenate(C), np.concatenate(S), prof, n)


def prueba(M):
    """Solucion conocida: en la bahia C_i = f_i uniforme (f = 0,02 / 0,01 / 0,005) y S = 36 (1 - sum f): M_i = f_i V,
    T_i = f_i V / Q_i, control exacto, reparto de M_i proporcional al volumen de cada zona; M creciente -> sin equilibrio."""
    n = len(M["zona"]); b = M["zona"] > 0; nt = 180; t = 90 + np.arange(nt) / 6
    f = np.array([0.02, 0.01, 0.005]); eta = np.zeros((nt, n)); prof = np.full(n, 8.0); Q = np.array([1.33, 0.72, 0.09])
    C = np.zeros((nt, n, 4, 3), np.float32); C[:, b] = f
    S = np.full((nt, n, 4), S_MAR, np.float32); S[:, b] = S_MAR * (1 - f.sum())
    r, mapas = metricas(t, eta, C, S, prof, M, Q); V = 8.0 * M["area"][b].sum()
    assert np.allclose(r["T_d"], f * V / Q / 86400, rtol=1e-5) and r["control_dif_rel"] < 1e-5 and r["control_ok"], r
    assert all(r["equilibrio"]) and np.allclose(r["frac_zona_Atares"], f, rtol=1e-5) and np.allclose(r["frac_zona_canal_sup"], f, rtol=1e-5)
    vz = {k: 8.0 * M["area"][M["zona"] == k].sum() for k in ZONAS}
    assert np.allclose(r["reparto_Marimelena"], vz[3] / V, rtol=1e-5) and abs(sum(r[f"reparto_{n}"][0] for n in ZONAS.values()) - 1) < 1e-6
    r2, _ = metricas(t, eta, C * (1 + 0.05 * (t - 90))[None, :, None, None].transpose(1, 0, 2, 3)[:, :, :, :].astype(np.float32), S, prof, M, Q)
    assert not any(r2["equilibrio"]), r2["deriva_rel_por_d"]                                  # crece ~ 5 %/d de la media: sin equilibrio
    r3, _ = metricas(t, eta, C * 0.5, S, prof, M, Q); assert not r3["control_ok"]            # inventario de rios 50 % del agua dulce
    assert reglas(r)["R2 agua de rios: menos fraccion en Atares que en Guasabacoa"] is False   # iguales: no es "menos"
    print("autoprueba trazadores: ok")


if __name__ == "__main__":
    R = Path(__file__).resolve().parent.parent
    M = dict(np.load(R / "datos" / "conjunto" / "posproceso_malla.npz"))
    if sys.argv[1] == "--prueba": prueba(M); sys.exit()
    if sys.argv[1] == "--clasifica": clasifica(sys.argv[2]); sys.exit()
    dirm = Path(sys.argv[1]); eta, C, S, prof, n = carga(dirm)
    t = np.arange(len(eta)) / 6.0 + (n - VENTANA)                      # dias, 6 salidas por dia (4 h)
    r, mapas = metricas(t, eta, C, S, prof, M, caudales(dirm))
    (dirm / "trazadores.json").write_text(json.dumps(r, indent=1)); np.savez_compressed(dirm / "trazadores.npz", **mapas)
    print(json.dumps({k: r[k] for k in ("T_d", "M_hm3", "equilibrio", "control_dif_rel", "control_ok")}), reglas(r))
