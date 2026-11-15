#!/usr/bin/env python3
"""Prolongacion a 365 d de la base, m0001 (calor, borde 28 C) y m0005 (calor + OISST) (revision V1, A1). Lectura fijada
en docs/resultados_robustez.md (adenda 14-nov). Lee runs/robustez_largo/mNNNN/resumen.{json,npz} (bajados del cluster).
  python scripts/robustez_largo.py  -> resultados/robustez_largo.txt (y en pantalla)
  python scripts/robustez_largo.py --prueba
Pre-registrado: edad por zona (ultimos 30 d), canal sup/fondo, deriva (ultimos 10 d; equilibrio si |deriva| <= 0,05 d/d).
Descriptivo, NO pre-registrado: medias mensuales, ventana movil de 30 d y dias con media diaria > 14 d de la serie de la bahia."""
import json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
CASOS = (("m0000", "base"), ("m0001", "calor (borde 28 C)"), ("m0005", "calor + OISST"))
ZONAS = ("canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia")
MES = np.cumsum([0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])   # 2016 bisiesto


def diaria(s):
    dd = np.floor(np.arange(len(s)) / (len(s) / 365)).astype(int)
    return np.array([s[dd == k].mean() for k in range(365)])


def prueba():
    md = diaria(np.full(365 * 6, 7.0)); assert md.shape == (365,) and np.allclose(md, 7.0)
    assert MES[-1] == 366 and np.allclose([md[MES[i]:MES[i + 1]].mean() for i in range(12)], 7.0)
    print("prueba ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--prueba"]: prueba(); sys.exit()
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); c = M["zona"] == 1; w = M["area"][c]
    out = []
    for m, nom in CASOS:
        r = json.loads((RAIZ / "runs" / "robustez_largo" / m / "resumen.json").read_text()); nz = np.load(RAIZ / "runs" / "robustez_largo" / m / "resumen.npz")
        md = diaria(nz["serie_bahia"]); r30 = np.array([md[k:k + 30].mean() for k in range(336)])
        out += [f"== {m} {nom}: {r['dias']:.0f} d, nan={r['nan']}",
                " edad ult. 30 d: " + ", ".join(f"{z} {r[f'edad_media_d_{z}']:.2f}" for z in ZONAS),
                f" deriva ult. 10 d: {r['deriva_edad_bahia_d_por_d']:+.3f} d/d -> " + ("equilibrio" if abs(r['deriva_edad_bahia_d_por_d']) <= 0.05 else "SIN equilibrio"),
                f" canal sup/fondo: {(nz['edad_sup'][c] * w).sum() / w.sum():.2f} / {(nz['edad_fondo'][c] * w).sum() / w.sum():.2f}",
                " [descriptivo] medias mensuales ene..dic: " + " ".join(f"{md[MES[i]:MES[i + 1]].mean():.1f}" for i in range(12)),
                f" [descriptivo] media anual {md.mean():.1f}; ventana de 30 d: min {r30.min():.1f} (dias {r30.argmin() + 1}-{r30.argmin() + 30}), max {r30.max():.1f} (dias {r30.argmax() + 1}-{r30.argmax() + 30}); dias > 14 d: {(md > 14).sum()}/365; dias 1-120: {md[:120].mean():.1f}"]
    texto = "\n".join(out); print(texto); (RAIZ / "resultados" / "robustez_largo.txt").write_text(texto + "\n")
