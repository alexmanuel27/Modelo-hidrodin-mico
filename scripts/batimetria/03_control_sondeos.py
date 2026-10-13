"""Figura de control: dibuja los sondeos leidos (rojo) sobre la carta para revisar lecturas.
Uso: python3 03_control_sondeos.py <carta> <csv_pix> <salida.jpg> x0 y0 x1 y1"""
import sys, csv
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
carta, f, out, x0, y0, x1, y1 = *sys.argv[1:4], *map(int, sys.argv[4:8])
im = Image.open(carta).convert('RGB').crop((x0, y0, x1, y1)); d = ImageDraw.Draw(im)
for r in csv.DictReader(open(f)):
    x, y = int(r['x']) - x0, int(r['y']) - y0
    if 0 <= x < im.width and 0 <= y < im.height:
        c = (0, 0, 255) if r['dudoso'] == '1' else (255, 0, 0)
        d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=c, width=3)
        d.text((x + 10, y - 20), r['brazas'], fill=c)
im.thumbnail((2400, 2400)); im.save(out, quality=88)
