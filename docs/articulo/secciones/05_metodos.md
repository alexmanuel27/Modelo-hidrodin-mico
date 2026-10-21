# 5. Métodos

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

- **SCHISM** (commit 09f407e8), 3D, con módulo AGE. Corregir en el texto: niveles **S** y no LSC²; borde con **esponja** y no Flather; partículas todavía sin implementar.
- **Malla** (DistMesh, Persson y Strang 2004; `09_malla.py`): círculo de 5 km centrado en la boca; **4832 nodos y 8941 triángulos** (4001 nodos en la bahía); 25 m en el canal (~11 elementos a lo ancho), 40 m en la bahía, hasta 400 m mar afuera; ángulo mínimo 12,4°. Figura: `../../figuras/malla.png`.
- **Vertical:** 16 niveles S. La profundidad se topa a 200 m (el talud llega a 1200 m y solo transmite la marea).
- **Numérica:** dt = 100 s; turbulencia GLS (itur = 3); Coriolis activado; rozamiento de fondo Cd uniforme (dimensión del conjunto).
- **Borde abierto:** arco de 33 nodos. Elevación armónica. Esponja de rozamiento (Cd → 0,05 a < 1 km del borde), viento que crece de 0 (a < 1 km del borde) a su valor pleno a 2 km, y sin advección de momento a < 800 m. Hay una corriente espuria en los nodos del borde (hasta ~1–4 m/s según la fricción), pero las cifras de la bahía no cambian con o sin esponja → va al material suplementario.
- **Con ríos (experimentos de mecanismo):** modelo baroclínico por salinidad (T y S constantes en el borde: 28 °C, 36; sin flujo de calor).

## 3. Forzamiento

- **Atmósfera:** ERA5 horario 2016–2025, dominio 22,8–23,5 N / 82,8–81,9 O (3 × 4 puntos útiles), 87 672 h sin huecos, convertido a `sflux`. Ventana de simulación: desde el 1-ene-2016.
- **Marea:** 11 constituyentes de FES2022 o 9 de EOT20, interpoladas en complejo a los 33 nodos del borde, con factores nodales y argumento astronómico de pyTMD. Los dos modelos difieren menos de 0,4 cm en amplitud (figura `../../figuras/marea_fes_eot20.png`).
- **Ríos:** Luyanó, Martín Pérez y Tadeo (2,14 m³ s⁻¹ en total), S = 0, entran como "agua nueva" para la edad.

## 4. Escalas de tiempo de transporte

- **Edad del agua** (módulo AGE; Deleersnijder et al. 2001): días desde que el agua salió del mar abierto (o de un río). Fuera de la bahía vale 0; dentro arranca en 0 el día 0. SCHISM escribe directamente la edad en días (α/C/86400).
- **Salidas por miembro** (`posproceso.py`, cada 4 h, ventana de los últimos 30 d):
  - edad media y p10/p50/p90 por zona;
  - fracción del volumen con edad > 30 d;
  - mapas de superficie y de fondo;
  - caudal neto y bruto por una sección del canal (330 m);
  - edad en superficie a las 16:00 UTC en la rejilla Sentinel-2 (252 × 238 celdas de 20 m).
- **Zonas:** canal, cuenca, Marimelena, Guasabacoa, Atarés (`../../figuras/zonas.png`).
- Pendiente: partículas por foco (fracción retenida a 30/60/90 d).

## 5. Diseño del conjunto y sensibilidad

- **Saltelli** con Sobol aleatorizado (scipy), N = 64, d = 8 → **640 miembros**. Índices de Jansen de primer orden y totales. Autoprueba con Ishigami: recupera los índices exactos con error < 0,02.

| Parámetro | Rango |
|---|---|
| Carta | 1879 / 1887 |
| Estado de dragado α | 0–1 |
| Realización del error de carta | semilla del campo aleatorio |
| Datum | 0 a +0,5 m |
| Cd | 0,001–0,005 (log-uniforme) |
| Escala del viento | ×0,8–1,2 |
| Dirección del viento | ±15° |
| Amplitud de la marea | ×0,9–1,1 |

- **Pendiente:** la duración de cada miembro. A 90 d la edad aún no está en equilibrio y la corrida de 1 año lo decidirá. También falta la convergencia de los índices por bootstrap.

## 6. Experimentos de mecanismo

Un miembro base, 1 año: (1) solo marea, (2) marea + viento, (3) marea + viento + ríos y densidad. El diseño está listo (`NWS`, `RIOS`, `QFAC`) y la prueba de 2 d con ríos corrió bien. Sin resultados todavía.

## 7. Cómputo

CÉCI, Lemaitre4 (EPYC 9534, 4096 núcleos simultáneos por usuario, arrays de Slurm). Cada miembro usa 4 núcleos de cálculo + 2 de escritura: **2,7–3,9 h por 90 d simulados**; con ríos el coste es el mismo. El conjunto cabe en un array de ≤ 682 miembros simultáneos. Las horas de núcleo totales dependen de la duración final.

## 8. Evaluación sin observaciones locales

- **(1) Control analítico:** el caudal de marea del modelo, 64–74 m³ s⁻¹, coincide con el del prisma, 66 m³ s⁻¹ ✅. La renovación es más lenta que en el control → discusión.
- **(2) Insensibilidad al tratamiento del borde:** con y sin esponja, las cifras de la bahía no cambian ✅.
- **(3) Dos modelos de marea independientes** coinciden en < 0,4 cm ✅.
- **(4) Sentinel-2:** la edad en superficie a la hora del paso del satélite ya se genera. Falta compararla con la persistencia de las anomalías de turbidez.
