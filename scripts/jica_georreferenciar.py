#!/usr/bin/env python3
"""Georreferencia las 11 estaciones de la fig. 4.25 de JICA 2004 (vol. V) sobre la malla del modelo.
Metodo y criterios de aceptacion fijados en la enmienda A1 de docs/protocolo_jica_observaciones.md (f9c1b00), antes de ejecutarlo:
ajuste por mascara (IoU entre el agua de la figura y los elementos con zona > 0 de la malla), similitud (giro, traslacion, escala),
aceptada si IoU >= 0,75 y 45 <= s <= 75 m/unidad; comprobacion con las bocas de Luyano, Martin Perez y Tadeo (tabla 4.8, celdas/2).
  python scripts/jica_georreferenciar.py            -> resultados/jica_estaciones.txt, datos/observaciones/jica2004_estaciones_utm.csv,
                                                       resultados/jica_georreferencia.png
  python scripts/jica_georreferenciar.py --prueba   -> el ajuste recupera una transformacion conocida"""
import csv, json, subprocess, sys, unicodedata
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts" / "batimetria"))
from utm import utm                                              # noqa: E402

FUENTES = RAIZ / "datos" / "batimetria" / "fuentes"
PNG = FUENTES / "jica_2004_vol5_03_fig425-02.png"                # pdftoppm -f 2 -l 2 -r 130 -png (pagina de la fig. 4.25)
MARCO = (189, 889, 275, 1019)                                    # px: x(u=0), x(u=60), y(v=65), y(v=0)
UMAX, VMAX = 60.0, 65.0
R, P = 20.0, 768                                                 # m por celda del raster y lado del raster
PASO = 2                                                         # px entre puntos de la mascara de la figura (a 3 px, ~1 punto por celda de 20 m: la cobertura sale < 1 y el IoU sesgado a la baja)
IOU_MIN, S_MIN, S_MAX, DIST_RIOS_MAX = 0.75, 45.0, 75.0, 300.0   # criterios de la enmienda A1


def caja(m, k, op):
    """Dilatacion (op = or) o erosion (op = and) con ventana cuadrada de lado 2k+1."""
    for ax in (0, 1):
        acc = m.copy()
        for d in range(1, k + 1):
            for s in (d, -d): acc = op(acc, np.roll(m, s, axis=ax))
        m = acc
    return m


def mascara_jica():
    """(u, v, peso) de las celdas de agua de la figura: lo que tiene rejilla dibujada dentro del marco, sin leyenda ni rotulos."""
    if not PNG.exists():
        subprocess.run(["pdftoppm", "-f", "2", "-l", "2", "-r", "130", "-png", str(FUENTES / "jica_2004_vol5_03.pdf"), str(PNG)[:-7]], check=True)
    g = np.array(Image.open(PNG).convert("L")).astype(int)
    x0, x1, y0, y1 = MARCO
    nb = np.zeros(g.shape, bool); nb[y0 + 3:y1 - 2, x0 + 3:x1 - 2] = g[y0 + 3:y1 - 2, x0 + 3:x1 - 2] < 235
    nb[:365, :720] = False                                       # leyenda
    cerr = caja(caja(nb, 7, np.logical_or), 7, np.logical_and)
    ext = np.zeros(g.shape, bool); ext[0, 0] = True
    while True:                                                  # el exterior es lo conectado con la esquina
        nuevo = caja(ext, 2, np.logical_or) & ~cerr
        if (nuevo == ext).all(): break
        ext = nuevo
    m = ~ext; m[:y0 + 3] = m[y1 - 2:] = False; m[:, :x0 + 3] = m[:, x1 - 2:] = False
    m = caja(caja(m, 6, np.logical_and), 6, np.logical_or)
    ys, xs = np.nonzero(m[::PASO, ::PASO]); xs, ys = xs * PASO + PASO / 2, ys * PASO + PASO / 2
    du, dv = UMAX / (x1 - x0), VMAX / (y1 - y0)
    return (xs - x0) * du, (y1 - ys) * dv, np.full(len(xs), PASO * PASO * du * dv), m


def lee_malla():
    L = (RAIZ / "datos" / "malla" / "hgrid.gr3").read_text().split("\n"); ne, nn = map(int, L[1].split())
    nod = np.array([l.split()[1:4] for l in L[2:2 + nn]], float); tri = np.array([l.split()[2:5] for l in L[2 + nn:2 + nn + ne]], int) - 1
    zona = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz")["zona"]
    return nod, tri, zona


def mascara_modelo(nod, tri, zona, c):
    """Raster de P x P celdas de R m centrado en c = (E, N): 1 donde cae un elemento con sus tres nodos en la bahia (zona > 0)."""
    M = np.zeros((P, P))
    for t in tri[(zona[tri] > 0).all(1)]:
        a, b, d = nod[t, :2] - c; lo = np.floor(np.minimum(np.minimum(a, b), d) / R).astype(int) + P // 2; hi = np.ceil(np.maximum(np.maximum(a, b), d) / R).astype(int) + P // 2
        ix, iy = np.meshgrid(np.arange(lo[0], hi[0] + 1), np.arange(lo[1], hi[1] + 1)); p = np.c_[(ix.ravel() + .5 - P // 2) * R, (iy.ravel() + .5 - P // 2) * R]
        det = (b[1] - d[1]) * (a[0] - d[0]) + (d[0] - b[0]) * (a[1] - d[1])
        l1 = ((b[1] - d[1]) * (p[:, 0] - d[0]) + (d[0] - b[0]) * (p[:, 1] - d[1])) / det; l2 = ((d[1] - a[1]) * (p[:, 0] - d[0]) + (a[0] - d[0]) * (p[:, 1] - d[1])) / det
        k = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1); M[iy.ravel()[k], ix.ravel()[k]] = 1
    return M


def gira(u, v, s, th, refl):
    """Metros relativos al centroide de la mascara: escala s, reflexion opcional del eje v y giro th (rad)."""
    X, Y = (u - u.mean()) * s, (v - v.mean()) * s * (-1 if refl else 1)
    return np.cos(th) * X - np.sin(th) * Y, np.sin(th) * X + np.cos(th) * Y


def evalua(u, v, w, FM, AM, s, th, refl):
    xr, yr = gira(u, v, s, th, refl); J = np.zeros((P, P))
    np.add.at(J, (np.floor(yr / R).astype(int) + P // 2, np.floor(xr / R).astype(int) + P // 2), w * s * s / R ** 2); J = np.minimum(J, 1)
    C = np.fft.irfft2(np.conj(np.fft.rfft2(J)) * FM, s=(P, P)); iou = C / (J.sum() + AM - C); k = np.unravel_index(np.argmax(iou), iou.shape)
    return iou[k], (k[1] if k[1] < P // 2 else k[1] - P) * R, (k[0] if k[0] < P // 2 else k[0] - P) * R


def ajusta(u, v, w, M):
    FM, AM = np.fft.rfft2(M), M.sum(); mejor = (-1,)
    for refl in (False, True):
        for s in (50., 60., 70.):
            for th in np.deg2rad(np.arange(0, 360, 3)):
                r = evalua(u, v, w, FM, AM, s, th, refl)
                if r[0] > mejor[0]: mejor = (*r, s, th, refl)
    _, _, _, s0, th0, refl = mejor
    for s in np.arange(s0 - 5, s0 + 5.1, 1.0):
        for th in th0 + np.deg2rad(np.arange(-3, 3.1, 0.25)):
            r = evalua(u, v, w, FM, AM, s, th, refl)
            if r[0] > mejor[0]: mejor = (*r, s, th, refl)
    return dict(iou=mejor[0], tx=mejor[1], ty=mejor[2], s=mejor[3], th=mejor[4], refl=mejor[5])


def a_utm(u, v, aj, uc, vc, c):
    """(u, v) de la figura -> (E, N) UTM, con el centroide (uc, vc) de la mascara y el centro c del raster."""
    X, Y = (np.asarray(u) - uc) * aj["s"], (np.asarray(v) - vc) * aj["s"] * (-1 if aj["refl"] else 1)
    return c[0] + aj["tx"] + np.cos(aj["th"]) * X - np.sin(aj["th"]) * Y, c[1] + aj["ty"] + np.sin(aj["th"]) * X + np.cos(aj["th"]) * Y


def bocas_osm(nombres, nod, tri, zona):
    plano = lambda t: unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    vias = json.loads((FUENTES / "osm_rios_habana.json").read_text())["elements"]
    ok = (zona[tri] > 0).all(1); cen = nod[tri[ok], :2].mean(1); out = {}
    for n in nombres:
        pts = np.array([(g["lon"], g["lat"]) for v in vias if n in plano(v.get("tags", {}).get("name", "")) for g in v.get("geometry", [])])
        E, N = utm(*pts.T); d = np.hypot(E[:, None] - cen[None, :, 0], N[:, None] - cen[None, :, 1]); i = np.unravel_index(np.argmin(d), d.shape)[0]
        out[n] = (float(E[i]), float(N[i]))
    return out


def prueba():
    nod, tri, zona = lee_malla(); b = nod[zona > 0, :2]; c = (b.min(0) + b.max(0)) / 2; M = mascara_modelo(nod, tri, zona, c)
    yy, xx = np.nonzero(M); yy, xx = np.repeat(yy, 4), np.repeat(xx, 4); o = np.tile([.25, .75], 2 * len(xx) // 4)   # 4 puntos por celda, cada 10 m
    E = (xx + o[:len(xx)] - P // 2) * R; N = (yy + np.tile([.25, .25, .75, .75], len(xx) // 4) - P // 2) * R
    s, th = 60., np.deg2rad(37.)                                 # JICA = modelo girado -th y escalado 1/s, con reflexion
    u, v = (np.cos(-th) * E - np.sin(-th) * N) / s, -(np.sin(-th) * E + np.cos(-th) * N) / s
    cy, cx = [(x.mean() + .5 - P // 2) * R for x in np.nonzero(M)]                          # centroide del modelo = traslacion esperada
    aj = ajusta(u + 3.1, v - 2.2, np.full(len(u), (R / 2 / s) ** 2), M)
    assert aj["iou"] > 0.95 and aj["refl"] and abs(aj["s"] - 60) <= 1 and abs(np.rad2deg(aj["th"]) - 37) <= 1.5 and abs(aj["tx"] - cx) <= R and abs(aj["ty"] - cy) <= R, aj
    print("prueba ok", {k: round(float(x), 2) for k, x in aj.items() if k != "refl"})


def main():
    nod, tri, zona = lee_malla(); b = nod[zona > 0, :2]; c = (b.min(0) + b.max(0)) / 2
    u, v, w, mj = mascara_jica(); M = mascara_modelo(nod, tri, zona, c); uc, vc = u.mean(), v.mean(); aj = ajusta(u, v, w, M)
    obs = list(csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_vol5.csv")))
    est = {r["estacion"]: {} for r in obs if r["tabla"] == "Fig. 4.25" and r["variable"] == "x_figura"}
    for r in obs:
        if r["tabla"] == "Fig. 4.25" and r["variable"] in ("x_figura", "y_figura") and r["estacion"] in est: est[r["estacion"]][r["variable"][0]] = float(r["valor"])
    src = {r["estacion"].split()[0]: {} for r in obs if r["tabla"] == "4.8"}
    for r in obs:
        if r["tabla"] == "4.8" and r["variable"] in ("x_celda", "y_celda"): src[r["estacion"].split()[0]][r["variable"][0]] = float(r["valor"])
    area_jica = w.sum() * aj["s"] ** 2 / 1e6; area_mod = M.sum() * R * R / 1e6
    o = [f"Ajuste por mascara (enmienda A1): reflexion del eje v = {aj['refl']}, giro = {np.rad2deg(aj['th']):.2f} grados, escala = {aj['s']:.1f} m/unidad, IoU = {aj['iou']:.3f}",
         f"  area de la mascara de la figura a esa escala = {area_jica:.2f} km2 (JICA da 5,2 km2 para la bahia); area de la mascara del modelo (zona > 0) = {area_mod:.2f} km2",
         f"  traslacion respecto al centro del raster = ({aj['tx']:.0f}, {aj['ty']:.0f}) m"]
    bocas = bocas_osm(["luyano", "martin perez", "tadeo"], nod, tri, zona); dist = []
    for sid, nom in (("S1", "luyano"), ("S2", "martin perez"), ("S3", "tadeo")):
        E, N = a_utm(src[sid]["x"] / 2, src[sid]["y"] / 2, aj, uc, vc, c); d = float(np.hypot(E - bocas[nom][0], N - bocas[nom][1])); dist.append(d)
        o.append(f"  boca {nom}: JICA ({src[sid]['x']:.0f}, {src[sid]['y']:.0f}) -> ({E:.0f}, {N:.0f}) UTM; OSM ({bocas[nom][0]:.0f}, {bocas[nom][1]:.0f}); distancia {d:.0f} m")
    ok = aj["iou"] >= IOU_MIN and S_MIN <= aj["s"] <= S_MAX and np.median(dist) <= DIST_RIOS_MAX
    o.append(f"  mediana de la distancia a las 3 bocas = {np.median(dist):.0f} m (umbral {DIST_RIOS_MAX:.0f}); IoU >= {IOU_MIN}: {aj['iou'] >= IOU_MIN}; "
             f"escala en [{S_MIN:.0f}, {S_MAX:.0f}]: {S_MIN <= aj['s'] <= S_MAX}")
    o.append("  ==> TRANSFORMACION " + ("ACEPTADA" if ok else "RECHAZADA (b) y (c) quedan no evaluables"))
    ib = np.where(zona > 0)[0]; filas = []
    o.append("Estaciones (nodo de la bahia mas cercano; zona 1 = canal, 2 = cuenca, 3 = Marimelena, 4 = Guasabacoa, 5 = Atares; prof = z del hgrid):")
    for k in sorted(est, key=int):
        E, N = a_utm(est[k]["x"], est[k]["y"], aj, uc, vc, c); d = np.hypot(nod[ib, 0] - E, nod[ib, 1] - N); j = ib[np.argmin(d)]
        n150 = int((d <= 150).sum()); filas.append([k, f"{float(E):.1f}", f"{float(N):.1f}", int(zona[j]), int(j) + 1, f"{d.min():.0f}", f"{nod[j, 2]:.1f}", n150])
        o.append(f"  {k:>2}: E {float(E):.0f} N {float(N):.0f} | nodo {j + 1} zona {zona[j]} a {d.min():.0f} m, prof {nod[j, 2]:.1f} m | nodos de la bahia a <= 150 m: {n150}")
    o.append("Otros drenajes de la tabla 4.8 con la misma transformacion (celdas/2):")
    for sid in ("S4", "S5", "S6"):
        E, N = a_utm(src[sid]["x"] / 2, src[sid]["y"] / 2, aj, uc, vc, c); d = np.hypot(nod[ib, 0] - E, nod[ib, 1] - N); j = ib[np.argmin(d)]
        o.append(f"  {sid}: ({float(E):.0f}, {float(N):.0f}) -> nodo {j + 1} zona {zona[j]} a {d.min():.0f} m")
    t = "\n".join(o); print(t); (RAIZ / "resultados" / "jica_estaciones.txt").write_text(t + "\n")
    with open(RAIZ / "datos" / "observaciones" / "jica2004_estaciones_utm.csv", "w", newline="") as fh:
        w_ = csv.writer(fh); w_.writerow(["estacion", "E_utm17n", "N_utm17n", "zona", "nodo", "dist_nodo_m", "prof_hgrid_m", "nodos_a_150m"]); w_.writerows(filas)
    # diagnostico: modelo (gris), mascara de la figura transformada (rojo) y estaciones
    S = 2; img = Image.new("RGB", (P * S // 2, P * S // 2), "white"); px = img.load()
    for iy, ix in zip(*np.nonzero(M)): px[ix * S // 2 % img.width, (P - 1 - iy) * S // 2 % img.height] = (190, 190, 190)
    xr, yr = gira(u, v, aj["s"], aj["th"], aj["refl"])
    for X, Y in zip(xr + aj["tx"], yr + aj["ty"]):
        ix, iy = int(X / R + P // 2) * S // 2, int(P - 1 - (Y / R + P // 2)) * S // 2
        if 0 <= ix < img.width and 0 <= iy < img.height: px[ix, iy] = (220, 60, 60)
    dr = ImageDraw.Draw(img)
    for f_ in filas:
        ix, iy = (float(f_[1]) - c[0]) / R + P // 2, P - 1 - ((float(f_[2]) - c[1]) / R + P // 2); dr.ellipse([ix * S // 2 - 4, iy * S // 2 - 4, ix * S // 2 + 4, iy * S // 2 + 4], outline="blue"); dr.text((ix * S // 2 + 6, iy * S // 2 - 5), f_[0], fill="blue")
    img.save(RAIZ / "resultados" / "jica_georreferencia.png")


if __name__ == "__main__":
    prueba() if sys.argv[1:] == ["--prueba"] else main()
