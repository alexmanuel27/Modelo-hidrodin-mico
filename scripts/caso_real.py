#!/usr/bin/env python3
"""Caso SCHISM con la malla real (09_malla.py) y la batimetria de un miembro del conjunto (08).

Marea FES2022b en el borde abierto (scripts/marea_fes2022.py; MAREA=m2 -> M2 uniforme de 0,15 m de prueba), viento ERA5,
3D barotropico, Coriolis activado por defecto, modulo AGE (edad del agua desde que sale del mar).

Uso:  python scripts/caso_real.py [dias]            (por defecto 2)
      variables: CASO (nombre), NCOR (1), NWS (2), CARTA (1887), ALFA (0), SEMILLA (-1 = sin campo aleatorio),
                 MAREA (fes si existe datos/marea/fes2022_habana.json; si no m2),
                 parametros del conjunto: DATUM (m, 0), CD (0.0025), VFAC (x viento, 1), VROT (grados, 0),
                 MFAC (x amplitud de marea, 1), SALIDA_H (horas entre salidas, 1), RUNDIR (carpeta del caso)
      Mac:   bash runs/real_<CASO>/correr.sh
      CECI:  ver runs/real_<CASO>/correr_slurm.sh
Requiere numpy, scipy y, con MAREA=fes, pyTMD (correcciones nodales; pip install pyTMD), y datos/batimetria/superficies/*.nc (07) + datos/malla/hgrid.{gr3,ll} (09).
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
RUN = Path(os.environ["RUNDIR"]) if "RUNDIR" in os.environ else RAIZ / "runs" / f"real_{CASO}"
NCOR = int(os.environ.get("NCOR", 1))
NWS = int(os.environ.get("NWS", 2))
CARTA, ALFA, SEMILLA = os.environ.get("CARTA", "1887"), float(os.environ.get("ALFA", 0)), int(os.environ.get("SEMILLA", -1))
DATUM, VFAC, VROT, MFAC = (float(os.environ.get(k, d)) for k, d in (("DATUM", 0), ("VFAC", 1), ("VROT", 0), ("MFAC", 1)))
SALIDA_H = float(os.environ.get("SALIDA_H", 1))
SCHISM = Path(os.environ.get("SCHISM_DIR", Path.home() / "modelos" / "schism"))
BIN_MAC = SCHISM / "build" / "bin" / "pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL"
SFLUX = RAIZ / "datos" / "forzamiento" / "sflux"
MALLA = RAIZ / "datos" / "malla"
SUP = RAIZ / "datos" / "batimetria" / "superficies"

RNDAY = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
DT = 100.0
INICIO = (2016, 1, 1)
M2_AMP = 0.15                 # m, solo con MAREA=m2 (prueba)
FES = RAIZ / "datos" / "marea" / "fes2022_habana.json"
MAREA = os.environ.get("MAREA", "fes" if FES.exists() else "m2")
FREC = dict(m2=1.405189e-4, s2=1.454441e-4, n2=1.378797e-4, k2=1.458423e-4, k1=7.292117e-5, o1=6.759774e-5,
            p1=7.251056e-5, q1=6.495854e-5, m4=2.810378e-4, ms4=2.859630e-4, mn4=2.783986e-4)   # rad/s
H_TOPE = 200.0                # m: profundidad maxima del modelo (el talud llega a 1200 m; solo importa la onda de marea)
NV = 16                       # niveles verticales: S puros; con h_s > fondo maximo SCHISM no pide niveles Z (h_s = H_TOPE+10)
D_ADV = 800.0                 # m: sin adveccion de momento a menos de esto del borde abierto
CD = float(os.environ.get("CD", 0.0025))
# Correccion del borde abierto (prueba del 13-oct: chorro espurio de hasta 2 m/s donde el arco abierto
# corta la costa en el extremo E, alimentado por el viento con el nivel impuesto en el borde):
ESPONJA = int(os.environ.get("ESPONJA", 1))   # friccion 0,0025 -> 0,05 a menos de R_ESQ del borde abierto
R_ESQ = 1000.0
VIENTO_BORDE = (1000.0, 2000.0)               # m: sin viento a < 1 km del borde abierto, completo a > 2 km (windfactor.gr3)


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


def armonicos_fes(lon, lat):
    """Amplitud (m) y fase (grados, Greenwich) de cada constituyente de FES2022 en (lon, lat): bilineal en
    complejo (sin saltos de fase); si un vecino es tierra/NaN, el punto valido mas cercano."""
    out = {}
    for c, d in __import__("json").loads(FES.read_text()).items():
        z = np.array(d["amp_m"]) * np.exp(-1j * np.radians(np.array(d["fase_grados"])))
        glo, gla = np.array(d["lon"]), np.array(d["lat"])
        orden = np.argsort(gla); gla, z = gla[orden], z[orden]
        f = RegularGridInterpolator((gla, glo), z, bounds_error=False, fill_value=np.nan)
        v = f(np.c_[lat, lon])
        ok = np.isfinite(z); GA, GO = np.meshgrid(gla, glo, indexing="ij")
        for k in np.where(~np.isfinite(v))[0]:
            v[k] = z[ok][np.argmin(np.hypot(GA[ok] - lat[k], GO[ok] - lon[k]))]
        out[c] = (np.abs(v), np.degrees(-np.angle(v)) % 360)
    return out


def nodales(constituyentes, dias):
    """(f, V0+u en grados) para bctides.in: V0 al inicio, f y u a mitad de la simulacion (pyTMD, convencion FES)."""
    try:
        from pyTMD.arguments import arguments
    except ImportError:
        sys.exit("MAREA=fes necesita pyTMD:  pip install pyTMD")
    mjd0 = (np.datetime64(f"{INICIO[0]:04d}-{INICIO[1]:02d}-{INICIO[2]:02d}") - np.datetime64("1858-11-17")).astype(int)
    _, _, G = arguments(np.array([float(mjd0)]), constituyentes, corrections="FES")
    pu, pf, _ = arguments(np.array([mjd0 + dias / 2]), constituyentes, corrections="FES")
    return pf[0], (G[0] + np.degrees(pu[0])) % 360


def main():
    RUN.mkdir(parents=True, exist_ok=True); (RUN / "outputs").mkdir(exist_ok=True)
    xy, tri, resto = lee_hgrid(MALLA / "hgrid.gr3")
    x, y = xy.T; n, ne = len(x), len(tri)
    lon, lat = utm_inv(x, y)
    abierto = [int(l) - 1 for l in resto[3:3 + int(resto[2].split()[0])]]
    # batimetria del miembro en los nodos
    gx, gy, h, _ = conj.miembro(str(SUP), carta=CARTA, alfa=ALFA, sigma=conj.SIGMA if SEMILLA >= 0 else 0, semilla=max(SEMILLA, 0), datum=DATUM)
    f = RegularGridInterpolator((gy, gx), np.nan_to_num(h, nan=conj.PROF_MIN), bounds_error=False, fill_value=conj.PROF_MIN)
    prof = np.clip(f(np.c_[y, x]), conj.PROF_MIN, H_TOPE)
    escribir_gr3(RUN / "hgrid.gr3", x, y, prof, tri, f"Bahia de La Habana UTM17N carta={CARTA} alfa={ALFA} semilla={SEMILLA} datum={DATUM}", resto)
    escribir_gr3(RUN / "hgrid.ll", lon, lat, prof, tri, "hgrid.ll", resto)
    d_borde = np.min(np.hypot(x[:, None] - x[abierto][None], y[:, None] - y[abierto][None]), axis=1)
    cd = CD + (0.05 - CD) * np.clip(1 - d_borde / R_ESQ, 0, 1) ** 2 if ESPONJA else np.full(n, CD)   # todo el borde: 4,45 m/s en el arco (17-oct)
    escribir_gr3(RUN / "drag.gr3", x, y, cd, tri, "drag.gr3 (esponja junto al borde abierto)")
    fv = VFAC * (np.clip((d_borde - VIENTO_BORDE[0]) / (VIENTO_BORDE[1] - VIENTO_BORDE[0]), 0, 1) if ESPONJA else np.ones(n))
    escribir_gr3(RUN / "windfactor.gr3", x, y, fv, tri, "windfactor: 0 junto al borde abierto")
    for nombre, v in (("diffmin.gr3", 1e-6), ("diffmax.gr3", 1e-2)):
        escribir_gr3(RUN / nombre, x, y, np.full(n, v), tri, nombre)
    # convergencia de meridianos UTM (grados) para girar el viento de geografico a la malla
    conv = np.degrees(np.arctan(np.tan(np.radians(lon + 81)) * np.sin(np.radians(lat))))
    escribir_gr3(RUN / "windrot_geo2proj.gr3", x, y, conv + VROT, tri, "windrot: convergencia UTM 17N (grados)")
    escribir_gr3(RUN / "adv.gr3", x, y, (d_borde >= D_ADV).astype(float), tri, "adv: 0 junto al borde abierto")
    import importlib as il
    malla = il.import_module("09_malla")
    mar = (~malla.en_bahia(xy)).astype(float)                # agua nueva = la que esta fuera de la bahia
    escribir_gr3(RUN / "AGE_hvar_1.ic", x, y, mar, tri, "AGE 1: 1 fuera de la bahia")
    escribir_gr3(RUN / "AGE_hvar_2.ic", x, y, np.zeros(n), tri, "AGE 2")
    (RUN / "tvd.prop").write_text("".join(f"{k+1} 1\n" for k in range(ne)))
    (RUN / "vgrid.in").write_text(
        f"2 !ivcor\n{NV} 1 {H_TOPE + 10:.1f} !nvrt, kz, h_s\nZ levels\n1 -{H_TOPE + 10:.1f}\nS levels\n5. 0. 1.e-4 !h_c, theta_b, theta_f\n"
        + "".join(f"{k+1} {-1 + k / (NV - 1):.4f}\n" for k in range(NV)))
    (RUN / "ts.ic").write_text(f"2\n1 -{H_TOPE + 10:.0f}. 28. 36.\n2 0. 28. 36.\n")
    if MAREA == "fes":
        arm = armonicos_fes(lon[abierto], lat[abierto]); cs = list(arm)
        ff, eq = nodales(cs, RNDAY)
        b = [f"{INICIO} marea FES2022b ({len(cs)} constituyentes)", "0 40. !ntip, tip_dp", f"{len(cs)} !nbfr"]
        b += [f"{c.upper()}\n{FREC[c]:.6e} {ff[k]:.5f} {eq[k]:.3f}" for k, c in enumerate(cs)]
        b += ["1 !nope", f"{len(abierto)} 3 0 0 0 0 !nodos, elev=armonica, vel, T, S, AGE"]
        for c in cs:
            b += [c.upper()] + [f"{a * MFAC:.5f} {g:.2f}" for a, g in zip(*arm[c])]
        (RUN / "bctides.in").write_text("\n".join(b) + "\n")
        print("marea FES2022 en el borde: " + ", ".join(f"{c.upper()} {arm[c][0].mean() * 100:.1f} cm" for c in cs))
    else:
        (RUN / "bctides.in").write_text(
            f"{INICIO} marea M2 de prueba uniforme\n0 40. !ntip, tip_dp\n1 !nbfr\nM2\n1.405189e-04 1.0 0.0\n"
            f"1 !nope\n{len(abierto)} 3 0 0 0 0 !nodos, elev=armonica, vel, T, S, AGE\nM2\n"
            + "".join(f"{M2_AMP * MFAC} 0.\n" for _ in abierto))
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
                            nspool=int(SALIDA_H * 3600 / DT), ihfskip=int(86400 / DT)),
               "OPT": dict(start_year=INICIO[0], start_month=INICIO[1], start_day=INICIO[2],
                           start_hour=0, utc_start=0, ics=1, ihot=0, ncor=NCOR, coricoef=0,
                           slam0=round(float(lon.mean()), 4), sfea0=round(float(lat.mean()), 4),
                           nchi=0, ic_elev=0, nadv=0, nws=NWS, wtiminc=DT, ishapiro=1, drampwind=1, iwindoff=ESPONJA,
                           ihconsv=0, itur=3, itr_met=3, level_age=-999, **{"flag_ic(1)": 2, "flag_ic(2)": 2}),
               "SCHOUT": {"nhot": 0, "iout_sta": 0, "iof_hydro(1)": 1, "iof_hydro(14)": 1,
                          "iof_hydro(16)": 1, "iof_hydro(25)": 0, "iof_hydro(26)": 0, "iof_age(1)": 1}}   # AGE_1 = edad en dias (alfa/C/86400)
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
