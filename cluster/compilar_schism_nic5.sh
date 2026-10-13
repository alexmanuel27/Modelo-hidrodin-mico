#!/usr/bin/env bash
# Compila SCHISM (mismo commit que en el Mac) con el modulo AGE en NIC5 (CECI).
# Desde el Mac:  scp cluster/compilar_schism_nic5.sh nic5: && ssh nic5 'bash -l compilar_schism_nic5.sh' > cluster/schism_nic5.log 2>&1
set -euo pipefail
COMMIT=09f407e855243554c51f8decf3ba053f805add21   # = cluster/schism_version.txt
module purge >/dev/null 2>&1 || true
module load releases/2023b foss/2023b netCDF-Fortran/4.6.1-gompi-2023b CMake/3.27.6-GCCcore-13.2.0
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
