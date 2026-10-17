# Cifras del artículo: valor en el borrador, valor actual y de dónde sale

Fuente de verdad de cada número que aparece (o aparecerá) en `publication plan/modelo-hidrodin-mico/articulo/main.tex`.
Al cambiar un resultado, se cambia aquí primero; al pasar el número al manuscrito, se marca ✅.

Estado: ✅ final y ya en el manuscrito · 🔁 en el manuscrito pero desactualizado · ⏳ provisional (cambiará) · ➕ falta en el manuscrito

## Área de estudio (sec. 2) y resumen

| Cifra | En main.tex | Valor actual | Fuente | Estado |
|---|---|---|---|---|
| Área de la bahía (incluye canal) | ~5.2 km² | **4.91 km²** | `scripts/batimetria/07_superficies.py` (cartas + costa OSM) | 🔁 |
| Profundidad media | ~9 m | **5.2 (1887) – 5.6 (1879) m** tal cual las cartas; 6.4–7.3 m con dragado | `datos/batimetria/superficies/volumenes_conjunto.json` | 🔁 |
| Volumen | 47 hm³ (tabla 2) | **26–36 hm³** según carta y dragado (central 30) | ídem | 🔁 |
| Canal de entrada | 1530 m, 220–330 m, 12.8 m | igual | Prácticos 2018 | ✅ |
| Carrera de marea | "a few decimetres" | 0.29 m media (JICA 2004); M2 de la prueba 0.15 m de amplitud; FES2022 pendiente | `scripts/marea_fes2022.py` | ⏳ |
| Ríos | — | Luyanó 1.33, Martín Pérez 0.72, Tadeo 0.09 m³ s⁻¹ (total 2.14; CIMAB 2002 en JICA 2004) | `scripts/caso_real.py` (Q_RIOS) | ➕ |
| Renovación del agua dulce (literatura) | — | ≈ 4 meses (JICA 2004) | JICA 2004, p. R-7 | ➕ (discusión) |

## Tabla de datos públicos (tab. 1)

| Fila | En main.tex | Corrección |
|---|---|---|
| Costa | "Sentinel-2 water mask" | **OpenStreetMap `natural=coastline`** (instantánea 2026-10-13, ODbL). La máscara S2 no se usó → 🔁 |
| Batimetría | cartas 1889 y 1898 | precisar: levantamientos españoles **hasta 1879 y hasta 1887**, misma carta H.O. n.º 307; 1126 + 1514 sondeos |
| GEBCO | `\todo{ref}` | GEBCO 2026 Grid (citar GEBCO Compilation Group 2026) |
| Marea | FES2022 `\todo{ref}` | doi:10.24400/527896/A01-2024.004 |
| Descargas | "literature and Sentinel-2; flows as wide ranges" | **JICA 2004 (tabla 1.1)** para caudales; desembocaduras de OSM `waterway` |

## Control analítico (sec. 4, tab. 2) — `scripts/prisma_marea.py` → `resultados/prisma_marea.csv`

| Magnitud | En main.tex | Actual (central, P5–P95) | Estado |
|---|---|---|---|
| Volumen | 47 (39–55) hm³ | **30.4 (27.2–34.5)** hm³ | 🔁 |
| Prisma de marea | 1.6 (1.2–2.3) hm³ | **1.47 (1.18–2.20)** hm³ | 🔁 |
| Fracción renovada por ciclo | 3.3 (2.6–5.1) % | **4.8 (3.8–7.3)** % | 🔁 |
| Renovación sin retorno | 16 (10–20) d | **10.7 (7.1–13.7)** d | 🔁 |
| Renovación con retorno + ríos | 34 (18–51) d | **23 (13–35)** d | 🔁 |
| Velocidad máx. de marea en el canal | 4.5 (3.2–6.5) cm s⁻¹ | **4.3 (3.1–6.1)** cm s⁻¹ | 🔁 |
| Excursión mareal | 650 (460–920) m | **610 (440–870)** m; 0.40 del canal | 🔁 |
| Figura `fig_prisma_marea.png` | versión vieja | regenerar en inglés con los valores nuevos | 🔁 |

Ojo: el mensaje "la excursión es menor que la mitad del canal en todas las muestras" sigue en pie (P95 0.57 → **no** en todas: corregir a "in 95 % of samples ≤ 0.57 of the channel length").

## Métodos (sec. 5) — datos ya disponibles para quitar los `\todo`

| Apartado | Cifra | Fuente |
|---|---|---|
| Batimetría | 1126 (1879) + 1514 (1887) sondeos; georreferencia RMS 18 m; registro 1898→1889 residuo mediano 1.2 m; datum incierto 0 a +0.5 m; campo aleatorio exponencial σ = 0.9 m, L = 150 m (variograma de 12 134 diferencias); estado de dragado α ∈ [0, 1] | `docs/00_estado_y_plan.md` §19 |
| Malla | 4832 nodos, 8941 triángulos; 25 m en el canal (~11 elementos a lo ancho), 40 m en la bahía, ≤ 400 m fuera; ángulo mínimo 12.4°; dominio: círculo de 5 km centrado en la boca | `datos/malla/malla_resumen.json` |
| Vertical | 16 niveles S (h_s = 210 m; profundidad del modelo topada a 200 m) — **no LSC²**: corregir el texto | `scripts/caso_real.py` |
| Tiempo | dt = 100 s; turbulencia GLS (itur = 3); Coriolis activado | ídem |
| Borde abierto | elevación armónica; esponja de fricción (Cd → 0.05) y sin viento a < 1 km del borde; sin advección de momento a < 800 m — **no Flather**: corregir | ídem |
| Edad del agua | módulo AGE de SCHISM; agua nueva = mar abierto (y ríos en los experimentos con densidad) | ídem |
| Conjunto | Saltelli, N = 64, d = 8 → 640 miembros; parámetros y rangos | `scripts/conjunto.py`, `datos/conjunto/diseno.csv` |
| Cómputo | Lemaitre4 (CÉCI), 4 + 2 núcleos por miembro, 2.7–3.9 h por 90 días simulados | `cluster/`, `coste.txt` |

## Resultados (sec. 6) — provisionales (2 miembros, M2 de prueba, sin ríos)

| Cifra | Valor | Estado |
|---|---|---|
| Caudal bruto por el canal | 64–74 m³ s⁻¹ (prisma: 66) | ⏳ |
| Edad media de la bahía, días 60–90 | 28–31 d, aún creciendo ~0.4 d/d | ⏳ (no equilibrio) |
| Edad por zona (días 60–90) | canal 15; cuenca 30–32; Marimelena 30–33; Guasabacoa 33–37; Atarés 36–41 d | ⏳ |
| Fracción de volumen con edad > 30 d | 0.55–0.76 (ensenadas ≈ 1) | ⏳ |

## Highlights

- "Tidal excursion is shorter than the entrance channel: the tide alone flushes poorly" → sigue valiendo (0.40 del canal).
