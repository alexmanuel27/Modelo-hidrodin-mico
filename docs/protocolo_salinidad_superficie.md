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
- 2026-11-18 — **RESULTADO de la parte I** (`scripts/salinidad_superficie.py`, commit b98a20f; salida completa en `resultados/salinidad_superficie_parteI.txt`). Lecturas del §1–§2 aplicadas sin cambios:
  - Hueco: S11 mediana de los 704 = 35,37 (P5–P95 34,94–35,68) frente a 31,25 observado → **+4,12**.
  - **H1, caudal: «no es cuestión de caudal».** La regresión (R² 0,92) da coef. de ln qfac −0,389 y de (ln qfac)² −0,064; las raíces para S11 = 31,25 son qfac ≈ 1e-5 (sin sentido) y 227,6 (la menor con qfac ≥ 1; muy por encima del límite 4). Con solo equilibrio: 227,5.
  - **H4, tres drenajes (F = 1,70): «no explica»**: cambio mediano de S11 −0,18; cierre +0,044.
  - **H2, mezcla vertical: «no explica»** las tres: k-ε −0,020; 32 niveles −0,041; difusividad mínima ×10 −0,000.
  - **H3, calor: «no explica»**: borde 28 °C +0,12; calor + OISST +0,035; 64 pares: cierre mediano +0,041 (P5–P95 +0,022 a +0,062; máximo +0,356, un miembro «parcial»).
  - Control de muestreo: mapas de 16:00 UTC frente a las 175 muestras, diferencia ≤ 0,03 en los tres miembros → representativo.
  - Zonas frente a la tabla 4.11 de nov. 2001 (±1): Canal 100 %, Centro 100 %, Marimelena 100 %, Guasabacoa 55 % (el modelo es **más dulce** que lo observado: mediana 34,63 frente a 35,6–36,0), **Atarés 0 %** (modelo 35,29 frente a 21,4–27,1). Bahía: 0,3 % de los miembros con S < 34,3 (tabla 4.12).
  - Lectura del §3: ninguna de H1–H4 «explica» y la suma de cierres positivos de H4 + H2 es 0,04 < 0,5. **La diferencia no se debe a ningún parámetro ni proceso probado con lo existente.** Matiz que no estaba en las lecturas pero sale de los números: frente a la campaña de nov. 2001 el modelo es compatible en 3 de 5 zonas y solo falla de forma clara en Atarés; frente a dic. 2002 (media de 11 estaciones) y a la climatología UNESCO 1985 (superficie: promedio anual 32,4, máximo mensual 34,3) es demasiado salado. Las campañas públicas no coinciden entre sí.
- 2026-11-18 — **HALLAZGO en el código de SCHISM, leído después de la parte I y antes de cualquier corrida nueva (H6).** `lev_tr_source` vale −9 por defecto («bottom», `schism_init.F90:507`) y en `schism_step.F90:7963-7974` el nivel de inyección es `kin = max(kbe+1, min(nvrt, lev_tr_source))`: **la T y la S de los ríos (S = 0) se inyectan en la capa de fondo del elemento fuente**; 0 = toda la columna; un valor ≥ 1 = ese nivel (nvrt = superficie). Nuestros `param.nml` tienen −9 para T y S (líneas 279–280 de `runs/robustez/m0000/param.nml`); la edad usa `level_age = -999` (todas las capas). El agua dulce entra, pues, por el fondo y debe subir por inestabilidad convectiva, lo que debilita la capa dulce superficial y la estratificación. Es una hipótesis estructural que la parte I no podía ver (no hay variante con otro nivel de inyección).
- 2026-11-18 — **FASE II PRE-REGISTRADA (antes de modificar `caso_real.py`/`conjunto.py` y de lanzar nada).** Miembro central (BASE), 120 d, EOT20, ríos, sin calor, `runs/salinidad`, todas con velocidad 3D y cotas guardadas (`iof_hydro(25) = iof_hydro(26) = 1`, 6 scribes):
  - m0000 control (`lev_tr_source` = −9, fondo); m0001 ríos en la capa superior (`lev_tr_source(1) = (2) = nvrt = 16`); m0002 ríos en toda la columna (`= 0`); m0003 = m0001 con caudal total ×1,7005 (los tres drenajes sumados, puestos en las desembocaduras existentes; la ubicación real de los drenajes no está fijada en el repositorio, así que es una aproximación del volumen y no del lugar).
  - **F1 (reproducibilidad):** m0000 debe repetir `runs/robustez/m0000`: |ΔS11| ≤ 0,05 y |Δedad media de la bahía| ≤ 0,05 d. Si no, las salidas nuevas cambian la dinámica o la corrida no es reproducible, y se informa antes de seguir.
  - **F2 (cotas):** `zCoordinates` guardada frente a la `zcor` reconstruida por el extractor: diferencia máxima ≤ 0,01 m. Si no, (b) se rehace con las cotas reales.
  - **F3 (salinidad superficial):** cierre de S11 (lectura común del §1) de m0001, m0002 y m0003 frente al control.
  - **F4 ((b), fase A):** veredicto de las reglas congeladas A1 sobre la media de las dos fases, extractor con los días 91–120 de cada miembro.
  - **F5 (efecto en el resultado central):** R = (edad media de la bahía de la variante − del control) / (P5–P95 de la edad media de la bahía de los 704); CAMBIA ≥ 0,25, NO CAMBIA < 0,10, PARCIAL entre medias (umbrales de `jica_caudales_extra.py`).
  - **F6 ((a) y (c)):** con la velocidad 3D se aplican las lecturas ya congeladas en `docs/protocolo_jica_observaciones.md`, sin cambios.
  - **Conclusión sobre H6:** «explica» si m0001 o m0002 tienen cierre de S11 ≥ 0,5 y su veredicto de (b) no es CONTRADICE; «parcial» si el cierre está en [0,25; 0,5); «no explica» en el resto. Si H6 explica, el conjunto de 704 y los 64 con calor comparten el sesgo (todos con inyección en el fondo); la F5 dice si cambia el resultado central, pero **rehacer el conjunto (≈ 704 × 48 core-h ≈ 34 000 core-h) es decisión de Alex**, no se lanza sin ella.
  - Si H6 tampoco explica: quedan sin probar las causas no estructurales (lluvia y aguas residuales que el modelo no tiene; las campañas de 2002 no representativas de 2016); no se prueban con corridas de este tipo y se informan como límite.
