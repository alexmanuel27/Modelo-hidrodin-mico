#!/usr/bin/env bash
# PDF del vol. V de JICA 2004 (caps. 4.3-4.4: tablas 4.8, 4.11, 4.19, 4.20 y figura 4.25), publico en openjicareport. Registra fecha y sha256 como el resto
# de descargas.tsv. Uso (en el Mac, con red, desde la raiz del repo): bash scripts/batimetria/01b_descargar_jica_vol5.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
D=datos/batimetria/fuentes; F=$D/jica_2004_vol5_cap4.pdf; URL=https://openjicareport.jica.go.jp/pdf/11767233_04.pdf
[ -s "$F" ] || curl -fL --connect-timeout 20 --max-time 600 --retry 3 -o "$F.parcial" "$URL" && mv "$F.parcial" "$F"
head -c 5 "$F" | grep -q '^%PDF' || { echo "no es un PDF: $F" >&2; exit 1; }
printf '%s\t%s\t%s\t%s\t%s\n' "$(basename "$F")" "$URL" "$(date -u +%Y-%m-%dT%H:%MZ)" "$(wc -c < "$F" | tr -d ' ')" "$(shasum -a 256 "$F" | cut -d' ' -f1)" >> "$D/descargas.tsv"
echo "ok: $F ($(wc -c < "$F" | tr -d ' ') bytes)"
