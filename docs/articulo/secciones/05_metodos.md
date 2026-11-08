# 5. Métodos (actualizado 7-nov-2026)

## 1. Batimetría desde cartas históricas y su incertidumbre

- **Cartas:** U.S. H.O. n.º 307, dos ediciones con levantamientos españoles distintos: hasta 1879 (ed. 1889) y hasta 1887 (ed. 1898). Sondeos en brazas (1,8288 m), con cuartos, y tercios en los bajos.
- **Digitalización manual** sobre teselas con rejilla de píxeles (`02`–`04`). Se obtuvieron **1126 sondeos (1879)** y **1514 (1887)**. La georreferencia de Harvard es WGS84 con RMS 18 m (el metadato dice NAD27, no es así). Control: el faro del Morro coincide.
- **Registro 1898 → 1889** automático (SIFT + RANSAC + polinomio de 2.º grado, 2432 pares): residuo mediano 1,2 m (p90 2,6 m). El faro queda a 8 m.
- **Comparación entre cartas:** fuera de la bahía la ed. 1898 repite la mayoría de los sondeos; **dentro es un levantamiento nuevo**. Entre sondeos vecinos: mediana 0, |Δz| medio 0,76 m.
- **Superficies** (`07`): rejilla UTM 17N de 20 m; interpolación lineal de sondeos + costa a 0 m, descartando triángulos de lado > 500 m; GEBCO lejos de los sondeos (transición 150–600 m); profundidad mínima 0,3 m.
- **Error de carta como campo aleatorio:** variograma de 12 134 diferencias 1887−1879, exponencial (meseta 1,08 m², alcance 149 m, pepita 0,54 m²) → **σ = 0,9 m, L = 150 m**. Se atenúa hacia la orilla y no toca el canal garantizado.
- **Estado de dragado α ∈ [0, 1]:** α = 0 es la carta tal cual; α = 1 lleva el canal a ≥ 12,8 m (220 × 1530 m, rumbo 124°) y el agua navegable histórica (≥ 5 m, conectada al canal) a 11 m (prácticos: 9,75–11,58 m). Volumen 26–36 hm³; el campo aleatorio añade ±1 hm³.
- **Datum de la carta desconocido** (probablemente bajamar): desplazamiento de 0 a +0,5 m.
- Figuras: `../../figuras/control_sondeos_1879_1887.png`, `superficies_1879_1887.png`, `batimetria_conjunto.png`.

## 2. Modelo hidrodinámico

- **SCHISM** (commit 09f407e8, el mismo en el Mac y en Lemaitre4), 3D, con módulo AGE. En el texto: niveles **S** (no LSC²) y borde con **esponja** (no Flather).
- **Malla** (DistMesh, Persson y Strang 2004; `09_malla.py`): círculo de 5 km centrado en la boca; **4832 nodos y 8941 triángulos** (4001 nodos en la bahía); 25 m en el canal (~11 elementos a lo ancho), 40 m en la bahía, hasta 400 m mar afuera; ángulo mínimo 12,4°. Figura: `../../figuras/malla.png`.
- **Vertical:** 16 niveles S; profundidad topada a 200 m (el talud llega a 1200 m y solo transmite la marea).
- **Numérica:** dt = 100 s; turbulencia GLS k-kl (itur = 3); Coriolis; Cd de fondo uniforme (dimensión del conjunto).
- **Borde abierto:** arco de 33 nodos; elevación armónica; esponja (Cd → 0,05 a < 1 km del borde), viento de 0 a < 1 km hasta pleno a 2 km, sin advección de momento a < 800 m. La corriente espuria del borde no cambia las cifras de la bahía (suplementario).
- **Densidad en todos los miembros** (decisión 21-oct): baroclínico por salinidad. Ríos con S = 0; borde con S = 36 y T = 28 °C fijas; temperatura constante y **sin flujo de calor**; **sin evaporación ni precipitación** (SCHISM pide recompilar con PREC_EVAP). Esto se declara como límite y se prueba aparte (§6 bis).

## 3. Forzamiento

- **Atmósfera:** ERA5 horario 2016–2025, 22,8–23,5 N / 82,8–81,9 O, convertido a `sflux`. Todas las corridas empiezan el 1-ene-2016.
- **Marea:** **EOT20** (9 constituyentes; CC BY, sin registro) en el conjunto, el mecanismo y la robustez. FES2022 (11 constituyentes) solo como comparación: difieren < 0,4 cm en amplitud (`../../figuras/marea_fes_eot20.png`). Factores nodales y argumento astronómico de pyTMD.
- **Ríos:** Luyanó, Martín Pérez y Tadeo, 2,14 m³ s⁻¹ en total (JICA 2004) × factor del conjunto; S = 0; cuentan como agua nueva para la edad.
- **SST (solo robustez):** NOAA OISST v2.1 diaria, media de 13 celdas de mar frente a la bahía; ene–abr 2016 24,5–27,9 °C. Entra como T del borde (serie diaria) y T inicial en el experimento de calor realista.

## 4. Escalas de tiempo de transporte y métricas (protocolo congelado 27-oct, `../../protocolo_metricas_conjunto.md`)

- **Edad del agua** (AGE; Deleersnijder et al. 2001): días desde que el agua salió del mar abierto **o de un río** (los ríos entran con AGE = 1, `msource.th`); SCHISM escribe la edad en días. Decirlo explícitamente: no es un tiempo de renovación del agua dulce.
- **Desviación del protocolo (registrada el 8-nov):** la fracción de volumen se da solo para > 30 d; para 7 y 14 d, P entre miembros y mapas de superficie.
- **Salidas** cada 4 h; métricas en los **últimos 30 de los 120 d** (`posproceso.py`): edad media y p10/50/90 por zona; fracción del volumen con edad > **30 d** (> 7 y > 14 d previstas pero no calculadas: desviación registrada) y P(edad > **7, 14 y 30 d**) entre miembros (7 d ≈ edad con densidad en el miembro central; 14 d ≈ sicigias–cuadratura; 30 d = umbral del plan original, fijados antes de ver el conjunto); mapas de superficie y fondo; edad en superficie y fondo del canal; agua dulce en superficie (1 − S/36); campos a las 16:00 UTC en la rejilla Sentinel-2.
- **Equilibrio:** deriva de la edad de la bahía ≤ 0,05 d/d en sus últimos 10 d; resultados con todos los miembros y aparte con los que están en equilibrio.
- **Caudal por el canal:** se calcula, pero no es un resultado del artículo (avisos en `../cifras.md`).
- **Zonas:** canal, cuenca, Marimelena, Guasabacoa, Atarés (`../../figuras/zonas.png`).
- **Pendiente:** destino del agua de cada río (fig. 8): partículas o un trazador por río, sin decidir.

## 5. Diseño del conjunto y sensibilidad

- **Saltelli** con Sobol aleatorizado (scipy), N = 64, **d = 9 → 704 miembros** (64 × 11), **120 d** cada uno. Índices de Jansen S1 y ST con IC bootstrap 95 %; autoprueba con Ishigami.

| Parámetro | Rango |
|---|---|
| Carta | 1879 / 1887 |
| Estado de dragado α | 0–1 |
| Realización del error de carta | semilla del campo aleatorio |
| Datum | 0 a +0,5 m |
| Cd | 0,001–0,005 (log-uniforme) |
| Escala del viento | × 0,8–1,2 |
| Dirección del viento | ± 15° |
| Amplitud de la marea | × 0,9–1,1 |
| **Caudal de los ríos** | **× 0,25–2 (log-uniforme)** sobre 2,14 m³ s⁻¹ |

- **Duración:** con densidad la edad llega al equilibrio en ~30 d (experimento de mecanismo) → 120 d con la métrica en los últimos 30 y la deriva como control.
- **Conclusiones que se ponen a prueba** (fijadas antes de ver el conjunto): C1 orden canal < cuenca < Guasabacoa < Atarés; C2 Atarés > canal; C3 Marimelena > cuenca; C4 Guasabacoa y Atarés > cuenca; C5 edad de la bahía < 30 d; C6 < 120 d (los "4 meses" de JICA); C7 en el canal, superficie más vieja que fondo; P(edad > 7/14/30 d); C8 parámetro con mayor ST (se informa, no se clasifica). **Robusta** ≥ 90 % de los miembros, **frágil** 10–90 %, **rechazada** ≤ 10 %.
- Con N = 64 el error de los índices es ~0,1 en ST y ~0,2 en S1 → interpretar sobre todo ST.

## 6. Experimentos de mecanismo (hechos)

Miembro central (carta 1887, α = 0,5, datum +0,25 m, Cd 0,0025), 1 año 2016, EOT20: (1) solo marea; (2) marea + viento; (3) marea + viento + ríos y densidad.

## 6 bis. Robustez de la circulación por densidad (nuevo; hechos salvo uno)

Miembro central con ríos, 120 d; se cambia una cosa cada vez: cierre k-ε; 32 niveles; difusividad mínima × 10; flujo de calor aire-mar de ERA5 (albedo 0,06, agua Jerlov 7) con el borde a 28 °C; y flujo de calor con la SST diaria de OISST en el borde y como T inicial (⏳ corriendo).

## 7. Cómputo

Lemaitre4 (CÉCI). **7 núcleos por miembro** (4 de cálculo + 3 de escritura, porque la salinidad es una 3.ª salida 3D). **Tramos de 20 d** encadenados con hotstart (combinado con `combine_hotstart7`, `ihot = 2`); comprobado que reiniciar no cambia las métricas (0,01 %). Los miembros avanzan con ~50 "trabajadores" de Slurm en paralelo. Un tramo de 20 d tarda 0,65–9 h (mediana 1,6 h) según la carga. Posproceso dentro del trabajo; los campos completos se borran salvo 3 miembros. Horas-núcleo totales: ⏳ (~5·10⁴, estimación gruesa).

## 8. Evaluación sin observaciones locales

- **(1) Control analítico:** con solo marea el modelo coincide con el diagnóstico del prisma (excursión < canal → renovación mala) y lo supera (166 d frente a 24 d). La coincidencia de caudales del borrador queda en suspenso (avisos de caudal).
- **(2) JICA 2004 ("tiempo de retención del agua dulce ≈ 4 meses"):** no es comparable con la edad (que cuenta el agua de los ríos como nueva); la magnitud comparable es el tiempo de renovación del agua dulce (`renovacion_dulce.py`, ⏳; cota ≲ 4 d). → discusión.
- **(3) Dos modelos de marea independientes** coinciden en < 0,4 cm ✅. **(4) Reinicio por tramos** no cambia las métricas ✅. **(5) Insensibilidad al borde** ✅.
- **(6) Sentinel-2** (protocolo congelado 21-oct, control de desplazamientos registrado 26-oct): ρ = 0,45 en la prueba principal, pero no distinguible del azar espacial (p = 0,16). Sentinel-2 no valida el modelo más allá del gradiente boca → cabeceras.
