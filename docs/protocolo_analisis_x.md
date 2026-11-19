# Cuatro análisis sin corridas nuevas (diagrama ΔS–ΔT, índice de bajo aporte, convergencia, mapa de S_T y perfil del canal): protocolo CONGELADO

> **Congelado el 19-nov-2026**, antes de calcular ningún resultado de estos análisis y antes de escribir sus scripts. Petición de Alex en el chat técnico.
> Solo datos ya existentes o públicos. Los umbrales de abajo no se cambian después de ver nada; cualquier aclaración va en el registro fechado del final.
> Los números que aparecen aquí (umbrales, semillas) vienen de la petición, de Sarrazin et al. (2016) o de protocolos ya congelados; ninguno sale de los datos.

## 0. Qué hay y qué falta (comprobado antes de fijar nada; no son resultados)
- `runs/robustez_largo/{m0000 sin calor, m0001 calor con borde a 28 °C, m0005 calor + OISST}` (365 d de 2016): solo tienen `resumen.npz/json` con la edad en 6 zonas cada 4 h (`serie_*`). **No se guardó T**
  (`iof_hydro(18)` solo con `TERMICO=1`) y **la S solo existe como campos completos**, que se conservan únicamente para los miembros 0, 1 y 2 de cada carpeta (aquí m0000 y m0001, en el cluster si no se han purgado; m0005 se borró). No hay medias mensuales de T ni de S.
- `canal_un` de `jica_estaciones.npz` es **NaN** en los miembros 0–2 del conjunto: no se guardó la velocidad 3D en esas corridas (la corrección `iof_hydro(26)` del 18-nov). El de `runs/salinidad` (velocidad 3D) llegará cuando acaben esas corridas.
- GEF/PNUD 1997: no he encontrado ninguna fuente **pública** con datos hidrográficos de la bahía (las páginas del proyecto CC Bays, RLA/93/G41, son resúmenes sin datos). Los ficheros locales de Alex (paper-to-read/Cimab) no están verificados como públicos. **No se usa GEF.**
- La petición anterior «tal como te pedí antes» sobre el mapa de S_T y el perfil del canal no está en este chat; la definición de §4 es mía y se corrige si Alex la quiere distinta.

## 1. Diagrama ΔS–ΔT (Largier 2023, fig. 5)
**Cantidades.** Por mes natural de 2016 (MES = 31,29,31,30,…), media de las medias diarias, **ponderada por volumen** (área del nodo × (h + η) × media de los 16 niveles σ, que tienen el mismo espesor relativo con σ puros):
S̄ y T̄ de la bahía (zona > 0) y de cada ensenada (canal, cuenca, Marimelena, Guasabacoa, Atarés). Borde: T_b = SST OISST diaria (m0005) o 28 °C (m0001) y S_b = 36; en m0000 (sin calor) T ≡ 28 por construcción (supuesto, no verificado con datos).
ΔS = S̄ − S_b, ΔT = T̄ − T_b, Δρ = ρ(T̄, S̄) − ρ(T_b, S_b) con la UNESCO 1980 de `termico.unesco`. Contornos de Δρ en el plano (ΔS, ΔT) con T_b y S_b de referencia = medias anuales del borde.
**Predicción fijada ahora.** Con Δρ mensual de la **bahía entera** y el crecimiento mensual de la edad G_m = (media de la edad de la bahía en los 5 últimos días del mes m − la del mes m−1) / días del mes, para febrero–diciembre (enero se descarta por el arranque desde edad 0, como en `mecanismo_calor.reglas`):
- «hipotérmico» = mes con Δρ > 0 (la bahía más densa que el borde).
- **CONFIRMA** si, en las dos corridas con calor (m0001, m0005), ρ_Spearman(Δρ_m, G_m) ≥ +0,59 (valor crítico de n = 11 a p = 0,05 a dos colas es 0,618; se usa 0,59 por la tabla de n = 12, **fijado así y no se cambia**) **y** la media de G_m en los meses hipotérmicos es mayor que en los demás (al menos 2 meses en cada clase).
- **CONTRADICE** si en alguna de las dos ρ ≤ −0,59 o si la media de G_m en los meses hipotérmicos es menor que en los demás con ρ < 0 en ambas. **INCONCLUSO** en el resto o si todos los meses tienen el mismo signo de Δρ.
- m0000 (sin calor) es el control: se informa, no entra en el veredicto. Las ensenadas se informan con las mismas reglas, sin veredicto.
**Si no hay T y S medias** (es el caso, §0): el script hace el cálculo en cuanto existan los datos y, mientras tanto, solo informa el crecimiento mensual de la edad y **qué hay que repetir**: m0001 (calor, borde 28 °C) con `TERMICO=1` 365 d (coste medido en `runs/robustez_largo/coste.txt`: 133 h-núcleo), más reducir los campos de m0000 y m0001 (si siguen en el cluster) y los de `runs/termico/m0000` (= m0005 repetido con salidas, X1, en cola) con `scripts/delta_st.py reduce`.

## 2. Índice de bajo aporte (exploratorio)
I = Q_r / (W · u_t³) por miembro. Q_r = 2,1409 · qfac m³/s (suma de `Q_RIOS` de `caso_real.py`). W = 33 · 10 m = 330 m (la sección del canal de `posproceso_malla.npz`; constante, no altera los rangos). **u_t**: `canal_un` no existe (§0); se usa el sustituto **u_t ≈ rms(Q − Q̄)/A**, con Q el caudal bruto por la sección del canal de `resumen.npz` en los últimos 30 d y A = 2751 m² (área de la sección con la profundidad de `hgrid.gr3`, igual para todos: no sigue a carta ni a datum). Es un sustituto, se dice así en el texto y se comprobará con `canal_un` de `runs/salinidad` cuando exista. I no es adimensional; solo se usa su orden.
**Relaciones** (Spearman, `conjunto_calor.spearman`): ρ(I, edad media de la bahía) con los 704 miembros válidos y, aparte, solo en equilibrio; ρ(I, desplazamiento por calor) con los 64 pares calor+OISST frente a sin calor (conjunto_calor frente a conjunto, miembros 0–63), en días (edad_calor − edad_sin) y en cociente. Cada ρ se compara con el de qfac con el mismo conjunto de datos.
**Lectura:** diferencia D = |ρ_I| − |ρ_qfac| con IC95 % por bootstrap emparejado (2000 remuestreos, semilla 20261119). **«I mejora a qfac»** si el IC está entero por encima de 0; **«no mejora»** si contiene 0; **«I es peor»** si está entero por debajo. Etiqueta: exploratorio.

## 3. Convergencia (Sarrazin, Pianosi y Wagener 2016)
Definiciones leídas en la copia de core.ac.uk (primeros ~40 000 caracteres literales; las ecuaciones 1–5 están en esa parte): bootstrap con reemplazo sobre las corridas existentes, IC95 %.
- **Índices:** Stat_ind = máx_i (S_sup,i − S_inf,i); converge si **< 0,05**.
- **Orden:** r_jk = Σ_i |R_j,i − R_k,i| · máx(S_j,i, S_k,i)² / Σ_i máx(S_j,i, S_k,i)², con R los rangos (1 = más influyente) de los remuestreos j y k; Stat_rank = cuantil 0,95 de r_jk sobre todos los pares; converge si **< 1**. (La petición decía «ponderado»; el artículo **no** usa puntuaciones Savage, solo las menciona como trabajo previo.)
- **Cribado:** X0 = factores con S media < T = **0,05**; Stat_scr = máx de la anchura del IC95 % en X0; converge si **< 0,05**; si X0 está vacío se informa «sin factores bajo T».
- **Remuestreos:** 1000 (el artículo dice 1000 en su tabla 1, no verificado en el texto literal; coincide con `analisis_conjunto.NBOOT`). Semilla 20261119.
**Qué se calcula.** S_T de Jansen (`analisis_conjunto.jansen`) para N = 16, 32, 48 y 64 con las filas j < N de cada bloque (A, B, AB1…AB9) de los 704, para la edad media de la bahía (resultado principal) y, aparte, las demás zonas. **«El orden de importancia converge con N\*»** = menor N tal que Stat_rank < 1 en N\* y en todos los N mayores; igual para las otras dos. Si no se cumple ni en N = 64, se dice «no converge con 64».

## 4. Mapa de S_T por nodo y perfil del canal frente a JICA
**Mapa.** S_T de Jansen (N = 64, los 704) para cada nodo de la malla (4832) de `edad_sup` y de `edad_fondo` (media de los últimos 30 d de cada miembro, en `resumen.npz`). Se dibujan: S_T de los **3 parámetros con mayor S_T de la edad media de la bahía a N = 64** (resultado de §3, regla fijada ahora), el parámetro dominante (argmax) por nodo, enmascarado donde el máximo S_T < 0,05 (el umbral de cribado), y la media ponderada por área de S_T por zona. Sin IC por nodo (el IC de la bahía está en §3).
**Perfil del canal.** Salinidad media del canal (nodos de zona 1) en los niveles superficie, medio y fondo de `jica_estaciones.npz` (`canal_S`, miembros 0–2 del conjunto, días 91–120, fases del ajuste armónico de la marea: creciente y bajamar) frente a la tabla 4.11 de JICA (Canal de Entrada: superficie, medio y fondo; junio y noviembre de 2001, pleamar y bajamar). Lectura: «dentro» si el modelo cae a ≤ 1 de la observación (mismo margen que la parte I de `protocolo_salinidad_superficie.md`); se informa la fracción de las 3 × 3 × 2 combinaciones dentro y la diferencia fondo − superficie frente a la observada. **La velocidad por nivel** (estación 1) **no se puede**: falta la velocidad 3D hasta que acaben las corridas de `runs/salinidad`. GEF: no se usa (§0).

## Registro
