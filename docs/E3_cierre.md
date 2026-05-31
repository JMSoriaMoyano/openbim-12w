# E3 — Cierre semana 3

> **Plantilla.** Rellenar al cerrar el sábado 30/05/2026.
> Esta es la "meta-evidencia" del entregable: qué se entregó, qué se aprendió
> y qué queda abierto. Sigue el mismo patrón que `docs/E2_cierre.md` (commit
> `8a17394`, tag `e2-closed`).

## Identidad del entregable

- **Semana:** 3
- **Sesiones cubiertas:** S3·L (25/05) + S3·X (recuperación 28-29/05) + S3·S (30/05)
- **Fecha de cierre:** 30/05/2026
- **Tag git:** `e3-closed`
- **Commit de cierre:** `75457fa`

## Qué se ha entregado

### Documentación nueva en `docs/`

| Fichero | Versión | Descripción |
|---|---|---|
| `S3L_ifc_jerarquia.md` | v0.1 | Bloque A: 3 jerarquías IFC + anatomía FZK-Haus |
| `S3L_ifc_relaciones.md` | v0.1 | Bloque B: 5+3 relaciones + caso muro #15042 |
| `S3L_ifc_glosario.md` | v1.0 | 40 términos en 8 secciones A–H |
| `S3X_dudas_resueltas.md` | v1.0 | 4 dictámenes NEXUM (D3-01, D3-02, D3B-01, D3B-02) |
| `E3_auditoria_fzk_haus.md` | v1.0 | Auditoría informacional completa del FZK-Haus |
| `E3_checklist.md` | v1.0 | Checklist binario de cierre |
| `E3_cierre.md` | v1.0 | Este meta-documento |

### Código nuevo en `scripts/`

| Fichero | Versión | Descripción |
|---|---|---|
| `s3l_ifc_inspect.py` | v0.3 | Inspector IFC con 6 funciones operativas (de 11 planeadas) |

### Infraestructura

| Item | Estado |
|---|---|
| `requirements.txt` consolidado | ✓ con 8 deps de IfcOpenShell + dev libs comentadas |
| `.venv/` operativo en Python 3.14 | ✓ |
| `.gitignore` actualizado | ✓ `_local/`, `.venv/`, `out/*.md` salvo `.gitkeep` y `E3_lab_run.md` |
| `out/` con `.gitkeep` | ✓ |
| `models/samples/_local/AC20-FZK-Haus.ifc` | ✓ SHA-256 verificado |

### Evidencia auto-generada commiteada

- `out/E3_lab_run.md` — informe del script ejecutado el sábado al inicio del trabajo

## Qué se ha aprendido

### Conclusiones técnicas

- **Las dos jerarquías ortogonales del IFC** (espacial: `IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace`; elementar: `IfcRoot → IfcObjectDefinition → IfcProduct → IfcElement → IfcBuildingElement → ...`) son el armazón sobre el que se monta cualquier lectura de modelo. Sin esa estructura mental, los conteos por clase no significan nada; con ella, cualquier conteo se traduce en una pregunta operativa concreta (¿cuántas particiones tiene cada planta?, ¿qué elementos faltan en este storey?).

- **El binomio `Pset_*Common` + `Qto_*BaseQuantities`** es el contrato OpenBIM mínimo entre herramientas; los Psets vendor-specific (`ArchiCAD*`, `AC_*`, `Revit*`) son ruido informacional no transferible. Auditar contra el binomio mínimo es eficiente; auditar contra el vendor es ilusión de rigor.

- **La validación dual de boundaries de 2º nivel** (subtipo formal `IfcRelSpaceBoundary2ndLevel` OR clase base con `Name='2ndLevel'` + `Description='2a'`) es necesaria para que el baseline NEXUM sea inclusivo con el parque ArchiCAD ≤20 sin perder rigor (D3B-02). Esta dualidad es trasladable a otros pares OpenBIM/vendor: identificar la equivalencia semántica detrás del literal es trabajo de auditor maduro.

- **IfcOpenShell 0.8.5 sobre Python 3.14** soporta la totalidad del análisis informacional sin necesidad de tocar Blender ni Bonsai. La extensión visual queda como herramienta complementaria, no como dependencia. Esto es importante porque permite CI/CD headless de auditoría sobre cualquier modelo, sin entorno gráfico.

- **El exportador determina la salida tanto o más que el modelador**. El hallazgo sistémico de S6 (0/40 conformidad Pset en FZK-Haus por uso del add-on IFC2x3 de ArchiCAD 20) reformula la auditoría: ya no basta con preguntar "¿quién modeló esto?", hay que preguntar también "¿con qué herramienta y qué versión de exportador se serializó?". El tooling es información contractual.

### Conclusiones de proceso

- **Las sesiones recuperadas en diferido funcionan** cuando el repo lleva trazabilidad clara. S3·X se recuperó jueves+viernes (28-29/05) sobre tres bloques bien delimitados (A inspector, B dudas, C plantillas E3); el cierre el sábado/domingo no acusó la deuda. El patrón se valida para futuras recuperaciones.

- **El cron de briefing matinal L/X/S 07:00 CEST** es soporte cognitivo eficaz para no perder el hilo entre sesiones espaciadas. Especialmente útil tras semanas con sesiones en diferido o festivos intercalados. Mantener el cron activo hasta cierre del plan (sábado 01/08).

## Qué queda abierto (deuda técnica)

### Dudas diferidas (heredadas de S3·L/S3·X)

| ID | Tema | Sesión receptora |
|---|---|---|
| D3-03 | Export IfcSpace desde Revit | S4·L |
| D3-04 | IfcZone en Living/PBSA | S4·L |
| D3-05 | IfcGrid mandatory en plantilla | S5·L |
| D3B-04 | Validación IDS de URIs bSDD | S7·L |
| D3B-05 | Export IfcRelConnectsPathElements desde Revit | S6·L |

### Funciones del script pendientes (4)

| Función | Sesión planeada | Bloque |
|---|---|---|
| `list_elements_per_storey` | S4·L | Lectura básica |
| `count_relationships` | S4·L | Inventario |
| `validate_doors_have_openings` | S6·L | Calidad |
| `validate_unique_project` | S6·L | Calidad |

### Trabajo de NEXUM relacionado

- Plantilla `Pset_NEXUM_AssetMeta` con campos: `AssetCode`, `OperatorRequirement`,
  `LeasingCategory`. Pendiente de definir en S4·L.
- IDS NEXUM v1.0 que codifique las 5 tablas de Psets mínimos (S7·L).
- Decisión sobre umbral de no-conformidad (¿100% o se permite cierto %?). S6·L.

## Resumen de commits de la semana

<!-- TODO: rellenar con `git log --oneline e2-closed..e3-closed` -->

75457fa E3 cierre: auditoria FZK-Haus completada · script v0.3 + lab_run + cierre + checklist
2297fc2 S3X Bloque C: inspector v0.3 (check_minimum_psets + explain_entity) + plantillas E3 (auditoria FZK-Haus + checklist binario + cierre) listas para sabado 30/05
a3f35b1 S3X Bloque B: 4 dudas tecnicas resueltas (D3-01 IfcWall vs StandardCase · D3B-02 SpaceBoundary 1st/2nd · D3-02 IFC4 vs IFC4.3 · D3B-01 Psets minimos NEXUM) con evidencia FZK-Haus verificada
5acc7f4 S3X: inspector IFC v0.2 operativo (open_ifc + report_header + walk_spatial_pyramid + count_physical_elements) · requirements.txt consolidado · out/ con .gitkeep · .gitignore actualizado para venv y out/*.md
2446ba0 S3L: docs IFC (jerarquia + relaciones + glosario) + script inspect Nivel 2
b84c941 S3L: infra models/samples (Opcion B) + .gitignore para _local + SOURCES.md (AC20-FZK-Haus IFC4)

## Métricas

| Métrica | Valor |
|---|---|
| Sesiones realizadas | 3 (S3·L, S3·X, S3·S) |
| Sesiones en diferido | 1 (S3·X) |
| Documentos nuevos | 7 |
| Scripts nuevos / actualizados | 1 (v0.1 → v0.3) |
| Líneas de Python operativas | ~750 |
| Líneas de documentación | ~1500 |
| Dudas resueltas | 4 |
| Dudas diferidas | 5 |
| Commits | 6 |
| Tag de cierre | `e3-closed` |

## Próximo: semana 4

- **S4·L lunes 01/06 07:00 CEST** · cron `6ffa9c6f` enviará briefing
- **Tema:** IfcOpenShell — lectura y consultas (Bloque profundo)
- **Pre-requisito:** Bonsai/Blender (extensión de S3·X, planeada para
  después de E3 pero antes de S4·L si hay tiempo el sábado tarde).
