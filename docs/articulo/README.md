# Puente con el manuscrito — LEER PRIMERO (actualizado 7-nov-2026)

Para el chat del artículo: lo que el texto debe decir, con su fuente. No es prosa del artículo.

- **Manuscrito:** `/Users/alex/Nube /repos/publication plan/modelo-hidrodin-mico/articulo/main.tex` (última edición: **17-oct-2026**). Desde este repo no se edita el `.tex`; solo se copian figuras finales en inglés a `articulo/figuras/` y cifras finales.

## Estado

| Bloque | Estado | Dónde |
|---|---|---|
| Área de estudio, datos públicos, control analítico | firme | `secciones/02`, `03`, `04` |
| Métodos | firme, salvo horas-núcleo totales y destino de los ríos | `secciones/05_metodos.md` |
| Mecanismo (marea / viento / densidad) | **firme** | `secciones/06_resultados.md` 6.4 |
| Robustez de la densidad | firme, salvo el flujo de calor (repetición con SST real corriendo) | 6.4 y `07_discusion.md` |
| Sentinel-2 | **firme, resultado negativo** | 6.6 |
| Conjunto de 704 (mapas, Sobol, robusta/frágil) | corriendo: 598/704 el 6-nov | 6.2, 6.3, 7.1 |
| Destino del agua de los ríos (fig. 8) | sin hacer ni decidir | 6.5 |
| Caudal por el canal | **no usar** como resultado ni como acuerdo con el prisma | avisos en `cifras.md` |
| Figuras finales en inglés | solo el prisma | `figuras.md` |

## Qué está viejo en main.tex (17-oct) y dónde está lo nuevo

1. **640 → 704 miembros, d = 8 → 9** (caudal de los ríos × 0,25–2), **90 → 120 d**, marea EOT20, **ríos y densidad en todos los miembros**: resumen (l. ~48), highlights (l. ~60), sec. 5.5 y tabla de parámetros (l. ~284–314). → `secciones/05_metodos.md` §5.
2. "mainly semidiurnal" → marea **mixta** (l. ~120). → `cifras.md`, área.
3. Tabla 2 del prisma: valores viejos (1,47 hm³; 4,8 %; 10,7 d; 23 d; 4,3 cm/s; 610 m). → `cifras.md`, control; figura nueva lista.
4. Sec. 5.6: el `\todo` del caudal de los ríos está resuelto; añadir la robustez. → §6 y §6 bis.
5. Sec. 5.7 Computation: 4 + 3 núcleos, tramos de 20 d con hotstart. → §7.
6. Sec. 5.8 Evaluation: resultado de Sentinel-2 y estado del control. → §8.
7. Sec. 6.1 Model behaviour: todo el bloque provisional sobra. → `06_resultados.md` 6.1.
8. Sec. 6.4 y 6.6: ya hay resultados.
9. Sec. 7.2 "Why the tidal prism overstates flushing": solo vale con marea sola; con densidad es al revés. → `07_discusion.md`.
10. Limitations: sin flujo de calor ni E − P, solo ene–abr 2016, caudal de una campaña, caudal del canal no usable.

## Archivos

- `cifras.md` — cada número: valor actual, fuente y si main.tex está al día.
- `figuras.md` — figuras previstas, de dónde salen y su estado.
- `secciones/` — material por sección (índice en `secciones/README.md`).
- Protocolos congelados antes de ver resultados (citarlos como tales, con fecha): `../protocolo_comparacion_s2.md` (21-oct, control 26-oct) y `../protocolo_metricas_conjunto.md` (27-oct).
- Resultados en detalle: `../resultados_mecanismo.md`, `../resultados_robustez.md`; comparación S2 en `../../resultados/comparacion_s2/`.
- Procedencia de los datos (URL, fecha, licencia): `../procedencia_datos.md` y los `descargas.tsv` de `datos/`.
- Bitácora completa: `../00_estado_y_plan.md`. **Este repo es la única fuente**: desde el 8-nov no se guarda nada en el Project de Claude (`claude/`); las copias que hay allí están congeladas y pueden estar viejas.
- Figura 8 (destino del agua de cada río): protocolo en borrador, `../protocolo_trazadores_rios.md`.
- **Histórico, no usar:** `../resumen_para_articulo.md` (2-oct) y `../nota_vault_2026-09-25.md`.
