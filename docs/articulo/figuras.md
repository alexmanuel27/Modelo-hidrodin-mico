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
| S1 | Suplementario: corriente espuria del borde y su insensibilidad en la bahía | `revisar_real.py` | datos hechos |
| S2 | Suplementario: curva de la edad (equilibrio) en la corrida de 1 año | `resumen.npz` de `runs/largo` | corriendo |

Convenciones: UTM 17N en metros; paleta y estilo comunes (se fijarán en un único `scripts/figuras_articulo.py` cuando haya resultados del conjunto).
