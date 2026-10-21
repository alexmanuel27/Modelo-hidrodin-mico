# 4. Control analítico: prisma de marea

`scripts/prisma_marea.py` (Monte Carlo, 2·10⁵ muestras, entradas triangulares; A = 4,91 km², h = 5,2–7,3 m) → `resultados/prisma_marea.csv`, figura `../../../resultados/prisma_marea.png` (en español, regenerar en inglés).

| Magnitud | Central | P5–P95 |
|---|---|---|
| Volumen | 30,4 hm³ | 27,2–34,5 |
| Prisma de marea | 1,47 hm³ | 1,18–2,20 |
| Fracción renovada por ciclo | 4,8 % | 3,8–7,3 |
| Renovación sin flujo de retorno | 10,7 d | 7,1–13,7 |
| Renovación con retorno + ríos | 23 d | 13–35 |
| Velocidad máx. de marea en el canal | 4,3 cm s⁻¹ | 3,1–6,1 |
| Excursión mareal en el canal | 610 m | 440–870 |
| Excursión / longitud del canal | 0,40 | 0,29–0,57 |

- Mensaje que se mantiene: la excursión mareal es menor que el canal, así que el agua que sale en vaciante no lo llega a dejar atrás antes de que vuelva la llenante y la marea sola renueva mal. Matiz: "≤ 0,57 de la longitud del canal en el 95 % de las muestras", no "menos de la mitad en todas".
- **Contraste con el modelo** (sec. 6): el modelo da el mismo caudal de marea por el canal (64–74 frente a 66 m³ s⁻¹), pero una renovación mucho más lenta que los 23 d (la edad sigue creciendo a los 90 d), en línea con los ~4 meses de JICA. El control con factor de retorno parece **sobrestimar** la renovación → punto de discusión.
