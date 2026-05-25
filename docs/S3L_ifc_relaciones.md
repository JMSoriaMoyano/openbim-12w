# S3·L — Relaciones IFC clave (Bloque B)

**Sesión:** S3·L (semana 3, lunes) · 25/05/2026
**Schema base:** IFC4 (IFC4 ADD2 TC1)
**Modelo de referencia:** `AC20-FZK-Haus.ifc` (KIT/IAI, SHA-256 `70cc8ff2…77994`)
**Documento hermano:** `S3L_ifc_jerarquia.md` (Bloque A — conceptos previos)
**Autor:** José M. Soria · NEXUM Developments
**Versión:** 0.1

> Este documento desarrolla la idea central que ya se introdujo en Bloque A §1.3: **en IFC las relaciones son entidades de primera clase**. Si quieres entender un IFC, las 5 relaciones clave que aquí se cubren te permiten reconstruir el 90% del modelo. Las 3 relaciones secundarias cubren el 8% restante. El 2% que queda son relaciones de nicho que veremos en sesiones posteriores.

---

## 0. Inventario real del FZK-Haus

Antes de las explicaciones, **el censo real** de relaciones en el fichero de referencia, ordenado por frecuencia. Esto es el “mapa de calor” del modelo:

| # | Relación | Conteo | Importancia | Categoría |
|---|---|---|---|---|
| 1 | `IfcRelDefinesByProperties` | 482 | ⭐⭐⭐ clave | Decoración semántica |
| 2 | `IfcRelSpaceBoundary` | 81 | ⭐⭐ secundaria | Conectividad espacial |
| 3 | `IfcRelAssociatesMaterial` | 21 | ⭐⭐⭐ clave | Decoración semántica |
| 4 | `IfcRelDefinesByType` | 18 | ⭐⭐⭐ clave | Decoración por tipo |
| 5 | `IfcRelVoidsElement` | 17 | ⭐⭐⭐ clave | Composición geométrica |
| 6 | `IfcRelFillsElement` | 16 | ⭐⭐⭐ clave | Composición geométrica |
| 7 | `IfcRelConnectsPathElements` | 16 | ⭐⭐ secundaria | Conectividad física |
| 8 | `IfcRelAggregates` | 5 | ⭐⭐⭐ clave | Composición espacial |
| 9 | `IfcRelContainedInSpatialStructure` | 2 | ⭐⭐⭐ clave | Anclaje espacial |
| 10 | `IfcRelAssociatesClassification` | 1 | ⭐⭐ secundaria | Decoración por clasificación |

Algunas observaciones de partida:
- `IfcRelDefinesByProperties` domina por completo (98% son properties, casi todo lo demás se cuenta con una mano).
- Solo hay **2** `IfcRelContainedInSpatialStructure`: una por planta. Cada una arrastra decenas de elementos (línea 8380 contiene 38 muros/puertas/ventanas en una sola relación).
- Solo hay **5** `IfcRelAggregates`: las 4 aristas de la pirámide (Project→Site→Building→2 Storeys) + 1 más que aparece en la planta del altillo.
- Hay **0** `IfcRelNests` en este modelo (escaleras y puertas usan aquí decomposition por aggregates, no nests).

---

## 1. Las 5 relaciones IFC clave

### 1.1 · `IfcRelAggregates` — composición y pirámide espacial

#### Propósito

Una sola relación cubre **dos casos distintos** que conviene separar mentalmente:

1. **Pirámide espacial:** `IfcProject` → `IfcSite` → `IfcBuilding` → `IfcBuildingStorey` → `IfcSpace`
2. **Descomposición de elementos:** un compuesto como `IfcStair`, `IfcCurtainWall` o `IfcWall` con capas, se descompone en partes (`IfcStairFlight`, `IfcPlate`, `IfcMember`)

Es la relación **whole-part**.

#### Firma EXPRESS

```
IfcRelAggregates : SUBTYPE OF (IfcRelDecomposes);
   RelatingObject  : IfcObjectDefinition;        -- el todo (1)
   RelatedObjects  : SET [1:?] OF IfcObjectDefinition;  -- las partes (N)
```

#### Firma STEP

```
IFCRELAGGREGATES(GlobalId, OwnerHistory, Name, Description, RelatingObject, RelatedObjects)
```

#### Ejemplo real (FZK-Haus, línea 250)

```step
#481= IFCRELAGGREGATES('1Y0uyqfGvXQyvJl5QblObD',
                       #12,            -- OwnerHistory
                       $, $,           -- Name, Description
                       #434,           -- RelatingObject = IfcBuilding "FZK-Haus"
                       (#479, #35065)); -- RelatedObjects = [Erdgeschoss, Dachgeschoss]
```

#### Reglas

- Cardinalidad **1:N** (un padre, varios hijos).
- Un objeto puede ser hijo de **un solo** `IfcRelAggregates` (no tienes 2 padres). Sí puede ser padre de varios `IfcRelAggregates` (raramente útil).
- Los objetos relacionados deben formar **whole-part** real (no “está cerca de”).

#### Diferencia con `IfcRelContainedInSpatialStructure`

- `IfcRelAggregates`: composición “es parte de” → IfcSite es parte de IfcProject; IfcStairFlight es parte de IfcStair.
- `IfcRelContainedInSpatialStructure`: ubicación “está en” → IfcWall está en IfcBuildingStorey.

Si lo confundes, los visores tipo Solibri reportan errores como “element not contained in any spatial structure”.

---

### 1.2 · `IfcRelContainedInSpatialStructure` — anclaje de elementos en estructura espacial

#### Propósito

Conecta **elementos físicos** (muros, puertas, slabs…) con el **nivel de la pirámide espacial** donde están ubicados (típicamente `IfcBuildingStorey`, a veces `IfcSpace` o `IfcSite`).

Es lo que permite responder “¿qué hay en la planta baja?”.

#### Firma EXPRESS

```
IfcRelContainedInSpatialStructure : SUBTYPE OF (IfcRelConnects);
   RelatedElements   : SET [1:?] OF IfcProduct;            -- los elementos contenidos
   RelatingStructure : IfcSpatialElement;                  -- el contenedor
```

#### Firma STEP

```
IFCRELCONTAINEDINSPATIALSTRUCTURE(GlobalId, OwnerHistory, Name, Description, RelatedElements, RelatingStructure)
```

#### Ejemplo real (FZK-Haus, línea 8380)

```step
#14517= IFCRELCONTAINEDINSPATIALSTRUCTURE(
            '13J1BKcWxmCqHLM0nJ4nFJ',
            #12, $, $,
            (#14502, #15042, #15372, #15848, #16507, #16982, #17040, #17468,
             #18407, #18465, #18698, #19199, #19504, #20069, #20268, #20299,
             #20329, #20374, #20598, #20808, #21966, #23024, #23944, #27013,
             #27421, #27833, #28113, #31079, #31470, #31818, #32098, #32407,
             #32829, #33109, #33389, #33672, #34509, #35053),  -- 38 elementos físicos
            #479);  -- RelatingStructure = Erdgeschoss (planta baja)
```

Una sola línea conecta 38 elementos físicos a la planta baja. Eficiente.

#### Reglas

- Un `IfcElement` puede estar contenido en **solo un** `IfcRelContainedInSpatialStructure` (un muro está en una planta, no en dos).
- Si necesitas asociar un elemento a varios espacios (un muro entre dos habitaciones), eso se hace con `IfcRelSpaceBoundary` (ver §2.2), **no** con contención múltiple.

#### Confusión típica

> "El muro que separa dos habitaciones, ¿en cuál `IfcSpace` lo pongo?"

En **ninguno**. Lo pones en el `IfcBuildingStorey` (con esta relación) y luego defines su contacto con los espacios mediante `IfcRelSpaceBoundary`. La contención espacial es jerárquica (storey > spaces dentro), no se mete en cada espacio individual.

---

### 1.3 · `IfcRelDefinesByType` — decoración con tipo

#### Propósito

Conecta una o varias **instancias** (`IfcObject`, ej. `IfcWallStandardCase`) con su **tipo** (`IfcTypeObject`, ej. `IfcWallType`). Es la materialización de la dualidad instance/type que vimos en Bloque A §3.4.

#### Firma EXPRESS

```
IfcRelDefinesByType : SUBTYPE OF (IfcRelDefines);
   RelatedObjects : SET [1:?] OF IfcObject;     -- instancias
   RelatingType   : IfcTypeObject;              -- el tipo
```

#### Firma STEP

```
IFCRELDEFINESBYTYPE(GlobalId, OwnerHistory, Name, Description, RelatedObjects, RelatingType)
```

#### Ejemplo real (FZK-Haus, línea 8775)

```step
#15253= IFCRELDEFINESBYTYPE(
            '05I0_KDnzQTr7CWw5aGQVc',
            #12, $, $,
            (#15042, #17040, #18465, #18698, #20598),  -- 5 muros instancia
            #15234);                                    -- IfcWallType "Leichtbeton 102890359 240"
```

Y el tipo referenciado:

```step
#15234= IFCWALLTYPE('2AEMyYvIjlsz7LRzqYHy64',
                    #12,
                    'Leichtbeton 102890359 240',  -- Nombre del tipo
                    $, $, $,
                    (#15244,#15248,#15250, ...),  -- PropertySets del tipo
                    '8A396F22-E52B-6FDB-D1D5-6FDD2247C184',  -- tag
                    $, .NOTDEFINED.);
```

Léelo así: “Las instancias #15042, #17040, #18465, #18698, #20598 son del tipo *Muro de hormigón ligero 240mm*”.

#### Reglas

- N instancias pueden compartir 1 tipo.
- Una instancia puede tener **solo un** `IfcRelDefinesByType` (un solo tipo).
- Las properties del tipo se **heredan** por las instancias, pero la instancia puede tener properties propias que sobreescriban.

#### Convención NEXUM (decisión S2·L)

Toda exportación Revit→IFC desde la plantilla `NEXUM_CanCabassa.rte` debe garantizar que cada elemento tenga un `IfcTypeObject` asociado. **Esto se controla en el config JSON de export.** Familia Revit → `IfcTypeObject`. Instancia colocada → `IfcObject`.

---

### 1.4 · `IfcRelDefinesByProperties` — decoración con propiedades

#### Propósito

Asocia un **PropertySet (Pset)** o un **QuantitySet (Qto)** a una o varias entidades. Es la **relación más numerosa** del FZK-Haus (482 de 660 relaciones totales, 73%).

#### Firma EXPRESS

```
IfcRelDefinesByProperties : SUBTYPE OF (IfcRelDefines);
   RelatedObjects     : SET [1:?] OF IfcObjectDefinition;
   RelatingPropertyDefinition : IfcPropertySetDefinitionSelect;  -- IFC4: IfcPropertySet o IfcElementQuantity
```

#### Firma STEP

```
IFCRELDEFINESBYPROPERTIES(GlobalId, OwnerHistory, Name, Description, RelatedObjects, RelatingPropertyDefinition)
```

#### Ejemplo real (FZK-Haus, línea 61)

```step
#105= IFCRELDEFINESBYPROPERTIES(
          '03qjyUPwhxheq4OS1_H2vQ',
          #12, $, $,
          (#66),    -- RelatedObjects = [IfcProject "Projekt-FZK-Haus"]
          #100);    -- RelatingPropertyDefinition = IfcPropertySet
```

Y el PropertySet referenciado:

```step
#100= IFCPROPERTYSET('1IVqkrHLf3e9ZJ6X4EwLWx',
                    #12,
                    'Pset_ProjectCommon',         -- Nombre del Pset (estándar IFC4)
                    $,
                    (#97,#98,#99));               -- Lista de IfcPropertySingleValue
```

Léelo: “El proyecto #66 tiene asociado el PropertySet estándar `Pset_ProjectCommon` con 3 properties”.

#### Convenciones de nombre de Psets

- `Pset_*` → Psets estandarizados por buildingSMART (ej. `Pset_WallCommon`, `Pset_DoorCommon`, `Pset_ProjectCommon`). **Usa estos siempre que existan.**
- `Qto_*` → QuantitySets estandarizados (`Qto_WallBaseQuantities`, `Qto_DoorBaseQuantities`).
- `GSPset_*` → Psets propietarios de Graphisoft (legacy de ArchiCAD). En FZK-Haus aparecen aún.
- `<dominio>_*` → Psets de la organización. **Convención NEXUM: `NEXUM_<disciplina>_<concepto>`.** Ej. `NEXUM_ARQ_AcabadoSuperficial`.

#### Regla clave

Si vas a publicar propiedades a través de **IDS** (semana S7), tienen que estar dentro de un `IfcPropertySet` con nombre y `IfcPropertySingleValue` con `Name` y `NominalValue`. Sin esa estructura, los IDS no las encuentran.

---

### 1.5 · `IfcRelAssociatesMaterial` — asociación de materiales

#### Propósito

Conecta una entidad o un `IfcTypeObject` con su descripción material (un material simple, un `IfcMaterialLayerSet` multicapa, un `IfcMaterialProfile`, etc.).

#### Firma EXPRESS

```
IfcRelAssociatesMaterial : SUBTYPE OF (IfcRelAssociates);
   RelatingMaterial : IfcMaterialSelect;  -- material o estructura de materiales
```

`IfcMaterialSelect` es un *select type* (unión) que admite:
- `IfcMaterial` (material simple, ej. "Holz")
- `IfcMaterialLayerSet` (capas, ej. muro multicapa)
- `IfcMaterialLayerSetUsage` (uso de un layer set con dirección)
- `IfcMaterialProfile` / `IfcMaterialProfileSet` (perfiles, para columnas/vigas)
- `IfcMaterialConstituentSet` (constituyentes, no estratificados)
- `IfcMaterialList` (lista simple legacy IFC2x3)

#### Firma STEP

```
IFCRELASSOCIATESMATERIAL(GlobalId, OwnerHistory, Name, Description, RelatedObjects, RelatingMaterial)
```

#### Ejemplo real (FZK-Haus, línea 8382)

```step
#14528= IFCRELASSOCIATESMATERIAL(
            '0vl$m3dc3r4cgsisVLq$pk',
            #12, $, $,
            (#14502),  -- RelatedObjects = un IfcSlab
            #14521);   -- RelatingMaterial = IfcMaterial "Holz"
```

Y el material:

```step
#14521= IFCMATERIAL('Holz', $, $);   -- "Madera"
```

Léelo: "El slab #14502 está hecho de madera".

#### Buenas prácticas

- **Asocia siempre el material al `IfcTypeObject`**, no a la instancia. Así, las 13 muros del FZK-Haus heredan el material del tipo.
- Para muros multicapa, usa `IfcMaterialLayerSet` (estratos en orden) y conecta vía `IfcMaterialLayerSetUsage` para indicar **dirección** (offset desde el eje).
- Sin material asociado, la entidad es geométrica pero **incompleta semánticamente**. Validadores tipo Solibri lo señalan.

---

### 1.6 · `IfcRelVoidsElement` + `IfcRelFillsElement` — huecos y rellenos

Estas dos van juntas. Modelan el proceso real de **abrir un hueco en un muro y rellenarlo con una puerta o ventana**. Es un “sandwich” lógico de 3 entidades + 2 relaciones.

#### El patrón

```
IfcWall ────IfcRelVoidsElement────► IfcOpeningElement ◄────IfcRelFillsElement──── IfcDoor
   ▲                                      ▲                                          ▲
   │                                      │                                          │
elemento estructural               hueco geométrico                       elemento que ocupa el hueco
```

Tres entidades, dos relaciones. **El `IfcOpeningElement` es el puente.**

#### Firma EXPRESS (IfcRelVoidsElement)

```
IfcRelVoidsElement : SUBTYPE OF (IfcRelDecomposes);
   RelatingBuildingElement : IfcElement;           -- el muro/slab que recibe el hueco
   RelatedOpeningElement   : IfcFeatureElementSubtraction;  -- el hueco (IfcOpeningElement)
```

#### Firma EXPRESS (IfcRelFillsElement)

```
IfcRelFillsElement : SUBTYPE OF (IfcRelConnects);
   RelatingOpeningElement : IfcOpeningElement;     -- el hueco
   RelatedBuildingElement : IfcElement;            -- la puerta/ventana que lo rellena
```

#### Firmas STEP

```
IFCRELVOIDSELEMENT(GlobalId, OwnerHistory, Name, Description, RelatingBuildingElement, RelatedOpeningElement)
IFCRELFILLSELEMENT(GlobalId, OwnerHistory, Name, Description, RelatingOpeningElement, RelatedBuildingElement)
```

#### Ejemplo real (FZK-Haus, puerta interior #17468 en muro #17040)

```step
-- Paso 1: el muro #17040 tiene un hueco #17106
#17111= IFCRELVOIDSELEMENT('3xfqht94kMnU58M32eCFVW',
                           #12, $, $,
                           #17040,    -- el muro
                           #17106);   -- el hueco
```

```step
-- El hueco propiamente dicho
#17106= IFCOPENINGELEMENT('0LM8GvGe$G3dlW4mZ4aA9R',
                          #12,
                          'Innentuer-1',   -- "puerta interior 1"
                          $, $,
                          #17061,          -- ObjectPlacement
                          #17102,          -- Representation (geometría del hueco)
                          '15588439-428F-D00E-7BE0-1308C490A25B',
                          $);
```

```step
-- Paso 2: el hueco #17106 se rellena con la puerta #17468
#17471= IFCRELFILLSELEMENT('3vnaWpjvDV8lGdMvqp8dkG',
                           #12, $, $,
                           #17106,    -- el hueco
                           #17468);   -- la puerta IfcDoor
```

#### Por qué este patrón en lugar de "puerta dentro de muro"

Porque IFC modela el **proceso de construcción**: primero levantas el muro, luego abres el hueco, luego colocas la carpintería. Cada cosa tiene su geometría propia. Si solo tuvieses muro y puerta sin hueco, la geometría no cuadraría (faltaría el "agujero" en el muro).

#### Validación cruzada

Si encuentras:
- `IfcOpeningElement` sin `IfcRelFillsElement` → hueco sin puerta/ventana (puede ser hueco arquitectónico abierto, legítimo).
- `IfcDoor` o `IfcWindow` sin `IfcRelFillsElement` → puerta o ventana "flotante" sin muro receptor. **Error de modelo.**
- `IfcRelVoidsElement` sin su correspondiente `IfcRelFillsElement` → hueco vacío (legítimo solo si es hueco arquitectónico).

En el FZK-Haus hay 17 voids y 16 fills → **1 hueco arquitectónico sin relleno** (probablemente un pasaje abierto).

---

## 2. Las 3 relaciones secundarias

### 2.1 · `IfcRelConnectsPathElements` — conectividad física entre elementos lineales

#### Propósito

Modela cómo dos elementos lineales (muros, vigas, tuberías) **se conectan físicamente** en sus extremos o a lo largo. No es una composición — es una **junta**.

#### Firma STEP

```
IFCRELCONNECTSPATHELEMENTS(GlobalId, OwnerHistory, Name, Description, ConnectionGeometry,
                           RelatingElement, RelatedElement,
                           RelatingPriorities, RelatedPriorities,
                           RelatingConnectionType, RelatedConnectionType)
```

Los `ConnectionType` son enums: `.ATSTART.`, `.ATEND.`, `.ATPATH.`, `.NOTDEFINED.`

#### Ejemplo real (FZK-Haus, línea 9695)

```step
#17049= IFCRELCONNECTSPATHELEMENTS(
            '1vGdhxc6IUK2fPFUdKXu4r',
            #12, $, $, $,
            #17040,        -- RelatingElement (un muro)
            #15042,        -- RelatedElement (otro muro)
            (), (),         -- priorities vacías
            .ATSTART.,     -- el muro #17040 conecta en su inicio
            .ATEND.);      -- ...con el final del muro #15042
```

Léelo: “El inicio del muro #17040 conecta con el final del muro #15042”. Esto permite a las herramientas reconstruir las uniones en T, L, etc., y calcular bien las cantidades de obra (descontando solapes).

#### Uso típico

- Muros que se cruzan en esquina o T.
- Vigas que se unen a pilares.
- Tuberías que se conectan a otras tuberías (en MEP se usan más variantes).

### 2.2 · `IfcRelSpaceBoundary` — contornos de espacios

#### Propósito

Define qué elemento físico forma cada **cara de un espacio**. Crítico para análisis energético (cuántos m² de muro exterior tiene el salón) y para cálculos térmicos.

#### Firma STEP

```
IFCRELSPACEBOUNDARY(GlobalId, OwnerHistory, Name, Description,
                    RelatingSpace, RelatedBuildingElement, ConnectionGeometry,
                    PhysicalOrVirtualBoundary, InternalOrExternalBoundary)
```

#### Ejemplo real (FZK-Haus, línea 42816)

```step
#76511= IFCRELSPACEBOUNDARY(
            '0F8DHwVIWaA92A8pankadM',
            #12,
            '2ndLevel', '2a',          -- Name, Description
            #20909,                     -- RelatingSpace = "Schlafzimmer" (dormitorio)
            #15042,                     -- RelatedBuildingElement = un muro
            #76510,                     -- ConnectionGeometry
            .PHYSICAL.,                 -- es un boundary físico (no virtual)
            .INTERNAL.);                -- interno (no da al exterior)
```

#### Niveles de space boundary

- **1st level:** una cara del espacio = un elemento físico. Simple.
- **2nd level:** subdivide cuando hay cambios de material o de propiedades térmicas. El FZK-Haus usa **2nd level**, declarado en el MVD del HEADER.

El MVD declarado en el HEADER del FZK-Haus es `SpaceBoundary2ndLevelAddOnView` (ver Bloque A §6.1). Esto promete que el modelo lleva boundaries de 2º nivel correctos — útil para BEM (Building Energy Modeling).

### 2.3 · `IfcRelAssociatesClassification` — asociación a sistemas de clasificación

#### Propósito

Asocia entidades con un **sistema de clasificación externo** (Uniclass, OmniClass, GuBIMClass, etc.). Es la conexión hacia bSDD que ya vimos en S2·L.

#### Firma STEP

```
IFCRELASSOCIATESCLASSIFICATION(GlobalId, OwnerHistory, Name, Description,
                               RelatedObjects, RelatingClassification)
```

#### Ejemplo real (FZK-Haus, línea 12036)

```step
#21173= IFCRELASSOCIATESCLASSIFICATION(
            '3b9H1tB0QEK36vByFDaPVw',
            #12,
            'AC Zone Category',  -- categoría ArchiCAD
            $,
            (#20909, #21283, #21640, #33774, #34191, #34763, #76214),  -- 7 espacios
            #21169);              -- referencia al IfcClassificationReference
```

#### Convención NEXUM (S2·L · D-01)

Toda asociación de clasificación debe ir por **URI bSDD**, no por nombre. El ejemplo anterior es legacy ArchiCAD y no cumple. La forma correcta IFC4 sería:

```step
#21169= IFCCLASSIFICATIONREFERENCE(
            'https://identifier.buildingsmart.org/uri/gubim/gubim/1/class/EE-XX-XX',  -- URI bSDD
            'EE-XX-XX',                -- código
            'Zona habitable',           -- nombre
            $);                         -- referenced source (legacy)
```

La regla NEXUM (decisión S2·L documentada en `S2L_bsdd_implementacion.md`): **clasificar por URI bSDD, nunca por nombre suelto**.

---

## 3. Relaciones no cubiertas (referencia rápida)

Otras relaciones que existen en IFC pero no están en el FZK-Haus o no son frecuentes en edificación residencial. Se cubren en sesiones posteriores:

| Relación | Cuándo aparece | Sesión |
|---|---|---|
| `IfcRelNests` | Composición ordenada (puertas, ventanas con partes ordenadas) | S4·L |
| `IfcRelAssignsToGroup` | Agrupaciones lógicas (sistemas MEP, fases constructivas) | S5·L |
| `IfcRelAssignsToProcess` | Asignación a tareas (4D planning) | S9 o futura |
| `IfcRelInterferesElements` | Detección de interferencias (clash) | S6·L (validación) |
| `IfcRelCoversBldgElements` | Coverings sobre building elements | S5·X |
| `IfcRelConnectsPortToElement` | Conexión de puertos MEP (flow ports) | S5–S6 (MEP) |
| `IfcRelReferencedInSpatialStructure` | Referencias secundarias (ej. ejes que cubren varias plantas) | S4·X |

---

## 4. Caso de estudio: el muro #15042 visto desde todas sus relaciones

El muro `#15042` (`IfcWallStandardCase`, nombre `Wand-Int-ERDG-4`) es perfecto para ver cómo **una misma entidad participa en múltiples relaciones simultáneamente**. Mapa completo:

```
#15042 IfcWallStandardCase 'Wand-Int-ERDG-4'
   │
   ├─── #14517 IfcRelContainedInSpatialStructure ─► #479 IfcBuildingStorey 'Erdgeschoss'
   │         (está contenido en la planta baja)
   │
   ├─── #15253 IfcRelDefinesByType ─► #15234 IfcWallType 'Leichtbeton 102890359 240'
   │         (es del tipo "muro hormigón ligero 240mm")
   │
   ├─── #15074 IfcRelAssociatesMaterial ─► IfcMaterial (o LayerSet)
   │         (su material está definido)
   │
   ├─── #15xxx IfcRelDefinesByProperties ─► Pset_WallCommon (y otros)
   │         (lleva PropertySets con datos térmicos, fuego, etc.)
   │
   ├─── #17049 IfcRelConnectsPathElements ─► #17040 (otro muro)
   │         (su final conecta con el inicio de otro muro)
   │
   ├─── #76511 IfcRelSpaceBoundary ─► #20909 IfcSpace 'Schlafzimmer'
   │         (forma una cara del dormitorio)
   │
   └─── (geometría propia: ObjectPlacement #14983, Representation #15037)
```

**Cinco relaciones distintas, todas pegadas al mismo muro.** Esto es lo que hace a IFC tan potente y, a la vez, tan complejo de leer. Cuando lees el `IfcWall #15042` en el fichero, solo ves la línea con sus atributos básicos. **Toda la riqueza semántica está en las relaciones que apuntan hacia él.**

---

## 5. Patrón general para "leer" un IFC

Con las 5 relaciones clave + 3 secundarias, el flujo mental para entender un modelo es:

1. **Localiza `IfcProject`** (único en el fichero). Es el ancla.
2. **Recorre la pirámide espacial** siguiendo los `IfcRelAggregates` desde `IfcProject` hasta los `IfcSpace`s.
3. **Para cada `IfcBuildingStorey`**, busca el `IfcRelContainedInSpatialStructure` que apunta a ella → ahí tienes los elementos físicos.
4. **Para cada elemento físico**, busca:
   - `IfcRelDefinesByType` → qué tipo es
   - `IfcRelDefinesByProperties` → sus properties
   - `IfcRelAssociatesMaterial` → su material
   - `IfcRelVoidsElement` / `IfcRelFillsElement` → si tiene huecos/rellenos
5. **Para espacios**, busca `IfcRelSpaceBoundary` → qué los delimita.
6. **Para clasificación**, busca `IfcRelAssociatesClassification` → en qué taxonomía está.

Este flujo se materializa en el script `scripts/s3l_ifc_inspect.py` (pseudocódigo, Nivel 2, Bloque C).

---

## 6. Errores frecuentes en el manejo de relaciones

### 6.1 · Buscar properties como atributos directos de la entidad

**Antipatrón:**
```python
wall.Pset_WallCommon.IsExternal  # NO funciona en IFC puro
```

**Correcto (mental):**
```
buscar IfcRelDefinesByProperties
  donde RelatedObjects contenga wall
  y RelatingPropertyDefinition.Name == 'Pset_WallCommon'
  → leer IfcPropertySingleValue 'IsExternal' dentro
```

IfcOpenShell expone helpers como `ifcopenshell.util.element.get_psets(wall)` que esconden esto, pero el modelo subyacente sigue siendo el patrón de arriba.

### 6.2 · Confundir `IfcRelAggregates` con `IfcRelContainedInSpatialStructure`

Ya cubierto en §1.1 y §1.2. **Mnemotécnica:**
- `Aggregates` = "es parte de" (whole-part).
- `Contained` = "está físicamente en" (host-content).

### 6.3 · Olvidar que las relaciones son entidades

Las relaciones tienen `GlobalId`, `OwnerHistory`, `Name`, `Description`. Puedes consultarlas, validarlas, y reportar sobre ellas. Un IDS puede comprobar que toda `IfcDoor` tenga un `IfcRelFillsElement` apuntando hacia un `IfcOpeningElement`. Eso se hace contra las relaciones, no contra las puertas directamente.

### 6.4 · Asumir que IfcOpeningElement es "una puerta"

No. `IfcOpeningElement` es **el hueco geométrico**. La puerta es `IfcDoor`. La conexión es `IfcRelFillsElement`. Tres entidades distintas, no una.

### 6.5 · Materiales asignados a la instancia, no al tipo

Asignar `IfcRelAssociatesMaterial` a cada `IfcWall` individual produce 13 relaciones donde bastaría con 1 (al `IfcWallType`). Genera modelos más pesados y propensos a inconsistencias.

---

## 7. Dudas pendientes

| Id | Tema | Acción | Resolver en |
|---|---|---|---|
| D3B-01 | ¿Qué Psets estandarizados IFC4 vamos a exigir como mínimo en NEXUM (Pset_WallCommon, Pset_DoorCommon, etc.)? | Listar en BEP §4.1.6 | S3·X |
| D3B-02 | ¿Vamos a usar `IfcRelSpaceBoundary` 1st o 2nd level para BEM en Can Cabassa? | Decidir según herramienta destino (Cype, DesignBuilder, etc.) | S5·L o S6·L |
| D3B-03 | ¿Convención NEXUM para QtoBase: exigir `Qto_WallBaseQuantities` y `Qto_DoorBaseQuantities` siempre? | Confirmar en plantilla Revit | S3·X |
| D3B-04 | ¿`IfcRelAssociatesClassification` con URI bSDD se valida con IDS? | Definir IDS específico | S7·L |
| D3B-05 | ¿`IfcRelConnectsPathElements` se exporta desde Revit automáticamente o requiere configuración? | Investigar en S2X_lectura_comentada_revit_config | S3·X |

---

## 8. Trazabilidad

- **Sesión origen:** S3·L (lunes 25/05/2026, mañana)
- **Documento hermano (previo):** `S3L_ifc_jerarquia.md` v0.1
- **Documento hermano (siguiente):** `S3L_ifc_glosario.md` v0.1 (Bloque C, en preparación)
- **Modelo de referencia:** `AC20-FZK-Haus.ifc`, SHA-256 `70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994`
- **Líneas STEP citadas (verificables abriendo el .ifc en VS Code):**
  - `#15042` IfcWallStandardCase — línea 8643
  - `#15234` IfcWallType — línea 8767
  - `#15253` IfcRelDefinesByType — línea 8775
  - `#100` IfcPropertySet `Pset_ProjectCommon` — línea 60
  - `#105` IfcRelDefinesByProperties — línea 61
  - `#14521` IfcMaterial 'Holz' — línea 8381
  - `#14528` IfcRelAssociatesMaterial — línea 8382
  - `#17106` IfcOpeningElement — línea 9726
  - `#17111` IfcRelVoidsElement — línea 9727
  - `#17471` IfcRelFillsElement — línea 9946
  - `#17049` IfcRelConnectsPathElements — línea 9695
  - `#76511` IfcRelSpaceBoundary — línea 42816
  - `#21173` IfcRelAssociatesClassification — línea 12036
- **Cierre S3·L (este doc):** pendiente commit tras Bloque C
