#!/usr/bin/env python3
"""V3 X4: ¿es estable entre anos el desplazamiento de la edad por el flujo de calor? Lectura fijada en docs/protocolo_metricas_conjunto.md (17-nov (4)).
Miembro central, 120 d (ene-abr), edad de la bahia en los ultimos 30 d. 2016 = runs/robustez m0005 (calor + OISST) y m0000 (sin calor); 2017-2025 = runs/anios.
  python scripts/anios.py -> resultados/anios.txt        python scripts/anios.py --prueba"""
import json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
DESP, MITAD = 5.40, 2.70      # desplazamiento pareado mediano del conjunto de 64 (17-nov) y su mitad; fijados antes de ver ningun ano


def lectura(d):
    """d: {ano: desplazamiento (d)} -> (lineas, veredicto)."""
    v = np.array(list(d.values())); rg = float(v.max() - v.min())
    ver = ("ESTABLE (todos > 0 y rango <= %.2f d)" % MITAD if (v > 0).all() and rg <= MITAD else
           "NO ESTABLE (algun desplazamiento <= 0 o rango > %.2f d)" % DESP if (v <= 0).any() or rg > DESP else "PARCIAL (rango entre %.2f y %.2f d)" % (MITAD, DESP))
    return [f"desplazamiento medio {v.mean():.2f} d, sd {v.std(ddof=1):.2f}, minimo {v.min():.2f} ({min(d, key=d.get)}), maximo {v.max():.2f} ({max(d, key=d.get)}), rango {rg:.2f} d; {len(v)} anos"], ver


def main():
    e = lambda p: (lambda r: None if r.get("nan", 0) else r["edad_media_d_bahia"])(json.loads((RAIZ / "runs" / p / "resumen.json").read_text()))
    pares = {2016: ("robustez/m0005", "robustez/m0000")}
    for a in range(2017, 2026): pares[a] = (f"anios/m{2 * (a - 2017):04d}", f"anios/m{2 * (a - 2017) + 1:04d}")
    o, d = ["ano: edad con calor, sin calor, desplazamiento (d)"], {}
    for a, (h, s) in pares.items():
        try: eh, es = e(h), e(s)
        except OSError: o.append(f"  {a}: falta resumen.json"); continue
        if eh is None or es is None: o.append(f"  {a}: con NaN, se excluye"); continue
        d[a] = eh - es; o.append(f"  {a}: {eh:.2f} {es:.2f} {eh - es:+.2f}")
    if len(d) < 8: o.append(f"solo {len(d)} anos validos de 10: no concluyente")
    else: l, ver = lectura(d); o += l + [f"veredicto X4: {ver}"]
    t = "\n".join(o); print(t); (RAIZ / "resultados" / "anios.txt").write_text(t + "\n")


def prueba():
    assert lectura({a: 5.4 + 0.1 * (a % 3) for a in range(2016, 2026)})[1].startswith("ESTABLE")
    assert lectura({a: 5.4 + (a - 2016) * 0.7 for a in range(2016, 2026)})[1].startswith("NO ESTABLE")
    assert lectura({a: 5.0 + (a - 2016) * 0.4 for a in range(2016, 2026)})[1].startswith("PARCIAL")
    assert lectura({**{a: 5.0 for a in range(2016, 2025)}, 2025: -0.1})[1].startswith("NO ESTABLE"); print("prueba ok")


if __name__ == "__main__":
    prueba() if sys.argv[1:] == ["--prueba"] else main()
