#!/usr/bin/env bash
# PDF del vol. V de JICA 2004 (openjicareport, 11767233_NN), publico. El vol. V esta partido en ficheros por capitulos: _04 es el cap. 5 (alcantarillado),
# asi que las tablas 4.8, 4.11, 4.19, 4.20 y la figura 4.25 estan en otro. Baja los que se le pidan (por defecto 01 a 07; los que no existan se saltan)
# y registra fecha y sha256 como el resto de descargas.tsv. Uso, en el Mac con red y desde la raiz del repo: bash scripts/batimetria/01b_descargar_jica_vol5.sh [NN ...]
set -uo pipefail
cd "$(dirname "$0")/../.."
D=datos/batimetria/fuentes
for N in "${@:-01 02 03 04 05 06 07}"; do for n in $N; do
  F=$D/jica_2004_vol5_$n.pdf; URL=https://openjicareport.jica.go.jp/pdf/11767233_$n.pdf
  if [ ! -s "$F" ]; then
    if curl -fsSL --connect-timeout 20 --max-time 600 --retry 3 -o "$F.parcial" "$URL" && head -c 5 "$F.parcial" | grep -q '^%PDF'; then mv "$F.parcial" "$F"
    else rm -f "$F.parcial" 2>/dev/null; echo "$n: no disponible o no es PDF"; continue; fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$(basename "$F")" "$URL" "$(date -u +%Y-%m-%dT%H:%MZ)" "$(wc -c < "$F" | tr -d ' ')" "$(shasum -a 256 "$F" | cut -d' ' -f1)" >> "$D/descargas.tsv"
  fi
  echo "$n ok ($(wc -c < "$F" | tr -d ' ') bytes)"
done; done
