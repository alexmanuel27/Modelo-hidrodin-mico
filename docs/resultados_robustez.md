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

**Adenda 9-nov: m0005 (flujo de calor con SST OISST en el borde y como T inicial, 120 d).** Edad por zona (d, días 90–120): canal 7,6 · cuenca 11,8 · Marimelena 12,9 · Guasabacoa 12,1 · Atarés 13,3 · **bahía 11,2**; deriva +0,24 d/d (sin equilibrio; media de los últimos 5 d: 12,7; mín/máx en la ventana 9,0/13,5). Menos extremo que con el borde a 28 °C (16,8), pero ×1,7 sobre la base y sin estabilizarse. `runs/robustez/m0005/resumen.json`.

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

**Adenda 14-nov — prolongación a 365 d (revisión V1, punto A1), lectura fijada ANTES de correr.** `runs/robustez_largo` (`conjunto.py robustez_largo`): m0000 (base), m0001 (flujo de calor, borde a 28 °C) y m0005 (flujo de calor + OISST), idénticos a los de 120 d salvo la duración (todo 2016, como el mecanismo). La base se prolonga también para comparar en los mismos días del año. Métricas de `posproceso.py` sin cambios (edad por zona en los últimos 30 d, deriva por regresión en los últimos 10 d) y canal sup/fondo como `analisis_conjunto.py`. **Criterio de equilibrio:** |deriva| ≤ 0,05 d/d en los últimos 10 d. **Lectura:** (1) si m0005 llega al equilibrio, su edad de la bahía en equilibrio es la cifra que sustituye a 11,2 d «sin equilibrio»; (2) si pasa de 14 d, se avisa al chat del artículo de que cambia el titular «one to two weeks» (C1–C8 del conjunto no cambian, porque el conjunto no lleva flujo de calor; lo que cambia es la frase sobre la sensibilidad al balance de calor); (3) si no llega al equilibrio a los 365 d, se informa la edad de los últimos 30 d y la deriva tal cual, sin extrapolar. La comparación con la base se hace en la misma ventana del año. Si el estado intermedio (~240 d) se mira antes, se informa como intermedio.

**Resultado de la prolongación a 365 d (15-nov; `scripts/robustez_largo.py` → `resultados/robustez_largo.txt`; lectura fijada el 14-nov, aplicada tal cual).** Edad de la bahía en los últimos 30 d (días 336–365; entre paréntesis, el valor a 120 d de la misma corrida) y deriva en los últimos 10 d: **base 6,57 d (6,6), −0,033 d/d → equilibrio** (la base de 120 d queda confirmada); **m0001 16,7 d (16,8), +0,48 d/d, sin equilibrio**; **m0005 15,4 d (11,2), +0,55 d/d, sin equilibrio**. Por zona en m0005: canal 10,4, cuenca 16,3, Marimelena 17,8, Guasabacoa 16,8, Atarés 18,2; canal superficie/fondo 12,6 / 9,9 d (a 120 d: 10,0 / 6,6). Sin extrapolación a equilibrio (el `edad_equilibrio_d_*` de `posproceso.py` supone una sola escala de tiempo y no se usa). **Lectura (2): la bahía con flujo de calor pasa de 14 d en la ventana de los últimos 30 d (m0001 y m0005) → se avisa al chat del artículo.** **Descriptivo, no pre-registrado:** con calor la edad no se estabiliza en ningún valor, sube y baja durante el año. m0005, medias mensuales ene–dic: 5,2 13,7 13,9 11,4 12,0 9,6 8,4 6,1 8,0 12,1 21,0 15,4; ventana móvil de 30 d entre 5,1 y 21,1 d (máximo en los días 309–338); 88 de 365 días con media diaria > 14 d. m0001: 4,9 11,4 17,1 17,3 9,9 5,4 4,2 4,2 5,1 9,1 20,6 16,7; ventana entre 4,2 y 21,1; 119 días > 14 d. La base es estable todo el año (medias mensuales 6,3–7,3, salvo enero 4,2 por el arranque; ventana entre 4,2 y 7,6; ningún día > 14 d). Enero es bajo en las tres por el arranque desde edad 0. En los días 1–120 (los del conjunto), la media de la serie diaria es 6,1 (base), 12,6 (m0001) y 11,0 (m0005). No se ha investigado la causa de las oscilaciones con calor; ninguna explicación (estratificación, enfriamiento, frentes) está comprobada.

**Prueba de la causa de los ~6 m/s en el borde abierto (revisión V1, A9; decisión de Alex del 15-nov), lectura fijada ANTES de lanzar.** `runs/borde_prueba` (`conjunto.py borde_prueba`, `scripts/borde_prueba.py`): miembro central, 10 d, EOT20 y ríos: m0000 control (Coriolis y viento), m0001 sin Coriolis (`NCOR=0`), m0002 sin viento (`NWS=0`). Hipótesis (de las pruebas de octubre con la malla esquemática, bitácora): una inestabilidad del borde con Coriolis, nivel impuesto y viento que sube hasta que `rmaxvel = 5 m/s` la topa. **Lectura:** (0) el control es válido solo si reproduce `vmax ≥ 4,5 m/s` (el P5 del conjunto) en un nodo del borde abierto en los 10 d; si no, la prueba no es concluyente (puede hacer falta más tiempo) y se dice. (1) Una variante «quita» la velocidad si su `vmax` es < 50 % del control y < 3 m/s. (2) Si solo la quita sin Coriolis, la frase dice que depende de Coriolis; si solo la quita sin viento, que depende del viento; si ambas, que requiere los dos; si ninguna, la causa no es ninguna de las dos y se retira la hipótesis. Apagar Coriolis o el viento cambia la física de toda la corrida: es un diagnóstico, no un caso para el artículo.
