> Copia de `claude/estado_y_plan.md` del Project de Claude "modelo-hidrodinamico" (estado del chat del artículo, versión
> del 8-nov-2026), archivada en el repo el 8-nov-2026 antes de borrar el Project. Desde entonces el chat del artículo
> guarda su estado en el repo del artículo y en la nota del vault.

Estado del ARTÍCULO (actualizado 8-nov-2026). Lo técnico vive en el repo de trabajo:
repos/Modelo-hidrodin-mico → docs/articulo/README.md (punto de entrada), cifras.md (fuente de verdad de cada número), figuras.md, secciones/; resúmenes técnicos en este Project (claude/*).

Repos
- Artículo: repos/publication plan/modelo-hidrodin-mico (solo articulo/). Este chat del Project = el paper.
- Trabajo: repos/Modelo-hidrodin-mico (Cowork técnico aparte).

ENFOQUE
- Pregunta: ¿qué partes de la bahía no se renuevan, y esa conclusión sobrevive a no tener datos? Conclusiones robustas vs frágiles.
- Solo datos públicos replicables. Conjunto de 704 miembros (Saltelli, 9 parámetros, 120 d, EOT20, ríos y densidad por salinidad en todos), mecanismo (3 corridas de 1 año) y robustez (5 + calor con SST OISST).

PLANTILLA Y NORMAS (Environmental Modelling & Software)
- elsarticle oficial, preprint 12pt, autor-año. Resumen ≤ 150 palabras; 1–7 palabras clave; 3–5 highlights ≤ 85 car. (archivo aparte); resumen gráfico; datos en repositorio y citados; CRediT, conflicto de intereses, financiación, declaración de IA generativa.

MANUSCRITO (8-nov-2026, 22 páginas, compila limpio, sin commit)
- Escrito y al día con cifras.md (commit 1e32fcf): intro (JICA = "freshwater retention time ≈ 4 months", sin método), sec. 2 (marea mixta con FES/EOT20; ríos y desembocaduras; Atarés sin río OSM), sec. 3 (tabla 1 con EOT20, FES solo comparación, OISST, Sentinel-2 2017–2025), sec. 4 (prisma con medianas: 24 d; excursión 0,41 del canal, ≤ 0,63 en el 95 %; figura nueva en inglés copiada), sec. 5 completa (densidad por salinidad en todos; edad con el agua de los ríos como nueva + T_f = V_f/Q; métricas y equilibrio; protocolos 21-oct y 27-oct y la desviación de 7/14 d; tabla de 9 parámetros; tabla de conclusiones C1–C8; mecanismo; robustez; cómputo 4+3 núcleos y tramos de 20 d; evaluación con el protocolo S2), 6.4 (tablas de mecanismo y robustez; calor 28 °C en azul, OISST pendiente), 6.6 (S2: ρ 0,45, p 0,16 → no distinguible del azar), 7.2 (el control mareal se equivoca en los dos sentidos), 7.3 nueva sobre JICA (T_f 1,8–2,0 d, ~60 veces menos; hipótesis V/Q con 4,5 m³/s, sin confirmar), limitaciones y transferibilidad.
- El caudal por el canal no se usa como resultado.
- Pendiente (espera al conjunto y a la corrida de calor con OISST): resumen y highlights (solo se corrigieron recuentos), 6.1–6.3, 6.5 (destino de los ríos, sin decidir), 7.1, 7.4, conclusiones; figuras 1–3, 5–9 en inglés; refs TODO (modelado con pocos datos, incertidumbre, contaminación de la bahía, estudio S2 propio, método de la fracción de agua dulce, DOI GEBCO, artículo FES2022); horas-núcleo; URL/DOI del repo; coautores; financiación.
- Bib: 21 entradas, todas citadas; verificadas en OpenAlex salvo Deleersnijder 2001 (no indexada; confirmada por búsqueda) y documentos grises.
