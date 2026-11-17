# Para el chat del artículo — cierre de PENDIENTES_V2 (17-nov-2026)

Sustituye a `para_chat_articulo_16nov_v2.md` (que se queda como histórico: tenía cifras de 16 miembros y costes estimados). Todo se hizo con la lectura fijada y commiteada antes de ver datos; ningún umbral cambió. Lecturas: a553d4d (protocolo 16-nov (3) y (4)). Resultados: 89da8ba (B2), d2d7682 (B4). Cifras y figuras: 96adee1 y el commit de este archivo.

## 1. Cifras que cambian (antes → después)

| Cifra | V2 (16 miembros) | Ahora (64 miembros) |
|---|---|---|
| Mediana de la bahía con calor (P5–P95) | 13,8 d (9,2–17,7) | **13,2 d (8,3–18,4)** |
| Mediana sin calor, mismos miembros | 7,4 d (5,9–10,4) | **7,6 d (5,5–10,7)** |
| Desplazamiento por el calor | 6,4 d (diferencia de medianas) | **5,4 d (pareado)**; calor mayor en 64/64 |
| Comparación con el rango paramétrico | 6,4 d frente a 4,8 d (16 frente a 128) | **5,4 d frente a 5,25 d (mismos 64), R = 1,03 → «del mismo orden»** |
| C1 y C4 con calor | 0,94 (15/16) | **0,91 (58/64)**, robustas por poco |
| C3 (Marimelena > cuenca) | 0,69 → 1,00 | **49/64 → 64/64** (frágil → robusta) |
| P(edad > 7 d) | 0,56 → 1,00 | **42/64 → 63/64** (frágil → robusta) |
| P(edad > 14 d) | 0,00 → 0,44 | **0/64 → 27/64** (rechazada → frágil) |
| P(edad > 30 d) | 0 → 0 | **0/64 → 0/64**; máximo con calor 24,4 d (un miembro) |
| En equilibrio (|deriva| ≤ 0,05 d/d) | 14/16 → 0/16 | **59/64 → 1/64** |
| Caudal con calor, ρ(edad, qfac) | −0,80 (no separable de la marea, ρ diseño +0,93) | **−0,79** (sin calor −0,91); ρ parcial qfac\|mfac −0,79, mfac\|qfac −0,13 (ρ diseño 0,00) |
| Marea EOT20 frente a FES2022 | «< 0,4 cm» | **«como mucho 0,4 cm»** (máx. 0,37, O1) |

Sin cambios (365 d, `robustez_largo`): edad media anual base 6,5 d, calor + 28 °C 10,5, calor + OISST 11,4; días > 14 d 0, 119 y 88 de 365; media de 30 d con calor + OISST 5,1–21,1 d; medias mensuales con calor + OISST 5,2 (ene) … 21,0 (nov), mínimo 6,1 en agosto (base 6,3).

## 2. Mecanismo (B2): resultado parcial

Proxy bulk del flujo neto (SST OISST, coeficientes constantes; **no es el flujo de SCHISM**) frente a la edad diaria de 365 d. m0005: T1 (enfriamiento → crecimiento de la edad, bloques de 5 d) +0,32, confirma por 0,02; control sin calor −0,01; T2 (mensual feb–dic) +0,75, confirma; **T3 (separar del viento) +0,14 < 0,25, no se cumple → veredicto parcial.** Réplica m0001: +0,51, +0,66, +0,33. El proxy da un balance anual de −18,5 W/m² (calor latente 148 W/m², probablemente sobreestimado): se usa solo por rangos. No hay Δρ del canal. Con calor, en los 64, ρ(edad, vfac) = −0,35 (descriptivo), coherente con que el viento pesa.

## 3. Frases en inglés

- **Heat-flux ensemble:** «Repeating the 64 members of block A with the air–sea heat flux and the OISST boundary temperature raised the bay-mean age in every member (64/64): the median rose from 7.6 d (P5–P95 5.5–10.7 d) to 13.2 d (8.3–18.4 d), a paired median shift of 5.4 d, of the same order as the 5.3-d P5–P95 range spanned by all nine parameters in the same members.»
- **Classes:** «With the heat flux three conclusions change class: Marimelena older than the central basin (49/64 → 64/64) and P(age > 7 d) (42/64 → 63/64) become robust, and P(age > 14 d) moves from rejected (0/64) to fragile (27/64). The along-bay ordering and the inner arms being older than the basin remain robust, but only just (58/64). No member exceeded 30 d.»
- **Discharge, not tide:** «River discharge remains the dominant parameter with the heat flux (Spearman ρ = −0.79, −0.91 without it). In these 64 members discharge and tidal amplitude are uncorrelated by design, and the effect is that of discharge (partial ρ = −0.79 for discharge given tidal amplitude, −0.13 for tidal amplitude given discharge).»
- **Year-long run:** «Over 2016, with the heat flux and the OISST boundary, the bay-mean age averaged 11.4 d (6.5 d without heat flux), exceeded 14 d on 88 of 365 days (none without), and its 30-day mean ranged from 5.1 to 21.1 d, peaking in November (21.0 d) and lowest in August (6.1 d; 6.3 d without heat flux).»
- **Mechanism:** «The age with the heat flux is highest in the months of negative net surface heat flux and stronger winds (October–March), but in this single year-long series cooling and wind stress cannot be separated; the pattern is consistent with, but does not demonstrate, a weakening of the estuarine circulation by winter cooling. The surface–bottom density difference in the channel, which would test this, was not stored.»
- **Scope:** «The heat-flux ensemble covers January–April 2016 (120 d, last 30 d). With the heat flux the age does not reach a steady state, so the 30-d window is one of several possible and the result is not extrapolated to other seasons.»

## 4. Figuras (en `docs/figuras/articulo/`)

- `fig_heatflux.{png,pdf}`: panel (b) ahora con los 64 miembros (antes 16); panel (a) igual. Pie: «(b) 64 members of block A …».
- `graphical_abstract.{png,pdf}`: titular «About one week without the heat flux, about two weeks with it, never months»; naranja = 64 con calor; barra en días «paired median shift» 5,4 frente a «P5–P95 range (same 64)» 5,3 (5,25 redondeado), separada de los S_T.

## 5. Tabla 4

Columna con calor de la Tabla 4 en fracciones n/64 (sección 1). C8 (Sobol) no se evalúa con calor: no hay matrices AB_i; el orden de parámetros va por Spearman.

## 6. Coste (medido)

Conjunto con calor: 64 miembros × ≈ 49 core-h = **≈ 3.100 core-h**. Tres corridas de 365 d: 120 + 133 + 126 = **≈ 380 core-h**. Conjunto principal: ≈ 54.000. Sigue pendiente de Alex el total de horas-núcleo del proyecto.

## 7. Pendientes (de Alex)

`git push`; total de horas-núcleo; Zenodo/DOI y enlace al repo; B5 (datos de observación), B8 (Ponce Portela: volumen, número, año, páginas), B9 (enlaces del repositorio y Sentinel-2); CRediT, afiliaciones y financiación. En reserva: repetir m0005 con T, S, flujos y estaciones del canal (≈ 130–180 core-h) solo si se quiere afirmar el mecanismo.
