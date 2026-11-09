# Requisitos de medidas de las figuras (Environmental Modelling & Software)

Resumen de `REQUISITOS_FIGURAS.md` del chat del artículo (8-nov-2026; el original está en el repo del artículo). Regla: la figura se hace
**ya al tamaño final y con el texto al tamaño final**; nada de hacerla grande y reducirla.

- Anchos: **90 mm** (una columna; alto ≤ 100, normal 60–80) o **190 mm** (dos columnas; alto ≤ 110, 120 solo si es la única figura de la
  página; relación ancho/alto 1,6–2,4). Nada a página completa.
- Tipografía: sans-serif, la misma en todas. Etiquetas y títulos de panel 7 pt; números de ejes, leyendas y barras 6–6,5 pt (nunca < 6);
  letra de panel «(a)» 8 pt negrita arriba a la izquierda. Sin título dentro de la imagen (va en el pie).
- Trazo: líneas de datos ≥ 0,7 pt; ejes 0,5 pt; marcadores ≥ 3 pt; distinguibles en gris. Paleta Okabe–Ito. Inglés; unidades entre
  paréntesis; UTM 17N en km sin «1e6»; escala y norte en mapas; una barra de color común si varios paneles muestran la misma magnitud.
- Exportar con `figsize=(190/25.4, h/25.4)` y `constrained_layout=True`, **sin `bbox_inches="tight"`**; PNG a 300 ppp (2244 px = 190 mm,
  1063 px = 90 mm; alto máx. a 190 mm: 1300 px) y PDF vectorial.
- Resumen gráfico (lo exige la revista): al menos 531 × 1328 px (alto × ancho), legible a 5 × 13 cm.
- Estilo y constantes: `scripts/figuras_articulo.py` (`ANCHO2`, `ANCHO1`, `estilo()`, `guarda()`).

| Fig. | Tamaño final | Estado |
|---|---|---|
| 1 mapa | 190 × ≤ 100 mm | ver `figuras.md` |
| 2 batimetría | 190 × ≤ 120 mm | ver `figuras.md` |
| 3 malla | 190 × 84 mm | hecha |
| 4 prisma | 190 × 72 mm | ver `figuras.md` |
| 5 P(edad > umbral) | 190 mm | espera al conjunto |
| 6 Sobol | 190 mm | espera al conjunto |
| 7 mecanismo | 190 × 72 mm | ver `figuras.md` |
| 8 ríos | 190 mm | espera a los trazadores |
| 9 Sentinel-2 | 190 × 90 mm, con (a)(b) y nulo de ρ | ver `figuras.md` |
| 10 marea EOT20 − FES2022 | 190 mm | ver `figuras.md` |
| S2 robustez | **90 × 60 mm** | ver `figuras.md` |
