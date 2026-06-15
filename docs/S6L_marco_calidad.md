# S6·L · Marco de calidad BIM (8 dimensiones · ISO 19650-2)

**Fecha:** 15/06/2026 (S6·L · sesión lunes)
**Sesión:** S6·L · Calidad: qué validar y cómo
**Autor:** José M. Soria · NEXUM Developments
**Versión documento:** 1.0
**Estado:** Vigente · marco normativo interno del plan formativo

---

## 1. Objeto

Este documento establece el **marco conceptual de calidad de información** que aplica el plan formativo OpenBIM 12 semanas (11/05/2026 – 01/08/2026) a todos los modelos BIM auditados y autoriados a partir de la semana S6.

El marco responde a tres preguntas operativas:

1. **¿Qué se valida en un BIM?** → taxonomía de 8 dimensiones de calidad (§2).
2. **¿Cómo se valida?** → reglas propias (Python/YAML) vs especificaciones IDS estándar (§4 + addendum decisión).
3. **¿Cuándo se acepta?** → criterios de aceptación pass/fail/partial por dimensión (§5).

El documento se alinea con **ISO 19650-2:2018 §5.3** (calidad de información durante la fase de delivery) y prepara la transición a **IDS v1.0** (buildingSMART, junio 2024) prevista en S7·L. Define la base teórica que el motor de calidad `s6l_quality_engine` (refactor de `s4s_audit_eir.py`) materializa en código.

### 1.1 Alcance

- Aplica a las 4 variantes EIR v0.2: común, diseño, contratista, asbuilt.
- Aplica a modelos IFC4 y IFC4.3 (IFC2x3 fuera de alcance del plan tras S5·X).
- No aplica a fases pre-RIBA Plan-of-Work 0 (estratégica), donde la información BIM aún no es contractual.

### 1.2 No-objetivos

- No sustituye a un PEB (Plan de Ejecución BIM) operativo de proyecto. Este es un marco formativo de referencia.
- No define la totalidad de los checks IDS posibles (eso depende del proyecto real).
- No establece thresholds numéricos de aceptación absolutos: cada proyecto ajusta los suyos sobre esta base.

---

## 2. Las 8 dimensiones de calidad organizadas por capa ISO 19650-2

ISO 19650-2 distingue 3 capas de información en la entrega de un activo. Cada dimensión de calidad se asigna a una capa según su naturaleza:

### 2.1 · Capa de información gráfica

Información representable visualmente en el modelo 3D/2D.

#### D4 · Geometría

- **Qué se valida:** existencia y validez de `IfcShapeRepresentation` y `IfcProductDefinitionShape` en todo producto físico (muros, forjados, ventanas, puertas, mobiliario fijo). Bounding box no nulo. Sólidos cerrados (manifoldness) cuando aplica. Coherencia entre representación `Body` y representación `Axis` en muros.
- **Por qué importa:** sin geometría válida el modelo no es navegable, no se puede federar con MEP/estructura, y la mayoría de validaciones IFC viewers reportan errores que bloquean al cliente.
- **Indicadores típicos:** `% productos físicos con IfcProductDefinitionShape`, `% sólidos cerrados`, `nº productos con bounding box nulo`.

### 2.2 · Capa de información no gráfica

Datos alfanuméricos, declarativos y relacionales del modelo. Es la capa más amplia del marco porque captura la mayor parte del valor contractual del BIM.

#### D1 · Modelo (integridad estructural)

- **Qué se valida:** schema declarado en `FILE_SCHEMA` (IFC4 / IFC4.3); coherencia entre `FILE_SCHEMA` y `model.schema`; existencia de las entidades raíz mínimas (`IfcProject`, `IfcSite`, `IfcBuilding`, ≥1 `IfcBuildingStorey`); coherencia de la cabecera STEP (autor, organización, herramientas declaradas vs reales).
- **Por qué importa:** un fichero IFC con schema declarado erróneamente (caso DT-S5L-01 falso positivo) o sin entidades raíz no es interoperable. Es el primer filtro de cualquier auditoría.
- **Indicadores típicos:** `schema == IFC4`, `nº IfcProject == 1`, `nº IfcBuildingStorey ≥ 1`, `FILE_SCHEMA coincide con model.schema`.

#### D2 · Propiedades (Psets y atributos)

- **Qué se valida:** existencia de los Psets obligatorios por familia de producto (`Pset_WallCommon` en muros, `Pset_DoorCommon` en puertas, `Pset_SpaceCommon` en espacios, etc.); existencia de propiedades específicas dentro de cada Pset (`FireRating`, `IsExternal`, `LoadBearing`, `ThermalTransmittance`); completitud por elemento (`% elementos con todas las propiedades obligatorias`).
- **Por qué importa:** la información no-gráfica es donde reside el 80% del valor de un BIM en fases operativas (FM, cumplimiento normativo, certificaciones). Sin Psets el modelo es solo geometría.
- **Indicadores típicos:** `% muros con Pset_WallCommon`, `% puertas con FireRating definido`, `nº propiedades nulas críticas`.

#### D3 · Relaciones (containment, agregación, conexión)

- **Qué se valida:** containment correcto (`IfcRelContainedInSpatialStructure`: todo producto físico está contenido en un `IfcBuildingStorey`); agregación correcta (`IfcRelAggregates`: jerarquía Project → Site → Building → Storey → Space); conexiones (`IfcRelConnectsElements` en uniones muro-forjado, muro-muro); ausencia de elementos huérfanos.
- **Por qué importa:** las relaciones definen la **lógica espacial y constructiva** del modelo. Un muro sin containment no aparece en planos de planta. Una puerta sin `FillsVoid` no se exporta a software de simulación. Errores aquí son los más sutiles y los que más bloquean integraciones downstream.
- **Indicadores típicos:** `% productos físicos con containment`, `nº elementos huérfanos`, `jerarquía Project→Site→Building→Storey completa`.

#### D5 · Unidades

- **Qué se valida:** declaración explícita de `IfcUnitAssignment` en el modelo; sistema métrico SI coherente (metros para longitud, m² para superficie, m³ para volumen, grados para ángulos); ausencia de unidades imperiales mezcladas; coherencia entre `IfcSIUnit` declarado y valores numéricos efectivos (sniff test: si un muro tiene `Length = 12000`, es probable que las unidades reales sean milímetros aunque se declare metro).
- **Por qué importa:** unidades incoherentes son el error más caro de detectar tarde — un edificio "exportado en mm pero declarado en m" causa retrabajos de semanas en MEP, estructura y QTO.
- **Indicadores típicos:** `IfcUnitAssignment presente == true`, `unidades métricas SI == true`, `sniff test longitudes coherente`.

#### D6 · Clasificación (sistemas externos)

- **Qué se valida:** asignación de códigos de clasificación externos (Uniclass 2015, Omniclass, COBie, CTE-DB, bSDD) a los elementos relevantes vía `IfcRelAssociatesClassification`; completitud por familia; consistencia del sistema declarado (no mezclar Uniclass + Omniclass sin razón).
- **Por qué importa:** la clasificación es el puente entre el BIM y los sistemas externos (presupuestos, mantenimiento CMMS, normativa CTE). Sin clasificación, el BIM es una isla.
- **Indicadores típicos:** `% elementos con clasificación`, `sistema clasificación declarado consistente`, `nº códigos clasificación inválidos`.

#### D7 · Temporal · 4D (planificación)

- **Qué se valida:** vinculación de productos a una WBS (`IfcTask` + `IfcRelAssignsToProcess`); coherencia secuencial de hitos contractuales; asignación de fechas planificadas (start/end) a tareas con duración no nula; ausencia de tareas huérfanas sin asignación a producto.
- **Aplica principalmente a:** variante **contratista** EIR v0.2 (3 checks introducidos en S5·X bloque B). Opcionalmente a diseño cuando el plan de obra integra anteproyecto.
- **Por qué importa:** sin 4D, el BIM no soporta planificación 4D ni control de avance. Es el dominio del contratista, no del proyectista.
- **Indicadores típicos:** `% productos físicos con tarea asignada`, `nº hitos contractuales declarados`, `secuencia WBS coherente`.

#### D8 · Coste · 5D (QTO y control de coste)

- **Qué se valida:** vinculación de productos a partidas de coste (`IfcCostItem` + `IfcRelAssignsToControl`); QTO automatizable por cantidades (`Qto_WallBaseQuantities`, `Qto_SlabBaseQuantities`); coherencia entre cantidad declarada y cantidad geométrica calculable (sniff test QTO).
- **Aplica principalmente a:** variante **diseño** EIR v0.2 (4 checks introducidos en S5·X bloque B). Opcionalmente a contratista cuando se gestionan certificaciones.
- **Por qué importa:** el 5D es el puente entre el BIM y el presupuesto. Sin 5D, las mediciones se hacen aparte en hojas Excel y se pierden a las primeras modificaciones de proyecto.
- **Indicadores típicos:** `% elementos con Qto base`, `nº elementos con IfcCostItem asociado`, `desviación cantidad declarada vs calculada`.

### 2.3 · Capa de documentación

Documentos del CDE que respaldan el modelo pero no son parte del modelo IFC.

- **Qué se valida:** existencia y vigencia del EIR contractual; existencia del BEP firmado por todas las partes; trazabilidad de auditorías previas (matrices `_compliance_*.json` versionadas en el repo); referencias normativas declaradas (ISO 19650, buildingSMART IDS, CTE, BREEAM).
- **Por qué importa:** sin documentación contractual asociada, el modelo no tiene marco de aceptación. Es la capa que conecta el BIM con el contrato.
- **Indicadores típicos:** `EIR versión X vigente`, `BEP firmado`, `nº matrices auditoría en repo`.

---

## 3. Matriz dimensión × variante EIR v0.2

Cómo se asignan las 8 dimensiones a cada variante del EIR multi-variante consolidado en S5·X:

| Dimensión | común | diseño | contratista | asbuilt |
|---|---|---|---|---|
| **D1 · Modelo** | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio |
| **D2 · Propiedades** | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio |
| **D3 · Relaciones** | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio |
| **D4 · Geometría** | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio |
| **D5 · Unidades** | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio |
| **D6 · Clasificación** | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio |
| **D7 · Temporal (4D)** | ⚪ no aplica | ⚪ opcional | ✅ obligatorio | ✅ obligatorio (hitos as-built) |
| **D8 · Coste (5D)** | ⚪ no aplica | ✅ obligatorio | ⚪ opcional | ⚪ no aplica |
| **Documentación** | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio | ✅ obligatorio |

**Lectura del esquema:**

- Las 6 dimensiones del modelo IFC (D1–D6) + documentación son **obligatorias siempre**: forman el contrato común.
- D7 (4D) **entra en contratista** porque la planificación es responsabilidad de la ejecución, no del proyectista.
- D8 (5D) **entra en diseño** porque el control de coste contractual nace en el anteproyecto (el contratista hereda QTO definido en diseño, no lo crea desde cero).
- D7 también es obligatorio en **asbuilt** pero solo para hitos de cierre (no WBS completo).

Esta asignación implementa fielmente la directiva del usuario registrada en S5·L: "EIR de diseño debe incluir control de coste (5D); EIR del contratista debe incluir planificación (4D)".

---

## 4. El "cómo" · reglas propias vs IDS estándar

### 4.1 Estado actual (heredado S5·X)

El motor de calidad actual es `scripts/s4s_audit_eir.py` (refactor multi-variante S5·X). Funciona con:

- **EIR en YAML** (4 variantes v0.2 en `eir/PBSA_v0.2_*.yaml`).
- **Reglas en Python** dentro del propio script (lógica `check_*` por tipo de check).
- **Auditoría → matriz JSON** (`out/AC20-FZK-Haus_compliance_post_*.json`).

Es funcional, multi-variante, fail-fast en colisiones, con `audit_meta.eir_source` para trazabilidad inversa. Pero **no es estándar**: nadie fuera de este repo puede ejecutarlo.

### 4.2 Criterio de migración a IDS v1.0

IDS (Information Delivery Specification) v1.0 fue ratificado por buildingSMART en junio 2024. Es **XML estándar** que permite expresar requisitos de información en un formato interoperable entre `ifctester`, `Bonsai`, `BIMcollab Zoom`, `Solibri`, `BIMvision`, `Revit IDS Manager` y cualquier otro herramienta IDS-compliant.

**Decisión de migración por tipo de check:**

| Tipo de check | Quedarse en YAML/Python | Migrar a IDS |
|---|---|---|
| Presencia de Pset / propiedad concreta | ❌ | ✅ IDS expresa esto nativamente |
| Valor de propiedad dentro de rango / enum | ❌ | ✅ IDS soporta `value` + `restriction` |
| Existencia de clasificación externa | ❌ | ✅ IDS soporta `classification` |
| Containment / agregación / relaciones | ❌ | ✅ IDS soporta `partOf` |
| Cardinalidad mínima de entidad | ❌ | ✅ IDS soporta `minOccurs` |
| **Lógica condicional cruzada entre Psets** | ✅ | ❌ IDS no soporta condicionales complejas |
| **Sniff tests numéricos (unidades, QTO)** | ✅ | ❌ IDS no soporta cálculos derivados |
| **Validaciones de cabecera STEP** | ✅ | ❌ IDS opera sobre entidades, no header |
| **Validaciones 4D temporales (secuencia)** | ✅ | ⚠️ IDS no soporta directamente (sí `IfcTask` presence) |

**Conclusión:** **~70% de los checks actuales son migrables a IDS**. El 30% restante (lógica condicional, sniff tests, header) permanecerá en motor propio. El motor refactorizado debe poder **componer ambos backends** en una sola auditoría.

### 4.3 Arquitectura del motor refactorizado (target Bloque D)

```
quality_engine/
├── __init__.py
├── core/
│   ├── runner.py          # orquestador: carga EIR + ejecuta backends + consolida matriz
│   ├── result.py          # dataclass ResultadoCheck (id, status, evidence, dimension, backend)
│   └── merger.py          # merge común+variante con fail-fast (heredado S5·X)
├── backends/
│   ├── yaml_python.py     # backend legacy: reglas estructurales+LOIN actuales
│   └── ids_xml.py         # backend nuevo: invoca ifctester contra .ids
├── rules/
│   ├── d1_modelo.py
│   ├── d2_propiedades.py
│   ├── d3_relaciones.py
│   ├── d4_geometria.py
│   ├── d5_unidades.py
│   ├── d6_clasificacion.py
│   ├── d7_temporal.py
│   └── d8_coste.py
└── cli.py                 # entrypoint: --variant, --eir-version, --ids opcional
```

El refactor Bloque D de hoy crea **la estructura modular y los stubs de cada módulo**, no migra todavía las reglas reales. La migración de reglas Python → módulos `rules/d*.py` se hará progresivamente entre S6·X y S7·L.

---

## 5. Criterios de aceptación pass/fail/partial

Cada check de calidad devuelve uno de **3 estados**:

- **`pass`** · el check pasa al 100% sobre el universo aplicable.
- **`fail`** · el check no pasa o pasa por debajo del threshold mínimo aceptable.
- **`partial`** · el check pasa por encima del threshold mínimo pero por debajo del 100%.

### 5.1 Thresholds genéricos por defecto

| Tipo de check | threshold `partial` | threshold `pass` |
|---|---|---|
| Presencia de Pset obligatorio | ≥ 80% elementos | 100% elementos |
| Presencia de propiedad obligatoria | ≥ 80% elementos | 100% elementos |
| Containment / relaciones | ≥ 95% elementos | 100% elementos |
| Clasificación externa | ≥ 70% elementos | 100% elementos |
| Geometría válida (sólidos cerrados) | ≥ 90% elementos | 100% elementos |
| Header / unidades / schema | (no aplica · binarios) | true |

Estos thresholds son **valores por defecto del marco formativo**. Un proyecto real puede endurecerlos o relajarlos en su EIR específico.

### 5.2 Estado final auditoría

- **Auditoría `pass`** → 100% de checks obligatorios en `pass` + ≥ 80% opcionales en `pass`.
- **Auditoría `partial`** → ≥ 80% obligatorios en `pass` + ningún obligatorio en `fail`.
- **Auditoría `fail`** → cualquier obligatorio en `fail`.

---

## 6. Formato de evidencias

Cada auditoría genera **2 ficheros mínimos** en `out/`:

1. `<modelo>_compliance_post_<variante>.json` · matriz completa de resultados (versionada en repo).
2. `<modelo>_audit_report_<variante>.md` · resumen humano (≤ 1 página, opcional pero recomendado para evidencia E6).

Y opcionalmente:

3. `<modelo>_validation_<variante>.bcf` · BCF con issues geo-localizados (cuando D4 falla con elementos concretos identificables).
4. `<modelo>_validation_<variante>.ids.log` · log de `ifctester` cuando se usa backend IDS.

**Convención de naming** (extendida de S5·X):

- `_compliance_post_<variante>.json` para matrices YAML/Python backend
- `_compliance_ids_<variante>.json` para matrices backend IDS
- `_compliance_full_<variante>.json` para matriz consolidada (ambos backends)

---

## 7. Referencias normativas

- **ISO 19650-2:2018** · Organization and digitization of information about buildings and civil engineering works, including building information modelling (BIM) — Part 2: Delivery phase of the assets. §5.3 calidad de la información.
- **ISO 19650-1:2018** · Concepts and principles.
- **buildingSMART IDS v1.0** (junio 2024) · Information Delivery Specification specification. Repo: `buildingSMART/IDS`.
- **buildingSMART IFC4** y **IFC4.3** · Industry Foundation Classes schema.
- **bSDD** · buildingSMART Data Dictionary (clasificaciones).
- **CTE-DB** · Código Técnico de la Edificación, documentos básicos (referencia normativa española).
- **EIR PBSA_v0.2_*.yaml** · 4 variantes vigentes del proyecto formativo (heredado S5·X).
- **S5L_reglas_autoria.md** · reglas vinculantes de autoría sobre modelos.

---

## 8. Trazabilidad de decisiones de S6·L

| Decisión | Opción elegida | Documentada en |
|---|---|---|
| Q1 · Alcance del marco | B · 6 dimensiones + 4D + 5D (8 total) | §2 + §3 |
| Q2 · Motor de calidad | B · Refactor modular real `quality_engine/` | §4.3 + Bloque D |
| Q3 · Posicionamiento IDS | B · Prototipo mínimo IDS XML en S6·L | §4.2 + Bloque E |
| Ordenación dimensiones | Por capa ISO 19650-2 | §2 |
| D1 (Modelo) en capa | No gráfica | §2.2 |
| D5 (Unidades) en capa | No gráfica | §2.2 |

---

**Fin de S6L_marco_calidad.md v1.0.**
**Próximo paso (Bloque C):** redactar `docs/E6_checklist_calidad.md` con la checklist concreta de evidencias para el entregable E6 del sábado 20/06.
