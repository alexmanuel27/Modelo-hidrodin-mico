#!/usr/bin/env python3
"""Series del modelo en las estaciones de JICA (fig. 4.25) para la comparacion de docs/protocolo_jica_observaciones.md (A1 y A2).
Corre en el cluster sobre un miembro con campos completos (outputs/*.nc; solo numpy + netCDF4):
  python scripts/jica_extrae_estaciones.py <carpeta del miembro> <dia_ini> <dia_fin> [nombre.npz]   -> <miembro>/jica_estaciones.npz (o el nombre dado, 22-nov)
      (conjunto m0000-m0002: 91 120; runs/termico, diciembre: 335 365; los dias cuentan desde el inicio de la corrida)
  python scripts/jica_extrae_estaciones.py --prueba                               -> autoprueba (vgrid, niveles verticales, fases)
Niveles (A2): sup = 0,5 m bajo la superficie; m5 y m10 = 5 y 10 m bajo la superficie; mid = mitad de la columna; fondo = 1 m sobre el fondo.
Estaciones: nodo mas cercano (posicion principal) y media de los nodos de la bahia a <= 300 m (sensibilidad), de
datos/observaciones/jica2004_estaciones_utm.csv. Ademas, la media de los nodos del canal (zona 1) de la velocidad a lo largo del canal
(> 0 hacia dentro) y la salinidad por nivel, solo para describir (a). No se aplica ningun umbral aqui.
Las corridas del conjunto NO guardan velocidad 3D (iof_hydro(16) es la velocidad promediada en la vertical, la 3D es iof_hydro(26) = 0; (25) es zCoordinates): sin
horizontalVelX/Y_N.nc, V_n, V_r y canal_un salen NaN y solo se obtiene la salinidad por nivel, que es lo que usa (b)."""
import csv, sys, warnings
from pathlib import Path
import numpy as np

warnings.filterwarnings("ignore", "Mean of empty slice")      # media de una estacion sin columna valida en ese instante: NaN
RAIZ = Path(__file__).resolve().parent.parent
NIVELES = ("sup", "m5", "m10", "mid", "fondo"); H_MIN = 2.0; R_SENS = 300.0
PERIODOS_H = (12.4206012, 12.0, 12.6583482, 23.9344697, 25.8193417)            # M2, S2, N2, K1, O1


def lee_vgrid(p):
    L = [l.split("!")[0].split() for l in Path(p).read_text().split("\n")]; L = [l for l in L if l]
    assert L[0][0] == "2", "solo ivcor = 2 (SZ con niveles S)"
    nvrt, kz = int(L[1][0]), int(L[1][1]); i = [j for j, l in enumerate(L) if l[0] == "S"][0]
    return (np.array([float(l[1]) for l in L[i + 2:i + 2 + nvrt - kz + 1]]), *map(float, L[i + 1][:3]))


def zcor(h, eta, vg):
    """z (tiempo, nodo, nivel) de los niveles S de SCHISM (ivcor = 2): h (nodo), eta (tiempo, nodo)."""
    sig, hc, tb, tf = vg
    cs = (1 - tb) * np.sinh(tf * sig) / np.sinh(tf) + tb * (np.tanh(tf * (sig + .5)) - np.tanh(tf * .5)) / (2 * np.tanh(tf * .5))
    e = eta[..., None]; H = h[None, :, None]
    return np.where(H <= hc, sig * (H + e) + e, e * (1 + sig) + hc * sig + (H - hc) * cs)


def a_nivel(z, f, zt):
    """f (tiempo, nodo, nivel) interpolado en la cota zt (tiempo, nodo); NaN fuera de la columna."""
    k = np.clip((z < zt[..., None]).sum(-1), 1, z.shape[-1] - 1)[..., None]
    z0, z1, f0, f1 = (np.take_along_axis(a, k + d, -1)[..., 0] for a in (z, f) for d in (-1, 0))
    o = f0 + (zt - z0) / np.where(z1 > z0, z1 - z0, 1) * (f1 - f0)
    o[(zt < z[..., 0] - 1e-6) | (zt > z[..., -1] + 1e-6)] = np.nan
    return o


def en_niveles(z, F, h, eta):
    """(tiempo, nodo, 5) en los niveles NIVELES; NaN si la columna tiene menos de H_MIN m."""
    H = h[None] + eta
    zt = np.stack([eta - .5, eta - 5, eta - 10, eta - .5 * H, -h[None] + 1.0 + 0 * eta], -1)
    o = np.stack([a_nivel(z, F, zt[..., j]) for j in range(5)], -1); o[H < H_MIN] = np.nan
    return o


def fases(t_d, eta, ancho_h=1.0):
    """Ajuste armonico (M2, S2, N2, K1, O1) a la elevacion media de la bahia; sobre la curva continua, creciente = a <= ancho_h del instante
    de maxima velocidad de subida y bajamar = a <= ancho_h del minimo. Devuelve (mascara creciente, mascara bajamar)."""
    w = 2 * np.pi / (np.array(PERIODOS_H) / 24)
    dis = lambda t: np.column_stack([np.ones_like(t), *[f(a * t) for a in w for f in (np.cos, np.sin)]])
    c = np.linalg.lstsq(dis(t_d), eta, rcond=None)[0]
    tf = np.arange(t_d.min(), t_d.max(), 1 / 1440); ef = dis(tf) @ c; r = np.gradient(ef, tf)
    pk_r = np.where((r[1:-1] > r[:-2]) & (r[1:-1] >= r[2:]))[0] + 1; pk_m = np.where((ef[1:-1] < ef[:-2]) & (ef[1:-1] <= ef[2:]))[0] + 1
    cerca = lambda pk: np.abs(t_d[:, None] - tf[pk][None, :]).min(1) <= ancho_h / 24
    return cerca(pk_r), cerca(pk_m)


def prueba():
    vg = lee_vgrid(RAIZ / "runs" / "conjunto" / "m0000" / "vgrid.in"); sig = vg[0]
    assert len(sig) == 16 and sig[0] == -1 and sig[-1] == 0 and vg[1:] == (5.0, 0.0, 1e-4), vg
    h, eta = np.array([8.0, 14.0, 1.0]), np.full((2, 3), 0.5); z = zcor(h, eta, vg)
    assert np.allclose(z[:, :, -1], 0.5) and np.allclose(z[0, :, 0], -h) and (np.diff(z, axis=-1) > 0).all()
    o = en_niveles(z, z.copy(), h, eta)                                   # campo F = z: el resultado es la cota pedida
    assert np.allclose(o[0, 0], [0.0, -4.5, np.nan, 0.5 - .5 * 8.5, -7.0], equal_nan=True), o[0, 0]      # estacion de 8 m, eta = 0,5
    assert np.isnan(o[0, 0, 2]) and not np.isnan(o[0, 1, 2]) and np.isnan(o[0, 2]).all()               # 10 m no existe en 8 m; si en 14 m; 1,5 m no vale
    t = np.arange(0, 30, 1 / 6); T = PERIODOS_H[0] / 24; eta = 0.3 * np.cos(2 * np.pi * t / T) + 0.1 * np.cos(2 * np.pi * t / (PERIODOS_H[3] / 24) + 1)
    cr, ba = fases(t, eta); ef = 0.3 * np.cos(2 * np.pi * t / T)
    assert cr.sum() >= 8 and ba.sum() >= 8 and not (cr & ba).any()
    assert np.sin(2 * np.pi * t[cr] / T).mean() < -0.3 and np.cos(2 * np.pi * t[ba] / T).mean() < -0.8, (ef[cr].mean(), ef[ba].mean())    # creciente: eta subiendo; bajamar: eta minima
    print("autoprueba jica_extrae_estaciones: ok")


def extrae(dirm, d0, d1, nombre="jica_estaciones.npz"):
    from netCDF4 import Dataset
    dirm = Path(dirm); out = dirm / "outputs"; num = lambda p: int(p.stem.split("_")[-1])
    est = list(csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_estaciones_utm.csv")))
    L = (RAIZ / "datos" / "malla" / "hgrid.gr3").read_text().split("\n"); nn = int(L[1].split()[1]); xy = np.array([l.split()[1:3] for l in L[2:2 + nn]], float)
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); zona, area = M["zona"], M["area"]; sd = M["sec_dir"]
    n1 = np.array([int(r["nodo"]) - 1 for r in est]); bahia = np.where(zona > 0)[0]
    sets = [bahia[np.hypot(xy[bahia, 0] - float(r["E_utm17n"]), xy[bahia, 1] - float(r["N_utm17n"])) <= R_SENS] for r in est]
    canal = np.where(zona == 1)[0]; uni = np.unique(np.concatenate([n1, canal, *sets])); pos = {int(n): i for i, n in enumerate(uni)}
    dzs = []                                                                  # F2 (protocolo_salinidad_superficie.md): max |zCoordinates guardada - zcor reconstruida|
    vg = lee_vgrid(dirm / "vgrid.in"); S_, ns = [], len(est); salida = {k: [] for k in ("t", "eta_bay", "S_n", "V_n", "S_r", "V_r", "canal_un", "canal_S")}
    for f2 in sorted(out.glob("out2d_*.nc"), key=num):
        n = num(f2)
        try:
            with Dataset(f2) as d:
                t = np.asarray(d["time"][:], float) / 86400; sel = np.where((t >= d0) & (t <= d1))[0]
                if not len(sel): continue
                eta_all = np.asarray(d["elevation"][sel], np.float32); h = np.asarray(d["depth"][:], float)[uni]
            def campo(pref, var, opcional=False):
                if opcional and not (out / f"{pref}_{n}.nc").exists(): return None
                with Dataset(out / f"{pref}_{n}.nc") as d: return np.asarray(d[var][sel][:, uni], np.float32)
            S, U, V = campo("salinity", "salinity"), campo("horizontalVelX", "horizontalVelX", True), campo("horizontalVelY", "horizontalVelY", True)
            zr = campo("zCoordinates", "zCoordinates", True)                     # cotas reales (iof_hydro(25) = 1), si se guardaron
            if U is None or V is None: U = V = np.full_like(S, np.nan)           # sin velocidad 3D (iof_hydro(26) = 0): V_*, canal_un = NaN; (b) solo usa S
        except (OSError, IndexError, KeyError) as e:
            print("dia", n, "no legible, se omite:", e); continue
        eta = eta_all[:, uni].astype(float); z = zcor(h, eta, vg)
        if zr is not None: dzs.append(float(np.abs(np.where((np.abs(zr) < 1e4) & ((h + eta) > 0.1)[:, :, None], zr - z, 0.0)).max()))
        Sl, Ul, Vl = (en_niveles(z, a.astype(float), h, eta) for a in (S, U, V)); Vm = np.hypot(Ul, Vl); un = Ul * sd[0] + Vl * sd[1]
        salida["t"].append(t[sel]); salida["eta_bay"].append((eta_all[:, bahia] * area[bahia]).sum(1) / area[bahia].sum())
        salida["S_n"].append(Sl[:, [pos[int(i)] for i in n1]]); salida["V_n"].append(Vm[:, [pos[int(i)] for i in n1]])
        salida["S_r"].append(np.stack([np.nanmean(Sl[:, [pos[int(i)] for i in s]], 1) for s in sets], 1))
        salida["V_r"].append(np.stack([np.nanmean(Vm[:, [pos[int(i)] for i in s]], 1) for s in sets], 1))
        ic = [pos[int(i)] for i in canal]; salida["canal_un"].append(np.nanmean(un[:, ic], 1)); salida["canal_S"].append(np.nanmean(Sl[:, ic], 1))
    assert salida["t"], f"ningun dia entre {d0} y {d1} en {out}"
    np.savez_compressed(dirm / nombre, niveles=np.array(NIVELES), estaciones=np.array([r["estacion"] for r in est]),
                        prof_nodo_m=np.array([float(r["prof_hgrid_m"]) for r in est]), dias_ventana=np.array([d0, d1]), dz_max=np.array(max(dzs) if dzs else np.nan),
                        **{k: np.concatenate(v) for k, v in salida.items()})
    print(dirm, "->", dirm / nombre, len(np.concatenate(salida["t"])), "muestras;", f"max |z guardada - z reconstruida| = {max(dzs):.4f} m" if dzs else "sin zCoordinates guardada")


if __name__ == "__main__":
    prueba() if sys.argv[1:] == ["--prueba"] else extrae(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), *sys.argv[4:5])
