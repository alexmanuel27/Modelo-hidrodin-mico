#!/usr/bin/env python3
"""Corridas de octubre y diciembre de 2002 (docs/protocolo_2002.md; lectura fijada y commiteada ANTES de generar las corridas).
Miembro central con ERA5 y OISST de 2002 (1-sep a 31-dic, runs/dos2002): m0000 caudales de la tabla 4.8, m0001 + drenajes S4-S6 en Atares, m0002 + escorrentia de ERA5.
Comparacion con JICA vol. V con las reglas congeladas de la fase II: cierre del hueco de S11 (>= 0,5 explica, >= 0,25 parcial), (b) con las reglas de A1
(rango observado del mes), perfiles por zona frente a la tabla 4.11 (+-1, como la parte I) y conclusion con la regla de H6.
Entradas (del cluster): runs/dos2002/m000N/jica_2002_{oct,oct_s,dic,dic_s}.npz (scripts/jica_extrae_estaciones.py con las ventanas de VENT) y resumen.json.
  python scripts/dos2002.py            -> resultados/dos2002.txt
  python scripts/dos2002.py --prueba"""
import csv, json, sys, warnings
from pathlib import Path
import numpy as np

warnings.filterwarnings("ignore", "Mean of empty slice")
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from salinidad_superficie import lectura, S_OBS, ZONAS                              # noqa: E402  (>= 0,5 explica, >= 0,25 parcial; S_OBS = 31,25)
from jica_compara_modelo import observado, rango_b, veredicto, analiza_miembro, N_MIN_FASE   # noqa: E402
from jica_extrae_estaciones import fases                                            # noqa: E402
from salinidad_faseII import conclusion_h6                                          # noqa: E402
from jica_caudales_extra import lectura as lectura_R                                # noqa: E402

D = RAIZ / "runs" / "dos2002"
# ventanas en dias desde el 1-sep-2002 00 UTC: principal (centrada en la campana) y sensibilidad; ver el protocolo
VENT = {"oct": ("2002-10", (31, 42), (28, 45)), "dic": ("2002-12", (100, 111), (92, 122))}
NOM = {0: "tabla 4.8 (tres rios)", 1: "+ S4-S6 en Atares", 2: "+ S4-S6 + escorrentia ERA5"}
TOL_ZONA, ZONAS_EST, EDAD_REF, ANCHO = 1.0, (1, 2, 4, 5), 6.025, 5.308   # +-1 de la parte I; edad de salinidad/m0001 (capa superior, abr-2016) y P5-P95 de los 704


def s_obs(o, mes): return float(np.mean([o[(mes, f, "superficie")][0] for f in ("creciente", "bajamar")]))


def s_fases(z):
    """Salinidad a 0,5 m, media de las 11 estaciones, por fase (creciente, bajamar) con el ajuste armonico; NaN con < N_MIN_FASE muestras."""
    cr, ba = fases(z["t"], z["eta_bay"]); s = np.nanmean(z["S_n"][:, :, 0], axis=1)
    return [float(np.nanmean(s[m])) if m.sum() >= N_MIN_FASE else np.nan for m in (cr, ba)]


def cierre(s11, med704, sobs): return (med704 - s11) / (med704 - sobs)       # (S11 de referencia - S11 variante) / hueco del mes; dic: hueco = +4,12


def ver_b(z, o, mes):
    """(b) con las reglas de A1 sobre la media de las dos fases; nodo y 300 m deben coincidir (si no, PARCIAL)."""
    lo, hi = rango_b(o, mes)[1]; r = analiza_miembro(z); vn, vr = (veredicto(r["b_" + v]["media"], lo, hi) for v in ("n", "r"))
    return r, (vn if vn == vr else "PARCIAL"), (lo, hi)


def obs_411():
    f = [r for r in csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_vol5.csv")) if r["tabla"] == "4.11" and r["variable"] == "salinidad" and r["mes"] == "2001-11"]
    return {(r["estacion"], r["nivel_m"], r["fase"]): float(r["valor"]) for r in f}


def zonas_est():
    E = list(csv.DictReader(open(RAIZ / "datos" / "observaciones" / "jica2004_estaciones_utm.csv")))
    zona = np.load(RAIZ / "datos" / "conjunto" / "posproceso_malla.npz")["zona"]
    return np.array([int(zona[int(r["nodo"]) - 1]) for r in E])


def perfiles(z, zest, o411):
    """Por zona con estaciones (1, 2, 4, 5) y fase: S a 0,5 m y S(fondo) - S(0,5 m) del modelo frente a la tabla 4.11 (superficie; fondo - superficie). Compatible si |dif| <= 1."""
    cr, ba = fases(z["t"], z["eta_bay"]); out = []
    for zn in ZONAS_EST:
        k = zest == zn
        for fa, m in (("creciente", cr), ("bajamar", ba)):
            if m.sum() < N_MIN_FASE or not k.any(): continue
            S = z["S_n"][m][:, k]; ss = float(np.nanmean(S[:, :, 0])); ds = float(np.nanmean(S[:, :, 4] - S[:, :, 0]))
            os_, of = o411[(ZONAS[zn], "surface", fa)], o411[(ZONAS[zn], "bottom", fa)]
            out.append((ZONAS[zn], fa, ss, os_, abs(ss - os_) <= TOL_ZONA, ds, of - os_, abs(ds - (of - os_)) <= TOL_ZONA))
    return out


def evalua(z, o, mes, med704):
    sf = s_fases(z); s11 = float(np.mean(sf)); c = cierre(s11, med704, s_obs(o, mes)); r, vb, (lo, hi) = ver_b(z, o, mes)
    dentro = [abs(sf[i] - o[(mes, f, "superficie")][0]) <= o[(mes, f, "superficie")][1] for i, f in enumerate(("creciente", "bajamar"))]
    return dict(s11=s11, sf=sf, cierre=c, lect=lectura(c), b=r, vb=vb, rango=(lo, hi), dentro=dentro)


def main():
    o = observado(); o411 = obs_411(); zest = zonas_est(); L = []
    P = list(csv.DictReader(open(RAIZ / "resultados" / "jica_sal_superficie_704.csv")))
    y = np.array([(float(f["S_creciente_nodo"]) + float(f["S_bajamar_nodo"])) / 2 for f in P]); med = float(np.nanmedian(y))
    L += [f"Referencia: mediana de S11 de los 704 = {med:.3f}; S11 observado dic 2002 = {s_obs(o, '2002-12'):.2f} (hueco {med - s_obs(o, '2002-12'):+.3f}), oct 2002 = {s_obs(o, '2002-10'):.2f} (hueco {med - s_obs(o, '2002-10'):+.3f})"]
    concl = {}
    for mes_k, (mes, vp, vs) in VENT.items():
        L += [f"--- {mes} (ventana principal dias {vp[0]}-{vp[1]}, sensibilidad {vs[0]}-{vs[1]} desde el 1-sep-2002; {'DECIDE' if mes_k == 'dic' else 'informativo, misma regla'})"]
        casos = {}
        for n in range(3):
            res = {}
            for etq, nom in (("principal", f"jica_2002_{mes_k}.npz"), ("sensibilidad", f"jica_2002_{mes_k}_s.npz")):
                p = D / f"m000{n}" / nom
                if p.exists(): res[etq] = evalua(np.load(p), o, mes, med)
            if "principal" not in res: L += [f"  m000{n} {NOM[n]}: pendiente ({mes_k})"]; continue
            for etq, e in res.items():
                L += [f"  m000{n} {NOM[n]} [{etq}]: S11 {e['s11']:.2f} (cr {e['sf'][0]:.2f}, ba {e['sf'][1]:.2f}; dentro de obs +-1 sd: cr {e['dentro'][0]}, ba {e['dentro'][1]}); "
                      f"cierre {e['cierre']:+.3f} -> {e['lect']}; (b) dS fondo-sup nodo {e['b']['b_n']['media']:+.2f} (cr {e['b']['b_n']['creciente']:+.2f}, ba {e['b']['b_n']['bajamar']:+.2f}), "
                      f"300 m {e['b']['b_r']['media']:+.2f} -> {e['vb']} [rango obs {e['rango'][0]:.1f}-{e['rango'][1]:.1f}; contradice < {e['rango'][0] / 2:.2f}]"]
            casos[n] = {k: (e["cierre"], e["vb"].split(" ")[0]) for k, e in res.items()}
            if mes_k == "dic":
                L += [f"    perfiles frente a la tabla 4.11 (nov 2001, +-{TOL_ZONA:g}), ventana principal:"]
                pz = perfiles(np.load(D / f"m000{n}" / f"jica_2002_{mes_k}.npz"), zest, o411)
                for zn, fa, ss, os_, ok1, ds, od, ok2 in pz: L += [f"      {zn:17s} {fa:9s} S sup {ss:.2f} (obs {os_:.2f}) {'ok' if ok1 else 'fuera'}; dS fondo-sup {ds:+.2f} (obs {od:+.2f}) {'ok' if ok2 else 'fuera'}"]
                L += [f"      compatibles: S sup {sum(p[4] for p in pz)}/{len(pz)}, dS {sum(p[7] for p in pz)}/{len(pz)}"]
        if len(casos) == 3:
            cp = conclusion_h6([casos[n]["principal"] for n in range(3)]); cs = conclusion_h6([casos[n]["sensibilidad"] for n in range(3)]) if all("sensibilidad" in casos[n] for n in range(3)) else None
            concl[mes_k] = cp if cs in (None, cp) else "parcial"
            L += [f"  CONCLUSION {mes}: {concl[mes_k].upper()} (principal: {cp}; sensibilidad: {cs or 'sin dato'})"]
            L += [f"  incrementos de S11 (ventana principal; informativo): drenajes {casos[1]['principal'][0] - casos[0]['principal'][0]:+.3f} de cierre, escorrentia {casos[2]['principal'][0] - casos[1]['principal'][0]:+.3f}"]
    if "dic" in concl:
        L += [{"explica": "LECTURA: CONFIRMA que las campanas de 2002 no representan la estacion seca sin lluvia: con el forzamiento y los aportes de 2002 se cierra >= la mitad del hueco y (b) deja de contradecir.",
               "parcial": "LECTURA: PARCIAL: 2002 cierra una parte del hueco (o lo cierra sin que (b) deje de contradecir); la estratificacion observada sigue sin reproducirse del todo.",
               "no explica": "LECTURA: CONTRADICE: con ERA5, OISST, drenajes y escorrentia de 2002 el hueco sigue (cierre < 0,25 en las tres variantes); el sesgo salino en superficie es del modelo, no de la representatividad de las campanas."}[concl["dic"]]]
    L += ["Edad media de la bahia en los ultimos 30 d (2-31 dic 2002; informativo, sin veredicto): R = (edad - 6,025 d de salinidad/m0001) / 5,308 d:"]
    for n in range(3):
        p = D / f"m000{n}" / "resumen.json"
        if p.exists():
            j = json.loads(p.read_text()); e = j["edad_media_d_bahia"]; R = (e - EDAD_REF) / ANCHO
            L += [f"  m000{n} {NOM[n]}: {e:.3f} d (deriva {j.get('deriva_edad_bahia_d_por_d', float('nan')):+.3f} d/d), R = {R:+.3f} ({lectura_R(R)}){' [NaN]' if j.get('nan', 0) else ''}"]
    t = "\n".join(L); print(t); (RAIZ / "resultados" / "dos2002.txt").write_text(t + "\n")


def prueba():
    o = observado(); assert abs(s_obs(o, "2002-12") - S_OBS) < 1e-9 and abs(s_obs(o, "2002-10") - 32.85) < 1e-9
    assert np.allclose(rango_b(o, "2002-12")[1], (3.7, 5.5)) and np.allclose(rango_b(o, "2002-10")[1], (2.7, 3.5))
    t = np.arange(0, 11, 1 / 6); eta = 0.3 * np.cos(2 * np.pi * t / (12.4206012 / 24))
    def z(sup, fondo):
        S = np.full((len(t), 11, 5), fondo); S[:, :, 0] = sup; return dict(t=t, eta_bay=eta, S_n=S, S_r=S.copy())
    med = 35.37
    e = evalua(z(31.25, 35.9), o, "2002-12", med); assert abs(e["cierre"] - 1) < 1e-9 and e["lect"] == "explica" and e["vb"] == "CONFIRMA", e
    e = evalua(z(35.37, 35.6), o, "2002-12", med); assert abs(e["cierre"]) < 1e-9 and e["lect"] == "no explica" and e["vb"] == "CONTRADICE"
    e = evalua(z(33.4, 35.9), o, "2002-12", med); assert e["lect"] == "parcial" and e["vb"] == "PARCIAL", e        # cierre 0,478; dS 2,5
    assert conclusion_h6([(0.1, "CONTRADICE"), (0.6, "PARCIAL"), (0.2, "CONTRADICE")]) == "explica" and conclusion_h6([(0.1, "CONTRADICE")] * 3) == "no explica"
    zest = np.array([1, 2, 2, 2, 2, 2, 4, 5, 5, 4, 4]); o411 = obs_411()
    pz = perfiles(z(35.0, 36.2), zest, o411); assert len(pz) == 8 and all(isinstance(p[4], bool) for p in pz)
    at = [p for p in pz if p[0] == "Atares"]; assert not at[0][4] and not at[1][4]          # 35,0 frente a 27,1 y 21,4: fuera
    print("autoprueba dos2002: ok")


if __name__ == "__main__":
    prueba() if "--prueba" in sys.argv else main()
