#!/usr/bin/env bash
# SST diaria NOAA OISST v2.1 (0,25 grados; dominio publico) frente a La Habana, 2016, para el borde y la condicion inicial
# de los experimentos con flujo de calor. Fuente: ERDDAP de NOAA CoastWatch (sin registro).
# Uso (en el Mac, con red): bash scripts/descargar_sst.sh   -> datos/forzamiento/sst/{oisst_caja_2016.csv, oisst_habana.csv}
set -euo pipefail
cd "$(dirname "$0")/.."
D=datos/forzamiento/sst; mkdir -p "$D"
URL='https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.csv?sst%5B(2015-12-31T12:00:00Z):1:(2017-01-01T12:00:00Z)%5D%5B(0.0)%5D%5B(23.125):1:(23.625)%5D%5B(-82.875):1:(-81.875)%5D'
curl -fsS --retry 3 -o "$D/oisst_caja_2016.csv" "$URL"
[ -f "$D/descargas.tsv" ] || printf 'archivo\turl\tfecha_acceso_utc\tbytes\tsha256\n' > "$D/descargas.tsv"
printf '%s\t%s\t%s\t%s\t%s\n' oisst_caja_2016.csv "$URL" "$(date -u +%Y-%m-%dT%H:%MZ)" "$(wc -c < "$D/oisst_caja_2016.csv" | tr -d ' ')" \
  "$(shasum -a 256 "$D/oisst_caja_2016.csv" | cut -d' ' -f1)" >> "$D/descargas.tsv"
python3 - "$D" <<'P'
import sys, csv, collections
d = sys.argv[1]; v = collections.defaultdict(list)
with open(f"{d}/oisst_caja_2016.csv") as f:
    r = csv.reader(f); next(r); next(r)                       # cabecera y unidades
    for t, z, la, lo, s in r:
        if s not in ("", "NaN"): v[t[:10]].append(float(s))   # celdas de tierra = NaN
with open(f"{d}/oisst_habana.csv", "w") as f:
    f.write("fecha,sst_C,celdas\n")
    for k in sorted(v): f.write(f"{k},{sum(v[k]) / len(v[k]):.3f},{len(v[k])}\n")
x = [sum(v[k]) / len(v[k]) for k in sorted(v)]
print(f"{len(x)} dias, SST media de la caja {min(x):.2f}-{max(x):.2f} C (1-ene-2016: {x[1]:.2f} C)")
P
