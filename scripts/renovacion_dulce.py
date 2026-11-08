#!/usr/bin/env python3
"""Tiempo de renovacion del agua dulce de la bahia por el metodo de la fraccion de agua dulce (Dyer 1997):
T_f = V_f / Q_rios, con V_f = suma en la bahia de (1 - S/S_MAR) * H * area (media de los niveles S, casi uniformes),
promediado en los ultimos 30 d. Es la magnitud comparable al "tiempo de retencion del agua dulce ~4 meses" de JICA
(2004, p. R-7). La edad del modelo no lo es: cuenta el agua de los rios como agua nueva (msource.th, AGE = 1).
Necesita salinity_*.nc y out2d_*.nc: solo los miembros que conservan los campos (GUARDAR de conjunto.py).
Uso: python renovacion_dulce.py <miembro> [malla.npz]      python renovacion_dulce.py --prueba"""
import json, sys
from pathlib import Path
import numpy as np

VENTANA, S_MAR = 30, 36.0     # como posproceso.py


def caudal_rios(dirm):
    """Caudal total medio de los rios en vsource.th (m3/s)."""
    a = np.loadtxt(Path(dirm) / "vsource.th", ndmin=2)
    return float(a[:, 1:].sum(1).mean())


def renovacion(eta, S, prof, M, Q):
    """eta (tiempo, nodo), S (tiempo, nodo, nivel), prof (nodo), Q (m3/s). Medias sobre todos los instantes dados."""
    b = M["zona"] > 0; a = M["area"][b]
    vol = np.maximum(prof[None] + eta, 0.0)[:, b] * a[None]
    f = np.clip(1 - S[:, b, :] / S_MAR, 0, 1)
    Vf, V = (f.mean(2) * vol).sum(1).mean(), vol.sum(1).mean()
    return dict(V_hm3=V / 1e6, f_media=Vf / V, f_sup=float((f[:, :, -1] * a).sum(1).mean() / a.sum()), Q_m3s=Q, Tf_d=Vf / Q / 86400)


def carga(dirm):
    from netCDF4 import Dataset
    out = Path(dirm) / "outputs"; n = max(int(f.stem.split("_")[-1]) for f in out.glob("salinity_*.nc"))
    eta, S = [], []
    for k in range(n - VENTANA + 1, n + 1):          # corrida terminada: el ultimo dia esta completo
        with Dataset(out / f"out2d_{k}.nc") as d: eta.append(np.asarray(d["elevation"][:], np.float32)); prof = np.asarray(d["depth"][:])
        with Dataset(out / f"salinity_{k}.nc") as d: S.append(np.asarray(d["salinity"][:], np.float32))
    return np.concatenate(eta), np.concatenate(S), prof, n


def prueba(M):
    n = len(M["zona"]); eta = np.zeros((6, n)); prof = np.full(n, 10.0); S = np.full((6, n, 16), S_MAR)
    S[:, :, -1] = S_MAR * (1 - 0.32)                   # solo la capa de superficie dulce al 32 %: media vertical 2 %
    r = renovacion(eta, S, prof, M, 2.0); V = 10 * M["area"][M["zona"] > 0].sum()
    assert abs(r["f_media"] - 0.02) < 1e-9 and abs(r["f_sup"] - 0.32) < 1e-9 and abs(r["Tf_d"] - 0.02 * V / 2 / 86400) < 1e-6, r
    print("prueba ok")


if __name__ == "__main__":
    R = Path(__file__).resolve().parent.parent
    M = dict(np.load(sys.argv[2] if len(sys.argv) > 2 else R / "datos" / "conjunto" / "posproceso_malla.npz"))
    if sys.argv[1] == "--prueba": prueba(M); sys.exit()
    dirm = Path(sys.argv[1]); eta, S, prof, n = carga(dirm); r = renovacion(eta, S, prof, M, caudal_rios(dirm))
    js = dirm / "resumen.json"; ref = json.loads(js.read_text()).get("frac_dulce_sup_bahia") if js.exists() else None
    print(f"{dirm} (dias {n - VENTANA + 1}-{n}): V = {r['V_hm3']:.1f} hm3, agua dulce media {100 * r['f_media']:.2f} % "
          f"(superficie {100 * r['f_sup']:.2f} %; resumen.json {100 * ref:.2f} %), Q = {r['Q_m3s']:.2f} m3/s -> T_f = {r['Tf_d']:.1f} d"
          if ref is not None else f"{dirm}: {r}")
