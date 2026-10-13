"""Registra la carta de 1898 (JPEG IIIF, sin georreferencia) sobre la de 1889 (GeoTIFF Harvard).
Son la misma plancha H.O. 307: se emparejan puntos SIFT, se filtran con RANSAC (afin) y se ajusta
un polinomio de 2.o grado px1898 -> px1889. Requiere opencv-python y numpy.
Uso: python3 05_registro_1898.py <1889_gris_reducida_3x.png> <1898_gris.png> <salida.json>"""
import sys, json, cv2, numpy as np

def terminos(p):
    x, y = p[:, 0] / 1e3, p[:, 1] / 1e3
    return np.c_[np.ones_like(x), x, y, x * x, x * y, y * y]

def aplicar(coef, p):  # p: (n,2) px1898 -> (n,2) px1889
    return terminos(np.asarray(p, float)) @ np.asarray(coef)

if __name__ == '__main__':
    fa, fb, sal = sys.argv[1:4]
    a = cv2.imread(fa, 0)                                  # 1889 reducida a 1/3
    b = cv2.resize(cv2.imread(fb, 0), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(nfeatures=15000)               # shortcut: 15000 puntos por memoria (8 GB)
    ka, da = sift.detectAndCompute(a, None); kb, db = sift.detectAndCompute(b, None)
    g = [m for m, n in cv2.BFMatcher().knnMatch(db, da, k=2) if m.distance < 0.75 * n.distance]
    pb = np.float32([kb[m.queryIdx].pt for m in g]) * 2   # px de la 1898 completa
    pa = np.float32([ka[m.trainIdx].pt for m in g]) * 3   # px de la 1889 completa
    _, inl = cv2.estimateAffine2D(pb, pa, ransacReprojThreshold=15, maxIters=20000, confidence=0.999)
    inl = inl.ravel().astype(bool); pb, pa = pb[inl], pa[inl]
    coef = np.linalg.lstsq(terminos(pb), pa, rcond=None)[0]
    r = np.hypot(*(pa - aplicar(coef, pb)).T)
    res = dict(modelo='polinomio 2.o grado (1, x, y, x2, xy, y2) con x,y = px1898/1000 -> px1889',
               coef=coef.tolist(), n_pares=int(inl.sum()), residuo_px1889_mediana=float(np.median(r)),
               residuo_px1889_p90=float(np.percentile(r, 90)), residuo_px1889_max=float(r.max()),
               nota='1 px de la 1889 ~ 0,65 m')
    assert res['residuo_px1889_p90'] < 10, res
    json.dump(res, open(sal, 'w'), indent=1); print({k: v for k, v in res.items() if k != 'coef'})
