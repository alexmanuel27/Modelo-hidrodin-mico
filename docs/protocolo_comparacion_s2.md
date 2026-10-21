# Comparación modelo ↔ Sentinel-2: protocolo CONGELADO

> **Congelado el 21-oct-2026, aprobado por Alex**, antes de lanzar el conjunto. El texto es el del commit 773b9fb;
> solo cambia esta cabecera. Cambios posteriores, únicamente en el registro fechado del final.
> Decisión asociada (21-oct): todos los miembros del conjunto llevan ríos (caudales JICA 2004) y densidad, así que la
> prueba principal se aplica a todo el conjunto.

## Qué se ha visto ya (para que conste)

El 21-oct, al revisar la entrega (`datos/sentinel2/`, commit dad5893), Claude calculó la frecuencia media de detección
por zona: canal 0,6 %, cuenca 0,7 %, Marimelena 0,8 %, Atarés 1,9 %, Guasabacoa 2,3 %. También calculó los píxeles con
exceso binomial respecto a la tasa global (1,3 %): 374 con p < 0,01 (se esperan ~104 por azar), sobre todo en la
cabecera del brazo sur (Guasabacoa, junto a la desembocadura del Martín Pérez), y a hasta ~300 m de la orilla.
Ya se conocían las edades por zona de la corrida de 1 año sin ríos (canal < cuenca ≈ Marimelena < Guasabacoa < Atarés).
**Por eso el orden entre zonas no es una prueba ciega**: queda como resultado exploratorio.
Tampoco se usan para confirmar los 3 focos "exploratorios" de `focos.csv`, que se definieron después de ver los datos.

## Prueba principal (confirmatoria)

- **Satélite:** `persistencia` de `rejilla.npz` (frecuencia de detección por píxel). Filas 0–251; la fila 252 sobra.
  El desfase de rejilla (+1 m E, −2 m N) se ignora.
- **Píxeles:** agua en las dos máscaras (S2 y malla); a ≥ 40 m (2 píxeles) de la costa S2, el mismo margen que el
  criterio 12.2 del proyecto S2; `n_validas` ≥ 50.
- **Modelo:** media de las instantáneas de las 16 UTC de los últimos 30 días de la **fracción de agua dulce en superficie**
  (`s2_dulce`, 1 − S/36) en corridas con ríos.
- **Estadístico:** correlación de Spearman ρ por píxel.
- **Incertidumbre:** bootstrap por bloques de 200 × 200 m (10 × 10 píxeles), 1000 remuestreos, IC 95 %.
- **Predicción:** ρ > 0.
- **Criterio:** se cumple en el experimento de mecanismo con ríos (m0002) si el límite inferior del IC 95 % es > 0. Es
  **robusta** si además ρ > 0 en ≥ 90 % de los miembros del conjunto que lleven ríos (bloques A y B). Si no se cumple,
  se publica igual.

## Secundaria

La misma prueba con la **edad del agua en superficie** (`s2_edad`) de los miembros sin ríos. Predicción: ρ > 0
(el agua más vieja, más estancada, retiene más turbidez).

## Límites que se declaran

- Las escenas son de 2017–2025 y el modelo simula 2016. La comparación es de patrones climatológicos, no de escenas.
- El método de detección S2 no superó su criterio de falsación 12.2 (ningún sitio sobrevive al margen de 40 m). Por eso
  se usa la frecuencia por píxel y no los sitios, y se excluye la franja de 40 m.
- La turbidez no es un trazador conservativo (resuspensión, fitoplancton, buques); la fracción dulce sí lo es.

## Registro de cambios

*(vacío)*
