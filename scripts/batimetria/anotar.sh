#!/usr/bin/env bash
# Anota sondeos leidos sobre una tesela ampliada: convierte coordenadas de pantalla a pixeles de la carta.
# Uso: anotar.sh <csv> <x0> <y0> <zoom> <tesela> < lineas "dx dy brazas dudoso"
F=$1; X0=$2; Y0=$3; Z=$4; T=$5
[ -f "$F" ] || echo "x,y,brazas,dudoso,tesela" > "$F"
awk -v x0="$X0" -v y0="$Y0" -v z="$Z" -v t="$T" 'NF>=4{printf "%d,%d,%s,%s,%s\n", x0+$1/z, y0+$2/z, $3, $4, t}' >> "$F"
wc -l < "$F"
