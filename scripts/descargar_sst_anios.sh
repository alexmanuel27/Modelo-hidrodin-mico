#!/usr/bin/env bash
# SST diaria NOAA OISST v2.1 (0,25 grados; dominio publico) frente a La Habana, 2016-12-31 a 2025-12-31, para los experimentos de otros anos (V3 X4).
# Mismo ERDDAP y la misma caja que descargar_sst.sh; no toca los ficheros de 2016. Salida: datos/forzamiento/sst/oisst_habana_2017_2025.csv (fecha,sst_C,celdas).
# Uso (en el Mac, con red): bash scripts/descargar_sst_anios.sh
set -euo pipefail
cd "$(dirname "$0")/.."
D=datos/forzamiento/sst; mkdir -p "$D"
URL='https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.csv?sst%5B(2016-12-31T12:00:00Z):1:(2025-12-31T12:00:00Z)%5D%5B(0.0)%5D%5B(23.125):1:(23.625)%5D%5B(-82.875):1:(-81.875)%5D'
curl -fsS --retry 3 -o "$D/oisst_caja_2017_2025.csv" "$URL"
[ -f "$D/descargas.tsv" ] || printf 'archivo\turl\tfecha_acceso_utc\tbytes\tsha256\n' > "$D/descargas.tsv"
printf '%s\t%s\t%s\t%s\t%s\n' oisst_caja_2017_2025.csv "$URL" "$(date -u +%Y-%m-%dT%H:%MZ)" "$(wc -c < "$D/oisst_caja_2017_2025.csv" | tr -d ' ')" \
  "$(shasum -a 256 "$D/oisst_caja_2017_2025.csv" | cut -d' ' -f1)" >> "$D/descargas.tsv"
python3 - "$D" <<'P'
import sys, csv, collections
d = sys.argv[1]; v = collections.defaultdict(list)
with open(f"{d}/oisst_caja_2017_2025.csv") as f:
    r = csv.reader(f); next(r); next(r)
    for t, z, la, lo, s in r:
        if s not in ("", "NaN"): v[t[:10]].append(float(s))
with open(f"{d}/oisst_habana_2017_2025.csv", "w") as f:
    f.write("fecha,sst_C,celdas\n")
    for k in sorted(v): f.write(f"{k},{sum(v[k]) / len(v[k]):.3f},{len(v[k])}\n")
print(len(v), "dias", min(v), max(v))
P
