# Experimentos de mecanismo (1 año, 2016, marea EOT20) — resultados

Corridas en Lemaitre4 del 24 al 26-oct-2026: 5 tramos de 73 días con hotstart. Las tres terminaron sin NaN.
Miembro central: carta 1887, α = 0,5, datum +0,25 m, Cd 0,0025.
Datos: `runs/mecanismo/m000{0,1,2}/resumen.{json,npz}` (no versionados).
Figuras: `docs/figuras/mecanismo.png` y `docs/figuras/s2_vs_dulce.png`.

## Edad media del agua (días, últimos 30 días, media de superficie y fondo)

| Zona | Solo marea | + viento | + ríos y densidad |
|---|---|---|---|
| Canal | 35 | 53 | 4,2 |
| Cuenca | 173 | 103 | 6,3 |
| Marimelena | 291 | 102 | 7,1 |
| Guasabacoa | 240 | 115 | 8,1 |
| Atarés | 251 | 118 | 9,6 |
| **Bahía** | **166** | **97** | **6,6** |
| Deriva al final (d/d) | +0,36 (no llega al equilibrio) | +0,09 (casi) | −0,03 (equilibrio desde el día ~30) |

Ríos: 2,14 m³/s en total (JICA 2004).

## Lectura

1. **La marea sola renueva muy mal.** Al año la edad media sigue creciendo (166 d). Encaja con el control analítico: la excursión mareal es 0,4 veces la longitud del canal.
2. **El viento acelera la renovación** (97 d al año, casi en equilibrio) y la iguala entre las ensenadas.
3. **La densidad cambia el resultado en un orden de magnitud: la edad pasa a ~7 días.** Los ríos (2,1 m³/s) generan una circulación gravitacional: agua dulce que sale por superficie y agua de mar que entra por el fondo. En el canal la edad en superficie es 6,5 d y en el fondo 1,9 d. El intercambio implícito es V/edad ≈ 50 m³/s, unas 25 veces el caudal de los ríos. El balance de Knudsen con la estratificación simulada lo hace coherente (~50–100 m³/s).
4. **Conclusión robusta (aparece en los tres experimentos):** el orden de las zonas canal < cuenca < Guasabacoa < Atarés.
   **Conclusión frágil:** la posición de Marimelena, que es la más vieja con solo marea y queda intermedia en los otros dos.
5. **Choque con JICA 2004**, que da "renovación del agua dulce ≈ 4 meses, poco intercambio". El modelo con densidad da ~1 semana. Que la densidad renueve tan rápido depende de cosas mal conocidas:
   - el caudal real (una sola campaña de JICA; también entran aguas residuales);
   - la mezcla vertical (turbulencia GLS, 16 niveles S);
   - la ausencia de evaporación y de flujo de calor (con T constante, la densidad depende solo de la salinidad).

   **Es el candidato más fuerte a conclusión frágil del artículo.**
6. **Caudal neto por la sección del canal:** no es fiable. Da −6 a +7 m³/s cuando debería ser ≈ −2,1. El error es de ~3–10 % del caudal bruto (~70 m³/s). No usarlo como cifra; el caudal bruto sí vale (69–70 m³/s en los tres).

## Comparación con Sentinel-2 (protocolo congelado + control registrado el 26-oct)

| Experimento | Campo | ρ (Spearman) | IC 95 % bloques | Criterio (IC > 0) | Control: p por desplazamientos | ρ nulo P95 |
|---|---|---|---|---|---|---|
| m0002 ríos (prueba principal) | agua dulce en superficie | **0,45** | 0,35–0,54 | se cumple | **0,16** | 0,61 |
| m0001 viento (secundaria) | edad en superficie | 0,48 | 0,39–0,57 | se cumple | 0,15 | 0,63 |
| m0000 solo marea | edad en superficie | 0,29 | 0,17–0,40 | se cumple | 0,28 | 0,61 |
| m0002 ríos | edad en superficie | 0,46 | 0,37–0,55 | se cumple | 0,15 | 0,60 |

Pixeles: 8908. Bloques: 145.

**Resultado, según la regla registrada:** el criterio principal se cumple, pero el control da p ≥ 0,05. El resultado se describe como **no distinguible del azar espacial**.

Ambos mapas aumentan desde la boca hacia las cabeceras de las ensenadas. Cualquier campo con ese gradiente correlaciona: desplazado al azar, el mapa S2 da ρ de hasta ~0,6. Con estos datos, Sentinel-2 no discrimina entre mecanismos ni valida el modelo más allá de ese gradiente.

Exploratorio, visto después: el satélite marca la cabecera de Atarés (brazo suroeste), donde el modelo no pone ningún río, y la cabecera de Guasabacoa, donde sí entra el Martín Pérez. Puede haber vertidos en Atarés que no están en OSM ni en JICA, o resuspensión en aguas someras.

## Consecuencias para el conjunto (decisiones pendientes)

- **Duración:** con ríos y densidad, la edad llega al equilibrio en ~30 días. 90 días por miembro bastan, con la métrica en los últimos 30 días y la deriva como control. Para miembros con caudal bajo, conviene confirmarlo.
- **Parámetros:** la incertidumbre dominante ya no es la batimetría ni el Cd, sino la circulación por densidad. Propuesta: añadir al Sobol el **factor de caudal de los ríos** (QFAC, p. ej. 0,25–2, log) y quizá un parámetro de **mezcla vertical**. Hoy los ríos van fijos en todos los miembros (decisión del 21-oct).
