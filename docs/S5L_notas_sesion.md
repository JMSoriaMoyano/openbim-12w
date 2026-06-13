# S5·L · Notas de sesión

**Fecha planificada:** Lunes 08/06/2026
**Fecha real ejecución:** Lunes 08/06/2026 (en plazo)
**Sesión:** S5·L · IfcOpenShell: geometría y autoría
**Tema:** Primer ciclo de autoría real sobre IFC + congelación EIR v0.1 + reglas vinculantes
**Duración estimada:** ~3.5 h (5 bloques: A, B, C, D, E)
**Versión documento:** 1.0
**Estado E5:** Cerrado el 13/06/2026 (S5·S) con tag `e5-closed` · ver `docs/E5_autoria_fzk_haus.md` v1.0

---

## 1. Objetivos cumplidos

- [x] Congelar EIR NEXUM PBSA v0.1 (Obligatorias) como contrato inmutable y registrar `DF-01` como deuda formativa estructural multi-variante (diseño / contratista / as-built).
- [x] Implementar lectura de geometría IFC (bounding box, conteos por tipo, plan view PNG) sobre `s5l_ifc_geom_read.py`, generando dos evidencias versionadas (`_baseline.json` + `_baseline.png`).
- [x] Establecer el documento `docs/S5L_reglas_autoria.md` v1.0 como contrato vinculante para toda autoría posterior (5 principios + whitelist explícita v0.1).
- [x] Ejecutar el primer ciclo de autoría real sobre AC20-FZK-Haus.ifc con 4 operaciones trazadas (3 propiedad + 1 geometría), produciendo IFC mutado + diff JSON.
- [x] Re-auditar el IFC autoriado, demostrar mejora cuantificable (`H3.DOOR.FireRating fail→pass`, +6.67 pp globales) y verificar cero retrocesos (P4).
- [x] Identificar deuda nueva DT-S5L-01 (schema declarado IFC4 vs cabecera STEP que sugería IFC2X3) para revisión en S5·X.

---

## 2. Bloques ejecutados

### 2.1 Bloque A · Housekeeping y congelación EIR v0.1 (commit `2b22d0f`)

- **Nuevo fichero:** `requirements.txt` con `ifcopenshell>=0.7`, `pyyaml>=6.0`, `matplotlib>=3.7`.
- **Congelación:** `eir/PBSA_v0.1_obligatorias.yaml` añade en `meta` los campos `frozen_at: 2026-06-08`, `variant: obligatorias_v0.1_comun`, `pending_refactors: [DF-01]`.
- **DF-01 registrada** en YAML como refactor estructural multi-variante a ejecutar en S5·X:
  ```
  eir/PBSA_v0.x_comun.yaml      # base
  eir/PBSA_v0.x_diseno.yaml     # extiende común + 5D (QTO, coste)
  eir/PBSA_v0.x_contratista.yaml # extiende común + 4D (planificación)
  eir/PBSA_v0.x_asbuilt.yaml    # extiende común + LOIN-FM operador
  ```
- **Justificación DF-01:** existe un EIR por cada BEP contractual. El EIR de diseño exige control de coste (interpretación industria estándar: 5D=cost/QTO); el EIR del contratista principal exige planificación (4D=time). El YAML actual mezcla ambos sin distinción.

### 2.2 Bloque B · Lectura de geometría (commit `c507e51`)

- **Nuevo módulo:** `scripts/s5l_ifc_geom_read.py` (381 líneas, 3 funciones G1/G2/G3 + CLI).
  - `G1 get_geometry_summary(model)` — conteo elementos con geometría procesable, bounding box global.
  - `G2 stats_by_type(model)` — agregación por IfcClass: count, triángulos promedio, bbox por tipo.
  - `G3 render_plan_view(model, out_png)` — proyección XY con matplotlib, colores por categoría.
- **Notebook explorador:** `notebooks/S5L_geom_explorer.py` (py-percent, 222 líneas, 6 celdas).
- **Outputs versionados:**
  - `out/s5l_geom_stats_baseline.json` (37.7 KB) — 90/127 IfcProduct procesables, bbox 18×16×7.3 m, schema IFC4.
  - `out/s5l_geom_planview_baseline.png` (300.4 KB) — solar cian, slab verde, walls azul, stairs naranja (helicoidal visible), spaces magenta. Validación visual correcta.
- **Hallazgos clave:** IfcRailing es el tipo más teselado (~3888 tri/unidad), IfcMember el más numeroso (42 unidades simples), escalera helicoidal 2614 tri.
- **DT-S5L-01 (deuda técnica nueva):** el schema reportado es **IFC4** pero la cabecera STEP sugería IFC2X3. A verificar en S5·X.

### 2.3 Bloque C · Reglas de autoría v1.0 (commit `c102bfb`)

- **Nuevo documento vinculante:** `docs/S5L_reglas_autoria.md` (193 líneas, 7 secciones).
- **5 principios rectores:**
  - **P1** No mutar el modelo original. Toda escritura va a `out/<base>_authored.ifc`.
  - **P2** Trazabilidad obligatoria vía `out/<base>_authored_diff.json`.
  - **P3** Una operación = una función con docstring que cite §EIR aplicable.
  - **P4** Validación post-autoría obligatoria. Cero retrocesos.
  - **P5** Whitelist explícita §3. Cualquier ampliación requiere actualizar este documento.
- **Whitelist v0.1:** 6 ops de propiedad (IfcDoor/Window/Wall/Slab/Space/BuildingStorey con Psets comunes) + 2 ops de geometría (crear IfcWall y IfcOpeningElement asociado).
- **Prohibidas:** borrar elementos, modificar geometría existente, alterar IfcRelAggregates/IfcRelContainedInSpatialStructure existentes, mutar cabecera STEP, reasignar GlobalIds.
- **Nomenclatura canónica:** `_authored.ifc`, `_authored_diff.json`, `_compliance_matrix_post.json`.
- **.gitignore extendido:** `!*_authored.ifc` permite versionar evidencia de autoría.

### 2.4 Bloque D · Autoría real (commit `18849c9`)

- **Nuevo módulo:** `scripts/s5l_ifc_authoring.py` (631 líneas, 4 funciones + CLI orchestrator).
  - `_load_source_copy(path)` — carga IFC fuente garantizando P1 (no mutación del fichero en disco).
  - `set_pset_property(model, element, pset, prop, value, diff, eir_ref, rationale)` — whitelist §3.1. Solo pobla ausentes; no sobrescribe valores válidos.
  - `create_basic_wall(model, name, length, width, height, location, container, diff, eir_ref, rationale)` — whitelist §3.2. IfcWall + IfcExtrudedAreaSolid + IfcRectangleProfileDef + IfcLocalPlacement encadenado al storey.
  - `write_authored_model(model, target_path, diff, diff_path)` — escritura atómica IFC + diff JSON, con verificación final de no-coincidencia target ≠ source (refuerzo P1).
- **Decisiones de diseño confirmadas:**
  - **Q1 = A** → 3 puertas sin FireRating detectadas automáticamente → `"EI 30"` uniforme (CTE DB-SI residencial).
  - **Q2 = A** → IfcWall 3.0 × 0.2 × 2.7 m en (10.0, 5.0, 0.0), eje X, contenedor `Erdgeschoss` (planta baja FZK-Haus, #479).
- **Outputs generados:**
  - `out/AC20-FZK-Haus_authored.ifc` (2.69 MB) — re-cargable con `ifcopenshell.open()` sin errores. IfcWall: 13→14. IfcDoor con FireRating="EI 30": 3.
  - `out/AC20-FZK-Haus_authored_diff.json` (3.07 KB) — 4 operaciones, formato §4.1 conforme (op_id, type, element, pset/geometry, value_before/after, eir_ref, rationale, summary agregado).
- **Operaciones trazadas:**

  | op_id | type | elemento | Pset/Geom | value_before | value_after |
  |---|---|---|---|---|---|
  | OP-001 | set_pset_property | IfcDoor #17468 Innentuer-1 | Pset_DoorCommon.FireRating | null | "EI 30" |
  | OP-002 | set_pset_property | IfcDoor #19199 Innentuer-2 | Pset_DoorCommon.FireRating | null | "EI 30" |
  | OP-003 | set_pset_property | IfcDoor #19504 Innentuer-3 | Pset_DoorCommon.FireRating | null | "EI 30" |
  | OP-004 | create_element | IfcWall #79112 S5L-AUTH-WALL-001 | IfcExtrudedAreaSolid + IfcRectangleProfileDef | walls=13 | walls=14 |

### 2.5 Bloque E · Cierre + re-auditoría (este commit)

- **Re-auditoría:** `python scripts/s4s_audit_eir.py --ifc out/AC20-FZK-Haus_authored.ifc --eir eir/PBSA_v0.1_obligatorias.yaml --out out/AC20-FZK-Haus_compliance_matrix_post.json`.
- **Nuevo artefacto:** `out/AC20-FZK-Haus_compliance_matrix_post.json` (16.3 KB).
- **Comparativa baseline vs post:**

  | KPI | Baseline | Post | Δ |
  |---|---|---|---|
  | % Pass global | 20.0% | 26.67% | **+6.67 pp** |
  | Counts: pass | 3 | 4 | +1 |
  | Counts: fail | 12 | 11 | -1 |
  | `H3.DOOR.FireRating` | fail (40% · 2/5) | **pass (100% · 5/5)** | +60 pp |

- **P4 verificada:** cero retrocesos en los 15 chequeos. Ninguna regresión status-a-status ni numérica.
- **Notas de sesión:** este documento.

---

## 3. Hallazgos y aprendizajes

### 3.1 Técnicos

1. **`ifcopenshell.api.run()` como dispatcher canónico.** En la versión 0.8.5 conviven varias formas de mutar el modelo (`api.pset.add_pset`, `api.run("pset.add_pset", ...)`). El dispatcher por string es la forma estable cross-versión y la que se ha adoptado en `set_pset_property` y `create_basic_wall`.
2. **Geometría mínima válida para un IfcWall requiere 5 entidades nuevas mínimo:** `IfcRectangleProfileDef` + `IfcAxis2Placement2D` + `IfcExtrudedAreaSolid` + `IfcAxis2Placement3D` + `IfcLocalPlacement`, todas encadenadas al storey contenedor vía `ObjectPlacement.PlacementRelTo`. Más `IfcShapeRepresentation` + `IfcProductDefinitionShape` para asociar el sólido al producto. Total: 7 entidades por muro nuevo.
3. **`ifcopenshell.api.spatial.assign_container`** es la forma correcta de asignar un producto a un IfcBuildingStorey (no `IfcRelContainedInSpatialStructure` manual). Crea o reutiliza la relación según corresponda.
4. **Auto-detección Q1=A funcionó limpiamente:** `_find_doors_without_fire_rating` localizó exactamente 3 puertas (Innentuer-1, -2, -3), confirmando la auditoría E4 (40% = 2/5 puertas con valor, 3/5 sin valor).
5. **Determinismo (P2 reproducibilidad §4.3):** la ejecución generó GlobalId `3sSuArjhP1VAHDFwRlK_Hf` para el muro nuevo. Re-ejecuciones generarán GlobalIds distintos (no fijamos semilla en v0.1). A formalizar en S6·L si se necesita reproducibilidad byte-a-byte.

### 3.2 Proceso

6. **El patrón "1 bloque = 1 commit + 1 confirmación de push" sigue funcionando** y permite recuperar el estado exacto si una sesión se interrumpe. Cinco bloques (A-E) → cinco commits limpios.
7. **Confirmar 2-3 decisiones antes de redactar un script grande** (Q1, Q2 en este bloque) evita reescritura. Pregunta del usuario sobre qué era CLI fue oportuna y evitó asumir contexto.
8. **`%%` para escapar `%` literales en `git commit -m "..."` en Windows CMD** sigue siendo necesario (pitfall registrado en S4·X, validado en S5·L).

### 3.3 Deuda formativa / técnica abierta

- **DF-01** (registrada en `meta.pending_refactors` del YAML, sin commit propio) — refactor EIR a estructura multi-variante (común / diseño / contratista / as-built). Target: S5·X.
- **DT-S5L-01** (Bloque B) — discrepancia schema declarado IFC4 vs cabecera STEP que sugería IFC2X3 en FZK-Haus. Target: S5·X.
- **Whitelist §3.3 ampliaciones futuras** — edición de geometría existente, borrado controlado, edición de relaciones espaciales, Psets personalizados. Targets: S5·X / S6·L / S7·L.

---

## 4. Artefactos producidos en S5·L

| Tipo | Ruta | Tamaño | Bloque |
|---|---|---|---|
| Config | `requirements.txt` | 76 B | A |
| YAML | `eir/PBSA_v0.1_obligatorias.yaml` (updated) | — | A |
| Code | `scripts/s5l_ifc_geom_read.py` | 12.7 KB | B |
| Notebook | `notebooks/S5L_geom_explorer.py` | 7.4 KB | B |
| Evidencia | `out/s5l_geom_stats_baseline.json` | 37.7 KB | B |
| Evidencia | `out/s5l_geom_planview_baseline.png` | 300.4 KB | B |
| Config | `.gitignore` (extended) | — | B |
| Doc | `docs/S5L_reglas_autoria.md` | 193 líneas | C |
| Code | `scripts/s5l_ifc_authoring.py` | 22.2 KB / 631 líneas | D |
| Evidencia | `out/AC20-FZK-Haus_authored.ifc` | 2.69 MB | D |
| Evidencia | `out/AC20-FZK-Haus_authored_diff.json` | 3.07 KB | D |
| Evidencia | `out/AC20-FZK-Haus_compliance_matrix_post.json` | 16.3 KB | E |
| Doc | `docs/S5L_notas_sesion.md` | este fichero | E |

---

## 5. Trazabilidad commit-a-evidencia

| Commit | Bloque | Evidencias producidas |
|---|---|---|
| `2b22d0f` | A | requirements.txt, YAML congelado v0.1 + DF-01 |
| `c507e51` | B | s5l_ifc_geom_read.py, stats + planview baseline, .gitignore |
| `c102bfb` | C | S5L_reglas_autoria.md v1.0 |
| `18849c9` | D | s5l_ifc_authoring.py, IFC + diff autoriados |
| (este) | E | compliance_matrix_post.json, S5L_notas_sesion.md |

---

## 6. Estado de avance hacia E5 (cierre 13/06)

Criterios de aceptación E5 según `S5L_reglas_autoria.md §6` (estado final tras S5·S):

| # | Criterio | Estado final |
|---|---|---|
| 1 | `scripts/s5l_ifc_authoring.py` con ≥2 funciones autorizadas | ✅ 4 funciones (1 propiedad + 1 geometría + 2 utilitarias) |
| 2 | `out/AC20-FZK-Haus_authored.ifc` válido (re-cargable) | ✅ verificado |
| 3 | `out/AC20-FZK-Haus_authored_diff.json` con todas las operaciones trazadas | ✅ 4 ops, formato §4.1 |
| 4 | `out/AC20-FZK-Haus_compliance_matrix_post.json` con ≥1 chequeo mejorado | ✅ `H3.DOOR.FireRating fail→pass` |
| 5 | `docs/E5_autoria_fzk_haus.md` describiendo operaciones e impacto | ✅ v1.0 firmada el 13/06 (S5·S) |
| 6 | Cero retrocesos vs baseline | ✅ verificado (en las 4 variantes EIR v0.2) |
| 7 | Tag `e5-closed` sobre commit final | ✅ creado el 13/06 (S5·S) |

**7/7 criterios verdes.** E5 cerrado formalmente el sábado 13/06/2026 con el documento `docs/E5_autoria_fzk_haus.md` v1.0 y el tag `e5-closed`. El refactor DF-01 (EIR multi-variant) cerró en S5·X como criterio bonus.

---

## 7. Próxima sesión · S5·X (Miércoles 10/06/2026)

Plan tentativo:

1. **Refactor DF-01** — descomponer `eir/PBSA_v0.1_obligatorias.yaml` en estructura multi-variante (común / diseño / contratista / as-built). Renombrar a `v0.2_*` y archivar v0.1 en `eir/_archive/`.
2. **DT-S5L-01** — investigar discrepancia schema FZK-Haus (IFC4 vs IFC2X3). Decidir si afecta a auditoría o solo a documentación.
3. **Bloque profundización geometría** — explorar autoría avanzada según whitelist §3.3 (candidatos: edición de geometría existente, crear IfcOpeningElement asociado al muro nuevo de S5·L).
4. **Iniciar `docs/E5_autoria_fzk_haus.md`** — primer borrador para cerrar el último criterio E5.

---

**Fin de S5L_notas_sesion.md v1.0.**
