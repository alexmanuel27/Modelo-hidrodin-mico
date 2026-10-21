#!/usr/bin/env bash
# Arma el repo publico (datos + configuracion + resultados + codigo) en build/publicacion/ (fuera de git).
# Solo copia lo que se puede redistribuir (lista explicita abajo; ver publicacion/DATA_SOURCES.md).
# Uso: bash scripts/preparar_publicacion.sh [destino]     -> luego: cd destino && git init && git add . && git commit ...
set -euo pipefail
cd "$(dirname "$0")/.."
DEST=${1:-build/publicacion}
INCLUIR=(
  scripts/*.py scripts/*.sh scripts/batimetria/*.py scripts/batimetria/*.sh
  cluster/compilar_schism_ceci.sh cluster/inventario.sh
  datos/batimetria/fuentes/descargas.tsv datos/batimetria/fuentes/osm_costa_habana.json datos/batimetria/fuentes/osm_rios_habana.json
  datos/batimetria/fuentes/gebco_habana.nc datos/batimetria/fuentes/gebco_habana_tid.nc
  datos/batimetria/fuentes/carta_1889_harvard_fgdc.xml datos/batimetria/fuentes/carta_1898_leventhal_manifest.json
  datos/batimetria/sondeos datos/batimetria/superficies/volumenes_conjunto.json
  datos/malla datos/conjunto/diseno.csv datos/conjunto/posproceso_malla.npz
  datos/marea/eot20_habana.json datos/marea/descargas.tsv
  datos/forzamiento/sflux
  resultados docs/figuras
)
# shortcut: resultados del conjunto (resumenes por miembro, Sobol) se anaden a INCLUIR cuando existan
rm -rf "$DEST"; mkdir -p "$DEST"
for p in "${INCLUIR[@]}"; do [ -e "$p" ] || { echo "!! falta $p"; exit 1; }; done
rsync -aR --exclude '__pycache__' --exclude '.DS_Store' "${INCLUIR[@]}" "$DEST/"
cp publicacion/README.md publicacion/DATA_SOURCES.md publicacion/LICENSE publicacion/LICENSE-DATA.md publicacion/CITATION.cff publicacion/.zenodo.json "$DEST/"
printf '__pycache__/\n.DS_Store\nruns/\nbuild/\ndatos/forzamiento/era5/\ndatos/forzamiento/fes2022/\ndatos/forzamiento/eot20/\ndatos/marea/fes2022_habana.json\n*.tif\n*.jpg\n' > "$DEST/.gitignore"
# nada que no se pueda redistribuir
if find "$DEST" \( -name '*practicos*' -o -name '*jica*' -o -name 'fes2022_habana.json' -o -name '*.tif' -o -name '*.jpg' \) | grep -q .; then
  echo "!! archivo no redistribuible en $DEST"; exit 1; fi
(cd "$DEST" && find . -type f ! -name SHA256SUMS ! -path './.git/*' -print0 | sort -z | xargs -0 shasum -a 256 > SHA256SUMS)
echo "listo: $DEST ($(du -sh "$DEST" | cut -f1), $(find "$DEST" -type f | wc -l | tr -d ' ') archivos)"
