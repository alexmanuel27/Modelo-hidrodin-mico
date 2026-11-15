#!/usr/bin/env python3
"""Representatividad del viento de enero-abril de 2016 frente a 2016-2025 (revision V1; lectura fijada en
protocolo_metricas_conjunto.md, 14-nov (2)). Lee los sflux de ERA5 que ya usa el modelo (uwind, vwind), celda mas cercana
a (23.14 N, -82.35 E) y los mismos 120 dias desde el 1 de enero de cada anio. Necesita netCDF4 (en el cluster:
module load releases/2024a netcdf4-python/1.7.1.post2-foss-2024a).
  python scripts/viento_interanual.py [datos/forzamiento/sflux]  -> resultados/viento_interanual.csv y tabla en pantalla
  python scripts/viento_interanual.py --prueba"""
import sys
from pathlib import Path
import numpy as np

LAT, LON, DIAS, ANIOS = 23.14, -82.35, 120, range(2016, 2026)


def metricas(u, v):
    """(a) rapidez media, (b) direccion de la media vectorial (de donde sopla, grados), (c) P90 de la rapidez."""
    rap = np.hypot(u, v)
    return rap.mean(), (270.0 - np.degrees(np.arctan2(v.mean(), u.mean()))) % 360.0, np.percentile(rap, 90)


def dif_dir(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def lee_anio(sflux, y):
    from netCDF4 import Dataset
    u, v = [], []
    for m in range(1, 5):
        with Dataset(sflux / f"sflux_air_{y}{m:02d}.nc") as d:
            lat, lon = np.asarray(d["lat"][:]), np.asarray(d["lon"][:])
            j, i = np.unravel_index(np.argmin((lat - LAT) ** 2 + (lon - LON) ** 2), lat.shape)
            u.append(np.asarray(d["uwind"][:, j, i], float)); v.append(np.asarray(d["vwind"][:, j, i], float))
    u, v = np.concatenate(u)[:DIAS * 24], np.concatenate(v)[:DIAS * 24]
    assert len(u) == DIAS * 24, (y, len(u))
    return u, v, (float(lat[j, i]), float(lon[j, i]))


def prueba():
    u = np.full(10, -3.0); v = np.full(10, -4.0)           # viento del NE: de 36.87 grados, 5 m/s
    a, b, c = metricas(u, v); assert abs(a - 5) < 1e-9 and abs(b - 36.8699) < 1e-3 and abs(c - 5) < 1e-9, (a, b, c)
    assert abs(dif_dir(350.0, 10.0) + 20.0) < 1e-9 and abs(dif_dir(10.0, 350.0) - 20.0) < 1e-9
    print("prueba ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--prueba"]: prueba(); sys.exit()
    sflux = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "datos" / "forzamiento" / "sflux"
    res = {}
    for y in ANIOS:
        u, v, celda = lee_anio(sflux, y); res[y] = metricas(u, v)
    print(f"celda ERA5 usada: {celda[0]:.3f} N, {celda[1]:.3f} E; 120 d desde el 1-ene")
    a0, b0, c0 = res[2016]
    print("anio  rapidez_media(m/s)  dir_media(grados)  P90(m/s) | a/a2016  c/c2016  dir-dir2016 | dentro 0,8-1,2 y +-15")
    filas = ["anio,rapidez_media,dir_media,p90,a_sobre_2016,c_sobre_2016,dir_menos_2016,dentro"]
    for y in ANIOS:
        a, b, c = res[y]; ra, rc, db = a / a0, c / c0, dif_dir(b, b0)
        dentro = 0.8 <= ra <= 1.2 and 0.8 <= rc <= 1.2 and abs(db) <= 15
        print(f"{y}  {a:6.2f}  {b:7.1f}  {c:6.2f} | {ra:5.2f}  {rc:5.2f}  {db:+6.1f} | {'si' if dentro else 'NO'}")
        filas.append(f"{y},{a:.3f},{b:.1f},{c:.3f},{ra:.3f},{rc:.3f},{db:.1f},{'si' if dentro else 'NO'}")
    for k, nom in enumerate(("rapidez media", "direccion media", "P90")):
        v = np.array([res[y][k] for y in ANIOS]); rk = int((v > res[2016][k]).sum()) + 1
        print(f"{nom}: 2016 = {res[2016][k]:.2f}, rango de la decada {v.min():.2f}-{v.max():.2f}, puesto {rk} de {len(v)} (1 = mayor)")
    out = Path(__file__).resolve().parent.parent / "resultados" / "viento_interanual.csv"
    out.parent.mkdir(exist_ok=True); out.write_text("\n".join(filas) + "\n")
