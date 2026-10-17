#!/usr/bin/env python3
"""Conjunto de Saltelli: diseno, generacion de los casos SCHISM y lanzador para Lemaitre4.

  python scripts/conjunto.py diseno  [N=64]      -> datos/conjunto/diseno.csv (versionado)
  python scripts/conjunto.py prueba               -> autoprueba: Jansen sobre Ishigami con la misma construccion
  python scripts/conjunto.py generar [J=6]       -> runs/conjunto/mNNNN/ (caso_real.py por miembro, J a la vez)
                                                    + runs/conjunto/correr_array.sh
Diseno: Saltelli (2002) con Sobol aleatorizado (scipy.stats.qmc): matrices A, B y AB_i -> N*(d+2) miembros;
los indices de Sobol (Jansen) salen de las mismas corridas. Parametros (rangos acordados el 16-oct-2026):"""
import csv, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from scipy.stats import qmc

RAIZ = Path(__file__).resolve().parent.parent
DISENO = RAIZ / "datos" / "conjunto" / "diseno.csv"
RUNS = RAIZ / "runs" / "conjunto"
DIAS, SALIDA_H, NUCLEOS = 90, 4, 4          # 90 d (>3x renovacion de 23 d); salidas cada 4 h (incluye las 16 UTC de Sentinel-2); 4 nucleos + 2 scribes
GUARDAR = (0, 1)                             # miembros que conservan los campos completos (figuras); el resto solo resumen.*
SEMILLA_DISENO = 20261016

# nombre, transformacion u in [0,1) -> valor
PARAM = [
    ("carta",   lambda u: "1879" if u < 0.5 else "1887"),             # dos levantamientos del s. XIX
    ("alfa",    lambda u: u),                                          # estado de dragado 0-1
    ("semilla", lambda u: int(u * 1_000_000)),                         # realizacion del error de carta (sigma 0,9 m, L 150 m)
    ("datum",   lambda u: 0.5 * u),                                    # nivel de referencia de la carta, 0 a +0,5 m
    ("cd",      lambda u: float(np.exp(np.log(0.001) + u * np.log(5)))),  # friccion de fondo 0,001-0,005, log-uniforme
    ("vfac",    lambda u: 0.8 + 0.4 * u),                              # fuerza del viento x0,8-1,2
    ("vrot",    lambda u: -15 + 30 * u),                               # direccion del viento +-15 grados
    ("mfac",    lambda u: 0.9 + 0.2 * u),                              # amplitud de la marea x0,9-1,1
]
__doc__ += "\n" + "\n".join(f"  {n}" for n, _ in PARAM)


def diseno(N):
    d = len(PARAM)
    U = qmc.Sobol(2 * d, scramble=True, seed=SEMILLA_DISENO).random(N)   # N potencia de 2
    A, B = U[:, :d], U[:, d:]
    filas = [("A", j, A[j]) for j in range(N)] + [("B", j, B[j]) for j in range(N)]
    for i in range(d):
        ABi = A.copy(); ABi[:, i] = B[:, i]
        filas += [(f"AB{i + 1}", j, ABi[j]) for j in range(N)]
    DISENO.parent.mkdir(parents=True, exist_ok=True)
    with open(DISENO, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["miembro", "bloque", "j"] + [n for n, _ in PARAM] + [f"u_{n}" for n, _ in PARAM])
        for m, (bl, j, u) in enumerate(filas):
            w.writerow([m, bl, j] + [t(v) for (_, t), v in zip(PARAM, u)] + [f"{v:.6f}" for v in u])
    print(f"{len(filas)} miembros = {N} x ({d} + 2) -> {DISENO}")
    return filas


def prueba():
    """Mismas matrices A, B, AB_i y estimadores de Jansen sobre Ishigami (indices exactos conocidos)."""
    d, N = 3, 4096; U = qmc.Sobol(2 * d, scramble=True, seed=1).random(N); A, B = U[:, :d], U[:, d:]
    f = lambda u: (lambda x: np.sin(x[:, 0]) + 7 * np.sin(x[:, 1]) ** 2 + 0.1 * x[:, 2] ** 4 * np.sin(x[:, 0]))(np.pi * (2 * u - 1))
    fA, fB = f(A), f(B); V = np.var(np.r_[fA, fB])
    for i, (s_ex, st_ex) in enumerate([(0.314, 0.558), (0.442, 0.442), (0.0, 0.244)]):
        ABi = A.copy(); ABi[:, i] = B[:, i]; fAB = f(ABi)
        S, ST = (V - 0.5 * np.mean((fB - fAB) ** 2)) / V, 0.5 * np.mean((fA - fAB) ** 2) / V
        assert abs(S - s_ex) < 0.02 and abs(ST - st_ex) < 0.02, (i, S, ST)
    print("autoprueba Saltelli/Jansen: ok")


def lee():
    with open(DISENO) as f: return list(csv.DictReader(f))


def uno(fila):
    m = int(fila["miembro"]); run = RUNS / f"m{m:04d}"
    if (run / "param.nml").exists(): return m, "ya"
    env = {**os.environ, "RUNDIR": str(run), "CASO": f"c{m:04d}", "CARTA": fila["carta"], "ALFA": fila["alfa"],
           "SEMILLA": fila["semilla"], "DATUM": fila["datum"], "CD": fila["cd"], "VFAC": fila["vfac"],
           "VROT": fila["vrot"], "MFAC": fila["mfac"], "SALIDA_H": str(SALIDA_H)}
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "caso_real.py"), str(DIAS)], env=env, capture_output=True, text=True)
    if r.returncode: (run.parent / f"error_m{m:04d}.txt").write_text(r.stdout + r.stderr); return m, "ERROR"
    for q in ("correr.sh", "correr_slurm.sh"): (run / q).unlink(missing_ok=True)
    return m, "ok"


def generar(J):
    filas = lee(); RUNS.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(J) as ex:
        for k, (m, est) in enumerate(ex.map(uno, filas)):
            if est == "ERROR" or k % 50 == 0: print(f"m{m:04d}: {est}  ({k + 1}/{len(filas)})", flush=True)
    n = len(filas)
    (RUNS / "correr_array.sh").write_text(f"""#!/bin/bash -l
# Lemaitre4. Desde la raiz del repo en el Mac (copia casos + sflux con la misma estructura, enlaces relativos):
#   rsync -aR ./runs/conjunto ./datos/forzamiento/sflux ./scripts/posproceso.py ./datos/conjunto/posproceso_malla.npz lemaitre4:bahia/
#   ssh lemaitre4 'bash -lc "cd bahia/runs/conjunto && sbatch --array=0-{n - 1}%{4096 // (NUCLEOS + 2)} correr_array.sh"'
# Prueba previa: --array=0-1
#SBATCH --job-name=bahia_conj
#SBATCH --ntasks={NUCLEOS + 2}
#SBATCH --time=08:00:00
#SBATCH --mem-per-cpu=2000
#SBATCH --output=slurm_%A_%a.out
set -eo pipefail
module purge >/dev/null 2>&1 || true
case "$SLURM_CLUSTER_NAME" in
  nic5) module load releases/2023b foss/2023b netCDF-Fortran/4.6.1-gompi-2023b ;;
  *)    module load releases/2024a foss/2024a netCDF-Fortran/4.6.1-gompi-2024a ;;
esac
cd $(printf "m%04d" $SLURM_ARRAY_TASK_ID)
grep -qs "Run completed successfully" outputs/mirror.out && {{ echo "ya hecho"; exit 0; }}
START=$(date +%s)
srun $HOME/schism/build/bin/pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL 2 > outputs/pantalla.log 2>&1 || true
grep -q "Run completed successfully" outputs/mirror.out && OK=si || OK=no
T=$(( $(date +%s) - START ))
# posproceso (numpy + netCDF4) y, si salio bien, borrar los campos completos
P=no
if [ $OK = si ]; then
  module load netcdf4-python/1.7.1.post2-foss-2024a >/dev/null 2>&1 || true
  python ../../../scripts/posproceso.py . ../../../datos/conjunto/posproceso_malla.npz > posproceso.log 2>&1 && P=si
  case " {' '.join(map(str, GUARDAR))} " in *" $SLURM_ARRAY_TASK_ID "*) ;; *) [ $P = si ] && rm -f outputs/*.nc ;; esac
fi
echo "$SLURM_ARRAY_TASK_ID $SLURM_CLUSTER_NAME segundos=$T completo=$OK posproceso=$P" >> ../coste.txt
""")
    print(f"listo: {n} casos en {RUNS}; lanzador {RUNS / 'correr_array.sh'}")


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else "diseno"
    if accion == "diseno":
        filas = diseno(int(sys.argv[2]) if len(sys.argv) > 2 else 64)
    elif accion == "prueba":
        prueba()
    elif accion == "generar":
        generar(int(sys.argv[2]) if len(sys.argv) > 2 else 6)
    else:
        sys.exit(__doc__)
