"""WGS84 -> UTM (serie de Krueger, error < 1 mm en la zona). Sin dependencias (numpy opcional)."""
import math
A_, F_ = 6378137.0, 1 / 298.257223563
_n = F_ / (2 - F_)
_A = A_ / (1 + _n) * (1 + _n ** 2 / 4 + _n ** 4 / 64)
_al = (_n / 2 - 2 * _n ** 2 / 3 + 5 * _n ** 3 / 16, 13 * _n ** 2 / 48 - 3 * _n ** 3 / 5, 61 * _n ** 3 / 240)
_c = 2 * math.sqrt(_n) / (1 + _n)

def utm(lon, lat, zona=17):
    """lon, lat en grados (escalares o arrays numpy) -> (E, N) en metros, hemisferio norte."""
    import numpy as np
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    l = np.radians(lon - (zona * 6 - 183)); s = np.sin(np.radians(lat))
    t = np.sinh(np.arctanh(s) - _c * np.arctanh(_c * s))
    xi = np.arctan2(t, np.cos(l)); eta = np.arctanh(np.sin(l) / np.sqrt(1 + t * t))
    E = eta + sum(a * np.cos(2 * j * xi) * np.sinh(2 * j * eta) for j, a in enumerate(_al, 1))
    N = xi + sum(a * np.sin(2 * j * xi) * np.cosh(2 * j * eta) for j, a in enumerate(_al, 1))
    return 500000 + 0.9996 * _A * E, 0.9996 * _A * N

_be = (_n / 2 - 2 * _n ** 2 / 3 + 37 * _n ** 3 / 96, _n ** 2 / 48 + _n ** 3 / 15, 17 * _n ** 3 / 480)
_de = (2 * _n - 2 * _n ** 2 / 3 - 2 * _n ** 3, 7 * _n ** 2 / 3 - 8 * _n ** 3 / 5, 56 * _n ** 3 / 15)

def utm_inv(E, N, zona=17):
    """(E, N) UTM hemisferio norte -> (lon, lat) en grados (serie de Krueger inversa)."""
    import numpy as np
    xi = np.asarray(N, float) / (0.9996 * _A); eta = (np.asarray(E, float) - 500000) / (0.9996 * _A)
    xp = xi - sum(b * np.sin(2 * j * xi) * np.cosh(2 * j * eta) for j, b in enumerate(_be, 1))
    ep = eta - sum(b * np.cos(2 * j * xi) * np.sinh(2 * j * eta) for j, b in enumerate(_be, 1))
    chi = np.arcsin(np.sin(xp) / np.cosh(ep))
    lat = chi + sum(d * np.sin(2 * j * chi) for j, d in enumerate(_de, 1))
    lon = np.degrees(np.arctan2(np.sinh(ep), np.cos(xp))) + (zona * 6 - 183)
    return lon, np.degrees(lat)

if __name__ == '__main__':
    e, n = utm(-81, 45)                       # meridiano central: arco de meridiano a 45 grados = 4984944.378 m
    assert abs(e - 500000) < 1e-6 and abs(n - 0.9996 * 4984944.378) < 0.01, (e, n)
    e, n = utm(-82.340, 23.135)               # centro de la bahia: dentro de la rejilla Sentinel-2 del articulo
    assert 361139 < e < 365896 and 2556342 < n < 2561392, (e, n)
    e, n = utm([-82.36, -82.35], [23.13, 23.13])  # 0,01 grados de longitud a 23,13 N ~ 1023 m x factor de escala
    assert abs((e[1] - e[0]) - 1023.9 * 0.99977) < 3, e[1] - e[0]
    lo, la = utm_inv(*utm(-82.3572, 23.1503))  # ida y vuelta
    assert abs(lo + 82.3572) < 1e-7 and abs(la - 23.1503) < 1e-7, (lo, la)
    print('utm ok')
