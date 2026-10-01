#!/usr/bin/env python3
"""Caso de prueba idealizado de SCHISM (sin batimetria real): prueba de humo y coste por paso.

Geometria esquematica, con las cifras del control analitico (prisma_marea.py):
  bahia 2650 x 2000 m, 9 m  |  canal 250 x 1530 m, 12,8 m  |  mar 4050 x 2000 m, 30 m
Situada en su posicion real (origen en 23,125 N, 82,335 W) para usar el sflux de ERA5.
Forzamiento: marea M2 de 0,15 m de amplitud en los bordes N, E y O del mar + viento ERA5 (nws=2).
3D barotropico, 10 capas sigma, sin Coriolis, modulo AGE: edad del agua desde que sale del mar.

Uso:  python scripts/caso_prueba.py [dias] [dx_m]      (por defecto 2 dias, 50 m)
      bash runs/prueba_idealizada/correr.sh
Variantes (cada una en su carpeta, se pueden correr a la vez):
      CASO=sinviento NWS=0 python scripts/caso_prueba.py 2    -> runs/prueba_idealizada_sinviento
      CASO=shapiro2 ISHAPIRO=2 python scripts/caso_prueba.py 2
      CASO=esponja ESPONJA=1 ...    CASO=sincor NCOR=0 ...
"""
import os, re, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
CASO = os.environ.get("CASO", "")
RUN = RAIZ / "runs" / ("prueba_idealizada" + (f"_{CASO}" if CASO else ""))
NWS = int(os.environ.get("NWS", 2))            # 2: viento/presion ERA5; 0: solo marea
ISHAPIRO = int(os.environ.get("ISHAPIRO", 1))  # 1: filtro fijo 0,5; 2: tipo Smagorinsky (shapiro.gr3)
ESPONJA = int(os.environ.get("ESPONJA", 0))    # 1: friccion creciente en 250 m junto al borde abierto
# Sin Coriolis por defecto: en este dominio de juguete (mar de 4 x 2 km, 30 m, abierto por 3 lados)
# la rotacion + nivel impuesto en el borde da una inestabilidad que crece x2,7 cada ~3,5 h si hay
# viento (ver docs/00_estado_y_plan.md, sec. 16). En la malla real hay que volver a probarlo.
NCOR = int(os.environ.get("NCOR", 0))          # 1: Coriolis con la latitud de hgrid.ll; 0: sin rotacion
SCHISM = Path(os.environ.get("SCHISM_DIR", Path.home() / "modelos" / "schism"))
BIN = SCHISM / "build" / "bin" / "pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL"
SFLUX = RAIZ / "datos" / "forzamiento" / "sflux"

RNDAY = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
DX = float(sys.argv[2]) if len(sys.argv) > 2 else 50.0
DT = 100.0                      # s
INICIO = (2016, 1, 1)
LAT0, LON0 = 23.125, -82.335
M2_AMP = 0.15                   # m (rango 0,3 m)
Y_CANAL = (0.0, 1530.0)         # la bahia queda en y<0, el mar en y>1530


def profundidad(x, y):
    """Profundidad [m] en (x, y); NaN fuera del dominio."""
    h = np.full(np.shape(x), np.nan)
    h[(abs(x) <= 1325) & (y >= -2000) & (y <= 0)] = 9.0
    h[(abs(x) <= 125) & (y > 0) & (y < 1530)] = 12.8
    h[(abs(x) <= 2025) & (y >= 1530) & (y <= 3530)] = 30.0
    return h


def malla():
    xs = np.arange(-2025, 2025 + 1e-6, DX)
    ys = np.arange(-2000, 3530 + 1e-6, DX)
    X, Y = np.meshgrid(xs, ys)                       # nodos candidatos
    xc, yc = (X[:-1, :-1] + X[1:, 1:]) / 2, (Y[:-1, :-1] + Y[1:, 1:]) / 2
    celda = ~np.isnan(profundidad(xc, yc))           # celdas dentro del dominio
    nid = -np.ones(X.shape, int)
    usados = np.zeros(X.shape, bool)
    j, i = np.nonzero(celda)
    for dj, di in ((0, 0), (0, 1), (1, 0), (1, 1)):
        usados[j + dj, i + di] = True
    nid[usados] = np.arange(usados.sum())
    x, y = X[usados], Y[usados]
    a, b, c, d = nid[j, i], nid[j, i + 1], nid[j + 1, i + 1], nid[j + 1, i]
    t1, t2 = np.c_[a, b, c], np.c_[a, c, d]                  # antihorario, diagonal a-c
    # SCHISM: ningun triangulo con los 3 nodos en el contorno (pasaba en las esquinas SE y NO,
    # y generaba ruido que crecia). En esas celdas se usa la otra diagonal (b-d).
    borde = np.zeros(usados.sum(), bool)
    borde[contorno(X[usados], Y[usados], np.concatenate([t1, t2]))] = True
    mala = borde[t1].all(1) | borde[t2].all(1)
    t1[mala], t2[mala] = np.c_[a, b, d][mala], np.c_[b, c, d][mala]
    tri = np.concatenate([t1, t2])
    assert not borde[tri].all(1).any(), "quedan triangulos con 3 nodos en el contorno"
    print(f"diagonal cambiada en {mala.sum()} celdas de esquina")
    # profundidad nodal: la mayor de las celdas vecinas (asi el canal conserva su calado)
    h = np.zeros(len(x))
    hc = profundidad(xc[j, i], yc[j, i])
    for dj, di in ((0, 0), (0, 1), (1, 0), (1, 1)):
        np.maximum.at(h, nid[j + dj, i + di], hc)
    return x, y, h, tri


def contorno(x, y, tri):
    """Contorno exterior ordenado en sentido antihorario (lista de nodos, sin repetir)."""
    aristas = {}
    for t in tri:
        for k in range(3):
            e = (t[k], t[(k + 1) % 3])
            clave = tuple(sorted(e))
            aristas[clave] = None if clave in aristas else e
    sig = {a: b for a, b in (e for e in aristas.values() if e is not None)}
    n0 = next(iter(sig)); lazo = [n0]
    while sig[lazo[-1]] != n0:
        lazo.append(sig[lazo[-1]])
    assert len(lazo) == len(sig), "el dominio debe tener un solo contorno (sin islas)"
    return lazo


def escribir_gr3(ruta, x, y, val, tri, cabecera="gr3"):
    """SCHISM exige ne y np reales en la cabecera de todo .gr3/.ic."""
    with open(ruta, "w") as f:
        f.write(f"{cabecera}\n{len(tri)} {len(x)}\n")
        # 8 decimales: en hgrid.ll son grados (0,001 grado = 100 m; con 3 decimales los nodos
        # vecinos compartian coordenadas y el forzamiento ERA5 interpolado salia en escalera)
        f.writelines(f"{k+1} {x[k]:.8f} {y[k]:.8f} {val[k]:.6g}\n" for k in range(len(x)))
        f.writelines(f"{k+1} 3 {t[0]+1} {t[1]+1} {t[2]+1}\n" for k, t in enumerate(tri))


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "outputs").mkdir(exist_ok=True)
    x, y, h, tri = malla()
    n, ne = len(x), len(tri)
    lon = LON0 + x / (6371000 * np.cos(np.radians(LAT0)) * np.pi / 180)
    lat = LAT0 + y / (6371000 * np.pi / 180)

    # contorno: abierto = bordes norte, este y oeste del mar (el mar sigue mas alla); la costa, tierra.
    # (Con solo el norte abierto, el mar era una caja que atrapaba un modo este-oeste de ~8 min.)
    abre = (y == y.max()) | (x == x.min()) | (x == x.max())
    lazo = contorno(x, y, tri)
    r = next(i for i, k in enumerate(lazo) if abre[k])
    lazo = lazo[r:] + lazo[:r]
    while abre[lazo[-1]]:                              # que el tramo abierto empiece en lazo[0]
        lazo = lazo[-1:] + lazo[:-1]
    m = sum(1 for k in lazo if abre[k])
    assert all(abre[k] for k in lazo[:m]), "el borde abierto debe ser un tramo continuo"
    abierto, tierra = lazo[:m], lazo[m - 1:] + [lazo[0]]

    with open(RUN / "hgrid.gr3", "w") as f:
        f.write(f"bahia idealizada dx={DX:g} m\n{ne} {n}\n")
        f.writelines(f"{k+1} {x[k]:.3f} {y[k]:.3f} {h[k]:.3f}\n" for k in range(n))
        f.writelines(f"{k+1} 3 {t[0]+1} {t[1]+1} {t[2]+1}\n" for k, t in enumerate(tri))
        f.write(f"1 = Number of open boundaries\n{len(abierto)} = Total number of open boundary nodes\n")
        f.write(f"{len(abierto)} = Number of nodes for open boundary 1\n")
        f.writelines(f"{k+1}\n" for k in abierto)
        f.write(f"1 = number of land boundaries\n{len(tierra)} = Total number of land boundary nodes\n")
        f.write(f"{len(tierra)} 0 = Number of nodes for land boundary 1\n")
        f.writelines(f"{k+1}\n" for k in tierra)
    escribir_gr3(RUN / "hgrid.ll", lon, lat, h, tri, "hgrid.ll")
    # distancia al borde abierto (solo en el mar)
    d_borde = np.minimum.reduce([x.max() - x, x - x.min(), y.max() - y])
    d_borde[y < Y_CANAL[1]] = 1e9
    cd = np.full(n, 0.0025)
    if ESPONJA:                                     # esponja: Cd 0,0025 -> 0,05 en los ultimos 250 m
        cd = 0.0025 + (0.05 - 0.0025) * np.clip(1 - d_borde / 250, 0, 1) ** 2
    escribir_gr3(RUN / "drag.gr3", x, y, cd, tri, cabecera="drag.gr3")
    for nombre, v in (("diffmin.gr3", 1e-6), ("diffmax.gr3", 1e-2),
                      ("windrot_geo2proj.gr3", 0.0)):
        escribir_gr3(RUN / nombre, x, y, np.full(n, v), tri, cabecera=nombre)
    # sin advección de momento a <250 m del borde abierto (la ELM daba ~6 m/s espurios en el borde)
    escribir_gr3(RUN / "adv.gr3", x, y, (d_borde >= 250).astype(float), tri, cabecera="adv: 0 junto al borde")
    mar = (y > Y_CANAL[1] + DX).astype(float)          # fuente de "agua nueva": el mar
    escribir_gr3(RUN / "AGE_hvar_1.ic", x, y, mar, tri, cabecera="AGE 1: 1 en el mar")
    escribir_gr3(RUN / "AGE_hvar_2.ic", x, y, np.zeros(n), tri, cabecera="AGE 2")
    (RUN / "tvd.prop").write_text("".join(f"{k+1} 1\n" for k in range(ne)))

    nv = 11
    (RUN / "vgrid.in").write_text(
        f"2 !ivcor\n{nv} 1 100. !nvrt, kz, h_s\nZ levels\n1 -100.\nS levels\n5. 0. 1.e-4 !h_c, theta_b, theta_f\n"
        + "".join(f"{k+1} {-1 + k / (nv - 1):.4f}\n" for k in range(nv)))
    (RUN / "ts.ic").write_text("2\n1 -100. 28. 36.\n2 0. 28. 36.\n")
    (RUN / "bctides.in").write_text(
        f"{INICIO} marea M2 idealizada\n0 40. !ntip, tip_dp\n1 !nbfr\nM2\n1.405189e-04 1.0 0.0\n"
        f"1 !nope\n{len(abierto)} 3 0 0 0 0 !nodos, elev=armonica, vel, T, S, AGE\nM2\n"
        + "".join(f"{M2_AMP} 0.\n" for _ in abierto))

    if ISHAPIRO == 2:
        escribir_gr3(RUN / "shapiro.gr3", x, y, np.full(n, 500.0), tri, cabecera="shapiro (tanh) 500")
    # sflux: los meses ERA5 que cubren la simulacion
    s = RUN / "sflux"; s.mkdir(exist_ok=True)
    for p in s.glob("*.nc"):
        p.unlink()
    y0, m0, _ = INICIO
    nmes = int(np.ceil(RNDAY / 28)) + 1
    for k in range(nmes):
        yy, mm = y0 + (m0 - 1 + k) // 12, (m0 - 1 + k) % 12 + 1
        for tipo in ("air", "rad", "prc"):
            fuente = SFLUX / f"sflux_{tipo}_{yy}{mm:02d}.nc"
            assert fuente.exists(), f"falta {fuente}: ejecuta antes scripts/era5_a_sflux.py"
            (s / f"sflux_{tipo}_1.{k+1}.nc").symlink_to(os.path.relpath(fuente, s))
    (s / "sflux_inputs.txt").write_text(
        "&sflux_inputs\nair_1_max_window_hours=745.,\nrad_1_max_window_hours=745.,\nprc_1_max_window_hours=745.,\n/\n")

    # param.nml: plantilla de SCHISM con los cambios de este caso
    p = (SCHISM / "sample_inputs" / "param.nml").read_text()
    nspool = int(3600 / DT)
    cambios = {"CORE": dict(ipre=0, ibc=1, ibtp=1, rnday=RNDAY, dt=DT, ntracer_age=2,
                            nspool=nspool, ihfskip=int(86400 / DT)),
               "OPT": dict(start_year=INICIO[0], start_month=INICIO[1], start_day=INICIO[2],
                           start_hour=0, utc_start=0, ics=1, ihot=0, ncor=NCOR, coricoef=0, slam0=LON0, sfea0=LAT0,
                           nchi=0, ic_elev=0, nadv=0, nws=NWS, wtiminc=DT, ishapiro=ISHAPIRO, drampwind=1, iwindoff=0,
                           ihconsv=0, itur=3, itr_met=3, level_age=-999,
                           **{"flag_ic(1)": 2, "flag_ic(2)": 2}),
               "SCHOUT": {"nhot": 0, "iout_sta": 0, "iof_hydro(1)": 1, "iof_hydro(14)": 1,
                          "iof_hydro(16)": 1, "iof_hydro(25)": 0, "iof_hydro(26)": 0,
                          "iof_age(1)": 1}}   # AGE_1 = edad en dias (SCHISM ya divide los dos trazadores)
    for sec, kv in cambios.items():
        a = p.index(f"&{sec}"); b = p.index("\n/", a)
        bloque = p[a:b]
        for k, v in kv.items():
            patron = re.compile(rf"^(\s*){re.escape(k)}\s*=.*$", re.M)
            if len(patron.findall(bloque)) == 1:
                bloque = patron.sub(lambda mt: f"{mt.group(1)}{k} = {v}", bloque)
            else:
                bloque += f"\n  {k} = {v}"
        p = p[:a] + bloque + p[b:]
    (RUN / "param.nml").write_text(p)

    # scribes = salidas 3D (AGE_1) + 1
    (RUN / "correr.sh").write_text(f"""#!/usr/bin/env bash
# Ejecuta la prueba y guarda el tiempo. Uso: bash {RUN.relative_to(RAIZ)}/correr.sh
set -eo pipefail
cd "$(dirname "$0")"
source "$HOME/miniforge3/etc/profile.d/conda.sh"; conda activate bahia
# En el Mac, MPICH de conda es ~30x mas lento con varios procesos de calculo (latencia):
# 1 de calculo + 2 scribes. Se puede cambiar: NP=5 bash correr.sh
NP=${{NP:-3}}
NS=2
echo "nucleos: $NP (calculo $((NP-NS)) + $NS scribes); {RNDAY:g} dias, dt={DT:g} s, {n} nodos, {ne} elementos"
START=$(date +%s)
mpirun -np $NP {BIN} $NS > outputs/pantalla.log 2>&1 || true
# exito = SCHISM llego al final (MPI_Finalize a veces falla si el Mac cambia de red; es inocuo)
grep -q "Run completed successfully" outputs/mirror.out || {{ echo "!! SCHISM fallo: mira outputs/pantalla.log y outputs/fatal.error"; exit 1; }}
T=$(( $(date +%s) - START ))
PASOS={int(round(RNDAY * 86400 / DT))}
echo "tiempo: $T s para $PASOS pasos -> $(echo "scale=3; $T/$PASOS" | bc) s/paso, $(echo "scale=1; $T*86400/{RNDAY*86400:g}/60" | bc) min por dia simulado" | tee outputs/tiempo.txt
""")
    xt, yt = x[tri], y[tri]
    at = 0.5 * abs((xt[:, 1] - xt[:, 0]) * (yt[:, 2] - yt[:, 0]) - (xt[:, 2] - xt[:, 0]) * (yt[:, 1] - yt[:, 0]))
    area = lambda cond: at[cond(yt.mean(axis=1))].sum()
    print(f"malla: {n} nodos, {ne} elementos, dx={DX:g} m; bahia {area(lambda yy: yy < 0)/1e6:.2f} km2; "
          f"borde abierto {len(abierto)} nodos, tierra {len(tierra)}; {RNDAY:g} dias, {nmes} meses de sflux")
    print(f"listo en {RUN}")


if __name__ == "__main__":
    main()
