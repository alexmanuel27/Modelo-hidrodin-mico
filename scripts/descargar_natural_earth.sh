#!/usr/bin/env bash
# Natural Earth 1:50m, países (dominio público), solo para el recuadro de Cuba de la figura 1.
# Uso, en el Mac (necesita red): bash scripts/descargar_natural_earth.sh   -> datos/mapa/ y regenera la figura 1
set -euo pipefail
cd "$(dirname "$0")/.."
D=datos/mapa; mkdir -p "$D"
URL=https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_admin_0_countries.geojson
F="$D/ne_50m_admin_0_countries.geojson"
curl -fsSL -o "$F" "$URL"
[ -f "$D/descargas.tsv" ] || printf 'archivo\turl\tfecha_acceso_utc\tbytes\tsha256\n' > "$D/descargas.tsv"
printf '%s\t%s\t%s\t%s\t%s\n' "$(basename "$F")" "$URL" "$(date -u +%Y-%m-%dT%H:%MZ)" "$(wc -c < "$F" | tr -d ' ')" \
  "$(shasum -a 256 "$F" | cut -d' ' -f1)" >> "$D/descargas.tsv"
echo "ok: $F ($(wc -c < "$F" | tr -d ' ') bytes)"
python3 scripts/figuras_articulo.py 1
