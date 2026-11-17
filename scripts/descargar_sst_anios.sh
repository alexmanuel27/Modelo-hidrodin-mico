#!/usr/bin/env bash
# SST diaria NOAA OISST v2.1 (0,25 grados; dominio publico) frente a La Habana, 2016-12-31 a 2025-12-31, para los experimentos de otros anos (V3 X4).
# Mismo ERDDAP y la misma caja que descargar_sst.sh; no toca los ficheros de 2016. Un pedido por ano, con limite de tiempo y reintentos (el pedido unico de nueve anos se colgo
# el 17-nov). Salida: datos/forzamiento/sst/oisst_habana_2017_2025.csv (fecha,sst_C,celdas).
# Uso (en el Mac, con red): bash scripts/descargar_sst_anios.sh
set -euo pipefail
cd "$(dirname "$0")/.."
D=datos/forzamiento/sst; mkdir -p "$D"
[ -f "$D/descargas.tsv" ] || printf 'archivo\turl\tfecha_acceso_utc\tbytes\tsha256\n' > "$D/descargas.tsv"
ERDDAP=${ERDDAP:-https://coastwatch.pfeg.noaa.gov/erddap}   # alternativa si este da 503: ERDDAP=https://upwell.pfeg.noaa.gov/erddap
for Y in 2017 2018 2019 2020 2021 2022 2023 2024 2025; do
  F="$D/oisst_caja_$Y.csv"
  if [ ! -s "$F" ]; then
    URL="$ERDDAP/griddap/ncdcOisst21Agg_LonPM180.csv?sst%5B($((Y - 1))-12-31T12:00:00Z):1:($Y-12-31T12:00:00Z)%5D%5B(0.0)%5D%5B(23.125):1:(23.625)%5D%5B(-82.875):1:(-81.875)%5D"
    curl -fsS --connect-timeout 20 --max-time 300 --retry 6 --retry-delay 30 --retry-all-errors -o "$F.parcial" "$URL" && mv "$F.parcial" "$F"
    printf '%s\t%s\t%s\t%s\t%s\n' "oisst_caja_$Y.csv" "$URL" "$(date -u +%Y-%m-%dT%H:%MZ)" "$(wc -c < "$F" | tr -d ' ')" "$(shasum -a 256 "$F" | cut -d' ' -f1)" >> "$D/descargas.tsv"
  fi
  echo "$Y ok ($(wc -l < "$F" | tr -d ' ') lineas)"
done
python3 - "$D" <<'P'
import sys, csv, collections, glob
d = sys.argv[1]; v = collections.defaultdict(list)
for fn in sorted(glob.glob(f"{d}/oisst_caja_20[12][0-9].csv")):
    if any(str(y) in fn for y in (2016,)): continue
    with open(fn) as f:
        r = csv.reader(f); next(r); next(r)
        dia = {}
        for t, z, la, lo, s in r:
            if s not in ("", "NaN"): dia.setdefault(t[:10], []).append(float(s))
        for k, x in dia.items(): v[k] = x          # los dias de empalme entre anos se repiten con el mismo valor
with open(f"{d}/oisst_habana_2017_2025.csv", "w") as f:
    f.write("fecha,sst_C,celdas\n")
    for k in sorted(v): f.write(f"{k},{sum(v[k]) / len(v[k]):.3f},{len(v[k])}\n")
print(len(v), "dias", min(v), max(v))
P
