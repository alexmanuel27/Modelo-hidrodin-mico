# Havana Bay ensemble model — public data, configuration and results

Everything needed to reproduce *"What can be known about flushing in a bay without data? Robust and fragile conclusions from a public-data ensemble model of Havana Bay, Cuba"* (Rivera et al., in prep., *Environmental Modelling & Software*).

**Rule of the study:** every input is public and freely available. Sources, URLs, access dates, licences and SHA-256 checksums: `DATA_SOURCES.md` and `datos/*/descargas.tsv`.

## Contents

| Folder | Content | Licence |
|---|---|---|
| `datos/batimetria/sondeos/` | **2640 depth soundings digitised** from U.S. Hydrographic Office chart 307 (Spanish surveys to 1879 and to 1887), in WGS84, with the 1887→1879 registration | CC BY 4.0 |
| `datos/batimetria/superficies/` | Bathymetric volumes per chart and dredging state | CC BY 4.0 |
| `datos/batimetria/fuentes/` | Redistributable inputs: GEBCO 2026 subset, OpenStreetMap coastline and rivers (Overpass snapshots), chart metadata, download log | GEBCO: public domain; OSM: **ODbL** |
| `datos/malla/` | SCHISM mesh (`hgrid.gr3`, `hgrid.ll`), 4832 nodes | CC BY 4.0 + ODbL (coastline © OpenStreetMap contributors) |
| `datos/marea/` | EOT20 tidal harmonics around the bay | CC BY 4.0 (EOT20, Hart-Davis et al. 2021) |
| `datos/forzamiento/sflux/` | ERA5 atmospheric forcing converted to SCHISM `sflux` | Copernicus licence (contains modified Copernicus Climate Change Service information) |
| `datos/conjunto/` | Saltelli ensemble design (640 members) and post-processing weights (zones, Sentinel-2 grid, channel section) | CC BY 4.0 |
| `resultados/` | Analytical tidal-prism control; ensemble summaries and Sobol indices (when available) | CC BY 4.0 |
| `scripts/` | Full processing chain, from downloads to post-processing | MIT |
| `cluster/` | SCHISM build and Slurm templates for CÉCI clusters | MIT |
| `docs/figuras/` | Working figures | CC BY 4.0 |

Not included (licence or size), but downloaded by the scripts: the chart scans (Harvard GeoTIFF, Leventhal JPEG), the harbour-pilot PDF and the JICA (2004) report (cited, copyrighted), raw ERA5 (Copernicus CDS account), FES2022 (free AVISO+ account), SCHISM source code (Apache 2.0, commit 09f407e8).

## Reproducing

1. Environment: `scripts/instalar_entorno_mac.sh` (conda env `bahia` + SCHISM build), or `cluster/compilar_schism_ceci.sh` on a Slurm cluster.
2. Inputs: `scripts/batimetria/01_descargar.sh`; tide: `scripts/marea_eot20.py` (no account) or `scripts/marea_fes2022.py`.
3. Bathymetry and mesh: `scripts/batimetria/07_superficies.py` → `08_batimetria_conjunto.py` → `09_malla.py` (outputs already included).
4. One SCHISM case: `scripts/caso_real.py`; ensemble: `scripts/conjunto.py diseno 64` → `generar` → `runs/conjunto/correr_array.sh`.
5. Post-processing per member: `scripts/posproceso.py`.

Folder and variable names are in Spanish (*datos* = data, *malla* = mesh, *marea* = tide, *conjunto* = ensemble, *sondeos* = soundings, *resultados* = results).

## Citation

See `CITATION.cff`. Please also cite the original data sources listed in `DATA_SOURCES.md`.
