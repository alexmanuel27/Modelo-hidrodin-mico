# Para el chat del artículo — respuesta a rev/V3 (22-nov-2026)

Chat técnico → chat del artículo. Commits 88aa4c9, db9a044, 907210c (repo `Modelo-hidrodin-mico`). Cifras con su commit; nada de esto contradice `docs/articulo/cifras.md`.

## Estado de lo pedido

| # | Petición | Estado |
|---|---|---|
| 1 | Simular oct y dic 2002 | **Preregistrado y con código (88aa4c9); sin correr.** Faltan la descarga de ERA5/OISST de 2002 y las corridas (≈ 175 h-núcleo). Sin resultado todavía: no escribir nada que dependa de él. |
| 2 | Landsat solo con el interior | **Preregistrado y con código (db9a044); sin descargar.** Sin resultado todavía. |
| 3 | Nivel de inyección de los ríos | **Respondido** (cifras ya existentes, 907210c). |
| 4 | Leyendas de dos figuras | **Hecho** (907210c); cifras idénticas. |
| 5 | Tamaño del repositorio | **Hecho:** ≈ 128 MB, 591 archivos. |

## 1. Octubre y diciembre de 2002 (pendiente; lectura ya fijada en `docs/protocolo_2002.md`)

- **Diseño:** miembro central, 1-sep → 31-dic-2002 (36 d de arranque antes del 7-oct), ERA5 de 2002 (viento, calor) y SST OISST de 2002, ríos en la capa superior. Tres variantes de caudal: (m0000) tabla 4.8, 2,141 m³/s; (m0001) + drenajes S4–S6 en Atarés, 3,640 m³/s; (m0002) + escorrentía de la lluvia horaria de ERA5, Q = C·I·A/3,6 con C = 0,5 (0,6 en Matadero) y las áreas de la tabla 2.1 de JICA → 3,640 + 8,744·I(t) m³/s (I en mm/h).
- **Fechas:** octubre = 7-oct-2002 (fig. 4.26 de JICA). **La fecha de la campaña de diciembre no está impresa en el vol. V**; se usa una ventana del 10 al 20 de diciembre (en torno a la campaña de canales del mismo contratista, 16–19-dic) y una de sensibilidad del 2 al 31 de diciembre.
- **Lectura (decide diciembre):** CONFIRMA que las campañas no representan una estación seca sin lluvia si alguna variante cierra ≥ 0,5 del hueco de +4,12 y ΔS fondo–superficie deja de contradecir (≥ 1,85, hacia 3,7–5,5); PARCIAL si cierra 0,25–0,5, o ≥ 0,5 sin que ΔS mejore, o si la ventana de sensibilidad da otra cosa; CONTRADICE si el cierre es < 0,25 en las tres (el sesgo salino es del modelo).
- **Límites ya conocidos:** sin lluvia directa sobre la bahía ni evaporación (SCHISM compilado sin ese módulo; ≈ 14 % de la escorrentía); escorrentía sin retardo; la tabla 4.11 (perfiles por zona) es de noviembre de 2001.
- **Para el texto ahora:** solo se puede decir que la prueba está diseñada; el resultado puede ir en cualquier dirección.

## 2. Landsat solo con el interior (pendiente; entrada V3-3f de `docs/protocolo_metricas_conjunto.md`)

- **Interior** = píxeles de la máscara de bahía de X3 a > 200 m de la costa de la malla (2 píxeles de 100 m de TIRS): 1,2 km² de 4,9, casi todo cuenca principal y Guasabacoa. Sensibilidad: 100 y 300 m.
- **Control:** el mismo par de mar abierto de X3 (mar A y mar B, 8–13 km al norte).
- **Lectura:** MANTIENE la contradicción si el interior sigue más cálido que el mar en nov–mar (IC95 > 0); la DEBILITA si el IC95 incluye 0; la INVIERTE si el interior es más frío que el mar, como el modelo.
- **Resultado vigente de X3 (bahía completa):** nov–mar +0,83 °C (IC95 +0,53 a +1,13), jun–sep +2,69 °C; modelo con calor −2,54 / +0,00 °C → no compatible.

## 3. Nivel de inyección de los ríos (respondido)

- **Por defecto** (base y los 704 miembros): `lev_tr_source = −9`, la T y la S de los ríos se mezclan en la **capa de fondo** del elemento fuente; el caudal entra en todo el elemento.
- **R no es un cambio relativo:** R = Δedad / 5,308 d (anchura P5–P95 de la edad media de la bahía de los 704). Mide el desplazamiento frente a la dispersión del conjunto.
  - capa superior: R = −0,105 → 6,581 → **6,025 d (−8,4 %)**;
  - toda la columna: R = −0,454 → 4,170 d (−36,6 %);
  - capa superior con caudal ×1,7005: R = −0,447 → 4,210 d (−36,0 %).
- **Realista para un río que entra en superficie: la capa superior.** Las desembocaduras del modelo tienen 0,4–2,2 m de profundidad y el agua del río (S ≈ 0–1) es ≈ 27 kg/m³ más ligera: sale como pluma superficial. El fondo obliga a un ajuste convectivo artificial; toda la columna supone mezcla completa en la boca (cota, no caso central).
- **Edad media de la bahía con inyección solo en la capa superior: 6,025 d** (miembro central, abril de 2016, últimos 30 d).
- **Matiz:** en esas corridas el trazador de edad siguió entrando por el fondo (solo se movieron T y S); en columnas de ~1 m no debería pesar, pero no está comprobado. Ninguna de las tres inyecciones cierra el hueco de salinidad (cierres +0,03; +0,18; +0,17).

## 4. Figuras (hechas)

`docs/figuras/articulo/fig_sobol_convergence_stats.{png,pdf}`: "channel", "main basin". `fig_jica_comparison.{png,pdf}`: "JICA Dec 2002", "JICA Oct 2002", "ensemble". Resultados idénticos byte a byte.

## 5. Tamaño del repositorio (para Software availability)

- Con la lista de `scripts/preparar_publicacion.sh`: **≈ 128 MB, 591 archivos** (código, malla, batimetría, forzamientos sflux 2016–2025 = 83 MB, SST, resultados, figuras, resúmenes de mecanismo y robustez). Los forzamientos de 2002 añadirán ≈ 3–4 MB.
- Los 704 resúmenes del conjunto (`resumen.npz/json`) son **1,88 GB**: mejor en Zenodo aparte.
- **Dos problemas por decidir antes de publicar (Alex):** (a) el script aborta porque su filtro rechaza 13 ficheros con «jica» en el nombre (scripts y resultados propios, no el PDF); (b) no incluye `datos/observaciones/` (la transcripción de las tablas de JICA), sin la que las comparaciones con JICA no se reproducen desde el repositorio público.

## Qué cambia en el texto (antes → después)

| Sección | Antes | Después |
|---|---|---|
| Métodos, ríos | "rivers as point sources at their mouths" | "river T and S are injected into the bottom layer of the source element (SCHISM default, used in all 704 members); a surface-layer injection, the realistic choice for a buoyant river plume, is tested as a sensitivity" |
| Resultados, sensibilidad | "R = −0.105 / −0.454" sin explicar | "surface injection lowers the central bay age from 6.58 to 6.03 d (−8 %, a shift of 0.10 of the ensemble P5–P95 width); whole-column injection gives 4.17 d (−37 %, 0.45)" |
| Discusión, salinidad | "las campañas de 2002 pueden no ser representativas" | **sin cambio hasta tener 2002**; añadir solo que JICA atribuye la baja salinidad de diciembre a las lluvias de las semanas previas (vol. V, §4.4.1) y que la prueba está preregistrada |
| Discusión, térmico | X3 contradice (bahía más cálida en nov–mar) | **sin cambio hasta tener el interior** |
| Leyendas | "canal", "cuenca", "dic", "oct", "conjunto" | "channel", "main basin", "Dec", "Oct", "ensemble" |
| Software availability | — | "~128 MB, 591 files (code, mesh, bathymetry, forcing, results); ensemble summaries (1.9 GB) archived separately" (cifra a revisar cuando se cierre la lista de publicación) |

## No decir

- Ningún resultado de 2002 ni del Landsat interior (no existen todavía).
- Que la inyección explica el hueco de salinidad (no lo explica).
- Que R es un porcentaje.
