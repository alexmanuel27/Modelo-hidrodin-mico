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
