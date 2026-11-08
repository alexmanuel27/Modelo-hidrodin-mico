# 6. Resultados (actualizado 7-nov-2026)

Tablas completas y fuentes en `../cifras.md`. Ordenado como las subsecciones de `main.tex`. Lo provisional del 17-oct (2 miembros con M2 de 0,15 m y sin ríos) queda **superado**; está en el historial de git.

## 6.1 Model behaviour

- Sustituir todo el bloque provisional. Qué se puede decir ya: con marea EOT20 la bahía sube y baja en bloque; todas las corridas (mecanismo y robustez) terminaron sin NaN; reiniciar por tramos no cambia las métricas (0,01 %).
- **No** dar el caudal por el canal como resultado ni como acuerdo con el prisma (avisos en `../cifras.md`).

## 6.2 Which parts of the bay do not flush — ⏳ conjunto

- Fig. 5: P(edad > 7/14/30 d) por zona y en mapa; mediana y P5–P95. Sale de `scripts/analisis_conjunto.py` cuando terminen los 704 (598 el 6-nov).
- Lo que ya apunta el miembro central con densidad: edad 4–10 d según la zona, mayor en Atarés.

## 6.3 Which unknown matters most — ⏳ conjunto

- Fig. 6: S1 y ST por zona, con IC. Expectativa (no resultado): el caudal de los ríos debería dominar, porque la densidad cambia la edad en un orden de magnitud.

## 6.4 Tide, wind or density — firme

- Edad de la bahía: **166 d solo marea** (sin equilibrio al año), **97 d con viento**, **6,6 d con ríos y densidad** (equilibrio desde ~día 30).
- La marea sola renueva muy mal: coincide con el control (excursión 0,41 del canal). El viento acelera y empareja las ensenadas.
- La densidad lo cambia todo con solo 2,14 m³ s⁻¹ de agua dulce: circulación gravitacional (canal: superficie 6,5 d, fondo 1,9 d); intercambio ≈ 50 m³ s⁻¹ ≈ 25 veces el caudal de los ríos.
- Orden canal < cuenca < Guasabacoa < Atarés en los tres experimentos; Marimelena cambia de puesto.
- Robustez (nueva, para esta subsección o para 7.1): 6,6–7,5 d con otro cierre turbulento, el doble de niveles o 10 veces más mezcla; 16,8 d con flujo de calor y borde a 28 °C (sospechoso, ⏳ repetición con SST real).
- Figura de trabajo: `../../figuras/mecanismo.png` y `../../figuras/robustez.png`.

## 6.5 Fate of the river water — sin hacer

- Fig. 8 sin decidir: partículas por desembocadura o un trazador por río. Decisión de Alex.

## 6.6 Comparison with Sentinel-2 — firme (resultado negativo)

- Protocolo congelado antes de mirar (21-oct) y control por desplazamientos registrado antes de calcularlo (26-oct).
- Agua dulce en superficie frente a persistencia de anomalías: ρ = 0,45 (IC 0,35–0,54), pero desplazando el mapa al azar se obtiene hasta ρ ≈ 0,6 (p = 0,16) → **no distinguible del azar espacial**. Las demás variantes, igual.
- Lectura: ambos mapas crecen de la boca a las cabeceras; Sentinel-2 no discrimina mecanismos ni valida el modelo más allá de ese gradiente.
- Exploratorio (visto después, decirlo así): el satélite marca la cabecera de Atarés, donde el modelo no tiene ningún río → posibles vertidos que no están en OSM ni en JICA, o resuspensión.
- Figura de trabajo: `../../figuras/s2_vs_dulce.png`.
