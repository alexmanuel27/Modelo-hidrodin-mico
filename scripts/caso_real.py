#!/usr/bin/env python3
"""Caso SCHISM con la malla real (09_malla.py) y la batimetria de un miembro del conjunto (08).

Prueba de humo y de coste: marea M2 uniforme PROVISIONAL (0,15 m) hasta tener FES2022, viento ERA5,
3D barotropico, Coriolis activado por defecto, modulo AGE (edad del agua desde que sale del mar).

Uso:  python scripts/caso_real.py [dias]            (por defecto 2)
      variables: CASO (nombre), NCOR (1), NWS (2), CARTA (1887), ALFA (0), SEMILLA (-1 = sin campo aleatorio)
      Mac:   bash runs/real_<CASO>/correr.sh
      CECI:  ver runs/real_<CASO>/correr_slurm.sh
Requiere numpy y scipy, y datos/batimetria/superficies/*.nc (07) + datos/malla/hgrid.{gr3,ll} (09).
"""
import os, re, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts" / "batimetria"))
from utm import utm_inv                                   # noqa: E402
import importlib
conj = importlib.import_module("08_batimetria_conjunto")
from scipy.interpolate import RegularGridInterpolator     # noqa: E402

CASO = os.environ.get("CASO", "prueba")
RUN = RAIZ / "runs" / f"real_{CASO}"
NCOR = int(os.environ.get("NCOR", 1))
NWS = int(os.environ.get("NWS", 2))
CARTA, ALFA, SEMILLA = os.environ.get("CARTA", "1887"), float(os.environ.get("ALFA", 0)), int(os.environ.get("SEMILLA", -1))
SCHISM = Path(os.environ.get("SCHISM_DIR", Path.home() / "modelos" / "schism"))
BIN_MAC = SCHISM / "build" / "bin" / "pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL"
SFLUX = RAIZ / "datos" / "forzamiento" / "sflux"
MALLA = RAIZ / "datos" / "malla"
SUP = RAIZ / "datos" / "batimetria" / "superficies"

RNDAY = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
DT = 100.0
INICIO = (2016, 1, 1)
M2_AMP = 0.15                 # m, PROVISIONAL (FES2022 pendiente)
H_TOPE = 200.0                # m: profundidad maxima del modelo (el talud llega a 1200 m; solo importa la onda de marea)
NV = 16                       # niveles verticales (S puros hasta H_TOPE)
D_ADV = 800.0                 # m: sin adveccion de momento a menos de esto del borde abierto
CD = 0.0025


def lee_hgrid(ruta):
    L = Path(ruta).read_text().split("\n")
    ne, nn = map(int, L[1].split())
    xy = np.array([list(map(float, l.split()[1:3])) for l in L[2:2 + nn]])
    tri = np.array([list(map(int, l.split()[2:5])) for l in L[2 + nn:2 + nn + ne]]) - 1
    resto = L[2 + nn + ne:]
    return xy, tri, resto


def escribir_gr3(ruta, x, y, val, tri, cabecera="gr3", resto=None):
    with open(ruta, "w") as f:
        f.write(f"{cabecera}\n{len(tri)} {len(x)}\n")
        f.writelines(f"{k+1} {x[k]:.8f} {y[k]:.8f} {val[k]:.6g}\n" for k in range(len(x)))
        f.writelines(f"{k+1} 3 {t[0]+1} {t[1]+1} {t[2]+1}\n" for k, t in enumerate(tri))
        if resto: f.write("\n".join(resto))


def main():
    RUN.mkdir(parents=True, exist_ok=True); (RUN / "outputs").mkdir(exist_ok=True)
    xy, tri, resto = lee_hgrid(MALLA / "hgrid.gr3")
    x, y = xy.T; n, ne = len(x), len(tri)
    lon, lat = utm_inv(x, y)
    abierto = [int(l) - 1 for l in resto[3:3 + int(resto[2].split()[0])]]
    # batimetria del miembro en los nodos
    gx, gy, h, _ = conj.miembro(str(SUP), carta=CARTA, alfa=ALFA, sigma=conj.SIGMA if SEMILLA >= 0 else 0, semilla=max(SEMILLA, 0))
    f = RegularGridInterpolator((gy, gx), np.nan_to_num(h, nan=conj.PROF_MIN), bounds_error=False, fill_value=conj.PROF_MIN)
    prof = np.clip(f(np.c_[y, x]), conj.PROF_MIN, H_TOPE)
    escribir_gr3(RUN / "hgrid.gr3", x, y, prof, tri, f"Bahia de La Habana UTM17N carta={CARTA} alfa={ALFA} semilla={SEMILLA}", resto)
    escribir_gr3(RUN / "hgrid.ll", lon, lat, prof, tri, "hgrid.ll", resto)
    d_borde = np.min(np.hypot(x[:, None] - x[abierto][None], y[:, None] - y[abierto][None]), axis=1)
    escribir_gr3(RUN / "drag.gr3", x, y, np.full(n, CD), tri, "drag.gr3")
    for nombre, v in (("diffmin.gr3", 1e-6), ("diffmax.gr3", 1e-2)):
        escribir_gr3(RUN / nombre, x, y, np.full(n, v), tri, nombre)
    # convergencia de meridianos UTM (grados) para girar el viento de geografico a la malla
    conv = np.degrees(np.arctan(np.tan(np.radians(lon + 81)) * np.sin(np.radians(lat))))
    escribir_gr3(RUN / "windrot_geo2proj.gr3", x, y, conv, tri, "windrot: convergencia UTM 17N (grados)")
    escribir_gr3(RUN / "adv.gr3", x, y, (d_borde >= D_ADV).astype(float), tri, "adv: 0 junto al borde abierto")
    import importlib as il
    malla = il.import_module("09_malla")
    mar = (~malla.en_bahia(xy)).astype(float)                # agua nueva = la que esta fuera de la bahia
    escribir_gr3(RUN / "AGE_hvar_1.ic", x, y, mar, tri, "AGE 1: 1 fuera de la bahia")
    escribir_gr3(RUN / "AGE_hvar_2.ic", x, y, np.zeros(n), tri, "AGE 2")
    (RUN / "tvd.prop").write_text("".join(f"{k+1} 1\n" for k in range(ne)))
    (RUN / "vgrid.in").write_text(
        f"2 !ivcor\n{NV} 1 {H_TOPE:.1f} !nvrt, kz, h_s\nZ levels\n1 -{H_TOPE:.1f}\nS levels\n5. 0. 1.e-4 !h_c, theta_b, theta_f\n"
        + "".join(f"{k+1} {-1 + k / (NV - 1):.4f}\n" for k in range(NV)))
    (RUN / "ts.ic").write_text("2\n1 -200. 28. 36.\n2 0. 28. 36.\n")
    (RUN / "bctides.in").write_text(
        f"{INICIO} marea M2 PROVISIONAL uniforme\n0 40. !ntip, tip_dp\n1 !nbfr\nM2\n1.405189e-04 1.0 0.0\n"
        f"1 !nope\n{len(abierto)} 3 0 0 0 0 !nodos, elev=armonica, vel, T, S, AGE\nM2\n"
        + "".join(f"{M2_AMP} 0.\n" for _ in abierto))
    s = RUN / "sflux"; s.mkdir(exist_ok=True)
    for q in s.glob("*.nc"): q.unlink()
    y0, m0, _ = INICIO; nmes = int(np.ceil(RNDAY / 28)) + 1
    for k in range(nmes):
        yy, mm = y0 + (m0 - 1 + k) // 12, (m0 - 1 + k) % 12 + 1
        for tipo in ("air", "rad", "prc"):
            fuente = SFLUX / f"sflux_{tipo}_{yy}{mm:02d}.nc"
            assert fuente.exists(), f"falta {fuente}: ejecuta antes scripts/era5_a_sflux.py"
            (s / f"sflux_{tipo}_1.{k+1}.nc").symlink_to(os.path.relpath(fuente, s))
    (s / "sflux_inputs.txt").write_text(
        "&sflux_inputs\nair_1_max_window_hours=745.,\nrad_1_max_window_hours=745.,\nprc_1_max_window_hours=745.,\n/\n")
    p = (SCHISM / "sample_inputs" / "param.nml").read_text()
    cambios = {"CORE": dict(ipre=0, ibc=1, ibtp=1, rnday=RNDAY, dt=DT, ntracer_age=2,
                            nspool=int(3600 / DT), ihfskip=int(86400 / DT)),
               "OPT": dict(start_year=INICIO[0], start_month=INICIO[1], start_day=INICIO[2],
                           start_hour=0, utc_start=0, ics=1, ihot=0, ncor=NCOR, coricoef=0,
                           slam0=round(float(lon.mean()), 4), sfea0=round(float(lat.mean()), 4),
                           nchi=0, ic_elev=0, nadv=0, nws=NWS, wtiminc=DT, ishapiro=1, drampwind=1, iwindoff=0,
                           ihconsv=0, itur=3, itr_met=3, level_age=-999, **{"flag_ic(1)": 2, "flag_ic(2)": 2}),
               "SCHOUT": {"nhot": 0, "iout_sta": 0, "iof_hydro(1)": 1, "iof_hydro(14)": 1,
                          "iof_hydro(16)": 1, "iof_hydro(25)": 0, "iof_hydro(26)": 0, "iof_age(1)": 1}}
    for sec, kv in cambios.items():
        a = p.index(f"&{sec}"); b = p.index("\n/", a); bloque = p[a:b]
        for k, v in kv.items():
            patron = re.compile(rf"^(\s*){re.escape(k)}\s*=.*$", re.M)
            if len(patron.findall(bloque)) == 1:
                bloque = patron.sub(lambda mt: f"{mt.group(1)}{k} = {v}", bloque)
            else:
                bloque += f"\n  {k} = {v}"
        p = p[:a] + bloque + p[b:]
    (RUN / "param.nml").write_text(p)
    pasos = int(round(RNDAY * 86400 / DT))
    (RUN / "correr.sh").write_text(f"""#!/usr/bin/env bash
# Mac: 1 proceso de calculo + 2 scribes. Uso: bash {RUN.relative_to(RAIZ)}/correr.sh
set -eo pipefail
cd "$(dirname "$0")"
source "$HOME/miniforge3/etc/profile.d/conda.sh"; conda activate bahia
NP=${{NP:-3}}; NS=2
START=$(date +%s)
mpirun -np $NP {BIN_MAC} $NS > outputs/pantalla.log 2>&1 || true
grep -q "Run completed successfully" outputs/mirror.out || {{ echo "!! SCHISM fallo: mira outputs/pantalla.log y outputs/fatal.error"; exit 1; }}
T=$(( $(date +%s) - START ))
echo "tiempo: $T s para {pasos} pasos con $((NP-NS)) proceso(s) de calculo" | tee outputs/tiempo.txt
""")
    (RUN / "correr_slurm.sh").write_text(f"""#!/bin/bash
# CECI (NIC5 o Lemaitre4). Desde el Mac:
#   rsync -aL {RUN.relative_to(RAIZ)}/ nic5:real_{CASO}/      (-L copia los sflux enlazados)
#   ssh nic5 'cd real_{CASO} && for n in 4 8 16 32; do sbatch --ntasks=$((n+2)) correr_slurm.sh; done'
#SBATCH --job-name=bahia_{CASO}
#SBATCH --time=02:00:00
#SBATCH --mem-per-cpu=2000
#SBATCH --output=slurm_%j.out
set -eo pipefail
module purge >/dev/null 2>&1 || true
# los mismos modulos con los que se compilo SCHISM en cada cluster (cluster/schism_<cluster>.log)
case "$SLURM_CLUSTER_NAME" in
  nic5) module load releases/2023b foss/2023b netCDF-Fortran/4.6.1-gompi-2023b ;;
  *)    module load releases/2024a foss/2024a netCDF-Fortran/4.6.1-gompi-2024a ;;
esac
module list 2>&1 | tail -5
NS=2
D=n${{SLURM_NTASKS}}_$SLURM_JOB_ID; mkdir -p $D/outputs
cp -rL $(ls | grep -v -e '^n[0-9]' -e '^slurm_') $D/ 2>/dev/null || true
cd $D
START=$(date +%s)
srun $HOME/schism/build/bin/pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL $NS > outputs/pantalla.log 2>&1 || true
T=$(( $(date +%s) - START ))
grep -q "Run completed successfully" outputs/mirror.out && OK=si || OK=no
echo "$SLURM_CLUSTER_NAME ntasks=$SLURM_NTASKS calculo=$((SLURM_NTASKS-NS)) pasos={pasos} segundos=$T completo=$OK" | tee -a ../coste.txt
""")
    print(f"{n} nodos, {ne} elementos, {len(abierto)} nodos de borde abierto; prof {prof.min():.1f}-{prof.max():.0f} m; "
          f"bahia {int((mar == 0).sum())} nodos; {RNDAY:g} dias ({pasos} pasos); NCOR={NCOR}; listo en {RUN}")


if __name__ == "__main__":
    main()
