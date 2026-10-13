"""Batimetria de un miembro del conjunto a partir de una superficie de carta (salida de 07).
Dimensiones de incertidumbre (todas documentadas en docs/00_estado_y_plan.md, sec. 19):
  carta    '1879' | '1887'            superficie base
  alfa     0..1                       estado de dragado: 0 = carta historica; 1 = zona navegable a D_NAV
                                      y canal de entrada a D_CANAL (calados de practicos 2018)
  sigma, L m                          campo aleatorio exponencial (estimado del variograma 1887-1879)
  datum    m                          desplazamiento del nivel de la carta (bajamar -> nivel medio)
  semilla                             semilla del campo aleatorio
Uso: python3 08_batimetria_conjunto.py <dir_superficies> <salida_dir>   (figura + estadisticas de volumen)"""
import sys, os, json
import numpy as np
from scipy.io import netcdf_file
from scipy import ndimage

D_CANAL, ANCHO_CANAL, LARGO_CANAL, RUMBO_CANAL = 12.8, 220.0, 1530.0, 124.0   # practicos 2018
CENTRO_CANAL = (361646.0, 2560188.0)  # centroide de las celdas > 11 m del canal (carta 1887), ver 08
D_NAV, H_NAV = 11.0, 5.0              # calado de los canales de acceso (9,75-11,58 m); umbral de agua navegable historica
SIGMA, L = 0.9, 150.0                 # m; variograma de la diferencia 1887-1879 (sigma_carta = sqrt(meseta/2))
PROF_MIN = 0.3
DEF = dict(carta='1887', alfa=0.0, sigma=SIGMA, L=L, datum=0.0, semilla=0)

def lee(f, v):
    d = netcdf_file(f, 'r', mmap=False)
    z = d.variables[v][:].astype(float); z[z == -9999] = np.nan
    return d.variables['x'][:].copy(), d.variables['y'][:].copy(), z

def bahia(X, Y, h):
    return np.isfinite(h) & (X > 361000) & (Y < 2560950)

def poligono_canal(X, Y):
    t = np.radians(RUMBO_CANAL); u = np.array([np.sin(t), np.cos(t)]); n = np.array([u[1], -u[0]])
    dx, dy = X - CENTRO_CANAL[0], Y - CENTRO_CANAL[1]
    return (np.abs(dx * u[0] + dy * u[1]) <= LARGO_CANAL / 2) & (np.abs(dx * n[0] + dy * n[1]) <= ANCHO_CANAL / 2)

def campo_aleatorio(shape, dx, sigma, L, semilla):
    """Campo gaussiano de covarianza exponencial (espectral, con relleno para evitar periodicidad)."""
    ny, nx = 2 * shape[0], 2 * shape[1]
    kx = np.fft.fftfreq(nx, dx) * 2 * np.pi; ky = np.fft.fftfreq(ny, dx) * 2 * np.pi
    K2 = kx[None, :] ** 2 + ky[:, None] ** 2
    amp = (1 + K2 * L ** 2) ** -0.75          # sqrt de S(k) ~ (1 + k^2 L^2)^(-3/2) en 2D
    w = np.random.default_rng(semilla).standard_normal((ny, nx))
    f = np.real(np.fft.ifft2(np.fft.fft2(w) * amp))[:shape[0], :shape[1]]
    return sigma * f / f.std()

def miembro(dir_sup, **p):
    p = {**DEF, **p}
    x, y, h = lee(f"{dir_sup}/batimetria_{p['carta']}.nc", 'profundidad')
    _, _, w = lee(f"{dir_sup}/batimetria_{p['carta']}.nc", 'peso_carta')
    X, Y = np.meshgrid(x, y); agua = np.isfinite(h); b = bahia(X, Y, h)
    canal = poligono_canal(X, Y) & agua
    lab, _ = ndimage.label(b & (h >= H_NAV) | canal)          # agua navegable conectada al canal
    nav = np.isin(lab, np.unique(lab[canal & (lab > 0)])) & (lab > 0)
    obj = np.where(canal, D_CANAL, np.where(nav, D_NAV, 0.0))
    h = h + p['alfa'] * np.maximum(0, obj - h)
    eps = campo_aleatorio(h.shape, x[1] - x[0], p['sigma'], p['L'], p['semilla']) if p['sigma'] > 0 else 0
    fijo = (p['alfa'] > 0) & canal                              # el calado garantizado no se perturba
    h = h + np.where(fijo, 0, eps * np.nan_to_num(w) * np.clip(np.nan_to_num(h) / 2, 0, 1)) + p['datum']
    return x, y, np.where(agua, np.maximum(h, PROF_MIN), np.nan), dict(nav=nav, canal=canal, bahia=b)

def volumen(X, Y, h, b):
    return np.nansum(h[b]) * (X[0, 1] - X[0, 0]) ** 2 / 1e6

if __name__ == '__main__':
    dsup, sal = sys.argv[1:3]; os.makedirs(sal, exist_ok=True)
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    x, y, h0, m = miembro(dsup, sigma=0); X, Y = np.meshgrid(x, y)
    assert abs(m['canal'].sum() * 400 - LARGO_CANAL * ANCHO_CANAL) / (LARGO_CANAL * ANCHO_CANAL) < 0.15, 'poligono del canal'
    res = {}
    for carta in ('1879', '1887'):
        for alfa in (0.0, 0.5, 1.0):
            v = [volumen(X, Y, miembro(dsup, carta=carta, alfa=alfa, semilla=s)[2], m['bahia']) for s in range(30)]
            v0 = volumen(X, Y, miembro(dsup, carta=carta, alfa=alfa, sigma=0)[2], m['bahia'])
            res[f'{carta}_alfa{alfa}'] = dict(vol_sin_ruido_hm3=round(v0, 1), vol_media_hm3=round(float(np.mean(v)), 1),
                                              vol_p5=round(float(np.percentile(v, 5)), 1), vol_p95=round(float(np.percentile(v, 95)), 1),
                                              prof_media_m=round(v0 * 1e6 / (m['bahia'].sum() * 400), 2))
            print(carta, alfa, res[f'{carta}_alfa{alfa}'])
    json.dump(dict(parametros=dict(D_CANAL=D_CANAL, ANCHO_CANAL=ANCHO_CANAL, RUMBO_CANAL=RUMBO_CANAL, D_NAV=D_NAV, H_NAV=H_NAV,
                                   SIGMA=SIGMA, L=L), volumenes=res, area_bahia_km2=round(m['bahia'].sum() * 400 / 1e6, 2)),
              open(f'{sal}/volumenes_conjunto.json', 'w'), indent=1)
    casos = [('1887, histórica (alfa=0)', dict(sigma=0)), ('1887, dragada (alfa=1)', dict(alfa=1, sigma=0)),
             ('1887, alfa=0.5 + campo aleatorio (semilla 1)', dict(alfa=0.5, semilla=1))]
    fig, ax = plt.subplots(1, 4, figsize=(26, 6.5))
    for a, (t, kw) in zip(ax, casos):
        im = a.imshow(miembro(dsup, **kw)[2], origin='lower', extent=(x[0], x[-1], y[0], y[-1]), cmap='viridis_r', vmin=0, vmax=15)
        a.set_title(t); plt.colorbar(im, ax=a, shrink=0.7)
    e = campo_aleatorio(h0.shape, 20.0, SIGMA, L, 1)
    im = ax[3].imshow(np.where(m['bahia'], e, np.nan), origin='lower', extent=(x[0], x[-1], y[0], y[-1]), cmap='RdBu', vmin=-2.5, vmax=2.5)
    ax[3].set_title(f'campo aleatorio sigma={SIGMA} m, L={L:.0f} m'); plt.colorbar(im, ax=ax[3], shrink=0.7)
    for a in ax:
        a.contour(X, Y, m['canal'].astype(float), [0.5], colors='r', linewidths=0.8)
        a.set_xlim(360500, 365500); a.set_ylim(2556300, 2561300); a.set_aspect('equal')
    fig.tight_layout(); fig.savefig(f'{sal}/batimetria_conjunto.png', dpi=100)
