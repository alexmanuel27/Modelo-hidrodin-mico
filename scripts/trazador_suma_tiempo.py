#!/usr/bin/env python3
"""Cuando se forma el deficit del trazador de la suma frente a la salinidad (12-nov-2026). Ver docs/protocolo_trazadores_rios.md.
d(t) = (I_C4 - I_Vf) / I_Vf con I = inventario medio de cada dia (dominio entero). Lecturas A/B/C fijadas antes de ver datos.
  python trazador_suma_tiempo.py <caso>   (cluster, netcdf4-python)   |   python trazador_suma_tiempo.py --prueba"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from trazadores_rios import S_MAR

REINICIOS = np.arange(11, 120, 10)                                         # primer dia de cada tramo de 10 d
def rangos(x): return np.argsort(np.argsort(x))


def lectura(dia, V, C4, Qint=None):
    """dia (d, centro de cada dia, 1..n), V y C4 (m3) inventarios diarios. Devuelve d(t), banderas y texto."""
    d = C4 / V - 1; dia_k = np.round(dia + 0.5).astype(int)                  # dia_k = numero de pila 1..n
    fin, pri = d[dia_k >= 91].mean(), d[(dia_k >= 2) & (dia_k <= 5)].mean()
    r = dict(d_fin=float(fin), d_pri=float(pri))
    if abs(fin) < 0.02: r["lectura"] = "no concluye: el deficit no se reproduce (|d_fin| < 2 %)"; return d, r
    s = np.sign(fin); dd = np.diff(d) * s; kd = dia_k[1:]                      # dd[i] = cambio entre dia_k[i] y dia_k[i+1]
    esrei = np.isin(kd, REINICIOS)
    sp = np.corrcoef(rangos(dia), rangos(np.abs(d)))[0, 1]
    r["A"] = bool(abs(pri) >= 0.5 * abs(fin))
    r["B"] = bool(abs(pri) < 0.2 * abs(fin) and sp >= 0.9)
    mrei, mresto = float(np.median(dd[esrei])), float(np.median(np.abs(dd[~esrei])))
    r["C"] = bool(mrei >= 0.002 and mrei >= 3 * mresto); r.update(spearman=float(sp), cambio_mediano_reinicios=mrei, cambio_mediano_resto=mresto)
    r["lectura"] = ("C: saltos en los reinicios con hotstart" if r["C"] else "A: el deficit esta desde la inyeccion" if r["A"] else
                    "B: el deficit se acumula en el dominio" if r["B"] else "intermedio: sin conclusion")
    if Qint is not None: r["V_sobre_Q"] = [float(x) for x in (V / Qint)[(dia_k >= 2) & (dia_k <= 5)]]; r["C4_sobre_Q"] = [float(x) for x in (C4 / Qint)[(dia_k >= 2) & (dia_k <= 5)]]
    return d, r


def serie(dirm, M):
    from netCDF4 import Dataset
    out = Path(dirm) / "outputs"; n = max(int(f.stem.split("_")[-1]) for f in out.glob("salinity_*.nc")); z, area = M["zona"], M["area"]; b = z > 0
    dia, VD, CD, VB, CB = [], [], [], [], []
    for k in range(1, n + 1):
        with Dataset(out / f"out2d_{k}.nc") as d: eta = np.asarray(d["elevation"][:], np.float64); prof = np.asarray(d["depth"][:], np.float64)
        with Dataset(out / f"salinity_{k}.nc") as d: Vf = (1 - np.asarray(d["salinity"][:], np.float64) / S_MAR).mean(2)
        with Dataset(out / f"GEN_4_{k}.nc") as d: C4 = np.asarray(d["GEN_4"][:], np.float64).mean(2)
        vol = np.maximum(prof[None] + eta, 0.0) * area[None]; nr = len(eta)
        dia.append(k - 1 + (nr + 1) / (2 * nr)); inv = lambda x, s: float((x[:, s] * vol[:, s]).sum(1).mean())
        VD.append(inv(Vf, slice(None))); CD.append(inv(C4, slice(None))); VB.append(inv(Vf, b)); CB.append(inv(C4, b))
    return [np.array(x) for x in (dia, VD, CD, VB, CB)]


def prueba():
    t = np.arange(1, 121) - 0.5; V = 1e6 * (1 - np.exp(-t / 15)) + 1.0; k = np.round(t + 0.5).astype(int)
    d, r = lectura(t, V, V.copy()); assert r["lectura"].startswith("no concluye"), r
    d, r = lectura(t, V, V * 0.945); assert r["A"] and not r["B"] and not r["C"] and r["lectura"].startswith("A"), r
    d, r = lectura(t, V, V * (1 - 0.055 * (1 - np.exp(-t / 30)))); assert r["B"] and not r["A"] and not r["C"] and r["lectura"].startswith("B"), r
    esc = -0.005 * np.array([(REINICIOS <= x).sum() for x in k]); d, r = lectura(t, V, V * (1 + esc)); assert r["C"] and r["lectura"].startswith("C"), r
    d, r = lectura(t, V, V * (1 - 0.055 * (0.5 + 0.5 * (t > 60)))); assert not (r["A"] and r["B"]) and "lectura" in r      # rampa a mitad: A (0,5 en el inicio), no B
    print("autoprueba trazador_suma_tiempo: ok")


if __name__ == "__main__":
    if sys.argv[1] == "--prueba": prueba(); sys.exit()
    M = dict(np.load(Path(__file__).resolve().parent.parent / "datos" / "conjunto" / "posproceso_malla.npz")); dirm = Path(sys.argv[1])
    dia, VD, CD, VB, CB = serie(dirm, M); Q = np.loadtxt(dirm / "vsource.th", ndmin=2)[:, 1:].mean(0).sum()
    d, r = lectura(dia, VD, CD, Q * 86400 * dia); r["d_bahia_fin"] = float((CB[-30:] / VB[-30:]).mean() - 1)
    np.savez(dirm / "trazador_suma_tiempo.npz", dia=dia, V_dominio=VD, C4_dominio=CD, V_bahia=VB, C4_bahia=CB, d=d)
    (dirm / "trazador_suma_tiempo.json").write_text(json.dumps(r, indent=1))
    print("dia: d(dominio)   d(bahia)   I_Vf/I_Q   I_C4/I_Q")
    for k in (1, 2, 3, 5, 10, 11, 20, 21, 30, 60, 90, 120):
        if k <= len(dia): print(f"{k:4d}  {d[k-1]:+8.3%}  {CB[k-1]/VB[k-1]-1:+8.3%}  {VD[k-1]/(Q*86400*dia[k-1]):8.3f}  {CD[k-1]/(Q*86400*dia[k-1]):8.3f}")
    print({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items() if k not in ("V_sobre_Q", "C4_sobre_Q")}); print("LECTURA:", r["lectura"])
