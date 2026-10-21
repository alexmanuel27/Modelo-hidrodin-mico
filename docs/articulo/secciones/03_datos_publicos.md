# 3. Solo datos públicos (tabla 1)

Fuente detallada con URL, fecha de acceso, licencia y sha256: `../../procedencia_datos.md` y `datos/*/descargas.tsv`.

| Insumo | Fuente | Papel en el modelo |
|---|---|---|
| Batimetría de la bahía | U.S. H.O. carta n.º 307 *Harbor of Havana*: ed. 1889 (levantamientos españoles hasta 1879, GeoTIFF de Harvard) y ed. 1898 (hasta 1887, Leventhal Map Center); 1126 + 1514 sondeos digitalizados | dimensión del conjunto (carta, error, datum) |
| Canal y calados | Prácticos del puerto de La Habana (2018) | control (canal 12,8 m; canales de acceso 9,75–11,58 m) → estado de dragado |
| Batimetría exterior | GEBCO 2026 Grid | fuera de los sondeos |
| Costa | OpenStreetMap `natural=coastline` (2026-10-13, ODbL) | fija (**no** Sentinel-2) |
| Ríos: desembocaduras | OpenStreetMap `waterway` (2026-10-17) | fuentes del modelo |
| Ríos: caudales | JICA 2004, tabla 1.1 (CIMAB 2002) | caudal base × factor |
| Atmósfera | ERA5 horario 2016–2025 (viento 10 m, presión, T y rocío 2 m, radiación, precipitación) | forzamiento; viento ×0,8–1,2 y ±15° |
| Marea | FES2022b (AVISO+, registro gratuito; doi:10.24400/527896/A01-2024.004) y **EOT20** (DGFI-TUM, Hart-Davis et al. 2021, doi:10.17882/79489, CC BY 4.0, **sin registro**) | borde abierto; dos modelos |
| Modelo | SCHISM, commit 09f407e8, módulo AGE | — |

Nota: ninguna fuente exige convenio, compra ni contacto personal. FES requiere una cuenta gratuita; EOT20 permite replicar todo sin ella.
