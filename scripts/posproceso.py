#!/usr/bin/env python3
"""Posproceso de un miembro del conjunto (corre en el cluster al terminar SCHISM; solo numpy + netCDF4).
Uso: python posproceso.py <carpeta del miembro> [datos/conjunto/posproceso_malla.npz]
     python posproceso.py --prueba      (autoprueba con campos sinteticos de solucion conocida)
Escribe <miembro>/resumen.json (escalares) y <miembro>/resumen.npz (series, mapas, rejilla Sentinel-2).
C = AGE_1 = fraccion de agua llegada del mar (1 fuera de la bahia, 0 dentro al inicio); edad = AGE_2 / C.
Salidas (plan, sec. 18): (a) edad y C por zona + mapas de superficie y fondo; (b) fraccion de volumen con
edad > 30 d; (d) caudal neto y bruto por la seccion del canal; (f) superficie a las 16:00 UTC en la rejilla S2.
(c) Sobol y (e) particulas se hacen fuera. Ventana de resumen: los ultimos 30 dias."""
import json, sys
from pathlib import Path
import numpy as np

ZONAS = {1: "canal", 2: "cuenca", 3: "Marimelena", 4: "Guasabacoa", 5: "Atares"}
VENTANA, UMBRAL_EDAD, HORA_S2 = 30.0, 30.0, 16


def resumen(t, C, A, eta, u, v, prof, M):
    """t (s), C y A (tiempo, nodo, nivel; A puede ser None), eta/u/v (tiempo, nodo), prof (nodo), M = npz de la malla."""
    dias = t / 86400.0; ult = dias > dias[-1] - VENTANA
    H = np.maximum(prof[None] + eta, 0.0); vol = H * M["area"][None]          # volumen por nodo y tiempo
    Cm = C.mean(2)                                                            # niveles S casi uniformes: media = media vertical
    r = dict(dias=float(dias[-1]), nan=int(np.isnan(eta).sum() + np.isnan(C).sum()), vmax=float(np.nanmax(np.hypot(u, v))))
    z = M["zona"]; bahia = z > 0
    r["marea_bahia_cm"] = float(np.ptp(eta[dias > dias[-1] - 25 / 24][:, bahia].mean(1)) / 2 * 100)
    serie = {}
    for k, nom in ZONAS.items():
        s = z == k; c = (Cm[:, s] * vol[:, s]).sum(1) / vol[:, s].sum(1); serie[nom] = c.astype(np.float32)
        bajo = np.where(1 - c <= np.exp(-1))[0]                              # renovacion e-folding de lo que habia
        r[f"renovacion_d_{nom}"] = float(dias[bajo[0]]) if len(bajo) else float("nan")
        r[f"C_{nom}"] = float(c[ult].mean())
    sb = bahia; cb = (Cm[:, sb] * vol[:, sb]).sum(1) / vol[:, sb].sum(1); serie["bahia"] = cb.astype(np.float32)
    bajo = np.where(1 - cb <= np.exp(-1))[0]; r["renovacion_d_bahia"] = float(dias[bajo[0]]) if len(bajo) else float("nan")
    mapas = dict(C_sup=C[ult, :, -1].mean(0), C_fondo=C[ult, :, 0].mean(0))
    if A is not None:
        edad = np.where(C > 1e-3, A / np.maximum(C, 1e-3), np.nan)          # edad en las unidades de SCHISM (dias)
        em = np.nanmean(edad, 2); e30 = np.nanmean(em[ult], 0); w = np.nanmean(vol[ult], 0)
        mapas.update(edad_sup=np.nanmean(edad[ult, :, -1], 0), edad_fondo=np.nanmean(edad[ult, :, 0], 0))
        for k, nom in list(ZONAS.items()) + [(None, "bahia")]:
            s = bahia if k is None else z == k; e, ww = e30[s], w[s]; ok = np.isfinite(e)
            r[f"edad_media_d_{nom}"] = float((e[ok] * ww[ok]).sum() / ww[ok].sum()) if ok.any() else float("nan")
            r[f"edad_p10_p50_p90_{nom}"] = [float(q) for q in np.nanpercentile(e, [10, 50, 90])] if ok.any() else []
            r[f"frac_vol_edad_mayor_{UMBRAL_EDAD:g}d_{nom}"] = float(ww[ok & (e > UMBRAL_EDAD)].sum() / ww[ok].sum()) if ok.any() else float("nan")
    # (d) seccion del canal: Q > 0 hacia dentro de la bahia
    i, wt = M["sec_i"], M["sec_w"]; un = u * M["sec_dir"][0] + v * M["sec_dir"][1]
    Q = ((un[:, i] * wt[None]).sum(2) * (H[:, i] * wt[None]).sum(2)).sum(1) * float(M["sec_dn"])
    r["Q_neto_m3s"], r["Q_bruto_m3s"] = float(Q[ult].mean()), float(np.abs(Q[ult]).mean())
    # (f) superficie a las 16:00 UTC en la rejilla Sentinel-2
    h = np.round((t % 86400) / 3600).astype(int); sel = np.where(ult & (h == HORA_S2))[0]
    si, sw, fuera = M["s2_i"], M["s2_w"], M["s2_i"][:, 0] < 0
    rej = lambda campo: np.where(fuera, np.nan, (campo[si] * sw).sum(1)).reshape(M["s2_forma"]).astype(np.float32)
    s2 = dict(s2_C=np.array([rej(C[k, :, -1]) for k in sel]), s2_dias=dias[sel].astype(np.float32))
    if A is not None: s2["s2_edad"] = np.array([rej(np.nan_to_num(edad[k, :, -1], nan=0.0)) for k in sel])
    r["s2_imagenes"] = len(sel)
    npz = dict(dias=dias.astype(np.float32), Q=Q.astype(np.float32), **{f"serie_{k}": s for k, s in serie.items()},
               **{k: m.astype(np.float32) for k, m in mapas.items()}, **s2)
    return r, npz


def prueba(M):
    """Bahia que se renueva con e-folding de 20 d, edad uniforme de 5 d y 0,1 m/s hacia dentro por el canal."""
    n, nv = len(M["zona"]), 16; t = np.arange(1, 91 * 6) * 4 * 3600.0; dias = t / 86400
    C = np.where(M["zona"][None, :, None] > 0, (1 - np.exp(-dias / 20))[:, None, None], 1.0) * np.ones((1, n, nv), np.float32)
    u, v = (np.full((len(t), n), 0.1 * M["sec_dir"][k]) for k in (0, 1))
    r, npz = resumen(t, C, 5 * C, np.zeros((len(t), n)), u, v, np.full(n, 8.0), M)
    assert abs(r["renovacion_d_bahia"] - 20) < 0.2 and abs(r["edad_media_d_bahia"] - 5) < 1e-3, r
    assert abs(r["Q_neto_m3s"] - 0.1 * 8 * len(M["sec_i"]) * 10) < 1e-6 and r["s2_imagenes"] == 30 and npz["s2_C"].shape[0] == 30
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
    return dict(t=cat("out2d", "time").astype(float), C=cat("AGE_1", "AGE_1"), A=cat("AGE_2", "AGE_2"),
                eta=cat("out2d", "elevation"), u=cat("out2d", "depthAverageVelX"), v=cat("out2d", "depthAverageVelY"), prof=prof)


if __name__ == "__main__":
    R = Path(__file__).resolve().parent.parent
    M = dict(np.load(sys.argv[2] if len(sys.argv) > 2 else R / "datos" / "conjunto" / "posproceso_malla.npz"))
    if sys.argv[1] == "--prueba": prueba(M); sys.exit()
    dirm = Path(sys.argv[1])
    d = lee(dirm); r, npz = resumen(d["t"], d["C"], d["A"], d["eta"], d["u"], d["v"], d["prof"], M)
    np.savez_compressed(dirm / "resumen.npz", **npz)
    (dirm / "resumen.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: v for k, v in r.items() if not k.startswith("edad_p")}, indent=None)[:1500])
