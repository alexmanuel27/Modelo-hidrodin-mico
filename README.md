# Modelo hidrodinámico — Bahía de La Habana (repo de trabajo)

Scripts, datos, resultados y notas del modelo SCHISM y del conjunto de simulaciones del artículo
*"What can be known about flushing in a bay without data?"* (Environmental Modelling & Software).
**Regla:** solo datos públicos, cada uno con URL y fecha (`docs/procedencia_datos.md`).
El manuscrito vive en otro repo (`publication plan/modelo-hidrodin-mico`); el puente es `docs/articulo/`.

## Dónde está cada cosa

| Carpeta | Qué hay |
|---|---|
| `resumen.md` / `resumen.pdf` | Resumen en español para el tutor (21-oct; anterior a los resultados de mecanismo, robustez y Sentinel-2) |
| `docs/articulo/` | **Para escribir el paper (empezar por su `README.md`):** estado, qué está viejo en `main.tex`, `secciones/` (hechos y cifras por sección), `cifras.md` (cada número, su fuente y si está al día), `figuras.md` |
| `docs/protocolo_*.md` | Protocolos congelados antes de ver resultados: comparación con Sentinel-2 (21-oct) y métricas del conjunto (27-oct) |
| `docs/resultados_*.md` | Resultados cerrados: experimentos de mecanismo y de robustez |
| `docs/00_estado_y_plan.md` | Bitácora técnica completa (decisiones, resultados, errores) |
| `docs/procedencia_datos.md` | Tabla de datos públicos (→ tabla 1 del artículo) |
| `docs/figuras/` | Figuras de trabajo (en español) |
| `datos/` | Insumos: `batimetria/` (fuentes, sondeos digitalizados), `malla/`, `conjunto/` (diseño Saltelli, pesos del posproceso), `marea/` (EOT20, FES2022), `forzamiento/` (ERA5 fuera de git; SST OISST versionada), `sentinel2/` (entrega del estudio Sentinel-2) |
| `scripts/` | Cadena de procesado (abajo) |
| `cluster/` | Inventarios, compilación de SCHISM y costes en CÉCI (NIC5, Lemaitre4) |
| `resultados/` | Resultados pequeños versionados (control analítico, comparación con Sentinel-2) |
| `runs/` | Casos generados y salidas (fuera de git; se regeneran) |
| `publicacion/` | Plantillas del repo público (README en inglés, fuentes y licencias, CITATION, Zenodo); se arma con `scripts/preparar_publicacion.sh` |

## Cadena de procesado (en orden)

1. **Batimetría** — `scripts/batimetria/`: `01_descargar.sh` (todas las fuentes, con fecha y sha256) → `02`–`04` digitalización de los sondeos de 1879 → `05`–`06` registro y comparación con 1887 → `07_superficies.py` → `08_batimetria_conjunto.py` (miembros: carta, dragado, error, datum) → `09_malla.py`.
2. **Forzamiento** — `descargar_era5.py` → `era5_a_sflux.py`; `marea_eot20.py` (EOT20, la que usa el conjunto) y `marea_fes2022.py` (FES2022, solo comparación); `descargar_sst.sh` (SST OISST, solo robustez).
3. **Control analítico** — `prisma_marea.py` → `resultados/prisma_marea.*`.
4. **Un caso SCHISM** — `caso_real.py` (variables: CARTA, ALFA, SEMILLA, DATUM, CD, VFAC, VROT, MFAC, MAREA, RIOS, QFAC, NWS…); revisión rápida con `revisar_real.py`.
5. **Conjunto** — `conjunto.py diseno 64` (704 miembros, 9 parámetros) → `generar` → `runs/conjunto/lanzar_trabajadores.sh` (trabajadores de Slurm en Lemaitre4 que avanzan cada miembro en tramos de 20 d con hotstart; `correr_array.sh` hace un tramo). Experimentos aparte: `conjunto.py mecanismo` y `conjunto.py robustez`. Vigilancia: `cluster/diagnostico_conjunto.sh`.
6. **Posproceso por miembro** — `posproceso_malla.py` (una vez; zonas de `zonas.py`) → `posproceso.py` (en el cluster, dentro del array).
7. **Análisis** — `analisis_conjunto.py` (Sobol de Jansen, conclusiones robustas/frágiles según el protocolo congelado) y `comparacion_s2.py` (Sentinel-2, protocolo congelado); diagnósticos: `comparar_tramos.py`, `diag_caudal.py` (+ `cluster/hf_caudal.sh`). Figuras finales del artículo (`figuras_articulo.py`): por hacer.

Histórico (prueba idealizada del 30-sep, no forma parte de la cadena): `caso_prueba.py`, `revisar_prueba.py`, `diagnostico_prueba.py`, `diagnostico_forzamiento.py`. Entorno del Mac: `instalar_entorno_mac.sh`.
