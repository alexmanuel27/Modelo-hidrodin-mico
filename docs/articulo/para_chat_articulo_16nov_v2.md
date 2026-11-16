# Respuesta del chat técnico a PENDIENTES_V2 (16-nov-2026)

Todo con la lectura fijada y commiteada antes de ver el resultado; ningún umbral cambió.

## Hecho (con commit)

- **B6, resumen gráfico** (3060347): `docs/figuras/articulo/graphical_abstract.{png,pdf}`, 1771 × 732 px (15 × 6,2 cm). Titular «About one week without the heat flux, about two weeks with it, never months». Panel central: mediana y P5–P95 por zona del conjunto (128, azul) y de los 16 con calor (naranja; bahía 13,8 d, 9,2–17,7). Panel derecho: S_T arriba y, aparte y en días, el flujo de calor («Heat flux (structural): shift of median» 6,4 frente a «Parameters: P5–P95 range» 4,8). Regenerable con `python scripts/figuras_resultados.py resumen`. Sigue siendo un 16 frente a un 128 (ver B4: con 64 miembros la comparación pasa a ser homogénea).
- **B3 en `cifras.md`** (96adee1 y la corrección de 6,41 → 6,40): añadidos 365 d con calor + OISST (media 11,4 d; base 6,5; calor 28 °C 10,5), 88/365 días > 14 d (base 0), media de 30 d 5,1–21,1 d, medias mensuales (5,2 ene … 21,0 nov; ago 6,1; base 6,3), C1 y C4 con calor 0,94 (15/16), marea «como mucho 0,4 cm» (máx. 0,37, O1). `scripts/fig_heatflux.py` está en `scripts/` con su salida `resultados/heatflux_cifras.txt` y `docs/figuras/articulo/fig_heatflux.{png,pdf}` (PNG idéntico al del chat del artículo).
- **Una corrección de cifra:** el desplazamiento es **6,40 d** con los decimales sin redondear (13,77 − 7,36), no 6,41; en el texto sigue siendo «6,4 d». Y la comparación «6,4 d frente a 4,8 d» mezcla una mediana de 16 miembros con calor y el ancho P5–P95 de otro conjunto de 128 (con los mismos 16 sin calor el ancho es 4,5 d). Vale como orden de magnitud; la versión homogénea es B4.
- **B2 y B4, lecturas fijadas** (a553d4d, `docs/protocolo_metricas_conjunto.md` 16-nov (3) y (4)), `scripts/mecanismo_calor.py`, acción `calor64` y `CALOR_N` en `conjunto_calor.py`. **Aún sin resultados**: faltan cosas que corre Alex en el clúster.

## B2, mecanismo (qué se puede decir ya)

Ningún run guardó temperatura, flujos ni esfuerzo del viento: el Δρ superficie–fondo del canal **no existe** y no se puede inventar. Se contrasta lo que sí hay: serie diaria de edad de `robustez_largo` frente a un **proxy** bulk de flujo neto (SST OISST, coeficientes constantes; no es el flujo de SCHISM) y al esfuerzo del viento. Reglas: T1 ρ(enfriamiento, crecimiento de la edad) ≥ +0,30 en bloques de 5 d con el control sin calor < 0,5 × T1; T2 ρ mensual ≥ +0,60 (feb–dic); T3 ρ parcial dado el viento ≥ +0,25. Aunque todo confirme, el texto debe decir «compatible con», no «demuestra». Para la cadena completa hace falta repetir m0005 365 d con T, S, flujos, esfuerzo y estaciones del canal: **≈ 220–330 core-h**, 1,5–2 días de cómputo + un día de código (decisión de Alex).
Hasta entonces, en el texto: la variabilidad con calor es un resultado del modelo; la explicación por enfriamiento invernal es una hipótesis (anula el contraste de densidad del río y frena la circulación estuarina), no un resultado.

## B4, conjunto con calor (recomendación)

**(a) 64 miembros del bloque A con calor + OISST**: 48 nuevos, ≈ 3.600–3.700 core-h (72–76 por miembro; con calor puede ser algo más). Da la Tabla 4 con fracciones exactas n/64, **separa caudal de marea** (correlación de diseño qfac–mfac 0,00 en los 64; +0,93 en los 16) y hace homogénea la comparación calor frente a rango paramétrico (R = diferencia pareada / ancho P5–P95 sin calor, regla R > 1 y ≥ 90 % de miembros). **(b) Saltelli N = 16**: 176 miembros, ≈ 13.200 core-h; da S_T con calor, pero nuestra convergencia da ±0,5 con N = 16: caro y ruidoso. Se recomienda (a); (b) solo si (a) muestra que el calor cambia el orden de los parámetros. C8 (Sobol) no se evalúa con (a). Alcance: enero–abril de 2016, 120 d, últimos 30 d.

## Qué cambia en el texto (antes → después)

- Resumen gráfico: «About one week within the ensemble / River flow controls it» → titular de dos niveles + panel de calor en días aparte de S_T.
- «6,4 d frente a 4,8 d»: añadir que son 16 miembros con calor frente al conjunto de 128 (o esperar a (a) y dar el cociente homogéneo).
- Mecanismo del calor: de «el flujo de calor invierte el contraste de densidad» a hipótesis hasta tener el Δρ.
- Marea: «< 0,4 cm» → «como mucho 0,4 cm» (0,37).

## Lo que necesito de Alex

1. `git push` (22 commits sin subir, según `git rev-list origin/HEAD..HEAD`).
2. Decidir B4 (a), (b) o ninguno; y si se repite m0005 365 d con salidas (B2).
3. En el clúster, para B2 (barato, solo lectura): `cd bahia && python3 scripts/mecanismo_calor.py extrae` (módulo `netcdf4-python`), traer `resultados/forzamiento_2016_horario.csv` y avisarme; y traer los `coste.txt` de `runs/robustez_largo` y `runs/conjunto_calor` para medir los core-h reales.
4. Si se elige (a): `CONJ_DIR=runs/conjunto_calor CONJ_DIAS=120 CONJ_SEG=20 python scripts/conjunto.py calor64`, rsync como en calor16, y `bash lanzar.sh 16-63` (+ `lanzar_trabajadores.sh N`).
5. Lo suyo, no mío: B8 (referencia Ponce Portela), B9 (enlaces), B5, CRediT/afiliaciones/financiación.

## Actualización de la noche del 16-nov: resultado de B2 (proxy) y costes medidos

`calor64` está lanzado (24 carriles, 48 miembros nuevos). El proxy se ha leído con la regla fijada (protocolo 16-nov (5), `resultados/mecanismo_calor.txt`, commit en el log):

- m0005 (calor + OISST): T1 (enfriamiento frente a crecimiento de la edad en bloques de 5 d) +0,32 → confirmada por un margen de 0,02 (con lag 1 sería +0,28); control sin calor −0,01, pasa; T2 mensual (feb–dic) +0,75 → confirmada; **T3 (separar del viento) +0,14 < 0,25 → no se cumple**. **Veredicto por la regla: no concluyente / parcial.** Réplica con m0001: T1 +0,51, T2 +0,66, parcial +0,33.
- **Frase que sostiene el resultado (inglés):** «The age with heat flux is highest in the months with negative net surface heat flux and stronger winds (November–March and October–December), but in this single year-long series cooling and wind stress cannot be separated; the pattern is consistent with, but does not demonstrate, a weakening of the estuarine circulation by winter cooling.»
- **Cautela que el artículo no debe esconder:** el proxy da un balance anual de −18,5 W/m² (calor latente 148 W/m², probablemente sobreestimado por usar coeficientes constantes). Se usa solo por rangos; no es el flujo de SCHISM.
- No hay Δρ del canal. Repetir m0005 con salidas queda en reserva: cuesta ≈ 130–180 core-h (medido: los 365 d de `robustez_largo` salieron a 120–133 core-h).
- **Costes medidos:** `conjunto_calor` a 120 d ≈ 49 core-h por miembro (no 72–76); los 48 nuevos ≈ 2.400 core-h.
- Qué cambia en el texto: «hipótesis del enfriamiento» pasa de «propuesta» a «compatible con el proxy, no separable del viento, Δρ sin medir».
