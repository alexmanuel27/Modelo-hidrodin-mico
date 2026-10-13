"""Corta una carta en teselas con cuadricula de pixeles (para leer sondeos a mano).
Uso: python3 02_teselas.py <carta> <prefijo> x0 y0 x1 y1 [lado=1500]
Las etiquetas de la cuadricula son coordenadas de pixel absolutas de la carta original."""
import sys, os
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
carta, pref, x0, y0, x1, y1 = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7])
L = int(sys.argv[7]) if len(sys.argv) > 7 else 1500
im = Image.open(carta).convert('RGB')
os.makedirs('datos/batimetria/teselas', exist_ok=True)
for ty in range(y0, y1, L - 100):  # 100 px de solape: ningun sondeo queda cortado en las dos
    for tx in range(x0, x1, L - 100):
        t = im.crop((tx, ty, tx + L, ty + L)); d = ImageDraw.Draw(t)
        for k in range(0, L + 1, 100):
            c = (255, 0, 0) if (tx + k) % 500 == 0 else (255, 150, 150)
            d.line([(k, 0), (k, L)], fill=c, width=1); d.text((k + 2, 2), str(tx + k), fill=(200, 0, 0))
            c = (255, 0, 0) if (ty + k) % 500 == 0 else (255, 150, 150)
            d.line([(0, k), (L, k)], fill=c, width=1); d.text((2, k + 2), str(ty + k), fill=(200, 0, 0))
        t.save(f'datos/batimetria/teselas/{pref}_x{tx}_y{ty}.jpg', quality=88)
