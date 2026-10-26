#!/usr/bin/env python3
"""Conjunto de Saltelli: diseno, generacion de los casos SCHISM y lanzador para Lemaitre4.

  python scripts/conjunto.py diseno  [N=64]      -> datos/conjunto/diseno.csv (versionado)
  CONJ_DIR=runs/mecanismo CONJ_DIAS=365 python scripts/conjunto.py mecanismo   -> 3 experimentos de mecanismo
  python scripts/conjunto.py prueba               -> autoprueba: Jansen sobre Ishigami con la misma construccion
  python scripts/conjunto.py generar [J=6] [m,m,...]  -> runs/conjunto/mNNNN/ (caso_real.py por miembro, J a la vez;
                                                    solo los miembros indicados si se da la lista)
                                                    + runs/conjunto/correr_array.sh
Diseno: Saltelli (2002) con Sobol aleatorizado (scipy.stats.qmc): matrices A, B y AB_i -> N*(d+2) miembros;
los indices de Sobol (Jansen) salen de las mismas corridas. Todos los miembros: marea EOT20 y rios de JICA 2004
(2,14 m3/s) con densidad; los rios no son dimension del Sobol. Parametros (rangos acordados el 16-oct-2026):"""
import csv, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from scipy.stats import qmc

RAIZ = Path(__file__).resolve().parent.parent
DISENO = RAIZ / "datos" / "conjunto" / "diseno.csv"
RUNS = RAIZ / os.environ.get("CONJ_DIR", "runs/conjunto")     # p. ej. CONJ_DIR=runs/largo CONJ_DIAS=365
DIAS, SALIDA_H, NUCLEOS = int(os.environ.get("CONJ_DIAS", 90)), 4, 4
SEG = min(DIAS, int(os.environ.get("CONJ_SEG", 73)))   # dias por tramo de Slurm (hotstart entre tramos); 73 d midieron 2,4-7,1 h -> se piden 10 h
ESCRIBAS = 3                                 # SCHISM exige >= 1 scribe por variable 3D de salida (AGE_1 + salinidad + ...)
GUARDAR = (0, 1, 2)                           # miembros que conservan los campos completos (figuras); el resto solo resumen.*
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
           "VROT": fila["vrot"], "MFAC": fila["mfac"], "SALIDA_H": str(SALIDA_H),
           "MAREA": "eot20", "RIOS": "1", **fila.get("extra", {})}   # conjunto: EOT20 (CC BY) + rios JICA y densidad (21-oct, Alex)
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "caso_real.py"), str(DIAS)], env=env, capture_output=True, text=True)
    if r.returncode: (run.parent / f"error_m{m:04d}.txt").write_text(r.stdout + r.stderr); return m, "ERROR"
    for q in ("correr.sh", "correr_slurm.sh"): (run / q).unlink(missing_ok=True)
    return m, "ok"


# Experimentos de mecanismo: un miembro central, marea EOT20; se anade un proceso cada vez
BASE = dict(carta="1887", alfa="0.5", semilla="-1", datum="0.25", cd="0.0025", vfac="1", vrot="0", mfac="1")
MECANISMO = [("solo marea", {"NWS": "0", "RIOS": "0"}), ("marea + viento", {"NWS": "2", "RIOS": "0"}),
             ("marea + viento + rios y densidad", {"NWS": "2", "RIOS": "1"})]


def caso_dt():
    import re
    return re.search(r"^DT = ([0-9.]+)", (RAIZ / "scripts" / "caso_real.py").read_text(), re.M).group(1)


def generar(J, solo=None, filas=None):
    filas = filas or [f for f in lee() if solo is None or int(f["miembro"]) in solo]; RUNS.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(J) as ex:
        for k, (m, est) in enumerate(ex.map(uno, filas)):
            if est == "ERROR" or k % 50 == 0: print(f"m{m:04d}: {est}  ({k + 1}/{len(filas)})", flush=True)
    n = len(filas)
    K = int(np.ceil(DIAS / SEG)); conc = 4096 // (NUCLEOS + ESCRIBAS)
    (RUNS / "correr_array.sh").write_text(f"""#!/bin/bash -l
# Lemaitre4. Un tramo de {SEG} d por trabajo; lanzar.sh encadena los {K} tramos (cada miembro sigue a su propio tramo
# anterior con --dependency=aftercorr). Desde la raiz del repo en el Mac:
#   rsync -aR ./{RUNS.relative_to(RAIZ)} ./datos/forzamiento/sflux ./scripts/posproceso.py ./datos/conjunto/posproceso_malla.npz lemaitre4:bahia/
#   ssh lemaitre4 'bash -lc "cd bahia/{RUNS.relative_to(RAIZ)} && bash lanzar.sh"'        (prueba: bash lanzar.sh 0-1)
#SBATCH --job-name=bahia_conj
#SBATCH --ntasks={NUCLEOS + ESCRIBAS}
#SBATCH --time={int(np.ceil(SEG / 73 * 7.5)) + 2:02d}:00:00
#SBATCH --mem-per-cpu=4000
#SBATCH --output=slurm_%A_%a.out
set -eo pipefail
module purge >/dev/null 2>&1 || true
case "$SLURM_CLUSTER_NAME" in
  nic5) module load releases/2023b foss/2023b netCDF-Fortran/4.6.1-gompi-2023b ;;
  *)    module load releases/2024a foss/2024a netCDF-Fortran/4.6.1-gompi-2024a ;;
esac
cd $(printf "m%04d" $SLURM_ARRAY_TASK_ID)
[ -f HECHO ] && {{ echo "ya hecho"; exit 0; }}
DT={caso_dt()}; TOTAL={DIAS}; SEG={SEG}; PASOS_SEG=$(( SEG * 86400 / ${{DT%.*}} ))
# reanudar: combinar el hotstart por rango que dejo el tramo anterior (outputs/hotstart_000000_<paso>.nc)
IT=$(ls outputs/hotstart_000000_*.nc 2>/dev/null | sed 's/.*_\\([0-9]*\\)\\.nc/\\1/' | sort -n | tail -1 || true)
if [ -n "$IT" ]; then
  (cd outputs && $HOME/schism/build/bin/combine_hotstart7 -i $IT > combine.log 2>&1) && mv "outputs/hotstart_it=$IT.nc" hotstart.nc
  rm -f outputs/hotstart_0*_*.nc; IHOT=2; HECHOS=$(( IT * ${{DT%.*}} / 86400 ))
else
  IHOT=0; HECHOS=0
fi
FIN=$(( HECHOS + SEG < TOTAL ? HECHOS + SEG : TOTAL ))
sed -i -E "s/^( *rnday *=).*/\\1 $FIN/; s/^( *ihot *=).*/\\1 $IHOT/; s/^( *nhot *=).*/\\1 1/; s/^( *nhot_write *=).*/\\1 $PASOS_SEG/" param.nml
echo "tramo: dias $HECHOS -> $FIN de $TOTAL (ihot=$IHOT)"
mv outputs/mirror.out outputs/mirror_hasta_$HECHOS.out 2>/dev/null || true   # el "Run completed" debe ser de este tramo
START=$(date +%s)
srun $HOME/schism/build/bin/pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL {ESCRIBAS} > outputs/pantalla_$FIN.log 2>&1 || true
grep -q "Run completed successfully" outputs/mirror.out && OK=si || OK=no
T=$(( $(date +%s) - START ))
echo "$SLURM_ARRAY_TASK_ID $SLURM_CLUSTER_NAME tramo=$HECHOS-$FIN segundos=$T completo=$OK" >> ../coste.txt
[ $OK = si ] || exit 1                                   # corta la cadena de este miembro
[ $FIN -lt $TOTAL ] && exit 0                            # quedan tramos
# ultimo tramo: posproceso (numpy + netCDF4) y, si salio bien, borrar los campos completos
P=no
module load netcdf4-python/1.7.1.post2-foss-2024a >/dev/null 2>&1 || true
python ../../../scripts/posproceso.py . ../../../datos/conjunto/posproceso_malla.npz > posproceso.log 2>&1 && P=si
case " {' '.join(map(str, GUARDAR))} " in *" $SLURM_ARRAY_TASK_ID "*) ;; *) [ $P = si ] && rm -f outputs/*.nc ;; esac
echo "$SLURM_ARRAY_TASK_ID posproceso=$P" >> ../coste.txt; touch HECHO
""")
    (RUNS / "lanzar.sh").write_text(f"""#!/bin/bash -l
# Encadena los {K} tramos de {SEG} d. Uso: bash lanzar.sh [rango del array, por defecto 0-{n - 1}]
R=${{1:-0-{n - 1}}}
J=$(sbatch --parsable --array=$R%{conc} correr_array.sh); echo "tramo 1: $J"
for k in $(seq 2 {K}); do
  J=$(sbatch --parsable --array=$R%{conc} --dependency=aftercorr:$J --kill-on-invalid-dep=yes correr_array.sh); echo "tramo $k: $J"
done
""")
    print(f"listo: {n} casos en {RUNS}; lanzador {RUNS / 'correr_array.sh'}")


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else "diseno"
    if accion == "diseno":
        filas = diseno(int(sys.argv[2]) if len(sys.argv) > 2 else 64)
    elif accion == "prueba":
        prueba()
    elif accion == "mecanismo":     # CONJ_DIR=runs/mecanismo CONJ_DIAS=365 python scripts/conjunto.py mecanismo
        filas = [dict(BASE, miembro=str(k), extra={"MAREA": "eot20", **e}) for k, (_, e) in enumerate(MECANISMO)]
        for k, (nom, _) in enumerate(MECANISMO): print(f"m{k:04d}: {nom}")
        generar(3, filas=filas)
    elif accion == "generar":
        generar(int(sys.argv[2]) if len(sys.argv) > 2 else 6,
                [int(m) for m in sys.argv[3].split(",")] if len(sys.argv) > 3 else None)
    else:
        sys.exit(__doc__)
