# E3 · Baseline de criterios de auditoría NEXUM

**Documento:** Baseline interna de Psets/Qto mínimos NEXUM utilizada en la auditoría E3 sobre el modelo público `AC20-FZK-Haus.ifc`.
**Versión baseline:** v0.3 (alineada con `scripts/s3l_ifc_inspect.py` v0.3).
**Commit de referencia del script:** `2297fc2` (S3X Bloque C · inspector v0.3 + plantillas E3).
**Hito de cierre E3:** `e3-closed` → `75457fa`.
**Fecha:** 31/05/2026.
**Autor:** José M. Soria (NEXUM).
**Estado:** Documentación retrospectiva de baseline implícita. Será sustituida por IDS formal en S7·L (22/06/2026).

---

## 1. Propósito de este documento

Durante la auditoría E3 (`docs/E3_auditoria_fzk_haus.md`) se evaluó el modelo `AC20-FZK-Haus.ifc` contra un conjunto de Psets y BaseQuantities mínimos definidos por NEXUM. Esa lista de criterios estaba **codificada directamente en el diccionario `PSETS_NEXUM` del script** `scripts/s3l_ifc_inspect.py` (líneas 414-453), no en un EIR (Exchange Information Requirements) externo formal.

Este documento extrae, justifica y deja trazable esa baseline para que:

1. La auditoría E3 sea **citable**: el informe puede referirse a "Baseline NEXUM v0.3 (este documento)" en lugar de a "lo que pone el script".
2. La transición a **IDS v1.0** en S7·L (22/06) tenga un punto de partida documentado y consensuado, no una traducción ciega del código.
3. Quede explícita la **limitación metodológica** del entregable E3 frente al rigor que exige ISO 19650.

---

## 2. Limitaciones de esta baseline (lectura honesta)

Antes de listar los criterios, hay que dejar claro qué **no** es este documento:

| Categoría | Esta baseline (E3) | Lo que sería ISO 19650-conforme |
|---|---|---|
| Origen | Lista hardcodeada en Python | EIR firmado por el Cliente + AIR/PIR |
| Formato | Diccionario `dict[str, dict[str, list[str]]]` | EIR en PDF/DOCX + IDS v1.0 (XML buildingSMART) |
| Aplicabilidad | Genérica NEXUM (cualquier proyecto) | Específica del proyecto y de la fase (PIM/AIM) |
| Vinculación a entregables | Implícita (vía script) | Explícita (vía LOIN — Level of Information Need) |
| Validación automática | `check_minimum_psets()` (ad-hoc) | `ifctester` contra fichero `.ids` |
| Trazabilidad de cambios | Versionada con el script | Versionada con el EIR (control documental) |
| Estado actual | **Operativa pero informal** | **Pendiente — llega en S7·L / S8·L** |

El modelo auditado (`AC20-FZK-Haus.ifc`) es además un **modelo público de prueba de KIT (Karlsruhe)**, no un entregable real de un proyecto NEXUM. La auditoría E3 es por tanto un **ensayo metodológico**, no una auditoría contractual.

---

## 3. Baseline de Psets/Qto mínimos NEXUM v0.3

Baseline aplicada en `check_minimum_psets()` del script v0.3. Se evalúa por **clase IFC exacta** (sin subtipos): por ejemplo, los criterios de `IfcWallStandardCase` no se aplican a `IfcWall` puro y viceversa.

### 3.1 Reglas de evaluación

- Una clase es **conforme** cuando, para cada instancia, están presentes todos los Psets/Qto exigidos y cada propiedad obligatoria tiene un valor **no nulo**.
- Una propiedad presente con valor `None` cuenta como **ausente** (un IFC válido puede declarar la clave y dejarla sin asignar).
- El validador **no acepta variantes históricas** sin prefijo canónico (ej. `BaseQuantities` sin `Qto_Wall`). Decisión alineada con dictamen D3B-01 (ver `docs/S3X_dudas_resueltas.md`): NEXUM exige nombres canónicos buildingSMART.

### 3.2 Tabla de criterios

#### IfcWallStandardCase

| Pset/Qto | Propiedades obligatorias |
|---|---|
| `Pset_WallCommon` | `Reference`, `LoadBearing`, `IsExternal`, `FireRating`, `AcousticRating`, `ThermalTransmittance` |
| `Qto_WallBaseQuantities` | `Length`, `Height`, `Width`, `GrossSideArea`, `NetVolume` |

#### IfcSlab

| Pset/Qto | Propiedades obligatorias |
|---|---|
| `Pset_SlabCommon` | `Reference`, `LoadBearing`, `IsExternal`, `FireRating`, `AcousticRating`, `ThermalTransmittance` |
| `Qto_SlabBaseQuantities` | `GrossArea`, `Perimeter`, `Width`, `GrossVolume` |

#### IfcWindow

| Pset/Qto | Propiedades obligatorias |
|---|---|
| `Pset_WindowCommon` | `Reference`, `IsExternal`, `FireRating`, `ThermalTransmittance`, `AcousticRating`, `Infiltration` |
| `Qto_WindowBaseQuantities` | `Width`, `Height`, `Area` |

#### IfcDoor

| Pset/Qto | Propiedades obligatorias |
|---|---|
| `Pset_DoorCommon` | `Reference`, `IsExternal`, `FireRating`, `ThermalTransmittance`, `AcousticRating`, `Infiltration` |
| `Qto_DoorBaseQuantities` | `Width`, `Height`, `Area` |

#### IfcSpace

| Pset/Qto | Propiedades obligatorias |
|---|---|
| `Pset_SpaceCommon` | `Reference`, `Category`, `PubliclyAccessible` |
| `Qto_SpaceBaseQuantities` | `NetFloorArea`, `GrossFloorArea`, `NetVolume`, `NetCeilingArea` |

**Total:** 5 clases · 10 Psets/Qto · 40 propiedades obligatorias.

---

## 4. Justificación funcional por clase

### IfcWallStandardCase

- **`Pset_WallCommon`** cubre datos funcionales esenciales: portancia (`LoadBearing`), interior/exterior (`IsExternal`), prestaciones reglamentarias (resistencia al fuego, acústica conforme DB-HR del CTE, transmitancia térmica para HE).
- **`Qto_WallBaseQuantities`** asegura mediciones consistentes para presupuesto y cómputo de mediciones (BIM 5D), sin depender de geometría implícita.

### IfcSlab

- Mismo patrón que muros, ampliado a forjados. Crítico para acústica de impacto (DB-HR), reacción al fuego entre sectores y cálculo térmico de soleras.

### IfcWindow / IfcDoor

- **`Infiltration`** es exigible por NEXUM por su impacto en cálculo de demanda energética (HE0/HE1 del CTE) y certificación energética.
- **`AcousticRating`** se mantiene aunque sea opcional en muchos proyectos: en residencial colateral a vivienda (PBSA, coliving) es contractualmente relevante.

### IfcSpace

- **`PubliclyAccessible`** es un dato funcional clave en activos de Living Alternativo (zonas comunes vs. privativas) y en accesibilidad (DB-SUA del CTE).
- **`Qto_SpaceBaseQuantities`** habilita programa de superficies útiles y construidas conforme a Orden VIV/984/2009 y planimetría comercial.

---

## 5. Lo que esta baseline **no** cubre (deuda hacia S7·L)

Listado explícito de elementos previstos para el IDS formal de S7·L pero **fuera del alcance** de esta baseline E3:

- ❌ Criterios sobre `IfcBeam`, `IfcColumn`, `IfcCovering`, `IfcRoof`, `IfcStair`, `IfcRailing`.
- ❌ Verificación de **clasificaciones** (`IfcClassificationReference` → Uniclass / Omniclass / CTE).
- ❌ Verificación de **materiales** y capas (`IfcMaterialLayerSetUsage` con espesores y materiales nombrados conforme a bSDD).
- ❌ Verificación de **tipos** (`IfcTypeObject`) con sus propios Psets.
- ❌ Reglas de **nomenclatura** de instancias (`Name` con patrón regex por disciplina).
- ❌ Reglas de **georreferenciación** (`IfcSite` con `RefLatitude`/`RefLongitude`/`RefElevation` no nulos).
- ❌ Reglas sobre **`IfcOpeningElement` huérfanos** (sin `IfcRelFillsElement`): hoy se detectan en la auditoría narrativa, no en `check_minimum_psets()`.
- ❌ Cobertura de **subtipos** (la baseline actual evalúa clase exacta; subtipos no auditados quedan invisibles).

Estos elementos se documentarán formalmente en el EIR/AIR de NEXUM y se materializarán en el fichero `eir_nexum_v1.ids` en S7·L.

---

## 6. Trazabilidad con la auditoría E3

| Pieza | Ubicación en repo |
|---|---|
| Baseline conceptual (este documento) | `docs/E3_baseline_criterios.md` |
| Baseline ejecutable (diccionario Python) | `scripts/s3l_ifc_inspect.py` líneas 414-453 (`PSETS_NEXUM`) |
| Motor de auditoría | `scripts/s3l_ifc_inspect.py` líneas 485-... (`check_minimum_psets()`) |
| Modelo auditado | `models/samples/AC20-FZK-Haus.ifc` (SHA-256 `70cc8ff2…b77994`) |
| Informe de auditoría | `docs/E3_auditoria_fzk_haus.md` |
| Checklist binario | `docs/E3_checklist.md` |
| Lab run reproducible | `out/E3_lab_run.md` |
| Meta-cierre | `docs/E3_cierre.md` |
| Commit del entregable | `75457fa` (tag `e3-closed`) |
| Dictamen D3B-01 (origen de los criterios) | `docs/S3X_dudas_resueltas.md` |

---

## 7. Versionado y siguientes pasos

| Versión | Fecha | Cambio | Estado |
|---|---|---|---|
| v0.3 | 31/05/2026 | Baseline documentada por primera vez (extraída del script). | **Vigente** |
| v1.0 (prevista) | 22/06/2026 (S7·L) | Codificación en IDS v1.0 (XML buildingSMART). Ampliación a clases pendientes (sección 5). | Pendiente |
| v1.1 (prevista) | 29/06/2026 (S8·L) | Validación automatizada con `ifctester` sobre FZK-Haus + segundo modelo. | Pendiente |

A partir de v1.0 este documento se mantendrá como **referencia conceptual** y se citará desde el fichero IDS oficial. El diccionario `PSETS_NEXUM` del script se marcará como `DEPRECATED` y se redirigirá a la lectura del IDS vía `ifctester`.

---

## 8. Referencias normativas

- **ISO 19650-1:2018** · Organización y digitalización de la información sobre edificios — Parte 1: Conceptos y principios.
- **ISO 19650-2:2018** · Parte 2: Fase de entrega de los activos. Sección sobre EIR.
- **buildingSMART IDS v1.0** · [Information Delivery Specification](https://github.com/buildingSMART/IDS).
- **buildingSMART bSDD** · [buildingSMART Data Dictionary](https://search.bsdd.buildingsmart.org/).
- **CTE DB-HR** · Documento Básico Protección frente al Ruido.
- **CTE DB-HE** · Documento Básico Ahorro de Energía.
- **CTE DB-SUA** · Documento Básico Seguridad de Utilización y Accesibilidad.
- **Dictamen interno D3B-01** · `docs/S3X_dudas_resueltas.md` (justificación de la elección de Psets canónicos buildingSMART).
