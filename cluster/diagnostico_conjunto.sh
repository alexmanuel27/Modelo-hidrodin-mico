#!/bin/bash -l
# Diagnostico del conjunto y de la robustez: estados de Slurm, miembros por estado y causa de los cortes.
# Uso: scp cluster/diagnostico_conjunto.sh lemaitre4:bahia/ && ssh lemaitre4 'bash -l bahia/diagnostico_conjunto.sh'
cd ~/bahia/runs
echo "== estados de Slurm desde el 29-oct (trabajo, estado: cuantos; tiempo del ultimo / limite) =="
sacct -u "$USER" -S 2026-10-29 -X -n -P --format=JobID,JobName,State,Elapsed,Timelimit |
  awk -F'|' '$2=="bahia_conj"{split($1,a,"_"); k=a[1]" "$3; n[k]++; t[k]=$4" / "$5} END{for(k in n) print k": "n[k]"  ("t[k]")"}' | sort
for d in conjunto robustez; do
  cd ~/bahia/runs/$d || continue
  h=0; c=0; s=0; nr=""
  for m in m[0-9][0-9][0-9][0-9]; do
    if [ -f "$m/HECHO" ]; then h=$((h+1)); [ -f "$m/resumen.json" ] || nr="$nr $m"; elif ls "$m"/outputs/hotstart_000000_*.nc >/dev/null 2>&1; then c=$((c+1)); else s=$((s+1)); fi
  done
  echo "== $d: terminados $h, a medias (con hotstart) $c, sin empezar o sin tramo completo $s =="
  [ -n "$nr" ] && echo "   terminados SIN resumen.json (fallo el posproceso; los campos no se borraron, repetirlo):$nr"
  echo "   cortados por tiempo: $(grep -l 'DUE TO TIME LIMIT' slurm_*.out 2>/dev/null | wc -l), por memoria: $(grep -li 'oom\|out of memory' slurm_*.out 2>/dev/null | wc -l), cancelados: $(grep -l 'CANCELLED' slurm_*.out 2>/dev/null | wc -l)"
  f=$(grep -l 'DUE TO TIME LIMIT\|CANCELLED\|rror' slurm_*.out 2>/dev/null | tail -1)
  [ -n "$f" ] && { echo "   ejemplo: $f"; tail -n 4 "$f" | sed 's/^/     /'; }
  echo "   tiempos de tramo completos (s): $(grep -o 'segundos=[0-9]*' coste.txt | cut -d= -f2 | sort -n | awk '{a[NR]=$1} END{if(NR) print "min",a[1],"mediana",a[int(NR/2)+1],"max",a[NR]}')"
done
cat ~/bahia/runs/robustez/coste.txt
