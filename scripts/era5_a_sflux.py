#!/usr/bin/env python3
"""ERA5 (datos/forzamiento/era5) -> formato sflux de SCHISM, un archivo por mes y tipo.
Uso:  conda activate bahia && python scripts/era5_a_sflux.py
Salida: datos/forzamiento/sflux/sflux_{air,rad,prc}_AAAAMM.nc  (base_date = dia 1, 00 UTC)
Cada caso enlaza los meses que necesite como sflux/sflux_air_1.N.nc (ver caso_prueba.py).

  air: uwind, vwind [m/s], prmsl [Pa], stmp [K], spfh [kg/kg] (de d2m y msl)
  rad: dswrf, dlwrf [W/m2]   = acumulado horario / 3600
  prc: prate [kg/m2/s]       = tp [m] * 1000 / 3600
Los acumulados de ERA5 cubren la hora anterior a valid_time: se fechan en el centro (-30 min).
"""
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

RAIZ = Path(__file__).resolve().parent.parent
ERA5 = RAIZ / "datos" / "forzamiento" / "era5"
OUT = RAIZ / "datos" / "forzamiento" / "sflux"


def humedad_especifica(d2m, msl):
    """Punto de rocio [K] y presion [Pa] -> humedad especifica [kg/kg] (Bolton 1980)."""
    td = d2m - 273.15
    e = 611.2 * np.exp(17.67 * td / (td + 243.5))
    return 0.622 * e / (msl - 0.378 * e)


def escribir(ruta, tipo, lon, lat, dias, base, campos):
    with Dataset(ruta, "w") as nc:
        nc.createDimension("time", None)
        nc.createDimension("ny_grid", lat.size)
        nc.createDimension("nx_grid", lon.size)
        t = nc.createVariable("time", "f8", ("time",))
        t.units = f"days since {base[0]:04d}-{base[1]:02d}-01"
        t.base_date = np.array(base, dtype="i4")
        t[:] = dias
        LON, LAT = np.meshgrid(lon, lat)
        for nombre, val in (("lon", LON), ("lat", LAT)):
            v = nc.createVariable(nombre, "f4", ("ny_grid", "nx_grid"))
            v[:] = val
        for nombre, (datos, unidades) in campos.items():
            v = nc.createVariable(nombre, "f4", ("time", "ny_grid", "nx_grid"))
            v.units = unidades
            v[:] = datos
        nc.Conventions = "CF-1.0"
        nc.source = f"ERA5 hourly single levels ({tipo}), convertido por era5_a_sflux.py"


def mes(base_nombre):
    yyyymm = base_nombre[-6:]
    base = [int(yyyymm[:4]), int(yyyymm[4:]), 1, 0]
    with Dataset(ERA5 / f"{base_nombre}_instant.nc") as i, Dataset(ERA5 / f"{base_nombre}_accum.nc") as a:
        lat = i["latitude"][:]
        s = np.argsort(lat)                        # SCHISM: latitud creciente (sur -> norte)
        lat, lon = lat[s], i["longitude"][:]
        t0 = np.datetime64(f"{yyyymm[:4]}-{yyyymm[4:]}-01T00:00", "s")
        def dias(nc):
            u = nc["valid_time"].units          # "seconds since 1970-01-01"
            assert u.startswith("seconds since 1970-01-01"), u
            return (nc["valid_time"][:].astype("i8") - (t0 - np.datetime64("1970-01-01T00:00", "s")).astype("i8")) / 86400.0
        g = lambda nc, v: np.asarray(nc[v][:], dtype="f4")[:, s, :]
        di, da = dias(i), dias(a) - 0.5 / 24
        msl = g(i, "msl")
        escribir(OUT / f"sflux_air_{yyyymm}.nc", "air", lon, lat, di, base, {
            "uwind": (g(i, "u10"), "m/s"), "vwind": (g(i, "v10"), "m/s"),
            "prmsl": (msl, "Pa"), "stmp": (g(i, "t2m"), "K"),
            "spfh": (humedad_especifica(g(i, "d2m"), msl), "1")})
        escribir(OUT / f"sflux_rad_{yyyymm}.nc", "rad", lon, lat, da, base, {
            "dswrf": (np.clip(g(a, "ssrd"), 0, None) / 3600, "W/m^2"),
            "dlwrf": (np.clip(g(a, "strd"), 0, None) / 3600, "W/m^2")})
        escribir(OUT / f"sflux_prc_{yyyymm}.nc", "prc", lon, lat, da, base, {
            "prate": (np.clip(g(a, "tp"), 0, None) * 1000 / 3600, "kg/m^2/s")})


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    meses = sorted(p.name[:-len("_instant.nc")] for p in ERA5.glob("era5_habana_??????_instant.nc"))
    assert len(meses) == 120, len(meses)
    for m in meses:
        mes(m)
    # comprobacion rapida sobre un mes: rangos fisicos
    with Dataset(OUT / "sflux_air_201607.nc") as a, Dataset(OUT / "sflux_rad_201607.nc") as r:
        q, v = a["spfh"][:], np.hypot(a["uwind"][:], a["vwind"][:])
        sw = r["dswrf"][:]
        print(f"jul-2016: viento medio {v.mean():.1f} m/s, q {q.min():.4f}-{q.max():.4f} kg/kg, "
              f"SW medio {sw.mean():.0f} W/m2 (max {sw.max():.0f}), t0 air {a['time'][0]:.3f} d, rad {r['time'][0]:.4f} d")
        assert 0.010 < q.mean() < 0.025 and 2 < v.mean() < 10 and 150 < sw.mean() < 350
    print(f"sflux: {len(meses)} meses en {OUT}")
