# Puente con el manuscrito — LEER PRIMERO (actualizado 9-nov-2026)

Para el chat del artículo: lo que el texto debe decir, con su fuente. No es prosa del artículo.

- **Manuscrito:** `/Users/alex/Nube /repos/publication plan/modelo-hidrodin-mico/articulo/main.tex` (reescrito el **8-nov-2026** por el chat del artículo, secciones 1–7 al día; los marcadores y números que siguen pendientes están en su `PENDIENTES.md`). Desde este repo no se edita el `.tex`; solo se copian figuras finales en inglés a `articulo/figuras/` y cifras finales.

## Estado

| Bloque | Estado | Dónde |
|---|---|---|
| Área de estudio, datos públicos, control analítico | firme | `secciones/02`, `03`, `04` |
| Métodos | firme, salvo horas-núcleo totales y destino de los ríos | `secciones/05_metodos.md` |
| Mecanismo (marea / viento / densidad) | **firme** | `secciones/06_resultados.md` 6.4 |
| Robustez de la densidad | firme salvo el flujo de calor: con SST real (m0005) 11,2 d, sin equilibrio; **no es robusta a incluir el balance de calor** (cifras.md) | 6.4 y `07_discusion.md` |
| Sentinel-2 | **firme, resultado negativo** | 6.6 |
| Conjunto de 704 (mapas, Sobol, robusta/frágil) | **terminado (9-nov): 704/704**; bahía 7,8 d (P5–P95 5,6–10,4), C1–C2, C4–C7 robustas, C3 frágil, P(>14 d) = 0, C8 caudal S_T 0,67; figs 5 y 6 hechas (cifras.md) | 6.2, 6.3, 7.1 |
| Destino del agua de los ríos (fig. 8) | protocolo congelado 8-nov; sin resultados (falta compilar con `USE_GEN`, validar y correr 4 casos) | 6.5 |
| Caudal por el canal | **no usar** como resultado ni como acuerdo con el prisma | avisos en `cifras.md` |
| Figuras finales en inglés | 1–3 y el prisma; el resto a tamaño final en curso | `figuras.md`, `../figuras_requisitos.md` |

## Qué NO hay que reescribir y qué falta

El manuscrito ya tiene al día (8-nov): 704 miembros y d = 9, 120 d, EOT20, ríos y densidad en todos los miembros, marea mixta,
tabla del prisma, tiempo de cómputo, evaluación con Sentinel-2, el bloque de comportamiento del modelo, la discusión del
prisma y las limitaciones. **No mandar rehacer esas secciones desde este repo.** Lo que solo el repo técnico puede dar, con
el estado de cada punto, está en la lista de pendientes del 8-nov (resultados del conjunto, m0005, trazadores, horas-núcleo,
figuras a tamaño final, repositorio y DOIs) y se sigue en `../00_estado_y_plan.md`.

Ojo con una sola diferencia de cifras: el volumen **central** del prisma es 30,4 hm³ (todas las entradas en su moda) y la
**mediana** del Monte Carlo es 30,7 hm³; el manuscrito debe decir cuál usa (ver `cifras.md`).

## Protocolos congelados: fechas y hashes (repo de trabajo, privado)

| Protocolo | Texto congelado | Cabecera / cambios después |
|---|---|---|
| Comparación con Sentinel-2 | `773b9fb6f3d583ab15c10020d1a2fae6651c99fd` (21-oct-2026) | `fb8ad7d4364932f35300d8290713c1fb274ec0ed` (21-oct, congelado, solo cabecera); control por desplazamientos cíclicos registrado antes de ver resultados: `231696af8a7c5b2c5bb876e1e63cc7dd66ca88d9` (26-oct; script `dded0eb`) |
| Métricas del conjunto (C1–C8) | `4564b7e7867fc5cb8085515945aabd60bcc50d44` (commit del 26-oct 23:21 UTC; aprobado por Alex el **27-oct**) | `8f3bf73fa24b153b6b4e8e41181678d8be36a2c5` (8-nov: cabecera «CONGELADO» y registro; el 4dff6a7 del 29-oct lo llamaba congelado sin tocar el archivo) |
| Trazadores por río (fig. 8) | `cf63c263993eed847a2920c95a997282661246c8` (8-nov, borrador) | `3907fd7d8b7694c54c343064430b069f9da7a69d` (8-nov, aprobado y congelado, sin cambio de texto) |

Las fechas del manuscrito (métricas 27-oct, S2 21-oct con control 26-oct, trazadores 8-nov) coinciden con estos commits (el de métricas se aprobó el 27-oct sobre un texto ya commiteado el 26-oct). **Estos hashes son del repo privado:** solo se pueden verificar si se publica el historial o si los protocolos se depositan con fecha en Zenodo (decisión de Alex abierta).

## Archivos

- `cifras.md` — cada número: valor actual, fuente y si main.tex está al día.
- `figuras.md` — figuras previstas, de dónde salen y su estado.
- `secciones/` — material por sección (índice en `secciones/README.md`).
- Protocolos congelados antes de ver resultados (citarlos como tales, con fecha): `../protocolo_comparacion_s2.md` (21-oct, control 26-oct) y `../protocolo_metricas_conjunto.md` (27-oct).
- Resultados en detalle: `../resultados_mecanismo.md`, `../resultados_robustez.md`; comparación S2 en `../../resultados/comparacion_s2/`.
- Procedencia de los datos (URL, fecha, licencia): `../procedencia_datos.md` y los `descargas.tsv` de `datos/`.
- Bitácora completa: `../00_estado_y_plan.md`. **Este repo es la única fuente**: desde el 8-nov no se guarda nada en el Project de Claude (`claude/`); las copias que hay allí están congeladas y pueden estar viejas.
- Figura 8 (destino del agua de cada río): protocolo **congelado el 8-nov** (aprobado por Alex), `../protocolo_trazadores_rios.md`; sin resultados todavía.
- **Histórico, no usar:** `../historico/` (resúmenes viejos, cuerpo antiguo de la nota del vault y copia de lo que había en el Project de Claude, con su índice en `../historico/README.md`).
