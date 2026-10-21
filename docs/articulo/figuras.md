# Figuras del artículo

Las figuras finales van **en inglés** a `publication plan/modelo-hidrodin-mico/articulo/figuras/` (solo se copian; el manuscrito no se toca desde aquí).
Las de `docs/figuras/` son de trabajo (en español) y no van al artículo tal cual.

| # | Contenido | Datos / script de trabajo | Estado |
|---|---|---|---|
| 1 | Mapa: bahía, canal, ensenadas, zonas, ríos y focos; recuadro de Cuba | `scripts/zonas.py`, `osm_rios_habana.json`, costa OSM | por hacer (falta OSM de ríos) |
| 2 | Batimetría: sondeos 1879 / 1887, superficie, diferencia y realizaciones del conjunto (α = 0 / 1) | `07_superficies.py`, `08_batimetria_conjunto.py` (`docs/figuras/superficies_1879_1887.png`, `batimetria_conjunto.png`) | versión de trabajo hecha; falta versión en inglés |
| 3 | Malla y detalle del canal | `09_malla.py` (`docs/figuras/malla.png`) | versión de trabajo hecha |
| 4 | Control analítico (prisma) | `prisma_marea.py` (`resultados/prisma_marea.png`) | en el manuscrito con valores viejos → regenerar |
| 5 | (a) Probabilidad de edad > 30 d por zona y mapa; mediana y P5–P95 | conjunto + `posproceso.py` | espera al conjunto |
| 6 | Índices de Sobol (primer orden y total) por zona | conjunto | espera al conjunto |
| 7 | Mecanismo: caudal por el canal y edad media por experimento (marea / + viento / + densidad) | experimentos de mecanismo | espera |
| 8 | Destino de las descargas: fracción retenida a 30/60/90 d por foco | partículas | por programar |
| 9 | Evaluación: exposición en superficie del modelo vs persistencia de turbidez Sentinel-2 (rejilla de 20 m, ~16:00 UTC) | `posproceso.py` (s2_edad) + estudio Sentinel-2 | espera |
| 10 | Marea en el borde: FES2022 frente a EOT20 (evaluación) | `docs/figuras/marea_fes_eot20.png` | versión de trabajo hecha |
| S0 | Edad media por zona en las dos primeras corridas (provisional) | `docs/figuras/edad_primeras_corridas.png` | hecha (provisional) |
| S1 | Suplementario: corriente espuria del borde y su insensibilidad en la bahía | `revisar_real.py` | datos hechos |
| S2 | Suplementario: curva de la edad (equilibrio) en la corrida de 1 año | `resumen.npz` de `runs/largo` | corriendo |

Convenciones: UTM 17N en metros; paleta y estilo comunes (se fijarán en un único `scripts/figuras_articulo.py` cuando haya resultados del conjunto).

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
