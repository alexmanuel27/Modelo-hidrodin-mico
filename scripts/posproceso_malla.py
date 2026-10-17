#!/usr/bin/env python3
"""Precalcula lo que el posproceso del conjunto necesita de la malla (una vez; numpy+scipy, en el Mac):
zona de cada nodo, area de cada nodo, pesos baricentricos a la rejilla Sentinel-2 (UTM 17N, 20 m,
E 361139-365896, N 2556342-2561392, centros de celda) y a la seccion transversal del canal.
Salida: datos/conjunto/posproceso_malla.npz (lo lee scripts/posproceso.py en el cluster solo con numpy)."""
import sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

R = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(R / "scripts"), str(R / "scripts" / "batimetria")]
from zonas import zonas, CENTRO, RUMBO      # noqa: E402
import importlib                            # noqa: E402
malla = importlib.import_module("09_malla")
S2 = dict(e0=361139.0, e1=365896.0, n0=2556342.0, n1=2561392.0, d=20.0)


def lee_hgrid(ruta):
    f = Path(ruta).read_text().split("\n"); ne, nn = map(int, f[1].split()[:2])
    xy = np.array([[float(v) for v in l.split()[1:3]] for l in f[2:2 + nn]])
    tri = np.array([[int(c) - 1 for c in l.split()[2:5]] for l in f[2 + nn:2 + nn + ne]])
    return xy, tri


def pesos(xy, tri, p):
    """Triangulo que contiene cada punto y sus coordenadas baricentricas; fuera de la malla: indice -1."""
    c = xy[tri].mean(1); arbol = cKDTree(c)
    idx = np.full((len(p), 3), -1); w = np.zeros((len(p), 3))
    _, cand = arbol.query(p, k=12)
    for k in range(cand.shape[1]):
        t = cand[:, k]; a, b, cc = xy[tri[t, 0]], xy[tri[t, 1]], xy[tri[t, 2]]
        det = (b[:, 0] - a[:, 0]) * (cc[:, 1] - a[:, 1]) - (cc[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])
        l1 = ((p[:, 0] - a[:, 0]) * (cc[:, 1] - a[:, 1]) - (cc[:, 0] - a[:, 0]) * (p[:, 1] - a[:, 1])) / det
        l2 = ((b[:, 0] - a[:, 0]) * (p[:, 1] - a[:, 1]) - (p[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])) / det
        l0 = 1 - l1 - l2; dentro = (np.minimum(np.minimum(l0, l1), l2) >= -1e-9) & (idx[:, 0] < 0)
        idx[dentro] = tri[t[dentro]]; w[dentro] = np.c_[l0, l1, l2][dentro]
    return idx, w


def main():
    xy, tri = lee_hgrid(R / "datos" / "malla" / "hgrid.gr3")
    z = zonas(xy[:, 0], xy[:, 1], malla.en_bahia(xy))
    a = xy[tri]; at = 0.5 * np.abs((a[:, 1, 0] - a[:, 0, 0]) * (a[:, 2, 1] - a[:, 0, 1]) - (a[:, 2, 0] - a[:, 0, 0]) * (a[:, 1, 1] - a[:, 0, 1]))
    area = np.bincount(tri.ravel(), np.repeat(at / 3, 3), minlength=len(xy))
    ex = np.arange(S2["e0"] + S2["d"] / 2, S2["e1"], S2["d"]); ny = np.arange(S2["n0"] + S2["d"] / 2, S2["n1"], S2["d"])
    E, N = np.meshgrid(ex, ny); s2_i, s2_w = pesos(xy, tri, np.c_[E.ravel(), N.ravel()])
    t = np.radians(RUMBO); es = np.array([np.sin(t), np.cos(t)]); en = np.array([np.cos(t), -np.sin(t)])
    nn = np.arange(-300, 301, 10.0); sec = np.array(CENTRO) + nn[:, None] * en
    sec_i, sec_w = pesos(xy, tri, sec); ok = sec_i[:, 0] >= 0
    out = R / "datos" / "conjunto" / "posproceso_malla.npz"; out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, zona=z.astype(np.int8), area=area, s2_i=s2_i.astype(np.int32), s2_w=s2_w.astype(np.float32),
                        s2_forma=np.array(E.shape), s2_e=ex, s2_n=ny, sec_i=sec_i[ok], sec_w=sec_w[ok], sec_dn=10.0, sec_dir=es)
    # autoprueba: los pesos reproducen un campo lineal y el area total coincide con la de los triangulos
    f = 3 * xy[:, 0] - 2 * xy[:, 1]; g = (f[s2_i] * s2_w).sum(1); m = s2_i[:, 0] >= 0
    assert np.allclose(g[m], (3 * E.ravel() - 2 * N.ravel())[m]) and np.isclose(area.sum(), at.sum())
    print(f"{out}: rejilla S2 {E.shape} ({m.mean():.0%} dentro de la malla), seccion del canal {ok.sum()} puntos "
          f"({ok.sum() * 10:.0f} m de ancho), zonas {np.bincount(z)}")


if __name__ == "__main__":
    main()
