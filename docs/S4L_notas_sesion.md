# S4·L · Notas de sesión

**Sesión:** S4·L · Lunes 01/06/2026
**Tema:** IfcOpenShell: lectura y consultas
**Modelo de trabajo:** `models/samples/_local/AC20-FZK-Haus.ifc` (KIT, schema IFC4, 44.249 entidades)
**Script producido:** `scripts/s4l_ifc_query.py` v0.4
**Commits del día:** `705c409` → `a2bc155` → `5845350` → `1e812a5`
**Entregable previsto:** E4 · cierre sábado 06/06

---

## 1. Objetivo de la sesión

Dejar operativa una herramienta de **consulta reproducible sobre cualquier IFC** que responda tres preguntas básicas, base de cualquier auditoría posterior:

| Q | Pregunta | Función | Bloque |
|---|---|---|---|
| Q1 | ¿Cuántas entidades hay y de qué tipo? | `count_by_type()` | B |
| Q2 | ¿Qué es y dónde está esta entidad concreta? | `find_by_guid()` | C |
| Q3 | ¿Qué propiedades y valores reales tiene? | `read_psets()` | D |

Las tres funciones quedan expuestas vía CLI (`--query counts|guid|psets`) y son consumibles desde otros scripts para futuros pipelines (S7·L IDS, S8·L ifctester).

---

## 2. Diseño aplicado

### 2.1 · Niveles de filtrado en `count_by_type()`

Decisión de partida: un solo `count` es engañoso porque IFC mezcla **44.249 entidades** entre objetos semánticos y geometría primitiva. Implementados 3 niveles vía `--level`:

| Nivel | Filtro | Cuenta en FZK-Haus | Pregunta que responde |
|---|---|---|---|
| `bruto` | `iter(model)` | 44.249 (115 clases) | "¿Cuánto pesa el STEP?" |
| `root` | `model.by_type('IfcRoot')` | 1.304 (40 clases) | "¿Cuál es el inventario semántico?" |
| `product` | `model.by_type('IfcProduct')` | 127 (15 clases) | "¿Cuál es el inventario de obra?" |

**Reparto en `bruto`:** 70% es geometría B-Rep primitiva (`IfcCartesianPoint`, `IfcPolyLoop`, `IfcFace`, `IfcFaceOuterBound`). Solo el 30% restante es información "no-geométrica".

### 2.2 · Nivel L3 estructurado en `find_by_guid()`

Decisión de partida: la S3·L ya tenía `explain_entity()` narrativa. La S4·L necesita una salida **estructurada JSON-serializable** para consumo programático. Se opta por L3 con 6 secciones diferenciadas:

```
identity         · id, guid, is_a, name, description, object_type, predefined_type
authoring        · owning_user, owning_application, creation_date, last_modified_date
spatial_container· ref al IfcBuildingStorey o IfcSpace contenedor
type_object      · ref al IfcTypeObject asociado
relationships    · counts de 10 relaciones inversas
psets_summary    · counts y nombres (no valores) de Psets/Qto/Vendor
```

Diferencia explícita con `explain_entity()`: aquí no hay prosa, solo dict consumible.

### 2.3 · Tres categorías en `read_psets()`

Decisión de partida: la información definitoria de una entidad puede vivir en 3 sitios distintos:

| Categoría | Origen | Solapamiento posible |
|---|---|---|
| `instance_psets` | `IfcRelDefinesByProperties` → `IfcPropertySet` | Puede ser override del type |
| `instance_quantities` | `IfcRelDefinesByProperties` → `IfcElementQuantity` | Raramente en type |
| `type_psets` | `IfcTypeObject.HasPropertySets` | Heredado por la instancia |

Se devuelven separadas para no enmascarar `instance vs type`. El auditor decide qué priorizar.

### 2.4 · Manejo de valores

Se implementa `_unwrap_value()` como dispatcher para 6 tipos de IfcProperty/IfcPhysicalQuantity:

- `IfcPropertySingleValue` → escalar
- `IfcPropertyEnumeratedValue` → lista
- `IfcPropertyListValue` → lista
- `IfcPropertyBoundedValue` → dict `{lower, upper, set_point}`
- `IfcPropertyReferenceValue` → resumen del objeto referenciado
- `IfcPhysicalSimpleQuantity` → valor de Length/Area/Volume/Count/Weight/Time

Decisión consciente: **incluir valores `None` en la salida**, no omitirlos. Coherente con la auditoría LOIN: "declarada pero vacía ≠ ausente".

---

## 3. Hallazgos sobre FZK-Haus

### Hallazgo 1 · `IfcMember`, `IfcBeam`, `IfcRailing`, `IfcStair` invisibles para E3

El conteo `product` reveló 6 clases que la auditoría E3 **no cubrió**:

| Clase | Count | Función probable |
|---|---|---|
| `IfcMember` | 42 | Cargaderos sobre huecos + estructura secundaria cubierta |
| `IfcAnnotation` | 14 | Cotas y etiquetas 2D embebidas |
| `IfcBeam` | 4 | Vigas estructurales explícitas |
| `IfcVirtualElement` | 3 | Separadores virtuales para `IfcRelSpaceBoundary` |
| `IfcRailing` | 2 | Barandillas (escalera + galería) |
| `IfcStair` | 1 | La escalera que origina el hueco huérfano #59365 |

**Coherente con sección 5 del baseline E3** (deuda hacia S7·L). Este conteo cuantifica el alcance de esa deuda.

### Hallazgo 2 · `Pset_WallCommon` casi vacío (muro #15042)

Lectura real del muro:

```json
"Pset_WallCommon": {
  "ThermalTransmittance": 1.5
}
```

**Solo 1 propiedad de 6** que pide la baseline NEXUM (`Pset_WallCommon` debería tener `Reference`, `LoadBearing`, `IsExternal`, `FireRating`, `AcousticRating`, `ThermalTransmittance`).

Implicación: el dictamen E3 "0/40 conformes" no era solo por nombres canónicos `Qto_*` ausentes. **Incluso el único Pset canónico que existe está prácticamente vacío.** La auditoría E3 queda confirmada con datos cuantitativos.

### Hallazgo 3 · La información canónica existe disfrazada en Psets vendor

`ArchiCADProperties` (35 propiedades en alemán) contiene **información funcionalmente equivalente** a la canónica:

| Vendor (de) | Equivalente canónico | Valor en muro #15042 |
|---|---|---|
| `Tragende Funktion` | `Pset_WallCommon.LoadBearing` | "Nicht definiert" |
| `Lage` | `Pset_WallCommon.IsExternal` | "Nicht definiert" |
| `Element-Klassifizierung` | `Pset_WallCommon.Reference` | "Wand" |
| `Ursprungsgeschoss` | (info espacial) | "Erdgeschoss" |
| `Baustoff` | (info material) | "Leichtbeton 102890359" |

**Caso de uso futuro:** mapeador `vendor → canonical` para activos donde el flujo de exportación no se puede cambiar. Refuerza el dictamen D3B-01.

### Hallazgo 4 · `BaseQuantities` completo pero mal nombrado

```json
"BaseQuantities": {
  "Length": 4.17, "Height": 2.5, "Width": 0.24,
  "GrossSideArea": 10.425, "NetSideArea": 10.425,
  "GrossVolume": 2.49624, "NetVolume": 2.49624,
  "GrossFootprintArea": 1.0008, "NetFootprintArea": 1.0008
}
```

Las **9 cantidades canónicas presentes**, todas calculadas. El único problema es el nombre: `BaseQuantities` en lugar de `Qto_WallBaseQuantities`. **Renombrado simple → conformidad inmediata.** Confirma la viabilidad técnica de la "Opción B dual naming" sugerida por el auditor E3.

### Hallazgo 5 · ArchiCAD no usa Type PropertySets

`IfcWallType #15234 'Leichtbeton 102890359 240'`:

```json
"type_psets": {}
```

ArchiCAD genera tipos como **agrupadores nominales sin propiedades**. Toda la información va a la instancia. Implicación para NEXUM:

- En FZK-Haus no hay overrides instance/type que confundan auditorías
- En proyectos reales NEXUM tendrá que decidir qué propiedades van en tipo (compartidas entre instancias) vs instancia (específicas)
- El IDS de S7·L debe definir explícitamente la convención

### Hallazgo 6 · Doble timestamp en autoría

| Origen | Valor |
|---|---|
| Header file_name | `2016-12-21T17:54:06` |
| OwnerHistory de la entidad | `2016-12-21T17:54:04` |

Diferencia de 2 segundos: el header se firma al **cerrar** la exportación, los OwnerHistory al **crear cada entidad**. No es bug, es cómo funciona el flujo de ArchiCAD. Útil saberlo para auditorías cronológicas precisas.

### Hallazgo 7 · `owning_user: "Nicht definiert"`

El `Author: "Architect"` del header (S3·L) es la **Organization**, no la **Person**. El `OwningUser.ThePerson.FamilyName` es **"Nicht definiert"** (no definido).

**Lección ISO 19650:** el "autor" de la información tiene dos niveles (Person vs Organization). NEXUM debe exigir `Person.FamilyName` no nulo en sus EIR/AIR reales.

### Hallazgo 8 · MVD declarado en cabecera

```
ViewDefinition [, QuantityTakeOffAddOnView, SpaceBoundary2ndLevelAddOnView]
```

3 ViewDefinitions declaradas simultáneamente, no una sola. El "MVD = CoordinationView_V2.0" que apuntamos en S3·L era simplificación. Confirma el dictamen D3-02 sobre cómo es de "IFC4 puro" un fichero en la práctica.

---

## 4. Decisiones de implementación a recordar

1. **`len(model)` no funciona** → usar `len(list(model))` o `len(model.by_type('IfcRoot'))` según contexto.
2. **`model.by_guid()` lanza `RuntimeError`** si el GUID no existe → capturar y devolver `None`, no propagar excepción.
3. **Manejo IFC2x3 vs IFC4 en types:** `IsTypedBy` (IFC4) con fallback a `IsDefinedBy` filtrado por `IfcRelDefinesByType` (IFC2x3).
4. **Timestamps `int Unix`** desde `OwnerHistory.CreationDate` → convertir a ISO 8601 con `datetime.fromtimestamp()`.
5. **Valores `None` se preservan** en la salida JSON (auditoría LOIN: declarada vacía ≠ ausente).
6. **CRLF/LF warning de Git** en Windows → inofensivo, Git normaliza al hacer checkout.

---

## 5. Deuda técnica abierta

| Item | Impacto | Cuándo se aborda |
|---|---|---|
| `out/*.json` no gitignored → riesgo de basura | Bajo | Decidir política whitelisting en S4·X |
| Constante `MODELS_DIR` para reutilizar entre scripts | Bajo | Refactor mañana en S4·X |
| Helpers `_unwrap_value` y similares quizá extraíbles a módulo común | Medio | Cuando crezca el repo (S5·L o S6·L) |
| Test 2 ventana (no ejecutado) | Bajo | Opcional en S4·X |
| Extensión Bonsai/Blender sobre FZK-Haus (acordada post-E3) | Medio | Post-E4 (sábado 06/06) |
| Versión exacta de Bonsai a pinear | Medio | Antes de tocar Bonsai (diferido) |

---

## 6. Relación con el plan de 12 semanas

| Semana | Lo que prepara S4·L |
|---|---|
| **S4·X (Miércoles 03/06)** | Profundización: notebook con consultas reproducibles + posible refactor a módulo |
| **S5·L (Lunes 08/06)** | IfcOpenShell: geometría y autoría. `_get_spatial_container` y `_get_type_object` ya están |
| **S6·L (Lunes 15/06)** | Calidad: qué validar y cómo. Las 3 queries son base del validador |
| **S7·L (Lunes 22/06)** | IDS v1.0. La baseline implícita del script será reemplazada por IDS explícito |
| **S8·L (Lunes 29/06)** | ifctester. Q3 (`read_psets`) será el motor de lectura para validar contra IDS |

---

## 7. Cierre del día

- ✅ 3 funciones operativas y validadas contra FZK-Haus
- ✅ Cuadre 1:1 con auditoría E3 (cross-check de 13 muros, 11 ventanas, 482 RelDefByProps, 81 SpaceBoundary)
- ✅ 8 hallazgos nuevos documentados (this doc)
- ✅ Evidencia versionada (`out/S4L_psets_muro15042.json`)
- ✅ Script reutilizable como base para S5/S6/S7/S8

**Entregable E4** (cierre sábado 06/06) ya tiene base sólida: los datos necesarios para el informe E4 están extraíbles con `s4l_ifc_query.py`.

---

## 8. Referencias

- **Script:** `scripts/s4l_ifc_query.py` v0.4
- **Evidencia:** `out/S4L_psets_muro15042.json`
- **Modelo:** `models/samples/_local/AC20-FZK-Haus.ifc` · SHA-256 `70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994`
- **Sesión previa:** S3·L (auditoría E3) → tag `e3-closed` @ `75457fa`
- **Baseline NEXUM:** `docs/E3_baseline_criterios.md` v0.3
- **Documentación ifcopenshell:** https://docs.ifcopenshell.org
- **buildingSMART IDS v1.0:** https://github.com/buildingSMART/IDS
