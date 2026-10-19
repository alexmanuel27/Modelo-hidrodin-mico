#!/usr/bin/env python3
"""Marea EOT20 (DGFI-TUM; Hart-Davis et al. 2021, doi:10.17882/79489; CC BY 4.0, descarga directa SIN registro).
Baja el zip de SEANOE (~2 GB), saca solo los archivos de marea oceanica de las constituyentes que usamos,
recorta la misma caja que marea_fes2022.py y guarda datos/marea/eot20_habana.json (mismo formato que FES).
Uso (Mac, entorno bahia):  python scripts/marea_eot20.py        (el zip se borra al final; su sha256 queda en descargas.tsv)"""
import hashlib, json, re, shutil, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

R = Path(__file__).resolve().parent.parent
D, TMP = R / "datos" / "marea", R / "datos" / "forzamiento" / "eot20"
URL = "https://www.seanoe.org/data/00683/79489/data/85762.zip"
CONST = ["m2", "s2", "n2", "k2", "k1", "o1", "p1", "q1", "m4"]       # EOT20 no trae MS4 ni MN4
CAJA = (-82.65, -82.05, 22.95, 23.45)                                  # igual que marea_fes2022.py

D.mkdir(parents=True, exist_ok=True); TMP.mkdir(parents=True, exist_ok=True)
zp = TMP / "eot20.zip"
if not zp.exists():
    print("descargando EOT20 (~2 GB)...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Modelo-hidrodin-mico/1.0 (+https://github.com/alexmanuel27/Modelo-hidrodin-mico)"})
    with urllib.request.urlopen(req, timeout=600) as r, open(zp, "wb") as f: shutil.copyfileobj(r, f, 1 << 22)
h = hashlib.sha256()
with open(zp, "rb") as f:
    for b in iter(lambda: f.read(1 << 24), b""): h.update(b)
reg = D / "descargas.tsv"
if not reg.exists(): reg.write_text("archivo\turl\tfecha_acceso_utc\tbytes\tsha256\n")
with open(reg, "a") as f: f.write(f"eot20.zip\t{URL}\t{datetime.now(timezone.utc):%Y-%m-%dT%H:%MZ}\t{zp.stat().st_size}\t{h.hexdigest()}\n")

out = {}
with zipfile.ZipFile(zp) as z:
    nc = [n for n in z.namelist() if n.endswith(".nc") and "load" not in n.lower()]
    for c in CONST:
        m = [n for n in nc if re.match(rf"{c}_", Path(n).name, re.I)]
        if len(m) != 1: raise SystemExit(f"{c}: no encuentro un archivo unico de marea oceanica: {m or nc[:20]}")
        tmp = TMP / Path(m[0]).name
        with z.open(m[0]) as a, open(tmp, "wb") as b: shutil.copyfileobj(a, b, 1 << 22)
        with Dataset(tmp) as ds:
            v = ds.variables
            if not out: print(m[0], {k: (v[k].dimensions, getattr(v[k], "units", "")) for k in v})
            lon, lat = np.asarray(v["lon"][:]), np.asarray(v["lat"][:]); lo = (lon + 180) % 360 - 180
            i = np.where((lo >= CAJA[0]) & (lo <= CAJA[1]))[0]; j = np.where((lat >= CAJA[2]) & (lat <= CAJA[3]))[0]
            dims = v["amplitude"].dimensions                                  # (lat, lon) o (lon, lat)
            corte = lambda k: np.ma.filled(v[k][j[0]:j[-1] + 1, i[0]:i[-1] + 1] if dims[0].startswith("lat")
                                           else v[k][i[0]:i[-1] + 1, j[0]:j[-1] + 1].T, np.nan).astype(float)
            amp, pha = corte("amplitude"), corte("phase"); ua = getattr(v["amplitude"], "units", "cm").strip()
        f = {"cm": 0.01, "m": 1.0, "mm": 0.001}[ua]
        out[c] = {"lon": lo[i].round(5).tolist(), "lat": lat[j].round(5).tolist(),
                  "amp_m": np.round(amp * f, 5).tolist(), "fase_grados": np.round(pha, 3).tolist()}
        print(f"{c}: {len(j)}x{len(i)} puntos; amplitud {np.nanmin(amp) * f * 100:.2f}-{np.nanmax(amp) * f * 100:.2f} cm")
        tmp.unlink()
(D / "eot20_habana.json").write_text(json.dumps(out, allow_nan=True))
zp.unlink()
print("guardado", D / "eot20_habana.json")
