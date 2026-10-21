#!/usr/bin/env bash
# Compila combine_hotstart7 (une el hotstart por rango de SCHISM) junto a pschism, con el mismo toolchain.
# Desde el Mac: scp cluster/compilar_combine_hotstart.sh lemaitre4: && ssh lemaitre4 "bash -l compilar_combine_hotstart.sh"
set -euo pipefail
module purge >/dev/null 2>&1 || true
module load releases/2024a foss/2024a netCDF-Fortran/4.6.1-gompi-2024a
cd "$HOME/schism/src/Utility/Combining_Scripts"
ls ../UtilLib/ | grep -i argparse || true
mpif90 -O2 -ffree-line-length-none -o "$HOME/schism/build/bin/combine_hotstart7" \
       ../UtilLib/argparse.f90 combine_hotstart7.f90 $(nf-config --fflags) $(nf-config --flibs)
ls -l "$HOME/schism/build/bin/combine_hotstart7" && echo LISTO
