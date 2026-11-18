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
