# Figuras del artículo

Las figuras finales van **en inglés** a `publication plan/modelo-hidrodin-mico/articulo/figuras/` (solo se copian; el manuscrito no se toca desde aquí).
Las de `docs/figuras/` son de trabajo (en español) y no van al artículo tal cual.

| # | Contenido | Datos / figura de trabajo | Estado (7-nov) |
|---|---|---|---|
| 1 | Mapa: bahía, canal, ensenadas, zonas, ríos y focos; recuadro de Cuba | `scripts/zonas.py`, `osm_rios_habana.json` (descargado 17-oct), costa OSM, `datos/sentinel2/focos.csv` | por hacer (ya están todos los datos) |
| 2 | Batimetría: sondeos 1879 / 1887, superficie, diferencia y realizaciones (α = 0 / 1) | `docs/figuras/superficies_1879_1887.png`, `batimetria_conjunto.png` | trabajo hecho; falta inglés y las correcciones del 21-oct |
| 3 | Malla y detalle del canal | `docs/figuras/malla.png` | trabajo hecho; falta inglés |
| 4 | Control analítico (prisma) | `resultados/prisma_marea.png` | **lista en inglés**; copiarla a `articulo/figuras/fig_prisma_marea.png` (la de allí es vieja) |
| 5 | P(edad > 7/14/30 d) por zona y mapa; mediana y P5–P95 | conjunto + `analisis_conjunto.py` | espera al conjunto (598/704 el 6-nov) |
| 6 | Índices de Sobol S1 y ST por zona, con IC | conjunto | espera al conjunto |
| 7 | Mecanismo: edad media por experimento (marea / + viento / + densidad) | `docs/figuras/mecanismo.png` | trabajo hecho; falta inglés. Sin caudal neto ni bruto (no fiables) |
| 8 | Destino del agua de los ríos | — | sin decidir (partículas o trazador por río) |
| 9 | Sentinel-2: agua dulce en superficie frente a persistencia de anomalías + distribución nula por desplazamientos | `docs/figuras/s2_vs_dulce.png`, `resultados/comparacion_s2/*.json` | trabajo hecho; falta inglés y mostrar el nulo |
| 10 | Marea en el borde: FES2022 frente a EOT20 | `docs/figuras/marea_fes_eot20.png` | trabajo hecho (correcciones del 21-oct) |
| S1 | Corriente espuria del borde y su insensibilidad en la bahía | `revisar_real.py` | datos hechos |
| S2 | Robustez de la densidad (k-ε, 32 niveles, mezcla × 10, flujo de calor) | `docs/figuras/robustez.png` | trabajo hecho; falta el caso con SST ⏳ |
| S3 | (si sale) caudal por el canal con salida cada 10 min frente a cada 4 h | `cluster/hf_caudal.sh` + `diag_caudal.py --hf` | prueba en marcha |

Obsoletas: S0 (`edad_primeras_corridas.png`, corridas provisionales) y la curva de 1 año sin ríos; las sustituyen 7 y S2.

Convenciones: UTM 17N en metros; paleta y estilo comunes en un único `scripts/figuras_articulo.py` (**todavía no existe**; se hará con los resultados del conjunto).

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
