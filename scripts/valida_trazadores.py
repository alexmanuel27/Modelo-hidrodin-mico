#!/usr/bin/env python3
"""Validacion del ejecutable con GEN: la serie de edad por zona de un caso de trazadores debe coincidir con la de la
corrida de robustez equivalente (T0 = m0000, T3 = m0005; mismo caso, solo cambia que lleva GEN). Compara los
serie_<zona> de resumen.npz en los dias comunes (SCHISM no es bit a bit entre ejecutables: criterio 1 % como comparar_tramos.py,
sobre la media de los ultimos 10 d comunes y sobre el maximo de la serie).
  python valida_trazadores.py runs/trazadores/m0000 runs/robustez/m0000
  python valida_trazadores.py --prueba"""
import sys
from pathlib import Path
import numpy as np

ZONAS = ["canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia"]


def compara(a, b, tol=0.01):
    ta, tb = a["dias"], b["dias"]; fin = min(ta.max(), tb.max()); ok = True
    print(f"dias comunes: 0-{fin:.1f}")
    for z in ZONAS:
        xa, xb = a[f"serie_{z}"][ta <= fin], b[f"serie_{z}"][tb <= fin]; n = min(len(xa), len(xb)); xa, xb = xa[:n], xb[:n]; u = np.arange(n) >= n - 60
        d_med = abs(xa[u].mean() - xb[u].mean()) / xb[u].mean(); d_max = np.abs(xa - xb).max() / xb.max()
        bien = d_med < tol and d_max < 3 * tol; ok &= bien
        print(f"  {z:11s} media ult. 10 d: nueva {xa[u].mean():.3f} ref {xb[u].mean():.3f} (dif {d_med:.2%}); dif max serie {d_max:.2%}  {'ok' if bien else 'FUERA DEL CRITERIO'}")
    print("RESULTADO:", "pasa" if ok else "NO pasa (parar y mirar antes de seguir)"); return ok


def prueba():
    t = np.arange(240) / 6; r = {"dias": t, **{f"serie_{z}": 5 + 0.1 * t + np.sin(t) for z in ZONAS}}
    assert compara(r, r); s = {**r, "serie_bahia": r["serie_bahia"] * 1.05}; assert not compara(s, r)
    print("autoprueba valida_trazadores: ok")


if __name__ == "__main__":
    if sys.argv[1] == "--prueba": prueba(); sys.exit()
    compara(np.load(Path(sys.argv[1]) / "resumen.npz"), np.load(Path(sys.argv[2]) / "resumen.npz"))
