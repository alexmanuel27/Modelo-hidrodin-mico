> Copia de `claude/revision_repo_tecnico_2026-11-08.md` del Project de Claude (revisión del chat del artículo y respuesta
> del chat técnico), archivada en el repo el 8-nov-2026 antes de borrar el Project.

# Revisión del repo técnico (8-nov-2026, chat del artículo)

Repo `repos/Modelo-hidrodin-mico`, HEAD 0650823 (111 commits; 10 sin push: origin en e586d68). Árbol limpio.

## Comprobado y bien
- Autopruebas que corren con numpy (VM del Mac): `utm.py`, `posproceso.py --prueba`, `analisis_conjunto.py --prueba`, `diag_caudal.py --prueba`, `comparacion_s2.py --prueba` → ok. `prisma_marea.py` reproduce `resultados/prisma_marea.csv` byte a byte. No corridas (necesitan scipy): `conjunto.py prueba`, `posproceso_malla.py --prueba`.
- Estimadores de Saltelli/Jansen correctos (S1 y ST); diseño 704 = 64 × 11, qfac 0,25–2.
- La media vertical de la edad (`E.mean(2)`) es válida: niveles S con theta_f = 1e-4 (casi uniformes).
- Sin secretos en archivos ni en el historial (solo el marcador PEGA-AQUI-TU-TOKEN).
- FES2022 se versiona en el repo privado pero `preparar_publicacion.sh` lo excluye del público.

## Problemas, por gravedad
1. **Protocolo de métricas no congelado formalmente.** `docs/protocolo_metricas_conjunto.md` sigue diciendo "BORRADOR, para que Alex lo apruebe" y el registro de cambios está vacío. El commit 4dff6a7 dice "protocolo congelado" pero no toca el archivo. Los resúmenes del conjunto ya están en el Mac (488 el 5-nov). Acción: marcar congelado citando 4564b7e (26-oct) y anotar en el registro cuándo se bajaron resultados.
2. **Desviación del protocolo: fracción de volumen > 7 y > 14 d por zona no existe.** `posproceso.py` solo calcula > 30 d, y los campos completos se borran (salvo m0000–m0002) → no recuperable. Registrar como desviación; usar en su lugar P(edad media de la zona > 7/14/30 d) entre miembros y los mapas de superficie, que sí existen.
3. **Definición de la edad: el agua de los ríos cuenta como agua nueva.** La edad de ~7 d mezcla intercambio con el mar y entrada de agua dulce. No es la misma magnitud que la "renovación del agua dulce ≈ 4 meses" de JICA. Hipótesis por comprobar (JICA p. R-7): los 4 meses podrían ser V/Q (sin intercambio). Para el artículo: decirlo explícitamente y, si se puede, una edad solo respecto al mar o el tiempo de renovación del agua dulce en los miembros con campos.
4. **Flujo de calor pendiente (robustez m0005, SST OISST).** Con calor y borde a 28 °C la edad pasó de 6,6 a 16,8 d sin equilibrio. Todo el conjunto es condicional a "densidad solo por salinidad". Es el resultado pendiente que más puede cambiar el mensaje.
5. **Caudal por el canal** no usable (ya documentado).

## Menores
- `publicacion/README.md` dice 640 miembros (son 704). `preparar_publicacion.sh` no incluye `datos/sentinel2/` (hace falta para reproducir la comparación S2) ni los resúmenes de mecanismo y robustez.
- `cifras.md` dice "central = mediana", pero el volumen 30,4 hm³ es el caso central; la mediana es 30,7.
- `correr_array.sh` marca HECHO aunque el posproceso falle (queda como "posproceso=no" en `coste.txt`): revisar ese recuento antes de cerrar el conjunto.

## Vistazo a los resúmenes del conjunto (hecho en esta revisión, declararlo)
488/704 en el Mac, 0 con NaN, todos de 120 d. Edad media de la bahía: mediana 7,7 d (P5–P95 5,6–10,8; máx. 12,7). 8,8 % con |deriva| > 0,05 d/d (umbral del protocolo: 10 %). No se calcularon Sobol ni conclusiones.

---

## Respuesta del chat técnico (8-nov-2026, commit 8f3bf73)

| Punto | Estado | Qué se hizo |
|---|---|---|
| 1 Protocolo | **corregido** | Cabecera "CONGELADO el 27-oct, aprobado por Alex, texto de 4564b7e". El registro anota el commit 4dff6a7 sin el archivo, la copia de 488 resúmenes el 5-nov y este vistazo del 8-nov. Una cabecera del 27-oct ya se había escrito, pero fuera del repo, y nunca se commiteó. |
| 2 Fracción > 7/14 d | **registrado como desviación** | Fracción de volumen solo para > 30 d. Para 7 y 14 d: P(edad de la bahía > umbral) entre miembros y mapas de probabilidad en superficie. `secciones/05_metodos.md` lo dice. |
| 3 Edad ≠ retención del agua dulce | **corregido en los docs + script nuevo** | JICA (resumen ejecutivo, p. R-7) dice literalmente "tiempo de retención del agua dulce ≈ 4 meses", sin método. Con sus 47 hm³, V/Q = 4 meses pide Q ≈ 4,5 m³/s (hipótesis sin confirmar). `msource.th` confirma ríos con AGE = 1. Nuevo `scripts/renovacion_dulce.py` (T_f = V_f/Q, fracción de agua dulce; autoprueba ok). Cota ya: agua dulce en superficie 2,3–2,5 % → T_f ≲ 4 d. Falta correrlo en el cluster en los miembros con campos. Registrado en el protocolo como aclaración: C6 compara magnitudes distintas. |
| 4 Calor | pendiente | m0005 sigue en el cluster. |
| 5 Caudal | ya documentado | Prueba de 10 min en marcha (`cluster/hf_caudal.sh`). |
| publicación | **corregido** | 704 miembros; incluye SST OISST, `datos/sentinel2/` (rejilla, README, escenas, focos), protocolos, procedencia y resúmenes de mecanismo y robustez; DATA_SOURCES con OISST y Sentinel-2. Probado: el script arma el repo público (107 MB, 467 archivos). |
| mediana del prisma | **corregido** | Columna = mediana (p50): volumen 30,7 hm³, renovación sin retorno 11,6 d. Aviso de no mezclar con el caso central (30,4) que tiene main.tex. |
| HECHO sin posproceso | **mitigado** | `diagnostico_conjunto.sh` lista los terminados sin `resumen.json`; esos conservan los campos (`rm` solo si el posproceso sale bien), así que se puede repetir el posproceso. |

Queda abierto: los hashes de los commits de congelación (4564b7e, 773b9fb) son del repo **privado**. Si el público se crea con `git init` nuevo, no se podrán verificar. Opciones: publicar también el historial, o depositar los protocolos con fecha en Zenodo.

Después (8-nov): T_f calculado en el cluster: 1,8–2,0 d (4,2 d con calor y borde a 28 °C), commit fcd886a.
