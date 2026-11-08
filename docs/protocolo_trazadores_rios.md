# Destino del agua de cada río (figura 8): protocolo de trazadores — CONGELADO (aprobado por Alex el 8-nov-2026)

> **Estado: congelado el 8-nov-2026, aprobado por Alex.** El texto es el del commit que lleva este cambio; ningún caso se
> había corrido. Cambios posteriores, solo en el registro fechado del final. Decisión de Alex del 8-nov: trazador por río (no partículas) y la figura 8 se
> mantiene; objetivo: el menor número posible de conclusiones frágiles.
>
> **Lo que ya se ha visto antes de redactarlo** (declararlo): el borrador `runs/borradores/fig8_borrador_dulce.png`
> (agua de río en superficie, los tres ríos juntos, miembro central, días 90–120) y el tiempo de renovación del agua dulce
> total (1,8–2,0 d, `scripts/renovacion_dulce.py`). En ese borrador, Atarés recibe poca agua de río y Tadeo apenas se nota.

## Qué se mide

Tres trazadores pasivos y conservativos (sin efecto sobre la densidad), uno por río: entran con concentración 1 con el
caudal de su río y 0 con los otros dos; mar abierto y condición inicial, 0. La concentración C_i en un punto es la fracción
del agua que viene del río i.

Por río y por caso, en los **últimos 30 de los 120 días** (como el protocolo de métricas):

- **T_i = M_i / Q_i**: tiempo de renovación del agua del río i (M_i = volumen de agua del río i en la bahía).
- **Fracción media de agua del río i en cada zona** (canal, cuenca, Marimelena, Guasabacoa, Atarés), ponderada por
  volumen, y en superficie y fondo por separado.
- **Mapas** de C_i en superficie y fondo.
- **Equilibrio:** M_i crece ≤ 1 % de su media por día en los últimos 10 días.

**Control (no es conclusión):** la suma de los tres trazadores debe reproducir el agua dulce de la salinidad (1 − S/36):
diferencia del inventario de la bahía < 5 %. Si no se cumple, no se usa ningún resultado hasta entender por qué.

## Conclusiones que se ponen a prueba

| | Conclusión |
|---|---|
| R1 | El agua de cada río se renueva en menos de 7 días (T_i < 7 d; umbral del protocolo de métricas) |
| R2 | El agua de los ríos (los tres sumados) es menos fracción del volumen de Atarés que del de Guasabacoa |
| R3 | La mayor parte del agua del Luyanó y del Martín Pérez que hay en la bahía está en Guasabacoa y la cuenca (> 50 % de M_i) |
| R4 | El agua del Tadeo que hay en la bahía está sobre todo en Marimelena (> 50 % de M_Tadeo) |
| — | Se informan sin clasificar: T_i de cada río y la fracción por zona, con su rango entre casos |

R2 está escogida sabiendo el borrador (ver arriba). Su interés es independiente de ese borrador: dice si los ríos explican la
mancha de Sentinel-2 en la cabecera de Atarés.

**Regla:** **robusta** si se cumple en los 4 casos; **frágil** si falla en alguno (y se dice en cuál y por qué). Con 4 casos
no se usan porcentajes.

## Casos (4)

Todos con la configuración del miembro central de robustez (carta 1887, α = 0,5, datum +0,25 m, Cd 0,0025, EOT20, ERA5
sin escalar, 16 niveles, 120 d desde el 1-ene-2016). Se cubre lo que más puede mover el agua de los ríos:

| Caso | Cambio | Por qué |
|---|---|---|
| T0 | ninguno (caudal × 1) | referencia; además valida el ejecutable nuevo |
| T1 | caudal de los ríos × 0,25 | extremo bajo del conjunto |
| T2 | caudal de los ríos × 2 | extremo alto del conjunto |
| T3 | flujo de calor con SST OISST (como robustez m0005) | el balance de calor es la amenaza mayor a la circulación por densidad |

Considerado y descartado: un pulso por río para "fracción retenida a 30/60/90 d" (la idea vieja de `main.tex`). Con
renovaciones de días, a los 30 d no quedaría nada. T_i y los mapas responden lo mismo mejor.

## Técnica

- **Recompilar SCHISM** (mismo commit 09f407e8) con el módulo de trazadores genéricos (`USE_GEN`, `ntracer_gen = 3`). El
  módulo AGE actual admite varios trazadores pero solo escribe la edad, no la concentración (comprobado en
  `schism_step.F90`).
- **Validación del ejecutable:** las métricas de T0 (edad por zona, agua dulce) deben coincidir con las de robustez m0000
  con diferencias < 1 % (criterio de `comparar_tramos.py`). Si no, se para.
- Entradas: columnas de los trazadores en `msource.th` (el orden de columnas por módulo hay que leerlo en el código antes de
  escribirlas: POR CONFIRMAR), borde 0, inicial 0. Opción `TRAZADORES=1` en `caso_real.py`.
- Cada trazador es una salida 3D más y necesita un scribe: 3 + 3 = 6 scribes, 10 núcleos por caso. Tramos de 10 d con
  hotstart, como robustez. Se conservan los campos completos de los 4 casos.
- Posproceso: `scripts/trazadores_rios.py` (por escribir, con autoprueba de solución conocida), que da T_i, fracciones por
  zona, mapas y el control de la suma.

## Coste

- Compilar y validar: ~1 día de trabajo; el ejecutable actual no se toca (el conjunto sigue con él).
- 4 casos × 120 d: ~6–16 h de reloj cada uno (según la cola) con 10 núcleos. Se lanzan cuando el conjunto termine o
  libere carriles.

## Figura 8 (propuesta)

(a)–(c) agua de cada río en superficie (T0); (d) T_i por río con el rango T0–T3; tabla o barras de la fracción por zona.

## Registro de cambios

- 2026-11-08 — Aprobado por Alex y congelado, sin cambios de texto respecto al borrador (commit cf63c26). Aún no se ha compilado ni corrido nada.

