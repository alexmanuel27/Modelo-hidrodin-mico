# Modelo-hidrodinámico — Bahía de La Habana (repo de trabajo)

Material de trabajo del modelo: scripts, datos, resultados y notas.
El artículo vive en otro repo: `publication plan/modelo-hidrodin-mico`.

- `docs/00_estado_y_plan.md` — estado, prisma de marea, cluster, elección de modelo, riesgos
- `docs/paso2_forzamiento.md` — cuentas y datos de forzamiento (ERA5, FES2022)
- `docs/carta_solicitud_batimetria.md` — borrador de solicitud de datos
- `scripts/prisma_marea.py` — control analítico → `resultados/`
- `scripts/instalar_entorno_mac.sh` — miniforge + entorno `bahia` + compilación de SCHISM
- `scripts/descargar_era5.py` — ERA5 horario 2016–2025 → `datos/forzamiento/era5/`
- `cluster/inventario.sh` — ejecutar en el nodo de login de CÉCI

Orden: batimetría → prisma → 2D base → 3D → partículas → conjunto.
