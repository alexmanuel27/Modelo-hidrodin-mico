#!/usr/bin/env bash
# Paso 3: entorno + compilacion de SCHISM en el Mac (Apple Silicon).
# Uso (Terminal):  bash scripts/instalar_entorno_mac.sh
# Instala miniforge en ~/miniforge3 (si no existe), crea el entorno "bahia",
# clona SCHISM en ~/modelos/schism y compila pschism con el modulo AGE.
# Los registros quedan en cluster/ para que Claude los revise.
set -euo pipefail
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$PROJ/cluster"
echo ">> 1/4 miniforge"
if [ ! -x "$HOME/miniforge3/bin/conda" ]; then
  curl -fL -o /tmp/Miniforge3.sh \
    https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
  bash /tmp/Miniforge3.sh -b -p "$HOME/miniforge3"
fi
source "$HOME/miniforge3/etc/profile.d/conda.sh"

echo ">> 2/4 entorno 'bahia' (tarda unos minutos)"
if ! conda env list | grep -q '^bahia '; then
  conda create -y -n bahia -c conda-forge python=3.11 \
    gfortran clang clangxx mpich netcdf-fortran parmetis cmake make git perl \
    numpy scipy matplotlib pandas xarray netcdf4 pyproj cdsapi > "$LOG/entorno_conda.log" 2>&1
fi
conda activate bahia

echo ">> 3/4 codigo SCHISM"
mkdir -p "$HOME/modelos" && cd "$HOME/modelos"
[ -d schism ] || git clone https://github.com/schism-dev/schism.git
cd schism
git log -1 --format='%H %cd' > "$LOG/schism_version.txt"

echo ">> 4/4 compilacion (5-15 min)"
rm -rf build && mkdir build && cd build
cmake -C ../cmake/SCHISM.local.build -C ../cmake/SCHISM.local.conda \
      -DUSE_AGE=ON -DCMAKE_BUILD_TYPE=Release ../src > "$LOG/schism_cmake.log" 2>&1
make -j"$(sysctl -n hw.ncpu)" pschism > "$LOG/schism_make.log" 2>&1
ls -l bin/ | tee "$LOG/schism_bin.txt"
echo "LISTO. Avisa a Claude."
