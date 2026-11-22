#!/usr/bin/env bash
# SST diaria NOAA OISST v2.1 (0,25 grados; dominio publico) frente a La Habana, 2002-08-31 a 2003-01-03, para las corridas de 2002 (docs/protocolo_2002.md).
# Misma caja y ERDDAP que descargar_sst_anios.sh. Salida: datos/forzamiento/sst/oisst_habana_2002.csv (fecha,sst_C,celdas): dias consecutivos desde 2002-09-01 hasta 2003-01-03;
# los huecos de un solo dia se rellenan por interpolacion lineal (celdas = 0) y se listan en datos/forzamiento/sst/oisst_huecos_2002.txt; un hueco de 2 o mas dias detiene el script (caso_real.py exige dias consecutivos).
# Uso (en el Mac, con red): until bash scripts/descargar_sst_2002.sh; do sleep 60; done
set -euo pipefail
cd "$(dirname "$0")/.."
D=datos/forzamiento/sst; mkdir -p "$D"
[ -f "$D/descargas.tsv" ] || printf 'archivo\turl\tfecha_acceso_utc\tbytes\tsha256\n' > "$D/descargas.tsv"
ERDDAP=${ERDDAP:-https://coastwatch.pfeg.noaa.gov/erddap}
F="$D/oisst_caja_2002.csv"
if [ ! -s "$F" ]; then
  URL="$ERDDAP/griddap/ncdcOisst21Agg_LonPM180.csv?sst%5B(2002-08-31T12:00:00Z):1:(2003-01-03T12:00:00Z)%5D%5B(0.0)%5D%5B(23.125):1:(23.625)%5D%5B(-82.875):1:(-81.875)%5D"
  curl -fsS --connect-timeout 20 --max-time 300 --retry 6 --retry-delay 30 --retry-all-errors -o "$F.parcial" "$URL"
  head -1 "$F.parcial" | grep -q "^time,zlev" || { echo "respuesta vacia o no valida de $ERDDAP" >&2; rm -f "$F.parcial" 2>/dev/null || mv "$F.parcial" "$F.invalido"; exit 1; }
  mv "$F.parcial" "$F"
  printf '%s\t%s\t%s\t%s\t%s\n' "oisst_caja_2002.csv" "$URL" "$(date -u +%Y-%m-%dT%H:%MZ)" "$(wc -c < "$F" | tr -d ' ')" "$(shasum -a 256 "$F" | cut -d' ' -f1)" >> "$D/descargas.tsv"
fi
python3 - "$D" <<'P'
import sys, csv, datetime as dt
d = sys.argv[1]; dia = {}
with open(f"{d}/oisst_caja_2002.csv") as f:
    r = csv.reader(f); next(r); next(r)
    for t, z, la, lo, s in r:
        if s not in ("", "NaN"): dia.setdefault(t[:10], []).append(float(s))
f0, f1 = dt.date(2002, 9, 1), dt.date(2003, 1, 3); v, huecos, k = [], [], f0
while k <= f1:
    c = k.isoformat()
    if c in dia: v.append((c, sum(dia[c]) / len(dia[c]), len(dia[c])))
    else: v.append((c, None, 0))
    k += dt.timedelta(1)
for i, (c, x, n) in enumerate(v):
    if x is None:
        j = i
        while j < len(v) and v[j][1] is None: j += 1
        assert i > 0 and j < len(v) and j - i == 1, f"hueco de {j - i} dia(s) desde {c}: no se rellena"
        v[i] = (c, (v[i - 1][1] + v[j][1]) / 2, 0); huecos.append(f"{c}, {v[i - 1][1]:.3f}, {v[j][1]:.3f}, {v[i][1]:.3f}")
with open(f"{d}/oisst_habana_2002.csv", "w") as f:
    f.write("fecha,sst_C,celdas\n")
    for c, x, n in v: f.write(f"{c},{x:.3f},{n}\n")
open(f"{d}/oisst_huecos_2002.txt", "w").write("Huecos de un dia de oisst_habana_2002.csv rellenados por interpolacion lineal (celdas = 0)\nfecha, dia anterior, dia posterior, valor interpolado\n" + "\n".join(huecos) + "\n")
print(len(v), "dias", v[0][0], v[-1][0], f"{len(huecos)} huecos rellenados", f"SST {min(x for _, x, _ in v):.2f}-{max(x for _, x, _ in v):.2f} C")
P
