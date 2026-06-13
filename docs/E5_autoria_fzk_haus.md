# E5 · Autoría controlada sobre AC20-FZK-Haus.ifc

**Documento:** E5 · Primer ciclo de autoría real con validación post-autoría sobre EIR NEXUM PBSA v0.2 multi-variant
**Modelo fuente:** `AC20-FZK-Haus.ifc` (muestra buildingSMART, ARCHICAD-20, schema IFC4)
**Modelo autoriado:** `out/AC20-FZK-Haus_authored.ifc`
**Sesiones origen:** S5·L (Lun 08/06) · S5·X (Mié 10/06) · S5·S (Sáb 13/06, cierre formal)
**Autor:** José M. Soria · NEXUM Developments
**Fecha de redacción inicial:** 10/06/2026 (S5·X · borrador funcional v0.1)
**Fecha de cierre formal:** 13/06/2026 (S5·S · v1.0 firmada · tag `e5-closed`)
**Versión documento:** 1.0 (cerrada)
**Estado:** Firmado · entregable E5 cerrado

---

## 1. Resumen ejecutivo

Se ha ejecutado el **primer ciclo completo de autoría controlada** sobre el modelo `AC20-FZK-Haus.ifc`, aplicando un contrato vinculante de autoría (`docs/S5L_reglas_autoria.md` v1.0) que establece 5 principios rectores y una whitelist explícita de operaciones permitidas (v0.1). El ciclo cubre las cuatro fases canónicas del workflow OpenBIM de autoría: **leer → mutar → escribir → re-auditar**, con trazabilidad completa vía diff JSON y verificación cuantitativa de impacto vía re-auditoría contra el EIR NEXUM PBSA.

| Indicador | Valor |
|---|---|
| Operaciones de autoría aplicadas | **4** (3 set_pset_property + 1 create_element) |
| Whitelist v0.1 cobertura | §3.1 (propiedades) + §3.2 (geometría IfcWall) |
| Mutaciones al modelo original | **0** (P1 garantizado) |
| Trazabilidad | 100% (`out/AC20-FZK-Haus_authored_diff.json`) |
| Validez del IFC autoriado | ✓ Re-cargable con `ifcopenshell.open()` |
| Variantes EIR re-auditadas | **4** (comun · diseno · contratista · asbuilt) |
| Mejora medible (variante común) | **+6.67 pp** global (`H3.DOOR.FireRating fail→pass`) |
| Regresiones detectadas | **0** (P4 verificada en las 4 variantes) |
| Refactor DF-01 cerrado | ✓ (auditor multi-variant operativo desde S5·X) |

**Conclusión:** el modelo autoriado supera la verificación P4 en las 4 variantes contractuales del EIR y demuestra mejora cuantificable en el chequeo objetivo de la autoría (puertas EI). El pipeline establece la base reproducible sobre la que se construirán las autorías posteriores (S6·L+).

---

## 2. Alcance y metodología

### 2.1 Alcance

- **Modelo fuente:** `AC20-FZK-Haus.ifc` (modelo residencial proxy de buildingSMART). Se mantiene como proxy formativo hasta disponer del modelo PBSA real NEXUM (target S7·L+).
- **Operaciones autorizadas:** únicamente las declaradas en la whitelist v0.1 de `docs/S5L_reglas_autoria.md` §3.
- **Validación post-autoría:** las 4 variantes EIR v0.2 (`comun`, `diseno`, `contratista`, `asbuilt`).
- **Fuera de scope (E5):** edición de geometría existente, borrado de elementos, mutación de relaciones espaciales preexistentes, alteración de cabecera STEP, reasignación de GlobalIds. Estos casos requieren ampliación formal de la whitelist (target S6·L+).

### 2.2 Metodología · workflow canónico de autoría OpenBIM

El ciclo de autoría implementa cuatro fases secuenciales:

1. **Lectura no-mutante** (P1): carga del IFC fuente en memoria con `ifcopenshell.open()` y verificación de que el target ≠ source antes de escribir.
2. **Mutación trazada** (P2 + P3): cada operación es una función Python con docstring que cita el §EIR aplicable, y deja registro en el acumulador `AuthorDiff`.
3. **Escritura atómica** (P1): el modelo mutado se serializa a `out/<base>_authored.ifc` y el diff a `out/<base>_authored_diff.json` simultáneamente.
4. **Re-auditoría post-autoría** (P4): el IFC autoriado se vuelve a pasar por `s4s_audit_eir.py` para cada variante, y se compara con baseline para verificar cero retrocesos.

### 2.3 Principios rectores aplicados

| ID | Principio | Verificación E5 |
|---|---|---|
| **P1** | No mutar el modelo original | `_load_source_copy()` + assert `target ≠ source` en `write_authored_model()`. Fuente intacta. |
| **P2** | Trazabilidad obligatoria | `AuthorDiff` con `op_id`, `value_before`, `value_after`, `eir_ref`, `rationale` por operación. |
| **P3** | Una operación = una función | 2 funciones de operación (`set_pset_property`, `create_basic_wall`) + 2 utilitarias (`_load_source_copy`, `write_authored_model`). |
| **P4** | Validación post-autoría obligatoria | 4 corridas del auditor (una por variante) + comparativa baseline vs post sin retrocesos. |
| **P5** | Whitelist explícita §3 | Solo se invocan operaciones whitelisted (§3.1 FireRating en IfcDoor + §3.2 crear IfcWall). |

---

## 3. Operaciones aplicadas · detalle

### 3.1 OP-001 a OP-003 · `set_pset_property` sobre IfcDoor.FireRating

**Decisión de diseño S5·L (Q1=A):** auto-detección de puertas sin `FireRating` y aplicación de valor uniforme `"EI 30"` conforme a CTE DB-SI para sector residencial.

| op_id | elemento | Pset.Property | value_before | value_after | §EIR |
|---|---|---|---|---|---|
| OP-001 | IfcDoor #17468 · Innentuer-1 | Pset_DoorCommon.FireRating | `null` | `"EI 30"` | §4.2.ARQ |
| OP-002 | IfcDoor #19199 · Innentuer-2 | Pset_DoorCommon.FireRating | `null` | `"EI 30"` | §4.2.ARQ |
| OP-003 | IfcDoor #19504 · Innentuer-3 | Pset_DoorCommon.FireRating | `null` | `"EI 30"` | §4.2.ARQ |

**Justificación:** el modelo fuente tenía 5 IfcDoor de las cuales 2 ya declaraban `FireRating="EI 30"` (cumpliendo) y 3 carecían de la propiedad. La autoría poblar las 3 ausentes con el mismo valor canónico estándar PBSA, corrigiendo el hallazgo `H3.DOOR.FireRating` que en E4 estaba en `fail (40% · 2/5)`.

**Comportamiento defensivo:** la función `set_pset_property` solo pobla propiedades **ausentes**. Si el valor ya existe (incluso si difiere del solicitado), la operación es no-op silenciosa. Esto protege ante regresiones por sobrescritura accidental de valores válidos.

### 3.2 OP-004 · `create_basic_wall` sobre planta baja

**Decisión de diseño S5·L (Q2=A):** muro de validación del pipeline geométrico, dimensiones residenciales típicas.

| Atributo | Valor |
|---|---|
| Tipo | `IfcWall` (entidad nueva) |
| GlobalId | `3sSuArjhP1VAHDFwRlK_Hf` (no determinístico v0.1, ver §6.1 DT-S5L-02) |
| Name | `S5L-AUTH-WALL-001` |
| Dimensiones | 3.0 m × 0.2 m × 2.7 m (largo × espesor × alto) |
| Posición global | (10.0, 5.0, 0.0) |
| Eje longitudinal | X |
| Contenedor | `IfcBuildingStorey "Erdgeschoss"` (#479, planta baja) |
| Representación geométrica | `IfcExtrudedAreaSolid` sobre `IfcRectangleProfileDef` (whitelist §3.2) |
| Conteo IfcWall | 13 → 14 |

**Estructura geométrica creada:** 7 entidades IFC nuevas por muro (`IfcRectangleProfileDef` + `IfcAxis2Placement2D` + `IfcExtrudedAreaSolid` + `IfcAxis2Placement3D` extrusión + `IfcLocalPlacement` muro + `IfcShapeRepresentation` + `IfcProductDefinitionShape`), todas encadenadas al storey contenedor vía `ObjectPlacement.PlacementRelTo`.

---

## 4. Impacto cuantitativo · re-auditoría EIR v0.2 multi-variant

Tras el refactor DF-01 (cerrado en S5·X), la re-auditoría se ejecuta contra las 4 variantes contractuales del EIR PBSA v0.2. La variante **`comun`** es la referencia de equivalencia con v0.1 para verificación P4 byte-a-byte (cero retrocesos vs `s4s_compliance_matrix_baseline.json`).

### 4.1 Comparativa baseline (v0.1) vs post-autoría (v0.2 multi-variant)

| Variante | Total | Pass | Partial | Fail | % Pass | Δ vs baseline v0.1 |
|---|---|---|---|---|---|---|
| baseline v0.1 (FZK-Haus original) | 15 | 3 | 0 | 12 | 20.00% | (referencia) |
| **`comun`** (post-autoría) | 15 | **4** | 0 | 11 | **26.67%** | **+6.67 pp** |
| **`diseno`** (post-autoría) | 19 | 4 | 0 | 15 | 21.05% | n/a (variante nueva) |
| **`contratista`** (post-autoría) | 18 | 4 | 0 | 14 | 22.22% | n/a (variante nueva) |
| **`asbuilt`** (post-autoría) | 18 | 4 | 0 | 14 | 22.22% | n/a (variante nueva) |

### 4.2 Verificación P4 · cero retrocesos por chequeo

Comparativa chequeo-a-chequeo entre baseline v0.1 y `comun` v0.2 (15 chequeos compartidos):

| check_id | Baseline v0.1 | Post v0.2 `comun` | Δ | Status |
|---|---|---|---|---|
| STR.MVD.ReferenceView | fail | fail | = | sin cambio |
| STR.BSDD.Classification | fail | fail | = | sin cambio |
| H3.WALL.ThermalTransmittance | pass (100% · 13/13) | pass (100% · 13/13) | = | sin cambio |
| H3.WALL.FireRating | fail (0% · 0/13) | fail (0% · 0/13) | = | sin cambio |
| H3.WALL.LoadBearing | fail (0% · 0/13) | fail (0% · 0/13) | = | sin cambio |
| H3.WALL.IsExternal | fail (0% · 0/13) | fail (0% · 0/13) | = | sin cambio |
| H3.SLAB.FireRating | fail (0% · 0/4) | fail (0% · 0/4) | = | sin cambio |
| H3.SLAB.LoadBearing | fail (0% · 0/4) | fail (0% · 0/4) | = | sin cambio |
| **H3.DOOR.FireRating** | **fail (40% · 2/5)** | **pass (100% · 5/5)** | **+60 pp · status flip** | **mejora dirigida** |
| H3.WINDOW.IsExternal | fail (0% · 0/11) | fail (0% · 0/11) | = | sin cambio |
| H4.SPACE.GrossPlannedArea | fail (0% · 0/7) | fail (0% · 0/7) | = | sin cambio |
| H4.SPACE.IsExternal | fail (0% · 0/7) | fail (0% · 0/7) | = | sin cambio |
| H4.STOREY.EntranceLevel | fail (0% · 0/2) | fail (0% · 0/2) | = | sin cambio |
| H4.BUILDING.YearOfConstruction | pass (100% · 1/1) | pass (100% · 1/1) | = | sin cambio |
| H4.BUILDING.NumberOfStoreys | pass (100% · 1/1) | pass (100% · 1/1) | = | sin cambio |

**Conclusión P4:** 0 regresiones · 1 mejora dirigida (la objetivo de la autoría). El IfcWall creado (OP-004) no impacta ningún chequeo de la variante `comun` porque ningún chequeo aplica a IfcWall sin Pset_WallCommon poblado, manteniéndose en `fail (0%)` con denominador 13 (no 14, porque el chequeo filtra IfcWallStandardCase, no IfcWall puro).

### 4.3 Por qué `_diseno`, `_contratista` y `_asbuilt` no mejoran sobre `_comun`

Los chequeos nuevos de cada variante son extensiones específicas del rol contractual:

- **`_diseno` (+4 chequeos · 5D/QTO):** las 4 propiedades QTO (`H3.WALL.QTO_NetVolume`, `H3.SLAB.QTO_GrossArea`, `H3.DOOR.QTO_Area`, `H3.WINDOW.QTO_Area`) requieren Pset `Qto_*BaseQuantities` que FZK-Haus no exporta. Resultado: 4 nuevos `fail (0%)`.
- **`_contratista` (+3 chequeos · 4D/WBS):** `WBS_Reference` en muros y losas requiere población de `Pset_*Common.Reference`. `AcousticRating` no está poblado. Resultado: 3 nuevos `fail (0%)`.
- **`_asbuilt` (+3 chequeos · LOIN-FM):** `OccupancyType` y `OccupancyNumber` requieren `Pset_SpaceOccupancyRequirements` que FZK-Haus no exporta. `IsLandmarked` no está poblado. Resultado: 3 nuevos `fail (0%)`.

**Interpretación:** la autoría S5·L se centró exclusivamente en cumplimiento normativo CTE (puertas EI), no en QTO/WBS/FM. Los chequeos nuevos demuestran que el pipeline multi-variant funciona y servirán de baseline para futuras autorías dirigidas por contrato (target S6·L+).

---

## 5. Artefactos producidos

### 5.1 Código

| Ruta | Líneas | Función |
|---|---|---|
| `scripts/s5l_ifc_authoring.py` | 631 | Pipeline de autoría (4 funciones + CLI) |
| `scripts/s4s_audit_eir.py` (v0.2) | +120 sobre v0.1 | Auditor con flag `--variant` + merge automático |

### 5.2 Especificaciones EIR (post DF-01)

| Ruta | Chequeos | Rol |
|---|---|---|
| `eir/_archive/PBSA_v0.1_obligatorias.yaml` | 15 | Histórico congelado (referencia) |
| `eir/PBSA_v0.2_comun.yaml` | 15 | Base obligatoria heredable |
| `eir/PBSA_v0.2_diseno.yaml` | +4 (=19 efectivos) | Variante Diseño · 5D/QTO |
| `eir/PBSA_v0.2_contratista.yaml` | +3 (=18 efectivos) | Variante Constructor · 4D/WBS |
| `eir/PBSA_v0.2_asbuilt.yaml` | +3 (=18 efectivos) | Variante As-built · LOIN-FM |

### 5.3 Evidencias de autoría (versionadas)

| Ruta | Tamaño | Tipo |
|---|---|---|
| `out/AC20-FZK-Haus_authored.ifc` | 2.69 MB | IFC mutado (P1 garantizado) |
| `out/AC20-FZK-Haus_authored_diff.json` | 3.07 KB | Diff trazado §4.1 (P2) |
| `out/AC20-FZK-Haus_compliance_matrix_post.json` | 16.3 KB | Matriz post v0.1 (S5·L) |
| `out/AC20-FZK-Haus_compliance_post_comun.json` | 13.4 KB | Matriz post v0.2 · comun |
| `out/AC20-FZK-Haus_compliance_post_diseno.json` | 20.0 KB | Matriz post v0.2 · diseño |
| `out/AC20-FZK-Haus_compliance_post_contratista.json` | 17.7 KB | Matriz post v0.2 · contratista |
| `out/AC20-FZK-Haus_compliance_post_asbuilt.json` | 17.4 KB | Matriz post v0.2 · asbuilt |

### 5.4 Documentación

| Ruta | Rol |
|---|---|
| `docs/S5L_reglas_autoria.md` | Contrato vinculante v1.0 (5 principios + whitelist) |
| `docs/S5L_notas_sesion.md` | Notas técnicas S5·L |
| `docs/DT-S5L-01_resolucion.md` | Cierre falso positivo schema FZK-Haus |
| `docs/E5_autoria_fzk_haus.md` | **Este documento** (entregable E5) |

---

## 6. Lecciones aprendidas y deuda generada

### 6.1 Deuda técnica abierta

| ID | Descripción | Target |
|---|---|---|
| ~~DT-S5L-01~~ | Discrepancia schema FZK-Haus IFC4 vs IFC2X3 | ✅ Cerrada S5·X (falso positivo) |
| **DT-S5L-02** | GlobalIds no determinísticos en autoría (v0.1 no fija semilla) · imposibilita reproducibilidad byte-a-byte del IFC autoriado | S6·L · formalizar política de semillas |
| **DT-S5X-01** | Bonsai 0.8.6-alpha unstable disponible (09/06) · decisión: no actualizar hasta release estable | Revisar al cierre del plan (01/08) o cuando salga estable |

### 6.2 Deuda formativa abierta

| ID | Descripción | Target |
|---|---|---|
| ~~DF-01~~ | EIR multi-variante (común/diseño/contratista/as-built) | ✅ Cerrada S5·X |
| **DF-02 (potencial)** | Whitelist §3 ampliación: edición de geometría existente, borrado controlado, edición de relaciones espaciales | S5·X bloque futuro / S6·L |

### 6.3 Aprendizajes clave

1. **El dispatcher `ifcopenshell.api.run(<op_name>, model, ...)` es la forma estable cross-versión** para mutar IFC con la API de ifcopenshell. Más fiable que `ifcopenshell.api.<modulo>.<op>`.
2. **Crear un IfcWall geométricamente válido requiere 7 entidades IFC nuevas**, no solo `IfcWall`. Sin `IfcShapeRepresentation` + `IfcProductDefinitionShape` el muro no tiene cuerpo visible.
3. **`spatial.assign_container` es la forma correcta de vincular un producto a un `IfcBuildingStorey`** sin crear `IfcRelContainedInSpatialStructure` manualmente.
4. **El campo `FILE_NAME.originating_system` de la cabecera STEP no es fuente de verdad sobre el schema IFC** (ver DT-S5L-01_resolucion.md). Usar siempre `FILE_SCHEMA` o `model.schema`.
5. **El patrón "comun + variante mergeable" es robusto sin necesidad de YAML `!include`** custom: PyYAML estándar + merge en código permite herencia explícita y fail-fast en colisiones.
6. **El patrón `.gitignore` genérico `out/*.json` es una trampa silenciosa** para evidencias versionadas. La práctica estable es whitelist explícita por sufijo canónico (`!out/*_authored_diff.json`, `!out/*_compliance_matrix_post.json`, `!out/*_compliance_post_*.json`). Lección dolorosa registrada en S5·X tras descubrir 2 evidencias huérfanas de S5·L no versionadas.
7. **El patrón "1 bloque = 1 commit + 1 confirmación de push"** es salvaguarda imprescindible contra commits silenciosamente incompletos. El caso real `970030f` (S5·X) contenía solo un borrado y se detectó únicamente porque el usuario pegó la salida del push y se ejecutó `git show --stat` tras ella. Sin esa disciplina, el refactor DF-01 habría quedado sin trazabilidad de origen.

### 6.4 Nota sobre evidencias IDS

El briefing matinal del 13/06 sugiere "IDS/validaciones ejecutadas" como evidencia E5. **Esta entrega NO incluye IDS aún**: la validación post-autoría se ejecuta vía auditor propio `s4s_audit_eir.py` (YAML EIR + lógica Python). La transición a IDS v1.0 oficial buildingSMART está planificada para **S7·L (22/06)** dentro del calendario del plan, y permitirá sustituir o complementar la matriz YAML por especificaciones IDS XML estándar. No es deuda formal porque el roadmap ya lo contempla.

---

## 7. Trazabilidad commit-a-evidencia

| Commit (HEAD anterior) | Sesión | Contenido |
|---|---|---|
| `c507e51` | S5·L Bloque B | Lectura geometría (90 elementos, plan view PNG) |
| `c102bfb` | S5·L Bloque C | Reglas de autoría v1.0 vinculantes |
| `18849c9` | S5·L Bloque D | `s5l_ifc_authoring.py` + IFC + diff autoriados (4 ops) |
| `43006fd` | S5·L Bloque E | Re-auditoría post-autoría v0.1 + notas S5·L |
| `970030f` | S5·X | Borrado v0.1 raíz (preparación archivado) |
| `8a66afa` | S5·X | Refactor DF-01: 4 YAML v0.2 + auditor multi-variant + DT-S5L-01 |
| `aab0a2a` | S5·X | Evidencias 4 variantes post-autoría + .gitignore extendido |
| `552c977` | S5·X | Recuperación evidencias huérfanas S5·L (authored_diff + matrix_post) |
| `67b54e1` | S5·X Bloque C | E5 borrador funcional v0.1 (287 líneas) |
| `25c4347` | S5·X Bloque D | `docs/S5X_notas_sesion.md` v1.0 (203 líneas) |
| (este commit) | S5·S | E5 firmado v1.0 + `S5L_notas_sesion.md` §6 actualizada |
| (tag) | S5·S | `e5-closed` sobre el commit anterior |

---

## 8. Criterios de aceptación E5 · estado final

| # | Criterio | Estado |
|---|---|---|
| 1 | `scripts/s5l_ifc_authoring.py` con ≥2 funciones autorizadas | ✅ 4 funciones (2 op + 2 utilitarias) |
| 2 | `out/AC20-FZK-Haus_authored.ifc` válido (re-cargable) | ✅ verificado en sandbox + local |
| 3 | `out/AC20-FZK-Haus_authored_diff.json` con todas las operaciones trazadas | ✅ 4 ops, formato §4.1 conforme |
| 4 | Matriz post con ≥1 chequeo mejorado | ✅ `H3.DOOR.FireRating fail→pass` |
| 5 | `docs/E5_autoria_fzk_haus.md` describiendo operaciones e impacto | ✅ **Este documento v1.0 firmado el 13/06** |
| 6 | Cero retrocesos vs baseline | ✅ verificado en las 4 variantes |
| 7 | (Bonus DF-01) Auditor multi-variant operativo | ✅ cerrado S5·X |
| 8 | Tag `e5-closed` sobre commit final | ✅ creado el 13/06 (S5·S) |

**8 de 8 criterios verdes.** Entregable E5 cerrado formalmente.

---

## 9. Próximos pasos · post-E5 (S6·L · lunes 15/06)

E5 queda cerrado con este documento v1.0 y el tag `e5-closed`. La sesión S6·L abre el bloque **"Calidad: qué validar y cómo"** con tres deudas heredadas a planificar:

1. **DT-S5L-02** · formalizar política de semillas para GlobalIds (reproducibilidad byte-a-byte del IFC autoriado).
2. **DT-S5X-01** · revisar Bonsai en próximo release estable (actualmente 0.8.6-alpha unstable, no actualizar).
3. **DF-02 (potencial)** · ampliar whitelist §3 de `S5L_reglas_autoria.md` para cubrir edición de geometría existente, borrado controlado y edición de relaciones espaciales.

El objeto de S6·L será definir los criterios de qué se valida en un BIM y cómo se materializa esa validación. Esto preparará la entrada de IDS v1.0 en S7·L (ver §6.4) como mecanismo estándar de validación.

---

## 10. Apéndice · comandos de reproducibilidad

Para reproducir el ciclo completo de autoría + re-auditoría desde un clone limpio del repo:

```bash
# 1. Setup (Windows CMD, ya con venv activo)
pip install -r requirements.txt

# 2. Autoría (genera IFC mutado + diff)
python scripts\s5l_ifc_authoring.py --verbose

# 3. Re-auditoría · 4 variantes
python scripts\s4s_audit_eir.py --ifc out\AC20-FZK-Haus_authored.ifc --variant comun       --out out\AC20-FZK-Haus_compliance_post_comun.json
python scripts\s4s_audit_eir.py --ifc out\AC20-FZK-Haus_authored.ifc --variant diseno      --out out\AC20-FZK-Haus_compliance_post_diseno.json
python scripts\s4s_audit_eir.py --ifc out\AC20-FZK-Haus_authored.ifc --variant contratista --out out\AC20-FZK-Haus_compliance_post_contratista.json
python scripts\s4s_audit_eir.py --ifc out\AC20-FZK-Haus_authored.ifc --variant asbuilt     --out out\AC20-FZK-Haus_compliance_post_asbuilt.json
```

---

**Fin de E5_autoria_fzk_haus.md v1.0 (firmado · S5·S · 13/06/2026).**
**Tag aplicado:** `e5-closed`.
