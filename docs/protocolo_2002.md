# Protocolo: simulación de octubre y diciembre de 2002 (campañas de JICA)

> Escrito el 22-nov-2026, **antes** de descargar ERA5/OISST de 2002, de generar las corridas y de ver ningún valor del modelo en 2002.
> Solo datos públicos (ERA5, NOAA OISST v2.1, JICA 2004 vol. V). Umbrales y reglas: los de la fase II (`docs/protocolo_salinidad_superficie.md`)
> y de A1/A2 (`docs/protocolo_jica_observaciones.md`), sin cambios. Un resultado que contradiga la hipótesis se informa tal cual.

## 0. Pregunta

JICA vol. V, §4.4.1 (M4-44): «En la observación de diciembre del 2002, el decrecimiento de la salinidad hacia Guasabacoa fue más marcado debido
a las lluvias caídas durante las semanas previas motivadas por los frentes fríos». Las campañas pueden no representar una estación seca sin lluvia.
¿Se cierra el hueco de S11 (+4,12 frente a diciembre de 2002) y se acerca el ΔS fondo–superficie a 3,7–5,5 cuando el modelo tiene el tiempo
atmosférico, la SST y los aportes de 2002?

## 1. Fechas de las campañas (leídas en el PDF antes de escribir esto)

- Octubre: **7-oct-2002** (fig. 4.26, «Fecha: 7 octuber 2002»; `jica_2004_vol5_03.pdf`, p. 3).
- Diciembre: **la fecha no está impresa** en el texto ni en las figs. 4.27–4.32 (comprobado también con OCR). La única fecha de diciembre del
  mismo contratista (CENHICA/CIMAB) es la de la calidad de agua de los canales de drenaje, 16–19-dic-2002 (vol. V, cap. 4 de `jica_2004_vol5_04.pdf`;
  en octubre esa campaña fue el 9–13-oct, dos días después de la de la bahía). Se toma 15-dic como centro y una ventana de sensibilidad de 30 d.

## 2. Corridas (`python scripts/conjunto.py dos2002`, `runs/dos2002`)

Miembro central (BASE de `conjunto.py`: carta 1887, α 0,5, datum 0,25 m, Cd 0,0025, sin campo aleatorio), EOT20, **1-sep-2002 00 UTC → 1-ene-2003
(122 d)**: 36 d de arranque antes del 7-oct (la edad de la bahía se equilibra en ~30 d; el tiempo de renovación del agua dulce es ~2 d).
ERA5 de 2002 (viento, presión, T y humedad del aire, radiación) con **flujo de calor** (`CALOR=1`) y **SST OISST de 2002** en el borde y como T
inicial (`SST=oisst`, `oisst_habana_2002.csv`); velocidad 3D y cotas guardadas (`VEL3D=1`, 6 scribes); campos completos conservados (`GUARDAR`
0, 1, 2). **T y S de las fuentes inyectadas en la capa superior** (`LEVSRC=sup`; es la inyección realista para un río que entra en superficie,
véase la respuesta del 22-nov en el registro). Agua de las fuentes: S = 0, T ambiente, edad 0 (como siempre).

| | Caudales (m³/s) | Total |
|---|---|---|
| m0000 | tabla 4.8: Luyanó 1,329; Martín Pérez 0,719; Tadeo 0,093 (iguales a la tabla 1.1 del vol. IV, que ya usa el modelo: 1,3294/0,7188/0,0926) | 2,141 |
| m0001 | m0000 + los drenajes de la tabla 4.8 que caen en Atarés con la georreferencia A2 (`resultados/jica_estaciones.txt`): S4 San Nicolás 0,099; S5 Arroyo Matadero 0,900; S6 Agua Dulce 0,500, cada uno en el elemento de la bahía de centroide más cercano a su posición (sin repetir elementos) | 3,640 |
| m0002 | m0001 + escorrentía de la lluvia de ERA5 en las seis fuentes | 3,640 + 8,744 · I(t) |

Los vertidos de la refinería (S7–S10, 0,094 m³/s en total) no caen en Atarés y no se incluyen.

**Escorrentía (m0002), fijada antes de mirar la lluvia de 2002.** Método racional, el mismo que usa JICA para el drenaje pluvial (vol. V, cap. 6,
`jica_2004_vol5_04.pdf`: Q = C·I·A/360 con A en ha): para cada fuente i, Q_i(t) = Q_i,tabla 4.8 + C_i · I(t) · A_i / 3,6 (m³/s; I en mm/h, A en km²).
- I(t): lluvia horaria de ERA5 (`tp`, en `sflux_prc_AAAAMM.nc` como `prate`), interpolada bilinealmente al centro de la malla (media de lon/lat
  de los nodos) y llevada a marcas horarias (t = 0, 3600 s, …) por interpolación lineal entre los centros de hora (conserva el total; comprobado
  con datos sintéticos: 4 pulsos de 6 mm → 24,0 mm). `vsource.th` horario, paso uniforme (SCHISM cuenta filas, como en `TEM_1.th`).
- A_i: tabla 2.1 de JICA vol. V (`jica_2004_vol5_01.pdf`): Luyanó 30,0; Martín Pérez 13,1; Tadeo 2,6; Arroyo Matadero 6,8; Agua Dulce 6,5 km².
  San Nicolás no tiene cuenca propia en la tabla (es uno de ~17 drenajes pequeños de Habana Vieja): se le asigna la de Habana Vieja, 2,6 km²
  (cota superior). Casablanca, Cabaña y la refinería (6,4 km²) no drenan a Atarés ni a los ríos y quedan fuera.
- C_i: 0,6 en la cuenca del dren Matadero y 0,5 en las demás (los valores de JICA, cap. 6). Σ C·A = 31,48 km² → 8,744 m³/s por mm/h.
- Sin retardo ni pérdidas iniciales (cada hora de lluvia llega a la bahía en la misma hora); sin lluvia directa sobre la bahía ni evaporación
  (SCHISM está compilado sin `PREC_EVAP`; la lluvia directa sobre 5 km² sería ≈ 14 % de la escorrentía efectiva de 31,5 km²). Es una
  estimación por exceso del volumen en las horas de lluvia y por defecto de los picos convectivos (ERA5 a 0,25° los suaviza).

## 3. Lo que se compara (extractor `jica_extrae_estaciones.py`, mismas estaciones, niveles y fases que la fase II)

Ventanas, en días desde el 1-sep-2002 00 UTC (`VENT` en `scripts/dos2002.py`):
- octubre: principal **31–42** (2–12-oct, centrada en el 7-oct); sensibilidad 28–45 (29-sep–14-oct);
- diciembre: principal **100–111** (10–20-dic, centrada en el 15-dic); sensibilidad 92–122 (2–31-dic, 30 d como la fase II).

Para cada ventana y variante (`jica_2002_{oct,oct_s,dic,dic_s}.npz`):
1. **S11** = media de las dos medias de fase (creciente, bajamar; ajuste armónico M2, S2, N2, K1, O1 de la elevación media de la bahía; ≥ 8 muestras
   por fase) de la salinidad a 0,5 m, media de las 11 estaciones (nodo más cercano). Es el estimador con muestras de la fase II, que coincide con el de
   los mapas de 16:00 UTC a ≤ 0,03.
2. **Cierre** = (S11_ref − S11_variante) / (S11_ref − S11_obs,mes), con S11_ref = mediana de los 704 (35,37; `jica_sal_superficie_704.csv`) y S11_obs
   = media de las dos fases de la tabla 4.19: diciembre 31,25 (hueco **+4,12**), octubre 32,85 (hueco +2,52). Lectura de la fase II: ≥ 0,5 «explica»,
   ≥ 0,25 «parcial», < 0,25 «no explica». Se informa también si cada fase cae dentro de la observada ± 1 desviación.
3. **(b) ΔS = S(fondo, 1 m sobre el fondo) − S(0,5 m)**, media de las 11 estaciones y de las dos fases, reglas de A1 con el rango observado del mes:
   diciembre [3,7; 5,5] (contradice si el signo es opuesto, > 11,0 o < 1,85), octubre [2,7; 3,5] (contradice si > 7,0 o < 1,35); nodo y 300 m deben
   coincidir, si no «parcial». El «ΔS del canal» (estación 1) se da dentro de los perfiles por zona (punto 4), sin veredicto propio.
4. **Perfiles de la tabla 4.11** (nov-2001, la única con perfiles por zona), ventana principal de diciembre: por zona con estaciones (canal = est. 1;
   centro = 2–6; Guasabacoa = 7, 10, 11; Atarés = 8, 9; Marimelena no tiene estación y no se evalúa) y fase, S a 0,5 m frente a «surface» y
   S(fondo) − S(0,5 m) frente a «bottom − surface»; compatible si |modelo − observado| ≤ 1 (el margen de la parte I). Se cuentan las compatibles.
   Fecha distinta (nov-2001 frente a dic-2002): sin veredicto, solo se compara con la parte I (abril de 2016: Atarés 0 % compatible).
5. Informativo: edad media de la bahía (últimos 30 d, 2–31-dic) y R = (edad − 6,025 d de `runs/salinidad/m0001`) / 5,308 d.

## 4. Qué confirma y qué contradice (decide diciembre, ventana principal; octubre con la misma regla, informativo)

Regla de la conclusión sobre H6 (`conclusion_h6`), aplicada a las tres variantes:
- **CONFIRMA** («explica»): alguna variante con cierre ≥ 0,5 y (b) distinto de CONTRADICE (ΔS ≥ 1,85, es decir, se acerca a 3,7–5,5). Lectura: las
  campañas de 2002 no representan una estación seca sin lluvia; con el tiempo y los aportes de 2002 el modelo reproduce lo observado y el hueco
  de la fase II se debe sobre todo a comparar con 2016 sin lluvia.
- **PARCIAL**: alguna variante con cierre en [0,25; 0,5), o (por la regla) con cierre ≥ 0,5 pero (b) CONTRADICE (la superficie se endulza pero la
  estratificación no aparece).
- **CONTRADICE** («no explica»): cierre < 0,25 en las tres. Lectura: ni el forzamiento de 2002 ni los drenajes ni la escorrentía cierran el hueco;
  el sesgo salino en superficie es del modelo (o de algo que no se ha probado), no de la representatividad de las campañas.
- Si la conclusión con la ventana de sensibilidad (2–31-dic) no coincide con la principal, la conclusión es **PARCIAL**.
- Incrementos de cierre m0001 − m0000 (drenajes) y m0002 − m0001 (escorrentía): informativos, sin veredicto.

## 5. Coste

Medido en `runs/salinidad/m0000` (mismas salidas, 6 scribes, 4 + 6 = 10 tareas): 20 072 s de pared para 120 d → 55,8 h-núcleo; con calor,
122 d y algo de margen, **≈ 58 h-núcleo por corrida, ≈ 175 h-núcleo las tres** (< 300: no requiere aprobación previa según la petición).
Disco: campos completos de las tres (como los 4 de `runs/salinidad`).

## 6. Pasos (Alex)

1. Mac: `python scripts/descargar_era5.py 200209 200301` (CDS, ~10 peticiones); `python scripts/era5_a_sflux.py 200209 200301`;
   `until bash scripts/descargar_sst_2002.sh; do sleep 60; done`.
2. Mac: `CONJ_DIR=runs/dos2002 CONJ_DIAS=122 CONJ_SEG=20 CONJ_ESCRIBAS=6 CONJ_HORAS=12 CONJ_MARGEN=3 python scripts/conjunto.py dos2002`
   (comprobar en la salida: los 6 elementos de fuente, la lluvia total de ERA5 y el caudal medio de m0002).
3. rsync a Lemaitre4 y `bash lanzar_trabajadores.sh 3`.
4. Cluster, al acabar: `jica_extrae_estaciones.py runs/dos2002/m000N 31 42 jica_2002_oct.npz`, `28 45 jica_2002_oct_s.npz`,
   `100 111 jica_2002_dic.npz`, `92 122 jica_2002_dic_s.npz` (N = 0, 1, 2); rsync de vuelta; `python scripts/dos2002.py`.

## Registro
- 2026-11-22 — Protocolo y código (`caso_real.py`: `MES0`, `DRENAJES`, `LLUVIA`; `conjunto.py dos2002`; `descargar_era5.py`/`era5_a_sflux.py` con
  meses; `descargar_sst_2002.sh`; extractor con nombre de salida; `scripts/dos2002.py --prueba` ok) commiteados antes de descargar nada de 2002.
