#!/usr/bin/env python3
"""Descarga ERA5 horario (single levels) sobre La Habana, 2016-2025, un mes por peticion.
Uso:  conda activate bahia && python scripts/descargar_era5.py
Necesita ~/.cdsapirc. Se puede interrumpir y relanzar: salta los meses ya bajados.

El CDS devuelve un ZIP (aunque se pida "unarchived") porque mezcla variables instantaneas
y acumuladas. Cada mes queda en dos NetCDF:
  era5_habana_AAAAMM_instant.nc  u10, v10, msl, t2m, d2m
  era5_habana_AAAAMM_accum.nc    ssrd, strd, tp  (acumulados en la hora previa)
"""
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "datos" / "forzamiento" / "era5"
AREA = [23.5, -82.8, 22.8, -81.9]          # N, O, S, E
VARS = ["10m_u_component_of_wind", "10m_v_component_of_wind",
        "mean_sea_level_pressure", "2m_temperature", "2m_dewpoint_temperature",
        "surface_solar_radiation_downwards", "surface_thermal_radiation_downwards",
        "total_precipitation"]


def desempaquetar(z, base):
    """ZIP del CDS -> base_instant.nc y base_accum.nc. Borra el ZIP."""
    with zipfile.ZipFile(z) as zf:
        for m in zf.namelist():
            tipo = "instant" if "instant" in m else "accum" if "accum" in m else None
            if tipo is None:
                raise ValueError(f"{z}: miembro inesperado {m}")
            dst = OUT / f"{base}_{tipo}.nc"
            dst.write_bytes(zf.read(m))
    z.unlink()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Descargas antiguas: ZIP guardado como era5_habana_AAAAMM.nc
    for z in sorted(OUT.glob("era5_habana_??????.nc")):
        if zipfile.is_zipfile(z):
            desempaquetar(z, z.stem)
    c = None
    for year in range(2016, 2026):
        for month in range(1, 13):
            base = f"era5_habana_{year}{month:02d}"
            if (OUT / f"{base}_instant.nc").exists() and (OUT / f"{base}_accum.nc").exists():
                continue
            if c is None:
                import cdsapi
                c = cdsapi.Client()
            tmp = OUT / f"{base}.zip.part"
            print("descargando", base, flush=True)
            c.retrieve("reanalysis-era5-single-levels", {
                "product_type": ["reanalysis"], "variable": VARS,
                "year": [str(year)], "month": [f"{month:02d}"],
                "day": [f"{d:02d}" for d in range(1, 32)],
                "time": [f"{h:02d}:00" for h in range(24)],
                "area": AREA, "data_format": "netcdf", "download_format": "unarchived",
            }, str(tmp))
            desempaquetar(tmp, base)
    print("ERA5 completo en", OUT)


if __name__ == "__main__":
    main()
