#!/usr/bin/env python3
"""Comparacion modelo <-> Sentinel-2 segun docs/protocolo_comparacion_s2.md (CONGELADO 21-oct-2026). Solo numpy.

  python scripts/comparacion_s2.py runs/mecanismo/m0002            -> prueba principal en un miembro (s2_dulce)
  python scripts/comparacion_s2.py runs/conjunto --conjunto        -> rho por miembro (bloques A y B) y P(rho > 0)
  python scripts/comparacion_s2.py ... --campo s2_edad             -> prueba secundaria (edad en superficie)
  python scripts/comparacion_s2.py --prueba                        -> autoprueba con campos sinteticos

Protocolo: pixeles de agua en las dos mascaras, a >= 40 m (2 pixeles) de la costa S2, n_validas >= 50; filas 0-251 de la
entrega (la 252 sobra); campo del modelo = media de las instantaneas de las 16 UTC; Spearman; IC 95 % por bootstrap de
bloques de 10 x 10 pixeles (200 m), 1000 remuestreos. Se cumple si el limite inferior del IC es > 0; robusta si ademas
rho > 0 en >= 90 % de los miembros. Control (cambio registrado el 26-oct, antes de ver resultados): nulo por
desplazamientos ciclicos del mapa S2 (>= 500 m, 999 desplazamientos); se informa p_desplazamientos junto al criterio. Salida: resultados/comparacion_s2/<nombre>.json"""
import csv, json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
S2 = RAIZ / "datos" / "sentinel2" / "rejilla.npz"
NMIN, MARGEN_PX, BLOQUE, NBOOT = 50, 2, 10, 1000
NDESPL, DESPL_MIN_PX, SOLAPE_MIN = 999, 25, 1000


def rangos(x):
    """Rangos con empates promediados (la frecuencia S2 tiene muchos ceros)."""
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    return (np.cumsum(cnt) - cnt + 0.5 * (cnt - 1))[inv]


def spearman(a, b):
    ra, rb = rangos(a), rangos(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def pixeles(s2, campo):
    """Mascara de pixeles del protocolo sobre la rejilla del modelo (252 filas)."""
    agua = s2["mascara_agua"][:252] > 0; nv = s2["n_validas"][:252]
    lejos = agua.copy()
    for _ in range(MARGEN_PX):                                     # erosion de 1 pixel (vecindad de 4) por paso
        p = np.pad(lejos, 1); lejos = lejos & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return lejos & (nv >= NMIN) & np.isfinite(s2["persistencia"][:252]) & np.isfinite(campo)


def prueba_rho(sat, mod, ok, rng, nboot=NBOOT):
    j, i = np.nonzero(ok); blq = (j // BLOQUE) * 1000 + i // BLOQUE
    ub, inv = np.unique(blq, return_inverse=True); grupos = [np.flatnonzero(inv == k) for k in range(len(ub))]
    x, y = sat[ok], mod[ok]; rho = spearman(x, y)
    bs = []
    for _ in range(nboot):
        idx = np.concatenate([grupos[k] for k in rng.integers(0, len(grupos), len(grupos))])
        bs.append(spearman(x[idx], y[idx]))
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return dict(rho=rho, ic95=[float(lo), float(hi)], n_pixeles=int(ok.sum()), n_bloques=len(grupos), cumple=bool(lo > 0))


def nulo_desplazado(sat, mod, base, rng, n=NDESPL):
    """Control: el mapa S2 (con su mascara de pixeles del protocolo, base) se desplaza en ciclo >= 500 m; la autocorrelacion
    espacial de los dos mapas se conserva y se rompe su alineacion. p = fraccion de desplazamientos con rho >= observado."""
    ok0 = base & np.isfinite(mod); rho0 = spearman(sat[ok0], mod[ok0]); nul = []
    while len(nul) < n:
        dy, dx = rng.integers(-sat.shape[0], sat.shape[0]), rng.integers(-sat.shape[1], sat.shape[1])
        if np.hypot(dy, dx) < DESPL_MIN_PX: continue
        ss, bs_ = np.roll(sat, (dy, dx), (0, 1)), np.roll(base, (dy, dx), (0, 1)); ok = bs_ & np.isfinite(mod)
        if ok.sum() < SOLAPE_MIN: continue
        nul.append(spearman(ss[ok], mod[ok]))
    nul = np.array(nul)
    return dict(p_desplazamientos=float((1 + np.sum(nul >= rho0)) / (1 + n)), rho_nulo_p95=float(np.percentile(nul, 95)))


def campo_medio(dirm, nombre):
    d = np.load(Path(dirm) / "resumen.npz")
    if nombre not in d: return None
    return np.nanmean(d[nombre], 0)                                # media de las instantaneas de las 16 UTC


def main(args):
    nombre = args[args.index("--campo") + 1] if "--campo" in args else "s2_dulce"
    destino = Path(args[0]); s2 = np.load(S2); sat = s2["persistencia"][:252]; rng = np.random.default_rng(20261021)
    salida = RAIZ / "resultados" / "comparacion_s2"; salida.mkdir(parents=True, exist_ok=True)
    if "--conjunto" not in args:
        mod = campo_medio(destino, nombre)
        if mod is None: sys.exit(f"{destino}/resumen.npz no tiene {nombre} (¿corrida sin rios? ¿posproceso viejo?)")
        r = dict(miembro=str(destino), campo=nombre, **prueba_rho(sat, mod, pixeles(s2, mod), rng),
                 **nulo_desplazado(sat, mod, pixeles(s2, np.ones_like(sat)), rng))
        print(json.dumps(r, indent=1)); (salida / f"{destino.name}_{nombre}.json").write_text(json.dumps(r, indent=1)); return r
    with open(RAIZ / "datos" / "conjunto" / "diseno.csv") as f: filas = [x for x in csv.DictReader(f) if x["bloque"] in ("A", "B")]
    rhos = {}
    for x in filas:
        dm = destino / f"m{int(x['miembro']):04d}"
        if not (dm / "resumen.npz").exists(): continue
        mod = campo_medio(dm, nombre)
        if mod is None: continue
        ok = pixeles(s2, mod); rhos[dm.name] = spearman(sat[ok], mod[ok])
    v = np.array(list(rhos.values()))
    r = dict(campo=nombre, n_miembros=len(v), frac_rho_positivo=float(np.mean(v > 0)) if len(v) else None,
             rho_p5_p50_p95=[float(q) for q in np.percentile(v, [5, 50, 95])] if len(v) else None,
             robusta=bool(len(v) and np.mean(v > 0) >= 0.9), rho_por_miembro=rhos)
    print(json.dumps({k: r[k] for k in r if k != "rho_por_miembro"}, indent=1))
    (salida / f"conjunto_{nombre}.json").write_text(json.dumps(r, indent=1)); return r


def prueba():
    """Con la mascara real: un campo = persistencia + ruido espacial da rho > 0 y cumple; un campo independiente
    (ruido espacial suave) no debe cumplir en mas de ~5-10 % de los casos; los empates se rankean bien."""
    assert np.allclose(rangos(np.array([3., 1, 1, 2])), [3, 0.5, 0.5, 2])
    s2 = np.load(S2); sat = s2["persistencia"][:252]; rng = np.random.default_rng(1)
    def suave(semilla):
        r = np.random.default_rng(semilla).normal(size=sat.shape)
        for _ in range(8): r = 0.2 * (r + np.roll(r, 1, 0) + np.roll(r, -1, 0) + np.roll(r, 1, 1) + np.roll(r, -1, 1))
        return r / r.std()
    bueno = np.where(np.isfinite(sat), sat / np.nanstd(sat) + 0.7 * suave(0), np.nan)
    rb = prueba_rho(sat, bueno, pixeles(s2, bueno), rng); assert rb["cumple"] and rb["rho"] > 0.3, rb
    falsos = [prueba_rho(sat, suave(100 + k), pixeles(s2, suave(100 + k)), rng, 200)["cumple"] for k in range(20)]
    assert np.mean(falsos) <= 0.15, falsos
    print(f"autoprueba comparacion S2: ok (campo relacionado rho {rb['rho']:.2f}, IC {rb['ic95'][0]:.2f}-{rb['ic95'][1]:.2f}; "
          f"falsos positivos con campos independientes {np.mean(falsos):.0%} de 20)")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--prueba"]: prueba()
    elif len(sys.argv) > 1: main(sys.argv[1:])
    else: sys.exit(__doc__)
