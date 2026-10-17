# Modelo hidrodinámico — Bahía de La Habana (repo de trabajo)

Scripts, datos, resultados y notas del modelo SCHISM y del conjunto de simulaciones del artículo
*"What can be known about flushing in a bay without data?"* (Environmental Modelling & Software).
**Regla:** solo datos públicos, cada uno con URL y fecha (`docs/procedencia_datos.md`).
El manuscrito vive en otro repo (`publication plan/modelo-hidrodin-mico`); el puente es `docs/articulo/`.

## Dónde está cada cosa

| Carpeta | Qué hay |
|---|---|
| `docs/articulo/` | **Para escribir el paper:** `cifras.md` (cada número, su fuente y si está al día), `figuras.md` (figuras previstas y estado) |
| `docs/00_estado_y_plan.md` | Bitácora técnica completa (decisiones, resultados, errores) |
| `docs/procedencia_datos.md` | Tabla de datos públicos (→ tabla 1 del artículo) |
| `docs/figuras/` | Figuras de trabajo (en español) |
| `datos/` | Insumos: `batimetria/` (fuentes, sondeos digitalizados), `malla/`, `conjunto/` (diseño Saltelli, pesos del posproceso), `marea/`, `forzamiento/` (ERA5, fuera de git) |
| `scripts/` | Cadena de procesado (abajo) |
| `cluster/` | Inventarios, compilación de SCHISM y costes en CÉCI (NIC5, Lemaitre4) |
| `resultados/` | Resultados pequeños versionados (control analítico) |
| `runs/` | Casos generados y salidas (fuera de git; se regeneran) |

## Cadena de procesado (en orden)

1. **Batimetría** — `scripts/batimetria/`: `01_descargar.sh` (todas las fuentes, con fecha y sha256) → `02`–`04` digitalización de los sondeos de 1879 → `05`–`06` registro y comparación con 1887 → `07_superficies.py` → `08_batimetria_conjunto.py` (miembros: carta, dragado, error, datum) → `09_malla.py`.
2. **Forzamiento** — `descargar_era5.py` → `era5_a_sflux.py`; `marea_fes2022.py` (FES2022, cuenta AVISO).
3. **Control analítico** — `prisma_marea.py` → `resultados/prisma_marea.*`.
4. **Un caso SCHISM** — `caso_real.py` (variables: CARTA, ALFA, SEMILLA, DATUM, CD, VFAC, VROT, MFAC, MAREA, RIOS, QFAC, NWS…); revisión rápida con `revisar_real.py`.
5. **Conjunto** — `conjunto.py diseno 64` → `generar` → `runs/conjunto/correr_array.sh` (array de Slurm en Lemaitre4).
6. **Posproceso por miembro** — `posproceso_malla.py` (una vez; zonas de `zonas.py`) → `posproceso.py` (en el cluster, dentro del array).
7. **Análisis del conjunto, Sobol y figuras del artículo** — por hacer.

Histórico (prueba idealizada del 30-sep, no forma parte de la cadena): `caso_prueba.py`, `revisar_prueba.py`, `diagnostico_prueba.py`, `diagnostico_forzamiento.py`. Entorno del Mac: `instalar_entorno_mac.sh`.
