# Modelo hidrodinámico de la Bahía de La Habana — estado y plan

*16 de septiembre de 2026. Primera entrega: batimetría, prisma de marea, cluster, elección
de modelo, colaboración y riesgos.*

---

## 1. Batimetría — estado: NO la tenemos

En tus carpetas no hay ninguna batimetría, carta ni sondas de la bahía (busqué en
`doctorado/` y en `publication plan/`). La carta que se envió en junio de 2025 al Grupo de
Trabajo Estatal de la Bahía (`doctorado/Grupo Estatal/carta a la bahia.docx`) pedía datos
de calidad de agua y "mapas o estudios sobre la dinámica de las corrientes", pero **no
pedía batimetría**. Hay que volver a pedirla, esta vez de forma explícita
(borrador en `docs/carta_solicitud_batimetria.md`).

Fuentes, en orden de preferencia:

| Fuente | Qué es | Estado / comentario |
|---|---|---|
| Autoridad portuaria / GEOCUBA / CIMAB | levantamiento hidrográfico del puerto (sondas XYZ) | la mejor opción. Pedir el **datum vertical, la fecha del levantamiento y la zona de dragado** |
| Autores de ADCIRC 2016 (CUJAE) | Ponce Portela y Córdova López modelaron la bahía y el malecón con ADCIRC (*Ing. Hidráulica y Ambiental* 37(3):59-73) | **ya tuvieron una batimetría digital.** Pedirla es probablemente la vía más rápida |
| Carta UKHO BA 414 "Puerto de la Habana" | 1:10 000, edición 2 (abril 2021), impresión bajo demanda (~60-70 €) | la vía de respaldo que planteaste. Escala muy buena para una bahía de 5 km² |
| Cartas antiguas de dominio público | útiles para comprobar, no como fuente principal | el dragado del canal y de los muelles cambia las profundidades |
| GEBCO | celdas de ~450 m | **no sirve** dentro de la bahía; solo para el dominio exterior |
| Batimetría derivada de satélite (S2) | enlazaría con tu otra línea | el agua turbia de la bahía la hace poco fiable. Solo para comprobar |

**Cómo entra en el conjunto.** Sondas digitalizadas + isóbatas + línea de costa de la
máscara de agua de Sentinel-2 (la que fija el protocolo congelado, sección 5), así la costa
del modelo y la del satélite son la misma. La incertidumbre se genera como
**campo aleatorio espacialmente correlacionado** sumado a la superficie interpolada:
σ según la precisión declarada de la carta (y mayor en zonas sin sondas y fuera del
canal), longitud de correlación del orden de la separación entre sondas. Cada miembro del
conjunto usa una realización. Hay dos cosas que conviene tratar aparte del ruido: la
profundidad del canal dragado (un solo parámetro, porque la fecha de dragado no se
conoce) y el cambio de datum de la carta al nivel medio.

## 2. Prisma de marea — control analítico

Script: `scripts/prisma_marea.py` → `resultados/prisma_marea.csv` y `.png`.
Las entradas se tratan como distribuciones (triangulares, 200 000 muestras) porque ahora
mismo son de fuentes secundarias.

**Entradas provisionales**

| | central | rango | fuente |
|---|---|---|---|
| Área | 5,2 km² | 4,7–5,7 | fuentes divulgativas (Wikipedia, CubaConecta) |
| Profundidad media | 9 m | 7–11 | ídem; 47 hm³ / 5,2 km² = 9,0 m, cuadra |
| Rango mareal | 0,30 m | 0,20–0,50 | prácticos del puerto: pleamar superior media 0,4 m, bajamar inferior media 0,1 m; predicciones públicas de hasta 0,43 m esta semana |
| Canal | 1530 m de largo, 220–330 m de ancho, 12,8 m de calado | sección 2000–3600 m² | prácticos del puerto |
| Fracción de retorno β | 0,6 | 0,3–0,85 | **supuesto** (ver abajo) |
| Aporte fluvial | 2 m³/s | 0,5–5 | estimación gruesa, sin aforo |

**Resultados**

| | central | p5–p95 |
|---|---|---|
| Volumen | 47 hm³ | 39–55 |
| Prisma | 1,6 hm³ | 1,2–2,3 |
| Fracción renovada por ciclo | 3,3 % | 2,6–5,1 % |
| Renovación ideal (mezcla completa, sin retorno) | **16 días** | 10–20 |
| Renovación con retorno + río | **34 días** | 18–51 |
| Solo río | ~270 días | 130–500 |
| Velocidad máxima mareal en el canal | 4,5 cm/s | 3–6,5 |
| Excursión mareal en el canal | **~650 m** | 460–920 |

Lo que se esperaba se confirma: **el tiempo de residencia sale en semanas** (2–7).
El río no pesa: renovar la bahía solo con agua dulce llevaría del orden de un año.

**Lo que no se esperaba, y es importante:** la excursión mareal (~650 m) es **menos de la
mitad del largo del canal** (1530 m) en el 100 % de las muestras. Una parcela de agua que
sale de la bahía durante la vaciante no llega a salir del canal antes de que empiece la
llenante. Por eso el intercambio por marea pura es poco eficiente, β debería ser alto,
y el número de "renovación ideal" (16 días) es una **cota inferior optimista**.
Consecuencia para el diseño: es muy probable que el intercambio real lo controlen
procesos que el prisma no ve: **viento, circulación por densidad (vertidos de agua dulce
y calientes) y oscilaciones de nivel subinerciales del exterior.** Esto es un argumento
físico a favor del 3D y del conjunto, y de paso una frase buena para la introducción.

Control para el modelo numérico: el caso base 2D solo con marea tiene que dar una
**velocidad mareal en el canal de pocos cm/s** y una **renovación de 2 a 7 semanas**. Si da
horas o años, hay un error.

Cuando llegue la batimetría y los armónicos de FES2022/TPXO en la bocana, se actualizan
las entradas y se vuelve a ejecutar el script (tarda un segundo).

## 3. El cluster — lo que sé y lo que no

**No he podido entrar al cluster desde esta sesión** (la red solo llega a dominios
permitidos y el SSH no sale). Tampoco pude abrir las páginas de CÉCI (se agotó el tiempo
de conexión). Lo que sí está verificado en la documentación pública:

- **Hydra** (compartido VUB–ULB): Slurm, más de 3000 núcleos, más de 20 GPU, InfiniBand
  EDR, un nodo de 1,5 TB. Particiones con sufijo `_mpi` (varios nodos con InfiniBand,
  que es lo que necesita un 3D grande), `_gpu`, `_himem` y generales. **Tiempo máximo por
  trabajo: 120 h (5 días).** Nodos en uso exclusivo. Hay un cluster de pruebas, *Anansi*
  (12 h, 16 núcleos por usuario) para depurar.
- Si tu cluster es uno de los de **CÉCI** (Lemaitre4, NIC5, Dragon2, Hercules…), los
  límites son otros. Dime cuál es.

**Qué necesito que hagas (5 minutos):** en el nodo de login,

```bash
bash inventario.sh > inventario_$(hostname -s).txt 2>&1
```

(`cluster/inventario.sh`). Solo lee: particiones, tiempo máximo, memoria por nodo, QOS y
límite de trabajos por usuario, tamaño máximo de *arrays*, cuotas y *scratch*, y si están
SCHISM / TELEMAC / Delft3D / ADCIRC y las librerías para compilarlos (NetCDF-Fortran,
HDF5, ParMETIS, OpenMPI/Intel MPI, CMake, Apptainer). Con esa salida cierro la elección
de modelo y parto el conjunto.

**Cómo condicionan los límites (adelanto).** Con 120 h por trabajo, una simulación 3D de
90 días (≈ 3 veces el tiempo de residencia, más el arranque) se encadena con *hotstart*
si no cabe en un trabajo. El conjunto se lanza como **job array** (un miembro = una tarea
de pocos núcleos) y no como un único trabajo enorme: aquí lo que cuenta es el
rendimiento total (muchos miembros medianos), no escalar un solo modelo a mil núcleos.
El coste real por miembro (núcleos·hora) **se mide en el paso 3 con el caso base**. Antes
de eso cualquier número sería inventado; como orden de magnitud, espera de 10² a 10³
núcleos·hora por miembro 3D, así que un conjunto de 300 miembros cuesta entre 10⁴ y 10⁵,
cantidad que un cluster de este tamaño puede asumir.

## 4. Elección de modelo — recomendación condicionada

**Recomendación: SCHISM**, salvo que el inventario o la colaboración cambien las cosas
(regla abajo).

| Criterio | SCHISM | TELEMAC-2D/3D | Delft3D-FM |
|---|---|---|---|
| Malla no estructurada, canal estrecho | triángulos + cuadriláteros, resolución de 10–20 m en el canal sin problema | elementos finitos triangulares, igual de bien | *flexible mesh*, bien |
| Paso de tiempo | **semi-implícito, sin límite de CFL**: una celda de 10 m en el canal no hunde el paso de tiempo. Esto pesa mucho en un conjunto | semi-implícito también | implícito para la onda, limitado por advección; con velocidades de cm/s no es grave |
| Vertical en 3D | **LSC²**: número de capas variable, adecuado para un canal dragado de 13 m junto a ensenadas someras | sigma / capas fijas | sigma o z-sigma |
| Tiempo de residencia | **módulo AGE** (edad del agua con trazadores) incluido | edad con trazador + subrutina Fortran | vía D-WAQ |
| Partículas | `ptrack` incluido | derivadores/partículas incluidos | D-WAQ PART |
| Compilación en HPC | CMake, NetCDF y MPI, con ParMETIS incluido. Es de las más limpias | *scripts* Python propios, más dependencias | la más dolorosa de compilar; Deltares da contenedores |
| Forzamiento FES/TPXO + ERA5 | herramientas maduras (pyschism, scripts VIMS) | existen | Delft Dashboard (solo Windows) |
| Entorno en Bélgica | poco visible | **Flanders Hydraulics y la consultoría flamenca usan TELEMAC** (p. ej. modelo SCALDIS del Escalda) | Deltares al lado, IMDC |

**Regla de decisión:**

1. Si en el inventario **TELEMAC está instalado** o el colaborador que consigas trabaja
   con TELEMAC → **TELEMAC**. Un colaborador que ya sabe usar el código ahorra más
   meses que cualquier ventaja técnica.
2. Si no hay nada instalado y trabajas solo → **SCHISM**: sin límite de CFL, LSC²,
   edad del agua y partículas de serie, y compilación limpia.
3. **Delft3D-FM** solo si aparece alguien que ya lo use.
4. Antecedente que conviene citar y contactar: ya existe un **ADCIRC** de la bahía
   (CUJAE, 2016). ADCIRC se usa sobre todo en 2D y está pensado para marea de tormenta; no lo
   elegiría para edad del agua, pero su malla y su batimetría valen oro.

## 5. Colaboración en Bélgica

- **BGEOSYS (ULB): existe y lo dirige Pierre Regnier**, en IGEAT, Facultad de Ciencias,
  Solbosch. **Matiz:** su fuerte es la biogeoquímica y la modelización del sistema
  Tierra (ciclos de carbono y nutrientes, estuarios, transporte reactivo), no montar
  códigos hidrodinámicos 3D costeros. Sirve como coautor para **qué le pasa a la carga
  en la bahía** (nutrientes, oxígeno), pero probablemente no para pelearse con SCHISM.
  Aun así, merece una reunión: pueden conocer a quien lo haga.
- **ESA — Écologie des Systèmes Aquatiques (ULB), Nathalie Gypens**: modelización de
  ecosistemas costeros del sur del mar del Norte (MIRO&CO) acoplada a hidrodinámica 3D.
  Está en tu misma universidad y es más cercana a la costa que BGEOSYS.
- **SLIM, UCLouvain (Emmanuel Hanert; Eric Deleersnijder)**: malla no estructurada,
  seguimiento de partículas y conectividad en arrecifes. Deleersnijder es la referencia
  en **teoría de la edad del agua y tiempos de renovación** (CART), que es justo el
  núcleo de tu artículo. Es la colaboración técnica con más encaje en Bélgica.
  UCLouvain forma parte de CÉCI, igual que la ULB.
- **Flanders Hydraulics** (Amberes): si se elige TELEMAC, es el sitio donde lo usan a
  diario.

Orden sugerido: escribir a Hanert/Deleersnijder con el resultado del prisma (la
excursión menor que el canal es un buen gancho) y, en paralelo, pedir reunión con
Regnier/Gypens en la ULB.

## 6. Diseño del conjunto (borrador para cuando tengas el inventario)

Parámetros perturbados (muestreo Latin Hypercube o Sobol):

| Parámetro | Cómo |
|---|---|
| Batimetría | realización de campo aleatorio + profundidad del canal dragado |
| Fricción de fondo | Manning o Cd, rango uniforme, quizá distinto en canal y ensenadas |
| Caudales de vertido | factor log-uniforme ×0,3–×3 por foco, con temperatura y salinidad del vertido |
| Viento | factor de escala ERA5 (0,8–1,2) + giro ±15° + año distinto |
| Marea de contorno | FES2022 frente a TPXO (la diferencia entre ambos es la incertidumbre) |
| Mezcla vertical/horizontal | parámetros del cierre turbulento |

Con muestreo Sobol, el conjunto también da **índices de sensibilidad**: qué desconocido
mueve más el tiempo de residencia. Es un segundo resultado publicable, y además indica
**qué medida conviene hacer primero** (valor de la información). Es lo que convierte la
falta de datos en el centro del artículo.

## 7. Salidas pensadas para compararlas con Sentinel-2

Para que el modelo y el satélite hablen el mismo idioma:

- **Misma rejilla**: interpolar las salidas 2D a la ventana del protocolo congelado,
  UTM 17N (EPSG:32617), E 361 139–365 896, N 2 556 342–2 561 392, **a 20 m**.
- **Misma máscara de agua y misma línea de costa** que el protocolo (sección 5).
- **Misma hora**: guardar instantáneas a la hora de paso de Sentinel-2 (~10:30 hora solar
  local, alrededor de las 16:00 UTC en La Habana), no solo medias diarias.
- **Misma capa**: trazador en superficie (primer metro, más o menos la profundidad
  óptica en agua turbia), no promediado en la vertical.
- **Un trazador pasivo por foco** con emisión unitaria. Así la exposición de cada píxel
  se puede descomponer por origen.
- **Comparar patrones persistentes, no escenas sueltas**: mapa de exposición media del
  modelo frente al mapa de persistencia de anomalías del satélite (correlación de rangos
  por píxel, zonas que coinciden o no). Propuesta: **congelar este criterio de comparación
  antes de mirar los resultados**, igual que hiciste con Sentinel-2.

## 8. Riesgos — sin rodeos

1. **Nivel de agua sin medir.** El conjunto cuantifica la incertidumbre pero no la reduce.
   **Decisión urgente:** si la franja de octubre de 2026 a febrero de 2027 de tu
   `plan de viajes.xlsx` es tu estancia en Cuba, **te quedan unas dos semanas** para
   comprar el sensor. Dos cosas que importan:
   - **El sensor NO puede ir en el cuerpo de la boya.** La boya flota y sube y baja con la
     superficie, así que un sensor de presión colgado de ella mide siempre la misma
     profundidad, no la marea. Tiene que ir **fijo al fondo** (en el muerto del fondeo)
     o a un muelle.
   - Lo más robusto es un **registrador autónomo** (tipo HOBO U20L o similar), que no
     depende de la electrónica de la boya. La presión barométrica que ya registra la boya
     sirve para corregirlo. Mínimo 29 días de registro para separar M2, S2, K1 y O1;
     mejor 3 meses. Muestreo de 1 a 6 minutos. **Dos sensores (bocana e interior)**
     darían el desfase a lo largo del canal, que restringe directamente la fricción, el
     parámetro más incierto.
2. **El intercambio no es mareal** (sección 2). Si viento y densidad dominan, el 2D solo
   con marea puede dar una respuesta equivocada con total estabilidad. No hay que
   escribir conclusiones con el caso base 2D; sirve para comprobar que el modelo funciona.
3. **Batimetría.** Sin ella no hay nada. Pide ya la de la CUJAE y la del puerto, y compra
   la BA 414 como respaldo para no depender de nadie.
4. **Curva de aprendizaje, dónde no compensa:**
   - **no** compiles los tres modelos para compararlos; elige uno con la regla de la
     sección 4;
   - **no** montes el 3D baroclínico hasta que el 2D reproduzca la marea;
   - **no** hagas oleaje (SWAN/WWM): no entra en las tres preguntas;
   - **no** acoples biogeoquímica en este artículo (si llega, con BGEOSYS, en el siguiente);
   - **sí** compensa aprender bien Slurm, *job arrays* y el *hotstart*: lo usarás en todo.
5. **Plantilla.** La de tu grupo es Springer (sn-jnl), pero **EMS, Ocean Engineering y
   ECSS son de Elsevier**. Las tres aceptan cualquier formato en el primer envío; si lo
   aceptan, habrá que pasarlo a `elsarticle`. Si prefieres una revista Springer
   (*Ocean Dynamics*, *Estuaries and Coasts*), la plantilla ya sirve.

## 9. Próximos pasos

| # | Qué | Quién |
|---|---|---|
| 1 | Ejecutar `cluster/inventario.sh` y pasarme el .txt | Alex |
| 2 | **Decidir y comprar el sensor de presión (antes de viajar)** | Alex |
| 3 | Enviar la solicitud de batimetría (puerto/CIMAB) + correo a Ponce/Córdova (CUJAE) | Alex |
| 4 | Pedir la carta BA 414 | Alex |
| 5 | Extraer armónicos FES2022/TPXO en la bocana → actualizar el prisma | Claude |
| 6 | Contactar con SLIM (UCLouvain) y BGEOSYS/ESA (ULB) | Alex |
| 7 | Cerrar la elección de modelo con el inventario → caso base 2D | juntos |

---

## 10. Actualización (16-sep-2026): sin sensor de presión

Decisión de Alex: **no se instala sensor de presión**. Como mucho, muestras semanales o
fotos. Sustitutos de la validación:

- **Mareógrafo HABANA (PSMSL, estación 2363)**: 23,13° N, 82,34° W (posición al minuto),
  de 2021 a 2024, 92 % completo, **Servicio Mareográfico Nacional de Cuba**. PSMSL solo
  publica medias mensuales; hay que **pedir la serie horaria o minutal** al servicio. Con
  eso se tienen las constantes armónicas en la bahía, que es justo lo que iba a dar el
  sensor. Es la petición de datos más valiosa del proyecto.
- **HAVANA (PSMSL 534)**, 1947–1956, marcado como "no research quality": como mucho,
  para comparar las constantes armónicas.
- **Siboney (PSMSL 1162)**, costa abierta al oeste: para comprobar la marea de contorno
  FES/TPXO.
- Muestras y fotos: **descartadas** (decisión de Alex, 16-sep).

## 11. Escenario actual: sin trabajo de campo, cálculo en el cluster

Aclaración (16-sep): "todo desde el portátil" = **no se va a la bahía**. El cluster sí se usa.

**Qué se publica.** Conjunto **3D** (SCHISM, cientos de miembros) para una bahía de bolsa
sin datos de calibración propios. El 2D queda como caso base y control, no como resultado.
- Control analítico (prisma; la excursión mareal es menor que el canal).
- Mapa de tiempo de residencia/edad del agua con envolvente (p5–p50–p95) y **mapa de
  probabilidad de "no se lava"**, en superficie y en el fondo.
- Destino de los vertidos con partículas: fracción exportada frente a retenida a 30/60/90 d, por foco.
- Sensibilidad (Sobol): qué desconocido pesa más (batimetría CUJAE frente a BA 414,
  fricción, viento, marea de contorno, caudales y flotabilidad de los vertidos).
- Resultado físico que solo da el 3D: **cuánto del intercambio es por densidad frente a
  la marea** (miembros con y sin vertidos flotantes).
- Validación, solo con datos de terceros: mareógrafo HABANA (si llega la serie) +
  comparación cualitativa con la persistencia de turbidez de Sentinel-2.
- Revista: **Environmental Modelling & Software**; alternativa ECSS.

**Qué gestiona Alex.**
1. Decir cuál es el cluster y ejecutar `cluster/inventario.sh`.
2. Comprar la carta BA 414.
3. Escribir a Ponce Portela / Córdova López (CUJAE) para pedir la batimetría o malla del ADCIRC.
4. Pedir la serie horaria del mareógrafo HABANA (2021–2024) al Servicio Mareográfico Nacional.
5. Crear cuentas gratuitas: Copernicus CDS (ERA5) y AVISO (FES2022) o TPXO.
6. Lista de focos de vertido (nombre + coordenada aproximada), de la línea de Sentinel-2 o de CIMAB.

## 12. Gestiones en curso (16-sep)

- CUJAE (Ponce Portela / Córdova López): **escrito por Alex**, pendiente de respuesta.
- Carta BA 414 (UKHO, 1:10 000, ed. 04-01-2021, 23°06,70'–23°10,10' N,
  82°24,90'–82°19,10' W; cubre toda la bahía y la bocana). Solo en papel, impresa bajo
  demanda. Precios vistos: Bookharbour (Southampton) 48,30 £ con IVA; Weilbach
  (Copenhague) 530 DKK con IVA; Maryland Nautical (EE. UU.) 54,95 $.
- Mareógrafo HABANA (PSMSL 2363): lo opera el Servicio Mareográfico Nacional, que forma
  parte del Servicio Hidrográfico y Geodésico de la República de Cuba (GEOCUBA Estudios
  Marinos, Playa; dependiente del MINFAR). Pedirlo por carta institucional (UH/ARES).

## 13. Cluster = CÉCI (16-sep)

Acceso pendiente de aprobación. Datos públicos (presentación ULiège, feb-2025):

| Cluster | Sede | Núcleos | RAM/nodo | GPU | Tiempo máx. |
|---|---|---|---|---|---|
| NIC5 | ULiège | 4672 | 256 GB–1 TB | no | 2 días |
| Lemaitre4 | UCLouvain | 5120 | 766 GB | no | 2 días |
| Hercules2 | UNamur | 1024 | 256 GB–2 TB | sí | 15 días |
| Dragon2 | UMons | 592 | 192–384 GB | sí | 21 días |

Un login y un home comunes. Implicaciones:
- **NIC5 / Lemaitre4** para el 3D en MPI y el conjunto (muchos núcleos, 2 días).
  Cada miembro se divide en tramos de < 48 h con *hotstart*, o se dimensiona para caber.
- **Hercules2 / Dragon2** para trabajos largos de pocos núcleos (p. ej. el 2D base).
- Ejecutar `cluster/inventario.sh` en cada cluster que se use: los módulos no son iguales.

## 14. Paso 3: entorno y SCHISM compilados en el Mac (27-sep)

`scripts/instalar_entorno_mac.sh` funciona. Registros en `cluster/`.

- Mac Apple Silicon (arm64), macOS 26.6.2, Command Line Tools instaladas.
- Entorno conda `bahia` (miniforge): gfortran 15.3 (conda-forge), clang 21, MPICH (MPI 5.0),
  NetCDF-C 4.10.1 / NetCDF-Fortran 4.6.4, CMake 4.4, Python 3.11 con cdsapi.
- SCHISM `develop`, commit `09f407e8` (23-sep-2026), en `~/modelos/schism`.
- Ejecutable: `~/modelos/schism/build/bin/pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL`
  (módulo AGE, limitador TVD van Leer, ParMETIS interno).
- 56 avisos de tipo en llamadas MPI (normales con gfortran ≥ 10 y `-fallow-argument-mismatch`).

**Tres fallos de SCHISM con la cadena conda (gfortran + clang) y cómo se resolvieron:**

1. `cmake/SCHISMCompile.cmake` pasa `--preprocess` a gfortran cuando el compilador de C es
   clang; gfortran lo interpreta como `-E` (solo preprocesar): los `.o` salen en texto y no hay
   `.mod` ("Error copying Fortran module"). **Parche:** `--preprocess` → `-cpp`.
2. `src/CMakeLists.txt` aplica ese indicador a todos los lenguajes (`add_compile_options`);
   clang rechaza `-cpp` al compilar el C de ParMETIS. **Parche:** solo para Fortran
   (`$<$<COMPILE_LANGUAGE:Fortran>:...>`).
3. `cmake/SCHISM.local.conda` fija `PARMETIS_ROOT`; al no encontrar ParMETIS en conda dice que
   vuelve al interno, pero no lo compila y el enlazado pide `-lparmetis`. **Solución:** no usar
   ese archivo (los compiladores MPI se pasan por línea de comandos).

Los dos parches los aplica el script sobre el clon local (originales en `*.orig`) y quedan
anotados en `cluster/schism_version.txt`. **En CÉCI** probablemente no hagan falta (compiladores
GNU o Intel sin clang), pero si aparece "Error copying Fortran module" es el fallo 1.

**Pendiente del paso 3:** un caso de prueba corto (p. ej. un test de SCHISM o el 2D base con
malla provisional) para medir el coste por paso de tiempo en el Mac antes de ir a CÉCI.

## 15. Forzamiento atmosférico ERA5 descargado (27–30 sep)

`scripts/descargar_era5.py` bajó los 120 meses (ene-2016 a dic-2025) en unas 51 h, con
cortes de red del CDS que cdsapi reintentó solo. Registro: `cluster/era5_descarga.log`.

- Zona 22,8–23,5 N, 82,8–81,9 W (rejilla 0,25°), horario, 40 MB en total, en
  `datos/forzamiento/era5/` (no versionado).
- **El CDS devuelve un ZIP** aunque se pida `unarchived`, porque mezcla variables
  instantáneas y acumuladas. El script ahora lo separa en dos NetCDF por mes:
  - `era5_habana_AAAAMM_instant.nc`: u10, v10, msl, t2m, d2m;
  - `era5_habana_AAAAMM_accum.nc`: ssrd, strd, tp, acumulados en la hora anterior
    (J m⁻² y m). Para SCHISM (`sflux`) hay que pasarlos a flujos (÷ 3600 s) y a kg m⁻² s⁻¹.
- Los 120 ZIP ya descargados se convirtieron así (240 archivos HDF5/NetCDF4).
- **Verificado (30-sep):** 87 672 horas (= 10 años exactos), paso de 1 h sin huecos y sin NaN
  en los 240 archivos. Rejilla ERA5 efectiva: 3 × 4 puntos (23,0–23,5 N; 82,75–82,0 W).

**Siguiente:** convertir ERA5 al formato `sflux` de SCHISM (air/rad/prc) y un caso de
prueba corto con malla provisional para medir el coste por paso de tiempo.

## 16. Prueba de humo de SCHISM: caso idealizado (30-sep a 2-oct)

Scripts: `scripts/era5_a_sflux.py` (ERA5 → `sflux` de SCHISM, 120 meses en
`datos/forzamiento/sflux/`), `scripts/caso_prueba.py` (genera el caso),
`scripts/revisar_prueba.py`, `scripts/diagnostico_prueba.py`, `scripts/diagnostico_forzamiento.py`.

**Caso.** Geometría esquemática con las cifras del control analítico: bahía 2650 × 2000 m a 9 m
(5,3 km²), canal 250 × 1530 m a 12,8 m, mar 4050 × 2000 m a 30 m, en su posición real.
Malla de 50 m (5674 nodos, 10 868 triángulos), 10 capas sigma, dt = 100 s. Marea M2 de 0,15 m
en los bordes N, E y O del mar; viento y presión ERA5 (`nws=2`); módulo AGE con el mar como fuente.

**Resultado (2 días, enero de 2016, versión final del script).** La cadena funciona de punta a punta:
compilación, `sflux`, `bctides` con trazador AGE, salidas `out2d`/`AGE_1`.
- Marea en la bahía 14,9 cm (forzada 15): la bahía sube y baja en bloque, como predice el prisma.
- Corriente en el canal 2,4 cm/s de media, 8,6 de máximo (control analítico 3–6,5 cm/s; el
  esquema es más corto y ancho que la realidad, así que el orden de magnitud es lo que cuenta).
- Mar: ≤ 0,19 m/s con viento ERA5 de 2–4 m/s.
- AGE: escribe; 2 días no dan para la edad (renovación de semanas).

**Coste en el Mac.** 0,47–0,54 s/paso con 1 proceso de cálculo → 7–8 min por día simulado.
Con varios procesos MPI es ~30 veces **más lento**: MPICH de conda en macOS tiene mucha latencia
(usa la interfaz de red). En el Mac: 1 proceso de cálculo + 2 *scribes* (`correr.sh` lo fija).
Lanzar con `caffeinate -i` y la tapa abierta: en reposo va 2–4 veces más lento.

**Lo aprendido (aplica a la malla real):**
1. Todo `.gr3`/`.ic` necesita `ne np` reales en la cabecera.
2. Ningún triángulo con los 3 nodos en el contorno (pasaba en esquinas SE/NO de la malla
   cuadriculada); da ruido que crece.
3. El mar no puede ser una caja cerrada por los lados: atrapa un modo este-oeste (~8 min).
4. Sin advección de momento cerca del borde abierto (`nadv=0` + `adv.gr3` = 0 a < 250 m):
   la ELM daba ~6 m/s espurios en el borde.
5. `hgrid.ll` con suficientes decimales (8): con 3, los nodos vecinos compartían coordenadas.
6. **Coriolis + nivel impuesto en el borde + viento → inestabilidad** (crece ×2,7 cada ~3,5 h y
   satura en ~6 m/s). Sin viento no arranca; con esponja de fricción tampoco se arregla; sin
   Coriolis desaparece. En este caso de juguete se usa `ncor=0`. **Pendiente de verificar con la
   malla real** (borde abierto lejano, en aguas profundas y en un solo arco). Si persiste:
   condición de borde con relajación de velocidades (Flather/`ifltype`) o dominio más grande.

**Siguiente:** cuando llegue la batimetría (CUJAE o BA 414), malla real con borde en aguas
profundas; repetir esta prueba con `ncor=1`; después, el 2D/3D base y el inventario de CÉCI.

## 17. Batimetría: búsqueda en internet (2-oct)

No hay cuadrícula moderna abierta. Fuentes encontradas y propuesta (carta U.S. H.O. de 1889
georreferenciada + 1898 + canal a 12,8 m + calados de muelles + GEBCO, con incertidumbre 1–2 m
fuera del canal como dimensión del conjunto): ver `docs/resumen_para_articulo.md`, sección 4.

## 18. Reorganización (2-oct): enfoque nuevo del artículo

Pregunta: **¿qué partes de la bahía no se renuevan, y esa conclusión sobrevive a no tener datos?**
Título provisional: "What can be known about flushing in a bay without data? Robust and
fragile conclusions from a public-data ensemble model of Havana Bay, Cuba" (EMS).

Reglas: (1) **solo datos públicos** con URL y fecha de acceso (`docs/procedencia_datos.md`);
no se compra la BA 414; CUJAE/GEOCUBA/mareógrafo solo como comparación opcional.
(2) **Acceso completo a CÉCI**: conjunto 3D de cientos de miembros + experimentos de mecanismo.

| # | Trabajo | Scripts / salida | Estado |
|---|---|---|---|
| 1 | Batimetría pública: sondas de 1889 y 1898 (unidades y datum), canal 12,8 m, muelles, GEBCO, costa Sentinel-2 → 2 superficies + diferencia + campo aleatorio | `scripts/batimetria/` | en curso (descargas) |
| 2 | Malla real (borde en aguas profundas, un arco; canal 10–20 m; ensenadas resueltas); prueba de humo con `ncor=1` | — | después de 1 |
| 3 | Marea FES2022 (TPXO alternativa y dimensión del conjunto); recalcular `prisma_marea.py` | — | AVISO en trámite |
| 4 | Caso base 3D (LSC², AGE, partículas) en CÉCI: coste por miembro; ¿cabe en 2 d o hotstart? Antes, `cluster/inventario.sh` | `cluster/` | inventario pedido |
| 5 | Conjunto: Saltelli (SALib) sobre batimetría (realización + carta), fricción, viento (×0,8–1,2, ±15°), marea (FES/TPXO), caudales (×0,3–3) y flotabilidad, mezcla; N según coste; convergencia por bootstrap; job arrays | — | |
| 6 | Mecanismo (factorial): marea / +viento / +viento+densidad | — | |
| 7 | Salidas definidas antes de lanzar (ver abajo) | — | |
| 8 | Tabla de procedencia de datos | `docs/procedencia_datos.md` | iniciada |

Salidas (7): (a) por miembro, edad media y percentiles por zona (canal, cuenca principal,
Marimelena, Guasabacoa, Atarés) + mapas 2D superficie/fondo; (b) P(edad > 30 d) por zona y en
mapa; (c) Sobol primer orden y total por zona; (d) flujo neto e intercambio en la sección del canal
por experimento; (e) partículas por foco: fracción retenida a 30/60/90 d; (f) trazador en superficie
en la rejilla Sentinel-2 (UTM 17N, 20 m, E 361139–365896, N 2556342–2561392) a ~16:00 UTC.

Figuras finales (en inglés) → `publication plan/modelo-hidrodin-mico/articulo/figuras/`.

## 19. Batimetría pública: primeras fuentes (2-oct)

Descargado (`datos/batimetria/fuentes/descargas.tsv` con URL, fecha y sha256):
- **GEBCO 2026 Global** (+ TID), 22,9–23,4 N, 82,6–82,1 W, 120 × 120 celdas de 15″.
  **La bahía no existe en GEBCO**: dentro sale como tierra (TID 0, cotas +5 a +50 m).
  Fuera, el talud es muy abrupto: frente a la bocana −126 m a ~1 km, −313 m a 2 km,
  −725 m a 3,5 km, −1220 m a 5 km. Casi todo es TID 40 (predicho por gravimetría satelital),
  con algo de TID 44; sondas directas (TID 11 monohaz, 16 lidar) solo en celdas aisladas.
  Consecuencia: el borde abierto de la malla puede ir a 3–5 km de la costa ya en aguas de
  700–1200 m; un solo arco es fácil. GEBCO solo sirve fuera de la bahía.
- **Prácticos (2018)**: texto extraído en `practicos_puerto_habana_2018.txt`. Canal 1530 m,
  rumbo 124°, 220–330 m, 12,8 m; calado máx. 11,43 m (11,58 con pleamar ≥ 0,2 m). Canales de
  acceso: refinería y dique seco 11,58 m, Atarés 10,5 m, Guasabacoa 9,75 m. Fondeaderos:
  La Tasajera 10,0 m, Casablanca 6,7 m. ~60 calados de muelles (1,6–11 m).
  Frases citables: "Las corrientes de marea en el interior del puerto son imperceptibles";
  fuera de la entrada, a la altura de Punta Barlovento, una corriente cruza el canal con
  hasta 4 nudos en mayo–junio; viento dominante NE con giro diurno (brisa) a S por la tarde.
  Uso: calado = profundidad mínima (cota superior del fondo) en cada muelle, una vez
  georreferenciados los muelles (pendiente, con OpenStreetMap).
- **Carta de 1898** = U.S. H.O. **chart n.º 307**, ed. 1898 (BPL G9096.P5 svar .U55 no. 307 1898).
  El enlace de descarga daba HTML; se baja ahora del servidor IIIF (7994 × 5527 px).
- Pendiente: carta de 1889 (Harvard, manual) y línea de costa Sentinel-2.

**Actualización 2 oct (tarde).** Descargada la carta "1889" de Harvard (GeoTIFF 640 MB + metadato FGDC). El metadato aclara que es la carta H.O. *Harbor of Havana: from the most recent Spanish surveys to 1879* (1.ª ed. 1882, ed. 1889, ~1:8 000): **los sondeos son de levantamientos españoles hasta 1879**, no de 1889. Georreferenciada a la carta H.O. de 1962 en NAD27 Cuba Norte con RMS 18,3 m (el error de posición entra en el campo aleatorio). La carta 1898 (H.O. 307) puede ser en buena parte la misma fuente: hay que comparar sondeo a sondeo antes de tratarlas como dos batimetrías independientes. Documentación y términos de uso de GEBCO guardados en `fuentes/`.

**Actualización 13 oct — lectura de las dos cartas.**
- Las dos son la carta H.O. n.º 307 *Harbor of Havana* (misma plancha). La de 1889 dice "from the most recent Spanish surveys **to 1879**"; la de 1898 (corregida a 10-mar-1898, "extensive corrections Dec. 1891") dice "**to 1887**". Comparten el dibujo de tierra, pero **los sondeos del canal son distintos** (otras posiciones y valores), así que hay dos épocas de levantamiento: 1879 y 1887. Se tratan como dos realizaciones de carta, sin suponer que sean independientes del todo.
- **Unidades: brazas** ("Soundings in fathoms"), con cuartos (1 braza = 1,8288 m; resolución 0,46 m).
- **Nivel de referencia: no está escrito.** Lo habitual en las cartas H.O. de levantamientos españoles es bajamar. Cartela: "H.W.F.&C. VIII h 14 m. Rise of tide about 3 ft". Se tratará como bajamar con un desplazamiento incierto (0 a +0,5 m) que entra en el conjunto.
- Canal de entrada: 7–9¼ brazas (13–17 m) en 1879 y 8–10 brazas (15–18 m) en 1887, más profundo que los 12,8 m que garantizan hoy los prácticos (calado de proyecto, no fondo natural).
- El GeoTIFF de Harvard **viene en WGS84 geográfico** (EPSG:4326, píxel 6,37e-6° ≈ 0,65 m), no en NAD27 como dice el metadato: píxel → lon/lat es directo. La de 1898 (JPEG IIIF) no está georreferenciada: se ajustará con puntos de control comunes con la de 1889 (misma plancha).
- Siguiente: digitalizar los sondeos (1889 primero porque ya está georreferenciada), georreferenciar la de 1898 y digitalizarla, y comparar las dos.

**Actualización 13 oct (tarde) — sondeos de 1879 digitalizados.**
- 1126 sondeos leídos a mano (1117 en la primera versión: el filtro de duplicados borraba 9 sondeos reales muy juntos; corregido el 13 oct) de la carta H.O. 307 (ed. 1889, levantamientos hasta 1879) sobre teselas con cuadrícula de píxeles (`scripts/batimetria/02_teselas.py`), pasados a lon/lat WGS84 y metros (`04_sondeos_a_coordenadas.py`, con comprobación del faro del Morro) → `datos/batimetria/sondeos/sondeos_1889.csv` (columnas lon, lat, brazas, prof_m, dudoso, x_pix, y_pix).
- Cubren toda la bahía (canal, cuenca principal, Marimelena, Guasabacoa, Atarés) y la franja exterior hasta ~1,7 km al oeste de la entrada. Figura de control: `docs/figuras/control_sondeos_1889.png` (y `03_control_sondeos.py` para revisar a resolución completa).
- `dudoso=1` (~41): lectura dudosa, casi todas fracciones "⅓"/"⅙" en los bajos (la carta usa tercios de braza en aguas muy someras). `dudoso=2` (4): sondeos "sin fondo a 109 brazas" fuera de la plataforma (cota mínima, no profundidad).
- Incluye las etiquetas de las isóbatas de 3 y 5 brazas como puntos de esa profundidad.
- Pendiente: segunda pasada de revisión a resolución completa por zonas, y la carta de 1898 (levantamientos hasta 1887).

## 20. CÉCI — inventario (13 oct 2026)

- Acceso SSH funcionando (usuario `arivera`, ULB) a NIC5 y Lemaitre4.
- **NIC5**: Slurm 22.05; partición `batch` 70 nodos × 64 núcleos AMD EPYC 7542 (Rome), 256 GB; `hmem` 3 nodos × 1 TB; **límite 2 días por trabajo**. Por usuario (QOS normal): **448 núcleos a la vez**, 201 trabajos en ejecución, 402 en cola; arrays de hasta 1001. HOME 100 GB; scratch en `/scratch/ulb/cenoli/arivera` (BeeGFS).
- Ningún modelo oceánico instalado como módulo → compilar SCHISM nosotros. Hay todo lo necesario: `foss/2023b` (GCC 13.2, OpenMPI 4.1.6), netCDF-Fortran 4.6.1, ParMETIS 4.0.3, CMake 3.27, Python 3.11, GDAL 3.9. Apptainer disponible.
- **Lemaitre4** (repetido con `bash -l`): Slurm 24.11; `batch` 40 nodos × **256 núcleos** AMD EPYC 9534 (Genoa), 750 GB; 2 días máx.; **4096 núcleos por usuario**; arrays de hasta 10 000. Scratch en `/globalscratch/ulb/cenoli/arivera`. Tiene foss/2023b–2025b. Es el mejor candidato para el conjunto (9× más núcleos simultáneos que NIC5).
- **SCHISM compilado en NIC5** (13 oct): commit 09f407e8 (= Mac), foss/2023b, netCDF-Fortran 4.6.1, módulo AGE → `~/schism/build/bin/pschism_AGE_BLD_STANDALONE_SH_MEM_COMM_TVD-VL` (registro `cluster/schism_nic5.log`; solo avisos de tipos MPI, normales con GCC ≥ 10). Script: `cluster/compilar_schism_ceci.sh`.
- **SCHISM compilado en Lemaitre4** (13 oct): mismo commit, toolchain elegida por el script: releases/2024a, foss/2024a, netCDF-Fortran 4.6.1, CMake 3.29 (registro `cluster/schism_lemaitre4.log`).
- Siguiente: medir el coste por miembro con la malla real (Lemaitre4 para el conjunto, NIC5 para pruebas).

**Actualización 13 oct (noche) — carta de 1898 (levantamientos hasta 1887).**
- Registrada sobre la de 1889 sin puntos a mano: SIFT + RANSAC + polinomio de 2.º grado (`scripts/batimetria/05_registro_1898.py`, 2432 pares, residuo mediano 1,9 px = 1,2 m; p90 2,6 m) → `datos/batimetria/sondeos/transformacion_1898_a_1889.json`. Comprobación: el faro del Morro cae a 12 px (8 m) de su posición en la de 1889.
- **1514 sondeos** digitalizados de la ed. 1898 → `datos/batimetria/sondeos/sondeos_1898.csv` (`04_sondeos_a_coordenadas.py` con la transformación). Figura superpuesta: `docs/figuras/control_sondeos_1879_1887.png` (`06_comparar_cartas.py`).
- **Comparación 1879 vs 1887** (vecinos a < 25 m): fuera de la bahía la ed. 1898 repite en buena parte los sondeos de 1879 (52 % de los pares con el mismo valor); **dentro de la bahía hay un levantamiento nuevo** (1113 sondeos frente a 793, en líneas distintas; 35 % de pares con el mismo valor). Donde difieren: |Δz| medio 0,76 m dentro y 1,16 m fuera; p10–p90 de 1887−1879 dentro: −1,4 a +0,9 m. Sin sesgo neto (mediana 0). Desfase medio entre ambas digitalizaciones ~4 m (error de lectura y registro), muy por debajo del espaciado de sondeos.
- **Consecuencia para el conjunto**: la incertidumbre de carta dentro de la bahía es del orden de 1 m (1σ) a la escala de los sondeos, consistente con la propuesta de σ 1–2 m del campo aleatorio. Las dos cartas sirven como dos realizaciones, no independientes fuera de la bahía.
- Siguiente: superficies 1879/1887 (interpolación sobre la máscara de agua), diferencia, y el campo aleatorio; canal y muelles de los prácticos; GEBCO fuera.

**Actualización 13 oct (noche) — primeras superficies.**
- Costa actual: OpenStreetMap (`natural=coastline`, instantánea 2026-10-13T15:41Z vía Overpass; 44 vías). Muelles y espigones aún no incluidos.
- `scripts/batimetria/07_superficies.py` (+ `utm.py`, proyección UTM 17N sin dependencias, con autotest): rejilla UTM 17N de 20 m (E 354–368 km, N 2554–2566 km), interpolación lineal de los sondeos + costa a profundidad 0 (triángulos de > 500 m descartados), fusión con GEBCO 2026 a 150–600 m del sondeo más cercano, profundidad mínima 0,3 m. Salidas en `datos/batimetria/superficies/` (NetCDF, fuera de git; se regeneran en segundos) y `docs/figuras/superficies_1879_1887.png`.
- **Números (bahía = agua al S de N 2 560 950 y al E de E 361 000, incluye el canal):** área 4,91 km²; profundidad media **5,6 m (1879) y 5,2 m (1887)**; volumen **27,5 y 25,7 hm³**. Diferencia 1887 − 1879 celda a celda donde ambas tienen sondeos: media −0,38 m, desviación 1,31 m (p10 −1,7, p90 +0,9).
- **Ojo — discrepancia con el control analítico:** `prisma_marea.py` usa 9 m de profundidad media y ~47 hm³ (fuentes divulgativas, bahía actual). Las cartas del siglo XIX dan casi la mitad del volumen. La diferencia es plausible (dragados del siglo XX: los prácticos garantizan 9,75–11,58 m en los canales de acceso a Guasabacoa, Atarés, refinería y dique seco, donde 1879 marca 5–9 m), pero el volumen entra directo en el tiempo de renovación. Propuesta: tratar el **estado de dragado** como dimensión del conjunto (de la batimetría histórica a una versión "actual" con canales de acceso y muelles a sus calados de prácticos) y recalcular el prisma con el volumen de las superficies.

**Actualización 13 oct (noche) — batimetría del conjunto y prisma recalculado.**
- **Canal de entrada comprobado con la costa OSM:** ancho de agua 250–400 m a lo largo de ~1,6 km (prácticos: 220–330 m, 1530 m). El eje de las celdas > 11 m tiene rumbo 131° (prácticos: 124°); se usa el de prácticos por el centroide del canal (361 646 E, 2 560 188 N). En las cartas, la parte > 12 m solo tiene 40–160 m de ancho.
- **Variograma de la diferencia 1887−1879** (12 134 celdas con sondeos de ambas): exponencial con meseta 1,08 m², alcance L = 149 m, pepita 0,54 m² → **σ_carta = √((meseta+pepita)/2) = 0,9 m, L ≈ 150 m**. Son los parámetros del campo aleatorio, estimados de los datos y no supuestos.
- `scripts/batimetria/08_batimetria_conjunto.py`: genera la batimetría de cada miembro con (carta 1879/1887, α = estado de dragado 0–1, σ, L, datum, semilla). α = 1: canal de entrada ≥ 12,8 m (220 m × 1530 m, rumbo 124°) y toda el agua navegable histórica (≥ 5 m, conectada al canal) a 11 m (canales de acceso 9,75–11,58 m según prácticos). El campo aleatorio no toca el canal garantizado y se atenúa hacia la orilla. Figura: `docs/figuras/batimetria_conjunto.png`; volúmenes: `datos/batimetria/superficies/volumenes_conjunto.json`.
- **Volumen de la bahía (hm³):** 1879: 27,5 (α=0) / 31,7 (α=0,5) / 35,8 (α=1); 1887: 25,7 / 29,6 / 33,5. El campo aleatorio solo mueve ±1 hm³ (p5–p95) porque se promedia. **Ni dragando toda la zona navegable a 11 m se llega a los 47 hm³ divulgativos** (haría falta 9,6 m de media en toda la bahía, ensenadas incluidas, incompatible con los calados de prácticos de 1,6–6,7 m en buena parte de los atraques y fondeaderos). La cifra divulgativa no es coherente con las cartas ni con los prácticos.
- **`prisma_marea.py` actualizado** (A = 4,91 km², h = 5,2–7,3 m, moda 6,2): V 30 hm³ (27–35); renovación ideal 10,7 d (7–14); **con retorno y ríos 23 d (13–35 d)**; antes 34 d (18–51 d). Excursión mareal 610 m (sin cambio, 0,4 del canal). El artículo debe actualizar esta cifra.

## 21. Malla real y caso SCHISM (13 oct 2026)

- `scripts/batimetria/09_malla.py`: malla de triángulos con DistMesh (Persson y Strang 2004), solo numpy/scipy. Dominio = agua de la superficie de 1887 dentro de un círculo de 5 km centrado en la boca (361 000 E, 2 560 900 N); el arco en mar abierto es el borde abierto (33 nodos, 46–1220 m de fondo). Costa simplificada a la escala de la malla (dársenas < 60 m cerradas, islotes < 0,02 km² quitados).
- Tamaños: 25 m en el canal (~11 elementos a lo ancho), 40 m en la bahía, creciendo al 15 % fuera hasta 400 m. Resultado: **4832 nodos, 8941 elementos** (4001 nodos en la bahía); ángulo mínimo 12,4°, 7 elementos < 20° (en la transición de la boca). `datos/malla/hgrid.{gr3,ll}`, `docs/figuras/malla.png`, `datos/malla/malla_resumen.json`.
- La definición de "bahía" (también en 08) incluye ahora la cabecera de Atarés al O de E 361 000; los volúmenes cambian < 0,2 %.
- `scripts/batimetria/utm.py` tiene ahora la inversa (UTM → lon/lat) con prueba de ida y vuelta.
- `scripts/caso_real.py`: caso SCHISM sobre la malla real con la batimetría de un miembro (CARTA, ALFA, SEMILLA). Profundidad del modelo topada a 200 m (el talud llega a 1200 m; solo transmite la marea). 16 niveles S, dt 100 s, Coriolis activado, ERA5, AGE con "agua nueva" = la de fuera de la bahía, sin advección de momento a < 800 m del borde abierto. **Marea M2 uniforme de 0,15 m PROVISIONAL** hasta tener FES2022. Genera `correr.sh` (Mac) y `correr_slurm.sh` (CÉCI, escribe el coste en `coste.txt`).
- Siguiente: correr la prueba de 2 días con Coriolis en NIC5 a 4/8/16/32 núcleos → ¿estable con Coriolis? y coste por miembro.
- **13 oct, 19:36 — primera simulación real en NIC5: corre y termina** (2 días, 1728 pasos, Coriolis activado, ERA5 + M2 provisional). Tras dos correcciones de `vgrid.in` (h_s debe superar el fondo máximo; si no, SCHISM exige niveles Z por debajo). Coste medido (pared): 8 núcleos de cálculo 172 s, 16 → 116 s, 32 → 110 s (no escala más allá de 16 con 4832 nodos). 4 núcleos → 279 s. Coste en núcleo·s: 4 → 1116, 8 → 1376, 16 → 1856, 32 → 3520; lo más eficiente es 4–8 núcleos por miembro. Un miembro de 90 días: ~3,5 h con 4 núcleos, ~2,2 h con 8 (`cluster/coste_real_prueba.txt`). Pendiente: revisar los campos (estabilidad con Coriolis, `scripts/revisar_real.py`).
- **Revisión de la prueba real (2 días, Coriolis, `revisar_real.py`):** sin NaN; la bahía sigue a la marea exterior en bloque (14,9 cm de amplitud, desfase 0 h); corriente en el canal media 2,5 cm/s y máx. 7,7 cm/s (control analítico ~4 cm/s) y en la bahía 1,2 cm/s de media → **la física de la bahía es coherente y no hay inestabilidad que crezca con Coriolis** (velocidad máxima diaria 0,81 → 2,06 → 2,08 m/s, se satura). **Defecto:** chorro espurio de hasta 2 m/s (media 0,1 m/s) en el extremo E del borde abierto, donde el arco corta la costa: el viento empuja agua a lo largo de la costa contra un nivel impuesto. Corrección en `caso_real.py` (ESPONJA=1 por defecto): fricción 0,0025 → 0,05 a < 1 km de los extremos del borde abierto y sin viento a < 1 km del borde (rampa hasta 2 km, `windfactor.gr3`, iwindoff=1). Pendiente de comprobar.
- **Esponja comprobada (13 oct, `runs/real_esponja`, 10 núcleos NIC5):** la velocidad máxima baja de 2,08 a 1,09 m/s. El defecto queda en **4 nodos**: la esquina E donde el borde abierto toca la costa (1,09 m/s; 62 m de fondo junto a un nodo de 8 m) y sus 3 vecinos directos (0,84 / 0,68 / 0,31 m/s), todos a < 450 m de la esquina y a ~5 km de la boca. El siguiente nodo más rápido (0,25 m/s, E 363 790 N 2 562 351) ya está en la deriva por viento de la plataforma (media del último día ~0,1 m/s, plausible para alisios de ~6 m/s). La franja de 1 m/s de la figura anterior era un artefacto del dibujo (Delaunay rellenando tierra); `revisar_real.py` ya dibuja con los triángulos de la malla y lista los 5 nodos más rápidos.
- **Prueba de sensibilidad gratis:** con y sin esponja el chorro cambia ×2 y las cifras de la bahía son idénticas a la décima (14,9 cm; canal 2,5 / 7,7 cm/s; bahía 1,20 cm/s, p99 5,5 cm/s) → **el tratamiento del borde no llega a la bahía**. Se acepta la esponja como configuración base; el defecto se documenta (Methods/suplementario) y las figuras recortan a < 500 m de la esquina. Si las salidas de la boca (pluma, intercambio) se vieran afectadas, se corrige la geometría de la esquina (mover el extremo del arco a la isóbata de 20–30 m).
- Siguiente: marea real FES2022 en el borde abierto (sustituye a la M2 provisional) y recalcular `prisma_marea.py` con sus armónicos.
- **Marea FES2022 preparada (13 oct):** cuenta AVISO+ creada por Alex (esperando credenciales). `scripts/marea_fes2022.py` baja 11 constituyentes (M2 S2 N2 K2 K1 O1 P1 Q1 M4 MS4 MN4) de `fes2022b/ocean_tide_extrapolated` (THREDDS de AVISO), recorta una caja de 0,6° × 0,5° y guarda `datos/marea/fes2022_habana.json` + `datos/marea/descargas.tsv`. `caso_real.py` usa FES por defecto si existe ese archivo (MAREA=m2 para la prueba antigua): interpolación bilineal en complejo a los 33 nodos del borde, factores nodales f y argumento V0+u con pyTMD (convención FES; V0 al inicio, f y u a mitad de la simulación), sin potencial de marea (dominio de 5 km). Interpolación comprobada con un campo falso (fase que cruza 0/360°, filas en tierra). Citar FES2022 con doi:10.24400/527896/A01-2024.004.

## 22. Conjunto de Saltelli (16 oct 2026)

- Acordado con Alex (16 oct) — 8 parámetros: carta (1879/1887), estado de dragado α (0–1), realización del error de carta (σ 0,9 m, L 150 m), datum (0 a +0,5 m), Cd (0,001–0,005, log-uniforme), viento ×0,8–1,2, dirección del viento ±15°, amplitud de marea ×0,9–1,1 (FES frente a TPXO cuando estén las dos). **Fuera por ahora: ríos y flotabilidad** (sin series de caudal públicas) → experimentos de mecanismo con caudales de la literatura.
- `scripts/conjunto.py`: `diseno N` (Saltelli 2002 con Sobol aleatorizado de scipy, semilla fija 20261016 → `datos/conjunto/diseno.csv`, N·(d+2) = 640 miembros con N = 64), `prueba` (autoprueba: Jansen sobre Ishigami recupera los índices exactos ±0,02), `generar J` (llama a `caso_real.py` por miembro con RUNDIR/CARTA/ALFA/SEMILLA/DATUM/CD/VFAC/VROT/MFAC → `runs/conjunto/mNNNN/`, ~0,6 s por miembro) y escribe `runs/conjunto/correr_array.sh` (array de Slurm, 4 núcleos de cálculo + 2 scribes por miembro, ≤ 682 a la vez = 4096 núcleos).
- `caso_real.py`: el viento se escala en `windfactor.gr3` y se gira en `windrot_geo2proj.gr3` (sin tocar los sflux); la marea se escala en `bctides.in`; el datum y Cd entran como variables. Salidas cada 6 h (SALIDA_H) para el conjunto. Comprobado en un caso generado: cada parámetro llega a su archivo.
- Ventana fija: 90 días desde el 1-ene-2016 (época seca, frentes fríos). La estación no es dimensión del conjunto; si hace falta, se compara una ventana de lluvias en los experimentos de mecanismo.
- Almacenamiento estimado: ~3 MB de entrada y ~0,4 GB de salida por miembro → ~250 GB para 640 en /globalscratch (72 TB libres). El posproceso por miembro (salidas a–f) se hará dentro del array para borrar luego los campos completos.
- Siguiente: prueba de 2 miembros de 90 días en Lemaitre4 (primer cálculo allí: coste real) con la M2 provisional; regenerar todo con FES2022 cuando llegue; posproceso.

**17 oct — primera corrida en Lemaitre4 y posproceso.**
- Prueba de 2 miembros (array 7965067, m0000–m0001, M2 provisional): arranca y avanza ~0,75 días de modelo por minuto con 4+2 núcleos (~2 h por miembro de 90 d, más rápido que NIC5). 25 días = 77 MB de salida.
- **AGE_1 ya es la edad en días** (comprobado en el código: `schism_step.F90` escribe α/C/86400; hay ntracer_age/2 salidas). Una primera suposición mía (AGE_1 = concentración, añadir AGE_2) era errónea y está deshecha; `posproceso.py` trata AGE_1 como edad.
- `scripts/zonas.py` + `docs/figuras/zonas.png`: canal (995 nodos), cuenca principal (954), Marimelena (494), Guasabacoa (967), Atarés (591). Límites trazados a mano y corregidos con Alex el 17-oct (orilla O de Guasabacoa y orilla S de Marimelena).
- `scripts/posproceso_malla.py` → `datos/conjunto/posproceso_malla.npz`: zona y área por nodo, pesos baricéntricos a la rejilla Sentinel-2 (252 × 238 celdas de 20 m) y a una sección del canal (33 puntos, 330 m). Autoprueba: reproduce un campo lineal y el área total.
- `scripts/posproceso.py` (solo numpy + netCDF4, corre en el cluster dentro del array): por zona y bahía, serie de la edad media, deriva de la edad en los últimos 10 d (¿estacionario?); edad media, p10/p50/p90 y fracción de volumen con edad > 30 d; mapas de superficie y fondo; caudal neto y bruto por el canal; superficie a las 16:00 UTC en la rejilla S2 (30 imágenes). Autoprueba con campos sintéticos (edad τ(1−e^(−t/τ)) con τ = 20 d, caudal conocido): ok. Si sale bien, el array borra los `.nc` (salvo m0000–m0001). Salidas cada 4 h para tener las 16 UTC.
- **Primer posproceso real (m0000 a los 31 días, en curso):** sin NaN; marea en la bahía 15,7 cm; **caudal bruto por el canal 69 m³/s** (prisma 4,91 km² × 0,30 m cada 12,42 h → 66 m³/s: coincide), neto 0,04 m³/s (sin ríos, ≈ 0). Edad media de los días 1–31 (aún en crecimiento): canal 3,7 d, cuenca 7,8, Marimelena 8,3, Guasabacoa 8,6, Atarés 9,5. vmax 2,99 m/s en todo el dominio (este miembro tiene Cd 0,0015: la esquina del borde crece con poca fricción) → el posproceso da también vmax dentro de la bahía.
- Pendiente: (e) partículas por foco.
- **m0000 y m0001 terminados (17 oct, 90 d, M2 provisional):** coste 9575 s y 14 206 s de pared con 4+2 núcleos (2,7 y 3,9 h; la diferencia es de nodo o de parámetros). Sin NaN. **Edad media de los días 60–90** (salida con la versión vieja del posproceso, campos "C_"): m0000 canal 15,0 d, cuenca 32,4, Marimelena 33,3, Guasabacoa 36,7, Atarés 41,0; m0001 15,1 / 29,9 / 30,5 / 33,1 / 36,4 d. Caudal bruto 74 y 64 m³/s; neto −1,6 y −2,0 m³/s (≈ 3 % del bruto: error de la sección, no un caudal real). **vmax 4,45 m/s** en el dominio: hay que ver si es la esquina del borde (posproceso nuevo da el nodo y la vmax dentro de la bahía).
- Un `device_commit_files` mío dejó en 16de927 una versión vieja de `posproceso.py`; corregido en 62b9c92.
- **Posproceso nuevo sobre m0000 / m0001:** edad media de la bahía (días 60–90) 31,3 / 28,1 d; fracción del volumen con edad > 30 d 0,76 / 0,55 (cuenca 0,90 / 0,40; Marimelena, Guasabacoa y Atarés ≈ 1; canal 0). **La edad no está en equilibrio a los 90 d: aún crece 0,43 / 0,35 d por día** (envejecimiento puro = 1 d/d). Hace falta o bien correr más (la ERA5 descargada llega a 2019) o extrapolar: el posproceso ajusta ahora dA/dt = (A∞ − A)/τ sobre las medias diarias de los últimos 45 d (autoprueba con A = 20(1 − e^(−t/20)): recupera A∞ y τ).
- vmax 4,45 m/s en el nodo 4790: **en el arco del borde abierto** (1180 m de fondo, a 4–8 km de las esquinas y ~5 km de la boca), no en la bahía. Dentro de la bahía vmax 1,52 / 0,92 m/s (por localizar: el posproceso da ahora el nodo). Corrección: la esponja de fricción pasa de las 2 esquinas a **todo el borde abierto** (< 1 km), sin efecto en la bahía (ya comprobado que el tratamiento del borde no llega a ella).
- **Curva de la edad (resumen.npz, medias diarias):** la edad media de la bahía crece casi lineal, ~0,4 d por día, con mesetas de 10–15 d (días ~15–25 y ~65–75; probablemente frentes fríos que renuevan). Día 90: bahía 37 / 33 d, Atarés 48 / 41 d, canal 18 / 19 d, todo aún creciendo. **La extrapolación de una sola escala no es fiable** (m0000: A∞ 79 d, τ 117 d; m0001: NaN o 883 d en algunas zonas) → no se usará; hacen falta corridas que lleguen al equilibrio.
- Lectura física provisional: con solo marea M2 de 0,15 m + viento y sin ríos ni gradientes de densidad (T y S uniformes), el intercambio es lento: la edad supera con creces los 23 d del control analítico. Encaja con que el control (prisma con factor de retorno) sobrestime la renovación, o con que falte la circulación por densidad. Es justo lo que deben separar los experimentos de mecanismo.
- vmax en la bahía 1,52 / 0,92 m/s en el nodo 4205 (E 361 040, N 2 560 803, 1,2 m de fondo): un nodo somero del borde del canal en la boca, expuesto al oleaje/viento. Puntual; vigilar.
- Siguiente: **una corrida larga (365 d) del miembro 0** con la esponja nueva para medir cuánto tarda la edad en estabilizarse (`CONJ_DIR=runs/largo CONJ_DIAS=365 python scripts/conjunto.py generar 1 0`; el tiempo de Slurm se ajusta a los días). De ahí sale la duración del conjunto.

**17 oct (tarde) — ríos y densidad preparados (para los experimentos de mecanismo).**
- Fuente pública de caudales: **JICA 2004** (Nihon Suido Consultants, informe final vol. IV, tabla 1.1, datos CIMAB de agosto de 2002): Luyanó 114 860, Martín Pérez 62 105, Tadeo 8 004 m³/d → **1,33 + 0,72 + 0,09 = 2,14 m³/s**. El informe dice que no hay aforos permanentes. Aguas residuales de la cuenca ~2,6–3 m³/s (2020), parte va a la bahía.
- **El mismo informe da "renovación del agua dulce ≈ 4 meses, con relativamente poco intercambio con el mar abierto"** y corrientes de densidad posiblemente fuertes en Atarés y Guasabacoa. Encaja con lo que da el modelo (edad que aún crece a los 90 d) y no con los 23 d del control analítico. También es la fuente del volumen de 47 hm³ y 9 m de profundidad media que las cartas no sostienen.
- `caso_real.py`: `RIOS=1` → fuentes en las desembocaduras (elemento de la bahía más cercano al cauce OSM, `osm_rios_habana.json`), caudal × QFAC, salinidad 0, T ambiente, agua de río = agua nueva para AGE (C = 1, α = 0); modelo baroclínico (ibc = 0) con T y S constantes en el borde (28 °C, 36) y sin flujo de calor (la densidad solo varía por salinidad). Probado con cauces sintéticos: elige el elemento correcto.
- `01_descargar.sh`: función `overpass` común; baja también los cauces OSM y el PDF de JICA (con fecha y sha256).
- Experimentos de mecanismo previstos (un miembro base, 1 año): (1) solo marea (NWS=0), (2) marea + viento, (3) marea + viento + ríos/densidad (RIOS=1).
- **Cauces OSM descargados (17-oct 22:43, overpass-api.de):** Luyanó, Martín Pérez y Arroyo Tadeo encontrados. Desembocaduras en la malla: **Luyanó** elemento 1040 (E 362 153, N 2 557 595; orilla O de Guasabacoa, a 38 m del cauce), **Martín Pérez** elemento 203 (E 363 089, N 2 556 683; cabecera de Guasabacoa, 10 m), **Tadeo** elemento 754 (E 363 949, N 2 558 581; orilla S de Marimelena, 62 m). Atarés no recibe ningún río de OSM (JICA menciona drenajes).
- **Repo organizado para el paper (17-oct):** `README.md` con mapa y cadena de procesado; `docs/articulo/` (puente con el manuscrito): `cifras.md` (cada número del borrador frente al valor actual y su fuente — hoy casi toda la sección 2 y la tabla 2 están desactualizadas; vertical S y no LSC²; borde con esponja y no Flather; costa OSM y no Sentinel-2) y `figuras.md` (9 figuras + 2 suplementarias, con script y estado). `runs/` entero fuera de git.

**19 oct — prueba con ríos y marea sin registro.**
- **Primera corrida con ríos y densidad (RIOS=1, 2 d, Lemaitre4): terminó bien** en 197 s (igual coste que sin ríos), posproceso ok.
- AVISO sigue sin mandar credenciales. **EOT20** (DGFI-TUM, Hart-Davis et al. 2021) es CC BY 4.0 y se baja **sin registro** desde SEANOE: cumple mejor la regla de datos públicos. `scripts/marea_eot20.py` (zip de ~2 GB; extrae 9 constituyentes, recorta la misma caja, mismo formato JSON). `caso_real.py`: `MAREA=fes | eot20 | m2`, por defecto el primero disponible. Propuesta: EOT20 como marea base y FES2022 (cuando llegue) como alternativa del conjunto, en lugar de TPXO (también requiere registro).
- **EOT20 extraído (20 oct):** amplitudes frente a La Habana M2 11,3–14,0 cm, S2 3,7–3,9, N2 2,5–2,8, K2 1,3–1,4, K1 7,7–8,3, O1 8,3–8,6, P1 2,2–2,5, Q1 1,9–2,2, M4 0,4–0,8 cm. Factor de forma (K1+O1)/(M2+S2) ≈ 1,0 → **marea mixta**, con diurnas casi tan grandes como semidiurnas (la M2 sola de 0,15 m del caso de prueba las ignoraba). pyTMD 3 renombró `arguments` → `pyTMD.constituents.arguments`; `caso_real.py` acepta las dos.
- AVISO aprobado (20 oct): FES2022 descargable con `scripts/marea_fes2022.py`.
- Corrida de 1 año (job 7965453): en cola por prioridad, arranque estimado 22-oct 08:17. Se deja en cola (reenviarla reinicia la antigüedad en la cola).
- **FES2022 completo (21 oct, 11 constituyentes por el FTP de AVISO; el THREDDS no resuelve en DNS).** Comparación con EOT20 frente a la boca (celda válida más cercana a 23,20 N 82,36 O): M2 12,19 / 12,55 cm (fase 45,2 / 46,4°), S2 3,94 / 3,84 (72 / 86°), N2 2,56 / 2,64, K1 8,26 / 8,03 (6,3 / 4,4°), O1 8,75 / 8,38 (1,7 / 4,7°), P1 2,59 / 2,30, Q1 2,09 / 2,13. **Diferencias < 0,4 cm en amplitud y de pocos grados en fase en las principales** (S2 14°, Q1 20°; M4 0,4 / 0,7 cm). Factor de forma 1,05 / 1,00 → marea mixta. La incertidumbre de la marea entre modelos es pequeña (≈ 3 % en M2): en el conjunto, el rango ×0,9–1,1 de amplitud la cubre de sobra.

**21 oct — repo público de datos y modelo (decidido con Alex).**
- Repo **nuevo y público** (GitHub) archivado en **Zenodo con DOI**; el repo de trabajo sigue privado. Licencias: **código MIT, datos propios CC BY 4.0**; terceros con la suya (OSM ODbL, GEBCO dominio público con cita, ERA5 licencia Copernicus con cita, EOT20 CC BY 4.0).
- Se arma con `bash scripts/preparar_publicacion.sh [destino]` (por defecto `build/publicacion/`), a partir de una lista explícita de lo redistribuible; mantiene la estructura de carpetas para que los scripts corran igual. Plantillas en `publicacion/` (README en inglés, DATA_SOURCES, LICENSE, LICENSE-DATA, CITATION.cff, .zenodo.json). Comprueba que no entre nada no redistribuible y escribe SHA256SUMS. Prueba: 88 MB, 428 archivos.
- **No se redistribuyen:** escaneos de las cartas (pesados; se bajan con script), PDF de prácticos y de JICA (con derechos; se citan), ERA5 bruto, **FES2022** (licencia AVISO por confirmar; EOT20 basta para reproducir), código de SCHISM.
- Faltan por añadir cuando existan: resúmenes del conjunto, índices de Sobol, experimentos de mecanismo y campos completos de 2 miembros (Zenodo).
- `docs/procedencia_datos.md` puesto al día (georreferencia WGS84 de la carta de 1889, prácticos y GEBCO descargados, FES por FTP, TPXO descartada).
- **Corrida de 1 año (21 oct):** arrancó el 21-oct a las 01:52 (antes de lo previsto). A las 15 h 24 min iba por el día 263: **~17 días simulados por hora** (≈ 5,3 h por 90 d, más lenta que los 2,7–3,9 h de las pruebas). Con el límite de 20 h pedido se cortará hacia el día ~340: suficiente para ver el equilibrio; el posproceso se corre a mano sobre los días escritos. `conjunto.py` pide ahora 6,5 h por cada 90 d + 2 h (365 d → 29 h; máx. 48 h).
- **Resumen de la corrida larga a los 291 d (M2 de prueba, viento, sin ríos):** edad media de la bahía **104 d** y aún crece 0,57 d/d; canal 54, cuenca 109, Marimelena 107, Guasabacoa 122, **Atarés 128 d**; 94 % del volumen con edad > 30 d. Superficie = fondo (sin densidad, mezcla vertical completa). Caudal bruto por el canal estable (69–77 m³/s/mes). Un "tiempo de caja" A/(1 − dA/dt) sube con el tiempo (33 d a los 60 d → 97 d a los 180 → 211 d a los 290): no hay una sola escala, se acumula agua muy vieja.
- **Interpretación:** con solo M2 de 0,15 m la marea entra y sale ~1,6 hm³ por ciclo, pero la excursión (~600 m) es menor que el canal (1530 m): el mismo agua va y vuelve y casi no se intercambia (factor de retorno ≈ 1). **La marea real es mixta**: K1 + O1 ≈ 17 cm con periodo de ~24 h dan una excursión diurna ~2–3 veces la de M2, que puede superar la longitud del canal → el caso de prueba **subestima mucho** el intercambio. Es la prueba de que la representación de la marea es crítica (y el control analítico, que usa periodo semidiurno, también subestima la excursión).
- vmax en la bahía 2,64 m/s en el nodo 4205 (somero, boca): vigilar.
- **Siguiente: experimentos de mecanismo con EOT20, 1 año** (`CONJ_DIR=runs/mecanismo CONJ_DIAS=365 python scripts/conjunto.py mecanismo`): m0000 solo marea, m0001 marea + viento, m0002 marea + viento + ríos y densidad; miembro central (carta 1887, α 0,5, sin campo aleatorio, datum 0,25 m, Cd 0,0025). Deciden la duración y la variable de salida del conjunto.
