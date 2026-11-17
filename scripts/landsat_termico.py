#!/usr/bin/env python3
"""V3 X3: contraste termico bahia-mar con Landsat 8/9 Collection 2 Level 2 (temperatura superficial, banda ST_B10), solo datos publicos.
Lectura fijada en docs/protocolo_metricas_conjunto.md (17-nov (3)) ANTES de descargar ninguna escena.
  python scripts/landsat_termico.py descarga   (Mac con red; pip install pystac-client planetary-computer rasterio) -> datos/landsat/escenas.csv
  python scripts/landsat_termico.py analiza    -> resultados/landsat_termico.txt
  python scripts/landsat_termico.py --prueba   (solo el nucleo numerico, datos sinteticos)
SIN PROBAR contra el servicio real: el acceso (STAC de Microsoft Planetary Computer, coleccion landsat-c2-l2, sin registro) y los nombres de activos hay que comprobarlos en la primera ejecucion."""
import csv, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent; OUT = RAIZ / "datos" / "landsat"
BAHIA_BOX = (-82.38, 23.10, -82.30, 23.17)                       # lon0, lat0, lon1, lat1 (solo para la consulta; la mascara sale de la malla)
MAR_A, MAR_B = (-82.42, 23.22, -82.34, 23.27), (-82.28, 23.22, -82.20, 23.27)   # mar abierto, ~8-13 km al norte de la costa; B es el par de control
NMIN_BAHIA, NMIN_MAR, NMIN_ESCENAS = 30, 200, 8
FRIA, CALIDA = (11, 12, 1, 2, 3), (6, 7, 8, 9)                   # nov-mar (frentes frios) y jun-sep


def st_celsius(dn, qa):
    """ST_B10 (DN) -> C con la escala de Collection 2 (0,00341802 y 149,0 K); QA_PIXEL: se descartan relleno (bit 0), nube dilatada (1), nube (3), sombra (4); agua = bit 7."""
    dn = np.asarray(dn, float); qa = np.asarray(qa).astype(int); malo = (dn <= 0) | ((qa >> 0) & 1) | ((qa >> 1) & 1) | ((qa >> 3) & 1) | ((qa >> 4) & 1)
    return np.where(malo | (((qa >> 7) & 1) == 0), np.nan, dn * 0.00341802 + 149.0 - 273.15)


def escena(T, mb, ma, mc):
    """T (C) y mascaras booleanas de bahia, mar A y mar B -> (T_bahia, T_A, T_B) = medianas, o None si hay pocos pixeles validos."""
    n = [np.isfinite(T[m]).sum() for m in (mb, ma, mc)]
    if n[0] < NMIN_BAHIA or n[1] < NMIN_MAR or n[2] < NMIN_MAR: return None
    return tuple(float(np.nanmedian(T[m])) for m in (mb, ma, mc))


def ic(x, n=2000, seed=20261117):
    x = np.asarray(x, float); r = np.random.default_rng(seed); b = np.median(x[r.integers(0, len(x), (n, len(x)))], 1); return float(np.median(x)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def lectura(meses, dT, dctrl, modelo=None):
    """meses, dT = T_bahia - (T_A + T_B)/2, dctrl = T_A - T_B por escena. modelo = {'fria': c, 'calida': c} (T_bahia - T_borde medio del modelo con calor, 2016) o None."""
    meses, dT, dctrl = map(np.asarray, (meses, dT, dctrl)); sp = float(np.percentile(np.abs(dctrl), 95)); o = [f"escenas validas {len(dT)}; control mar-mar: |T_A - T_B| P95 = {sp:.2f} C (suelo de ruido)"]; r = {}
    for nom, ms in (("fria (nov-mar)", FRIA), ("calida (jun-sep)", CALIDA)):
        s = np.isin(meses, ms); n = int(s.sum())
        if n < NMIN_ESCENAS: o.append(f"  {nom}: {n} escenas < {NMIN_ESCENAS}: no estimable"); r[nom] = None; continue
        m, lo, hi = ic(dT[s]); r[nom] = (m, lo, hi); o.append(f"  {nom}: n = {n}, T_bahia - T_mar mediana {m:+.2f} C (IC95 {lo:+.2f} a {hi:+.2f}); control mediano {np.median(dctrl[s]):+.2f}")
    f, c = r.get("fria (nov-mar)"), r.get("calida (jun-sep)")
    if f is None or c is None: v = "NO ESTIMABLE (pocas escenas en una estacion)"
    elif f[2] < 0 and f[0] < c[0] - sp: v = "CONTRASTE FRIO VISIBLE: la bahia es mas fria que el mar en la estacion fria y mas que en la calida por mas que el ruido del control"
    elif f[1] > 0: v = "CONTRADICE: la bahia es MAS CALIDA que el mar en la estacion fria"
    else: v = "NO SE VE contraste frio distinguible del ruido"
    o.append(f"veredicto X3 (observacion): {v}")
    if modelo and f is not None and c is not None:
        ok = [np.sign(modelo[k]) == np.sign(r[n][0]) and abs(modelo[k] - r[n][0]) <= max(0.5, sp) for k, n in (("fria", "fria (nov-mar)"), ("calida", "calida (jun-sep)"))]
        o.append(f"modelo con calor (2016): fria {modelo['fria']:+.2f}, calida {modelo['calida']:+.2f} C -> " + ("COMPATIBLE con la observacion (signo y diferencia <= max(0,5 C, ruido) en las dos estaciones)" if all(ok) else "NO compatible en " + " y ".join(k for k, b in zip(("fria", "calida"), ok) if not b)))
    return o, v


def descarga():
    import planetary_computer as pc, pystac_client, rasterio
    from rasterio.windows import from_bounds
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
    items = cat.search(collections=["landsat-c2-l2"], bbox=BAHIA_BOX, datetime="2014-01-01/2025-12-31", query={"platform": {"in": ["landsat-8", "landsat-9"]}, "eo:cloud_cover": {"lt": 40}}).item_collection()
    print(len(items), "escenas con nubosidad < 40 %"); OUT.mkdir(parents=True, exist_ok=True)
    ll = [l.split() for l in open(next((RAIZ / "runs").glob("*/m0000/hgrid.ll"))).read().splitlines()]; ne, nn = map(int, ll[1][:2]); nodos = np.array([[float(x) for x in l[1:3]] for l in ll[2:2 + nn]])
    M = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz"); bahia = nodos[M["zona"] > 0]
    filas = []
    for it in items:
        try:
            it = pc.sign(it)   # la firma de la busqueda caduca (~1 h): sin esto las escenas viejas daban 403 (17-nov)
            with rasterio.open(it.assets["lwir11"].href) as a, rasterio.open(it.assets["qa_pixel"].href) as q:
                from rasterio.warp import transform_bounds
                bb = transform_bounds("EPSG:4326", a.crs, MAR_A[0], BAHIA_BOX[1], MAR_B[2], MAR_A[3]); w = from_bounds(*bb, a.transform)
                dn, qa = a.read(1, window=w), q.read(1, window=w); tr = a.window_transform(w)
                ny, nx = dn.shape; cols, rows = np.meshgrid(np.arange(nx) + 0.5, np.arange(ny) + 0.5); xs, ys = tr * (cols, rows)
                from rasterio.warp import transform as tf
                lon, lat = tf(a.crs, "EPSG:4326", xs.ravel(), ys.ravel()); lon, lat = np.array(lon).reshape(ny, nx), np.array(lat).reshape(ny, nx)
        except Exception as e:
            print(it.id, "fallo:", e); continue
        T = st_celsius(dn, qa); caja = lambda b: (lon >= b[0]) & (lon <= b[2]) & (lat >= b[1]) & (lat <= b[3])
        d = np.full(lon.shape, np.inf)
        for k0 in range(0, lon.size, 20000):                                       # distancia aproximada (m) al nodo de bahia mas cercano
            sl = slice(k0, k0 + 20000); dx = (lon.ravel()[sl, None] - bahia[None, :, 0]) * 102000; dy = (lat.ravel()[sl, None] - bahia[None, :, 1]) * 111000
            d.ravel()[sl] = np.sqrt(dx ** 2 + dy ** 2).min(1)
        mb = (d <= 150) & caja(BAHIA_BOX); r = escena(T, mb, caja(MAR_A), caja(MAR_B))
        if r: filas.append([it.id, it.datetime.date().isoformat(), it.datetime.month, it.properties["platform"], *[f"{x:.3f}" for x in r]])
    w = csv.writer(open(OUT / "escenas.csv", "w", newline="")); w.writerow(["id", "fecha", "mes", "plataforma", "T_bahia", "T_marA", "T_marB"]); w.writerows(filas); print(len(filas), "escenas validas ->", OUT / "escenas.csv")


def analiza():
    E = list(csv.DictReader(open(OUT / "escenas.csv"))); mes = [int(e["mes"]) for e in E]; tb, ta, tc = (np.array([float(e[k]) for e in E]) for k in ("T_bahia", "T_marA", "T_marB"))
    modelo = None
    try:
        f = list(csv.DictReader(open(RAIZ / "runs" / "termico" / "m0000" / "termico_diario.csv"))); ss = {r["fecha"]: float(r["sst_C"]) for r in csv.DictReader(open(RAIZ / "datos" / "forzamiento" / "sst" / "oisst_habana.csv"))}
        d = np.array([float(r["T_bahia_sup"]) - ss[str(np.datetime64("2016-01-01") + i)] for i, r in enumerate(f)]); m = np.array([int(str(np.datetime64("2016-01-01") + i)[5:7]) for i in range(len(f))])
        modelo = {"fria": float(d[np.isin(m, FRIA)].mean()), "calida": float(d[np.isin(m, CALIDA)].mean())}
    except (OSError, KeyError): pass
    o, _ = lectura(mes, tb - (ta + tc) / 2, ta - tc, modelo); t = "\n".join(o); print(t); (RAIZ / "resultados" / "landsat_termico.txt").write_text(t + "\n")


def prueba():
    dn = np.array([[22000, 22000], [22000, 0]]); qa = np.array([[1 << 7, 1 << 7], [1 << 7 | 1 << 3, 1 << 7]]); T = st_celsius(dn, qa)
    assert abs(T[0, 0] - (22000 * 0.00341802 + 149.0 - 273.15)) < 1e-9 and np.isnan(T[1, 0]) and np.isnan(T[1, 1])
    rng = np.random.default_rng(1); n = 60; meses = rng.integers(1, 13, n); frio = np.isin(meses, FRIA)
    dT = np.where(frio, -0.8, 0.2) + 0.3 * rng.normal(size=n); dc = 0.15 * rng.normal(size=n)
    assert lectura(meses, dT, dc)[1].startswith("CONTRASTE FRIO VISIBLE"); assert lectura(meses, 0.2 + 0.3 * rng.normal(size=n), dc)[1].startswith("NO SE VE")
    assert lectura(meses, np.where(frio, 1.0, 0.2) + 0.2 * rng.normal(size=n), dc)[1].startswith("CONTRADICE"); assert lectura(meses[:5], dT[:5], dc[:5])[1].startswith("NO ESTIMABLE")
    assert "COMPATIBLE" in lectura(meses, dT, dc, {"fria": -0.8, "calida": 0.2})[0][-1]
    T2 = np.full((100, 100), 25.0); m = lambda r0, r1, c0, c1: (lambda z: (z.__setitem__((slice(r0, r1), slice(c0, c1)), True), z)[1])(np.zeros((100, 100), bool))
    assert escena(T2, m(0, 6, 0, 6), m(20, 40, 20, 30), m(50, 70, 20, 30)) == (25.0, 25.0, 25.0) and escena(T2, m(0, 6, 0, 6), m(20, 40, 20, 30), m(50, 60, 20, 30)) is None
    print("prueba ok")


if __name__ == "__main__":
    a = sys.argv[1:]; prueba() if a == ["--prueba"] else descarga() if a == ["descarga"] else analiza()
