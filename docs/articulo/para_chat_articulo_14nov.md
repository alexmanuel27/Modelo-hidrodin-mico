# Para el chat del artículo — respuesta a la revisión V1 (14-nov-2026)

Fuente de cada cifra: `cifras.md`. Commits del repo de trabajo: `7c74c13` (A1, preparado y lectura fijada), `b4fa63a` (A2 y A3), y el de este archivo.

## A1 — m0005 hasta el equilibrio: EN CURSO
Corriendo `runs/robustez_largo`: base, m0001 (borde a 28 °C) y m0005 (calor + OISST) a 365 d (todo 2016), ~2,5 días de reloj, ~1200 horas-núcleo. Lectura fijada antes de correr en `docs/resultados_robustez.md` (adenda 14-nov): equilibrio = |deriva| ≤ 0,05 d/d en los últimos 10 d; si la bahía pasa de 14 d se avisa (cambia «one to two weeks»); si no se equilibra, se da la edad y la deriva tal cual, sin extrapolar. **Hasta entonces no cambia ninguna cifra.** No se hacen los 10–20 miembros con calor (opcional; no pedido en firme).

## A2 — convergencia de Sobol (sin corridas nuevas)
Cifras nuevas (no cambia ninguna existente; N = 64 reproduce `sobol.csv`):
- S_T del caudal, edad de la bahía: N = 16 / 32 / 64 → 0,70 [0,49–0,99] / 0,61 [0,40–0,86] / 0,68 [0,49–0,87]; primero en las 6 zonas con cada N (0,46–0,72).
- Segundo: campo de error de la carta con N = 32 y 64 (0,068; 0,095); con N = 16, la dirección del viento (0,042 [0,016–0,074]) frente al campo de error (0,032 [0,013–0,060]), con IC solapados.
- S_1 del caudal 0,86 / 0,84 / 0,86.
- Comprobación cruzada (S_1 «dado los datos», 128 miembros A y B, 8 intervalos, nula por permutación): caudal 0,83 (P95 nula 0,12); C_d 0,13 frente a una nula de 0,105 (1 de 7 pruebas; su S_T es 0,007).
- Figura suplementaria nueva: `figS_sobol_convergence` (190 × 80 mm), copiada a `articulo/figuras/`.

Texto propuesto:
> The ranking of the total-order indices did not depend on sample size. Recomputing the Jansen estimators with the first N = 16 and 32 rows of each Saltelli block (176 and 352 members) gave river discharge the largest S_T for the bay-mean age at every N (0.70, 0.61 and 0.68 for N = 16, 32 and 64) and in every zone (0.46–0.72), with S_1 = 0.84–0.86. The chart-error field ranked second for N = 32 and 64; for N = 16, wind direction and the chart-error field swapped places within overlapping 95 % intervals (Fig. S#). A given-data estimate of first-order indices from the 128 independent A and B members (eight quantile bins, compared with a permutation null) confirmed the dominance of discharge (S_1 = 0.83; 95th percentile of the null 0.12); among the other continuous parameters only bottom drag slightly exceeded its null (0.13 vs 0.105), as expected by chance among seven tests and consistent with its S_T of 0.007.

## A3 — fig. 6d
Etiqueta cambiada a «Renewal time T_i = M_i/Q_i (d)»; `fig_rivers` (PDF y PNG) regenerada y copiada a `articulo/figuras/`. Sin cambios de datos.

## A4 — justificación de los rangos de la tabla 2
**Aviso:** en el repo los rangos de C_d, viento y datum figuran como «acordados con Alex el 16-oct», sin fuente. Lo que sigue son frases con la fuente que hay; donde no la hay, se dice. Referencias comprobadas en OpenAlex (existen; su contenido no lo he leído): Sternberg 1968, doi:10.1016/0025-3227(68)90033-9; Ramon et al. 2019, doi:10.1002/qj.3616.

- **C_d 0.001–0.005 (log-uniform):**
  > The quadratic bottom-drag coefficient was sampled log-uniformly over 0.001–0.005, a range that brackets the values commonly used for estuaries and tidal channels (≈ 0.0025; e.g. Sternberg, 1968) and spans a factor of five because no current measurements exist in the bay to calibrate it.
  (Comprobar en Sternberg 1968 el valor que cita antes de usarlo.)
- **Viento ×0.8–1.2 y ±15°:**
  > ERA5 winds were scaled by 0.8–1.2 and rotated by ±15° to represent the uncertainty of a 0.25° reanalysis at a coastal site where no local wind record was available; near-surface reanalysis winds carry regional speed biases (Ramon et al., 2019), and the cell nearest the bay mixes land and sea.
  (Los valores ±20 % y ±15° son una elección nuestra; ninguna fuente los fija.)
- **Datum 0 a +0.5 m:**
  > The vertical datum of the nineteenth-century soundings is not stated in the copies used; it is most likely a low-water datum. We therefore added an offset between 0 (soundings referred to mean sea level) and +0.5 m, which exceeds the mean tidal range (0.29 m; JICA, 2004) and the 0.1–0.4 m low- and high-water levels given in the pilots' guide.
  (Fuente de 0,1/0,4 m: guía de prácticos del puerto de La Habana 2018, `datos/batimetria/fuentes/practicos_puerto_habana_2018.txt`; dice «pleamar más baja promedio 0,4 m, bajamar más baja promedio 0,1 m». Si el chat del artículo no la cita ya, decidir si se cita.)
- **Caudales CIMAB de agosto de 2002:**
  > The only published discharges are single gaugings by CIMAB in August 2002 (JICA, 2004, Table 1.1), taken in the rainy season (May–October), and the report states that there are no permanent gauges. Because the simulated window is in the dry season, we treated them as an order-of-magnitude estimate and sampled a factor of 0.25–2 (log-uniform) around them (0.54–4.3 m³ s⁻¹ in total).
  Contexto con fuente (para limitaciones, si se quiere): el invierno 2015–16 fue anómalo: el boletín de sequía de CariCOF de marzo de 2016 (Dec–Feb) dice «Conditions in Cuba ranged from extremely wet in western and central area to slightly wet in the east» (https://rcc.cimh.edu.bb/files/2018/04/CaribbeanDroughtBulletin_March_Vol2_Issue10.pdf), y Reuters/VOA (3-feb-2016) habla de lluvia intensa en el oeste de Cuba en una época normalmente seca. Ninguna fuente es de La Habana ni da caudales; no lo atribuyen a El Niño.
- **¿Por qué 2016 y enero–abril?** Enero–abril está documentado: estación seca y temporada de frentes fríos (bitácora, 16-oct). **Por qué 2016 no está escrito en el repo:** decisión de Alex; no lo invento. Si se usa el contexto anterior, ojo: enero–febrero de 2016 no fue una estación seca típica en el oeste de Cuba.

## A9 — velocidades de ~6 m/s en el borde abierto
Causa probable, sin prueba que la quite:
> The maximum speeds at open-boundary nodes cluster tightly (median 6.0 m s⁻¹, 95th percentile 6.1 m s⁻¹ across members), which points to a boundary instability that grows until SCHISM's velocity limiter (rmaxvel = 5 m s⁻¹ per component) caps it, not to a physical flow. In early tests on a schematic grid, the combination of Coriolis, imposed elevation and wind forcing at the open boundary produced an instability that saturated at about 6 m s⁻¹ and disappeared without Coriolis. These speeds are unrelated to bay age across members (Spearman ρ = −0.07; Fig. S1).
Si se quiere la prueba: 10 d del miembro central sin Coriolis o con borde de tipo Flather (~15 horas-núcleo); no se ha lanzado.
