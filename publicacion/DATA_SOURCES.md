# Data sources

| Input | Source | Access | Licence | In this repository |
|---|---|---|---|---|
| Bathymetry inside the bay (Spanish surveys to 1879) | U.S. Hydrographic Office, *Harbor of Havana* chart 307, 1889 edition — Harvard Map Collection GeoTIFF, https://hgl.harvard.edu/catalog/harvard-g4924-h3-1889-u5 | 2026-10-02 | Public domain (U.S. Government work, 1889) | digitised soundings + FGDC metadata; scan downloaded by `01_descargar.sh` |
| Bathymetry inside the bay (surveys to 1887) | U.S.H.O. chart 307, 1898 edition — Leventhal Map & Education Center, Boston Public Library, https://collections.leventhalmap.org/search/commonwealth:g445ht01p | 2026-10-02 | Public domain | digitised soundings + IIIF manifest; image downloaded by script |
| Entrance channel and berth depths | Prácticos del puerto de La Habana (2018), published by Cubadebate, http://media.cubadebate.cu/wp-content/uploads/2018/09/puerto_de_la_habana-PRACTICOS.pdf | 2026-10-02 | © publisher; cited, not redistributed | values used in `08_batimetria_conjunto.py` |
| Offshore bathymetry | GEBCO Compilation Group (2026) GEBCO 2026 Grid, https://download.gebco.net/ | 2026-10-02 | Public domain, attribution required | subset `gebco_habana*.nc` |
| Coastline | OpenStreetMap `natural=coastline`, Overpass API snapshot | 2026-10-13 | ODbL, © OpenStreetMap contributors | `osm_costa_habana.json` |
| River mouths | OpenStreetMap `waterway`, Overpass API snapshot | 2026-10-17 | ODbL, © OpenStreetMap contributors | `osm_rios_habana.json` |
| River discharges (Luyanó 1.33, Martín Pérez 0.72, Tadeo 0.09 m³ s⁻¹) | JICA / Nihon Suido Consultants (2004), *Estudio del Desarrollo del Alcantarillado y el Drenaje Pluvial en la Cuenca Tributaria de la Bahía de La Habana*, final report vol. IV, table 1.1 (CIMAB data, Aug 2002), https://openjicareport.jica.go.jp/pdf/11767225.pdf | 2026-10-17 | © JICA; cited, not redistributed | values in `scripts/caso_real.py` |
| Atmosphere (hourly, 2016–2025) | ERA5 hourly data on single levels (Hersbach et al. 2020), Copernicus Climate Data Store | 2026-09-27/30 | Copernicus licence, attribution required | converted `sflux` files |
| Tide (no account needed) | EOT20 (Hart-Davis et al. 2021, doi:10.17882/79489), SEANOE | 2026-10-19 | CC BY 4.0 | harmonics extract `eot20_habana.json` |
| Tide (alternative) | FES2022b (doi:10.24400/527896/A01-2024.004), AVISO+ | 2026-10-20/21 | AVISO+ licence (free account) | not redistributed; `scripts/marea_fes2022.py` |
| Hydrodynamic model | SCHISM, https://github.com/schism-dev/schism, commit 09f407e8 | 2026-09-27 | Apache 2.0 | not included |

SHA-256 checksums of every downloaded file: `datos/batimetria/fuentes/descargas.tsv`, `datos/marea/descargas.tsv`.

Required attributions: "Contains modified Copernicus Climate Change Service information (2026)"; "© OpenStreetMap contributors, ODbL"; "GEBCO Compilation Group (2026) GEBCO 2026 Grid".
