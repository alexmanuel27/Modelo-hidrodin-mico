# Métricas y conclusiones del conjunto: protocolo (BORRADOR, 27-oct-2026)

> **Estado: borrador para que Alex lo apruebe.** Se congela con fecha y hash **antes** de bajar ningún resultado del
> conjunto de 704 miembros (lanzado el 27-oct, arrays 8018180/8018181). Lo implementa `scripts/analisis_conjunto.py`.
> Cambios posteriores, solo en el registro fechado del final.

## Por qué cambia la métrica

El plan usaba P(edad > 30 d). En los experimentos de mecanismo (`docs/resultados_mecanismo.md`), con ríos y densidad
la edad media de la bahía es ~7 d. Un único umbral de 30 d quedaría casi siempre en 0 y no informaría. Para no elegir
un umbral a la vista de los datos, se fijan ahora **varios umbrales** y se informan todos.

## Métricas por miembro (últimos 30 días de los 120; `posproceso.py`)

- Edad media del agua (ponderada por volumen) por zona: canal, cuenca, Marimelena, Guasabacoa, Atarés y bahía.
  También sus percentiles 10/50/90 por nodo.
- Fracción de volumen y probabilidad de superar **7, 14 y 30 días** (por zona y, en superficie, en mapa).
  Elección de los umbrales:
  - 7 d: el orden de magnitud de la edad con densidad en el miembro central;
  - 14 d: un ciclo de sicigias a cuadratura;
  - 30 d: el umbral del plan original.
- Edad en superficie y en el fondo del canal (firma de la circulación estuarina).
- Caudal **bruto** por la sección del canal. El caudal **neto** no se usa como resultado: su error es de ±6 m³/s
  (experimentos de mecanismo).
- Fracción de agua dulce en superficie.

## Equilibrio

- Un miembro está **en equilibrio** si la edad media de la bahía crece ≤ 0,05 d por día en sus últimos 10 días.
- Todo se informa con todos los miembros válidos y, aparte, solo con los que están en equilibrio.
- Si más del 10 % no llega al equilibrio, esos miembros se alargan (más tramos con hotstart) antes de cerrar resultados.

## Conclusiones que se ponen a prueba (bloques A y B, 2N = 128 miembros)

| | Conclusión |
|---|---|
| C1 | Orden canal < cuenca < Guasabacoa < Atarés (edad media) |
| C2 | Atarés más vieja que el canal |
| C3 | Marimelena más vieja que la cuenca |
| C4 | Guasabacoa y Atarés más viejas que la cuenca |
| C5 | Edad media de la bahía < 30 d |
| C6 | Edad media de la bahía < 120 d (los "~4 meses" de JICA 2004) |
| C7 | En el canal, el agua de superficie es más vieja que la del fondo (circulación estuarina) |
| P | P(edad de la bahía > 7 / 14 / 30 d) |
| C8 | Parámetro con mayor índice total de Sobol en la edad de la bahía (se informa, no se clasifica) |

**Regla de clasificación:**

- **robusta:** se cumple en ≥ 90 % de los miembros;
- **frágil:** entre el 10 % y el 90 %;
- **rechazada:** ≤ 10 %.

Los índices de Sobol se dan siempre con su IC 95 % (bootstrap). Con N = 64 su error es de ~0,1 en ST y ~0,2 en S1.

## Lo que el conjunto no cubre (se declara en el artículo)

- Mezcla vertical, número de niveles y flujo de calor. Se prueban aparte, en los 5 experimentos de robustez del miembro
  central (`conjunto.py robustez`).
- Evaporación y precipitación: no están en el modelo (SCHISM pide recompilar con PREC_EVAP). E − P neta del orden de
  0,1 m³/s en la estación seca (estimación gruesa, sin fuente todavía: ~70 mm/mes sobre 5 km²), ~5 % del caudal de los ríos.
- Variabilidad interanual: el conjunto simula enero–abril de 2016.

## Registro de cambios

*(vacío)*
