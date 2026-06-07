# E4 · Auditoría LOIN sobre AC20-FZK-Haus.ifc

**Documento:** E4 · Auditoría de cumplimiento EIR NEXUM PBSA v0.1
**Modelo auditado:** `AC20-FZK-Haus.ifc` (muestra buildingSMART, ARCHICAD-20)
**Sesiones origen:** S4·L (Lun 01/06) · S4·X (Mié 03/06) · S4·S (Sáb 06/06, ejec. 07/06)
**Autor:** José M. Soria · NEXUM Developments
**Fecha de auditoría:** 07/06/2026
**Versión documento:** 1.0
**Estado:** Cierre E4 · Entregable interno

---

## 1. Resumen ejecutivo

Se ha auditado el modelo `AC20-FZK-Haus.ifc` contra el conjunto de **15 requisitos OBLIGATORIOS** del EIR NEXUM PBSA v0.1, cubriendo los hitos **H3 (Proyecto Ejecutivo)** y **H4 (As-built / Entrega)**. La auditoría se ejecuta de forma **reproducible y automatizada** mediante el orquestador `scripts/s4s_audit_eir.py`, que consume una representación máquina-leíble del EIR (`eir/PBSA_v0.1_obligatorias.yaml`).

| Indicador | Valor |
|---|---|
| Chequeos totales | **15** (2 estructurales + 13 LOIN) |
| Chequeos aplicables | 15 (0 N/A) |
| **Cumplimiento global** | **20 %** (3 pass / 0 partial / 12 fail) |
| Cumplimiento por categoría | Estructural: **0/2 (0 %)** · LOIN: **3/13 (23 %)** |
| Cumplimiento por hito | H3: 1/10 (10 %) · H4: 2/5 (40 %) |
| No conformidades P0 | 2 (estructurales: MVD + bSDD) |
| No conformidades P1 | 5 (seguridad fuego + estructura) |
| No conformidades P2 | 5 (operación PBSA · FM) |

**Conclusión:** el modelo NO supera la auditoría EIR. Las no conformidades estructurales (MVD y bSDD) son bloqueantes para cualquier entrega real y deben corregirse antes de abordar los déficits LOIN. La única propiedad LOIN crítica que el modelo cumple plenamente es `ThermalTransmittance` en muros (13/13 instancias, valor 1.5 W/m²K), lo que demuestra que la metodología de auditoría funciona correctamente y diferencia conformidad real de incumplimiento.

---

## 2. Alcance y metodología

### 2.1 Alcance

- **Hitos en scope:** H3 (Proyecto Ejecutivo) + H4 (As-built / Entrega)
- **Hitos fuera de scope (v0.1):** H1 (Anteproyecto) y H2 (Proyecto Básico). Se cubrirán en EIR v0.2 (S5·L).
- **Severidad cubierta:** únicamente requisitos **OBLIGATORIOS**. Las propiedades RECOMENDADAS se documentarán en `eir/PBSA_v0.1_recomendadas.yaml` en sesiones posteriores.
- **BIM Uses:** los 5 BIM Uses del EIR (U1-U5: coordinación, QTO/forward funding, CTE, FM, BREEAM/ESG) se contextualizan vía el `rationale` de cada chequeo pero NO se auditan como bloques independientes en v0.1.

### 2.2 Metodología

La auditoría sigue el principio **"requisito → regla → evidencia"** definido en S4·L:

1. **Requisito:** declarado en `eir/PBSA_v0.1_obligatorias.yaml` con trazabilidad al §EIR y al BIM Use.
2. **Regla:** función Python invocable, de tres tipos:
   - `query_missing_property` (LOIN) — auditoría inversa: cuenta instancias que NO declaran la propiedad.
   - `check_mvd_compliance` (estructural) — inspecciona cabecera STEP del IFC.
   - `check_bsdd_classification` (estructural) — valida URI de las `IfcClassificationReference`.
3. **Evidencia:** matriz JSON consolidada (`out/s4s_compliance_matrix_baseline.json`) regenerable en cualquier momento desde el código + modelo.

### 2.3 Política de umbrales

| Status | Criterio LOIN | Criterio estructural |
|---|---|---|
| **pass** | `compliance_pct >= 95` | función devuelve `pass` |
| **partial** | `60 <= compliance_pct < 95` | función devuelve `partial` |
| **fail** | `compliance_pct < 60` | función devuelve `fail` |
| **n/a** | `total == 0` instancias del tipo | (no aplica) |

### 2.4 Limitaciones declaradas

- **Validación bSDD sin HTTP:** la función `check_bsdd_classification` valida formato URI y dominio aceptado pero **no hace petición HTTP** contra `bsdd.buildingsmart.org`. La validación HTTP real se incorporará en S7·L con IDS 1.0.
- **Validación semántica de valores:** la auditoría comprueba presencia/ausencia de propiedades, no la corrección semántica de sus valores (ej. `FireRating="REI 90"` se acepta como `present` sin validar formato CTE). Esto también queda para IDS 1.0.
- **Falsos positivos espaciales conocidos:** el chequeo `query_spatial_containment` (S4·X) detecta `IfcOpeningElement` e `IfcVirtualElement` como huérfanos. Es comportamiento IFC correcto y se documenta como deuda técnica 5.1 para corrección en S5·L/S6·L.

---

## 3. Modelo auditado

### 3.1 Cabecera STEP

| Campo | Valor |
|---|---|
| Fichero | `models/samples/_local/AC20-FZK-Haus.ifc` |
| Schema | IFC2X3 |
| Originating system | ARCHICAD-64 / IFC StepStream |
| ViewDefinitions declaradas | **29 entradas** (1 ViewDefinition + 28 Options) |
| ViewDefinition principal | `QuantityTakeOffAddOnView, SpaceBoundary2ndLevelAddOnView` |
| MVD ReferenceView declarado | **NO** |

### 3.2 Conteos espaciales (S4·L)

| Entidad | Cantidad |
|---|---|
| `IfcProject` | 1 |
| `IfcSite` | 1 |
| `IfcBuilding` | 1 |
| `IfcBuildingStorey` | 2 (Planta Baja, Planta Alta) |
| `IfcSpace` | 7 |
| `IfcWallStandardCase` | 13 (8 envolventes + 5 internos) |
| `IfcSlab` | 4 |
| `IfcDoor` | 5 |
| `IfcWindow` | 11 |
| `IfcClassificationReference` | 1 (sin Location) |

### 3.3 Contexto

`AC20-FZK-Haus.ifc` es un modelo de prueba publicado por buildingSMART, generado desde ARCHICAD para validar pipelines IFC. **No es un modelo PBSA real** y no fue producido bajo un EIR explícito. Se usa aquí como **proxy reproducible** para validar el método de auditoría antes de aplicarlo a un activo NEXUM real (previsto S8 o posterior). La elevada tasa de no conformidades observada es esperada y deseada: confirma que la auditoría discrimina correctamente entre conformidad y déficit.

---

## 4. Hallazgos estructurales

### 4.1 H-STR-01 · MVD ReferenceView ausente (P0 · bloqueante)

| Atributo | Valor |
|---|---|
| Check ID | `STR.MVD.ReferenceView` |
| EIR ref | §3.1 |
| Resultado | `fail` |
| Match esperado | substring `ReferenceView` |
| Match encontrado | **0 / 29** ViewDefinitions declaradas |

**Evidencia:** la cabecera STEP declara `ViewDefinition [, QuantityTakeOffAddOnView, SpaceBoundary2ndLevelAddOnView]`. Ninguna de las 29 entradas (1 ViewDefinition principal + 28 Options de export ARCHICAD) contiene la cadena `ReferenceView`.

**Interpretación:** el modelo fue exportado con un MVD de Quantity Takeoff + Space Boundary L2, no con el Reference View requerido por el EIR. Esto compromete:

- **Interoperabilidad downstream:** herramientas IDS-based pueden rechazar el modelo.
- **Compatibilidad con BCF y CDE OpenBIM:** Speckle, Bonsai y validadores asumen RV por defecto.
- **Estabilidad de geometría:** Quantity Takeoff View incluye representaciones geométricas más permisivas (BRep para sitios) que pueden romper auditorías posteriores.

**Acción correctiva:** re-exportar el modelo desde ARCHICAD seleccionando perfil **IFC4 Reference View** (o el equivalente en la versión del exportador). El header debe declarar `ReferenceView_V1.2` o variante explícita.

### 4.2 H-STR-02 · Clasificación bSDD ausente o no válida (P0 · bloqueante)

| Atributo | Valor |
|---|---|
| Check ID | `STR.BSDD.Classification` |
| EIR ref | §3.1.6 |
| Resultado | `fail` (0 %) |
| `IfcClassificationReference` totales | 1 |
| Refs con URI bSDD válida | 0 |
| Refs sin Location | 1 |

**Evidencia:** el modelo declara una única `IfcClassificationReference` sin atributo `Location`. El EIR §3.1.6 exige que toda referencia de clasificación apunte a un URI HTTP en uno de los dominios aceptados:

- `bsdd.buildingsmart.org`
- `identifier.buildingsmart.org`
- `gubimclass.itec.cat` (sistema oficial catalán, equivalente reconocido)

**Interpretación:** sin URI bSDD, las clasificaciones del modelo no son verificables ni traducibles entre sistemas (Uniclass, OmniClass, GuBIMClass). Esto bloquea:

- **Coordinación multi-disciplinar:** los identificadores de clasificación son ambiguos.
- **QTO automatizado:** las consultas por clase sin URI no son trazables.
- **Reporting BREEAM/ESG:** la trazabilidad de categorías de uso requiere URI estable.

**Acción correctiva:** poblar `IfcClassificationReference.Location` con URI GuBIMClass para cada categoría usada (mínimo: muros, forjados, carpinterías, espacios). Documentar en `Sources` el sistema de clasificación elegido (Uniclass 2015 vs GuBIMClass).

---

## 5. Matriz LOIN de cumplimiento

| # | Check ID | Hito | EIR § | Tipo IFC · Pset · Prop | Total | Present | % | Status |
|---:|---|:---:|---|---|---:|---:|---:|:---:|
| 1 | H3.WALL.ThermalTransmittance | H3 | §4.2.ARQ | `IfcWallStandardCase` · `Pset_WallCommon` · `ThermalTransmittance` | 13 | 13 | 100.0 | **pass** |
| 2 | H3.WALL.FireRating | H3 | §4.2.ARQ | `IfcWallStandardCase` · `Pset_WallCommon` · `FireRating` | 13 | 0 | 0.0 | fail |
| 3 | H3.WALL.LoadBearing | H3 | §4.2.EST | `IfcWallStandardCase` · `Pset_WallCommon` · `LoadBearing` | 13 | 0 | 0.0 | fail |
| 4 | H3.WALL.IsExternal | H3 | §4.2.ARQ | `IfcWallStandardCase` · `Pset_WallCommon` · `IsExternal` | 13 | 0 | 0.0 | fail |
| 5 | H3.SLAB.FireRating | H3 | §4.2.ARQ | `IfcSlab` · `Pset_SlabCommon` · `FireRating` | 4 | 0 | 0.0 | fail |
| 6 | H3.SLAB.LoadBearing | H3 | §4.2.EST | `IfcSlab` · `Pset_SlabCommon` · `LoadBearing` | 4 | 0 | 0.0 | fail |
| 7 | H3.DOOR.FireRating | H3 | §4.2.ARQ | `IfcDoor` · `Pset_DoorCommon` · `FireRating` | 5 | 2 | 40.0 | fail |
| 8 | H3.WINDOW.IsExternal | H3 | §4.2.ARQ | `IfcWindow` · `Pset_WindowCommon` · `IsExternal` | 11 | 0 | 0.0 | fail |
| 9 | H4.SPACE.GrossPlannedArea | H4 | §4.4.FM | `IfcSpace` · `Pset_SpaceCommon` · `GrossPlannedArea` | 7 | 0 | 0.0 | fail |
| 10 | H4.SPACE.IsExternal | H4 | §4.4.FM | `IfcSpace` · `Pset_SpaceCommon` · `IsExternal` | 7 | 0 | 0.0 | fail |
| 11 | H4.STOREY.EntranceLevel | H4 | §4.4.FM | `IfcBuildingStorey` · `Pset_BuildingStoreyCommon` · `EntranceLevel` | 2 | 0 | 0.0 | fail |
| 12 | H4.BUILDING.YearOfConstruction | H4 | §4.4.FM | `IfcBuilding` · `Pset_BuildingCommon` · `YearOfConstruction` | 1 | 1 | 100.0 | **pass** |
| 13 | H4.BUILDING.NumberOfStoreys | H4 | §4.4.FM | `IfcBuilding` · `Pset_BuildingCommon` · `NumberOfStoreys` | 1 | 1 | 100.0 | **pass** |

### 5.1 Muestra de offenders (H3.DOOR.FireRating · único chequeo con cumplimiento parcial significativo)

El chequeo `H3.DOOR.FireRating` es el único `fail` no trivial: **2 de 5 puertas declaran `FireRating`**, las otras 3 no. Esto sugiere que el modelador empezó a poblar la propiedad pero no completó el conjunto. Los 3 offenders se identifican en `out/s4s_compliance_matrix_baseline.json` bajo `results[8].compliance_breakdown` y se pueden enumerar con:

```bash
python scripts/s4x_ifc_lab.py --ifc AC20-FZK-Haus.ifc --query missing \
    --type IfcDoor --pset Pset_DoorCommon --prop FireRating \
    --out out/s4s_door_firerating_offenders.json
```

El resto de chequeos `fail` lo son por **ausencia total** (`present_none=0`, `absent_pset` ≈ total): no es un problema de propiedades vacías sino de Psets enteros no exportados. La acción correctiva es la misma para todos: activar el export de `Pset_WallCommon`, `Pset_SlabCommon`, `Pset_DoorCommon`, `Pset_WindowCommon`, `Pset_SpaceCommon` y `Pset_BuildingStoreyCommon` en el perfil IFC del proveedor BIM.

---

## 6. Análisis por hito

### 6.1 H3 · Proyecto Ejecutivo (10 chequeos · 10 % cumplimiento)

- **Pass:** 1 → `H3.WALL.ThermalTransmittance` (100 %)
- **Fail:** 9 → los 2 estructurales (MVD, bSDD) + 7 LOIN (FireRating, LoadBearing, IsExternal en muros/forjados/puertas/ventanas)

**Interpretación:** el modelo cumple solo el requisito de envolvente térmica. **No cumple ningún requisito de seguridad estructural ni de protección contra incendios**, ambos críticos para validar CTE DB-SE y CTE DB-SI. Para un Proyecto Ejecutivo real esto sería rechazado en check-in CDE.

### 6.2 H4 · As-built / Entrega (5 chequeos · 40 % cumplimiento)

- **Pass:** 2 → `H4.BUILDING.YearOfConstruction` y `H4.BUILDING.NumberOfStoreys` (ambos 100 %)
- **Fail:** 3 → `H4.SPACE.GrossPlannedArea`, `H4.SPACE.IsExternal`, `H4.STOREY.EntranceLevel`

**Interpretación:** las dos propiedades a nivel `IfcBuilding` (entidad singleton del modelo) se cumplen porque ARCHICAD las exporta por defecto. **El gap real está en la gestión operativa PBSA**: sin `GrossPlannedArea` no hay rent-roll automatizable, sin `IsExternal` no se diferencian zonas climatizadas para cálculo de costes operativos, sin `EntranceLevel` no hay base para señalética y wayfinding. Estos déficits invalidarían el modelo para entrega al operador.

### 6.3 Comparativa H3 vs H4

| Indicador | H3 | H4 |
|---|---:|---:|
| Chequeos | 10 | 5 |
| Pass | 1 (10 %) | 2 (40 %) |
| Fail | 9 | 3 |
| Tipo de gap dominante | Pset enteros no exportados | Propiedades de detalle FM ausentes |

El gap de H3 es **sistémico** (faltan Psets completos) y se corrige reconfigurando el perfil de exportación IFC del proveedor. El gap de H4 es **granular** (faltan propiedades específicas) y requiere instrucción explícita al modelador sobre el LOIN de entrega al operador.

---

## 7. No conformidades priorizadas

| Prioridad | ID | Categoría | Hito | Impacto | Esfuerzo estimado |
|:---:|---|---|:---:|---|---|
| **P0** | H-STR-01 | MVD | H3 | Bloqueante. Modelo rechazado en check-in CDE. | Re-export desde ARCHICAD (config IFC) · ~1 h |
| **P0** | H-STR-02 | bSDD | H3 | Bloqueante. Sin clasificación auditable. | Poblar Location en clasificaciones · ~2-4 h |
| **P1** | LOIN-SI | Pset_WallCommon/SlabCommon/DoorCommon · FireRating | H3 | Sin evidencia CTE DB-SI. | Activar Psets en perfil IFC + poblar valores · ~4-8 h |
| **P1** | LOIN-EST | Pset_WallCommon/SlabCommon · LoadBearing | H3 | Sin diferenciación estructural. Bloquea QTO y EST. | Activar Pset + clasificación elemento · ~2-4 h |
| **P1** | LOIN-HE | Pset_WallCommon/WindowCommon · IsExternal | H3 | Sin envolvente clara. Bloquea CTE DB-HE y BREEAM. | Activar atributo · ~1-2 h |
| **P2** | LOIN-FM-Space | Pset_SpaceCommon · GrossPlannedArea + IsExternal | H4 | Bloquea rent-roll y FM operador. | Activar Pset + poblar valores · ~2-4 h |
| **P2** | LOIN-FM-Storey | Pset_BuildingStoreyCommon · EntranceLevel | H4 | Bloquea señalética y wayfinding. | Atributo único por planta · ~30 min |

**Total esfuerzo estimado para alcanzar 100 % cumplimiento EIR Obligatorias v0.1: ~12-22 h** de trabajo del proveedor BIM sobre un modelo de complejidad similar a FZK-Haus.

---

## 8. Recomendaciones al proveedor BIM

Las siguientes recomendaciones están ordenadas por prioridad y formuladas para ser ejecutadas en orden. Cada una incluye la evidencia que las justifica y el hito objetivo.

### R1 · Reconfigurar perfil de exportación IFC (P0)

- **Problema:** el modelo se exporta con MVD `QuantityTakeOff + SpaceBoundary2ndLevel`, no con `Reference View`.
- **Acción:** en ARCHICAD (o equivalente) seleccionar el perfil de exportación **IFC4 Reference View** y verificar que la cabecera STEP declare `ReferenceView_V1.2`.
- **Evidencia:** `out/s4s_mvd_fzk_haus_baseline.json` → `declared_views` listado completo.
- **Hito objetivo:** H3 (cualquier entrega posterior debe partir de esta corrección).
- **Verificación:** re-ejecutar `python scripts/s4s_structural_checks.py --ifc <modelo> --check mvd` y obtener `compliance: "pass"`.

### R2 · Poblar URI bSDD en clasificaciones (P0)

- **Problema:** `IfcClassificationReference.Location` está vacía. Las clasificaciones no son verificables.
- **Acción:** elegir sistema de clasificación oficial (recomendado **GuBIMClass** para proyectos catalanes) y poblar cada `IfcClassificationReference` con URI `https://gubimclass.itec.cat/uri/<categoria>`.
- **Evidencia:** `out/s4s_bsdd_fzk_haus_baseline.json` → `offenders[*].reason: "location_empty"`.
- **Hito objetivo:** H2 (deseable) · H3 (obligatorio).
- **Verificación:** `compliance_pct >= 95` en `check_bsdd_classification`.

### R3 · Activar Psets comunes obligatorios en el perfil de exportación (P1)

- **Problema:** los Psets `Pset_WallCommon`, `Pset_SlabCommon`, `Pset_DoorCommon`, `Pset_WindowCommon`, `Pset_SpaceCommon` y `Pset_BuildingStoreyCommon` no se están exportando (o se exportan vacíos).
- **Acción:** en la configuración de exportación IFC, activar la exportación de los Psets estándar buildingSMART para todas las disciplinas. Verificar que el perfil no esté filtrándolos.
- **Evidencia:** chequeos #2-#11 del compliance matrix → `compliance_breakdown.absent_pset` ≈ total instancias.
- **Hito objetivo:** H3.
- **Verificación:** re-ejecutar `python scripts/s4s_audit_eir.py` y obtener al menos `partial` (≥60 %) en chequeos de Wall, Slab, Door, Window y Space.

### R4 · Poblar propiedades de protección contra incendios (P1)

- **Problema:** `FireRating` ausente en 13/13 muros, 4/4 forjados, 3/5 puertas.
- **Acción:** establecer matriz de clasificación EI/REI por elemento (CTE DB-SI Tabla 1.1 y 1.2) y exigir al modelador poblar `FireRating` para todo elemento de sectorización.
- **Evidencia:** chequeos #2, #5, #7 del compliance matrix.
- **Hito objetivo:** H3.
- **Verificación:** `compliance_pct = 100` en los 3 chequeos `FireRating`.

### R5 · Diferenciar elementos estructurales vs no estructurales (P1)

- **Problema:** `LoadBearing` ausente en 13/13 muros y 4/4 forjados. Imposible distinguir estructura de cerramiento.
- **Acción:** poblar `LoadBearing` (true/false) como propiedad de tipo IFC en biblioteca de objetos del modelador.
- **Evidencia:** chequeos #3 y #6 del compliance matrix.
- **Hito objetivo:** H3.
- **Verificación:** `compliance_pct = 100` en `H3.WALL.LoadBearing` y `H3.SLAB.LoadBearing`.

### R6 · Marcar envolvente térmica (P1)

- **Problema:** `IsExternal` ausente en 13/13 muros y 11/11 ventanas. No hay envolvente identificable.
- **Acción:** poblar `IsExternal` por instancia (no por tipo, ya que un mismo tipo puede usarse interior y exterior). En ARCHICAD se puede automatizar vía atributos de capa.
- **Evidencia:** chequeos #4 y #8 del compliance matrix.
- **Hito objetivo:** H3.
- **Verificación:** `compliance_pct = 100` en ambos chequeos.

### R7 · Completar atributos operativos de espacios (P2 · H4)

- **Problema:** `GrossPlannedArea`, `IsExternal` ausentes en 7/7 espacios. `EntranceLevel` ausente en 2/2 plantas.
- **Acción:** establecer LOIN-FM para entrega H4: cada `IfcSpace` debe declarar superficie planificada (no calculada geométricamente) e indicador climatizado; cada `IfcBuildingStorey` debe marcar la planta de acceso principal.
- **Evidencia:** chequeos #9, #10, #11 del compliance matrix.
- **Hito objetivo:** H4 (As-built).
- **Verificación:** `compliance_pct = 100` en los 3 chequeos.

---

## 9. Trazabilidad y reproducibilidad

### 9.1 Artefactos versionados

| Artefacto | Ruta | Rol |
|---|---|---|
| Especificación EIR | `eir/PBSA_v0.1_obligatorias.yaml` | Contrato máquina-leíble (15 chequeos) |
| Orquestador | `scripts/s4s_audit_eir.py` | Consume YAML, invoca funciones, emite matriz |
| Funciones LOIN | `scripts/s4x_ifc_lab.py` (`query_missing_property`) | Auditoría inversa por propiedad |
| Funciones estructurales | `scripts/s4s_structural_checks.py` (`check_mvd_compliance`, `check_bsdd_classification`) | Auditoría modelo completo |
| Helpers comunes | `scripts/_ifc_helpers.py` | `load_ifc`, `resolve_model_path` |
| Baseline MVD | `out/s4s_mvd_fzk_haus_baseline.json` | Evidencia individual MVD |
| Baseline bSDD | `out/s4s_bsdd_fzk_haus_baseline.json` | Evidencia individual bSDD |
| Baseline LOIN FireRating | `out/s4x_missing_firerating_baseline.json` | Evidencia S4·X heredada |
| **Matriz consolidada** | `out/s4s_compliance_matrix_baseline.json` | **Salida principal E4** |
| Documento síntesis | `docs/E4_auditoria_loin_fzk_haus.md` | Este documento |
| EIR humano | `docs/EIR_NEXUM_PBSA_v0.1.md` | Versión narrativa del EIR |

### 9.2 Comando de regeneración

Cualquier auditoría futura sobre cualquier modelo IFC se regenera con un único comando:

```bash
python scripts/s4s_audit_eir.py \
    --ifc <ruta_o_nombre>.ifc \
    --eir eir/PBSA_v0.1_obligatorias.yaml \
    --out out/<nombre_baseline>.json
```

El orquestador imprime un resumen en consola y escribe la matriz JSON consolidada. La consola refleja los mismos contadores que la sección 1 (Resumen ejecutivo) de este documento.

### 9.3 Trazabilidad commit-a-evidencia

| Commit | Bloque | Contribución a E4 |
|---|---|---|
| `b0dd6cb` | S4·X · A | Refactor `_ifc_helpers` (resolución portable de rutas) |
| `d4c1614` | S4·X · B | `query_missing_property` + baseline FireRating |
| `e8001e8` | S4·X · C | Notebook didáctico de consultas |
| `837d808` | S4·X · D | EIR draft NEXUM PBSA v0.1 (versión narrativa) |
| `c084a9f` | S4·X · E | Cierre notas S4·X |
| `0ef6034` | S4·S · A | `check_mvd_compliance` + `check_bsdd_classification` |
| `1ea22cc` | S4·S · B | YAML EIR + orquestador + matriz consolidada |

Para reproducir la auditoría tal como se publica en este documento, basta con `git checkout 1ea22cc` y ejecutar el comando de la sección 9.2 sobre `AC20-FZK-Haus.ifc`.

### 9.4 Próximos pasos

- **S5·L (15/06):** introducir geometría con IfcOpenShell + iniciar EIR v0.2 (incorporar H1 y H2).
- **S6·L (15/06):** corregir deuda técnica 5.1 (`query_spatial_containment` ignora openings).
- **S7·L (22/06):** migrar todas las verificaciones de este E4 a IDS 1.0 (XML), permitiendo validación HTTP real de URIs bSDD.

---

**Fin del documento E4.**
