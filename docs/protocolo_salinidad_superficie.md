# ¿Por qué el modelo es demasiado salado en superficie? Protocolo CONGELADO

> **Congelado el 18-nov-2026**, antes de calcular nada de lo que sigue. Contexto: frente a JICA 2002, la salinidad en superficie del conjunto
> (media de las 11 estaciones de la fig. 4.25) es 35,4 (P5–P95 35,0–35,7) frente a 32,2 ± 1,0 (creciente) y 30,3 ± 3,5 (bajamar) en
> diciembre de 2002, y ΔS fondo−superficie es +0,28 frente a [3,7; 5,5] (`docs/protocolo_jica_observaciones.md`, registro del 18-nov).
> Solo datos públicos y corridas ya existentes en esta primera parte. Cualquier cambio posterior va solo en el registro fechado del final.

## 1. Cantidad y hueco
**S11** de un miembro = media de las dos medias de fase (creciente y bajamar, nodo más cercano, mínimo 3 mapas por fase) de la salinidad en superficie,
S = 36 · (1 − fracción de agua dulce), de las 11 estaciones, con los mapas de las 16:00 UTC de los días 91–120 (`resumen.npz`; mismo cálculo que
`scripts/jica_compara_modelo.py`). **Observada de referencia** S_obs = (32,2 + 30,3) / 2 = 31,25. **Hueco** del control = mediana de S11 del conjunto (704)
− 31,25. **Cierre** de una variante = (S11_control − S11_variante) / hueco, con el control y la variante pareados.
Lectura común: **«explica»** si el cierre ≥ 0,5; **«parcial»** si 0,25 ≤ cierre < 0,5; **«no explica»** si < 0,25 (incluye que la variante dé más sal).

## 2. Hipótesis que se prueban con lo que ya existe (sin corridas nuevas)
- **H1, el caudal de los ríos.** Regresión sobre los 704 miembros: S11 = b0 + Σ b_i x_i + c1 ln qfac + c2 (ln qfac)², con los 9 parámetros del diseño (`jica_caudales_extra.disenyo`).
  Se resuelve qfac para S11 = 31,25 con el resto de parámetros en su media. **«No es cuestión de caudal»** si qfac > 4 (el doble del máximo muestreado, 8,6 m³/s) o no hay solución; **«marginal»** si
  está entre 2 y 4; **«explica»** si ≤ 2. Es una extrapolación fuera del rango 0,25–2 y se informa como tal.
- **H4, los tres drenajes que faltan (+70 % de caudal, F = 1,70).** Cambio de S11 predicho por la misma regresión al pasar de qfac a 1,70 · qfac, mediana sobre los miembros con qfac ≤ 2/1,70;
  cierre = cambio / hueco, con la lectura común.
- **H2, la mezcla vertical.** Con `runs/robustez` (miembro central, 120 d): m0002 (cierre k-ε), m0003 (32 niveles), m0004 (difusividad mínima ×10) frente a m0000 (base); cierre de cada una con la lectura común.
- **H3, el flujo de calor.** (i) `runs/robustez` m0001 (calor, borde 28 °C) y m0005 (calor + OISST) frente a m0000; (ii) los 64 pares de `runs/conjunto_calor` frente a `runs/conjunto` (miembros 0–63), cierre mediano y rango.
- **Control de muestreo.** Para m0000–m0002 del conjunto, S11 con los mapas de las 16:00 UTC frente a S11 con las 175 muestras de `jica_estaciones.npz` (media de las dos fases del ajuste armónico).
  Si la diferencia absoluta es ≥ 0,3, el muestreo a las 16:00 UTC no es representativo y se informa.
- **Dónde está el hueco (sin veredicto).** Salinidad en superficie media por zona (zona 1 canal, 2 cuenca, 3 Marimelena, 4 Guasabacoa, 5 Atarés; media de `dulce_sup` ponderada por área, últimos 30 d) de los 704 frente a la tabla 4.11 de noviembre de
  2001 (promedio de pleamar y bajamar; Centro = cuenca): fracción de los 704 dentro de [mín − 1, máx + 1] de los dos valores observados en cada zona. Y fracción de los 704 con S de bahía < 34,3 (máximo mensual de la tabla 4.12, UNESCO, vía JICA).
  La estación de noviembre de 2001 es otro año y otra época; solo dice si el hueco es de toda la bahía o de una zona.

## 3. Qué se concluye
Si ninguna de H1–H4 da «explica» y la suma de los cierres independientes de H4 y H2 (las que dan cierre positivo) es < 0,5, la diferencia **no se debe a ninguno de los parámetros ni procesos probados con lo existente**
y pasa a causas estructurales que solo se prueban con corridas nuevas (fase II, que se pre-registra aparte antes de lanzarla): fuentes de agua dulce que el modelo no tiene (lluvia, aguas residuales), inyección de los ríos en toda la columna,
o que las observaciones de 2002 (lluvias previas por frentes fríos, texto de JICA M4-44) no sean representativas. Un resultado que contradiga la hipótesis del artículo se informa tal cual.

## Registro
- 2026-11-18 — **Aclaraciones A1, escritas antes de ejecutar el script (no cambian umbrales ni lecturas).**
  1. *H1, raíces.* La regresión es cuadrática en ln qfac y puede tener dos raíces. Se toma la menor raíz con qfac ≥ 1 (más agua dulce que el caso central, la dirección que cierra el hueco). Si no hay ninguna, «no es cuestión de caudal». Se listan todas las raíces.
  2. *Miembros.* Todos los miembros con `resumen.json` y `nan = 0` (los mismos de `jica_sal_superficie_704.csv`); la regresión usa los que tienen S11 definido (≥ 3 mapas por fase). La versión «solo en equilibrio» (deriva ≤ 0,05 d/d) se informa como sensibilidad, sin cambiar la lectura.
  3. *S11 de un directorio de corrida* = mismo cálculo que `sal_704` (nodo principal; creciente Q > 0, bajamar Q ≤ 0 en el mapa de 16:00 UTC más cercano). El script comprueba que reproduce las filas del CSV de los 704.
  4. *Cierre* = (S11_control − S11_variante) / hueco; para H4 = −(cambio predicho) / hueco. En H3(ii) el hueco es el global (mediana de los 704 − 31,25), no uno por pareja.
  5. *Zonas.* «Centro de la Bahía» = zona 2 (cuenca). Valores de la tabla 4.11 (nov. 2001, superficie): se toman los de «High tide» y «Low tide» (no los de junio). `dulce_sup` es la media de los mapas de la ventana final de `posproceso.py` (VENTANA); S = 36 · (1 − dulce).
  6. *Verificado en el PDF antes de calcular:* tabla 4.12 (UNESCO vía JICA, M4-16), superficie: salinidad máxima 34,3 (dic.), mínima 27,4 (ene.), promedio anual 32,4; fondo 36,4 (abr.) / 34,4 (sep.) / 35,7. También figura allí la tabla 4.14 (UNESCO, «distribución vertical de la salinidad», 0–5 m: Atarés 12,9; Guasabacoa 13,3; Marimelena 3,3; Centro 4,9; Canal 3,8). La 4.14 se leyó antes de calcular, pero **no entra en ninguna lectura de este protocolo**; solo es contexto.
