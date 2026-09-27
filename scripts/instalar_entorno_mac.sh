#!/usr/bin/env bash
# Paso 3: entorno + compilacion de SCHISM en el Mac.
# Uso (Terminal, desde la raiz del repo):  bash scripts/instalar_entorno_mac.sh
# Instala miniforge en ~/miniforge3 (si no existe), crea el entorno "bahia",
# clona SCHISM en ~/modelos/schism y compila pschism con el modulo AGE.
# Los registros quedan en cluster/ para que Claude los revise.
# Se puede relanzar: salta lo que ya esta hecho.
set -eo pipefail
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$PROJ/cluster"
mkdir -p "$LOG"
trap 'echo "!! FALLO en la linea $LINENO. Revisa los .log de cluster/ y avisa a Claude." >&2' ERR

{ echo "fecha: $(date)"; sw_vers 2>/dev/null; uname -m; xcode-select -p 2>&1 || true; } > "$LOG/sistema.txt"

echo ">> 1/4 miniforge"
if [ ! -x "$HOME/miniforge3/bin/conda" ]; then
  ARCH="$(uname -m)"   # arm64 (Apple Silicon) o x86_64 (Intel)
  curl -fL -o /tmp/Miniforge3.sh \
    "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-${ARCH}.sh"
  bash /tmp/Miniforge3.sh -b -p "$HOME/miniforge3"
fi
source "$HOME/miniforge3/etc/profile.d/conda.sh"

echo ">> 2/4 entorno 'bahia' (tarda unos minutos)"
if ! conda env list | grep -q '^bahia '; then
  # ParMETIS no hace falta: SCHISM lo trae incluido.
  conda create -y -n bahia -c conda-forge python=3.11 \
    compilers mpich mpich-mpicc mpich-mpifort netcdf-fortran netcdf4 cmake make git perl \
    numpy scipy matplotlib pandas xarray pyproj cdsapi > "$LOG/entorno_conda.log" 2>&1
fi
conda activate bahia
{ echo "CONDA_PREFIX=$CONDA_PREFIX"; which mpif90 mpicc gfortran cmake nc-config nf-config;
  mpif90 --version | head -1; nf-config --version; } > "$LOG/entorno_resumen.txt" 2>&1

echo ">> 3/4 codigo SCHISM"
mkdir -p "$HOME/modelos" && cd "$HOME/modelos"
[ -d schism ] || git clone https://github.com/schism-dev/schism.git
cd schism
git log -1 --format='%H %cd' > "$LOG/schism_version.txt"
ls cmake >> "$LOG/schism_version.txt"

# Parche: con gfortran + clang (conda), SCHISMCompile.cmake pasa "--preprocess" a gfortran,
# que equivale a -E (solo preprocesa): los .o salen en texto y no se generan los .mod
# ("Error copying Fortran module"). Se cambia por -cpp. Queda anotado en schism_version.txt.
if grep -q '"--preprocess"' cmake/SCHISMCompile.cmake; then
  sed -i.orig 's/"--preprocess"/"-cpp"/g' cmake/SCHISMCompile.cmake
  echo "parche local: --preprocess -> -cpp en cmake/SCHISMCompile.cmake" >> "$LOG/schism_version.txt"
fi
# ...y -cpp solo para Fortran: add_compile_options lo aplicaba tambien al C de ParMETIS y clang lo rechaza.
if grep -qxF 'add_compile_options(${C_PREPROCESS_FLAG})' src/CMakeLists.txt; then
  sed -i.orig 's/^add_compile_options(\${C_PREPROCESS_FLAG})$/add_compile_options($<$<COMPILE_LANGUAGE:Fortran>:${C_PREPROCESS_FLAG}>)/' src/CMakeLists.txt
  echo "parche local: C_PREPROCESS_FLAG solo para Fortran en src/CMakeLists.txt" >> "$LOG/schism_version.txt"
fi

echo ">> 4/4 compilacion (5-15 min)"
rm -rf build && mkdir build && cd build
# Sin SCHISM.local.conda: fija PARMETIS_ROOT, no encuentra ParMETIS en conda y, por un fallo
# de src/CMakeLists.txt, tampoco compila el interno -> "library not found for -lparmetis".
cmake -C ../cmake/SCHISM.local.build \
      -DCMAKE_Fortran_COMPILER=mpif90 -DCMAKE_C_COMPILER=mpicc -DCMAKE_CXX_COMPILER=mpicxx \
      -DCMAKE_Fortran_FLAGS="-fallow-argument-mismatch" \
      -DUSE_AGE=ON -DCMAKE_BUILD_TYPE=Release ../src > "$LOG/schism_cmake.log" 2>&1
make -j"$(sysctl -n hw.ncpu)" pschism > "$LOG/schism_make.log" 2>&1
ls -l bin/ | tee "$LOG/schism_bin.txt"
echo "LISTO. Avisa a Claude."
