"""Sondeos leidos en pixeles -> lon/lat (WGS84) y metros; quita duplicados de las teselas solapadas.
Uso: python3 04_sondeos_a_coordenadas.py <carta_georref.tif> <entrada_pix.csv> <salida.csv>
dudoso: 0 lectura clara, 1 lectura dudosa, 2 'sin fondo a' (cota minima, no profundidad)."""
import sys, csv, math
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
BRAZA = 1.8288  # m

def georref(tif):
    t = Image.open(tif).tag_v2
    sx, sy, _ = t[33550]; _, _, _, lon0, lat0, _ = t[33922]
    assert t[34737].startswith('WGS 84'), 'se esperaba un GeoTIFF en WGS84 geografico'
    return lambda x, y: (lon0 + (x + 0.5) * sx, lat0 - (y + 0.5) * sy)

def sin_duplicados(filas, r=40):
    fuera, conflictos = [], []
    for f in filas:
        cerca = [g for g in fuera if math.hypot(g['x'] - f['x'], g['y'] - f['y']) < r]
        if not cerca: fuera.append(f); continue
        if all(abs(g['brazas'] - f['brazas']) > 0.01 for g in cerca) and \
           any(math.hypot(g['x'] - f['x'], g['y'] - f['y']) < 20 for g in cerca):
            conflictos.append((f, cerca))
    return fuera, conflictos

if __name__ == '__main__':
    tif, ent, sal = sys.argv[1:4]
    a_lonlat = georref(tif)
    lon, lat = a_lonlat(5750, 1062)  # faro del Morro en la carta de 1889
    assert abs(lat - 23.1503) < 0.001 and abs(lon + 82.3572) < 0.001, (lon, lat)
    filas = [dict(r, x=int(r['x']), y=int(r['y']), brazas=float(r['brazas'])) for r in csv.DictReader(open(ent))]
    filas, conf = sin_duplicados(filas)
    for f, c in conf:
        print('CONFLICTO', f['x'], f['y'], f['brazas'], '<->', [(g['x'], g['y'], g['brazas']) for g in c])
    with open(sal, 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['lon', 'lat', 'brazas', 'prof_m', 'dudoso', 'x_pix', 'y_pix'])
        for f in filas:
            lo, la = a_lonlat(f['x'], f['y'])
            w.writerow([f'{lo:.6f}', f'{la:.6f}', f['brazas'], f'{f["brazas"] * BRAZA:.2f}', f['dudoso'], f['x'], f['y']])
    print(len(filas), 'sondeos unicos ->', sal)
