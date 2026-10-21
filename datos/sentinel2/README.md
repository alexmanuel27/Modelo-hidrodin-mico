# Sentinel-2 → modelo: contrato de entrega

Esta carpeta recibe los productos del proyecto Sentinel-2 (turbidez de la bahía de La Habana) que el modelo
usa para **comparar**, nunca como insumo: la edad del agua en superficie a las 16:00 UTC (`posproceso.py`,
`s2_edad` en cada `resumen.npz`) frente a la persistencia de anomalías de turbidez. Criterio de comparación:
`docs/00_estado_y_plan.md` sección 7 (patrones persistentes, correlación de rangos por píxel, congelado antes
de mirar resultados).

Regla del proyecto: solo datos públicos y replicables; cada dato con URL y fecha de acceso.

## Rejilla del modelo (a la que interpolamos nosotros)

UTM 17N (EPSG:32617), píxel de 20 m, 238 columnas × 252 filas.
Bordes de píxel: E 361 139–365 899, N 2 556 342–2 561 382; centros E 361 149 + 20·i, N 2 556 352 + 20·j
(en `datos/conjunto/posproceso_malla.npz`: `s2_e`, `s2_n`; filas de sur a norte).
**Entregad en vuestra rejilla nativa sin remuestrear**, con la georreferencia explícita; si coincide con esta, mejor.

## Ficheros esperados

| Fichero | Contenido | Formato |
|---|---|---|
| `escenas.csv` | una fila por escena del archivo: `fecha_hora_utc, producto` (nombre completo S2x_MSIxxx_…), `nivel` (L1C/L2A), `url`, `fecha_acceso`, `nubes_pct`, `frac_agua_valida`, `usada` (0/1), `motivo_descarte` | CSV UTF-8 |
| `rejilla.npz` | `persistencia` (fracción de escenas válidas con anomalía positiva por píxel, NaN fuera del agua), `n_validas` (escenas válidas por píxel), `mascara_agua` (uint8), `e`, `n` (centros de píxel, m, EPSG:32617), `umbral_anomalia` y `definicion` (texto) | numpy `.npz` (se lee sin GDAL) |
| `persistencia_anomalias.tif`, `mascara_agua.tif` | lo mismo en GeoTIFF norte-arriba, EPSG:32617, NaN/0 fuera del agua | GeoTIFF (para el repo público) |
| `costa.geojson` | línea de costa / borde de la máscara de agua usada | GeoJSON, EPSG:4326 o 32617 (decirlo) |
| `focos.csv` | focos de vertido o de turbidez identificados: `nombre, E, N, tipo, evidencia` (escenas o fuente pública que lo apoya, con URL) | CSV |
| `anomalias.nc` (opcional) | anomalía por escena (`time, y, x`) para comparar escena a escena | NetCDF-4 CF |

## Metadatos obligatorios (en este README, sección "Procedencia", la rellena el proyecto Sentinel-2)

- Producto y nivel (L1C/L2A), colección/baseline de procesado, portal y fecha de acceso (Copernicus Data Space).
- Corrección atmosférica y algoritmo de turbidez (software, versión, parámetros, referencia bibliográfica).
- Definición exacta de la anomalía (respecto a qué climatología o mediana, umbral) y de "escena válida".
- Periodo cubierto; el modelo simula 2016–2025 (ERA5), así que interesa al menos ese periodo.
- Licencia: datos Copernicus Sentinel de uso libre; productos derivados CC BY 4.0, con la atribución
  "Contains modified Copernicus Sentinel data [años]".

## Procedencia

Entregado el 2026-10-21 por el proyecto Sentinel-2 (repositorio público
https://github.com/alexmanuel27/Vertidos-recurrentes, commit `dca303e`). Todos los ficheros de esta carpeta
salen de `scripts/11_entrega_modelo.py` de ese repositorio, sin pasos a mano. El método está fijado en su
`PROTOCOLO_CONGELADO.md`: preregistro del 15/09/2026 (commit `0eeeecd`) y registro de cambios fechado en su
sección 14.

**Corrección del 2026-10-21.** Se alinea la nomenclatura de las ensenadas con la del modelo: Atarés es el brazo suroeste, Guasabacoa el brazo sur y Marimelena el brazo este (registro de la sección 14 del protocolo). Solo cambian los nombres de los 3 focos exploratorios de `focos.csv`; el resto de ficheros es idéntico byte a byte. Los ficheros actuales salen de `scripts/11_entrega_modelo.py` en el commit `96d2944` de Vertidos-recurrentes.

### Rejilla: no coincide exactamente con la del modelo

Es la rejilla nativa del proyecto, sin remuestrear: UTM 17N (**EPSG:32617**), píxel de **20 m**,
**238 columnas × 253 filas**.

| | Este (m) | Norte (m) |
|---|---|---|
| Bordes de píxel | 361 140 – 365 900 | 2 556 340 – 2 561 400 |
| Centros | 361 150 + 20·i (i = 0…237) | 2 556 350 + 20·j (j = 0…252) |
| Esquina noroeste (origen de los GeoTIFF) | 361 140 | 2 561 400 |

Frente a la rejilla del modelo (centros E 361 149 + 20·i, N 2 556 352 + 20·j, 252 filas):

- los centros están desplazados **+1 m en E y −2 m en N**;
- hay **una fila más al norte** (j = 252, centro N 2 561 390), que la rejilla del modelo no tiene.

La fila j del modelo corresponde a la fila j de esta entrega; la última fila de la entrega sobra.

Orden de los datos:

- `rejilla.npz` y `anomalias.nc`: filas de sur a norte (`n` creciente) y columnas de oeste a este.
- GeoTIFF: norte arriba. Geotransform (361140, 20, 0, 2561400, 0, −20).

Las claves `epsg`, `pixel_m`, `bordes_oeste_sur_este_norte` y `orden_filas` del `.npz` repiten esta
georreferencia.

### Producto, nivel y portal

- **Producto.** Sentinel-2 MSI **Level-1C** (S2MSI1C), tesela **T17QLF**, solo la órbita relativa **R097**.
  La R054 también toca la tesela, pero no cubre la bahía.
- **Satélites.** S2A, S2B y S2C.
- **Baselines de procesado del archivo** (664 productos): N0500 (349; es el reprocesado del archivo antiguo),
  N0510 (191), N0511 (123) y N9906 (1).
- **Baselines de las 113 escenas usadas:** N0500 (62), N0510 (29) y N0511 (22).
- **Portal.** Copernicus Data Space Ecosystem, API OData
  (https://catalogue.dataspace.copernicus.eu/odata/v1/Products). Descargar requiere una cuenta gratuita.
  - Catálogo de productos: consulta del 2026-09-16.
  - Descargas: del 2026-09-16 al 2026-10-03. La fecha de cada producto está en la columna `fecha_acceso`.
  - Nubosidad (`nubes_pct`): consulta del 2026-10-21 con `$expand=Attributes`.
- La `url` de `escenas.csv` es la ficha OData del producto. Añadiendo `/$value` se obtiene la descarga.

### Corrección atmosférica y turbidez

**Corrección atmosférica:** **ACOLITE**, Dark Spectrum Fitting (DSF).

- Código: https://github.com/acolite/acolite, clon en el commit `d61c8de` (`git describe`:
  20260421.0-88-gd61c8de; en los metadatos de salida, «Generic GitHub Clone c2026-09-16»).
- Ajustes no por defecto:
  - `s2_target_res=20`;
  - `dsf_aot_estimate=fixed`: un AOT por escena, calculado sobre la ventana de procesado 23,10–23,21 N,
    82,40–82,28 O;
  - `dsf_residual_glint_correction=True`;
  - `l2w_mask_water_parameters=False`: las banderas no se aplican dentro de ACOLITE, sino después, tal como
    se describe abajo;
  - `l2w_parameters=[tur_dogliotti2015, tur_nechad2009_*, spm_nechad2010_*, rhos_*]`.
- Ajustes que quedan por defecto: LUT ACOLITE-LUT-202110 (MOD1/MOD2, elegida por escena) y datos
  auxiliares GMAO MERRA-2.
- Referencias: Vanhellemont, Q., Ruddick, K. (2018). Remote Sensing of Environment 216, 586–597,
  https://doi.org/10.1016/j.rse.2018.07.015 · Vanhellemont, Q. (2019). Remote Sensing of Environment 225,
  175–192, https://doi.org/10.1016/j.rse.2019.03.010.

**Turbidez (FNU):** Dogliotti et al. (2015), en su implementación de ACOLITE (`TUR_Dogliotti2015`, versión
«blended»).

- Bandas: rojo de 665 nm (B4) cuando ρ_rojo < 0,05 y NIR de 865 nm (B8A) cuando ρ_rojo > 0,07; mezcla
  lineal entre los dos valores.
- Coeficientes: A = 228,1 y C = 0,1641 para el rojo; A = 3078,9 y C = 0,2112 para el NIR.
- En la bahía el 99,8 % de las observaciones válidas tiene T < 16,4 FNU, que es lo que da el algoritmo
  del rojo en su límite ρ_rojo = 0,05. En la práctica, la turbidez de la bahía es la del rojo.
- Referencia: Dogliotti, A.I., Ruddick, K.G., Nechad, B., Doxaran, D., Knaeps, E. (2015). Remote Sensing
  of Environment 156, 157–168, https://doi.org/10.1016/j.rse.2014.09.020.

Las tres referencias se comprobaron contra doi.org el 2026-10-21.

### Escena válida, píxel válido y anomalía

**Máscara de agua** (`mascara_agua`). Es agua el píxel donde la mediana temporal del NDWI supera 0, con dos
condiciones:

- NDWI = (ρ_B3 − ρ_B8)/(ρ_B3 + ρ_B8), calculado sobre las 637 adquisiciones sin los píxeles de nube, cirro
  o fuera de escena;
- solo cuentan las componentes conexas que contienen la bahía (23,133 N 82,333 O) o el mar abierto
  (23,200 N 82,333 O).

**Escena usada** (`usada = 1`). Se toma un solo producto L1C por paso: cuando el tile viene partido, el de
mayor huella en la ventana. Ese producto se usa si cumple las dos condiciones:

- el AOT de ACOLITE es finito;
- al menos el **60 %** del agua de esta ventana tiene píxel válido (`frac_agua_valida`).

Con eso entran **113 de 637 adquisiciones**.

**Píxel válido** en una escena. Tiene que cumplir todo esto:

- es agua y su turbidez es finita;
- tiene sin activar los bits 1–4 de `l2_flags` de ACOLITE: cirros, TOA alto, ρ negativa y fuera de escena;
- ρ(2200 nm) ≤ 0,010, que es el test de bruma;
- está fuera de la máscara de buques: residuo del perfil de adyacencia en SWIR por encima de la mediana
  + 6·MAD de la escena, dilatado 2 píxeles.

**Climatología** (referencia de la anomalía).

- Para cada píxel y estación (seca nov–abr, lluviosa may–oct): mediana y 1,4826·MAD de la turbidez válida,
  calculadas sobre las mismas 113 escenas usadas.
- Un píxel es **evaluable** si tiene ≥ 20 observaciones y MAD > 0.
- Se calculó y se commiteó antes de calcular ninguna anomalía (commit `0dba286`, 2026-10-13).

**Anomalía positiva.** Se cumplen a la vez z_t ≥ **3,5** y z_s ≥ **3,0** (`umbral_anomalia = [3.5, 3.0]`):

- z_t = (T − mediana estacional del píxel) / (1,4826·MAD estacional);
- z_s = (T − mediana del día) / (1,4826·MAD del día), con la mediana y la MAD del día calculadas sobre los
  píxeles válidos de esta ventana.

**`persistencia`** = `n_anomalias` / `n_validas`, donde `n_validas` es el número de escenas usadas en que el
píxel es válido y evaluable.

- Vale NaN fuera del agua y en los 935 píxeles de agua (8 % de 11 287) con `n_validas = 0`.
- Es la «frecuencia de detección por píxel» (E1) del proyecto. No es la «persistencia de sitio» del
  protocolo, que agrupa en celdas de 40 m.

El método de detección preregistrado del proyecto no superó su criterio de falsación 12.2: ningún sitio
recurrente sobrevive al margen de 40 m de costa (protocolo, sección 18). Estos productos se entregan tal
cual, sin ajustar nada después.

### Periodo cubierto

- **Archivo:** 2016-01-15 a 2025-12-28. Son 664 productos L1C y 637 adquisiciones: dos días tienen dos
  satélites.
- **Escenas usadas:** 2017-03-10 a 2025-12-28. Por año: 2017: 6, 2018: 13, 2019: 20, 2020: 12, 2021: 11,
  2022: 14, 2023: 12, 2024: 8, 2025: 17.
- **No hay ninguna escena de 2016.** De los 19 productos de ese año, 17 son el producto elegido de su paso
  y no llegan al 60 % de agua válida (el mejor, 59 %); los otros 2 son trozos sin datos de pasos
  partidos.

### Notas por fichero

- **`escenas.csv`** (664 filas, una por producto L1C del archivo).
  - `fecha_hora_utc` es la hora de adquisición de la tesela según los metadatos L1C (≈ 16:17 UTC).
    Excepción: en los 20 productos sin escena exportada es el inicio del datatake según el catálogo, unos
    10 min antes.
  - `nubes_pct` es la nubosidad de toda la tesela (100 × 100 km) según el catálogo, no la de la bahía.
    Está vacía en el producto que ya no figura en el catálogo.
  - `frac_agua_valida` solo existe para el producto elegido de cada paso.
  - Motivos de descarte:

    | Motivo | Productos |
    |---|---|
    | agua válida < 60 % | 524 |
    | otro producto del mismo paso elegido | 7 |
    | recorte sin datos (blackfill), con la bahía en el otro producto del paso | 19 |
    | 404 en el portal | 1 |

- **`rejilla.npz`.** Se lee con `numpy.load(..., allow_pickle=False)`. Además de las claves del contrato
  trae `n_anomalias`, y `definicion` repite esta sección en una línea.
- **`persistencia_anomalias.tif`** (float32, NoData = NaN) y **`mascara_agua.tif`** (uint8, 1 agua, 0
  tierra). DEFLATE, EPSG:32617.
- **`costa.geojson`.** Polígonos del agua de la máscara en **EPSG:32617**, declarado en el miembro `crs`;
  no es RFC 7946. Su borde es el borde de la máscara de agua usada.
- **`focos.csv`** (E y N en EPSG:32617). Tres clases:
  1. Los 2 sitios recurrentes preregistrados. Los dos caen **fuera** de esta ventana: costa al este y
     bocana.
  2. 3 focos permanentes **exploratorios** (familia E3, definida después de ver los datos).
  3. 4 desembocaduras de cauces de OpenStreetMap: el último vértice de un `waterway` cae dentro de la
     ventana y a ≤ 60 m del agua. Consulta Overpass del 2026-10-17.

  Los focos satelitales están pendientes de verificación de campo.
- **`anomalias.nc`** (NetCDF-4, CF-1.8; dimensiones `time` = 113, `y` = 253, `x` = 238).
  - Variables `z_t` (float32, NaN donde el píxel no es válido o no es evaluable) y `anomalia_positiva`
    (uint8: 1 sí, 0 no, 255 sin dato).
  - `producto`: el L1C de cada tiempo.
  - Mapeo de rejilla en `crs`.

### Licencia y atribución

- **Productos derivados:** CC BY 4.0. Atribución: **«Contains modified Copernicus Sentinel data
  [2017–2025]»**. Son los años de las escenas usadas.
- **Datos Sentinel:** de uso libre y gratuito según la política de datos de Copernicus.
- **Filas OpenStreetMap de `focos.csv`:** © colaboradores de OpenStreetMap, licencia ODbL.
