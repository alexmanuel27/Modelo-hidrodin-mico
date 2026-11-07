#!/bin/bash -l
# Prueba de muestreo del caudal (Lemaitre4): reinicia la base m0000 desde su hotstart del dia 120 y corre 2 dias mas
# guardando out2d cada 10 min (nspool=6) en runs/robustez/m0000_hf. No toca m0000. Despues:
#   python scripts/diag_caudal.py --hf runs/robustez/m0000_hf     (con netcdf4-python cargado)
# Uso, desde ~/bahia:  sbatch cluster/hf_caudal.sh      (primero: rsync -aR scripts/diag_caudal.py cluster/hf_caudal.sh lemaitre4:bahia/)
#SBATCH --job-name=hf_caudal
#SBATCH --ntasks=7
#SBATCH --nodes=1
#SBATCH --time=01:30:00
#SBATCH --mem-per-cpu=4000
#SBATCH --output=hf_caudal_%j.out
set -eo pipefail
module purge >/dev/null 2>&1 || true
module load releases/2024a foss/2024a netCDF-Fortran/4.6.1-gompi-2024a
cd $HOME/bahia/runs/robustez
IT=103680; [ -e m0000/outputs/hotstart_000000_$IT.nc ] || { echo "falta el hotstart del dia 120 de m0000"; exit 1; }
[ -e m0000_hf ] && { echo "m0000_hf ya existe: bórralo o renómbralo"; exit 1; }
mkdir m0000_hf m0000_hf/outputs
rsync -a --exclude=outputs --exclude=sflux --exclude='resumen.*' --exclude=posproceso.log --exclude=HECHO --exclude='slurm_*' m0000/ m0000_hf/
ln -s "$(readlink -f m0000/sflux)" m0000_hf/sflux
cd m0000_hf/outputs
for r in 0 1 2 3; do ln -s ../../m0000/outputs/hotstart_00000${r}_$IT.nc .; done
$HOME/schism/build/bin/combine_hotstart7 -i $IT > combine.log 2>&1
mv "hotstart_it=$IT.nc" ../hotstart.nc; rm -f hotstart_00000?_$IT.nc; cd ..
sed -i -E "s/^( *rnday *=).*/\1 122/; s/^( *ihot *=).*/\1 2/; s/^( *nhot *=).*/\1 0/; s/^( *nspool *=).*/\1 6/" param.nml
grep -nE "^ *(rnday|ihot|nhot|nspool|ihfskip) *=" param.nml
srun $HOME/schism/build/bin/pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL 3 > outputs/pantalla.log 2>&1 || true
grep -q "Run completed successfully" outputs/mirror.out && echo "OK: out2d cada 10 min en runs/robustez/m0000_hf/outputs" || { echo "FALLO: mira outputs/pantalla.log y mirror.out"; exit 1; }
