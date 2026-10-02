#!/usr/bin/env bash
# Paso 1 de la batimetria publica: descarga de fuentes con fecha de acceso y sha256.
# Uso (Terminal, raiz del repo):  bash scripts/batimetria/01_descargar.sh
# Lo que no admite descarga directa (Harvard, GEBCO) se baja a mano en el navegador
# y se deja en datos/batimetria/fuentes/ con el nombre indicado; el script lo registra.
set -eo pipefail
cd "$(dirname "$0")/../.."
D=datos/batimetria/fuentes; mkdir -p "$D"; LOG="$D/descargas.tsv"
[ -f "$LOG" ] || printf "archivo\turl\tfecha_acceso_utc\tbytes\tsha256\n" > "$LOG"
baja() {  # baja <nombre> <url>
  if [ ! -s "$D/$1" ]; then echo "descargando $1"; curl -fL --retry 3 -o "$D/$1" "$2"; fi
  if file "$D/$1" | grep -q HTML; then echo "!! $1 es una pagina HTML, no el archivo"; rm -f "$D/$1"; return 1; fi
  grep -q "^$1	" "$LOG" || printf "%s\t%s\t%s\t%s\t%s\n" "$1" "$2" "$(date -u +%Y-%m-%dT%H:%MZ)" \
      "$(wc -c < "$D/$1" | tr -d ' ')" "$(shasum -a 256 "$D/$1" | cut -d' ' -f1)" >> "$LOG"
}
# Carta U.S. Hydrographic Office n. 307, ed. 1898 (levantamientos espanoles hasta 1887), Leventhal Map Center.
# El boton "download" devuelve HTML; la imagen completa (7994 x 5527) se pide al servidor IIIF.
baja carta_1898_leventhal.jpg "https://iiif.digitalcommonwealth.org/iiif/2/commonwealth:0c487z874/full/full/0/default.jpg"
baja carta_1898_leventhal_manifest.json "https://collections.leventhalmap.org/search/commonwealth:g445ht01p/manifest"
# Practicos del puerto de La Habana (canal y calados de muelles), Cubadebate 2018
baja practicos_puerto_habana_2018.pdf "http://media.cubadebate.cu/wp-content/uploads/2018/09/puerto_de_la_habana-PRACTICOS.pdf"
# A mano (navegador) -> registrar
for f in carta_1889_harvard.tif gebco_habana.nc gebco_habana_tid.nc; do
  if [ -s "$D/$f" ]; then
    case $f in carta_1889_harvard.tif) u="https://hgl.harvard.edu/catalog/harvard-g4924-h3-1889-u5";;
               gebco_habana.nc) u="https://download.gebco.net/ (GEBCO 2026 Global, bathymetry, 22.9-23.4N 82.6-82.1W)";;
               gebco_habana_tid.nc) u="https://download.gebco.net/ (GEBCO 2026 Global, TID, 22.9-23.4N 82.6-82.1W)";; esac
    baja "$f" "$u"
  else echo "FALTA (descarga manual): $D/$f"; fi
done
column -t -s $'\t' "$LOG"
