# Para el chat del artículo — respuesta del chat técnico a la V3 (17-nov-2026)

Todo con la lectura fijada y commiteada antes de lanzar o ver resultados; ningún umbral cambia a posteriori; solo datos públicos (ERA5, OISST, EOT20, Landsat).

## Hecho (con commit)

- **X8, `cifras.md` (73458bb):** añadidas las cifras de la V3. **Dos avisos:** (1) **5,252 d es el ancho P5–P95 de los 64 miembros del bloque A sin calor, no el del conjunto principal**; el del conjunto principal (128 miembros) es 4,837 d. En el texto, «5,4 d frente a 5,3 d» (R = 5,40/5,252 = 1,03) compara los mismos 64; si aparece «4,8 d» es el de 128; no mezclarlos. (2) **X5 (ρ = −0,53, 6,5 d frente a 4,3 d, factor 1,67…) no tiene script ni dato en este repo**: se anotó tal cual lo dio el chat del artículo, marcado «no verificado aquí»; el cálculo tiene que constar en el repo donde se hizo. Q2 sí se comprobó: OISST jul–sep de 2016 = 28,346–30,458 °C. Los costes también: 3.106 h-núcleo (64 miembros, ≈ 49 c/u) y 120 + 133 + 126 ≈ 380 (tres años).
- **X6, resumen gráfico (f1e2f3a):** `docs/figuras/articulo/graphical_abstract.{png,pdf}` con el titular «One structural choice weighs as much as nine uncertain inputs»; panel central = medianas y P5–P95 por zona **de los mismos 64 miembros** sin calor (azul) y con calor (naranja); panel derecho = S_T y, aparte y en otro color, la barra en días: desplazamiento pareado 5,4 d frente a rango P5–P95 de 5,3 d (5,252). El titular lo sostiene R = 1,03: «pesa tanto como», no «más que»; la barra 5,4 frente a 5,3 no autoriza más.

## Preparado, sin lanzar (commit 9f09617; lecturas en `docs/protocolo_metricas_conjunto.md`, 17-nov V3-1 a V3-5)

- **X1, freno térmico:** repetir la corrida central calor + OISST de 365 d guardando T, S, flujos y esfuerzo del viento (T, S y flujos no se habían guardado nunca). Lectura fijada: con anomalía de edad = (calor − sin calor) por mes (feb–dic, n = 11), el freno térmico queda **apoyado solo si** ρ(Δρ canal, anomalía) ≤ −0,60, ρ(T_bahía − T_borde, anomalía) ≤ −0,60 y el Δρ mediano de los 3 meses de mayor anomalía < 0,5 × el de los 3 de menor; **contradicho** si la primera o la tercera dan ≥ −0,30 o ≥ 1,0. Además T1–T3 con el flujo del modelo, no el proxy. Coste ≈ 130 h-núcleo.
- **X2, factorial 2×2 de un año:** calor sí/no × viento real/climatológico; A y B ya existen (`robustez_largo`), faltan C y D (≈ 260 h-núcleo). Lectura: el efecto térmico «se mantiene sin frentes fríos» si HC ≥ 0,5 × HR; «depende de los frentes» si HC < 0,25 × HR; en medio, parcial. **Limitaciones que el texto debe heredar:** el viento climatológico (media 2016–2025 por mes y hora) baja la rapidez media y el viento entra también en los flujos turbulentos de calor, así que el factor separa «variabilidad sinóptica del viento» y no solo cantidad de movimiento.
- **X3, Landsat 8/9 C2 L2:** `scripts/landsat_termico.py`, **sin probar contra el servicio real**; regiones, mínimos, estaciones (nov–mar / jun–sep) y regla (IC95 bootstrap frente al ruido del par de control mar–mar) fijados. Limitaciones heredadas: temperatura de piel a ~10:30 h local frente a temperatura a 1 m del modelo; solo cielo despejado; resolución térmica de 100 m; varios años de escenas frente a un modelo de 2016.
- **X4, años 2017–2025:** miembro central, 120 d, con y sin calor + OISST del año (el desplazamiento hace falta pareado). Regla fijada con 5,40 d: «estable» si los diez años (con 2016) son > 0 y su rango ≤ 2,70 d; «no estable» si alguno ≤ 0 o el rango > 5,40 d. **Coste real ≈ 900–1.350 h-núcleo (18 corridas), no 700: 700 son solo las 9 con calor y con ellas no se puede calcular el desplazamiento.**
- **Opcional (E − P):** sin hacer; requiere recompilar SCHISM con `PREC_EVAP` (+ ~130 h-núcleo).

## Qué decir y qué no decir hasta tener los resultados

- «Freno térmico»: hoy es **hipótesis** compatible con el proxy (T1 +0,32, T2 +0,75, T3 +0,14; el viento no se separaba), no resultado; el Δρ del canal no se guardó. No escribirlo como mecanismo demostrado.
- No hay resultados de X1–X4 todavía. Cuando lleguen, se leen con las reglas de arriba y se reportan tal cual, también si contradicen la hipótesis.

## Qué cambia en el texto (antes → después)

| Antes | Después |
|---|---|
| «6,4 d frente a 4,8 d» / «5,4 d frente a 5,3 d» sin aclarar | 5,40 d frente a 5,252 d de los **mismos 64**; 4,837 d es el del conjunto de 128 |
| Titular «about one week without… two weeks with… never months» | «One structural choice weighs as much as nine uncertain inputs» (resumen gráfico; R = 1,03) |
| X5 en texto como cifra propia | marcar su origen; no verificable en este repo |
| «el calor frena la circulación estuarina» | «consistent with» hasta X1 |

## Para Alex

Comandos de lanzamiento (X1+X2 y X4), `git push` (≥ 26 commits), horas-núcleo totales, Zenodo/DOI, B5/B8/B9, CRediT/afiliaciones/financiación.
