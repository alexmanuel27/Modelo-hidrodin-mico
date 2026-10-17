"""Zonas de la bahia para las salidas del conjunto (UTM 17N, m). Etiquetas: 0 fuera, 1 canal, 2 cuenca principal,
3 Marimelena (lobulo E), 4 Guasabacoa (brazo S), 5 Atares (brazo SO). Comprobacion visual: docs/figuras/zonas.png."""
import numpy as np

NOMBRES = {1: "canal", 2: "cuenca", 3: "Marimelena", 4: "Guasabacoa", 5: "Atares"}
CENTRO, RUMBO, MEDIO_LARGO, MEDIO_ANCHO = (361646.0, 2560188.0), 124.0, 1100.0, 250.0   # canal de los practicos, ensanchado a la costa


def zonas(x, y, en_bahia):
    t = np.radians(RUMBO); dx, dy = x - CENTRO[0], y - CENTRO[1]
    s, n = dx * np.sin(t) + dy * np.cos(t), dx * np.cos(t) - dy * np.sin(t)
    z = np.where(en_bahia, 2, 0)
    sur = (y < 2558800) & (x < 363300)
    z[en_bahia & sur & (x < 362350 - 0.25 * (2558800 - y))] = 5
    z[en_bahia & sur & (x >= 362350 - 0.25 * (2558800 - y))] = 4
    z[en_bahia & (x > 363600)] = 3            # todo el lobulo E, tambien su orilla sur (corregido con Alex, 17-oct)
    z[en_bahia & (((np.abs(s) <= MEDIO_LARGO) & (np.abs(n) <= MEDIO_ANCHO)) | (y > 2560400))] = 1   # y la punta de la boca
    return z
