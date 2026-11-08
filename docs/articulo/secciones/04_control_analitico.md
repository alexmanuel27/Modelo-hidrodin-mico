# 4. Control analítico: prisma de marea

`scripts/prisma_marea.py` (Monte Carlo, 2·10⁵ muestras; A = 4,91 km², h = 5,2–7,3 m, entradas triangulares; **marea: días reales de un año sintetizado con los 9 armónicos de EOT20** frente a la boca — 1,93 llenantes por día, subida diaria total 0,26/0,54/0,78 m y mayor llenante 0,18/0,33/0,50 m en P5/P50/P95; ríos 2,14 m³ s⁻¹ (1–5), JICA 2004) → `resultados/prisma_marea.csv`, figura `../../../resultados/prisma_marea.png` (en español, regenerar en inglés).

| Magnitud | Central | P5–P95 |
|---|---|---|
| Volumen | 30,7 hm³ | 27,2–34,5 |
| Prisma de la mayor llenante del día | 1,6 hm³ | 0,9–2,5 |
| Fracción del volumen que entra por día | 8,7 % | 4,1–12,7 |
| Renovación sin flujo de retorno | 11,6 d | 7,9–24,5 |
| Renovación con retorno + ríos | 24 d | 14–47 |
| Solo ríos (V/Q) | 136 d | 83–243 |
| Velocidad máx. de marea en el canal | 4,7 cm s⁻¹ | 2,7–7,3 |
| Excursión mareal en el canal | 630 m | 340–960 |
| Excursión / longitud del canal | 0,41 | 0,22–0,63 |

(Columna "Central" = mediana del Monte Carlo, columna p50 de `prisma_marea.csv`; el "caso central" del csv es otra cosa: 30,4 hm³. Con la marea real el prisma se cuenta por día — dos llenantes de tamaño distinto la mayoría de los días — y no por ciclo M2.)

- Mensaje que se mantiene, ahora con la marea real: la excursión mareal es menor que el canal (≤ 0,63 de su longitud en el 95 % de los días/muestras, 100 % por debajo de 1), así que el agua que sale en vaciante no lo llega a dejar atrás antes de que vuelva la llenante y la marea sola renueva mal.
- La excursión es volumen / sección, proporcional al **rango** de la llenante, no a su periodo: que la marea sea mixta (diurnas ≈ semidiurnas) no la alarga por sí mismo; solo cambia la distribución de rangos (días tropicales/sicigias hasta ~0,5 m, mediana 0,33 m, parecida al 0,30 supuesto antes). Por eso las cifras casi no cambian respecto a la versión con rango supuesto (23 → 24 d), pero las colas se abren (P95 35 → 47 d).
- **Contraste con el modelo** (actualizado 7-nov; sec. 6 y `../cifras.md`): el control (24 d, 14–47) queda **entre** los dos regímenes del modelo. Con solo marea el modelo renueva mucho más despacio (edad de la bahía 166 d al año, sin equilibrio): el factor de retorno real es casi 1 y el control lo infravalora. Con ríos y densidad renueva mucho más rápido (6,6 d): el intercambio lo hace la circulación gravitacional, que el prisma no contiene. Mensaje: el prisma no acierta por ninguno de los dos lados, porque el mecanismo que domina no es la marea.
- El "caudal de marea del modelo = prisma (64–74 frente a 66 m³ s⁻¹)" del borrador queda **en suspenso**: el caudal bruto del modelo depende del muestreo de 4 h (avisos en `../cifras.md`). No usarlo hasta la prueba de alta frecuencia.
- Figura: `resultados/prisma_marea.png` ya está en inglés con los valores nuevos (21-oct); la de `articulo/figuras/fig_prisma_marea.png` es la vieja → copiarla.
