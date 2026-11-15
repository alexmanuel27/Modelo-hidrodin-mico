#!/usr/bin/env python3
"""Prueba de la causa de las velocidades de ~6 m/s en el borde abierto (revision V1, A9). Lectura fijada en
docs/resultados_robustez.md (15-nov). Lee runs/borde_prueba/m0000 (control), m0001 (sin Coriolis), m0002 (sin viento).
  python scripts/borde_prueba.py  -> resultados/borde_prueba.txt;   python scripts/borde_prueba.py --prueba"""
import json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
CASOS = (("m0000", "control (Coriolis y viento)"), ("m0001", "sin Coriolis"), ("m0002", "sin viento"))
VCONTROL, FRAC, VABS = 4.5, 0.5, 3.0   # control valido si vmax >= 4,5 m/s (P5 del conjunto) en un nodo del borde; "baja" si < 50 % del control y < 3 m/s


def borde(hgrid):
    L = Path(hgrid).read_text().split("\n"); ne, nn = map(int, L[1].split()[:2]); k = 2 + nn + ne
    return {int(L[k + 3 + i].split()[0]) for i in range(int(L[k + 2].split()[0]))}   # numeros de nodo (1-based)


def prueba():
    assert borde_demo() == {5, 7}; print("prueba ok")


def borde_demo():
    import tempfile
    t = Path(tempfile.mkdtemp()) / "h.gr3"
    t.write_text("x\n1 7\n" + "".join(f"{i} 0 0 1\n" for i in range(1, 8)) + "1 3 1 2 3\n1 !open boundaries\n2 !open boundary nodes\n2 !nodes of boundary 1\n5\n7\n0 !land\n"); return borde(t)


if __name__ == "__main__":
    if sys.argv[1:] == ["--prueba"]: prueba(); sys.exit()
    d = RAIZ / "runs" / "borde_prueba"; b = borde(d / "m0000" / "hgrid.gr3"); r = {m: json.loads((d / m / "resumen.json").read_text()) for m, _ in CASOS}
    out = []
    for m, nom in CASOS:
        out.append(f"{m} {nom}: {r[m]['dias']:.0f} d, vmax {r[m]['vmax']:.2f} m/s en el nodo {r[m]['vmax_nodo']} ({'borde abierto' if r[m]['vmax_nodo'] in b else 'NO es del borde'}); vmax dentro de la bahia {r[m]['vmax_bahia']:.2f}; nan={r[m]['nan']}")
    c = r["m0000"]; valido = c["vmax"] >= VCONTROL and c["vmax_nodo"] in b
    out.append("control " + ("VALIDO: reproduce la velocidad del borde" if valido else "NO reproduce la velocidad del borde en 10 d: la prueba no es concluyente"))
    if valido:
        for m, nom in CASOS[1:]:
            baja = r[m]["vmax"] < FRAC * c["vmax"] and r[m]["vmax"] < VABS
            out.append(f"{nom}: vmax {r[m]['vmax']:.2f} frente a {c['vmax']:.2f} -> " + ("la velocidad desaparece" if baja else "la velocidad NO desaparece"))
    texto = "\n".join(out); print(texto); (RAIZ / "resultados" / "borde_prueba.txt").write_text(texto + "\n")
