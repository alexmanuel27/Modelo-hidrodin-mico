# Comparación del conjunto con las observaciones de JICA 2004 (vol. V): protocolo CONGELADO

> **Congelado el 18-nov-2026**, antes de abrir el vol. V del informe y antes de extraer del modelo ninguna cantidad en
> los puntos de las estaciones. Lo único que se conoce al escribirlo es lo que pidió Alex: qué tablas hay (4.8, 4.11,
> 4.19, 4.20), la figura 4.25 con las 12 estaciones y que la época seca es diciembre de 2002. Cualquier cambio posterior
> va solo en el registro fechado del final, nunca editando el texto de arriba.
> Solo datos públicos: JICA 2004, vol. V, caps. 4.3–4.4 (`openjicareport.jica.go.jp/pdf/11767233_04.pdf`), el modelo
> del repo y los resultados ya existentes del conjunto.

## 1. Datos observados

Un único fichero, `datos/observaciones/jica2004_vol5.csv`, con una fila por valor y las columnas: `tabla`, `pagina_informe`
(la impresa), `pagina_pdf`, `estacion`, `variable`, `nivel_m` (profundidad bajo la superficie), `fase` (creciente,
bajamar, media_24h, otra), `mes`, `valor`, `unidad`, `nota`. Contiene las tablas 4.19 (salinidad en superficie, 5 m y 10 m,
creciente y bajamar, octubre y diciembre de 2002), 4.20 (velocidades por nivel en las tres estaciones de 24 h), 4.8
(caudales) y 4.11 (temperatura, noviembre de 2001), más las coordenadas o la posición de las 12 estaciones de la
figura 4.25.
- Si el PDF tiene capa de texto se extrae de ahí. Si es una imagen, se transcribe leyendo cada página dos veces; las
  lecturas que no coinciden o son dudosas llevan `nota = dudoso` y no se usan en ningún veredicto.
- Un valor ilegible no se rellena ni se interpola: la fila no existe.
- Comprobación de la transcripción: nº de filas por tabla frente al nº de celdas de la tabla impresa, y las sumas
  o medias que la propia tabla imprima.

## 2. Referencia y lo que se compara

La referencia es la **época seca (diciembre de 2002)**. Octubre de 2002 se informa pero no decide ningún veredicto.
Las comparaciones se hacen con las estaciones que la figura 4.25 y el texto ubican dentro del **canal de entrada**
(zona 1 de la malla, `posproceso_malla.npz`); si una estación está en el borde, se asigna al lado que dice el texto.
Si el informe no da coordenadas, la posición se toma superponiendo la figura 4.25 sobre la costa de OSM con una
transformación afín de al menos 4 puntos de control y se asigna al nodo de agua más cercano con incertidumbre de ±100 m;
se informa también el resultado con el nodo a 150 m de distancia.

### (a) Circulación estuarina en el canal
Observación: velocidad media de 24 h, con signo, por nivel, proyectada sobre el eje del canal (hacia fuera / hacia dentro),
en la estación de 24 h del canal (tabla 4.20). Modelo: media sobre un número entero de ciclos de M2 de la misma
proyección, en superficie y en el nivel más profundo medido.
- **Confirma**: la observación y el modelo (mediana de los miembros; el único miembro disponible en la fase A) muestran
  superficie neta hacia fuera y fondo neto hacia dentro.
- **Contradice**: la observación muestra esa inversión vertical y el modelo no, o el modelo la muestra y la observación
  no, o el signo de la superficie es opuesto en ambos.
- **No evaluable**: la tabla no da el sentido de la corriente (solo módulos) o no hay estación de 24 h en el canal.
  No se sustituye por otra estación.

### (b) Diferencia de salinidad superficie–fondo en el canal
Observación: ΔS = S(10 m) − S(superficie) en las estaciones del canal, en diciembre, por fase (creciente y bajamar) y
promediando ambas. Modelo: la misma diferencia, con S interpolada verticalmente a esas profundidades bajo la
superficie (el canal tiene 15–18 m, así que 10 m no es el fondo; no se compara con la salinidad del fondo). El rango
observado es [mín, máx] de los valores observados de ΔS (todas las estaciones del canal y las dos fases).
- **Confirma**: el signo de la mediana del modelo coincide con el observado **y** cae dentro del rango observado.
- **Contradice**: el signo es opuesto, o el módulo de la mediana del modelo es mayor que 2 × el máximo observado, o
  menor que ½ × el mínimo observado.
- **Parcial**: cualquier otro caso (mismo signo, fuera del rango pero dentro de un factor 2).

### (c) Velocidades medias por nivel en la estación 1
Observación: velocidad media por nivel de la tabla 4.20 en la estación 1. Modelo: la misma magnitud, en el nodo de la
estación, con el mismo promedio que usa la tabla. Se compara el módulo, r_n = |U_modelo| / |U_obs| por nivel, y el
sentido si la tabla lo da.
- **Confirma**: 0,5 ≤ r_n ≤ 2 en todos los niveles.
- **Contradice**: algún nivel con r_n < 0,25 o r_n > 4, o el sentido opuesto en dos o más niveles.
- **Parcial**: cualquier otro caso.

## 3. Modelo: de dónde salen las cantidades

- **Qué hay guardado hoy** (de leer `posproceso.py`, `caso_real.py` y `conjunto.py`, sin mirar resultados): en
  `resumen.json`/`resumen.npz` de cada miembro solo hay edades por zona y mapas, el caudal por la sección y la fracción de
  agua dulce **en superficie** (media de los últimos 30 d y 30 mapas a las 16:00 UTC en la rejilla de 20 m). No hay
  salinidad a 5 o 10 m ni velocidad por nivel. Los campos completos (3D) solo se conservaron en el cluster para los
  miembros m0000–m0002 de cada carpeta (`GUARDAR`). La numeración del `param.nml` indica que `iof_hydro(16) = 1` es la
  velocidad horizontal 3D, pero eso no está comprobado en un fichero de salida real.
- **Fase A, sin corridas nuevas**: los campos completos de m0000–m0002 de `runs/conjunto` (120 d desde el 1-ene-2016,
  ventana = días 91–120) y de `runs/termico` (365 d, X1/X2, ventana de **diciembre = días 335–365**). Con 3 miembros no hay
  «fracción de miembros»: se informa el valor de cada uno frente al rango observado.
- **Fase B, corridas nuevas con salida de estaciones (SCHISM `iout_sta`)** en los puntos y niveles de las estaciones, para
  los 64 miembros sin calor y los 64 con calor (pares del conjunto). Es la única forma de obtener la fracción de miembros
  en (a), (b) y (c); la requiere decidir Alex porque cuesta cluster (véase el punto 5).
- **Fracción de miembros dentro de la dispersión observada** = nº de miembros cuyo valor cae dentro de [mín, máx] de lo
  observado / nº de miembros, por magnitud, estación, nivel y fase, con N = 64 + 64. Si una tabla da una media y una
  desviación, la dispersión es media ± 1 desviación. Si da un único valor, la fracción no se calcula y se informa la
  distancia relativa.
- **Fases de la marea en el modelo**: creciente = las 2 h centradas en la mayor velocidad de subida de la elevación media
  de la bahía; bajamar = ±1 h del mínimo de esa elevación en cada ciclo.
- **Salinidad en superficie con lo que ya hay (sin corridas nuevas, 704 miembros)**: S_sup = 36 · (1 − fracción de
  dulce) en la celda de la estación a las 16:00 UTC; la fase se toma del signo de Q en ese instante. Es lo único de la
  tabla 4.19 que se puede comparar con todos los miembros hoy. No sustituye a (b).

## 4. Los tres drenajes que faltan (tabla 4.8)

Arroyo Matadero 0,9; Agua Dulce 0,5; San Nicolás 0,099 m³/s (suma 1,499) frente a los 2,14 m³/s de los tres ríos del
modelo: el caudal total sube un factor f = (2,14 + 1,499) / 2,14 = 1,70.
- **Estimación con los 704 miembros ya corridos** (sin corridas nuevas): ln(edad media de la bahía) = b0 + Σ b_i x_i +
  c (ln qfac)², con los nueve parámetros del diseño en `datos/conjunto/diseno.csv`. Efecto = mediana, sobre los miembros
  con qfac ≤ 2/1,70 (para no extrapolar fuera del rango muestreado 0,25–2), de la edad predicha con qfac × 1,70 menos
  la predicha con qfac. R = efecto / (P5–P95 de los 704). Se informa también por zona.
- **Lectura**: «cambia» si R ≥ 0,25; «no cambia» si R < 0,10; «parcial» entre ambos. Se informa además que f = 1,70 está
  dentro del rango de qfac que el conjunto ya muestrea (0,25–2), de modo que el conjunto ya cubre ese caudal total.
- **Supuesto fijado**: los tres drenajes descargan en las zonas donde ya descargan los ríos del modelo, en la misma
  proporción. No se sabe dónde desembocan (no están en la capa OSM de cauces del repo), así que esta estimación no dice
  nada del efecto local de la salinidad junto a sus bocas.
- **Si la tabla 4.8 da caudales distintos de los de la tabla 1.1 del vol. IV para los tres ríos del modelo** (más de un
  10 %), se informa; el modelo no se cambia.
- **Coste de una variante con los tres drenajes**: miembro por miembro igual que el actual (el coste no depende del
  número de fuentes). Se calcula con la cifra medida del conjunto con calor (3,1 × 10³ h-núcleo para 64 miembros de
  120 d, 48 h-núcleo por miembro), más lo que haya que añadir en `caso_real.py` para localizar las desembocaduras.

## 5. Qué entrega la comparación

Cifras con commit, una figura en `docs/figuras/articulo/` (observación frente a modelo por magnitud, rango observado y
miembros) y qué cambia en el texto del artículo (antes → después), cada veredicto con las reglas de arriba. Un resultado
que contradiga la hipótesis se informa tal cual.

## Registro
- 2026-11-18 — **Resultado del punto 4 (tabla 4.8), con la lectura de la sección 4 sin cambios.** `scripts/jica_caudales_extra.py` sobre los 704 miembros (todos con resumen y sin NaN; 639 en equilibrio). F = 1,700, dentro del rango de qfac muestreado (0,25–2); se usan 519 miembros con qfac ≤ 1,176. **Edad media de la bahía: efecto mediano −1,22 d (la edad baja), R = −0,230 → PARCIAL**, justo por debajo del umbral 0,25 (R² del ajuste 0,92). Por zona, todos entre −0,20 y −0,25: canal −0,82 d, cuenca −1,15, Marimelena −0,88, Guasabacoa −1,46, Atarés −1,81 d. Con solo los miembros en equilibrio, la bahía da R = −0,233 y **Atarés R = −0,250, que por la regla es CAMBIA** (en el umbral). La decisión de la sección 4 se toma con la bahía y todos los miembros válidos: PARCIAL. Limitaciones: supone que los tres drenajes descargan donde ya lo hacen los ríos del modelo (no se sabe dónde desembocan; no están en la capa OSM de cauces del repo) y no dice nada de la salinidad junto a sus bocas. Cifras en `resultados/jica_caudales_extra.txt`.
- 2026-11-18 — **ENMIENDA A1: lectura de las tablas reales. Escrita después de transcribir las tablas (c216aeb) y ANTES de georreferenciar las estaciones y de extraer del modelo ninguna cantidad en ellas. Los umbrales no cambian; lo que cambia es qué cantidad se compara.**
  Lo que se vio al abrir el informe (solo observaciones): (1) la tabla 4.19 resume juntas las estaciones de la bahía (media ± desviación entre estaciones y momentos), no da canal por separado; (2) la tabla 4.20 da solo el módulo de la velocidad, sin sentido, para la bahía (creciente y bajamar) y para las estaciones 1, 3 y 5 en 24 h; (3) la tabla 4.11 sí separa «Canal de Entrada» (superficie, medio, fondo) pero es de junio y noviembre de 2001; (4) la figura 4.25 no tiene coordenadas impresas (ejes 0–60 y 0–65 en unidades de la figura); (5) el sentido de las corrientes solo está en las figuras 4.29–4.32 (vectores), no en una tabla.
  **(a) Circulación estuarina en el canal: NO EVALUABLE** con las reglas de la sección 2 (la tabla 4.20 no da sentido). Se mantiene así, sin sustituir por otra estación. Solo se describe, sin veredicto y con la etiqueta «cualitativo, no es una medición del canal en diciembre de 2002», si el modelo da superficie neta hacia fuera y fondo neto hacia dentro en el canal, frente a la frase del texto (M4-48: circulación neta hacia mar abierto en superficie y hacia la bahía en el fondo, establecida por el PNUD en 1982/83).
  **(b) Diferencia de salinidad superficie–10 m, ahora para el conjunto de la bahía y no solo el canal.** Observado (diciembre de 2002, tabla 4.19): ΔS = S(10 m) − S(superficie) con las medias impresas: creciente 35,9 − 32,2 = **+3,7**; bajamar 35,8 − 30,3 = **+5,5**; rango observado [3,7; 5,5]. Modelo: media sobre las 11 posiciones de la figura 4.25 (nodo más cercano) de S(10 m) − S(superficie) en la misma fase; mediana de los miembros. Reglas **idénticas** a la sección 2(b) aplicadas a ese rango: confirma si el signo coincide y la mediana está en [3,7; 5,5]; contradice si el signo es opuesto o |mediana| > 2 × 5,5 = 11,0 o < ½ × 3,7 = 1,85; parcial en el resto. Se informa por separado cada fase y la media de las dos. Dispersión observada para la fracción de miembros: ΔS ± √(sd_sup² + sd_10²): creciente 3,7 ± 1,0; bajamar 5,5 ± 3,5. Esa sd es dispersión entre estaciones y momentos, no error de medida: la fracción es una medida de compatibilidad, no una prueba. Aparte, sin veredicto: canal de entrada de la tabla 4.11 (noviembre de 2001, S(fondo) − S(superficie): creciente +0,79; bajamar +1,76) frente al modelo en la zona 1.
  **(c) Estación 1, velocidades por nivel: sin cambios de regla.** Observado en diciembre (tabla 4.20): 15,9 ± 7,8 (superficie), 16,3 ± 5,6 (5 m), 17,1 ± 7,0 (10 m) cm/s; es la media del módulo en 24 h (muestras cada 2 h). Modelo: media temporal del módulo de la velocidad horizontal en el nodo de la estación 1, sobre 2 ciclos de M2 (24,84 h), interpolada a 0,5 m, 5 m y 10 m bajo la superficie (si la profundidad local es menor que 10 m, ese nivel no se evalúa). La parte «sentido opuesto» de la regla no aplica. La tabla 4.18 dice niveles 0,5 m / medio / 1 m sobre el fondo y la 4.20 rotula 5 m y 10 m: se usan los rótulos de la 4.20 y, como sensibilidad, los niveles de la 4.18.
  **Posición de las estaciones: ajuste por máscara en vez de afín con ≥4 puntos.** La figura no trae puntos de control impresos. Hipótesis a comprobar, no supuesta: la figura usa 1 unidad = 2 celdas de la malla de 30 m de JICA (60 m/unidad; la malla es 130 × 130 y los ejes llegan a 60 y 65). Método: se extrae del PNG de la figura la máscara de agua (la zona con rejilla dibujada), se pasa a metros con escala s (parte de 60 m/unidad) y se ajusta una similitud (giro, traslación y s) contra la máscara de la bahía del modelo (nodos con zona > 0 de `posproceso_malla.npz`) maximizando la intersección sobre la unión (IoU). **Se acepta si IoU ≥ 0,75 y s está entre 45 y 75 m/unidad; si no, (b) y (c) quedan «no evaluables» y se informa.** Comprobación independiente: las bocas de Luyano, Martín Pérez y Tadeo de la tabla 4.8 (celdas x, y de JICA ÷ 2 en unidades de la figura, mismas transformación) deben caer a ≤ 300 m (mediana) de las desembocaduras del modelo (`desembocaduras()` de `caso_real.py`). Las estaciones se asignan al nodo de agua más cercano; se informa también con el nodo a 150 m de distancia.
  **Fuente del modelo.** Los campos completos (salinidad y velocidad por nivel) de m0000–m0002 solo están en el cluster (el repo local tiene `outputs/` vacío). La fase A necesita que Alex ejecute en el cluster un script de extracción que se commitea antes; la fase B (corridas nuevas con salida de estaciones, 64 + 64 miembros) cuesta ≈ 3 × 10³ h-núcleo por conjunto de 64 y la decide Alex. Hasta entonces no hay veredicto de (b) ni de (c), y la fracción de miembros solo puede darse con la fase B.
- 2026-11-18 — **Resultado de la georreferenciación de las estaciones (enmienda A1), con los criterios de aceptación sin cambios.** `scripts/jica_georreferenciar.py` (prueba con transformación conocida: ok), salida en `resultados/jica_estaciones.txt`, `datos/observaciones/jica2004_estaciones_utm.csv` y diagnóstico `resultados/jica_georreferencia.png`. Ajuste: sin reflexión, giro 328,75°, **escala 67,0 m/unidad** (no 60: la hipótesis de 2 celdas de 30 m por unidad no se cumple; el área de la máscara a 67 m/unidad es 5,38 km², frente a los 5,2 km² del texto de JICA y los 4,93 km² del modelo), **IoU = 0,788** (cumple ≥ 0,75, escala dentro de 45–75), pero la **mediana de la distancia a las 3 bocas de la tabla 4.8 es 318 m (Luyano 311, Martín Pérez 503, Tadeo 318) frente al límite de 300 m: la transformación queda RECHAZADA por la regla de la enmienda A1 (por 18 m), y (b) y (c) son «no evaluables» salvo que Alex decida una enmienda A2.** Primera ejecución: IoU = 0,687 con una máscara muestreada cada 3 px; el IoU salía sesgado a la baja porque con ~1 punto por celda de 20 m la cobertura rasterizada es < 1; se corrigió el muestreo (cada 2 px) y se repitió, sin tocar ningún criterio; el resto del ajuste (giro, escala, traslación) no cambió. Posiciones resultantes (nodo de la bahía más cercano, a ≤ 25 m): estación 1 en el canal (zona 1, prof. 13,6 m en el `hgrid`); 2–6 en la cuenca (zona 2); 7, 10 y 11 en Guasabacoa (zona 4); 8 y 9 en Atarés (zona 5); la estación 11 cae en un nodo de 2,1 m de profundidad (no hay nivel de 10 m). Los tres drenajes que faltan (S4–S6) caen en Atarés (zona 5; S6 a 146 m del nodo más cercano), solo como indicación porque la transformación está rechazada.
- 2026-11-18 — **ENMIENDA A2 (decidida por Alex tras ver que la georreferencia queda rechazada por 18 m): se acepta la transformación SOLO para las cantidades de toda la bahía de (b) y para la comparación de salinidad en superficie con los 704 miembros; (c) sigue «no evaluable» y (a) también. Es una enmienda POSTERIOR al resultado de la georreferencia (hay que decirlo así en el artículo) y ANTERIOR a cualquier valor del modelo en las estaciones. Los umbrales de A1 no cambian.**
  **Incertidumbre de posición.** Las estaciones se toman en el nodo de la bahía más cercano (posición principal, `datos/observaciones/jica2004_estaciones_utm.csv`) y como sensibilidad en la media de los nodos a ≤ 300 m (la mediana de error de las bocas es 318 m). Si ambas versiones no coinciden en el veredicto, el veredicto es «parcial».
  **(b), niveles.** En la bahía la profundidad media es 9 m (JICA) y 9 de las 11 estaciones tienen < 10 m en el `hgrid`, así que «10 m» no existe en la mayoría. Se usan los niveles de la tabla 4.18: superficie = 0,5 m bajo la superficie y fondo = 1 m sobre el fondo; ΔS_b = S(fondo) − S(superficie), media sobre las estaciones con profundidad total ≥ 2 m. Como sensibilidad, ΔS con 10 m bajo la superficie solo en las estaciones con profundidad total ≥ 10,5 m. El rango observado y las reglas de confirma/contradice/parcial son los de A1 ([3,7; 5,5]; 11,0; 1,85).
  **Fases con salida cada 4 h.** Los miembros guardan campos cada 4 h (`nspool` 144 × 100 s), de modo que no se puede derivar la velocidad de subida entre muestras. Se ajusta por mínimos cuadrados a la elevación media de la bahía (nodos con zona > 0) en la ventana una marea armónica de M2, S2, N2, K1 y O1; sobre esa curva continua, creciente = muestras a ≤ 1 h del instante de máxima velocidad de subida de cada ciclo, y bajamar = muestras a ≤ 1 h del mínimo de cada ciclo (las mismas definiciones de A1). Con menos de 8 muestras en una fase, esa fase de ese miembro no se evalúa.
  **Fuente del modelo en la fase A.** Conjunto, miembros m0000–m0002: ventana de los días 91–120 (abril de 2016, final de la época seca; **no es diciembre**, y así se informa). Diciembre (días 335–365) solo existe en las corridas X1/X2 (`runs/termico`), cuando terminen; se informa por separado y es la que cuenta como «época seca de referencia». Con 3 miembros el veredicto se toma con la mediana de los 3, y se informa cada uno.
  **Salinidad en superficie con los 704 miembros (sección 3, sin cambios de umbral, sin veredicto).** Para cada miembro, S_sup = 36 · (1 − fracción de dulce) en la celda de la rejilla S2 (20 m) más cercana a cada estación (y media de las celdas a ≤ 300 m como sensibilidad), media de las 11 estaciones, en cada uno de sus 30 mapas de las 16:00 UTC (días 91–120); la fase sale del signo de Q en ese instante (Q > 0 hacia dentro = creciente; Q < 0 = bajamar, que en realidad es vaciante: es la única separación posible con lo guardado). Media del miembro por fase (mínimo 3 mapas). Se informa la fracción de los 704 (y de los 639 en equilibrio) con la media dentro de la observada ± 1 desviación en diciembre de 2002 (creciente 32,2 ± 1,0; bajamar 30,3 ± 3,5), y la de octubre (32,4 ± 1,5; 33,3 ± 0,9) sin que decida nada. Avisos: abril de 2016 frente a diciembre de 2002; una sola hora del día; las observaciones de JICA tienen lluvias recientes (texto M4-44, «frentes fríos»).
- 2026-11-18 — **Resultado de la salinidad en superficie con los 704 miembros (A2, sin veredicto).** `scripts/jica_compara_modelo.py` (commit 67b23dd, ejecutado después), salida en `resultados/jica_comparacion.txt` y `resultados/jica_sal_superficie_704.csv`, figura `docs/figuras/articulo/fig_jica_comparison.{png,pdf}` (paneles a y b; el c espera la fase A). Media de las 11 estaciones (abril de 2016, días 91–120): **P5/P50/P95 = 35,0/35,4/35,7 en creciente y 34,9/35,4/35,7 en bajamar; ningún miembro de los 704 (0 %; 0 % de los 639 en equilibrio) cae dentro de la observada ± 1 desviación**, ni en diciembre de 2002 (creciente 32,2 ± 1,0; bajamar 30,3 ± 3,5) ni en octubre (32,4 ± 1,5; 33,3 ± 0,9). Lo mismo con la media de las celdas a ≤ 300 m, así que no depende de la incertidumbre de posición. El miembro más salado en superficie en la creciente da 34,65 (qfac alto) y la correlación de la salinidad con ln qfac es −0,84: más caudal baja la salinidad, pero ni con qfac = 2 (4,3 m³/s) se alcanza lo observado. En fracción de agua dulce en superficie, el modelo da 1–5 % de la bahía (mediana 1,9 %) y lo observado en las estaciones equivale a ≈ 10–16 % (1 − 32,2/36 y 1 − 30,3/36). Hechos que no se han investigado (no se ha cambiado nada): el modelo no tiene lluvia, evaporación ni aguas residuales fuera de los tres ríos; las estaciones de JICA están más en el interior que el promedio de la bahía; abril de 2016 frente a 2002; una sola hora del día; la fase «bajamar» es en realidad Q ≤ 0.
- 2026-11-18 — **Resultado de (b) con campos completos, fase A, conjunto m0000–m0002 (días 91–120, abril de 2016), con las reglas de A1/A2 sin cambios: CONTRADICE.** Series extraídas en el cluster con `scripts/jica_extrae_estaciones.py` (cccbee8; 175 muestras por miembro, 29/29, 29/28 y 28/29 muestras por fase) y guardadas en `resultados/jica_estaciones_modelo/`; veredicto de `scripts/jica_compara_modelo.py` (`resultados/jica_comparacion.txt`, figura `fig_jica_comparison`). ΔS_b = S(fondo) − S(superficie), media de las 11 estaciones: m0000 +0,80, m0001 +0,18, m0002 +0,28 (media de las dos fases; creciente y bajamar casi iguales: +0,77/+0,84, +0,16/+0,20, +0,26/+0,31). **Mediana de los 3 = +0,28 con el nodo más cercano (+0,26 a 300 m) frente al rango observado [3,7; 5,5]; el límite inferior de «contradice» es ½ × 3,7 = 1,85, así que lo contradice por un factor ≈ 7 y las dos versiones de posición coinciden.** Con 10 m en lugar del fondo (solo estaciones con ≥ 10,5 m): +0,68, +0,21, +0,32. El modelo tiene la salinidad del fondo bien (≈ 35,97, frente a 35,9 de JICA a 10 m) y la superficie mucho más salada (35,6–35,8 en la estación 1, frente a 30–32 observado), de modo que la estratificación observada no aparece: coincide con el resultado de los 704 miembros en superficie. No se sabe aún la causa (no hay lluvia, evaporación ni aguas residuales fuera de los tres ríos; abril frente a diciembre; solo 3 miembros). **Las corridas del conjunto no guardan velocidad 3D** (`iof_hydro(16)` es la velocidad promediada en la vertical; la 3D es `iof_hydro(25)` = 0), por lo que (a) no puede ni describirse y (c) sigue «no evaluable»; haría falta una corrida nueva con `iof_hydro(25)` = 1. Falta la ventana de diciembre (X1/X2, `runs/termico`, días 335–365) cuando terminen.
- 2026-11-18 — **CORRECCIÓN de un error mío: la velocidad 3D NO es `iof_hydro(25)`, es `iof_hydro(26)`.** En la fuente de SCHISM (`sample_inputs/param.nml`, versión 09f407e8): (14) = velocidad del viento, (16) = velocidad promediada en la vertical, (25) = `zCoordinates`, (26) = velocidad horizontal 3D `{horizontalVelX,Y}`. Las corridas tienen (25) = 0 y (26) = 0. Las frases «`iof_hydro(25)` = 0 es la velocidad 3D» de este registro (entradas del resultado de (b)) y del commit cccbee8 deben leerse como «(26)»; la conclusión no cambia (sin velocidad 3D guardada, (a) y (c) no evaluables con esas corridas). Para la corrida nueva de velocidad 3D se activarán (26) y también (25) para validar la reconstrucción de las cotas verticales del extractor frente a las reales.
