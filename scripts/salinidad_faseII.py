#!/usr/bin/env python3
"""Fase II de docs/protocolo_salinidad_superficie.md: lee F1-F6 y la conclusion sobre H6 con las reglas congeladas el 18-nov (commit 01d5766)
y la aclaracion A3 del registro (escrita antes de ejecutar este script). Entradas: runs/salinidad/m000N/{resumen.json,resumen.npz,jica_estaciones.npz}.
  python scripts/salinidad_faseII.py            -> resultados/salinidad_superficie_faseII.txt
  python scripts/salinidad_faseII.py --prueba"""
import csv, json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from salinidad_superficie import celdas, s11_dir, lectura, S_OBS                    # noqa: E402  (lectura: >= 0,5 explica, >= 0,25 parcial)
from jica_caudales_extra import lectura as lectura_R                                # noqa: E402  (CAMBIA >= 0,25, NO CAMBIA < 0,10)
from jica_compara_modelo import observado, rango_b, veredicto, analiza_miembro      # noqa: E402

SAL = RAIZ / "runs" / "salinidad"; NOM = {0: "control (fondo)", 1: "rios en la capa superior", 2: "rios en toda la columna", 3: "capa superior, caudal x1,7005"}
TOL_S11, TOL_EDAD, TOL_Z = 0.05, 0.05, 0.01
OBS_C = {"sup": 15.9, "m5": 16.3, "m10": 17.1}                                      # tabla 4.20, estacion 1, diciembre, cm/s


def edad(d): return float(json.loads((Path(d) / "resumen.json").read_text())["edad_media_d_bahia"])


def veredicto_c(r):
    """(c): confirma si 0,5 <= r_n <= 2 en todos los niveles; contradice si algun r_n < 0,25 o > 4; parcial en el resto (el sentido no aplica)."""
    r = [x for x in r if not np.isnan(x)]
    if not r: return "no evaluable"
    if any(x < 0.25 or x > 4 for x in r): return "CONTRADICE"
    return "CONFIRMA" if all(0.5 <= x <= 2 for x in r) else "PARCIAL"


def conclusion_h6(casos):
    """casos = [(cierre S11, veredicto (b))] de m0001 y m0002. explica: algun cierre >= 0,5 y su (b) != CONTRADICE; parcial: algun cierre en [0,25; 0,5); no explica: el resto."""
    if any(c >= 0.5 and v != "CONTRADICE" for c, v in casos): return "explica"
    return "parcial" if any(0.25 <= c < 0.5 for c, _ in casos) else "no explica"


def prueba():
    assert [veredicto_c(x) for x in ([1, 1, 1], [0.4, 1, 1], [0.2, 1, 1], [5, 1, 1], [np.nan] * 3)] == ["CONFIRMA", "PARCIAL", "CONTRADICE", "CONTRADICE", "no evaluable"]
    assert [conclusion_h6(c) for c in ([(0.6, "PARCIAL"), (0.1, "CONTRADICE")], [(0.6, "CONTRADICE"), (0.1, "CONTRADICE")], [(0.3, "CONTRADICE")], [(0.1, "CONFIRMA")])] == ["explica", "no explica", "parcial", "no explica"]
    cel = celdas(); d = RAIZ / "runs" / "robustez" / "m0000"
    if d.exists(): assert abs(s11_dir(d, cel) - s11_dir(d, cel)) == 0 and edad(d) > 0
    print("autoprueba salinidad_faseII: ok")


def main():
    L = []; cel = celdas(); o = observado(); d_b, (lo, hi) = rango_b(o)
    P = list(csv.DictReader(open(RAIZ / "resultados" / "jica_sal_superficie_704.csv")))
    y = np.array([(float(f["S_creciente_nodo"]) + float(f["S_bajamar_nodo"])) / 2 for f in P]); y = y[~np.isnan(y)]; hueco = float(np.median(y)) - S_OBS
    ed704 = []
    for p in sorted((RAIZ / "runs" / "conjunto").glob("m[0-9]*")):
        if (p / "resumen.json").exists() and json.loads((p / "resumen.json").read_text()).get("nan", 1) == 0: ed704.append(edad(p))
    ancho = float(np.percentile(ed704, 95) - np.percentile(ed704, 5))
    L += [f"Fase II (runs/salinidad). Hueco de S11 = mediana(704) - {S_OBS:.2f} = {hueco:+.3f} (n {len(y)}); P5-P95 de la edad media de la bahia de {len(ed704)} miembros validos = {ancho:.3f} d"]
    ctl = SAL / "m0000"; s0, e0 = s11_dir(ctl, cel), edad(ctl)
    # F1
    rb = RAIZ / "runs" / "robustez" / "m0000"; sr, er = s11_dir(rb, cel), edad(rb)
    L += [f"F1 reproducibilidad: m0000 S11 {s0:.3f} frente a robustez/m0000 {sr:.3f} (dif {s0 - sr:+.3f}, tol {TOL_S11}); edad media de la bahia {e0:.3f} frente a {er:.3f} d (dif {e0 - er:+.3f}, tol {TOL_EDAD}) -> "
          + ("CUMPLE" if abs(s0 - sr) <= TOL_S11 and abs(e0 - er) <= TOL_EDAD else "NO CUMPLE (informar antes de seguir)")]
    # F2
    dz = [float(np.load(SAL / f"m000{n}" / "jica_estaciones.npz")["dz_max"]) for n in range(4) if (SAL / f"m000{n}" / "jica_estaciones.npz").exists() and "dz_max" in np.load(SAL / f"m000{n}" / "jica_estaciones.npz").files]
    L += ["F2 cotas: " + (f"max |zCoordinates - zcor| = {max(dz):.4f} m (tol {TOL_Z}) -> " + ("CUMPLE" if max(dz) <= TOL_Z else "NO CUMPLE: (b) se rehace con las cotas reales") if dz else "NO EVALUABLE (el .npz no trae dz_max: extraido con una version antigua del extractor; hay que reextraer con scripts/jica_extrae_estaciones.py de bf5c608)")]
    # F3-F5 por variante
    L += ["F3 (cierre de S11 = (S11 control - S11 variante) / hueco), F4 ((b), media de las dos fases, nodo y 300 m, reglas A1) y F5 (R = (edad variante - control) / P5-P95 de los 704):"]
    casos = []
    for n in range(4):
        d = SAL / f"m000{n}"
        if not (d / "resumen.npz").exists(): L += [f"  m000{n} {NOM[n]}: pendiente (sin resumen.npz)"]; continue
        s, e = s11_dir(d, cel), edad(d); c = (s0 - s) / hueco; R = (e - e0) / ancho
        txt = f"  m000{n} {NOM[n]}: S11 {s:.3f}; F3 cierre {c:+.3f} -> {lectura(c)}; edad media {e:.3f} d, F5 R = {R:+.3f} -> {lectura_R(R)}"
        vb = "sin dato"
        if (d / "jica_estaciones.npz").exists():
            r = analiza_miembro(np.load(d / "jica_estaciones.npz")); vn, vr = (veredicto(r["b_" + v]["media"], lo, hi) for v in ("n", "r")); vb = vn if vn == vr else f"PARCIAL (nodo: {vn}, 300 m: {vr})"
            txt += f"; F4 dS_b media nodo {r['b_n']['media']:+.2f} (cr {r['b_n']['creciente']:+.2f}, ba {r['b_n']['bajamar']:+.2f}), 300 m {r['b_r']['media']:+.2f} -> (b) {vb} [rango observado {lo:.1f}-{hi:.1f}]"
        L += [txt]
        if n in (1, 2): casos.append((c, vb.split(" ")[0] if vb != "sin dato" else "sin dato"))
    if len(casos) == 2:
        L += [f"CONCLUSION H6 (m0001, m0002): {conclusion_h6(casos).upper()}" + ("  [nota: un cierre >= 0,5 con (b) CONTRADICE no cuenta como «explica» por la regla congelada]" if any(c >= 0.5 and v == "CONTRADICE" for c, v in casos) else "")]
    # F6
    L += ["F6 (a) y (c), reglas de docs/protocolo_jica_observaciones.md sin cambios; aclaracion A3: el promedio «sobre 2 ciclos de M2» se estima con la ventana completa (dias 91-120, ~56 ciclos) porque las salidas son cada 4 h:"]
    for n in range(3):
        p = SAL / f"m000{n}" / "jica_estaciones.npz"
        if not p.exists(): continue
        z = np.load(p); ni = list(z["niveles"]); V = z["V_n"][:, 0, :]; prof = float(z["prof_nodo_m"][0]); t = z["t"]
        U = {k: float(np.nanmean(V[:, ni.index(k)])) * 100 for k in ("sup", "m5", "m10")}          # modulo medio, cm/s
        r = [U[k] / OBS_C[k] if not (k == "m10" and prof < 10) else np.nan for k in ("sup", "m5", "m10")]
        bl = [np.nanmean(V[(t >= t[0] + i * 24.84 / 24) & (t < t[0] + (i + 1) * 24.84 / 24), ni.index("sup")]) * 100 for i in range(int((t[-1] - t[0]) / (24.84 / 24)))]
        un = np.nanmean(z["canal_un"], 0) * 100
        L += [f"  m000{n} (c) estacion 1 (prof {prof:.1f} m): modulo sup {U['sup']:.1f}, 5 m {U['m5']:.1f}, 10 m {U['m10']:.1f} cm/s frente a {OBS_C['sup']}, {OBS_C['m5']}, {OBS_C['m10']}; r_n = " + ", ".join(f"{x:.2f}" for x in r)
              + f" -> {veredicto_c(r)} (sensibilidad: superficie en bloques de 24,84 h, P5-P95 {np.nanpercentile(bl, 5):.1f}-{np.nanpercentile(bl, 95):.1f} cm/s)",
              f"         (a) cualitativo, sin veredicto: velocidad media a lo largo del canal (> 0 hacia dentro) {dict(zip(map(str, ni), map(float, np.round(un, 1))))} cm/s -> superficie {'hacia dentro' if un[0] > 0 else 'hacia fuera'}, fondo {'hacia dentro' if un[-1] > 0 else 'hacia fuera'}"]
    t = "\n".join(L); print(t); (RAIZ / "resultados" / "salinidad_superficie_faseII.txt").write_text(t + "\n")


if __name__ == "__main__":
    prueba() if "--prueba" in sys.argv else main()
