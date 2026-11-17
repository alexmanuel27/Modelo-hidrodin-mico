#!/usr/bin/env python3
"""Viento climatologico (V3 X2): sflux_air de 2016 con uwind y vwind sustituidos por la media 2016-2025 de cada (mes, hora del dia), componente a componente.
Quita la variabilidad sinoptica (frentes frios) y deja el ciclo estacional y el diurno; presion, temperatura, humedad y radiacion siguen siendo los reales de 2016.
Aviso fijado de antemano: la media vectorial reduce la rapidez media y el viento tambien entra en los flujos turbulentos (calor sensible y latente) del flujo de calor,
asi que el contraste «viento real / climatologico» no separa solo la cantidad de movimiento; el cociente de rapideces se imprime y se guarda.
  python scripts/viento_climatologico.py          (Mac o cluster, con netCDF4) -> datos/forzamiento/sflux_climviento/sflux_air_2016MM.nc y resultados/viento_climatologico.txt
  python scripts/viento_climatologico.py --prueba"""
import shutil, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
SFLUX = RAIZ / "datos" / "forzamiento" / "sflux"; SAL = RAIZ / "datos" / "forzamiento" / "sflux_climviento"
ANIOS = range(2016, 2026)


def media_mes_hora(vals, meses, horas):
    """vals (nt, ...) con meses (1-12) y horas (0-23) por instante -> dict {(mes, hora): media sobre todos los instantes}."""
    return {(m, h): vals[(meses == m) & (horas == h)].mean(0) for m in range(1, 13) for h in range(24) if ((meses == m) & (horas == h)).any()}


def prueba():
    meses = np.repeat([1, 2], 48); horas = np.tile(np.arange(24), 4); v = (horas + 100 * (meses - 1)).astype(float)[:, None, None] * np.ones((1, 2, 2))
    c = media_mes_hora(v, meses, horas); assert c[(2, 5)].shape == (2, 2) and abs(c[(2, 5)][0, 0] - 105) < 1e-9 and abs(c[(1, 23)][1, 1] - 23) < 1e-9 and len(c) == 48
    print("prueba ok")


def main():
    from netCDF4 import Dataset, num2date
    SAL.mkdir(parents=True, exist_ok=True); lineas = []
    info = {}
    for m in range(1, 13):
        U, V, mes, hor = [], [], [], []
        for a in ANIOS:
            with Dataset(SFLUX / f"sflux_air_{a}{m:02d}.nc") as d:
                t = num2date(d["time"][:], d["time"].units, only_use_cftime_datetimes=False, only_use_python_datetimes=True)
                U.append(np.asarray(d["uwind"][:], float)); V.append(np.asarray(d["vwind"][:], float)); hor += [x.hour for x in t]; mes += [x.month for x in t]
        U, V, mes, hor = np.concatenate(U), np.concatenate(V), np.array(mes), np.array(hor)
        cu, cv = media_mes_hora(U, mes, hor), media_mes_hora(V, mes, hor)
        f = SAL / f"sflux_air_2016{m:02d}.nc"; shutil.copyfile(SFLUX / f"sflux_air_2016{m:02d}.nc", f)
        with Dataset(f, "r+") as d:
            t = num2date(d["time"][:], d["time"].units, only_use_cftime_datetimes=False, only_use_python_datetimes=True)
            real = np.hypot(np.asarray(d["uwind"][:], float), np.asarray(d["vwind"][:], float))
            nu = np.stack([cu[(x.month, x.hour)] for x in t]); nv = np.stack([cv[(x.month, x.hour)] for x in t])
            d["uwind"][:] = nu; d["vwind"][:] = nv
            info[m] = (real.mean(), np.hypot(nu, nv).mean())
        lineas.append(f"mes {m:2d}: rapidez media real 2016 {info[m][0]:.2f} m/s, climatologica {info[m][1]:.2f} m/s (cociente {info[m][1] / info[m][0]:.2f})")
    r = np.mean([v[1] for v in info.values()]) / np.mean([v[0] for v in info.values()])
    lineas.append(f"anual: cociente de rapidez media climatologica / real = {r:.2f}" + ("   <-- < 0,6: el contraste mezcla quitar la variabilidad y bajar la rapidez media" if r < 0.6 else ""))
    t = "\n".join(lineas); print(t); (RAIZ / "resultados" / "viento_climatologico.txt").write_text(t + "\n")


if __name__ == "__main__":
    prueba() if sys.argv[1:] == ["--prueba"] else main()
