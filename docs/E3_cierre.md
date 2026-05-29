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
- **Commit de cierre:** _(rellenar con SHA tras push)_

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

<!-- TODO: rellena con 3-5 conclusiones técnicas y 1-2 conclusiones de proceso.

  Sugerencias técnicas:
  - El schema IFC4 distingue jerarquía espacial (Project→Site→Building→Storey→Space)
    de jerarquía elementar (BuildingElement →…). Son ortogonales.
  - Los Psets del fabricante son ruido; solo los Pset_*Common del estándar son
    transferibles entre herramientas.
  - Las boundaries 2nd level en IFC4 vienen en dos sabores: subtipo formal
    (IfcRelSpaceBoundary2ndLevel) o convención por Name/Description (clase base
    con metadatos). La validación robusta usa ambos.
  - IfcOpenShell 0.8.x permite todo el análisis sin tocar Blender.

  Sugerencias de proceso:
  - Sesiones en diferido (S3·X recuperada en jueves+viernes) funcionan bien
    cuando hay buen registro en el repo.
  - El cron automático del briefing matinal es útil para no perder el hilo.
-->

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

```
<insertar salida del git log aquí>
```

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
| Commits | _(rellenar)_ |
| Tag de cierre | `e3-closed` |

## Próximo: semana 4

- **S4·L lunes 01/06 07:00 CEST** · cron `6ffa9c6f` enviará briefing
- **Tema:** IfcOpenShell — lectura y consultas (Bloque profundo)
- **Pre-requisito:** Bonsai/Blender (extensión de S3·X, planeada para
  después de E3 pero antes de S4·L si hay tiempo el sábado tarde).
