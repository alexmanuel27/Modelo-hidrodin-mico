# Contexto del Cowork técnico

*Trasladado desde el Project "modelo-hidrodinamico" (chat del artículo) el 27-sep-2026.
El chat del artículo ya no guarda contexto técnico: la referencia es este repo.*

## Reparto
- **Este repo** (`repos/Modelo-hidrodin-mico`, remoto `github.com/alexmanuel27/Modelo-hidrodin-mico`):
  scripts, datos, resultados, cluster y notas técnicas. Se trabaja desde el Cowork técnico.
- **Repo del artículo** (`repos/publication plan/modelo-hidrodin-mico`): solo `articulo/`
  (elsarticle, Environmental Modelling & Software). Desde aquí solo se copian figuras y cifras
  finales a `articulo/figuras/`.

## Decisiones técnicas vigentes
- Modelo: **SCHISM** (malla no estructurada, LSC², módulo AGE, partículas). TELEMAC solo si CÉCI
  lo tiene instalado o un colaborador lo usa.
- Diseño: conjunto 3D de cientos de miembros, muestreo Sobol sobre batimetría, fricción, viento,
  marea de contorno, caudales y flotabilidad de los vertidos.
  Orden: batimetría → prisma → 2D base → 3D → partículas → conjunto.
- Sin trabajo de campo (sin sensor, muestras ni fotos).
- Validación solo con datos de terceros: mareógrafo HABANA (PSMSL 2363; serie horaria o, si no,
  constantes armónicas) y persistencia de turbidez de Sentinel-2 en la misma rejilla
  (UTM 17N, 20 m, E 361139–365896, N 2556342–2561392; instantáneas a ~16:00 UTC).
- Marea de contorno: FES2022. TPXO solo si FES falla.
- Cluster: CÉCI. NIC5/Lemaitre4 (2 días por trabajo → encadenar con hotstart) para el 3D y el
  conjunto; Hercules2 (15 d) / Dragon2 (21 d) para trabajos largos con pocos núcleos.

## Estado (27-sep-2026)
- Entorno conda `bahia` creado en el Mac (gfortran 15.3, mpich, netcdf-fortran 4.6.4) —
  ver `cluster/entorno_resumen.txt`.
- Compilación de SCHISM: sin registros todavía (`schism_cmake.log` / `schism_make.log` no existen).
- ERA5: cuenta y `~/.cdsapirc` listos; descarga no lanzada.
- FES2022: cuenta AVISO en trámite.
- Batimetría: pedida a la CUJAE (ADCIRC 2016); respaldo carta UKHO BA 414 (Weilbach 530 DKK,
  Bookharbour 48,30 £).
- Mareógrafo HABANA: pedir vía carta institucional / CIMAB a GEOCUBA Estudios Marinos.
- CÉCI: acceso pendiente del administrador.
- Push de este repo: **pendiente** (el remoto sigue vacío).

## Limitaciones de las sesiones Cowork (comprobadas)
- El shell del dispositivo no tiene red ni compiladores; la app Terminal solo admite clics.
  Instalaciones, descargas y push los ejecuta Alex con los comandos que se le den.
