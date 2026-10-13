"""Malla no estructurada de triangulos para SCHISM (algoritmo DistMesh, Persson y Strang 2004),
solo con numpy/scipy. Dominio: agua de la superficie de batimetria (07) dentro de un circulo
centrado en la boca de la bahia; el arco del circulo en mar abierto es el borde abierto.
Uso: python3 09_malla.py <batimetria.nc> <salida_dir>
Salidas: hgrid.gr3 (UTM 17N, m), hgrid.ll (lon/lat), malla.png, malla_resumen.json"""
import sys, os, json
import numpy as np
from scipy import ndimage
from scipy.spatial import Delaunay
from scipy.interpolate import RegularGridInterpolator
from scipy.io import netcdf_file
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utm import utm_inv

BOCA = np.array([361000.0, 2560900.0])   # m, entrada del canal (Morro - La Punta)
R = 5000.0                               # m, radio del dominio: borde abierto a 3-5 km de la costa, 400-1100 m de fondo
H_CANAL, H_BAHIA, H_MAX, CRECE = 25.0, 40.0, 400.0, 0.15
ANCHO_MIN, ISLA_MIN = 60.0, 20000.0   # m: darsenas mas estrechas se cierran; islotes menores (m2) se quitan   # tamanos (m) y ritmo de crecimiento fuera de la bahia
CENTRO_CANAL, RUMBO, LARGO, ANCHO = (361646.0, 2560188.0), 124.0, 1700.0, 450.0  # zona de refinamiento del canal

def lee(nc):
    d = netcdf_file(nc, 'r', mmap=False)
    z = d.variables['profundidad'][:].astype(float); z[z == -9999] = np.nan
    return d.variables['x'][:].copy(), d.variables['y'][:].copy(), z

def en_canal(p):
    t = np.radians(RUMBO); u = np.array([np.sin(t), np.cos(t)]); n = np.array([u[1], -u[0]])
    d = p - CENTRO_CANAL
    return (np.abs(d @ u) <= LARGO / 2) & (np.abs(d @ n) <= ANCHO / 2)

def en_bahia(p):  # misma definicion que bahia() en 08 (incluye la cabecera de Atares al O de E 361000)
    return ((p[:, 0] > 361000) & (p[:, 1] < 2560950)) | ((p[:, 0] > 360500) & (p[:, 1] < 2559000))

def tamano(p):
    fuera = H_BAHIA + CRECE * np.maximum(0, np.hypot(*(p - BOCA).T) - 300)
    h = np.where(en_bahia(p), H_BAHIA, np.minimum(fuera, H_MAX))
    return np.where(en_canal(p), H_CANAL, h)

def dominio(x, y, z):
    X, Y = np.meshgrid(x, y)
    dom = np.isfinite(z) & (np.hypot(X - BOCA[0], Y - BOCA[1]) < R)
    # simplifica la costa a la escala de la malla: quita darsenas mas estrechas que ~2 elementos
    disco = np.hypot(*np.mgrid[-2:3, -2:3]) <= ANCHO_MIN / 2 / (x[1] - x[0])
    dom = ndimage.binary_opening(dom, structure=disco)
    hue, nh = ndimage.label(~dom)                                      # islotes de < ISLA_MIN m2: agua
    tam = np.bincount(hue.ravel()); peq = np.flatnonzero(tam * (x[1] - x[0]) ** 2 < ISLA_MIN)
    dom |= np.isin(hue, peq[peq > 0]) & (hue != hue[0, 0])
    lab, n = ndimage.label(dom)
    dom = lab == np.argmax(np.bincount(lab.ravel())[1:]) + 1          # solo el cuerpo de agua principal
    dx = x[1] - x[0]
    sdf = (ndimage.distance_transform_edt(~dom) - ndimage.distance_transform_edt(dom)) * dx
    f = RegularGridInterpolator((y, x), sdf, bounds_error=False, fill_value=dx * 50)
    tierra = ndimage.distance_transform_edt(np.isfinite(z)) * dx            # distancia a tierra (no al circulo)
    ft = RegularGridInterpolator((y, x), tierra, bounds_error=False, fill_value=0)
    fz = RegularGridInterpolator((y, x), np.nan_to_num(z, nan=0.3), bounds_error=False, fill_value=0.3)
    return (lambda p: f(p[:, ::-1])), (lambda p: ft(p[:, ::-1])), (lambda p: fz(p[:, ::-1])), dom

def distmesh(fd, fh, caja, h0, niter=600, semilla=1):
    rng = np.random.default_rng(semilla)
    xx, yy = np.meshgrid(np.arange(caja[0], caja[2], h0), np.arange(caja[1], caja[3], h0 * np.sqrt(3) / 2))
    xx[1::2] += h0 / 2
    p = np.c_[xx.ravel(), yy.ravel()]
    p = p[fd(p) < -0.3 * h0]
    p = p[rng.random(len(p)) < (h0 / fh(p)) ** 2]
    geps, deps, ttol, Fscale, dt = 1e-3 * h0, 1e-3 * h0, 0.1, 1.2, 0.2
    pold = np.inf
    for it in range(niter):
        if np.max(np.hypot(*(p - pold).T)) / h0 > ttol:
            pold = p.copy()
            t = Delaunay(p).simplices
            t = t[fd(p[t].mean(1)) < -geps]
            bars = np.unique(np.sort(np.r_[t[:, [0, 1]], t[:, [1, 2]], t[:, [0, 2]]], axis=1), axis=0)
        bv = p[bars[:, 0]] - p[bars[:, 1]]; L = np.hypot(*bv.T)
        hb = fh(p[bars].mean(1))
        L0 = hb * Fscale * np.sqrt(np.sum(L ** 2) / np.sum(hb ** 2))
        F = np.maximum(L0 - L, 0)
        Fv = (F / L)[:, None] * bv
        Ft = np.zeros_like(p)
        np.add.at(Ft, bars[:, 0], Fv); np.add.at(Ft, bars[:, 1], -Fv)
        p = p + dt * Ft
        d = fd(p); fuera = d > 0
        if fuera.any():                                       # proyecta al contorno
            q = p[fuera]
            gx = (fd(q + [deps, 0]) - d[fuera]) / deps; gy = (fd(q + [0, deps]) - d[fuera]) / deps
            p[fuera] = q - (d[fuera] / (gx ** 2 + gy ** 2 + 1e-12))[:, None] * np.c_[gx, gy]
        mov = np.hypot(*(dt * Ft[d < -geps]).T)
        if it % 50 == 0:
            print(f'  iter {it}: {len(p)} nodos, mov. max/h0 = {mov.max() / h0:.3f}', flush=True)
        if mov.max() / h0 < 2e-3:
            break
    t = Delaunay(p).simplices
    t = t[fd(p[t].mean(1)) < -geps]
    usados = np.unique(t); idx = -np.ones(len(p), int); idx[usados] = np.arange(len(usados))
    return p[usados], idx[t]

def calidad(p, t):
    a = p[t]; e = [np.hypot(*(a[:, (i + 1) % 3] - a[:, i]).T) for i in range(3)]
    ang = []
    for i in range(3):
        b, c, o = e[i], e[(i + 2) % 3], e[(i + 1) % 3]
        ang.append(np.degrees(np.arccos(np.clip((b ** 2 + c ** 2 - o ** 2) / (2 * b * c), -1, 1))))
    return np.min(ang, axis=0), np.mean(e, axis=0)

def contornos(t):
    """Lazos de contorno a partir de las aristas dirigidas de triangulos antihorarios
    (el dominio queda a la izquierda: exterior antihorario, islas horarias)."""
    e = np.r_[t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]]
    clave = {tuple(a): k for k, a in enumerate(e)}
    borde = [tuple(a) for a in e if (a[1], a[0]) not in clave]
    sig = {}
    for a, b in borde:
        assert a not in sig, f'nodo {a} con dos aristas de contorno salientes (estrangulamiento)'
        sig[a] = b
    lazos, vistos = [], set()
    for ini in sig:
        if ini in vistos: continue
        lazo, cur = [], ini
        while cur not in vistos:
            vistos.add(cur); lazo.append(cur); cur = sig[cur]
        lazos.append(np.array(lazo))
    return lazos

def quita_estrangulamientos(p, t):
    """Quita triangulos hasta que ningun nodo tenga dos aristas de contorno salientes."""
    while True:
        e = np.r_[t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]]
        clave = set(map(tuple, e))
        sal = [a for a, b in e if (b, a) not in clave]
        u, c = np.unique(sal, return_counts=True)
        malos = u[c > 1]
        if not len(malos): return t
        a = p[t]; area = 0.5 * np.abs((a[:, 1, 0] - a[:, 0, 0]) * (a[:, 2, 1] - a[:, 0, 1]) - (a[:, 2, 0] - a[:, 0, 0]) * (a[:, 1, 1] - a[:, 0, 1]))
        quitar = set()
        for m in malos:
            k = np.flatnonzero((t == m).any(1)); quitar.add(k[np.argmin(area[k])])
        t = np.delete(t, list(quitar), axis=0)

def area_firmada(p):
    return 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])

if __name__ == '__main__':
    nc, sal = sys.argv[1:3]; os.makedirs(sal, exist_ok=True)
    x, y, z = lee(nc)
    fd, ftierra, fz, dom = dominio(x, y, z)
    caja = (BOCA[0] - R, BOCA[1] - R, BOCA[0] + R, BOCA[1] + R)
    p, t = distmesh(fd, tamano, caja, H_CANAL)
    # orientacion antihoraria
    a = p[t]; s = (a[:, 1, 0] - a[:, 0, 0]) * (a[:, 2, 1] - a[:, 0, 1]) - (a[:, 2, 0] - a[:, 0, 0]) * (a[:, 1, 1] - a[:, 0, 1])
    t[s < 0] = t[s < 0][:, [0, 2, 1]]
    for _ in range(5):                                       # astillas pegadas al contorno (casi colineales)
        am, _l = calidad(p, t)
        e = np.r_[t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]]; cl = set(map(tuple, e))
        bord = np.array([any((r[(i + 1) % 3], r[i]) not in cl for i in range(3)) for r in t])
        malas = (am < 5) & bord
        if not malas.any(): break
        t = t[~malas]
    t = quita_estrangulamientos(p, t)
    usados = np.unique(t); idx = -np.ones(len(p), int); idx[usados] = np.arange(len(usados)); p, t = p[usados], idx[t]
    angmin, lado = calidad(p, t)
    lazos = contornos(t)
    ext = max(lazos, key=lambda l: area_firmada(p[l]))
    assert area_firmada(p[ext]) > 0
    islas = [l for l in lazos if l is not ext]
    # borde abierto: nodos del contorno exterior sobre el circulo y lejos de tierra
    abierto = (np.abs(np.hypot(*(p[ext] - BOCA).T) - R) < 0.5 * tamano(p[ext])) & (ftierra(p[ext]) > 300)
    k = np.flatnonzero(abierto)
    assert len(k) > 10, 'no se encontro el borde abierto'
    ext = np.roll(ext, -(k[np.argmax(np.diff(np.r_[k, k[0] + len(ext)]))] + 1))   # el lazo empieza tras el hueco mas largo
    ab = np.isin(np.arange(len(ext)), np.flatnonzero((np.abs(np.hypot(*(p[ext] - BOCA).T) - R) < 0.5 * tamano(p[ext])) & (ftierra(p[ext]) > 300)))
    i0, i1 = np.flatnonzero(ab)[[0, -1]]
    nodos_ab = ext[i0:i1 + 1]
    nodos_tierra = np.r_[ext[i1:], ext[:i0 + 1]]
    prof = np.maximum(fz(p), 0.3)
    lon, lat = utm_inv(p[:, 0], p[:, 1])
    def escribe(ruta, X, Y, val, cab):
        with open(ruta, 'w') as f:
            f.write(f'{cab}\n{len(t)} {len(p)}\n')
            for i, (a, b, v) in enumerate(zip(X, Y, val), 1): f.write(f'{i} {a:.8f} {b:.8f} {v:.3f}\n')
            for i, e in enumerate(t + 1, 1): f.write(f'{i} 3 {e[0]} {e[1]} {e[2]}\n')
            f.write(f'1 = Number of open boundaries\n{len(nodos_ab)} = Total number of open boundary nodes\n')
            f.write(f'{len(nodos_ab)} = Number of nodes for open boundary 1\n' + ''.join(f'{i + 1}\n' for i in nodos_ab))
            f.write(f'{1 + len(islas)} = number of land boundaries\n{len(nodos_tierra) + sum(map(len, islas))} = Total number of land boundary nodes\n')
            f.write(f'{len(nodos_tierra)} 0 = Number of nodes for land boundary 1\n' + ''.join(f'{i + 1}\n' for i in nodos_tierra))
            for j, l in enumerate(islas, 2):
                f.write(f'{len(l)} 1 = Number of nodes for land boundary {j} (isla)\n' + ''.join(f'{i + 1}\n' for i in l))
    escribe(f'{sal}/hgrid.gr3', p[:, 0], p[:, 1], prof, 'Bahia de La Habana, UTM 17N (EPSG:32617), prof. de la carta (09_malla.py)')
    escribe(f'{sal}/hgrid.ll', lon, lat, prof, 'Bahia de La Habana, lon/lat WGS84 (09_malla.py)')
    bah = en_bahia(p)
    res = dict(nodos=int(len(p)), elementos=int(len(t)), nodos_bahia=int(bah.sum()),
               angulo_min_grados=round(float(angmin.min()), 1), angulo_min_p1=round(float(np.percentile(angmin, 1)), 1),
               elementos_angulo_menor_20=int((angmin < 20).sum()),
               lado_canal_m=round(float(np.median(lado[en_canal(p[t].mean(1))])), 1),
               lado_bahia_m=round(float(np.median(lado[en_bahia(p[t].mean(1)) & ~en_canal(p[t].mean(1))])), 1),
               lado_max_m=round(float(lado.max()), 1), nodos_borde_abierto=int(len(nodos_ab)),
               prof_borde_abierto_m=[round(float(prof[nodos_ab].min()), 1), round(float(prof[nodos_ab].max()), 1)],
               islas=len(islas), elementos_a_traves_del_canal=round(300 / float(np.median(lado[en_canal(p[t].mean(1))])), 1))
    json.dump(res, open(f'{sal}/malla_resumen.json', 'w'), indent=1); print(res)
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(20, 9))
    for a_, lim in zip(ax, [None, (360600, 365200, 2556400, 2561200)]):
        a_.triplot(p[:, 0], p[:, 1], t, lw=0.15, color='k')
        a_.plot(*p[nodos_ab].T, 'r-', lw=2, label='borde abierto')
        a_.plot(*p[nodos_tierra].T, 'g-', lw=0.8, label='tierra')
        a_.set_aspect('equal')
        if lim: a_.set_xlim(lim[:2]); a_.set_ylim(lim[2:])
    ax[0].legend(); ax[0].set_title(f"{res['nodos']} nodos, {res['elementos']} elementos"); ax[1].set_title('bahia')
    fig.tight_layout(); fig.savefig(f'{sal}/malla.png', dpi=110)
