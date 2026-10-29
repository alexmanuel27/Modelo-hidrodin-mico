#!/bin/bash -l
#SBATCH --job-name=mover_scratch
#SBATCH --time=06:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=2000
#SBATCH --output=/globalscratch/ulb/cenoli/arivera/mover_scratch_%j.out
# Mueve ~/bahia a $GLOBALSCRATCH/bahia (la cuota de /home se lleno el 28-oct con las salidas del conjunto) y deja
# ~/bahia como enlace, asi que rutas, rsync y lanzadores siguen igual. El original queda en ~/bahia_home_viejo hasta
# que se compruebe la copia. Uso: ssh lemaitre4 'bash -lc "sbatch $GLOBALSCRATCH/mover_a_scratch.sh"'
set -euo pipefail
cd "$HOME"
[ -L bahia ] && { echo "ya es un enlace: $(readlink bahia)"; exit 0; }
du -sh bahia
rsync -a bahia/ "$GLOBALSCRATCH/bahia/"
mv bahia bahia_home_viejo && ln -s "$GLOBALSCRATCH/bahia" bahia
echo "copiado: $(du -sh "$GLOBALSCRATCH/bahia" | cut -f1)  (original $(du -sh bahia_home_viejo | cut -f1))"
echo "MOVIDO. Comprobar y luego: rm -rf ~/bahia_home_viejo"
