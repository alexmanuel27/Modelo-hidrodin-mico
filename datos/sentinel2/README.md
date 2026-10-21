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

*(pendiente de entrega)*
