#!/bin/bash -l
# Recoge lo necesario para saber por que hay tramos lentos: estados y nodos de Slurm, coste.txt y la hora a la que
# cada miembro escribio cada dia simulado (mtime de out2d_N.nc). Deja todo en ~/bahia/diag_tiempos.tgz.
# Uso: scp cluster/diagnostico_tiempos.sh lemaitre4:bahia/ && ssh lemaitre4 'bash -l bahia/diagnostico_tiempos.sh'
#      scp lemaitre4:bahia/diag_tiempos.tgz runs/ && mkdir -p runs/diag && tar xzf runs/diag_tiempos.tgz -C runs/diag
set -eo pipefail
D=$(mktemp -d); cd ~/bahia/runs/conjunto
sacct -u "$USER" -S 2026-10-29 -X -n -P --format=JobID,JobName,State,Elapsed,NodeList,Start,End > "$D/sacct.txt"
cp coste.txt "$D/coste.txt"
for m in m*; do ls "$m"/outputs/out2d_*.nc >/dev/null 2>&1 && stat -c "$m %n %Y" "$m"/outputs/out2d_*.nc; done | sed 's#/outputs/out2d_# #; s#\.nc##' | awk '{print $1, $3, $4}' > "$D/dias.txt"
for f in slurm_8062929_*.out; do echo "$f $(grep -m1 '^tramo:' "$f" | awk '{print $3, $5}') $(grep -c 'TIME LIMIT' "$f")"; done > "$D/tramos.txt"
tar czf ~/bahia/diag_tiempos.tgz -C "$D" . && rm -rf "$D" && ls -l ~/bahia/diag_tiempos.tgz
