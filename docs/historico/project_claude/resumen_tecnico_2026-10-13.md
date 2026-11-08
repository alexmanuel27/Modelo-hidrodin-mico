> Copia de `claude/resumen_tecnico_2026-10-13.md` del Project de Claude, archivada en el repo el 8-nov-2026 antes de
> borrar el Project. Superado: lo vigente está en `docs/articulo/`.

# Actualización técnica para el chat del artículo (13-oct-2026)

Continúa `claude/resumen_tecnico_2026-10-02.md`. Repo de trabajo `repos/Modelo-hidrodin-mico`, commits 8aa9683–dfb3bfe; detalle en `docs/00_estado_y_plan.md` (final de la sección 19, secciones 20 y 21) y `docs/resumen_para_articulo.md`.

Regla vigente: solo datos públicos y replicables (no se compra la BA 414; CUJAE/GEOCUBA/mareógrafo solo como comparación opcional).

## ⚠ Cifra del artículo que cambia

**Control analítico (`prisma_marea.py`) recalculado con el volumen de las cartas:** tiempo de renovación con retorno y ríos **23 d (p5–p95 13–35 d)**; antes 34 d (18–51 d). Renovación ideal 10,7 d (7–14), antes 15,5 d. Volumen 30 hm³ (27–35), antes 47 hm³. Excursión mareal ~610 m (0,4 del canal), sin cambio. La cifra antigua venía de 9 m de profundidad media y 47 hm³ de fuentes divulgativas, que las cartas y los prácticos no sostienen (ver abajo).

## Batimetría histórica

- Las cartas "1889" (Harvard) y "1898" (Leventhal) son ediciones de la **misma carta U.S. H.O. n.º 307 *Harbor of Havana***, con levantamientos españoles distintos: **hasta 1879** (ed. 1889, ~1:8 000) y **hasta 1887** (ed. 1898, corregida a mar-1898).
- **Unidades: brazas** (1 braza = 1,8288 m), con cuartos; en los bajos aparecen tercios y sextos.
- **Nivel de referencia: no figura** (cartela: "H.W.F.&C. VIII h 14 m. Rise of tide about 3 ft"). Probablemente bajamar; se tratará como desplazamiento incierto 0 a +0,5 m dentro del conjunto.
- El GeoTIFF de Harvard viene en **WGS84 geográfico** (no NAD27 como dice el metadato); georreferencia con RMS 18 m.
- **1126 sondeos** de la ed. 1889 (levantamientos hasta 1879) y **1514** de la ed. 1898 (levantamientos hasta 1887, registrada automáticamente sobre la de 1889; residuo mediano 1,2 m): `datos/batimetria/sondeos/`.
- Profundidades: canal de entrada 13–17 m; cuenca principal 9–13 m; Marimelena, Guasabacoa y Atarés mayoritariamente < 4 m.
- **Comparación 1879 vs 1887**: fuera de la bahía la ed. 1898 repite en buena parte los sondeos de 1879; **dentro de la bahía es un levantamiento nuevo**. Donde hay sondeos vecinos: sin sesgo (mediana 0), |Δz| medio 0,76 m dentro de la bahía.
- Figuras: `docs/figuras/control_sondeos_1889.png`, `docs/figuras/control_sondeos_1879_1887.png`.

## Superficies y batimetría del conjunto

- Costa actual: OpenStreetMap (`natural=coastline`, instantánea 2026-10-13 vía Overpass, ODbL). Rejilla UTM 17N de 20 m; sondeos + costa a profundidad 0; GEBCO 2026 lejos de los sondeos (`scripts/batimetria/07_superficies.py`). Figura: `docs/figuras/superficies_1879_1887.png`.
- **Bahía (incluye el canal): área 4,91 km²; profundidad media 5,6 m (1879) / 5,2 m (1887); volumen 27,5 / 25,7 hm³.**
- **Validación de la costa con prácticos:** ancho de agua del canal 250–400 m a lo largo de ~1,6 km (prácticos: 220–330 m, 1530 m).
- **Campo aleatorio estimado de los datos** (variograma de la diferencia 1887−1879, 12 134 celdas): exponencial, **σ_carta = 0,9 m, L = 150 m**.
- **Estado de dragado α como dimensión del conjunto** (`scripts/batimetria/08_batimetria_conjunto.py`): α = 0 carta tal cual; α = 1 canal de entrada ≥ 12,8 m (220 × 1530 m, rumbo 124°) y agua navegable histórica (≥ 5 m, conectada al canal) a 11 m (canales de acceso 9,75–11,58 m según prácticos). **Volumen 26–36 hm³** según carta y α; el campo aleatorio solo añade ±1 hm³. **Ni el extremo dragado llega a los 47 hm³ divulgativos** (exigiría 9,6 m de media en toda la bahía). Figura: `docs/figuras/batimetria_conjunto.png`.

## CÉCI

- **NIC5**: 70 nodos × 64 núcleos, 2 días máx., 448 núcleos simultáneos por usuario.
- **Lemaitre4**: 40 nodos × 256 núcleos, 2 días máx., **4096 núcleos simultáneos por usuario**, arrays ≤ 10 000 → el sitio del conjunto.
- **SCHISM compilado en ambos** (commit 09f407e8, módulo AGE).

## Malla real y primeras simulaciones (NIC5)

- **Malla** (DistMesh, Persson y Strang 2004): círculo de 5 km centrado en la boca; 4832 nodos, 8941 triángulos (4001 nodos en la bahía); 25 m en el canal (~11 elementos a lo ancho), 40 m en la bahía, hasta 400 m mar adentro; ángulo mínimo 12,4°. Borde abierto en arco (33 nodos, 46–1220 m; profundidad topada a 200 m). Figura: `docs/figuras/malla.png`.
- **SCHISM** (`scripts/caso_real.py`): 16 niveles S, dt 100 s, Coriolis, ERA5, módulo AGE ("agua nueva" = la de fuera de la bahía), esponja de fricción y sin viento junto al borde abierto. Marea aún **M2 uniforme de 0,15 m (provisional)**.
- **Prueba de 2 días:** estable (sin NaN, velocidades saturadas con Coriolis). La bahía sube y baja en bloque (14,9 de 15 cm, desfase 0 h). Corriente mareal en el canal 2,5 cm/s de media, 7,7 cm/s de máximo (control analítico ~4 cm/s); 1,2 cm/s en la bahía.
- **Defecto de borde:** corriente espuria de hasta 1 m/s en 4 nodos de la esquina E donde el borde abierto toca la costa (~5 km de la boca). Con y sin esponja (el chorro cambia ×2) las cifras de la bahía son idénticas → no afecta a las conclusiones; va al suplementario.
- **Coste por miembro (NIC5):** 2 días = 279 s con 4 núcleos, 172 s con 8, 116 s con 16, 110 s con 32. Lo eficiente es 4–8 núcleos → **90 días ≈ 2,2–3,5 h por miembro**; cientos de miembros caben en días con los límites de CÉCI.

## Pendiente

1. Marea FES2022 en el borde abierto (sustituye a la M2 provisional) y recalcular `prisma_marea.py`.
2. Conjunto en Lemaitre4 (arrays de Slurm), diseño de Saltelli, experimentos de mecanismo, salidas (a)–(f).
3. Muelles y espigones en la costa (OSM `man_made=pier`), si hacen falta.
