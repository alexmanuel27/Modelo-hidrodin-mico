#!/usr/bin/env python3
"""Marea FES2022b (AVISO+, registro gratuito) alrededor de la boca de la bahia de La Habana.
Por cada constituyente: descarga el .nc.xz global (~165 MB) del servidor THREDDS de AVISO, lo descomprime,
recorta una caja de 0,5 grados alrededor del dominio, guarda amplitud y fase y borra el global.
Uso (Mac, entorno bahia):  AVISO_USER=<usuario> python scripts/marea_fes2022.py      (pide la contrasena)
Salidas: datos/marea/fes2022_habana.json (versionado) y datos/marea/descargas.tsv (URL, fecha, bytes, sha256)."""
import ftplib, getpass, hashlib, json, lzma, os, shutil, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

R = Path(__file__).resolve().parent.parent
D = R / "datos/marea"; TMP = R / "datos/forzamiento/fes2022"   # TMP fuera de git
URL = "https://tds.aviso.altimetry.fr/thredds/fileServer/dataset-auxiliary-fes-tide-model/fes2022b/ocean_tide_extrapolated/{c}_fes2022.nc.xz"
FTP = ("ftp-access.aviso.altimetry.fr", "/auxiliary/tide_model/fes2022b/ocean_tide_extrapolated/{c}_fes2022.nc.xz")   # si THREDDS falla
CONST = ["m2", "s2", "n2", "k2", "k1", "o1", "p1", "q1", "m4", "ms4", "mn4"]
CAJA = (-82.65, -82.05, 22.95, 23.45)   # lon0, lon1, lat0, lat1 (dominio: -82.41..-82.31, 23.11..23.20)

usr = os.environ.get("AVISO_USER") or input("usuario AVISO: ")
pwd = os.environ.get("AVISO_PASS") or getpass.getpass("contrasena AVISO: ")
pm = urllib.request.HTTPPasswordMgrWithDefaultRealm(); pm.add_password(None, "https://tds.aviso.altimetry.fr", usr, pwd)
abre = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(pm)).open
D.mkdir(parents=True, exist_ok=True); TMP.mkdir(parents=True, exist_ok=True)
reg = D / "descargas.tsv"
if not reg.exists(): reg.write_text("archivo\turl\tfecha_acceso_utc\tbytes\tsha256\n")
out = json.loads((D / "fes2022_habana.json").read_text()) if (D / "fes2022_habana.json").exists() else {}

for c in CONST:
    if c in out: print(c, "ya extraido"); continue
    xz, nc = TMP / f"{c}_fes2022.nc.xz", TMP / f"{c}_fes2022.nc"
    if not xz.exists():
        print(f"{c}: descargando..."); u = URL.format(c=c)
        try:
            with abre(u, timeout=600) as r, open(xz, "wb") as f: shutil.copyfileobj(r, f, 1 << 20)
        except urllib.error.URLError as e:                        # THREDDS no responde: mismo archivo por FTP
            print(f"   THREDDS fallo ({e}); pruebo FTP"); u = f"ftp://{FTP[0]}{FTP[1].format(c=c)}"
            with ftplib.FTP(FTP[0], timeout=600) as ftp, open(xz, "wb") as f:
                ftp.login(usr, pwd); ftp.retrbinary("RETR " + FTP[1].format(c=c), f.write, 1 << 20)
        h = hashlib.sha256(xz.read_bytes()).hexdigest()
        with open(reg, "a") as f: f.write(f"{xz.name}\t{u}\t{datetime.now(timezone.utc):%Y-%m-%dT%H:%MZ}\t{xz.stat().st_size}\t{h}\n")
    with lzma.open(xz) as a, open(nc, "wb") as b: shutil.copyfileobj(a, b, 1 << 20)
    with Dataset(nc) as ds:
        v = ds.variables
        if not out: print("variables:", {k: (v[k].dimensions, getattr(v[k], "units", "")) for k in v})
        lon, lat = np.asarray(v["lon"][:]), np.asarray(v["lat"][:])
        lo = (lon + 180) % 360 - 180
        i = np.where((lo >= CAJA[0]) & (lo <= CAJA[1]))[0]; j = np.where((lat >= CAJA[2]) & (lat <= CAJA[3]))[0]
        amp, pha = (np.ma.filled(v[k][j[0]:j[-1] + 1, i[0]:i[-1] + 1].astype(float), np.nan) for k in ("amplitude", "phase"))
        ua = getattr(v["amplitude"], "units", "cm")
    f = {"cm": 0.01, "m": 1.0, "mm": 0.001}[ua.strip()]
    out[c] = {"lon": lo[i].round(5).tolist(), "lat": lat[j].round(5).tolist(),
              "amp_m": np.round(amp * f, 5).tolist(), "fase_grados": np.round(pha, 3).tolist()}
    print(f"{c}: {len(j)}x{len(i)} puntos; amplitud {np.nanmin(amp)*f*100:.2f}-{np.nanmax(amp)*f*100:.2f} cm")
    (D / "fes2022_habana.json").write_text(json.dumps(out, allow_nan=True))
    nc.unlink(); xz.unlink()   # el sha256 queda en descargas.tsv; se puede volver a bajar
print("guardado", D / "fes2022_habana.json")
