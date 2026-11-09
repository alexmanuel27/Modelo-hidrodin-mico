#!/usr/bin/env python3
"""Validacion del ejecutable con GEN: la serie de edad por zona de un caso de trazadores debe coincidir con la de la
corrida de robustez equivalente (T0 = m0000, T3 = m0005; mismo caso, solo cambia que lleva GEN). Compara los
serie_<zona> de resumen.npz en los dias comunes (SCHISM no es bit a bit entre ejecutables: criterio 1 % como comparar_tramos.py,
sobre la media de los ultimos 10 d comunes y sobre el maximo de la serie).
  python valida_trazadores.py runs/trazadores/m0000 runs/robustez/m0000
  python valida_trazadores.py runs/trazadores/m0000 runs/robustez/m0000 --final     (con los 120 d: ademas resumen.json < 1 %)
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
    import tempfile, json; d = Path(tempfile.mkdtemp()); (d / "resumen.json").write_text(json.dumps({"edad_media_d_bahia": 6.6, "frac_dulce_sup_bahia": 0.02}))
    assert compara_json(d, d); print("autoprueba valida_trazadores: ok")


def compara_json(a, b, tol=0.01):
    """Corrida completa: las metricas de resumen.json (edad media por zona y bahia, agua dulce) difieren < 1 % (criterio de comparar_tramos.py)."""
    import json
    ra, rb = (json.loads((Path(x) / "resumen.json").read_text()) for x in (a, b)); ok = True
    for k in [k for k in rb if k.startswith("edad_media_d_") or k == "frac_dulce_sup_bahia"]:
        d = abs(ra[k] - rb[k]) / abs(rb[k]); ok &= d < tol
        print(f"  {k:28s} nueva {ra[k]:.3f} ref {rb[k]:.3f} dif {d:.2%}  {'ok' if d < tol else 'FUERA'}")
    print("RESUMEN.JSON:", "pasa (< 1 %)" if ok else "NO pasa"); return ok


if __name__ == "__main__":
    if sys.argv[1] == "--prueba": prueba(); sys.exit()
    compara(np.load(Path(sys.argv[1]) / "resumen.npz"), np.load(Path(sys.argv[2]) / "resumen.npz"))
    if "--final" in sys.argv: compara_json(sys.argv[1], sys.argv[2])
