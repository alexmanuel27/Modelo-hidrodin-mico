#!/usr/bin/env python3
"""Diagnostico (solo lectura) de los picos de caudal bruto por la seccion del canal. numpy + netCDF4.
Uso: python diag_caudal.py <carpeta del miembro> [N_picos=8] [malla.npz]
     python diag_caudal.py --hf <carpeta con out2d cada ~10 min>   (espectro de Q y efecto del muestreo de 4 h; ver cluster/hf_caudal.sh)
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
    i = M["sec_i"]; Qp, un, Q, V, H = serie(t, eta, u, v, prof, M)
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


def espectro(t, Q):
    """Q (m3/s) a paso constante. Devuelve (picos, bandas, media|Q| completa, (min, media, max) de media|Q| con muestreo de 4 h y todas las fases)."""
    dt = float(np.median(np.diff(t))); n = len(Q); f = np.fft.rfftfreq(n, dt)
    P = np.abs(np.fft.rfft((Q - Q.mean()) * np.hanning(n))) ** 2; per = np.where(f > 0, 1 / np.where(f > 0, f, 1) / 3600, np.inf)
    k = [x for x in range(1, len(P) - 1) if P[x] > P[x - 1] and P[x] > P[x + 1]]; k = sorted(k, key=lambda x: -P[x])[:3]
    picos = [(float(per[x]), float(P[x] / P[1:].sum())) for x in k]
    bandas = {nom: float(P[(per >= a) & (per < b)].sum() / P[1:].sum()) for nom, a, b in (("<2 h", 0, 2), ("2-8 h", 2, 8), ("8-16 h", 8, 16), (">16 h", 16, 1e9))}
    paso = max(1, int(round(4 * 3600 / dt))); m = [np.abs(Q[o::paso]).mean() for o in range(paso)]
    return picos, bandas, float(np.abs(Q).mean()), (min(m), float(np.mean(m)), max(m))


def main_hf(dirm, malla=None):
    M = dict(np.load(malla or Path(__file__).resolve().parent.parent / "datos" / "conjunto" / "posproceso_malla.npz"))
    t, eta, u, v, prof = carga(dirm, None); Q = serie(t, eta, u, v, prof, M)[2]
    picos, bandas, completa, (lo, med, hi) = espectro(t, Q)
    print(f"{dirm}: {len(t)} instantes cada {np.median(np.diff(t)) / 60:.0f} min, {np.ptp(t) / 86400:.1f} d")
    print("picos del espectro de Q (periodo h, parte de la varianza): " + "; ".join(f"{p:.2f} h ({w:.0%})" for p, w in picos))
    print("varianza por banda: " + ", ".join(f"{k}: {w:.0%}" for k, w in bandas.items()))
    print(f"media |Q|: completa {completa:.1f}; con muestreo de 4 h segun la fase: min {lo:.1f}, media {med:.1f}, max {hi:.1f} m3/s")


def serie(t, eta, u, v, prof, M):
    """Q por punto de la seccion (tiempo, 33; > 0 hacia dentro), velocidad normal, Q total y volumen de la bahia."""
    H = np.maximum(prof[None] + eta, 0.0); i, wt = M["sec_i"], M["sec_w"]
    un = u * M["sec_dir"][0] + v * M["sec_dir"][1]
    Qp = (un[:, i] * wt[None]).sum(2) * (H[:, i] * wt[None]).sum(2) * float(M["sec_dn"])
    bahia = M["zona"] > 0
    return Qp, un, Qp.sum(1), (H[:, bahia] * M["area"][bahia][None]).sum(1), H


def carga(dirm, dias):
    from netCDF4 import Dataset
    out, t, eta, u, v = Path(dirm) / "outputs", [], [], [], []
    if dias is None: dias = [int(f.stem.split("_")[-1]) for f in out.glob("out2d_*.nc")]
    for n in sorted(dias):
        f = out / f"out2d_{n}.nc"
        if not f.exists(): continue
        with Dataset(f) as d:
            t.append(np.asarray(d["time"][:], float)); eta.append(np.asarray(d["elevation"][:], np.float32))
            u.append(np.asarray(d["depthAverageVelX"][:], np.float32)); v.append(np.asarray(d["depthAverageVelY"][:], np.float32))
            prof = np.asarray(d["depth"][:])
    if not t: sys.exit(f"No hay out2d_*.nc en {out}. En m0000_hf: el trabajo hf_caudal.sh no se lanzo, sigue en cola o fallo. En un miembro normal: no esta en GUARDAR (conjunto.py) y se borraron al terminar.")
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
    tt = np.arange(0, 48 * 3600, 600.0)                                                  # Q sintetico: marea M2 + oscilacion de 55 min
    pk, _, comp, (lo, med, hi) = espectro(tt, 100 * np.sin(2 * np.pi * tt / (12.42 * 3600)) + 150 * np.sin(2 * np.pi * tt / 3300))
    assert abs(pk[0][0] - 0.92) < 0.08 and any(abs(p - 12.4) < 1.6 for p, _ in pk) and hi / lo > 1.15, (pk, lo, med, hi)
    print("prueba ok")


if __name__ == "__main__":
    if sys.argv[1] == "--prueba": prueba()
    elif sys.argv[1] == "--hf": main_hf(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else: main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8, sys.argv[3] if len(sys.argv) > 3 else None)
