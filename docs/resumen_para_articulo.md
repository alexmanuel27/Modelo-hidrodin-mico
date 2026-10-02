# Resumen técnico para el chat del artículo (2-oct-2026)

Lo que hay hecho en el repo de trabajo (`repos/Modelo-hidrodin-mico`) y lo que afecta al
manuscrito. Detalle completo: `docs/00_estado_y_plan.md` (secciones 14–17).

## 1. Hecho

| Paso | Estado | Dónde |
|---|---|---|
| Entorno + SCHISM | Compilado en el Mac (Apple Silicon): SCHISM `develop` commit 09f407e8 (23-sep-2026), módulo AGE, ParMETIS interno, conda `bahia` (gfortran 15.3, MPICH, NetCDF 4.10) | `scripts/instalar_entorno_mac.sh`, sec. 14 |
| Forzamiento atmosférico | ERA5 horario 2016–2025 (120 meses, 87 672 h, sin huecos), 22,8–23,5 N / 82,8–81,9 W, rejilla efectiva 3 × 4 puntos de 0,25° | `scripts/descargar_era5.py`, sec. 15 |
| ERA5 → SCHISM | Convertido a `sflux` (viento, presión, T, humedad específica, radiación, precipitación) | `scripts/era5_a_sflux.py` |
| Prueba de humo | Caso idealizado (bahía esquemática) que corre de punta a punta con marea + ERA5 + AGE | `scripts/caso_prueba.py`, sec. 16 |
| Control analítico | Prisma, renovación 16–34 d, excursión ~650 m < canal 1530 m | `scripts/prisma_marea.py` (ya en el artículo) |

## 2. Resultado de la prueba de humo (útil para Methods / material suplementario)

Caso: bahía 5,3 km² a 9 m, canal 250 × 1530 m a 12,8 m, mar a 30 m; malla de 50 m
(5674 nodos), 10 capas sigma, dt = 100 s, marea M2 de 0,15 m, ERA5 de enero de 2016.

- Marea en la bahía 14,9 cm (forzada 15): la bahía oscila "en bloque", como supone el prisma.
- Corriente en el canal 2,4 cm/s de media (máx. 8,6), mismo orden que el control analítico
  (4,5 cm/s; 3–6,5). Confirma con el modelo numérico que **la marea sola mueve poco el agua**.
- Coste: ~0,5 s por paso con 1 núcleo en el Mac (7–8 min por día simulado). El coste real por
  miembro del conjunto se medirá con la malla real en CÉCI.

## 3. Decisiones de configuración que irán en Methods

- Sin advección de momento en una franja de 250 m junto al borde abierto (`nadv=0` + `adv.gr3`):
  práctica habitual en SCHISM para estabilizar bordes con nivel impuesto.
- El borde abierto debe estar en mar abierto y no formar una "caja" (atrapa modos).
- **Coriolis**: en el caso de juguete (mar de 4 × 2 km abierto por 3 lados), rotación + nivel
  impuesto + viento produce una inestabilidad (crece ×2,7 cada ~3,5 h). Sin Coriolis desaparece;
  una esponja de fricción no la corrige. Se usó `ncor=0` solo en la prueba. **Hay que comprobarlo
  con la malla real** (borde lejano, aguas profundas). Si persiste: condición de borde con
  relajación de velocidades (tipo Flather) o dominio mayor. A escala de la bahía (Rossby ≈ 0,3)
  la rotación no domina, pero conviene incluirla en el artículo.
- MPI en el Mac es inservible para paralelizar (latencia); en el Mac solo pruebas, el
  conjunto va a CÉCI.

## 4. Batimetría: qué existe (búsqueda del 2-oct-2026)

No hay una cuadrícula moderna y abierta de la bahía. Opciones, de más a menos útil hoy:

| Fuente | Qué es | Acceso | Uso propuesto |
|---|---|---|---|
| U.S. Hydrographic Office, "Havana and Harbor, Cuba" (levant. hasta 1879, ed. 1889), ~1:8 000 | Carta con sondas, **ya georreferenciada** (GeoTIFF, Harvard) | Libre | Base provisional de las ensenadas |
| U.S. Hydrographic Office, "West Indies, Cuba, harbor of Havana" (levant. españoles hasta 1887, ed. 1898), ~1:7 800 | Sondas e isóbatas, TIFF 126 MB (Leventhal) | Libre, sin restricciones | Contraste con la de 1889 |
| U.S. H.O. chart 307 "Habana Harbor" (levant. hasta 1930), 1:7 500 | Más reciente | Solo ficha de catálogo; escaneo por localizar (LoC / NARA) | Mejor carta histórica si aparece |
| Prácticos del puerto (Cubadebate, 2018) | Canal 1530 m, 220–330 m, 12,8 m; calados de cada muelle (6,9–11 m) | Libre (PDF) | Puntos de control del canal y muelles |
| GEBCO | Mar abierto, ~450 m | Libre | Dominio exterior |
| BA 414 (UKHO, 1:10 000, ed. 2021) | Mejor carta moderna | Compra, ~50 £, papel | Sustituye a la provisional |
| GEOCUBA / CUJAE (ADCIRC 2016) | Levantamientos nacionales; usados también por un Delft3D–XBeach del Malecón (Ocean Eng., 2025) | No publicados | Si responden, la mejor |
| NV Charts (1:20 000), Navionics | Comerciales, licencia restrictiva | — | No |
| Batimetría por satélite | Agua turbia dentro de la bahía | — | No dentro de la bahía |

**Propuesta:** batimetría provisional = carta de 1889 georreferenciada (+ 1898 para contrastar)
digitalizada, canal fijado a 12,8 m, muelles con sus calados, GEBCO fuera, costa de la máscara
Sentinel-2. Incertidumbre fuera del canal 1–2 m (dragados y aterramiento en 130 años) → entra
como dimensión del conjunto y del Sobol. Se sustituye cuando llegue la BA 414 o la CUJAE.

**Para el artículo:** encaja con el mensaje central (bahía sin datos propios; la incertidumbre
se cuantifica). El uso de cartas del siglo XIX como prior, con su error explícito, es un punto
que hay que justificar bien en Methods y discutir en Limitations.

Enlaces:
- https://geodata.libraries.mit.edu/record/gisogm:edu.harvard:a9fa87e833a6 (Harvard, 1889; GeoTIFF en https://hgl.harvard.edu/catalog/harvard-g4924-h3-1889-u5)
- https://collections.leventhalmap.org/search/commonwealth:g445ht01p (1898)
- https://mocat.library.unt.edu/catalog/441-ch613 (H.O. 307, 1930)
- http://media.cubadebate.cu/wp-content/uploads/2018/09/puerto_de_la_habana-PRACTICOS.pdf
- https://www.sciencedirect.com/science/article/pii/S0029801825021444 (Delft3D–XBeach Malecón, GEOCUBA)
- http://scielo.sld.cu/scielo.php?script=sci_arttext&pid=S1680-03382016000300005 (Ponce y Córdova 2016)
- https://www.weilbach.com/webshop/charts/nautical-chart-414-puerto-de-la-habana--ba04140 (BA 414)

## 5. Pendientes que bloquean o cambian cifras del artículo

1. Batimetría (provisional ya posible; definitiva BA 414 / CUJAE).
2. Marea de contorno FES2022 (cuenta AVISO en trámite).
3. Acceso a CÉCI (pendiente del administrador) → coste real por miembro y tamaño del conjunto.
4. Comprobar Coriolis con la malla real.
5. Serie del mareógrafo HABANA (PSMSL 2363) para validación.
