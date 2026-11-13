# Cifras del artículo: valor en el borrador, valor actual y de dónde sale

**Actualizado el 7-nov-2026** (main.tex es del 17-oct). Fuente de verdad de cada número que aparece (o aparecerá) en `publication plan/modelo-hidrodin-mico/articulo/main.tex`.
Al cambiar un resultado, se cambia aquí primero; al pasar el número al manuscrito, se marca ✅.

Estado: ✅ final y ya en el manuscrito · 🔁 en el manuscrito pero desactualizado · ⏳ provisional (cambiará) · ➕ falta en el manuscrito

## Área de estudio (sec. 2) y resumen

| Cifra | En main.tex | Valor actual | Fuente | Estado |
|---|---|---|---|---|
| Área de la bahía (incluye canal) | ~5.2 km² | **4.91 km²** | `scripts/batimetria/07_superficies.py` (cartas + costa OSM) | 🔁 |
| Profundidad media | ~9 m | **5.2 (1887) – 5.6 (1879) m** tal cual las cartas; 6.4–7.3 m con dragado | `datos/batimetria/superficies/volumenes_conjunto.json` | 🔁 |
| Volumen | 47 hm³ (tabla 2) | **26–36 hm³** según carta y dragado (central 30) | ídem | 🔁 |
| Canal de entrada | 1530 m, 220–330 m, 12.8 m | igual | Prácticos 2018 | ✅ |
| Marea | "small and mixed, mainly semidiurnal" | Frente a la boca, FES2022 / EOT20: M2 12.2 / 12.6, K1 8.3 / 8.0, O1 8.8 / 8.4, S2 3.9 / 3.8 cm; form factor 1.05 / 1.00 → **mixed**, diurnal ≈ semidiurnal (corregir "mainly semidiurnal"); los dos modelos difieren < 0.4 cm por constituyente y **1,15 cm RMS en el nivel** (9 constituyentes comunes, mismo punto y método que `prisma_marea.py`; `fig_tide`, `scripts/figuras_resultados.py marea`: RMS exacto 1,15 cm, enero 2016 1,16 cm); carrera media 0.29 m (JICA 2004) | `marea_fes2022.py`, `marea_eot20.py` | ⏳ |
| Ríos | — | Luyanó 1.33, Martín Pérez 0.72, Tadeo 0.09 m³ s⁻¹ (total 2.14; CIMAB 2002 en JICA 2004) | `scripts/caso_real.py` (Q_RIOS) | ➕ |
| Retención del agua dulce (literatura) | — | "tiempo de retención del agua dulce ≈ 4 meses" (JICA 2004); el resumen no da el método | JICA 2004, resumen ejecutivo, p. R-7 | ➕ (discusión) |

## Tabla de datos públicos (tab. 1)

| Fila | En main.tex | Corrección |
|---|---|---|
| Costa | "Sentinel-2 water mask" | **OpenStreetMap `natural=coastline`** (instantánea 2026-10-13, ODbL). La máscara S2 no se usó → 🔁 |
| Batimetría | cartas 1889 y 1898 | precisar: levantamientos españoles **hasta 1879 y hasta 1887**, misma carta H.O. n.º 307; 1126 + 1514 sondeos |
| GEBCO | `\todo{ref}` | GEBCO 2026 Grid (citar GEBCO Compilation Group 2026) |
| Marea | FES2022 `\todo{ref}` | FES2022 (doi:10.24400/527896/A01-2024.004) **y EOT20** (Hart-Davis et al. 2021, doi:10.17882/79489, CC BY 4.0, sin registro) |
| Descargas | "literature and Sentinel-2; flows as wide ranges" | **JICA 2004 (tabla 1.1)** para caudales; desembocaduras de OSM `waterway` |
| Marea del conjunto | — | **solo EOT20** en el conjunto, mecanismo y robustez; FES2022 solo para comparar (no redistribuible) |
| SST (solo robustez) | — | ➕ NOAA OISST v2.1 diaria (ERDDAP CoastWatch, dominio público), caja 23,125–23,625 N / 82,875–81,875 W, 13 celdas de mar; ene–abr 2016: 24,5–27,9 °C (`datos/forzamiento/sst/`) |
| Sentinel-2 (evaluación) | `\todo{ref own Sentinel-2 study}` | ➕ entrega del estudio propio en `datos/sentinel2/` (persistencia de anomalías, máscara, focos) |

## Control analítico (sec. 4, tab. 2) — `scripts/prisma_marea.py` → `resultados/prisma_marea.csv`

| Magnitud | En main.tex | Actual (central, P5–P95) | Estado |
|---|---|---|---|
| Volumen | 47 (39–55) hm³ | **30.7 (27.2–34.5)** hm³ | 🔁 |
| Marea | rango supuesto 0.30 (0.20–0.50) m | **días reales de un año EOT20**: mayor llenante 0.33 (0.18–0.50) m, 1.93 llenantes/d | 🔁 |
| Prisma de marea | 1.6 (1.2–2.3) hm³ | **1.6 (0.9–2.5)** hm³ (mayor llenante del día) | 🔁 |
| Fracción renovada | 3.3 (2.6–5.1) % por ciclo | **8.7 (4.1–12.7)** % por día | 🔁 |
| Renovación sin retorno | 16 (10–20) d | **11.6 (7.9–24.5)** d | 🔁 |
| Renovación con retorno + ríos | 34 (18–51) d | **24 (14–47)** d | 🔁 |
| Solo ríos V/Q | — | **136 (83–243)** d (Q 2.14, JICA) | 🔁 |
| Velocidad máx. de marea en el canal | 4.5 (3.2–6.5) cm s⁻¹ | **4.7 (2.7–7.3)** cm s⁻¹ | 🔁 |
| Excursión mareal | 650 (460–920) m | **630 (340–960)** m; 0.41 (0.22–0.63) del canal | 🔁 |
| Figura `fig_prisma_marea.png` | versión vieja | regenerar en inglés con los valores nuevos | 🔁 |

Ojo: el mensaje de main.tex "la excursión es menor que la mitad del canal en todas las muestras" debe pasar a "shorter than the channel in all samples; ≤ 0.63 of its length in 95 %". Valores = mediana (P5–P95) del Monte Carlo, 21-oct-2026 (`resultados/prisma_marea.csv`, columna p50). No mezclar con la columna "central" (todas las entradas en su moda: 30,4 hm³, 11,5 d, 24,4 d, 165 d, 5,1 cm/s, 671 m), que es la que tiene hoy main.tex para el volumen.

## Métodos (sec. 5)

En main.tex (17-oct): 🔁 = el texto tiene el valor viejo.

| Apartado | Cifra actual | Fuente | main.tex |
|---|---|---|---|
| Batimetría | 1126 (1879) + 1514 (1887) sondeos; georreferencia RMS 18 m; registro 1898→1889 residuo mediano 1,2 m; datum incierto 0 a +0,5 m; campo aleatorio exponencial σ = 0,9 m, L = 150 m (variograma de 12 134 diferencias); estado de dragado α ∈ [0, 1] | `docs/00_estado_y_plan.md` §19 | |
| Malla | 4832 nodos, 8941 triángulos; 25 m en el canal (~11 elementos a lo ancho), 40 m en la bahía, ≤ 400 m fuera; ángulo mínimo 12,4°; círculo de 5 km centrado en la boca | `datos/malla/malla_resumen.json` | |
| Vertical | 16 niveles S (h_s = 210 m; profundidad topada a 200 m); 32 solo en una prueba de robustez | `scripts/caso_real.py` | |
| Numérica | dt = 100 s; GLS k-kl (itur = 3, mid = KL, stab = KC); Coriolis; salidas cada 4 h | ídem | |
| Borde abierto | elevación armónica (EOT20, 9 constituyentes); esponja de fricción (Cd → 0,05) y sin viento a < 1 km del borde; sin advección de momento a < 800 m; T = 28 °C y S = 36 fijas | ídem | |
| Densidad | **baroclínico por salinidad en todos los miembros** (ríos con S = 0); temperatura constante, sin flujo de calor; sin evaporación ni precipitación (E − P ~0,1 m³/s en seca, estimación gruesa sin fuente, ~5 % de los ríos) | `caso_real.py`, `docs/protocolo_metricas_conjunto.md` | 🔁 (solo decía densidad en el experimento 3) |
| Edad del agua | módulo AGE; agua nueva = mar abierto **y agua de los ríos** | ídem | |
| Conjunto | Saltelli, N = 64, **d = 9 → 704 miembros** (64 × 11); 9.º parámetro: **caudal de los ríos × 0,25–2** (log-uniforme) sobre 2,14 m³/s; **120 d** desde el 1-ene-2016; marea EOT20 | `scripts/conjunto.py`, `datos/conjunto/diseno.csv` | 🔁 (640, d = 8, 90 d) |
| Métricas | últimos 30 de los 120 d; edad media y p10/50/90 por zona; fracción de volumen con edad > **7, 14 y 30 d**; edad en superficie y fondo del canal; agua dulce en superficie; caudal bruto (ver avisos) | protocolo congelado 27-oct (commit 4564b7e) | 🔁 (solo > 30 d) |
| Equilibrio | deriva de la edad de la bahía ≤ 0,05 d/d en los últimos 10 d; si > 10 % de miembros no llega, se alargan | ídem | |
| Clasificación | robusta ≥ 90 % de los miembros; frágil 10–90 %; rechazada ≤ 10 % (bloques A y B, 2N = 128) | ídem | ➕ |
| Sobol | Jansen S1 y ST; IC 95 % bootstrap (1000); con N = 64 error ~0,1 en ST y ~0,2 en S1 → interpretar ST | `scripts/analisis_conjunto.py` | |
| Cómputo | Lemaitre4 (CÉCI); **7 núcleos por miembro** (4 de cálculo + 3 de escritura: la salinidad es la 3.ª salida 3D); **tramos de 20 d con hotstart** (reinicio comprobado: métricas iguales al 0,01 %); 20 d tardan 0,65–9 h (mediana 1,6 h) según cuántos miembros corren a la vez; **≈ 1,7·10⁵ horas-núcleo asignadas en total** (`sacct -X`, 24-oct a 9-nov, `cluster/horas_nucleo.txt`: incluye conjunto, mecanismo, robustez, pruebas, tramos cortados por tiempo, trabajos cancelados y trabajadores que esperan; reloj de pared × núcleos asignados), de las que **≈ 5,4·10⁴ son el cómputo útil de los 704** (estimación del 9-nov: los 484 miembros completos de la copia de `runs/conjunto/coste.txt` tardan 10,9 h de reloj de media, P5–P95 7,0–15,7 h, × 7 núcleos = 76 h-núcleo por miembro; × 704); mecanismo ≈ 4,4·10² y robustez ≈ 6,4·10² (sin m0005); no cuenta posproceso ni reintentos no registrados; reloj de pared del trabajo × núcleos asignados, no CPU usada ⏳ (repetir al terminar) | `cluster/`, `runs/*/coste.txt`, `docs/00_estado_y_plan.md` (2-nov, 6-nov) | 🔁 (4 + 2 núcleos, 2,7–3,9 h por 90 d) |
| Mecanismo | miembro central (carta 1887, α = 0,5, datum +0,25 m, Cd 0,0025), 1 año 2016, EOT20, 5 tramos de 73 d | `docs/resultados_mecanismo.md` | |
| Robustez | miembro central con ríos, 120 d: cierre k-ε; 32 niveles; difusividad mínima × 10 (10⁻⁵ m²/s); flujo de calor ERA5 (albedo 0,06, Jerlov 7) con borde a 28 °C; **flujo de calor con SST diaria NOAA OISST v2.1 en el borde y como T inicial** ⏳ (corriendo) | `docs/resultados_robustez.md`, `datos/forzamiento/sst/` | ➕ |

## Resultados (sec. 6)

### Mecanismo — firme (`docs/resultados_mecanismo.md`)

Edad media (d, últimos 30 d del año, media de superficie y fondo):

| Zona | Solo marea | + viento | + ríos y densidad |
|---|---|---|---|
| Canal | 35 | 53 | 4,2 |
| Cuenca | 173 | 103 | 6,3 |
| Marimelena | 291 | 102 | 7,1 |
| Guasabacoa | 240 | 115 | 8,1 |
| Atarés | 251 | 118 | 9,6 |
| **Bahía** | **166** | **97** | **6,6** |
| Deriva final (d/d) | +0,36 (sin equilibrio) | +0,09 | −0,03 (equilibrio desde ~día 30) |

**⚠ Dos definiciones de «edad media por zona» en uso (9-nov).** La tabla de arriba es la media simple sobre los nodos de la zona de los mapas de edad en superficie y fondo (promediados en los últimos 30 d); la bahía coincide con la otra definición (166 / 97 / 6,6 d) pero las zonas **no**. La definición del protocolo congelado, la de `resumen.json` (`edad_media_d_*`) y la de la tabla de robustez es la **media ponderada por volumen en los últimos 30 d**:

| Zona | Solo marea | + viento | + ríos y densidad |
|---|---|---|---|
| Canal | 35,6 | 55,5 | 4,0 |
| Cuenca | 170,5 | 103,3 | 6,6 |
| Marimelena | 295,1 | 102,0 | 7,0 |
| Guasabacoa | 211,5 | 113,9 | 7,6 |
| Atarés | 233,3 | 116,7 | 8,9 |
| **Bahía** | **166,2** | **96,7** | **6,6** |

(`runs/mecanismo/m000{0,1,2}/resumen.json`; con ríos coincide con la base de robustez: 4,0 / 6,7 / 7,0 / 7,6 / 8,8 / 6,6.) **Recomendación:** usar esta segunda tabla en el artículo (misma definición que robustez, el protocolo y el conjunto) y decirlo en Métodos. El orden canal < cuenca < Guasabacoa < Atarés se cumple en las dos definiciones y en los tres experimentos; Marimelena sigue siendo la zona frágil (la más vieja con solo marea, algo por debajo de la cuenca con viento, entre cuenca y Guasabacoa con ríos). La figura 7 (`fig_mechanism`) usa la definición ponderada por volumen.

Con densidad: canal 6,5 d en superficie y 1,9 d en el fondo (circulación estuarina); intercambio implícito V/edad ≈ 50 m³/s ≈ 25 veces el caudal de los ríos; coherente con Knudsen (~50–100 m³/s).

**Ojo con la definición:** la edad cuenta el agua de los ríos como agua nueva, así que no es el "tiempo de retención del agua dulce" de JICA. La magnitud comparable es T_f = volumen de agua dulce / caudal de los ríos. **Resultado (8-nov, `scripts/renovacion_dulce.py`, últimos 30 d, V = 30,8 hm³, Q = 2,14 m³/s):** agua dulce media en la bahía 1,1–1,2 % (superficie 2,3–2,5 %, igual que `resumen.json`) → **T_f = 1,8–2,0 d** (robustez base 1,9; k-ε 2,0; mecanismo con 1 año 1,8); **4,2 d** con flujo de calor y borde a 28 °C. Frente a los ~120 d de JICA, unas 60 veces menos. Con ríos solos sin intercambio, V/Q = 136 d (prisma); JICA, con su volumen de 47 hm³, necesitaría Q ≈ 4,5 m³/s para dar 4 meses por V/Q (hipótesis, no se puede afirmar).

### Robustez de la densidad — firme salvo el flujo de calor (`docs/resultados_robustez.md`)

| | Base | k-ε | 32 niveles | Difusividad × 10 | + calor (borde 28 °C) | + calor (SST OISST) |
|---|---|---|---|---|---|---|
| Edad de la bahía (d, días 90–120) | 6,6 | 6,9 | 7,5 | 6,6 | 16,8 (sin equilibrio, deriva −0,10) | **11,2 (sin equilibrio, deriva +0,24; últimos 5 d: 12,7)** |
| Canal sup / fondo (d) | 6,6 / 1,8 | 6,7 / 2,1 | 7,5 / 2,3 | 6,6 / 1,9 | 14,2 / 10,6 | pendiente (mismo script que las otras columnas) |

El orden de las zonas no cambia en ninguno (en m0005: canal 7,6 < cuenca 11,8 < Guasabacoa 12,1 < Marimelena 12,9 < Atarés 13,3; C3 y C1 se cumplen). El experimento con calor y borde a 28 °C es sospechoso: la SST real de ene–abr 2016 es 24,5–27,9 °C. **Con la SST real (m0005) el efecto se reduce (11,2 d frente a 16,8) pero no desaparece: la edad sigue ×1,7 sobre la base y no se estabiliza en 120 d (oscila 9–13,5 d en la ventana). La conclusión honesta es que la renovación es robusta a la turbulencia, a la resolución vertical y a la difusividad, y NO a incluir el balance de calor.** Falta saber si con calor la edad converge a otro valor o sigue creciendo; 120 d no lo dicen.

### Sentinel-2 — firme, resultado negativo (protocolo congelado 21-oct + control 26-oct)

| Experimento | Campo | ρ Spearman | IC 95 % (bloques) | p por desplazamientos | ρ nulo P95 |
|---|---|---|---|---|---|
| ríos y densidad (prueba principal) | agua dulce en superficie | 0,45 | 0,35–0,54 | 0,16 | 0,61 |
| + viento (secundaria) | edad en superficie | 0,48 | 0,39–0,57 | 0,15 | 0,63 |
| solo marea | edad en superficie | 0,29 | 0,17–0,40 | 0,28 | 0,61 |
| ríos y densidad (secundaria) | edad en superficie | 0,46 | 0,37–0,55 | 0,15 | 0,60 |

Fuentes: `resultados/comparacion_s2/m0002_s2_dulce.json` (principal), `m0002_s2_edad.json` (fila «ríos y densidad · edad»; ρ = 0,465, p = 0,147), `m0001_s2_edad.json` (+ viento), `m0000_s2_edad.json` (solo marea). 8908 píxeles, 145 bloques. Regla registrada: criterio principal cumplido, pero p ≥ 0,05 → **no distinguible del azar espacial**: los dos mapas solo comparten el gradiente boca → cabeceras.

### Conjunto de 704 — resultados (9-nov, 704/704 miembros terminados)

Protocolo congelado (27-oct); `scripts/analisis_conjunto.py` → `resultados/conjunto/`. 704 = 64 × (2 + 9): bloques A y B = **128 miembros** para distribuciones y probabilidades; los AB_i solo entran en Sobol. **117 de 128 están en equilibrio** (|deriva| ≤ 0,05 d/d); las clases son las mismas con solo esos 117. Todo condicional a "densidad solo por salinidad, ene–abr 2016, caudales JICA × 0,25–2 (log-uniforme)".

| Zona | Edad media, últimos 30 d (d): mediana (P5–P95) | P(> 7 d) | P(> 14 d) | P(> 30 d) |
|---|---|---|---|---|
| Canal | 4,6 (3,2–6,4) | 0,02 | 0 | 0 |
| Cuenca | 7,7 (5,6–10,2) | 0,69 | 0 | 0 |
| Marimelena | 8,1 (6,3–10,4) | 0,82 | 0 | 0 |
| Guasabacoa | 9,1 (6,4–12,5) | 0,85 | 0 | 0 |
| Atarés | 10,5 (7,3–14,6) | 0,96 | 0,11 | 0 |
| **Bahía** | **7,8 (5,6–10,4)** | **0,68** | **0** | **0** |

Conclusiones del protocolo (fracción de los 128 miembros que las cumplen): **C1** orden canal < cuenca < Guasabacoa < Atarés 1,00 robusta · **C2** Atarés más vieja que el canal 1,00 robusta · **C3** Marimelena más vieja que la cuenca **0,76 frágil** · **C4** Guasabacoa y Atarés más viejas que la cuenca 1,00 robusta · **C5** edad de la bahía < 30 d 1,00 robusta · **C6** < 120 d (JICA "~4 meses") 1,00 robusta · **C7** canal con superficie más vieja que el fondo 1,00 robusta · **P(edad bahía > 7 d)** 0,68 frágil · **> 14 d** 0 rechazada · **> 30 d** 0 rechazada.

**C8 (Sobol, Jansen, bootstrap 1000, N = 64):** el parámetro con mayor S_T en la edad de la bahía es el **caudal de los ríos (qfac): S_T = 0,67 (IC 95 % 0,49–0,89), S_1 = 0,86 (0,80–0,90)**. Todos los demás tienen S_T ≤ 0,10 (campo de error de la carta, es decir la semilla, 0,095; dirección del viento 0,046; edición de la carta 0,032; el resto ≤ 0,013 y la amplitud de la marea 0,003). Mismo reparto en las cinco zonas (qfac 0,56–0,70). Cautelas: con N = 64 los IC de S_1 de los parámetros sin efecto son de ±0,3 (el estimador resta dos cantidades casi iguales), así que de esos S_1 solo se lee "no distinguible de 0"; S_T(qfac) < S_1(qfac) es ruido del estimador (los IC se solapan; en teoría S_T ≥ S_1); y "S_T del caudal 0,67" no significa que el resto sea irrelevante, solo que no se distingue en este diseño.

**Lo que NO cubre el conjunto:** el flujo de calor (la sección de robustez de arriba): m0001 da 16,8 d y m0005 11,2 d, los dos sin equilibrio, y m0001 estaría por encima de 14 d. "P(> 14 d) = 0" vale dentro de la estructura del modelo del conjunto, no frente a esa alternativa estructural.

**Sentinel-2 (conjunto, `resultados/comparacion_s2/conjunto_s2_dulce.json`):** ρ > 0 en **128/128** miembros con ríos (mediana 0,447, P5–P95 0,434–0,465) → por el protocolo el resultado es "robusto" (≥ 90 %), pero la dispersión es mínima porque el patrón espacial apenas depende de los parámetros, y el control de desplazamientos del caso central sigue en p = 0,16: **no distinguible del azar espacial** (regla del 26-oct). El control de desplazamientos no se ha repetido por miembro.

Figuras: `fig_ensemble` (5) y `fig_sobol` (6) generadas con estos datos.

### Trazadores por río (fig. 8) — ⏳ EN REVISIÓN, NO USAR todavía en el manuscrito (10-nov)

Protocolo congelado 8-nov (`docs/protocolo_trazadores_rios.md`); 4 casos de 120 d, últimos 30 d. **Bloqueo por la regla del protocolo:** el control de la suma de trazadores frente al agua dulce de la salinidad debe dar < 5 % y en T1 da 5,43 % (T0 2,2 %, T2 0,46 %, T3 0,57 %); mientras no se entienda, no se usan resultados. Validación del ejecutable: T0 frente a robustez m0000 0,08–0,18 % en `resumen.json` (pasa). **Diagnóstico del control (10-nov):** los trazadores suman menos agua dulce que la salinidad (−2,2 %, −5,4 %, +0,46 %, −0,57 % en T0–T3; ≈ 0,003–0,012 psu), sin recorte de S > 36 ni agua dulce inicial; sin recorte ni agua dulce inicial. **Comprobaciones (10–13-nov, `docs/protocolo_trazadores_rios.md`):** no es el limitador TVD (los tres trazadores suman lo mismo que uno solo, 0,07 %), ni la inyección, ni los reinicios; con la tolerancia del TVD vertical `eps1_tvd_imp` = 1e-9 en lugar de 1e-4 el control de T1 pasa de −5,45 % a +1,67 %, y lo que cambia es sobre todo la salinidad (−6,6 %; trazadores +0,5 %): la tolerancia es relativa al valor del trazador y para S ≈ 36 es laxa. Lectura fijada: «intermedio» (umbral 1 %). Corrigiendo el desajuste por zona no cambia ninguna de R1–R4. Decisión pendiente de Alex. **Aviso para T_f y Sentinel-2:** el agua dulce por salinidad (corridas con 1e-4) puede llevar un error numérico de unos pocos % (−6,6 % en T1 con caudal ×0,25; en el caudal base, sin comprobar, el control de T0 sugiere ~2 %).

| Caso | T_i (d): Luyanó / Martín Pérez / Tadeo | M_i (hm³) | En equilibrio (≤ 1 %/d) |
|---|---|---|---|
| T0 central | 1,97 / 1,69 / 2,52 | 0,226 / 0,105 / 0,020 | no / sí / no |
| T1 caudal × 0,25 | 4,17 / 3,11 / 5,73 | 0,120 / 0,048 / 0,011 | sí / sí / sí |
| T2 caudal × 2 | 1,27 / 1,33 / 1,54 | 0,291 / 0,165 / 0,025 | no / sí / no |
| T3 calor + OISST | 2,84 / 2,41 / 4,96 | 0,326 / 0,150 / 0,040 | sí / sí / no |

Provisional (si el control se resolviera): **R1** (T_i < 7 d) se cumple en los 4 casos (máximo 5,7 d, Tadeo en T1); **R2** (menos agua de los ríos en Atarés que en Guasabacoa) se cumple en los 4 pero con poco margen (Atarés 6–11 % por debajo); **R3** (> 50 % del agua del Luyanó y del Martín Pérez en Guasabacoa + cuenca) se cumple en los 4 (63–64 % y 67–69 %); **R4** (Tadeo sobre todo en Marimelena) **no se cumple en ninguno**: solo 10–15 % de M_Tadeo está en Marimelena y 44–48 % en la cuenca. Los T_i son mucho menores que el «≈ 4 meses» de JICA (como T_f = 1,8–2,0 d). En los casos sin equilibrio M_i deriva entre −2,3 y +1,5 %/d, así que esos T_i tienen esa incertidumbre añadida.

### Avisos sobre el caudal por el canal — no usar como resultado

- **Neto:** −6 a +7 m³/s cuando debería ser ≈ −2,1 → error de ±6 m³/s.
- **Bruto (~70 m³/s):** sale de instantáneas cada 4 h de la velocidad promediada en vertical. Tiene picos de toda la sección de hasta 3–10 veces el cambio de volumen de la bahía (base: máx. 370 m³/s; 32 niveles: máx. 932, por eso da 90). La hipótesis de una oscilación permanente de ~1 h **no se sostiene**: el día 121 con salida cada 10 min (`cluster/hf_caudal.sh`) no tiene varianza por debajo de 2 h (88 % semidiurna); los picos siguen sin explicar (intermitentes). Ese día, la media de |Q| muestreada cada 4 h varía ±15 % según la fase (34,5–46,8 frente a 40,6 m³/s). Además, al promediar en vertical no ve la circulación estuarina. Tampoco usarlo para "el modelo reproduce el prisma".
- **9-nov, repetición desde el hotstart del día 120 (`m0000_hf`, 2 d, cada 10 min; `cluster/hf_caudal_diag.txt`):** esta vez sí hay mucha varianza por debajo de 2 h (46 %; 12 h solo 22 %, pico de 1 h 5 %) y la media de |Q| es 59,8 m³/s (45,6–79,6 según la fase del muestreo de 4 h), distinto del día 121 de la corrida original (40,6). **No cuadra con lo del día 121, y no es un transitorio del reinicio** (repetido el 10-nov con el control nuevo, `cluster/hf_caudal_diag.txt`): el primer día está tranquilo (desviación de los saltos de Q entre instantes de 10 min por bloques de 6 h: 4,3 · 1,5 · 3,1 · 2,6 m³/s) y en el segundo aparecen ráfagas de alta frecuencia (4,8 · **147** · **68** m³/s); solo ese segundo día tiene un 85 % de la varianza por debajo de 2 h, media de |Q| 78,9 m³/s y entre 51 y 116 según la fase del muestreo de 4 h. Es decir, el caudal instantáneo por la sección tiene ráfagas intermitentes de origen no aclarado (sin explicar si son numéricas); el caudal bruto sigue sin usarse como resultado, y su valor depende mucho de la fase del muestreo.

### Superado (no usar)

Las cifras provisionales del 17-oct que hay en main.tex sec. 6.1 (2 miembros de 90 d, M2 de 0,15 m, sin ríos: edad 28–37 d, 55–76 % del volumen > 30 d, caudal 64–74 frente a 66 del prisma) y el conjunto de 640.

## Highlights

- "Tidal excursion is shorter than the entrance channel: the tide alone flushes poorly" → sigue valiendo (0,41 del canal) y ahora lo confirma el modelo (166 d con solo marea).
- Nuevo candidato: "Density-driven exchange from 2 m³/s of river water flushes the bay in about a week, 25 times faster than the tide alone" (firme frente a turbulencia y resolución; pendiente del flujo de calor).

## Nombres de las figuras de resultados a tamaño final (9-nov)

`docs/figuras/articulo/`: `fig_prisma` (control analítico, 190 × 72 mm), `fig_mechanism` (mecanismo, 190 × 72), `fig_robustness` (robustez, **90 × 62**), `fig_sentinel2` (Sentinel-2 con (a)(b) y el nulo de ρ, 190 × 70), `fig_tide` (EOT20 − FES2022, 190 × 70); tras el conjunto: `fig_ensemble` (190 × 72) y `fig_sobol` (190 × 80). PNG a 300 ppp y PDF vectorial (mapas solo PNG). No llevan el número de figura en el nombre porque la numeración difiere entre los documentos (ver `figuras.md`).
