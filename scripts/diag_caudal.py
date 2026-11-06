#!/usr/bin/env python3
"""Diagnostico (solo lectura) de los picos de caudal bruto por la seccion del canal. numpy + netCDF4.
Uso: python diag_caudal.py <carpeta del miembro> [N_picos=8] [malla.npz]
     python diag_caudal.py --prueba
Toma de <miembro>/resumen.npz los N instantes con mayor |Q| de los ultimos 30 d, relee out2d de esos dias y de los
vecinos (necesita outputs/out2d_*.nc: solo los miembros en GUARDAR de conjunto.py los conservan) y, por instante, dice:
que puntos de la seccion aportan, que nodo tiene la mayor velocidad normal y como evoluciona (un solo instante o no),
y cuanto vale |Q| frente al cambio de volumen de la bahia entre instantes vecinos (cociente >> 1: no lo explica la marea)."""
import sys
from pathlib import Path
import numpy as np

RIO = 2.14   # m3/s que entran por los rios (JICA 2004); el resto del cambio de volumen pasa por la seccion


def analiza(t, eta, u, v, prof, M, js):
    """t (s), eta/u/v (tiempo, nodo), prof (nodo). js = indices de t a diagnosticar. Devuelve una lista de dicts."""
    H = np.maximum(prof[None] + eta, 0.0); i, wt = M["sec_i"], M["sec_w"]
    un = u * M["sec_dir"][0] + v * M["sec_dir"][1]                                   # velocidad normal, > 0 hacia dentro
    Qp = (un[:, i] * wt[None]).sum(2) * (H[:, i] * wt[None]).sum(2) * float(M["sec_dn"]); Q = Qp.sum(1)
    bahia = M["zona"] > 0; V = (H[:, bahia] * M["area"][bahia][None]).sum(1)
    dt = np.diff(t); dVdt = np.where(dt <= 5 * 3600, np.diff(V) / np.where(dt > 0, dt, 1) - RIO, np.nan)   # j -> j+1
    nodos = np.unique(i); res = []
    for j in js:
        p = np.argsort(-np.abs(Qp[j]))[:3]; k = nodos[np.argmax(np.abs(un[j, nodos]))]
        vec = np.abs([dVdt[x] for x in (j - 1, j) if 0 <= x < len(dVdt)]); vec = vec[np.isfinite(vec)]
        res.append(dict(dia=t[j] / 86400, Q=Q[j], puntos=[(int(a), float(abs(Qp[j, a]) / np.abs(Qp[j]).sum())) for a in p],
                        nodo=int(k) + 1, un_vecinos=[float(un[x, k]) if 0 <= x < len(t) else np.nan for x in (j - 1, j, j + 1)],
                        H=float(H[j, k]), eta=float(eta[j, k]), dV_Q=float(vec.max()) if len(vec) else np.nan,
                        cociente=float(abs(Q[j]) / vec.max()) if len(vec) else np.nan))
    return res


def carga(dirm, dias):
    from netCDF4 import Dataset
    out, t, eta, u, v = Path(dirm) / "outputs", [], [], [], []
    for n in sorted(dias):
        f = out / f"out2d_{n}.nc"
        if not f.exists(): continue
        with Dataset(f) as d:
            t.append(np.asarray(d["time"][:], float)); eta.append(np.asarray(d["elevation"][:], np.float32))
            u.append(np.asarray(d["depthAverageVelX"][:], np.float32)); v.append(np.asarray(d["depthAverageVelY"][:], np.float32))
            prof = np.asarray(d["depth"][:])
    if not t: sys.exit(f"No hay out2d_*.nc en {out}: el miembro no esta en GUARDAR (conjunto.py) y se borraron al terminar.")
    return np.concatenate(t), np.concatenate(eta), np.concatenate(u), np.concatenate(v), prof


def main(dirm, n=8, malla=None):
    M = dict(np.load(malla or Path(__file__).resolve().parent.parent / "datos" / "conjunto" / "posproceso_malla.npz"))
    z = np.load(Path(dirm) / "resumen.npz"); d, Q = z["dias"].astype(float), z["Q"]
    ult = np.where(d > d[-1] - 30)[0]; sel = ult[np.argsort(-np.abs(Q[ult]))[:n]]
    t, eta, u, v, prof = carga(dirm, {int(np.ceil(x)) + k for x in d[sel] for k in (-1, 0, 1)})
    js = [int(np.argmin(np.abs(t - d[s] * 86400))) for s in sel]
    print(f"{dirm}: media |Q| ult. 30 d = {np.abs(Q[ult]).mean():.1f}, mediana = {np.median(np.abs(Q[ult])):.1f} m3/s")
    print("dia     Q(npz) Q(out2d) | nodo  un[j-1,j,j+1] (m/s)   H(m)  eta(m) | |dV/dt-rio| cociente | puntos de la seccion (indice: parte de sum|Qp|)")
    for s, r in zip(sel, analiza(t, eta, u, v, prof, M, js)):
        print(f"{r['dia']:6.2f} {Q[s]:7.0f} {r['Q']:8.0f} | {r['nodo']:5d} {r['un_vecinos'][0]:6.2f}{r['un_vecinos'][1]:6.2f}{r['un_vecinos'][2]:6.2f}"
              f" {r['H']:6.1f} {r['eta']:6.2f} | {r['dV_Q']:9.0f} {r['cociente']:8.1f} | "
              + " ".join(f"{a}:{f:.0%}" for a, f in r["puntos"]))


def prueba():
    M = dict(np.load(Path(__file__).resolve().parent.parent / "datos" / "conjunto" / "posproceso_malla.npz"))
    n, t = len(M["zona"]), np.arange(1, 7) * 4 * 3600.0
    prof, eta = np.full(n, 10.0), np.zeros((6, n)); u = np.full((6, n), 0.1 * M["sec_dir"][0]); v = np.full((6, n), 0.1 * M["sec_dir"][1])
    r = analiza(t, eta, u, v, prof, M, [2])[0]
    assert abs(r["Q"] - 0.1 * 10 * len(M["sec_i"]) * float(M["sec_dn"])) < 1e-6 and abs(r["dV_Q"] - RIO) < 1e-6   # Q = 330, volumen constante
    k = int(M["sec_i"][5, 0]); u[3, k] *= 20; v[3, k] *= 20                                                       # pico en un nodo, un instante
    r = analiza(t, eta, u, v, prof, M, [3])[0]
    assert r["nodo"] == k + 1 and r["Q"] > 400 and r["cociente"] > 100 and abs(r["un_vecinos"][0] - 0.1) < 1e-6 and abs(r["un_vecinos"][1] - 2.0) < 1e-6, r
    print("prueba ok")


if __name__ == "__main__":
    if sys.argv[1] == "--prueba": prueba()
    else: main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8, sys.argv[3] if len(sys.argv) > 3 else None)
