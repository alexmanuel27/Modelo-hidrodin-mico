# Para el chat del artículo — resultados del chat técnico, X1–X6 y análisis asociados (22-nov-2026)

Todo con la lectura fijada y commiteada **antes** de ver los datos; ningún umbral cambió a posteriori; solo datos públicos (ERA5, OISST, EOT20, JICA vol. V público). Las correcciones de ejecución están registradas en `docs/protocolo_*.md`. Nada contradice `docs/articulo/cifras.md`: S_T(qfac) = 0,67–0,68 a N = 64 y X5 (ρ = −0,525 frente a −0,53) se reproducen.

## Resultados (con commit)

- **X1, freno térmico (T y flujos guardados; `termico.py`): PARCIAL / NO CONCLUYENTE** (219d939 y anteriores; 4fb32ed). La repetición reproduce la m0005 (0,000 d). ρ(Δρ del canal, anomalía de edad) = −0,40 (signo coherente, no concluyente); ρ(T_bahía − T_borde, anomalía) = −0,87 (confirma: la bahía está más fría que el borde en los meses de mayor anomalía, −3,5 °C en noviembre); R3 = 0,62 (no concluyente). **El mecanismo de densidad no queda demostrado.**
- **X2, factorial 2×2 (365 d): el efecto térmico se mantiene sin viento sinóptico.** Efecto del calor +5,26 d con viento real y +5,40 d con viento climatológico (103 %); interacción +0,13 d; efecto del viento +0,82 d (sin calor) y +0,95 d (con calor). Limitaciones: la rapidez media climatológica es ≈ 0,66 de la real (< 0,6 en enero y febrero), y el viento entra en los flujos turbulentos (Q_down medio +20 frente a +41 W/m²), así que el contraste no separa solo la cantidad de movimiento.
- **ΔS–ΔT (Largier 2023, Fig. 5): INCONCLUSO** (cc8f95d). ρ(Δρ_m, G_m) = +0,39 y +0,36 (umbral +0,59). G medio en los meses hipotérmicos +0,22 d/d (n = 3) y +0,24 (n = 2) frente a ≈ −0,03 en los demás: dirección coherente con la hipótesis, pero con 2–3 meses no se puede confirmar. No contradice. Figura `fig_dst_diagram`.
- **X4, diez años (2016–2025): PARCIAL** (219d939). Desplazamiento por calor del miembro central: todos > 0 (de +0,96 d en 2020 a +6,07 en 2017; media 3,29, sd 1,62; 2016 = +4,62). Signo estable, magnitud no (rango 5,11 d). Un día de SST interpolado en 2021, 2023 y 2024 (huecos de la descarga OISST; corrección V3-4b); el rango lo fijan 2017 y 2020, con serie completa.
- **X3 (Landsat 8/9, 234 escenas 2014–2025): CONTRADICE la observación y el modelo no es compatible** (V3-3d del 17-nov y V3-3e de hoy). Landsat: T_bahía − T_mar = **+0,83 °C** en nov–mar (IC95 +0,53 a +1,13) y **+2,69 °C** en jun–sep; la bahía es **más cálida** que el mar también en la estación fría. El modelo con calor da **−2,54 °C** (fría) y **+0,00 °C** (cálida) frente al OISST del borde: **no compatible en las dos estaciones** (signo opuesto en la fría). Limitaciones: temperatura de piel a ~10:30 h con cielo despejado, píxeles de ~100 m en un canal de 250–400 m (contaminación por tierra caliente probable pero no evaluada), modelo a 1 m promediado en el día. **Es el punto débil del mecanismo térmico y hay que decirlo.**
- **Convergencia (Sarrazin et al. 2016, N = 16–64):** el **orden** de importancia converge desde N = 16 (Stat_rank 0,04 < 1) y el cribado (T = 0,05) desde N = 32; los **índices S_T no convergen** en anchura de IC95 % (≈ 0,40 en la bahía a N = 64, umbral 0,05).
- **Mapa de S_T por nodo:** qfac domina en todas las zonas y en edad de superficie y de fondo (S_T medio por área 0,52–0,68 en superficie, 0,52–0,65 en fondo).
- **Índice de bajo aporte Q_r/(W·u_t³) (exploratorio): peor que el caudal** (ρ −0,83 frente a −0,91 con la edad; tampoco mejora con el desplazamiento por calor). u_t es un sustituto (`canal_un` no existe). No incluir como resultado.
- **Salinidad superficial: el modelo está demasiado salado en superficie (hueco +4,12) y ninguna causa estructural probada lo explica.** Fase II (inyección de T/S de los ríos en la capa superior, en toda la columna, y con caudal ×1,7): cierres +0,03, +0,18 y +0,17 (H6 «no explica»). (b) ΔS fondo−superficie del canal +0,49 a +1,14 frente a [3,7; 5,5] de JICA: CONTRADICE en las cuatro. (c) velocidades en la estación 1: CONTRADICE (r = 0,22–0,23 a 5 m, por debajo de 0,25; superficie 0,60–0,69). (a) cualitativo: circulación de dos capas en el canal (superficie −7 a −9 cm/s hacia fuera, fondo +1,6 a +2,0 hacia dentro). Perfil del canal frente a JICA (tabla 4.11): 22 de 27 comparaciones dentro de ±1, pero el gradiente fondo−superficie del modelo (+0,16 a +0,41) es mucho menor que el observado (+0,79 a +3,04).
- **Hallazgo adicional:** el nivel de inyección de los ríos cambia la **edad** (R = −0,105 con la capa superior; −0,454 y −0,447 con toda la columna o con ×1,7: de 6,58 a 4,2 d). Es una elección estructural más del modelo; no explica la salinidad, pero conviene decidirla (Alex) si se menciona.

## Qué decir y qué no

- «Freno térmico»: **«consistent with»**, no mecanismo demostrado, **y el enfriamiento de la bahía que lo sostiene en el modelo no se ve en Landsat (X3)**: decirlo como limitación, sin afirmar que el satélite tenga razón (sesgo de piel y de costa posible) ni el modelo. Sí se puede decir que el efecto térmico sobre la edad **persiste sin los frentes fríos** (X2) y que la bahía está más fría que el borde en los meses de mayor anomalía (X1, R2).
- «5,4 d de desplazamiento»: es la mediana de 64 miembros en 120 d. En otros años, para el miembro central, el desplazamiento va de +0,96 a +6,07 d (todos positivos): se puede decir «el signo es estable en diez años; la magnitud varía de ≈ 1 a ≈ 6 d».
- Convergencia: «el orden de los parámetros es estable desde N = 16; las magnitudes de S_T no están acotadas con precisión (anchura del IC95 % ≈ 0,4 a N = 64)».
- Salinidad: límite declarado, **no** corregido; las causas no estructurales (lluvia, aguas residuales no modeladas, campañas de 2002 no representativas de 2016) no se han probado.

## Qué cambia en el texto (antes → después)

| Antes | Después |
|---|---|
| «el calor frena la circulación estuarina» / «freno térmico» | «consistent with a thermal effect that persists without synoptic wind variability; the density-brake mechanism is not demonstrated, and the modelled winter cooling of the bay is not seen in Landsat surface temperature (bay − sea +0.8 °C vs model −2.5 °C)» |
| desplazamiento por calor de 5,4 d como cifra general | 5,4 d (mediana de 64, 2016) y «+0,96 a +6,07 d en diez años, siempre positivo» |
| convergencia del análisis de Sobol sin más | orden estable desde N = 16; S_T de magnitud con IC ancho |
| salinidad superficial sin discutir | límite: modelo demasiado salado en superficie, no explicado por la inyección de los ríos ni por el caudal |

## Para Alex

`git push`; borrar `docs/figuras/articulo/_to_delete/` y `fig_age_growth_monthly.*` (superada); decidir si se menciona el efecto del nivel de inyección de los ríos y si se rehace algo (≈ 34 000 h-núcleo para el conjunto completo; no se lanza sin tu decisión); decidir si se hace la prueba de contaminación de costa de X3 (solo el interior de la cuenca, descarga nueva; se escribiría en el protocolo antes de ejecutarla); Zenodo/DOI, B5/B8/B9, CRediT/afiliaciones/financiación.
