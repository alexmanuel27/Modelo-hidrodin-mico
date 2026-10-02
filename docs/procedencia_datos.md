# Procedencia de los datos de entrada (regla: solo datos públicos)

Cada insumo del modelo con fuente, URL, fecha de acceso y licencia. Base para las secciones
"Public data only" y "Software and data availability" del artículo. Las descargas con
script registran fecha y sha256 en `datos/*/fuentes/descargas.tsv`.

| Insumo | Fuente | URL | Acceso | Licencia | Estado |
|---|---|---|---|---|---|
| Viento, presión, T, humedad, radiación, precipitación (2016–2025, horario) | ERA5 hourly single levels, Copernicus CDS (Hersbach et al., 2020) | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels | 27–30 sep 2026 | Licencia Copernicus (libre, con cita) | Descargado y verificado |
| Batimetría (carta 1889) | U.S. Hydrographic Office, "Havana and Harbor, Cuba" (levant. hasta 1879), escaneo georreferenciado, Harvard Map Collection | https://hgl.harvard.edu/catalog/harvard-g4924-h3-1889-u5 | pendiente | Acceso público (Harvard) | Por descargar (manual) |
| Batimetría (carta 1898) | U.S. Hydrographic Office, "West Indies, Cuba, harbor of Havana: from the most recent Spanish surveys to 1887", Leventhal Map & Education Center | https://collections.leventhalmap.org/search/commonwealth:g445ht01p | pendiente | Sin restricciones conocidas | Por descargar (script) |
| Canal (1530 m, 220–330 m, 12,8 m) y calados de muelles | Prácticos del puerto de La Habana, publicado por Cubadebate (2018) | http://media.cubadebate.cu/wp-content/uploads/2018/09/puerto_de_la_habana-PRACTICOS.pdf | pendiente | Documento público | Por descargar (script) |
| Batimetría exterior | GEBCO_2024 Grid | https://download.gebco.net/ | pendiente | Dominio público (GEBCO) | Por descargar (manual) |
| Línea de costa | Máscara de agua Sentinel-2 del protocolo congelado (Copernicus Sentinel-2 L2A) | — | — | Copernicus (libre) | Por localizar en el repo de Sentinel-2 |
| Marea de contorno | FES2022 (AVISO+) | https://www.aviso.altimetry.fr/ | — | Registro gratuito | Cuenta en trámite |
| Marea de contorno (alternativa y dimensión del conjunto) | TPXO10-atlas (OSU) | https://www.tpxo.net/ | — | Gratuito uso académico | Por pedir |
| Modelo | SCHISM `develop`, commit 09f407e8 | https://github.com/schism-dev/schism | 27 sep 2026 | Apache 2.0 | Compilado |

Opcionales, solo para comparación (nunca insumo): mareógrafo HABANA (PSMSL 2363),
batimetría CUJAE (ADCIRC 2016), levantamientos GEOCUBA.
