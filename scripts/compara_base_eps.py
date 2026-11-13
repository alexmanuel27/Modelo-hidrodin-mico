#!/usr/bin/env python3
"""Comprobacion del 13-nov: cuanto cambian las cifras del caso central (edad, T_f, agua dulce, rho de Sentinel-2) al resolver
el TVD vertical con eps1_tvd_imp = 1e-9 en lugar de 1e-4. Lectura fijada antes de ver datos en docs/protocolo_trazadores_rios.md.
  python compara_base_eps.py runs/base_eps/m0000 runs/trazadores/m0000      |      python compara_base_eps.py --prueba
Necesita en cada caso resumen.json, resumen.npz (posproceso.py), renovacion_dulce.json; trazadores.json opcional."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))

ZONAS = ["canal", "cuenca", "Marimelena", "Guasabacoa", "Atares", "bahia"]
EDAD_MAX, TF_MAX, RHO_MAX = 0.01, 0.05, 0.02


def lectura(n, r):
    """n, r: dict(edad={zona: d}, Tf=d, f_sup=fraccion, rho=valor) con 1e-9 (n) y 1e-4 (r)."""
    de = {z: n["edad"][z] / r["edad"][z] - 1 for z in ZONAS}; dT = n["Tf"] / r["Tf"] - 1; dr = n["rho"] - r["rho"]
    o = dict(cambio_edad=de, cambio_Tf=dT, cambio_fsup=n["f_sup"] / r["f_sup"] - 1, cambio_rho=dr)
    o["edad"] = "no afectada (< 1 % en todas las zonas)" if max(map(abs, de.values())) < EDAD_MAX else "CAMBIA (>= 1 % en alguna zona)"
    o["T_f"] = "se mantiene (< 5 %)" if abs(dT) < TF_MAX else "CAMBIA (>= 5 %)"
    o["rho"] = "se mantiene (< 0,02)" if abs(dr) < RHO_MAX else "CAMBIA (>= 0,02)"
    return o


def lee(dirm):
    from comparacion_s2 import S2, campo_medio, pixeles, spearman
    d = Path(dirm); res = json.loads((d / "resumen.json").read_text()); ren = json.loads((d / "renovacion_dulce.json").read_text())
    s2 = np.load(S2); sat = s2["persistencia"][:252]; mod = campo_medio(d, "s2_dulce"); ok = pixeles(s2, mod)
    x = dict(edad={z: res[f"edad_media_d_{z}"] for z in ZONAS}, Tf=ren["Tf_d"], f_sup=res["frac_dulce_sup_bahia"], rho=float(spearman(sat[ok], mod[ok])))
    if (d / "trazadores.json").exists(): x["control_suma"] = json.loads((d / "trazadores.json").read_text())["control_dif_rel"]
    return x


def prueba():
    r = dict(edad={z: 6.5 for z in ZONAS}, Tf=1.9, f_sup=0.025, rho=0.45)
    o = lectura(r, r); assert o["edad"].startswith("no") and o["T_f"].startswith("se") and o["rho"].startswith("se"), o
    n = dict(r, edad={**r["edad"], "canal": 6.6}, Tf=1.75, rho=0.42); o = lectura(n, r)
    assert o["edad"].startswith("CAMBIA") and o["T_f"].startswith("CAMBIA") and o["rho"].startswith("CAMBIA"), o
    print("autoprueba compara_base_eps: ok")


if __name__ == "__main__":
    if sys.argv[1] == "--prueba": prueba(); sys.exit()
    n, r = lee(sys.argv[1]), lee(sys.argv[2]); o = lectura(n, r)
    (Path(sys.argv[1]) / "compara_base_eps.json").write_text(json.dumps(dict(nuevo=n, ref=r, **o), indent=1))
    print("edad media (d), 1e-4 -> 1e-9:", ", ".join(f"{z} {r['edad'][z]:.3f}->{n['edad'][z]:.3f} ({o['cambio_edad'][z]:+.2%})" for z in ZONAS))
    print(f"T_f {r['Tf']:.3f} -> {n['Tf']:.3f} d ({o['cambio_Tf']:+.2%}); agua dulce en superficie {r['f_sup']:.4f} -> {n['f_sup']:.4f} ({o['cambio_fsup']:+.2%}); "
          f"rho S2 {r['rho']:.3f} -> {n['rho']:.3f} ({o['cambio_rho']:+.3f})")
    if "control_suma" in n: print(f"control de la suma (caudal base): {r.get('control_suma', float('nan')):.2%} -> {n['control_suma']:.2%}")
    print("LECTURA: edad", o["edad"], "| T_f", o["T_f"], "| rho", o["rho"])
