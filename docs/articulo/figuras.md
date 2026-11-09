# Figuras del artículo

Las figuras finales van **en inglés** a `publication plan/modelo-hidrodin-mico/articulo/figuras/` (solo se copian; el manuscrito no se toca desde aquí).
Las de `docs/figuras/` son de trabajo (en español) y no van al artículo tal cual.

| # | Contenido | Datos / figura de trabajo | Estado (7-nov) |
|---|---|---|---|
| 1 | Mapa: bahía, canal, ensenadas, zonas, ríos y focos; recuadro de Cuba | **`docs/figuras/articulo/fig01_map.png`** (`scripts/figuras_articulo.py 1`) | **inglés hecho (8-nov)**, con recuadro de Cuba (Natural Earth); **190 × 98 mm** (9-nov) |
| 2 | Batimetría: superficies 1879 / 1887 con sondeos, diferencia (solo donde las dos tienen sondeos a < 100 m), miembro dragado, campo de error, volumen frente a α | **`docs/figuras/articulo/fig02_bathymetry.png`** | **inglés hecho (8-nov)**, con las correcciones del 21-oct; **190 × 118 mm** (9-nov, pedido ≤ 120) |
| 3 | Malla: dominio con profundidad, borde abierto y esponja; bahía; detalle del canal | **`docs/figuras/articulo/fig03_mesh.png`** (profundidad del miembro central) | **inglés hecho (8-nov)** |
| 4 | Control analítico (prisma) | `resultados/prisma_marea.csv`; `scripts/prisma_marea.py` | **hecha a tamaño final (9-nov)**: `fig_prisma.png/.pdf`, 190 × 72 mm |
| 5 | Edad media por zona entre miembros (mediana, P5–P95) y mapas de P(edad en superficie > 7 y 14 d) | `scripts/analisis_conjunto.py` → `resultados/conjunto/prob_zonas.csv`, `prob_edad_sup.npz`; `scripts/figuras_resultados.py conjunto` | código listo y probado con el conjunto sintético (`analisis_conjunto.py --prueba`); espera al conjunto → `fig_ensemble`, 190 × 72 mm |
| 6 | Índices de Sobol: S1 y ST con IC 95 % de la bahía y ST por zona | `resultados/conjunto/sobol.csv`; `figuras_resultados.py sobol` | código listo y probado; espera al conjunto → `fig_sobol`, 190 × 80 mm |
| 7 | Mecanismo: edad de la bahía en el año y edad por zona (media ponderada por volumen, últimos 30 d; ver `cifras.md`) | `runs/mecanismo/m000{0,1,2}/resumen.*` | **hecha (9-nov)**: `fig_mechanism.png/.pdf`, 190 × 72 mm. Sin caudal neto ni bruto |
| 8 | Destino del agua de los ríos | — | protocolo aprobado y congelado 8-nov (`docs/protocolo_trazadores_rios.md`); resultados pendientes (primero compilar y validar) |
| 9 | Sentinel-2: frecuencia de anomalías, agua dulce del modelo y distribución nula de ρ | `datos/sentinel2`, `runs/mecanismo/m0002`, `resultados/comparacion_s2/m0002_s2_dulce.json` | **hecha (9-nov)**: `fig_sentinel2.png/.pdf`, 190 × 70 mm; el script reproduce ρ, p y P95 del JSON (aserción) |
| 10 | Marea en el borde: amplitudes FES2022 / EOT20 y diferencia de nivel en enero de 2016 | `datos/marea/*_habana.json` | **hecha (9-nov)**: `fig_tide.png/.pdf`, 190 × 70 mm; RMS de la diferencia 1,15 cm |
| S1 | Corriente espuria del borde y su insensibilidad en la bahía | `revisar_real.py` | datos hechos; sin figura final |
| S2 | Robustez de la densidad (k-ε, 32 niveles, mezcla × 10, flujo de calor) | `runs/robustez/m000*/resumen.npz` | **hecha (9-nov)**: `fig_robustness.png/.pdf`, **90 × 62 mm** (una columna); dibuja m0005 (calor con SST OISST) sola cuando exista su `resumen.npz` |
| S3 | (si sale) caudal por el canal con salida cada 10 min frente a cada 4 h | `cluster/hf_caudal.sh` + `diag_caudal.py --hf` | prueba en marcha |

**Numeración:** los documentos del chat del artículo no coinciden entre sí (en `REQUISITOS_FIGURAS.md` el mecanismo es la fig. 5; en la lista de pendientes la fig. 5 es la de P(edad > umbral)). Los archivos de resultados llevan nombre descriptivo (`fig_mechanism`, `fig_sentinel2`…) y no el número; las figuras 1–3 conservan `fig01_map`, `fig02_bathymetry`, `fig03_mesh`.

Obsoletas: S0 (`edad_primeras_corridas.png`, corridas provisionales) y la curva de 1 año sin ríos; las sustituyen 7 y S2.

Convenciones: tamaño final y 7 pt (`docs/figuras_requisitos.md`); estilo común en `scripts/estilo_figuras.py`; mapas en `scripts/figuras_articulo.py` (necesita scipy; corre en el contenedor), figuras de resultados en `scripts/figuras_resultados.py` (solo numpy + matplotlib; corre en el Mac). Salida: `docs/figuras/articulo/` (inglés, 300 ppp, 90 o 190 mm).

## Revisión 21-oct-2026 (qué falta en cada figura antes de pasarla al artículo)

- **Todas:** pasar al inglés; quitar el "1e6" de los ejes (km o metros completos); letras de panel (a), (b)…; etiqueta y unidades en cada barra de color; mismo sistema de coordenadas (UTM 17N) en todas las figuras de mapa; `scripts/figuras_articulo.py` con estilo común.
- **4 prisma:** ✅ lista (inglés, histogramas en escalón, medianas, referencia JICA, etiqueta del canal dentro del panel).
- **Mapas de batimetría (2):** la escala satura en 15–20 m y el exterior se ve como un bloque uniforme; usar escala 0–15 m con el exterior aparte o en escala logarítmica. Explicar el rectángulo rojo (canal dragado) en la leyenda; escribir α en vez de "alfa".
- **Diferencia 1887 − 1879:** fuera de la bahía se ven las facetas triangulares de la interpolación (sondeos dispersos), y en las orillas de Atarés y los muelles hay franjas rojo/azul que vienen de pendiente fuerte más error de georreferencia (RMS 18 m), no de cambio real. Enmascarar donde no haya sondeos de las dos ediciones a < ~100 m, o mostrar solo pares de sondeos cercanos.
- **Malla (3):** colorear la batimetría y marcar la zona de esponja (1 km desde el borde abierto); añadir un recuadro con la resolución del canal.
- **Zonas (→ 1):** el mapa final debe llevar ríos (OSM), focos de vertido, recuadro de Cuba, escala y norte. Las líneas grises son triángulos entre dos zonas (cosmético).
- **Marea FES/EOT20 (10):** solo amplitudes; añadir fases o, mejor, la diferencia entre las dos predicciones de nivel en un mes (RMS en cm), que es la cifra que importa.
- **S0 primeras corridas:** queda superada. Sustituir por S2 (curva de 1 año, medias diarias, con la escala "sin renovación"). La etiqueta diagonal se sale del eje y el mapa no tiene costa ni escala.
- **Controles de sondeos (suplementarios):** el de 1889 está en píxeles de la imagen; pasarlo a coordenadas o quitar los ejes. El de 1879/1887 está en lon/lat; hay cruces de 1887 fuera del borde de la imagen (la edición de 1898 cubre más al oeste), y conviene decirlo en el pie.
