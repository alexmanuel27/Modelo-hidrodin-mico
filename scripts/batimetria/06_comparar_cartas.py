"""Compara los sondeos de dos cartas (lon/lat): figura de control superpuesta y diferencias
entre sondeos vecinos (< D m), por zona de profundidad.
Uso: python3 06_comparar_cartas.py <carta_1889.tif> <s1889.csv> <s1898.csv> <fig.png>"""
import sys, csv, math
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
D = 25.0  # m: vecinos considerados "el mismo punto"

def leer(f):
    return [dict(lon=float(r['lon']), lat=float(r['lat']), z=float(r['prof_m']), d=r['dudoso'])
            for r in csv.DictReader(open(f)) if r['dudoso'] != '2']

def pares(a, b):
    k = 111320 * math.cos(math.radians(23.13))
    out = []
    for p in a:
        q = min(b, key=lambda q: ((q['lon'] - p['lon']) * k) ** 2 + ((q['lat'] - p['lat']) * 110570) ** 2)
        dist = math.hypot((q['lon'] - p['lon']) * k, (q['lat'] - p['lat']) * 110570)
        if dist < D:
            out.append((p, q, dist))
    return out

if __name__ == '__main__':
    tif, f1, f2, fig = sys.argv[1:5]
    a, b = leer(f1), leer(f2)
    pp = pares(a, b)
    print(f'1879: {len(a)} sondeos; 1887: {len(b)}; pares a < {D:.0f} m: {len(pp)}')
    for lo, hi in [(0, 2), (2, 5), (5, 10), (10, 25)]:
        dz = sorted(q['z'] - p['z'] for p, q, _ in pp if lo <= p['z'] < hi)
        if dz:
            n = len(dz); igual = sum(abs(x) < 0.01 for x in dz)
            print(f'  {lo:>2}-{hi:<2} m: n={n:4d}  mediana(1887-1879)={dz[n // 2]:+.2f} m  '
                  f'p10..p90={dz[n // 10]:+.2f}..{dz[9 * n // 10]:+.2f}  identicos={igual / n:.0%}')
    im = Image.open(tif).convert('L'); W, H = im.size
    im = im.crop((2500, 500, 11000, 7400)); im.thumbnail((2000, 2000))
    from PIL import TiffImagePlugin  # georreferencia para la extension
    t = Image.open(tif).tag_v2; sx = t[33550][0]; lon0, lat0 = t[33922][3], t[33922][4]
    ext = (lon0 + 2500 * sx, lon0 + 11000 * sx, lat0 - 7400 * sx, lat0 - 500 * sx)
    f, ax = plt.subplots(figsize=(15, 12)); ax.imshow(im, cmap='gray', extent=ext, alpha=0.5, aspect=1 / math.cos(math.radians(23.13)))
    ax.scatter([p['lon'] for p in a], [p['lat'] for p in a], s=10, c='tab:blue', label='1879 (ed. 1889)')
    ax.scatter([p['lon'] for p in b], [p['lat'] for p in b], s=10, c='tab:red', marker='x', label='1887 (ed. 1898)')
    ax.legend(); ax.set_title('Sondeos digitalizados de las dos ediciones de la carta H.O. 307')
    f.tight_layout(); f.savefig(fig, dpi=110)
