"""Superficies de batimetria de la bahia de La Habana a partir de datos publicos.
Une: sondeos de carta (csv de 04), linea de costa actual (OSM, json de Overpass) y GEBCO fuera.
Rejilla UTM 17N (EPSG:32617). Profundidad positiva hacia abajo, en m bajo el nivel de la carta.
Uso: python3 07_superficies.py <osm.json> <gebco.nc> <salida_dir> <sondeos_A.csv> [<sondeos_B.csv> ...]
Requiere numpy, scipy, matplotlib."""
import sys, os, json, csv, math
import numpy as np
from scipy.interpolate import griddata, LinearNDInterpolator
from scipy.spatial import Delaunay
from scipy.spatial import cKDTree
from scipy.io import netcdf_file
from matplotlib.path import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utm import utm

DX = 20.0                                       # m (= rejilla Sentinel-2 del articulo)
X0, X1, Y0, Y1 = 354000, 368000, 2554000, 2566000
PROF_MIN = 0.3                                  # m: agua minima en celdas mojadas
D_CARTA, D_GEBCO = 150.0, 600.0                 # m: peso 1 de la carta hasta D_CARTA de un sondeo, 0 a D_GEBCO
LADO_MAX = 500.0                                # m: triangulos mas largos no se usan (evita puentes costa-mar abierto)

def rejilla():
    x = np.arange(X0 + DX / 2, X1, DX); y = np.arange(Y0 + DX / 2, Y1, DX)
    return x, y, *np.meshgrid(x, y)

def costa(osm):
    """Cadenas de costa OSM (tierra a la izquierda) -> (poligono de mar, lista de islas) en UTM."""
    ways = [w for w in json.load(open(osm))['elements'] if w['type'] == 'way' and w['tags'].get('natural') == 'coastline']
    seg = {w['id']: (w['nodes'], [(g['lon'], g['lat']) for g in w['geometry']]) for w in ways}
    cadenas = []
    while seg:                                  # encadena por nodos compartidos
        _, (nod, geo) = seg.popitem()
        cambio = True
        while cambio:
            cambio = False
            for k, (n2, g2) in list(seg.items()):
                if n2[0] == nod[-1]: nod, geo = nod + n2[1:], geo + g2[1:]
                elif n2[-1] == nod[0]: nod, geo = n2 + nod[1:], g2 + geo[1:]
                else: continue
                del seg[k]; cambio = True
        cadenas.append((nod, geo))
    xy = lambda g: np.c_[utm(*np.array(g).T)]
    islas = [xy(g) for n, g in cadenas if n[0] == n[-1]]
    abiertas = sorted((xy(g) for n, g in cadenas if n[0] != n[-1]), key=len)
    assert abiertas, 'no hay costa abierta que cruce la zona'
    c = abiertas[-1]                            # costa principal; tierra a la izquierda => recorre de E a O
    if c[0, 0] < c[-1, 0]: c = c[::-1]
    norte = Y1 + 50000
    mar = np.r_[c, [[c[-1, 0], norte], [c[0, 0], norte]]]
    return mar, islas, abiertas

def mascara_agua(X, Y, mar, islas):
    p = np.c_[X.ravel(), Y.ravel()]
    m = Path(mar).contains_points(p)
    for i in islas:
        m &= ~Path(i).contains_points(p)
    return m.reshape(X.shape)

def gebco(nc, X, Y):
    f = netcdf_file(nc, 'r', mmap=False)
    lat, lon, z = f.variables['lat'][:].copy(), f.variables['lon'][:].copy(), f.variables['elevation'][:].astype(float)
    # rejilla UTM -> lon/lat por busqueda inversa en la propia rejilla GEBCO (suficiente a 450 m)
    LON, LAT = np.meshgrid(lon, lat); E, N = utm(LON, LAT)
    return -griddata(np.c_[E.ravel(), N.ravel()], z.ravel(), (X, Y), method='linear')

def sondeos(f):
    r = [x for x in csv.DictReader(open(f)) if x['dudoso'] != '2']
    E, N = utm([float(x['lon']) for x in r], [float(x['lat']) for x in r])
    return np.c_[E, N], np.array([float(x['prof_m']) for x in r])

def superficie(p, z, linea_costa, X, Y, agua, zg):
    """Interpola sondeos + costa (prof 0) linealmente y funde con GEBCO lejos de los sondeos."""
    pc = np.vstack([remuestrea(c, 40) for c in linea_costa])
    pts = np.r_[p, pc]; val = np.r_[z, np.zeros(len(pc))]
    tri = Delaunay(pts)
    lado = np.max([np.hypot(*(pts[tri.simplices[:, i]] - pts[tri.simplices[:, (i + 1) % 3]]).T) for i in range(3)], axis=0)
    q = np.c_[X.ravel(), Y.ravel()]; s = tri.find_simplex(q)
    zc = LinearNDInterpolator(tri, val)(q)
    zc[(s < 0) | (lado[s] > LADO_MAX)] = np.nan
    zc = zc.reshape(X.shape)
    d = cKDTree(p).query(np.c_[X.ravel(), Y.ravel()])[0].reshape(X.shape)
    w = np.clip((D_GEBCO - d) / (D_GEBCO - D_CARTA), 0, 1)
    w[np.isnan(zc)] = 0
    zz = np.where(w > 0, w * np.nan_to_num(zc) + (1 - w) * zg, zg)
    zz = np.where(agua, np.maximum(zz, PROF_MIN), np.nan)
    return zz, w

def remuestrea(c, paso):
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
    s = np.arange(0, d[-1], paso)
    return np.c_[np.interp(s, d, c[:, 0]), np.interp(s, d, c[:, 1])]

def escribe(nombre, x, y, campos, attrs):
    f = netcdf_file(nombre, 'w')
    f.createDimension('x', len(x)); f.createDimension('y', len(y))
    for k, v in (('x', x), ('y', y)):
        var = f.createVariable(k, 'd', (k,)); var[:] = v; var.units = 'm'; var.crs = 'EPSG:32617 (WGS84 / UTM 17N)'
    for k, (v, u, desc) in campos.items():
        var = f.createVariable(k, 'f', ('y', 'x')); var[:] = np.nan_to_num(v, nan=-9999.); var._FillValue = np.float32(-9999.)
        var.units = u; var.long_name = desc
    for k, v in attrs.items(): setattr(f, k, v)
    f.close()

if __name__ == '__main__':
    osm, nc, sal, *fs = sys.argv[1:]
    os.makedirs(sal, exist_ok=True)
    x, y, X, Y = rejilla()
    mar, islas, lineas = costa(osm)
    agua = mascara_agua(X, Y, mar, islas)
    zg = gebco(nc, X, Y)
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    res = {}
    for f in fs:
        tag = os.path.basename(f).replace('sondeos_', '').replace('.csv', '')
        p, z = sondeos(f)
        zz, w = superficie(p, z, lineas + islas, X, Y, agua, zg)
        res[tag] = zz
        escribe(f'{sal}/batimetria_{tag}.nc', x, y,
                {'profundidad': (zz, 'm', 'profundidad bajo el nivel de la carta (positiva hacia abajo)'),
                 'peso_carta': (w, '1', 'peso de los sondeos de carta frente a GEBCO')},
                {'fuentes': f'{os.path.basename(f)}; costa OSM; GEBCO 2026', 'script': '07_superficies.py'})
        print(tag, 'celdas de agua', int(agua.sum()), 'prof. max en la bahia (peso>0.99) %.1f m' % np.nanmax(np.where(w > .99, zz, np.nan)))
    tags = list(res)
    nfig = len(tags) + (len(tags) == 2)
    fig, ax = plt.subplots(1, nfig, figsize=(7 * nfig, 6.5), squeeze=False); ax = ax[0]
    ext = (X0, X1, Y0, Y1)
    for a, t in zip(ax, tags):
        im = a.imshow(res[t], origin='lower', extent=ext, cmap='viridis_r', vmin=0, vmax=20)
        a.set_title(f'Profundidad {t} (m)'); plt.colorbar(im, ax=a, shrink=0.7)
    if len(tags) == 2:
        dz = res[tags[1]] - res[tags[0]]
        im = ax[-1].imshow(dz, origin='lower', extent=ext, cmap='RdBu', vmin=-3, vmax=3)
        ax[-1].set_title(f'{tags[1]} - {tags[0]} (m)'); plt.colorbar(im, ax=ax[-1], shrink=0.7)
        escribe(f'{sal}/diferencia_{tags[1]}_{tags[0]}.nc', x, y, {'dz': (dz, 'm', f'{tags[1]} menos {tags[0]}')}, {'script': '07_superficies.py'})
    for a in ax:
        a.set_xlim(358500, 367000); a.set_ylim(2555500, 2563500); a.set_aspect('equal')
    fig.tight_layout(); fig.savefig(f'{sal}/superficies.png', dpi=110)
