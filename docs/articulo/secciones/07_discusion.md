# 7–8. Discusión y conclusiones: material (actualizado 7-nov-2026)

Ideas con su apoyo, no texto. Subsecciones de `main.tex`.

## 7.1 Robust and fragile conclusions

- **Robustas ya** (mecanismo + robustez): la marea sola no renueva la bahía; el orden canal < cuenca < Guasabacoa < Atarés; la firma estuarina del canal (superficie más vieja que fondo) con densidad.
- **Frágiles ya:** la posición de Marimelena; la escala de renovación con densidad frente al balance de calor (6,6 → 16,8 d, ⏳ SST real).
- **El veredicto formal** (≥ 90 % / 10–90 % / ≤ 10 % de los miembros) lo da el conjunto ⏳.

## 7.2 "Why the tidal prism overstates flushing" → hay que replantearla

- Solo vale para la marea sola: el prisma (24 d) es más optimista que el modelo con solo marea (166 d) porque supone un retorno parcial y en realidad casi todo el agua vuelve.
- Con densidad pasa lo contrario: el modelo renueva en ~1 semana, más rápido que el prisma, porque el intercambio lo hace la circulación gravitacional.
- Mensaje posible: un control basado en la marea se equivoca en las dos direcciones; en una bahía con poca marea manda la densidad.

## JICA 2004 ("tiempo de retención del agua dulce ≈ 4 meses", p. R-7)

- **No es la misma magnitud que la edad del modelo.** La edad cuenta el agua de los ríos como agua nueva; JICA habla de retención del agua dulce y no da el método en el resumen. Comparar la edad (~7 d) con los 4 meses (C6 del protocolo) compara magnitudes distintas.
- **La comparable es el tiempo de renovación del agua dulce** T_f = V_f / Q (método de la fracción de agua dulce). Cota con la salinidad de superficie: ≲ 4 d. Exacta con `scripts/renovacion_dulce.py` ⏳. Si se confirma, el choque con JICA es aún mayor que con la edad.
- Hipótesis sobre JICA (sin confirmar): V/Q sin intercambio. Con sus 47 hm³ y 4 meses saldría Q ≈ 4,5 m³/s, el doble de los ríos aforados (¿con drenajes y aguas residuales?).
- Causas posibles de la diferencia, todas declaradas: caudal real (una campaña de 2002; aguas residuales sin aforar); mezcla vertical (la robustez dice que la edad apenas cambia con el cierre, los niveles o la mezcla de fondo); falta de flujo de calor y de E − P (⏳ SST real); método de JICA desconocido.

## 7.3 What to measure first

- ⏳ ranking de Sobol. Mientras tanto: el caudal real de los ríos y aguas residuales (si domina el ST) y un perfil de salinidad en el canal (comprueba la circulación estuarina con un solo dato).

## 7.4 Limitations

- Densidad solo por salinidad en el conjunto; sin flujo de calor ni E − P.
- Solo enero–abril de 2016 (estación seca, frentes fríos); sin variabilidad interanual.
- Caudales de una sola campaña (2002), sin aguas residuales.
- Caudal por el canal no usable (neto con error ±6 m³ s⁻¹; bruto dependiente del muestreo).
- Sentinel-2 solo comparte el gradiente boca → cabeceras: no hay validación independiente.
- N = 64: índices S1 con IC anchos.

## 7.5 Transferability

- Cadena entera con datos públicos (cartas del XIX, GEBCO, OSM, ERA5, EOT20, OISST) y código abierto; protocolos congelados antes de ver resultados.

## 8. Conclusions

- Escribir al final, cuando esté el conjunto.
