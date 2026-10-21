# Procedencia de los datos de entrada (regla: solo datos públicos)

Cada insumo del modelo con fuente, URL, fecha de acceso y licencia. Base para las secciones
"Public data only" y "Software and data availability" del artículo. Las descargas con
script registran fecha y sha256 en `datos/*/fuentes/descargas.tsv`.

| Insumo | Fuente | URL | Acceso | Licencia | Estado |
|---|---|---|---|---|---|
| Viento, presión, T, humedad, radiación, precipitación (2016–2025, horario) | ERA5 hourly single levels, Copernicus CDS (Hersbach et al., 2020) | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels | 27–30 sep 2026 | Licencia Copernicus (libre, con cita) | Descargado y verificado |
| Batimetría (carta 1889) | U.S. Hydrographic Office, "Harbor of Havana: from the most recent Spanish surveys to 1879" (J.C.P. de Krafft; 1.ª ed. ene-1882, ed. 1889), escala ~1:8 000; GeoTIFF Harvard (el metadato dice NAD27 Cuba Norte, pero el archivo viene en WGS84 geográfico; RMS georref. 18,3 m) + metadato FGDC | https://hgl.harvard.edu/catalog/harvard-g4924-h3-1889-u5 | 2 oct 2026 | Acceso público (Harvard) | `fuentes/carta_1889_harvard.tif` (640 MB, fuera de git) y `_fgdc.xml` |
| Batimetría (carta 1898) | U.S. Hydrographic Office, chart n.º 307, "West Indies, Cuba, harbor of Havana: from the most recent Spanish surveys to 1887", ed. 1898 (Boston Public Library, G9096.P5 svar .U55 no. 307 1898), Leventhal Map & Education Center | https://collections.leventhalmap.org/search/commonwealth:g445ht01p (imagen: IIIF https://iiif.digitalcommonwealth.org/iiif/2/commonwealth:0c487z874) | pendiente | Sin restricciones conocidas | Por descargar (script) |
| Canal (1530 m, 220–330 m, 12,8 m) y calados de muelles | Prácticos del puerto de La Habana, publicado por Cubadebate (2018) | http://media.cubadebate.cu/wp-content/uploads/2018/09/puerto_de_la_habana-PRACTICOS.pdf | 2 oct 2026 (`descargas.tsv`) | Documento público con derechos de autor: se cita, no se redistribuye | Descargado; cifras usadas en `08_batimetria_conjunto.py` |
| Batimetría exterior (+ TID) | GEBCO 2026 Global Grid (GEBCO Compilation Group 2026) | https://download.gebco.net/ | 2 oct 2026 | Dominio público, con cita (términos en `fuentes/gebco_terminos_uso.pdf`) | Descargado (`gebco_habana*.nc`) |
| Línea de costa actual, muelles y espigones | OpenStreetMap (ways `natural=coastline`, `man_made=pier/breakwater/groyne/quay`), instantánea vía Overpass API | https://overpass-api.de/api/interpreter (consulta en `scripts/batimetria/01_descargar.sh`) | ver `datos/batimetria/fuentes/descargas.tsv` | ODbL (© colaboradores de OpenStreetMap) | Se contrastará con la máscara de agua Sentinel-2 (protocolo del repo de Sentinel-2) |
| Marea de contorno | FES2022b, `ocean_tide_extrapolated`, 11 constituyentes (AVISO+; doi:10.24400/527896/A01-2024.004) | ftp://ftp-access.aviso.altimetry.fr/auxiliary/tide_model/fes2022b/ocean_tide_extrapolated/ (el THREDDS no resuelve en DNS) | 20–21 oct 2026 (`datos/marea/descargas.tsv`) | Cuenta gratuita AVISO+; licencia AVISO (no se redistribuye el extracto hasta confirmar la licencia) | `scripts/marea_fes2022.py` → `datos/marea/fes2022_habana.json` |
| Marea de contorno (descartada) | TPXO10-atlas (OSU) | https://www.tpxo.net/ | — | Requiere registro | No se usa: EOT20 la sustituye sin registro |
| Modelo | SCHISM `develop`, commit 09f407e8 | https://github.com/schism-dev/schism | 27 sep 2026 | Apache 2.0 | Compilado |
| Caudales de ríos (Luyanó 1,33; Martín Pérez 0,72; Tadeo 0,09 m³/s) | JICA / Nihon Suido Consultants (2004), *Estudio del Desarrollo del Alcantarillado y el Drenaje Pluvial en la Cuenca Tributaria de la Bahía de La Habana*, Informe final vol. IV, tabla 1.1 (datos CIMAB ago-2002) | https://openjicareport.jica.go.jp/pdf/11767225.pdf | ver `datos/batimetria/fuentes/descargas.tsv` | Público | Una sola campaña; no hay aforos permanentes → QFAC en el conjunto |
| Desembocaduras de los ríos | OpenStreetMap (`waterway`), vía Overpass | https://overpass-api.de/ | ver `descargas.tsv` | ODbL | `osm_rios_habana.json` |
| Marea de contorno (sin registro; alternativa a FES y dimensión del conjunto) | EOT20, DGFI-TUM (Hart-Davis et al. 2021, ESSD 13:3869), 9 constituyentes | https://www.seanoe.org/data/00683/79489/ (doi:10.17882/79489) | ver `datos/marea/descargas.tsv` | CC BY 4.0, descarga directa | `scripts/marea_eot20.py` → `datos/marea/eot20_habana.json` |

Opcionales, solo para comparación (nunca insumo): mareógrafo HABANA (PSMSL 2363),
batimetría CUJAE (ADCIRC 2016), levantamientos GEOCUBA.
