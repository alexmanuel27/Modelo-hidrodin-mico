#!/usr/bin/env bash
# Compila SCHISM (mismo commit que en el Mac) con el modulo AGE en un cluster CECI (probado en NIC5).
# Desde el Mac:  C=nic5; scp cluster/compilar_schism_ceci.sh $C: && ssh $C "bash -l compilar_schism_ceci.sh" > cluster/schism_$C.log 2>&1
set -euo pipefail
COMMIT=09f407e855243554c51f8decf3ba053f805add21   # = cluster/schism_version.txt
# Cada cluster tiene versiones distintas: se elige la primera "release" de EasyBuild que tenga
# netCDF-Fortran para gompi y un CMake del mismo GCCcore.
declare -A GCCCORE=([2023b]=13.2.0 [2024a]=13.3.0 [2025b]=14.3.0)
for R in 2023b 2024a 2025b; do
  module purge >/dev/null 2>&1 || true
  module load releases/$R >/dev/null 2>&1 || continue
  NF=$(module -t avail netCDF-Fortran 2>&1 | grep -E "^netCDF-Fortran/.*-gompi-$R$" | tail -1 || true)
  CM=$(module -t avail CMake 2>&1 | grep -E "^CMake/.*-GCCcore-${GCCCORE[$R]}$" | tail -1 || true)
  [ -n "$NF" ] && [ -n "$CM" ] && break
  NF=""
done
[ -n "$NF" ] || { echo "FALLO: no hay netCDF-Fortran + CMake compatibles en releases 2023b/2024a/2025b"; exit 1; }
echo "Toolchain: releases/$R foss/$R $NF $CM"
module load foss/$R "$NF" "$CM"
module list 2>&1
cd "$HOME"
[ -d schism ] || git clone https://github.com/schism-dev/schism.git
cd schism && git fetch -q origin && git checkout -q "$COMMIT" && git log -1 --format='SCHISM %H %cd'
rm -rf build && mkdir build && cd build
cmake -C ../cmake/SCHISM.local.build \
      -DCMAKE_Fortran_COMPILER=mpif90 -DCMAKE_C_COMPILER=mpicc -DCMAKE_CXX_COMPILER=mpicxx \
      -DCMAKE_Fortran_FLAGS="-fallow-argument-mismatch" \
      -DNetCDF_FORTRAN_DIR="$EBROOTNETCDFMINFORTRAN" -DNetCDF_C_DIR="$EBROOTNETCDF" \
      -DUSE_AGE=ON -DCMAKE_BUILD_TYPE=Release ../src
make -j8 pschism
ls -l bin/
echo "LISTO: $(ls bin/pschism_* | head -1)"
