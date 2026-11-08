> Copia de `claude/resumen_tecnico_2026-10-17.md` del Project de Claude, archivada en el repo el 8-nov-2026 antes de
> borrar el Project. Superado: lo vigente está en `docs/articulo/`.

# Actualización técnica para el chat del artículo (17-oct-2026)

Continúa `claude/resumen_tecnico_2026-10-13.md`. Repo `repos/Modelo-hidrodin-mico`, commits hasta 68b3f48; detalle en `docs/00_estado_y_plan.md` (secciones 21–22).

## Conjunto y posproceso

- **Diseño** (`scripts/conjunto.py`): Saltelli con Sobol aleatorizado, 8 parámetros — carta (1879/1887), estado de dragado α (0–1), realización del error de carta (σ 0,9 m, L 150 m), datum (0 a +0,5 m), Cd (0,001–0,005, log), viento ×0,8–1,2 y ±15°, amplitud de marea ×0,9–1,1 → **640 miembros** (N = 64). Ríos y densidad quedan fuera del Sobol y van a los experimentos de mecanismo.
- **Posproceso por miembro** (`scripts/posproceso.py`, dentro del array de Slurm): edad del agua (AGE_1 de SCHISM ya es la edad en días) por zona — canal, cuenca, Marimelena, Guasabacoa, Atarés (`docs/figuras/zonas.png`, límites revisados con Alex) —; fracción de volumen con edad > 30 d; mapas de superficie y fondo; caudal por el canal; edad en superficie a las 16:00 UTC en la rejilla Sentinel-2.
- **Coste en Lemaitre4:** 2,7–3,9 h por miembro de 90 d con 4 + 2 núcleos.

## Primeros resultados (2 miembros de 90 d, marea M2 provisional + ERA5, sin ríos)

- **Caudal bruto por el canal 64–74 m³/s**; el prisma de marea da 66 m³/s, coinciden. Caudal neto ≈ 0 (error de la sección ~3 %).
- **Edad media en los días 60–90:** bahía 28–31 d; canal 15 d; cuenca 30–32; Marimelena 30–33; Guasabacoa 33–37; **Atarés 36–41 d**. Entre el 55 % y el 76 % del volumen tiene agua de más de 30 d (las ensenadas, ~100 %).
- **⚠ La edad no llega al equilibrio en 90 d:** crece ~0,4 d por día, con pausas de 10–15 d (probablemente frentes fríos). La extrapolación con una sola escala de tiempo no es fiable. Hay una corrida de 1 año del miembro 0 en marcha para fijar la duración del conjunto.
- Hay velocidades espurias en el borde abierto (hasta 4,45 m/s, a ~5 km de la boca). La esponja de fricción se extendió a todo el borde. Ya estaba comprobado que el tratamiento del borde no cambia las cifras de la bahía.

## Fuente pública nueva: JICA 2004

Nihon Suido Consultants para JICA (2004), *Estudio del Desarrollo del Alcantarillado y el Drenaje Pluvial en la Cuenca Tributaria de la Bahía de La Habana*, informe final vol. IV — https://openjicareport.jica.go.jp/pdf/11767225.pdf

- **Caudales** (tabla 1.1, datos CIMAB de ago-2002; no hay aforos permanentes): Luyanó 1,33, Martín Pérez 0,72, Tadeo 0,09 m³/s, **2,14 m³/s en total**.
- **"Renovación del agua dulce ≈ 4 meses", con "relativamente poco intercambio con el mar abierto"**. Posibles corrientes de densidad en Atarés y Guasabacoa.
- Es también el origen de los 47 hm³ y 9 m de profundidad media que las cartas no sostienen.
- **Punto de discusión para el artículo:** su ~4 meses encaja con lo que da el modelo y no con los 23 d del control analítico (prisma con factor de retorno).

## Ríos y densidad

Ya programados en `caso_real.py` (`RIOS=1`, caudal × QFAC):

- desembocaduras tomadas de OpenStreetMap;
- agua de río con S = 0, tratada como "agua nueva" para la edad;
- modelo baroclínico por salinidad, con T y S constantes en el borde (28 °C, 36) y sin flujo de calor.

Experimentos de mecanismo previstos (un miembro base, 1 año): (1) solo marea, (2) marea + viento, (3) marea + viento + ríos y densidad.

## Pendiente

1. Duración del conjunto (sale de la corrida de 1 año en marcha).
2. Marea FES2022 (cuenta AVISO creada, esperando credenciales) y TPXO.
3. Experimentos de mecanismo.
4. Regenerar y lanzar los 640 miembros; Sobol; conclusiones robustas y frágiles.
5. Partículas por foco, comparación con Sentinel-2 y figuras en inglés.
