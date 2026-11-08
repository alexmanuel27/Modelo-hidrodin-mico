# Robustez de la circulación por densidad (5 experimentos, 120 d, 2016) — resultados

Miembro central con ríos de JICA (2,14 m³/s) y densidad. Se cambia una cosa cada vez (`conjunto.py robustez`).
Corridas en Lemaitre4 entre el 1 y el 4-nov-2026, en tramos de 10 d; ninguna con NaN.
Figura: `docs/figuras/robustez.png`. Datos: `runs/robustez/m000{0..4}/resumen.*` (no versionados).

## Edad media del agua (días, días 90–120)

| Zona | Base | k-ε | 32 niveles | Difusividad ×10 | **+ flujo de calor** |
|---|---|---|---|---|---|
| Canal | 4,0 | 4,4 | 4,9 | 4,1 | **11,5** |
| Cuenca | 6,7 | 7,0 | 7,5 | 6,7 | **17,9** |
| Marimelena | 7,0 | 7,1 | 7,5 | 7,1 | **19,3** |
| Guasabacoa | 7,6 | 8,0 | 8,7 | 7,6 | **18,1** |
| Atarés | 8,8 | 9,4 | 10,0 | 8,8 | **19,5** |
| **Bahía** | **6,6** | **6,9** | **7,5** | **6,6** | **16,8** |
| Deriva al final (d/d) | +0,02 | +0,01 | +0,01 | +0,03 | **−0,10** (no estable) |
| Canal: edad sup / fondo | 6,6 / 1,8 | 6,7 / 2,1 | 7,5 / 2,3 | 6,6 / 1,9 | 14,2 / 10,6 |

## Lectura

1. **Robusta frente a la turbulencia y la resolución vertical.** Con otro cierre (k-ε), con el doble de niveles o con
   10 veces más mezcla de fondo, la edad de la bahía queda en 6,6–7,5 d. La firma estuarina del canal (superficie más
   vieja que el fondo) se mantiene en todos. El orden de las zonas tampoco cambia.
2. **Frágil frente al balance de calor.** Con el flujo de calor aire-mar de ERA5, la edad sube a 16,8 d (×2,5). Crece
   hasta ~22 d hacia el día 90 y luego baja: no está en equilibrio. La diferencia entre superficie y fondo del canal casi
   desaparece (14,2 / 10,6 d), así que la circulación estuarina se debilita.
3. **Ojo, puede ser un artefacto de cómo está montado el experimento.** El borde abierto tiene la temperatura fija en
   28 °C y no hay datos de temperatura del mar en el modelo. En enero–abril la atmósfera de ERA5 enfría la bahía somera
   frente a un mar que se mantiene a 28 °C. El agua de la bahía se vuelve más densa y contrarresta la flotabilidad del
   agua dulce. En la realidad el mar también se enfría en invierno (POR CONFIRMAR con datos de SST). La prueba honesta
   pide una temperatura de borde y una inicial realistas: SST pública (NOAA OISST o ERA5).
4. **Caudal bruto con 32 niveles: 90 m³/s frente a 70 en las demás.** No se explica por el prisma. Análisis de la serie Q guardada (6-nov, `resumen.npz`, muestreo cada 4 h, últimos 30 d, 180 instantes):
   la diferencia viene de 7 instantes con |Q| > 300 m³/s (máx. 932; la base tiene 2 y máx. 370). Sin ellos la media es 72 frente a 67 m³/s.
   La correlación entre las series de Q de ambas corridas es solo 0,37 pese a tener el mismo forzamiento. No sabemos si los picos son
   físicos o numéricos (POR CONFIRMAR con `scripts/diag_caudal.py`, que lee `out2d`). Ojo: solo conservan `out2d` los miembros de `GUARDAR` (0, 1, 2); m0003 (32 niveles) no, así que habría que repetirlo conservando los campos. Hasta entonces, no usar la cifra de 90 m³/s.
   Diagnóstico en la base m0000 (7-nov, `scripts/diag_caudal.py`; el Q recalculado desde `out2d` coincide con el guardado): los 8 mayores
   picos (hasta 370 m³/s) no son de un nodo, sino de toda la sección (ningún punto aporta más del 9 %). Valen 3–10 veces el cambio de
   volumen de la bahía entre instantes vecinos y 2–4 veces el flujo mareal M2 estimado (~100 m³/s: 4,7 km² × 2π·0,15 m / 44 700 s).
   Hipótesis, POR CONFIRMAR: una oscilación bahía–canal de periodo ~1 h (estimación gruesa de Helmholtz: ~53 min) que el muestreo de 4 h
   solo ve en parte; entonces la media de |Q| depende del muestreo y no es una cifra robusta. Además Q usa la velocidad promediada en
   vertical, así que la circulación estuarina (superficie hacia fuera, fondo hacia dentro) se anula y el caudal bruto no mide ese
   intercambio. La sección está a mitad del canal: 0,26 km² de canal quedan del lado del mar y el diagnóstico los cuenta como bahía (~5 %).
   8-nov, día 121 de la base con salida cada 10 min (`cluster/hf_caudal.sh`, `diag_caudal.py --hf`): sin oscilación de ~1 h
   (varianza por debajo de 2 h: 0 %; 88 % en la banda semidiurna). La hipótesis no se sostiene ese día y los picos siguen sin
   explicar. Muestrear cada 4 h cambia la media diaria de |Q| en ±15 % según la fase.

## Para el artículo

- La renovación de ~1 semana es robusta a la turbulencia, a la resolución vertical y a la mezcla de fondo. Depende del
  balance de densidad: con calor (y borde a 28 °C) se alarga a ~2–3 semanas. **Conclusión frágil**, que hay que contar
  como tal.
- El conjunto de 704 miembros no tiene flujo de calor. Sus conclusiones son condicionales a "densidad solo por salinidad".
