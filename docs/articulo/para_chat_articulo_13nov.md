# Del chat técnico al chat del artículo (13-nov-2026)

Fuente de cada número: `docs/articulo/cifras.md` del repo de trabajo. Nada de esto contradice cifras.md (se ha actualizado hoy).

## 1. Conjunto de 704 (sin cambios desde el 9-nov)
- Terminados 704/704. Distribuciones y probabilidades con los bloques A+B = 128 miembros; **117 de 128 en equilibrio** (|deriva| ≤ 0,05 d/d), 11 no; las clases son las mismas con solo los 117.
- Clases (fracción de los 128): C1 orden canal < cuenca < Guasabacoa < Atarés 1,00 robusta · C2 Atarés más vieja que el canal 1,00 robusta · **C3 Marimelena más vieja que la cuenca 0,76 frágil** · C4 1,00 robusta · C5 bahía < 30 d 1,00 robusta · C6 bahía < 120 d 1,00 robusta · C7 canal superficie más vieja que el fondo 1,00 robusta · P(bahía > 7 d) 0,68 frágil · > 14 d 0 rechazada · > 30 d 0 rechazada.
- Edad media (últimos 30 d), mediana (P5–P95) y P(> 7 / 14 / 30 d): canal 4,6 (3,2–6,4) 0,02/0/0 · cuenca 7,7 (5,6–10,2) 0,69/0/0 · Marimelena 8,1 (6,3–10,4) 0,82/0/0 · Guasabacoa 9,1 (6,4–12,5) 0,85/0/0 · Atarés 10,5 (7,3–14,6) 0,96/0,11/0 · **bahía 7,8 (5,6–10,4) 0,68/0/0**.
- Sobol (Jansen, N = 64, bootstrap 1000), caudal de los ríos (qfac), S1 y S_T (IC 95 %): bahía 0,86 (0,80–0,90) / **0,67 (0,49–0,89)**; canal 0,86 / 0,70 (0,51–0,91); cuenca 0,86 / 0,67 (0,47–0,87); Marimelena 0,76 / 0,56 (0,38–0,80); Guasabacoa 0,85 / 0,67 (0,49–0,87); Atarés 0,84 / 0,67 (0,50–0,90). Segundo en todas las zonas: campo de error de la carta, S_T 0,09–0,14. Todos los demás S_T ≤ 0,05 en la bahía. **C8 = caudal de los ríos.** Cautela para el pie: con N = 64 los IC de S1 de los parámetros sin efecto son de ±0,3, y S_T < S1 del caudal es ruido del estimador. Tabla completa: `resultados/conjunto/sobol.csv`.
- Figuras: `fig_ensemble` (190 × 72 mm) y `fig_sobol` (190 × 80 mm), PNG 300 ppp + PDF, en `docs/figuras/articulo/`.
- Horas-núcleo: **≈ 1,7·10⁵ asignadas** (sacct, 24-oct a 9-nov, todo incluido: conjunto, mecanismo, robustez, pruebas, cortes y esperas) y **≈ 5,4·10⁴ de cómputo útil de los 704** (estimación: 76 h-núcleo por miembro × 704). Decid cuál se cita; las dos son reloj × núcleos asignados, no CPU usada.

## 2. Robustez m0005 (calor con SST OISST)
- Edad por zona (ponderada por volumen, días 90–120): canal 7,6 · cuenca 11,8 · Marimelena 12,9 · Guasabacoa 12,1 · Atarés 13,3 · **bahía 11,2 d**; **canal superficie / fondo 10,0 / 6,6 d** (nuevo); deriva +0,24 d/d, **sin equilibrio** (últimos 5 d 12,7; oscila 9,0–13,5).
- T_f de m0005: **no disponible** (el clúster no conserva sus campos de salinidad; haría falta repetir la corrida). No escribir T_f para m0005.
- Lectura: «≈ 1 semana» es **robusta** a turbulencia, resolución vertical y mezcla (6,6–7,5 d) y **frágil frente al balance de calor**: con SST real 11,2 d (× 1,7) y sin estabilizarse. El 16,8 d con el borde a 28 °C **no era solo un artefacto**: con la SST real el efecto baja, pero no desaparece. El orden de las zonas no cambia (C1 y C3 se cumplen en m0005).
- `fig_robustness` (90 × 62 mm) ya incluye m0005.

## 3. Figuras (todas en `docs/figuras/articulo/`, inglés, tamaño final)
- **Resumen gráfico**: `graphical_abstract.png/.pdf`, 1535 × 590 px (13 × 5 cm a 300 ppp).
- **S1**: `figS_boundary` (190 × 66 mm). Ya no es solo el borde: (a) dónde está la velocidad máxima de cada miembro; (b) la del dominio frente a la edad de la bahía; (c) la de dentro de la bahía frente a la edad. Cifras para el pie: el máximo está en el borde abierto en el 94 % de los miembros (P50 6,0 m/s, a 4–5 km de la boca), sin relación con la edad (ρ = −0,07). **Nuevo, para limitaciones:** en 68 de 704 miembros la velocidad dentro de la bahía pasa de 3 m/s (hasta 6,9 m/s) en nodos de 0,3–0,5 m de fondo, donde SCHISM toca su límite de velocidad (`rmaxvel`); sin relación con la edad (ρ = −0,04), y quitando esos miembros ninguna clase cambia (bahía 7,73 frente a 7,78 d, P(> 7 d) 0,69 frente a 0,68, C3 0,78 frente a 0,76).
- **S3: no sale.** El caudal bruto por el canal tiene ráfagas intermitentes de origen no aclarado; no es un resultado. Quitarla; como mucho una frase en limitaciones (el estado de hf_caudal no ha cambiado).
- **Sondeos (suplementaria)**: `figS_soundings` (190 × 88 mm), una figura con dos paneles en UTM 17N: (a) los 1126 sondeos de la ed. 1889 (levantamientos hasta 1879) por profundidad, con las lecturas dudosas marcadas; (b) posiciones de 1879 (1126) y 1887 (1514). Pie: los sondeos de 1887 (ed. 1898) se dibujan sobre la carta de 1889, misma plancha.
- Fig. 8 (`fig_rivers`) ya enviada.

## 4. Confirmaciones
- **Tolerancia del transporte (`eps1_tvd_imp`):** no se repite el conjunto ni m0005. Caso central con 1e-9 en lugar de 1e-4: **edad +3,7 a +5,6 % por zona (bahía 6,58 → 6,91 d)**, T_f −3 % (1,94 → 1,88 d; «1,8–2,0 d» se mantiene), ρ de Sentinel-2 0,450 → 0,449 (se mantiene), R1–R4 iguales. No se sabe cuál de las dos tolerancias es más exacta. Escalando el conjunto con ese cambio (aproximación, no una corrida), ninguna clase cambia (bahía 7,8 → 8,2 d; P(> 7 d) 0,68 → 0,76, sigue frágil; P(> 14 d) sigue 0; C3 0,76 → 0,66, sigue frágil). Propuesta para limitaciones: «incertidumbre numérica de la edad ≈ 5 % por la tolerancia del solver de transporte, pequeña frente a la dispersión del conjunto». **Ojo con la frase de la desviación de T1** que os pasé: la explicación «la tolerancia deja la salinidad menos resuelta» no se sostiene del todo (con 1e-9 el control del caso central empeora, 2,2 → 4,4 %). Esperad a la decisión de Alex antes de escribirla; lo que sí se sostiene es que R1–R4 no cambian con la tolerancia.
- **Hashes de los protocolos** (repo privado; solo verificables si se publica el historial o se depositan en Zenodo):
  - Sentinel-2: texto `773b9fb` (21-oct), congelado `fb8ad7d` (21-oct); control por desplazamientos `231696a` (26-oct).
  - Métricas C1–C8: texto `4564b7e` (commit del 26-oct, aprobado por Alex el 27-oct); cabecera «congelado» `8f3bf73` (8-nov).
  - Trazadores: borrador `cf63c26`, aprobado y congelado `3907fd7` (8-nov). Desviación de T1 aceptada por Alex el 13-nov (registro del protocolo).
  - Hashes completos en `docs/articulo/README.md`.
- **hf_caudal:** sin cambios.
- **README y cifras.md:** al día (13-nov); el README ya no manda reescribir las secciones 5–7.

## 5. Datos y repositorio
Decisiones de Alex, sin cambios: repo público, DOI de Zenodo del código y de los datos, depósito de las salidas del conjunto, DOI del producto Sentinel-2 y cómo probar las fechas de congelación.

## 6. Referencias (metadatos comprobados en OpenAlex; **el contenido no lo he leído**: comprobad que dicen lo que la frase necesita)
- GEBCO: GEBCO Bathymetric Compilation Group 2026 (2026). The GEBCO_2026 Grid – a continuous terrain model for oceans and land at 15 arc-second intervals. NERC EDS British Oceanographic Data Centre NOC. doi:10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa (de gebco.net; no he abierto el DOI).
- FES2022: Lyard, F., Carrère, L., Fouchet, E., et al. (2026). FES2022 global tide atlas: a step towards SWOT-compliant tidal corrections. EGUsphere (preprint en discusión), doi:10.5194/egusphere-2026-6805. Producto: AVISO FES2022b, doi:10.24400/527896/A01-2024.004.
- Candidatas para las tres citas de la introducción:
  - Pocos datos: Payandeh, A.R., Simard, M., et al. (2026). A fully satellite-driven workflow for hydrodynamic modeling in data-scarce coastal systems. Frontiers in Remote Sensing, doi:10.3389/frsen.2026.1751006 · do Amaral, F.R., Camenen, B., et al. (2025). Operational calibration… 1D hydrodynamic model in a data-scarce coastal area. HESS 29, doi:10.5194/hess-29-4327-2025.
  - Incertidumbre y sensibilidad: Saltelli, A., et al. (2019). Why so many published sensitivity analyses are false. Environ. Model. Softw. 114, 29–39, doi:10.1016/j.envsoft.2019.01.012 · Uusitalo, L., et al. (2015). An overview of methods to evaluate uncertainty of deterministic models in decision support. Environ. Model. Softw. 63, 24–31, doi:10.1016/j.envsoft.2014.09.017.
  - Contaminación de la bahía: Díaz-Asencio, M., et al. (2011). Reconstruction of metal pollution and recent sedimentation processes in Havana Bay (Cuba). J. Hazard. Mater., doi:10.1016/j.jhazmat.2011.09.037.
