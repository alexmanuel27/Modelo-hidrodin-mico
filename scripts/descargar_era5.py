#!/usr/bin/env python3
"""Descarga ERA5 horario (single levels) sobre La Habana, 2016-2025, un fichero por mes.
Uso:  conda activate bahia && python scripts/descargar_era5.py
Necesita ~/.cdsapirc. Se puede interrumpir y relanzar: salta los meses ya bajados.
"""
from pathlib import Path
import cdsapi

OUT = Path(__file__).resolve().parent.parent / "datos" / "forzamiento" / "era5"
OUT.mkdir(parents=True, exist_ok=True)
AREA = [23.5, -82.8, 22.8, -81.9]          # N, O, S, E
VARS = ["10m_u_component_of_wind", "10m_v_component_of_wind",
        "mean_sea_level_pressure", "2m_temperature", "2m_dewpoint_temperature",
        "surface_solar_radiation_downwards", "surface_thermal_radiation_downwards",
        "total_precipitation"]

c = cdsapi.Client()
for year in range(2016, 2026):
    for month in range(1, 13):
        f = OUT / f"era5_habana_{year}{month:02d}.nc"
        if f.exists() and f.stat().st_size > 0:
            continue
        tmp = f.with_suffix(".nc.part")
        print("descargando", f.name, flush=True)
        c.retrieve("reanalysis-era5-single-levels", {
            "product_type": ["reanalysis"], "variable": VARS,
            "year": [str(year)], "month": [f"{month:02d}"],
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": [f"{h:02d}:00" for h in range(24)],
            "area": AREA, "data_format": "netcdf", "download_format": "unarchived",
        }, str(tmp))
        tmp.rename(f)   # solo se da por bajado si termino entero
print("ERA5 completo en", OUT)
