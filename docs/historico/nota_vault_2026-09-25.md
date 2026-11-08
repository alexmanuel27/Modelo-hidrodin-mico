# Copia del cuerpo de la nota del vault (a 2026-11-06)

> Copia íntegra de `Modelo hidrodinámico Bahía de La Habana.md` (vault Obsidian, IA compartida) tal como estaba el
> 2026-11-06, antes de condensarla. **El cuerpo es del 2026-09-25 y está desfasado**; lo vigente está en la nota del vault
> (Ficha, Registro, Decisiones, Restricciones) y en `docs/00_estado_y_plan.md`. Se conserva como histórico.

---

---
tags: [proyecto, codex, claude, antigravity, articulo]
actualizado: 2026-11-05
---

# Modelo hidrodinámico Bahía de La Habana

## Ficha (leer primero)

- **Qué es:** artículo para *Environmental Modelling & Software* sobre qué se puede saber de la renovación de la Bahía de La Habana sin datos propios: conjunto de simulaciones SCHISM 3D solo con datos públicos.
- **Estado (2026-11-03):** conjunto de 704 miembros × 120 d corriendo en Lemaitre4 (globalscratch) con 50 «trabajadores» que avanzan los miembros en tramos de 20 d (las cadenas de arrays se atascaban): 488 terminados (2026-11-05). Robustez: la renovación de ~1 semana aguanta otra turbulencia, 32 niveles y más mezcla (6,6–7,5 d), pero con flujo de calor sube a 16,8 d (posible artefacto del borde a 28 °C, POR CONFIRMAR). Mecanismo (2026-10-26): edad de la bahía 166 d solo marea, 97 d con viento, 6,6 d con ríos y densidad. Sentinel-2: ρ = 0,45, no distinguible del azar espacial. Protocolos de análisis congelados.
- **Siguiente acción:** esperar a m0005 (calor + SST OISST, lanzado el 2026-11-05) y al resto del conjunto; vigilar con `ssh lemaitre4 'bash -l bahia/diagnostico_conjunto.sh'` hasta 704.
- **Dónde mirar:** repo de trabajo, `docs/00_estado_y_plan.md`, `docs/resultados_mecanismo.md`, `docs/protocolo_*.md`.
- **Ojo:** lo de abajo es del 2026-09-25 y está desfasado, salvo **Decisiones**.

## Registro

- 2026-11-02 — Ficha añadida por Claude a partir de los commits del repo de trabajo; el cuerpo de la nota no se ha actualizado.
- 2026-11-02 (Claude, Cowork) — Decisión de Alex: la IA hace los commits del repo de trabajo y Alex el push (Decisiones y Restricciones).
- 2026-11-02 (Claude, Cowork) — Ficha, Siguiente acción y Decisiones actualizadas con el estado del conjunto y del mecanismo; detalle en el repo de trabajo (`docs/00_estado_y_plan.md`).
- 2026-11-02 (Claude, Cowork) — diagnóstico de tiempos del conjunto (`runs/diag/`, `cluster/diagnostico_tiempos.sh`); límite de 25 simultáneos por tramo y `--nodes=1` en `scripts/conjunto.py`.
- 2026-11-03 (Claude, Cowork) — conjunto relanzado con 50 trabajadores por carril (`runs/conjunto/trabajador.sh`, `lanzar_trabajadores.sh`); arrays atascados 8062929–34 cancelados; robustez sigue (4 miembros por el día 60–70).
- 2026-11-05 (Claude, Cowork) — con los trabajadores el conjunto pasó de 72 a 488 terminados en ~2 días; robustez completa (5/5).
- 2026-11-05 (Claude, Cowork) — robustez analizada: `docs/resultados_robustez.md`, `docs/figuras/robustez.png`; resúmenes del conjunto (488) copiados al Mac.
- 2026-11-05 (Claude, Cowork) — preparado el experimento de calor con SST OISST (`scripts/descargar_sst.sh`, `SST=oisst` en `caso_real.py`, robustez m0005).
- 2026-11-05 (Claude, Cowork) — SST OISST descargada (`datos/forzamiento/sst/`, 24,5–27,9 °C en ene–abr) y m0005 lanzado; entradas comprobadas.

Última actualización: 2026-09-25 (Claude y Codex, migración a memoria compartida verificada en ambos repositorios).

## Nombre y propósito

- Nombre del proyecto en Claude: `modelo-hidrodinamico` (descripción: «escribir articulo cientifico»).
- Propósito: escribir un artículo científico sobre un **conjunto (ensemble) de simulaciones hidrodinámicas 3D de la Bahía de La Habana** (Cuba): circulación, mapa de tiempo de residencia / edad del agua y destino de los vertidos con seguimiento de partículas, **sin datos de calibración propios**. La incertidumbre se cuantifica con cientos de miembros que perturban batimetría, fricción, viento, marea de contorno, caudales y flotabilidad.
- Título provisional: *Where do the discharges go? An ensemble hydrodynamic model of flushing and residence time in an uncalibrated tropical pocket bay (Havana Bay, Cuba)*.
- Autor: Alex Manuel Rivera (Université libre de Bruxelles). Coautores: No disponible (se busca colaborador).

## Rutas y repositorios

Hay **dos repositorios separados** (decisión del usuario):

| Repo | Ruta local | Remoto | Contenido |
|---|---|---|---|
| Artículo (este) | `/Users/alex/Nube /repos/publication plan/modelo-hidrodin-mico` | `https://github.com/Publication-Plan/modelo-hidrodin-mico.git` | solo el manuscrito LaTeX (`articulo/`) |
| Trabajo | `/Users/alex/Nube /repos/Modelo-hidrodin-mico` | `https://github.com/alexmanuel27/Modelo-hidrodin-mico.git` | scripts, datos, resultados, notas, cluster |

Estado de Git a 2026-09-25:
- Artículo: rama `main`; sin cambios versionados pendientes salvo `AGENTS.md` y `CLAUDE.md`, nuevos y sin commit (2026-09-25). Últimos commits `f3f161c` (README: la plantilla es elsarticle, no sn-jnl) y `cf86725` (borrador con elsarticle), ambos del 2026-09-16. Git informa `origin/main [gone]`: la referencia remota local no existe; no se comprobó si el repositorio remoto existe ni si hubo push.
- Trabajo: rama `main`, árbol limpio, commits `fbd5a08` (2026-09-17, «Update scripts/descargar_era5.py, scripts/instalar_entorno_mac.sh») y `2f7e6e4` (2026-09-16, commit inicial). También `origin/main [gone]`.

## Estado actual (2026-09-25)

- Manuscrito: esqueleto en `elsarticle` para *Environmental Modelling & Software* (EMS). Compila (4 páginas). Escritos: título, highlights, keywords, Introducción (un párrafo), Área de estudio, sección de control analítico (prisma de marea con Tabla 1 y Fig. 2). **Vacíos**: resumen, Métodos (solo comentarios con el plan), Resultados, Discusión, Conclusiones, *Software and data availability*, mapa Fig. 1.
- Bibliografía: 1 entrada (Ponce Portela y Córdova López 2016).
- Datos: **no hay batimetría** ni forzamiento descargado (`datos/batimetria/` y `datos/forzamiento/` vacíos salvo `.gitkeep`).
- Entorno de modelo: no hay registros en `cluster/` del repo de trabajo, así que no consta que `instalar_entorno_mac.sh` se haya ejecutado.
- Cluster CÉCI: acceso pendiente de aprobación del administrador (último dato: 16-sep).
- ERA5: cuenta lista y `~/.cdsapirc` guardado en el Mac (según notas del 16-sep). Descarga no hecha.
- FES2022: cuenta AVISO solicitada (16-sep); estado posterior No disponible.
- CUJAE (Ponce Portela / Córdova López): Alex les escribió para pedir batimetría/malla ADCIRC; respuesta No disponible.

## Funcionalidades terminadas

- Control analítico del prisma de marea (Monte Carlo, 200 000 muestras, entradas triangulares provisionales): `scripts/prisma_marea.py` → `resultados/prisma_marea.csv` y `.png` (repo de trabajo); figura copiada a `articulo/figuras/fig_prisma_marea.png`.
  - Resultados (central, p5–p95): volumen 47 hm³ (39–55); prisma 1,6 hm³ (1,2–2,3); renovación por ciclo 3,3 % (2,6–5,1); renovación ideal 16 d (10–20); con retorno + río 34 d (18–51); solo río ~270 d; Umax canal 4,5 cm/s (3,2–6,5); excursión mareal ~650 m (460–920) frente a canal de 1530 m → excursión < canal en el 100 % de las muestras → intercambio mareal ineficiente → justifica el 3D.
  - Entradas provisionales: área 5,2 km² (4,7–5,7), profundidad 9 m (7–11), rango mareal 0,30 m (0,20–0,50), canal 1530 m × 220–330 m × 12,8 m, β = 0,6 (0,3–0,85, supuesto), río 2 m³/s (0,5–5).
- Borrador LaTeX con plantilla oficial elsarticle (commit 04aee43 de STM-Document-Engineering/elsarticle), estilo autor-año `elsarticle-harv`.
- Scripts preparados (sin probar): `instalar_entorno_mac.sh` (miniforge + entorno conda `bahia` + compilar SCHISM con módulo AGE), `descargar_era5.py` (ERA5 horario 2016–2025, dominio 22,8–23,5 N / 82,8–81,9 W), `cluster/inventario.sh` (inventario de solo lectura del cluster).
- Borradores de gestión: `docs/carta_solicitud_batimetria.md`, texto de solicitud TPXO en `docs/paso2_forzamiento.md`.

## Decisiones importantes y motivos

- 2026-10 (Alex): **solo datos públicos replicables**, cada dato con URL y fecha de acceso; no se compra la carta BA 414; CUJAE, GEOCUBA y el mareógrafo solo como comparación opcional.
- 2026-10-16: conjunto Saltelli/Sobol (N = 64): carta 1879/1887, dragado, error de carta, datum, Cd, viento ×/giro, marea ×; 2026-10-26 se añade el caudal de los ríos (×0,25–2) → **704 miembros de 120 d** (con densidad la edad se estabiliza en ~30 d).
- 2026-10-21: marea **EOT20** (CC BY) en el conjunto; FES2022 solo para comparar (no redistribuible). Ríos de JICA 2004 (2,14 m³/s) con densidad en todos los miembros.
- 2026-10-21/27: protocolos congelados antes de ver resultados: comparación con Sentinel-2 (+ control por desplazamientos, 26/10) y métricas del conjunto (umbrales 7/14/30 d; robusta ≥ 90 % de miembros).
- 2026-10-29/11-01: cálculo en Lemaitre4 en tramos con hotstart, en globalscratch (cuota de /home llena); tramos de 20 d.
- Repo público + Zenodo al final: código MIT, datos CC BY 4.0.
- 2026-11-05: repetir el experimento de calor con SST diaria NOAA OISST (pública) en el borde y como T inicial — el borde a 28 °C fijo podía crear la fragilidad.
- 2026-11-03: trabajadores por carril (50 a la vez, sucesor con `afterany`) en lugar de cadenas de arrays con `aftercorr`, que se atascaban (`scripts/conjunto.py`).
- ~~2026-11-02: máximo 25 miembros a la vez por tramo y un nodo por miembro — el diagnóstico de tiempos muestra que el ritmo total satura hacia 60 simultáneos (`docs/00_estado_y_plan.md`).~~ Sustituida por los trabajadores (2026-11-03).
- 2026-11-02 (Alex): en el repo de trabajo, la IA hace los commits (autor Alex, con la línea Co-Authored-By) y **Alex hace el push**.

- **Sin trabajo de campo**: no se va a la bahía; sin sensor de presión, sin muestras ni fotos (decisión de Alex, 16-sep). Todo desde el portátil; cálculo en el cluster CÉCI.
- **Enfoque de conjunto** (cientos de miembros, muestreo Sobol/LHS): convierte la falta de datos de calibración en incertidumbre cuantificada y da índices de sensibilidad (segundo resultado publicable). La batimetría (CUJAE frente a carta BA 414) es una dimensión del conjunto.
- **Orden de trabajo**: batimetría → prisma (control analítico) → 2D base → 3D → partículas → conjunto. El 2D solo es control; no se sacan conclusiones de él.
- **Modelo: SCHISM** por defecto (semi-implícito sin límite CFL, ~~vertical LSC²~~ 16 niveles S (2026-10), módulo AGE y partículas incluidos, compilación limpia). Regla: TELEMAC si está instalado en el cluster o lo usa el colaborador; Delft3D-FM solo si aparece alguien que lo use. No compilar los tres.
- **Forzamiento**: ~~FES2022 (marea)~~ EOT20 (2026-10-21, licencia abierta) + ERA5 (atmósfera); TPXO solo si fallan las otras fuentes. Descargas estimadas o de CIMAB.
- **Validación solo con datos de terceros**: mareógrafo HABANA (PSMSL 2363, 2021–2024; hay que pedir la serie horaria al Servicio Mareográfico Nacional / GEOCUBA Estudios Marinos por carta institucional) + comparación cualitativa con persistencia de turbidez de Sentinel-2 (misma rejilla UTM 17N a 20 m).
- **Revista**: Environmental Modelling & Software (Elsevier); alternativa Estuarine, Coastal and Shelf Science (también se mencionó Ocean Engineering). Por eso la plantilla pasó de sn-jnl (Springer, del grupo) a `elsarticle` (16-sep).
- **Repos separados**: artículo y trabajo en repos distintos; el chat del Project de Claude es solo para el paper.
- **No hacer en este artículo**: oleaje (SWAN/WWM), biogeoquímica acoplada. ~~3D baroclínico antes de que el 2D reproduzca la marea~~ (hecho: 3D baroclínico por salinidad desde 2026-10-21).

## Estructura y archivos principales

Repo del artículo:
- `README.md` — descripción del repo.
- `articulo/main.tex` — manuscrito (132 líneas).
- `articulo/referencias.bib` — bibliografía.
- `articulo/figuras/fig_prisma_marea.png` — figura del prisma.
- `articulo/elsarticle.cls`, `elsarticle-harv.bst`, `LICENSE-elsarticle` — plantilla Elsevier.
- `articulo/main.pdf` — PDF compilado (versionado en Git).
- `AGENTS.md`, `CLAUDE.md` — instrucciones para agentes (apuntan a esta nota).

Repo de trabajo:
- `docs/00_estado_y_plan.md` — documento maestro: batimetría, prisma, cluster, elección de modelo, colaboración, diseño del conjunto, riesgos, gestiones.
- `docs/paso2_forzamiento.md` — cuentas ERA5 / FES2022 / TPXO.
- `docs/carta_solicitud_batimetria.md` — borrador de carta.
- `scripts/prisma_marea.py`, `scripts/instalar_entorno_mac.sh`, `scripts/descargar_era5.py`, `cluster/inventario.sh`.
- `resultados/prisma_marea.csv`, `resultados/prisma_marea.png`.
- `datos/batimetria/`, `datos/forzamiento/` (vacíos; datos pesados no se versionan).

## Tecnologías y dependencias

- LaTeX: `elsarticle` (preprint, 12pt, authoryear), paquetes amsmath, amssymb, graphicx, booktabs, lineno, hyperref; `latexmk` + pdflatex + BibTeX.
- Python 3 con numpy (prisma), matplotlib (figura), cdsapi (ERA5).
- Entorno conda `bahia` (previsto): python 3.11, compilers, mpich, netcdf-fortran, netcdf4, cmake, make, git, perl, numpy, scipy, matplotlib, pandas, xarray, pyproj, cdsapi.
- Modelo: SCHISM (se clona en `~/modelos/schism`) con módulo AGE.
- HPC: CÉCI (NIC5 y Lemaitre4: 2 días máx.; Hercules2: 15 días; Dragon2: 21 días), Slurm, job arrays, hotstart.

## Comandos

Artículo (repo del artículo):
```bash
cd "/Users/alex/Nube /repos/publication plan/modelo-hidrodin-mico/articulo"
latexmk -pdf main.tex        # compila; comprobado el 2026-09-25 en una copia: 4 páginas, sin errores
```
Trabajo (repo de trabajo):
```bash
cd "/Users/alex/Nube /repos/Modelo-hidrodin-mico"
python3 scripts/prisma_marea.py                 # recalcula el prisma → resultados/
bash scripts/instalar_entorno_mac.sh            # instala miniforge + entorno bahia + SCHISM (sin probar; logs en cluster/)
conda activate bahia && python scripts/descargar_era5.py   # necesita ~/.cdsapirc
bash cluster/inventario.sh > inventario_$(hostname -s).txt 2>&1   # en el nodo de login de CÉCI
```
Pruebas: no hay suite de pruebas. Comprobación mínima: que `main.tex` compile sin errores y que el prisma reproduzca la tabla.

## Problemas conocidos

- Entradas del prisma provisionales (fuentes secundarias) hasta tener batimetría y armónicos FES2022.
- Sin batimetría: bloquea todo el trabajo numérico.
- Scripts de entorno y ERA5 sin probar.
- `origin/main [gone]` en ambos repos (referencia remota ausente; no verificado).
- Compilación LaTeX: avisos de hyperref «Token not allowed in a PDF string» y destino duplicado `page.1` (no bloquean).
- `articulo/main.pdf` está versionado en Git (los demás productos de compilación se ignoran).
- La memoria y un documento antiguo del Project de Claude aún citan la plantilla sn-jnl y FES2014; lo vigente es elsarticle y FES2022.
- Las sesiones de Claude en Cowork no tenían red ni compiladores en el shell del Mac: instalaciones y push los ejecuta Alex.

## Trabajo pendiente (por prioridad)

1. Conseguir batimetría: respuesta de CUJAE (malla/batimetría ADCIRC); si no llega, comprar carta UKHO BA 414 (1:10 000, ed. 2021; Bookharbour 48,30 £, Weilbach 530 DKK, Maryland Nautical 54,95 $). Opcional: carta de solicitud al puerto/CIMAB.
2. Acceso a CÉCI y ejecutar `cluster/inventario.sh` en cada cluster que se use → cerrar la elección de modelo.
3. Ejecutar `instalar_entorno_mac.sh` y revisar logs; después `descargar_era5.py`.
4. FES2022 (cuenta AVISO) → armónicos en la bocana y frontera → actualizar el prisma y la Tabla 1/Fig. 2 del artículo.
5. Pedir la serie horaria del mareógrafo HABANA (carta institucional UH/ARES o vía CIMAB).
6. Lista de focos de vertido (nombre + coordenada), de la línea Sentinel-2 o de CIMAB.
7. Buscar colaborador: SLIM UCLouvain (Hanert, Deleersnijder; mejor encaje técnico), ESA-ULB (Gypens), BGEOSYS-ULB (Regnier; biogeoquímica).
8. Caso base 2D → 3D → partículas → conjunto Sobol en CÉCI.
9. Manuscrito: Fig. 1 (mapa con vertidos, ensenadas, canal y dominio), Métodos, ampliar Introducción y bibliografía, Resultados, Discusión, Conclusiones, *Software and data availability*, resumen al final.

## Restricciones y preferencias del usuario

- Escribe en español; el manuscrito está en inglés.
- Sin trabajo de campo, sin sensor, sin muestras ni fotos.
- Separar repos: el manuscrito solo en el repo del artículo; scripts, datos y resultados en el repo de trabajo. Las figuras/números nuevos se copian a `articulo/figuras`.
- TPXO solo si fallan las otras fuentes de marea.
- No pegar tokens ni contraseñas en el chat ni en Git (ERA5 `~/.cdsapirc`, credenciales AVISO).
- ~~No hacer commit ni push sin que el usuario lo pida.~~ (2026-11-02) Repo de trabajo: la IA hace los commits; el push lo hace Alex.
- No compilar varios modelos para compararlos; no oleaje; no biogeoquímica en este artículo.

## Última tarea y siguiente acción

- Última tarea: 2026-09-25, migración del contexto a esta nota y creación de `AGENTS.md` / `CLAUDE.md` en el repo del artículo. Antes: 2026-09-16, paso del borrador a elsarticle; 2026-09-17, ajuste de scripts en el repo de trabajo.
- Siguiente acción recomendada: que Alex ejecute `bash scripts/instalar_entorno_mac.sh` en el repo de trabajo y consulte el estado de CUJAE, CÉCI y AVISO. Mientras no haya datos, lo que se puede avanzar en el manuscrito es la Introducción, la bibliografía y los Métodos que no dependen de datos.

## Archivos, enlaces o fuentes a trasladar

- Documentos del Project de Claude (solo existen en claude.ai; su contenido está resumido aquí): `claude/estado_y_plan.md`, `claude/arranque_cowork_tecnico.md`.
- Repo de la línea Sentinel-2: `repos/publication plan/series-Sentinel-2` (el «protocolo congelado» de ventana, máscara de agua y línea de costa). Contenido: No disponible en esta revisión.
- Carta a la bahía (26-jun-2025): `doctorado/Grupo Estatal/carta a la bahia.docx`. Plan de viajes: `plan de viajes.xlsx` (ruta completa No disponible).
- Referencias externas: PSMSL estaciones 2363 (HABANA), 534 (HAVANA), 1162 (Siboney); CDS Copernicus; AVISO FES2022; TPXO10-atlas (Oregon State); ceci-hpc.be; github.com/schism-dev/schism.
- `~/.cdsapirc` en el Mac contiene un token: no copiar.
