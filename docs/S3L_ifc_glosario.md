# S3·L — Mini-glosario IFC (Bloque C)

**Sesión:** S3·L (semana 3, lunes) · 25/05/2026
**Schema base:** IFC4 (IFC4 ADD2 TC1)
**Modelo de referencia:** `AC20-FZK-Haus.ifc` (KIT/IAI, SHA-256 `70cc8ff2…77994`)
**Documentos hermanos:** `S3L_ifc_jerarquia.md` (Bloque A) · `S3L_ifc_relaciones.md` (Bloque B)
**Autor:** José M. Soria · NEXUM Developments
**Versión:** 0.1

> Glosario operativo de 40 términos esenciales para leer un IFC. Cada entrada incluye: definición breve, dónde se sitúa en el modelo conceptual, y — cuando aplica — ejemplo concreto del FZK-Haus con línea STEP. Cuando un término aparece ya desarrollado en Bloque A o B, se enlaza por referencia interna.

---

## Convención de uso

- ✅ Términos imprescindibles para S3·L–S5·L (saberlos de memoria).
- 🔧 Términos útiles para implementación con IfcOpenShell (S4·L+).
- 📐 Términos para geometría avanzada (S5·X+).
- 🏷️ Términos para clasificación y semantica externa (S7+).

---

## A — Fundamentos del modelo

### 1. `IFC` (Industry Foundation Classes) ✅
Schema de datos abierto para construcción, expresado en EXPRESS (ISO 10303-11), serializado normalmente como STEP Physical File (ISO 10303-21) en ficheros `.ifc`. Ver Bloque A §1.1.

### 2. `EXPRESS` ✅
Lenguaje de modelado de datos formal (ISO 10303-11) usado para definir el schema IFC. No se ve directamente al leer un `.ifc`, pero el formato del fichero (entidades con atributos posicionales) deriva de EXPRESS.

### 3. `SPF` (STEP Physical File) ✅
Serialización textual del modelo definida en ISO 10303-21. Es el formato `.ifc` "clásico", el que ves cuando abres el fichero con un editor de texto. Estructura: `HEADER` + `DATA`.

### 4. `MVD` (Model View Definition) ✅
Subconjunto del schema IFC aplicable a un intercambio concreto. Declarado en el HEADER del SPF. Ejemplo en FZK-Haus: `'ViewDefinition [, QuantityTakeOffAddOnView, SpaceBoundary2ndLevelAddOnView]'` (HEADER, línea 2). Define qué entidades y relaciones son obligatorias/opcionales para un caso de uso (export para QTO, para BEM, para coordinación, etc.).

### 5. `Schema` ✅
Definición formal del modelo IFC. En el HEADER se declara con `FILE_SCHEMA(('IFC4'))`. Versión usada en esta sesión: IFC4. Notas IFC4.3 cuando aporten.

### 6. `ifcXML / ifcJSON / ifcZIP / ifcHDF5`
Otras serializaciones del mismo schema. Ver Bloque A §1.1. No se usan en este modelo.

---

## B — Identificación y trazabilidad

### 7. `GlobalId` (`IfcGloballyUniqueId`) ✅
Identificador único base64 de 22 caracteres, atributo obligatorio de toda entidad que herede de `IfcRoot`. Es **el ancla estable** del objeto entre exportaciones.
**Ejemplo FZK-Haus:** `'2hQBAVPOr5VxhS3Jl0O47h'` (el `IfcBuilding` #434).
**Regla NEXUM (S2·L):** `StoreIFCGUID=true` en el export Revit asegura que el GUID se mantiene entre versiones.

### 8. `OwnerHistory` (`IfcOwnerHistory`) ✅
Entidad que registra quién creó/modificó la entidad y cuándo. Atributo obligatorio de toda entidad `IfcRoot`. En FZK-Haus, todas las entidades referencian la misma `#12` (un solo evento de creación).

### 9. `#NN` (referencia STEP) ✅
Identificador interno del fichero SPF. `#66` es la línea/entidad nº 66. No se mantiene entre exportaciones (cada export reasigna). El identificador estable es el `GlobalId`.

### 10. `tag` (`IfcIdentifier`) 🔧
Identificador interno del software originador. Ejemplo FZK-Haus: el `IfcWallStandardCase` #15042 tiene tag `'BC6F0F70-6195-495E-A2-FC-239713029DB1'`. En Revit, es el `ElementId`.

---

## C — Jerarquía espacial

### 11. `IfcProject` ✅
Contexto raíz del modelo. Único por fichero. Línea 53 del FZK-Haus (#66). Define unidades, contextos de representación y vincula con `IfcSite` mediante `IfcRelAggregates`. Ver Bloque A §6.2.

### 12. `IfcSite` ✅
Sitio físico. Incluye coordenadas geográficas (`RefLatitude`, `RefLongitude`, `RefElevation`). Línea 213 del FZK-Haus (#389). Ver Bloque A §6.3.

### 13. `IfcBuilding` ✅
Edificio individual. Línea 228 del FZK-Haus (#434). Ver Bloque A §6.5.

### 14. `IfcBuildingStorey` ✅
Planta del edificio. FZK-Haus tiene 2: planta baja (#479, Z=0) y cubierta (#35065, Z=2.7m).

### 15. `IfcSpace` ✅
Espacio habitable o funcional. FZK-Haus tiene espacios como Schlafzimmer (#20909), Bad (#21283), Buero (#21640). No siempre se exporta — depende del config (S2·X) y de la herramienta originadora.

### 16. `IfcSpatialStructureElement` ✅
Clase abstracta padre de `IfcSite`, `IfcBuilding`, `IfcBuildingStorey`, `IfcSpace`. Sirve para tipar cualquier "contenedor espacial". Ver Bloque A §3.3.

### 17. `IfcFacility` / `IfcFacilityPart` 📐 (IFC4.3+)
Ampliación de IFC4.3 para infraestructura. Padre abstracto de `IfcBuilding`, `IfcBridge`, `IfcRoad`, `IfcRailway`, `IfcMarineFacility`. Ver Bloque A §4.2.

### 18. `IfcZone` 🔧
Agrupación lógica de `IfcSpace`s con un propósito (térmica, funcional, acústica). No es `IfcSpatialStructure` — es `IfcGroup`. Se asocia mediante `IfcRelAssignsToGroup`. Pendiente decisión NEXUM (D3-04).

---

## D — Elementos físicos

### 19. `IfcProduct` ✅
Clase abstracta. Todo objeto con posición y/o geometría en el modelo. Padre tanto de `IfcSpatialElement` como de `IfcElement`. Ver Bloque A §3.3.

### 20. `IfcElement` ✅
Clase abstracta. Todo objeto físico construible. Padre de `IfcBuildingElement`, `IfcDistributionElement`, `IfcFurnishingElement`, etc.

### 21. `IfcBuildingElement` ✅
Clase abstracta de elementos de edificación: muros, slabs, puertas, ventanas, vigas, columnas, cubiertas, escaleras. FZK-Haus contiene principalmente subtipos de esta clase (ver §22-26).

### 22. `IfcWall` / `IfcWallStandardCase` ✅
Muro. `IfcWallStandardCase` (más restrictivo) requiere eje + perfil + altura. FZK-Haus tiene 13 muros, todos `IfcWallStandardCase`. Ejemplo: #15042 ('Wand-Int-ERDG-4'). Ver Bloque B §4 (caso de estudio).

### 23. `IfcSlab` ✅
Forjado, losa, suelo o cubierta plana. FZK-Haus: 4 instancias. Ejemplo #14502 (con material 'Holz', madera).

### 24. `IfcDoor` ✅
Puerta. FZK-Haus: 5 puertas (3 interiores + 2 exteriores). Siempre debe ir asociada a un `IfcOpeningElement` mediante `IfcRelFillsElement`. Ejemplo: #17468.

### 25. `IfcWindow` ✅
Ventana. FZK-Haus: 11 ventanas. Mismo patrón que `IfcDoor` (Voids + Fills).

### 26. `IfcStair`, `IfcStairFlight`, `IfcRailing` 🔧
Escaleras y barandillas. `IfcStair` es el "todo" agregado (compuesto por `IfcStairFlight`s y `IfcRailing`s mediante `IfcRelAggregates`). FZK-Haus: 1 escalera, 2 barandillas.

### 27. `IfcOpeningElement` ✅
Hueco geométrico (no es la puerta o ventana — es el "agujero" en el muro). Ejemplo FZK-Haus: #17106 ("Innentuer-1"). Modelo: `IfcWall ─Voids─► IfcOpeningElement ◄─Fills─ IfcDoor`. Ver Bloque B §1.6.

### 28. `IfcFurnishingElement` 🔧
Mobiliario. FZK-Haus no contiene mobiliario (0 instancias).

### 29. `IfcDistributionElement` 📐
Clase abstracta de elementos MEP: tuberías (`IfcFlowSegment`), codos (`IfcFlowFitting`), grifos/luces/difusores (`IfcFlowTerminal`). Cobertura amplia (50+ subtipos). FZK-Haus no contiene MEP. Lo veremos en S5·L.

---

## E — Tipos y plantillas

### 30. `IfcTypeObject` ✅
Plantilla compartida por varias instancias. Materializa la dualidad instance/type. En Revit: la familia. Conectado a instancias por `IfcRelDefinesByType`. Ver Bloque A §3.4 y Bloque B §1.3.

### 31. `IfcWallType`, `IfcDoorType`, `IfcSlabType`, etc. ✅
Subtipos concretos de `IfcTypeObject` por categoría. FZK-Haus: 2 `IfcWallType`. Ejemplo: #15234 ('Leichtbeton 102890359 240' — hormigón ligero 240mm) compartido por 5 muros.

---

## F — Propiedades y cantidades

### 32. `Pset` (`IfcPropertySet`) ✅
Conjunto de propiedades. Asociado a entidades por `IfcRelDefinesByProperties`. Convenciones:
- `Pset_*` → estándar buildingSMART (ej. `Pset_WallCommon`, `Pset_ProjectCommon`).
- `GSPset_*` → propietario Graphisoft (legacy ArchiCAD).
- `NEXUM_*` → propietario NEXUM (convención decidida en S2·X).
**Ejemplo FZK-Haus:** #100 (`'Pset_ProjectCommon'`, asociado al `IfcProject` por #105).

### 33. `Qto` (`IfcElementQuantity`) 🔧
Conjunto de cantidades (volumen, área, longitud). Mismo mecanismo que Pset pero contiene `IfcPhysicalQuantity` en lugar de `IfcProperty`. Convenciones: `Qto_WallBaseQuantities`, `Qto_DoorBaseQuantities`. Pendiente decisión NEXUM (D3B-03).

### 34. `IfcPropertySingleValue` ✅
La unidad mínima de propiedad: nombre + valor (+ unidad opcional). Empaquetada dentro de un `IfcPropertySet`. Ejemplo: `IfcPropertySingleValue('IsExternal', $, IfcBoolean(.TRUE.), $)`.

### 35. `Pset_WallCommon`, `Pset_DoorCommon`, etc. 🔧
Psets estandarizados IFC4. Listan las properties mínimas para cada tipo de elemento. **Buenas prácticas: usar siempre que existan antes de crear Psets propios.**

---

## G — Geometría y representación

### 36. `IfcLocalPlacement` / `ObjectPlacement` 📐
Sistema de coordenadas local de cada `IfcProduct`. Anidados (un muro está colocado relativo a una planta, que está colocada relativa al edificio…). Permite trasladar el modelo cambiando solo el placement raíz.

### 37. `IfcRepresentation` 📐
La geometría propiamente dicha. Cada `IfcProduct` puede tener varias representaciones (Body, Axis, FootPrint, Annotation…) según el `IfcGeometricRepresentationContext` definido en el `IfcProject`. Lo veremos en detalle en S5·L.

### 38. `IfcMaterial` / `IfcMaterialLayerSet` / `IfcMaterialProfileSet` ✅
Definición de materiales. Simple (`IfcMaterial 'Holz'`), por capas (`IfcMaterialLayerSet` para muros multicapa), o por perfil (`IfcMaterialProfileSet` para columnas/vigas). Asociado mediante `IfcRelAssociatesMaterial`. Ver Bloque B §1.5.

---

## H — Clasificación externa

### 39. `IfcClassification` / `IfcClassificationReference` 🏷️
Sistema de clasificación externo (Uniclass, OmniClass, GuBIMClass…). `IfcClassification` es el sistema; `IfcClassificationReference` es una entrada concreta. Conectado mediante `IfcRelAssociatesClassification`.
**Regla NEXUM (S2·L):** clasificar por **URI bSDD**, nunca por nombre suelto. Ver `S2L_bsdd_implementacion.md`.

### 40. `bSDD` (buildingSMART Data Dictionary) 🏷️
Servicio web de buildingSMART que aloja taxonomías y propiedades curadas. Cada entrada tiene un URI estable (`https://identifier.buildingsmart.org/uri/...`). Es el "Wikipedia controlado" del sector. Cubierto en sesión S2·L (`S2L_bsdd_implementacion.md`).

---

## Tabla resumen — qué hay en el FZK-Haus

| Término | Conteo | Línea ejemplo |
|---|---|---|
| `IfcProject` | 1 | #66 (línea 53) |
| `IfcSite` | 1 | #389 (línea 213) |
| `IfcBuilding` | 1 | #434 (línea 228) |
| `IfcBuildingStorey` | 2 | #479 (línea 249), #35065 (línea 19978) |
| `IfcSpace` | ≥6 | #20909, #21283, #21640 (líneas 11879, 12092, 12300) |
| `IfcWallStandardCase` | 13 | #15042 (línea 8643) |
| `IfcSlab` | 4 | #14502 (referenciado en #14528) |
| `IfcDoor` | 5 | #17468 |
| `IfcWindow` | 11 | — |
| `IfcStair` | 1 | — |
| `IfcRailing` | 2 | — |
| `IfcOpeningElement` | 17 | #17106 (línea 9726) |
| `IfcWallType` | 2 | #15234 (línea 8767) |
| `IfcPropertySet` | muchos | #100 'Pset_ProjectCommon' (línea 60) |
| `IfcMaterial` | varios | #14521 'Holz' (línea 8381) |
| `IfcRelAggregates` | 5 | #481 (línea 250) |
| `IfcRelContainedInSpatialStructure` | 2 | #14517 (línea 8380) |
| `IfcRelDefinesByType` | 18 | #15253 (línea 8775) |
| `IfcRelDefinesByProperties` | 482 | #105 (línea 61) |
| `IfcRelAssociatesMaterial` | 21 | #14528 (línea 8382) |
| `IfcRelVoidsElement` | 17 | #17111 (línea 9727) |
| `IfcRelFillsElement` | 16 | #17471 (línea 9946) |
| `IfcRelConnectsPathElements` | 16 | #17049 (línea 9695) |
| `IfcRelSpaceBoundary` | 81 | #76511 (línea 42816) |
| `IfcRelAssociatesClassification` | 1 | #21173 (línea 12036) |

---

## Convenciones NEXUM cubiertas en S3·L

| Convención | Decidida en | Aplica a |
|---|---|---|
| `StoreIFCGUID=true` en export Revit | S2·L | Estabilidad de `GlobalId` |
| Clasificar por URI bSDD, no por nombre | S2·L | `IfcClassificationReference` |
| Plantilla `NEXUM_CanCabassa.rte` unificada | S2·L (BEP §4.1.7) | Familias = `IfcTypeObject` |
| Psets propios prefijo `NEXUM_<disciplina>_<concepto>` | S2·X | `IfcRelDefinesByProperties` |
| `_NEXUM_metadata` con 8 claves mínimas | S2·X | Convención de Pset técnico |

---

## Errores frecuentes de terminología

| Confusión | Aclaración |
|---|---|
| "Property" como atributo de entidad | Es un PropertySet asociado por `IfcRelDefinesByProperties`. La entidad NO tiene la property directamente. |
| `IfcOpeningElement` = "puerta" | No. Es el HUECO. La puerta es `IfcDoor`. Patrón: Voids → OpeningElement ← Fills. |
| `IfcSite` = "país" o "región" | No. Es un sitio físico con coordenadas. Un proyecto puede tener varios `IfcSite`s. |
| "GUID" = identificador interno del fichero | No. GUID = `GlobalId` (estable, base64-22, mundial). Identificador interno = `#NN` (cambia entre exports). |
| `IfcWall` = "todos los muros del fichero" | No. `IfcWall` es una entidad concreta del schema (una instancia). El conjunto de muros es la lista de todas las entidades de tipo `IfcWall` o subtipos. |

---

## 4. Trazabilidad

- **Sesión origen:** S3·L (lunes 25/05/2026)
- **Documentos hermanos:**
  - Bloque A: `S3L_ifc_jerarquia.md` v0.1
  - Bloque B: `S3L_ifc_relaciones.md` v0.1
- **Script asociado:** `scripts/s3l_ifc_inspect.py` v0.1 (Nivel 2 — pseudocódigo)
- **Modelo de referencia:** `AC20-FZK-Haus.ifc` (KIT/IAI, SHA-256 `70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994`)
- **Cierre S3·L:** pendiente commit conjunto tras este bloque.
