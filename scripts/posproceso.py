#!/usr/bin/env python3
"""Posproceso de un miembro del conjunto (corre en el cluster al terminar SCHISM; solo numpy + netCDF4).
Uso: python posproceso.py <carpeta del miembro> [datos/conjunto/posproceso_malla.npz]
     python posproceso.py --prueba      (autoprueba con campos sinteticos de solucion conocida)
Escribe <miembro>/resumen.json (escalares) y <miembro>/resumen.npz (series, mapas, rejilla Sentinel-2).
AGE_1 de SCHISM ya es la EDAD en dias (schism_step.F90: alfa/C/86400): tiempo desde que el agua salio del mar
(fuera de la bahia la edad se mantiene en 0; dentro empieza en 0 el dia 0).
Salidas (plan, sec. 18): (a) edad por zona + mapas de superficie y fondo; (b) fraccion de volumen con
edad > 30 d; (d) caudal neto y bruto por la seccion del canal; (f) edad en superficie a las 16:00 UTC en la
rejilla S2. (c) Sobol y (e) particulas se hacen fuera. Ventana de resumen: los ultimos 30 dias."""
import json, sys
from pathlib import Path
import numpy as np

ZONAS = {1: "canal", 2: "cuenca", 3: "Marimelena", 4: "Guasabacoa", 5: "Atares"}
VENTANA, UMBRAL_EDAD, HORA_S2 = 30.0, 30.0, 16


def resumen(t, E, eta, u, v, prof, M):
    """t (s), E = edad en dias (tiempo, nodo, nivel), eta/u/v (tiempo, nodo), prof (nodo), M = npz de la malla."""
    dias = t / 86400.0; ult = dias > dias[-1] - VENTANA
    H = np.maximum(prof[None] + eta, 0.0); vol = H * M["area"][None]          # volumen por nodo y tiempo
    Em = E.mean(2)                                                            # niveles S casi uniformes: media = media vertical
    z = M["zona"]; bahia = z > 0; spd = np.hypot(u, v)
    r = dict(dias=float(dias[-1]), nan=int(np.isnan(eta).sum() + np.isnan(E).sum()),
             vmax=float(np.nanmax(spd)), vmax_nodo=int(np.nanargmax(np.nanmax(spd, 0))) + 1,   # numero de nodo en hgrid.gr3
             vmax_bahia=float(np.nanmax(spd[:, bahia])),
             vmax_bahia_nodo=int(np.where(bahia)[0][np.nanargmax(np.nanmax(spd[:, bahia], 0))]) + 1)
    r["marea_bahia_cm"] = float(np.ptp(eta[dias > dias[-1] - 25 / 24][:, bahia].mean(1)) / 2 * 100)
    serie, e30, w = {}, Em[ult].mean(0), vol[ult].mean(0)
    for k, nom in list(ZONAS.items()) + [(None, "bahia")]:
        s = bahia if k is None else z == k
        serie[nom] = ((Em[:, s] * vol[:, s]).sum(1) / vol[:, s].sum(1)).astype(np.float32)
        e, ww = e30[s], w[s]
        r[f"edad_media_d_{nom}"] = float((e * ww).sum() / ww.sum())
        r[f"edad_p10_p50_p90_{nom}"] = [float(q) for q in np.percentile(e, [10, 50, 90])]
        r[f"frac_vol_edad_mayor_{UMBRAL_EDAD:g}d_{nom}"] = float(ww[e > UMBRAL_EDAD].sum() / ww.sum())
    # equilibrio: cuanto crece aun la edad media de la bahia en los ultimos 10 dias (d por dia; ~0 = estacionario)
    d10 = dias > dias[-1] - 10
    r["deriva_edad_bahia_d_por_d"] = float(np.polyfit(dias[d10], serie["bahia"][d10], 1)[0])
    # extrapolacion a equilibrio con A(t) -> A_inf (1 - exp(-t/tau)): dA/dt = (A_inf - A)/tau, regresion lineal
    # sobre medias diarias de los ultimos 45 d. shortcut: supone una sola escala de tiempo; validar con corridas largas.
    nd = int(dias[-1]); dd = np.floor(dias - 1e-9).astype(int)
    for nom, se in serie.items():
        md = np.array([se[dd == k].mean() for k in range(nd)])[-46:]
        m, c = np.polyfit(0.5 * (md[1:] + md[:-1]), np.diff(md), 1)
        r[f"edad_equilibrio_d_{nom}"] = float(-c / m) if m < 0 else float("nan")
        r[f"tau_d_{nom}"] = float(-1 / m) if m < 0 else float("nan")
    mapas = dict(edad_sup=E[ult, :, -1].mean(0), edad_fondo=E[ult, :, 0].mean(0))
    # (d) seccion del canal: Q > 0 hacia dentro de la bahia
    i, wt = M["sec_i"], M["sec_w"]; un = u * M["sec_dir"][0] + v * M["sec_dir"][1]
    Q = ((un[:, i] * wt[None]).sum(2) * (H[:, i] * wt[None]).sum(2)).sum(1) * float(M["sec_dn"])
    r["Q_neto_m3s"], r["Q_bruto_m3s"] = float(Q[ult].mean()), float(np.abs(Q[ult]).mean())
    # (f) edad en superficie a las 16:00 UTC en la rejilla Sentinel-2
    h = np.round((t % 86400) / 3600).astype(int); sel = np.where(ult & (h == HORA_S2))[0]
    si, sw, fuera = M["s2_i"], M["s2_w"], M["s2_i"][:, 0] < 0
    rej = lambda campo: np.where(fuera, np.nan, (campo[si] * sw).sum(1)).reshape(M["s2_forma"]).astype(np.float32)
    s2 = dict(s2_edad=np.array([rej(E[k, :, -1]) for k in sel]), s2_dias=dias[sel].astype(np.float32))
    r["s2_imagenes"] = len(sel)
    npz = dict(dias=dias.astype(np.float32), Q=Q.astype(np.float32), **{f"serie_{k}": s for k, s in serie.items()},
               **{k: m.astype(np.float32) for k, m in mapas.items()}, **s2)
    return r, npz


def prueba(M):
    """Edad que crece como tau*(1-exp(-t/tau)) con tau = 20 d dentro de la bahia y 0 fuera; 0,1 m/s hacia dentro."""
    n, nv = len(M["zona"]), 16; t = np.arange(1, 91 * 6) * 4 * 3600.0; dias = t / 86400
    E = np.where(M["zona"][None, :, None] > 0, (20 * (1 - np.exp(-dias / 20)))[:, None, None], 0.0) * np.ones((1, n, nv), np.float32)
    u, v = (np.full((len(t), n), 0.1 * M["sec_dir"][k]) for k in (0, 1))
    r, npz = resumen(t, E, np.zeros((len(t), n)), u, v, np.full(n, 8.0), M)
    esperado = np.mean(20 * (1 - np.exp(-dias[dias > dias[-1] - 30] / 20)))
    assert abs(r["edad_media_d_bahia"] - esperado) < 1e-3 and r["frac_vol_edad_mayor_30d_bahia"] == 0, r
    assert abs(r["Q_neto_m3s"] - 0.1 * 8 * len(M["sec_i"]) * 10) < 1e-6 and r["s2_imagenes"] == 30 and npz["s2_edad"].shape[0] == 30
    assert 0 < r["deriva_edad_bahia_d_por_d"] < 0.1
    assert abs(r["edad_equilibrio_d_bahia"] - 20) < 1.0 and abs(r["tau_d_bahia"] - 20) < 1.0, (r["edad_equilibrio_d_bahia"], r["tau_d_bahia"])
    print("autoprueba posproceso: ok")


def lee(dirm):
    from netCDF4 import Dataset
    out = Path(dirm) / "outputs"
    num = lambda p: int(p.stem.split("_")[-1])
    def legible(f):
        try: Dataset(f).close(); return True
        except OSError: return False
    ndias = sum(1 for _ in out.glob("out2d_*.nc"))
    while ndias and not (legible(out / f"out2d_{ndias}.nc") and (not (out / "AGE_1_1.nc").exists() or legible(out / f"AGE_1_{ndias}.nc"))):
        ndias -= 1                                                            # corrida en curso: solo los dias completos
    def cat(pref, var):
        fs = sorted(out.glob(f"{pref}_*.nc"), key=num)
        if fs and num(fs[-1]) > ndias: fs = fs[:ndias]                        # el ultimo dia puede estar a medio escribir
        return np.concatenate([np.asarray(Dataset(f)[var][:], dtype=np.float32) for f in fs]) if fs else None
    f0 = sorted(out.glob("out2d_*.nc"), key=num)[0]
    with Dataset(f0) as d: prof = np.asarray(d["depth"][:])
    return dict(t=cat("out2d", "time").astype(float), E=cat("AGE_1", "AGE_1"),
                eta=cat("out2d", "elevation"), u=cat("out2d", "depthAverageVelX"), v=cat("out2d", "depthAverageVelY"), prof=prof)


if __name__ == "__main__":
    R = Path(__file__).resolve().parent.parent
    M = dict(np.load(sys.argv[2] if len(sys.argv) > 2 else R / "datos" / "conjunto" / "posproceso_malla.npz"))
    if sys.argv[1] == "--prueba": prueba(M); sys.exit()
    dirm = Path(sys.argv[1])
    d = lee(dirm); r, npz = resumen(d["t"], d["E"], d["eta"], d["u"], d["v"], d["prof"], M)
    np.savez_compressed(dirm / "resumen.npz", **npz)
    (dirm / "resumen.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if not k.startswith("edad_p")}))
