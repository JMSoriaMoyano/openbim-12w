# S3·X — Dudas técnicas resueltas (Bloque B)

**Sesión:** S3·X · semana 3, miércoles (ejecutada en diferido el 28/05/2026)
**Versión:** v1.0
**Estado:** Dictámenes operativos NEXUM. 4 dudas cerradas; 6 diferidas a S4·L / S5·L / S6·L / S7·L.

## Cómo leer este documento

Cada duda sigue el patrón:

1. **Pregunta** literal tal como quedó en `Dudas.md` tras S3·L.
2. **Respuesta corta** — la decisión operativa NEXUM en 1–2 frases.
3. **Fundamento técnico** — referencia al schema IFC4 + evidencia del FZK-Haus.
4. **Consecuencias prácticas** — qué cambia en BEP, EIR, script, plantilla, E3.

Toda referencia "(FZK-Haus)" es **verificada** mediante ejecución de `scripts/s3l_ifc_inspect.py` contra `models/samples/_local/AC20-FZK-Haus.ifc` (SHA-256 70cc8ff2…).

---

## D3-01 · IfcWall vs IfcWallStandardCase: ¿cuál usar y cuándo?

### Pregunta original

> En FZK-Haus contamos 13 `IfcWallStandardCase`. ¿Qué pasa si en un proyecto NEXUM exportado desde Revit aparece `IfcWall` "a secas"? ¿Es lo mismo? ¿Hay que normalizar?

### Respuesta corta NEXUM

**`IfcWall` es la clase, `IfcWallStandardCase` es un subtipo restringido.** Las consultas del CDE NEXUM deben filtrar **siempre por `IfcWall` incluyendo subtipos** (comportamiento por defecto de `by_type()` en IfcOpenShell). La distinción solo importa en exportación: el BEP exige `IfcWallStandardCase` cuando la pared cumpla las restricciones; en caso contrario, `IfcWall`.

### Fundamento técnico

En el schema IFC4, `IfcWallStandardCase` es un subtipo de `IfcWall` con tres restricciones geométricas y semánticas (definidas en la página oficial del schema, [IfcWallStandardCase — buildingSMART](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifcsharedbldgelements/lexical/ifcwallstandardcase.htm)):

1. El **axis** (eje) debe ser una `IfcCurve2D` recta o curva simple.
2. El **body** debe ser una extrusión **a lo largo del eje**, con sección constante.
3. Debe tener un `IfcMaterialLayerSetUsage` asignado vía `IfcRelAssociatesMaterial`.

Si la pared incumple **cualquiera** de los tres puntos (p. ej. una pared con offset variable, una pared inclinada, una pared sin layer set definido), el exportador **debe** emitir `IfcWall` y NO `IfcWallStandardCase`. Esto es un requisito del schema, no una recomendación.

En IFC4.3, la clase `IfcWallStandardCase` queda **DEPRECATED** en favor de `IfcWall` con `PredefinedType` apropiado. Pero en IFC4 (nuestra base), la distinción sigue vigente y los exportadores la usan activamente.

### Evidencia FZK-Haus

```
IfcWall (model.by_type("IfcWall"))            = 13   ← incluye subtipos
IfcWall sin subtipos                           =  0   ← cero paredes "puras"
IfcWallStandardCase (estricto)                 = 13   ← todas son StandardCase
```

Las 13 paredes son todas `IfcWallStandardCase`. ArchiCAD 20 las exportó así porque cumplen las 3 restricciones (extrusión recta + layer set vía `Pset_WallCommon` + material definido).

### Comportamiento de `model.by_type()` en IfcOpenShell

Por defecto **incluye subtipos**. Por eso `by_type("IfcWall")` devuelve también todas las `IfcWallStandardCase`. Para forzar solo la clase pura: `model.by_type("IfcWall", include_subtypes=False)`.

### Consecuencias prácticas

| Ámbito | Regla NEXUM |
|---|---|
| **Consultas BIM en CDE** | Filtrar por `IfcWall` con subtipos (= por defecto). Capturas TODO. |
| **BEP** | Exigir al equipo que exporte como `IfcWallStandardCase` salvo justificación geométrica. |
| **EIR** | Mencionar que IFC4 distingue 4 subtipos relevantes: `IfcWall`, `IfcWallStandardCase`, `IfcWallElementedCase` (muros con paneles tipo cortina), `IfcCurtainWall` (que **no** es subtipo de IfcWall sino clase independiente). |
| **Script `s3l_ifc_inspect.py`** | Mantener ambos en `PHYSICAL_TYPES`: `IfcWall` (todo) + `IfcWallStandardCase` (subset). Permite diagnosticar paredes "no-Standard" mediante `len(IfcWall) - len(IfcWallStandardCase)`. |
| **Validación E3** | Exigir que el conteo `IfcWall - IfcWallStandardCase == 0` en FZK-Haus (lo verifica la tabla EXPECTED_COUNTS_FZK). |

### Aviso para Can Cabassa (PBSA)

PBSA típico de Revit: paredes con desnivel (muros inclinados en escaleras de evacuación), paredes con apertura no rectangular, paredes con material no layered → todas se exportan como `IfcWall` no-Standard. Detectarlas a tiempo con la consulta `by_type("IfcWall", include_subtypes=False)` (debe ser **>0** si hay alguna no-Standard).

---

## D3B-02 · IfcRelSpaceBoundary: 1st level vs 2nd level

### Pregunta original

> En FZK-Haus hay 81 `IfcRelSpaceBoundary`. ¿Son 1st o 2nd level? ¿Qué exige NEXUM para Can Cabassa (cálculo térmico, EnerPHit)? ¿Cómo lo validamos?

### Respuesta corta NEXUM

NEXUM exige **2nd level boundaries** para todo activo con simulación energética (Senior Living, PBSA, oficinas con certificación BREEAM/LEED). Para activos solo dimensionales (logística, datacenter shell), basta con 1st level. **Validación obligatoria**: ningún boundary puede tener `RelatedBuildingElement = NULL` excepto cuando `PhysicalOrVirtualBoundary = VIRTUAL`.

### Fundamento técnico — los dos niveles

`IfcRelSpaceBoundary` define la conexión entre un `IfcSpace` y un `IfcBuildingElement` (un muro, un forjado, una ventana). Los dos niveles vienen del **IFC Coordination View** y de los MVD de transferencia para análisis térmico ([SpaceBoundary 2nd level — buildingSMART](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifcproductextension/lexical/ifcrelspaceboundary.htm)):

| Aspecto | 1st level | 2nd level |
|---|---|---|
| **Granularidad** | Una boundary por par (Space, Element) | Una boundary **por cara visible** del par |
| **Subdivisiones** | No subdivide cuando hay otro espacio adyacente | **Subdivide** según las caras compartidas |
| **Apto para** | Cálculo de áreas, navegación 2D | **Simulación térmica, acústica, energética** |
| **Subtipos schema IFC4** | `IfcRelSpaceBoundary1stLevel` | `IfcRelSpaceBoundary2ndLevel` |
| **Atributo distintivo** | Sin `ParentBoundary` ni `CorrespondingBoundary` | Tiene `ParentBoundary` (jerarquía) y `CorrespondingBoundary` (boundary "espejo" del espacio vecino) |
| **Códigos buildingSMART** | "1" | "2a" (cara externa del par) y "2b" (cara interna) |

### Evidencia FZK-Haus — sorpresa importante

```
IfcRelSpaceBoundary (clase base)               = 81
IfcRelSpaceBoundary1stLevel (estricto)         =  0
IfcRelSpaceBoundary2ndLevel (estricto)         =  0
```

**Las 81 boundaries son de la clase base, NO de los subtipos.** Sin embargo:

```
Name de las 81:        '2ndLevel'  (las 81)
Description de las 81: '2a'        (las 81)
```

Esto significa que ArchiCAD 20 **declaró semánticamente** las boundaries como 2nd level vía Name/Description, **pero no usó los subtipos `IfcRelSpaceBoundary2ndLevel`**. ¿Por qué? Porque en 2016 los exportadores que generaban IFC4 vinieron de un pipeline IFC2x3 donde esos subtipos no existían (se introdujeron en IFC4 ADD1). Es un caso clásico de "IFC4 nominal, semántica IFC2x3+Extension".

### Implicación para validación NEXUM

Una validación robusta debe comprobar **dos vías**:

```python
def is_2nd_level(sb):
    # Vía 1: subtipo formal IFC4 ADD1+
    if sb.is_a("IfcRelSpaceBoundary2ndLevel"):
        return True
    # Vía 2: convención semántica (FZK-Haus, ArchiCAD 20)
    if sb.Name == "2ndLevel" or (sb.Description and "2" in sb.Description):
        return True
    return False
```

Esta es **D6-XX** (la levantaremos en S6·L como deuda técnica de validación) y se implementará como regla IDS en S7·L.

### Reparto de las 81 boundaries en FZK-Haus

| Atributo | Distribución |
|---|---|
| **PhysicalOrVirtualBoundary** | 70 PHYSICAL · 11 VIRTUAL |
| **InternalOrExternalBoundary** | 40 INTERNAL · 41 EXTERNAL |
| **RelatedBuildingElement** | 28 IfcWallStandardCase · 23 IfcSlab · 11 IfcWindow · 8 IfcDoor · 6 IfcVirtualElement · 5 NULL |

Lectura técnica:
- **11 VIRTUAL** + **6 IfcVirtualElement** + **5 NULL** = ~22 boundaries "fantasma" (los espacios se subdividen en zonas pero sin elemento físico). Esto es **correcto** en 2nd level (es el "límite imaginario" entre, por ejemplo, salón y comedor en un loft).
- **40 INTERNAL = 41 EXTERNAL** equilibrio razonable para un chalet con 7 estancias.

### Consecuencias prácticas

| Ámbito | Regla NEXUM |
|---|---|
| **BEP** (sección 4.1.7 plantilla) | Para Senior Living / PBSA / oficinas: **exigir** "IFC Space boundaries: 2nd level" en el exportador (ArchiCAD) o "Export boundaries: 2nd Level" (Revit IFC Exporter). Para logística / datacenter: 1st level suficiente. |
| **EIR** (LOIN E5) | Añadir requisito de información: "Para cada `IfcSpace`, deben existir boundaries que cubran el 100 % de su perímetro y techo, agregando 2a + 2b cuando el espacio es interno." |
| **Validación IDS (S7·L)** | Regla "every IfcSpace must have ≥1 IfcRelSpaceBoundary with `(Name='2ndLevel' OR is_a IfcRelSpaceBoundary2ndLevel)`". |
| **Script `s3l_ifc_inspect.py`** | Añadir en S4·L una función `count_boundaries_by_level()` que use la heurística doble (subtipo + Name/Description). |
| **E3** | Demostrar las 81 boundaries del FZK-Haus, identificar el 2nd level por Name, listar el reparto por tipo de elemento. La tabla de evidencia ya está en este documento. |

---

## D3-02 · IFC4 vs IFC4.3 para Can Cabassa

### Pregunta original

> Can Cabassa es residencial (PBSA evolución a Coliving). ¿Tenemos que usar IFC4.3 o nos quedamos en IFC4? Hay infraestructura urbana en la parcela (acera, alcorque, acometida).

### Respuesta corta NEXUM

**IFC4 (IFC4 ADD2 TC1) como baseline para Can Cabassa y todos los activos NEXUM Living Alternativo.** IFC4.3 solo entra cuando el activo sea **principalmente infraestructura** (datacenter con redes, logístico con viales internos) o cuando el cliente lo exija explícitamente. Para Can Cabassa, IFC4 cubre el 100 % de los entregables.

### Fundamento técnico

#### Qué añade IFC4.3 sobre IFC4

IFC4.3 (publicado abril 2024, ISO 16739-1:2024) añade dominios de **infraestructura horizontal**:

- `IfcRail`, `IfcRailway` — ferrocarril
- `IfcRoad`, `IfcRoadElement`, `IfcRoadFurniture` — viales
- `IfcMarineFacility`, `IfcMarinePart` — puertos
- `IfcBridge`, `IfcBridgePart` — puentes
- Refinamiento de `IfcGeographicElement`, georreferenciación con `IfcMapConversion`
- Refactor de `IfcLinearPositioning` para alineaciones

Lo que NO añade para edificación: el dominio de building elements (walls, slabs, windows, doors…) sigue siendo el mismo. Un PBSA modelado en IFC4 es bit a bit equivalente en IFC4.3.

#### Estado del soporte 2026

| Stack | IFC4 | IFC4.3 |
|---|---|---|
| **Revit IFC Exporter** | Sólido desde 2018 | Soporte parcial desde 2024.1, inestable para casos no-infra |
| **ArchiCAD** | Sólido desde v20 (2016) | Soporte oficial desde v27 (2023) pero limitado a building |
| **IfcOpenShell** | Sólido | Funcional desde 0.7.x, todavía con bugs reportados en geom |
| **bSDD** | Diccionarios estables | Diccionarios estables (los conceptos no cambian) |
| **Validadores oficiales bSI** | OK | OK |
| **IDS spec** | v1.0 estable | v1.0 estable (independiente del schema) |

#### Por qué IFC4 para Can Cabassa

1. **Activo edificatorio, no infraestructural.** Acera + alcorque + acometida = `IfcSite` con `IfcGeographicElement` (existe en IFC4). No necesitamos `IfcRoad`.
2. **Pipeline más maduro.** Revit + IfcOpenShell + ifctester en IFC4 es un workflow probado por miles de proyectos. En IFC4.3, los reportes de issues en GitHub de IfcOpenShell son aún frecuentes en 2026.
3. **Compatibilidad con bSDD.** Las clasificaciones que vamos a usar (Uniclass, OmniClass, MasterFormat) están publicadas para IFC4. Las versiones IFC4.3 existen pero algunas siguen marcadas como "draft".
4. **Validación regulatoria.** Spanish CTE y los códigos de simulación energética (LIDER/CALENER, HULC) consumen IFC4 sin problemas. IFC4.3 todavía no está reconocido oficialmente por la administración española.

#### Cuándo cambiar a IFC4.3 en NEXUM

| Activo | Schema | Razón |
|---|---|---|
| **Can Cabassa** (PBSA → Coliving) | **IFC4** | Edificatorio puro |
| **Senior Living** estándar | **IFC4** | Edificatorio + parcela pequeña |
| **Coliving urbano** (rooftop, parcela < 2000 m²) | **IFC4** | Edificatorio |
| **Logístico** con viales internos > 200 m | IFC4.3 (evaluar) | Requiere `IfcRoad` para naves > 50.000 m² |
| **Datacenter** Tier IV con red eléctrica propia | IFC4.3 (evaluar) | Requiere alineaciones para canalizaciones |
| **Cliente exige IFC4.3** | IFC4.3 | Cláusula contractual prevalece |

### Evidencia FZK-Haus

FZK-Haus declara `FILE_SCHEMA(('IFC4'))` en el HEADER. Es nuestro modelo de referencia oficial y nos cubre TODA la formación de las 12 semanas. El día que necesitemos un caso IFC4.3, descargaremos un sample equivalente (probablemente `RST_basic_sample_project` de Revit o `IfcOpenInfra-Bridge-01.ifc`).

### Consecuencias prácticas

| Ámbito | Decisión |
|---|---|
| **BEP** | Sección 4.1.4: "Schema IFC: IFC4 ADD2 TC1 (ISO 16739-1:2018). Schema IFC4.3 reservado para activos infraestructurales tras evaluación caso a caso." |
| **EIR** | Anclar todos los LOIN al schema IFC4. Citar IFC4.3 solo como referencia de evolución futura. |
| **Plantilla unificada NEXUM** | Mantener IFC4 como hard-coded en la sección de Schema. |
| **Script `s3l_ifc_inspect.py`** | El SHA-256 verifica un IFC4. Cuando llegue un IFC4.3, se añadirá una rama condicional o un script separado. |
| **E3** | Confirmar `model.schema == "IFC4"` en el HEADER. Ya lo hace `report_header()`. |
| **bSDD** | Usar diccionarios estables IFC4 (Uniclass 2015, etc.). |

### Deuda técnica abierta

- **D6-XX (S6·L)**: Cuando trabajemos en BREEAM España v6+, comprobar si el módulo de transporte (Mat 03) acepta IFC4 o exige IFC4.3.
- **D11-XX (S11·L)**: CDE Speckle/Bonsai: confirmar que ambos publican el schema declarado sin perder fidelidad.

---

## D3B-01 · Psets mínimos obligatorios NEXUM

### Pregunta original

> Para E3 hay que demostrar "calidad informacional" en los elementos. ¿Qué Psets son obligatorios en una pared, una losa, una ventana, una puerta, un espacio? ¿Qué BaseQuantities? ¿Cómo lo validamos?

### Respuesta corta NEXUM

Solo Psets **`Pset_*Common`** del estándar buildingSMART son obligatorios en NEXUM. Los Psets del fabricante (`AC_Pset_*`, `Revit Type*`, etc.) son **informativos**. Cada `IfcBuildingElement` debe llevar adicionalmente `BaseQuantities` (`Qto_*BaseQuantities`). Los Psets de proyecto (`Pset_NEXUM_*`) se definen en el BEP y se validan vía IDS.

### Fundamento técnico — taxonomía Pset

El schema IFC4 distingue:

1. **Psets estándar `Pset_*`** publicados por buildingSMART como anexo del schema. Nombres, claves y tipos están fijados. Lista oficial: [Property Sets — buildingSMART](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/annex/annex-b/alphabeticalorder_psets.htm).
2. **BaseQuantities `Qto_*`** también estándar, pero solo cantidades dimensionales (longitud, área, volumen, masa).
3. **Psets de proyecto `Pset_<Org>_*`** definidos por el equipo BIM en el BEP. Los nuestros: `Pset_NEXUM_*` (definiremos en S4·L).
4. **Psets del fabricante `AC_*`, `Revit*`, `Tekla_*`, …** específicos del autoring tool. **NO** transferibles a NEXUM porque cambian al cambiar de software.

### Psets mínimos NEXUM por clase

Lista derivada de Pset_*Common del IFC4 y refinada con criterio NEXUM (subset de los obligatorios bSI):

#### `IfcWall` / `IfcWallStandardCase`

| Pset / Property | Por qué |
|---|---|
| `Pset_WallCommon.Reference` | Trazabilidad código de pared |
| `Pset_WallCommon.LoadBearing` | Cálculo estructural |
| `Pset_WallCommon.IsExternal` | Cálculo térmico / acústico |
| `Pset_WallCommon.FireRating` | Cumplimiento CTE-SI |
| `Pset_WallCommon.AcousticRating` | Cumplimiento CTE-DB-HR |
| `Pset_WallCommon.ThermalTransmittance` | Cumplimiento CTE-DB-HE / EnerPHit |
| `Qto_WallBaseQuantities.Length` | Mediciones |
| `Qto_WallBaseQuantities.Height` | Mediciones |
| `Qto_WallBaseQuantities.Width` | Mediciones (espesor) |
| `Qto_WallBaseQuantities.GrossSideArea` | Mediciones |
| `Qto_WallBaseQuantities.NetVolume` | Mediciones |

#### `IfcSlab`

| Pset / Property | Por qué |
|---|---|
| `Pset_SlabCommon.Reference` | Trazabilidad |
| `Pset_SlabCommon.LoadBearing` | Estructura |
| `Pset_SlabCommon.IsExternal` | Cubierta vs forjado interno |
| `Pset_SlabCommon.FireRating` | CTE-SI |
| `Pset_SlabCommon.AcousticRating` | CTE-DB-HR |
| `Pset_SlabCommon.ThermalTransmittance` | CTE-DB-HE |
| `Qto_SlabBaseQuantities.GrossArea` | Mediciones |
| `Qto_SlabBaseQuantities.Perimeter` | Mediciones |
| `Qto_SlabBaseQuantities.Width` | Espesor |
| `Qto_SlabBaseQuantities.GrossVolume` | Mediciones |

#### `IfcWindow` / `IfcDoor`

| Pset / Property | Por qué |
|---|---|
| `Pset_WindowCommon.Reference` o `Pset_DoorCommon.Reference` | Código carpintería |
| `Pset_*Common.IsExternal` | Térmico |
| `Pset_*Common.FireRating` | CTE-SI |
| `Pset_*Common.ThermalTransmittance` | CTE-DB-HE |
| `Pset_*Common.AcousticRating` | CTE-DB-HR |
| `Pset_*Common.Infiltration` | Estanqueidad (HE0) |
| `Qto_WindowBaseQuantities.Width` / `Height` / `Area` | Mediciones |
| `Qto_DoorBaseQuantities.Width` / `Height` / `Area` | Mediciones |

#### `IfcSpace`

| Pset / Property | Por qué |
|---|---|
| `Pset_SpaceCommon.Reference` | Trazabilidad (debe coincidir con `Pset_SpaceOccupancyRequirements.Reference` si existe) |
| `Pset_SpaceCommon.Category` | Tipología (dormitorio, baño, etc.) — clave para LOIN |
| `Pset_SpaceCommon.PubliclyAccessible` | Accesibilidad / códigos |
| `Qto_SpaceBaseQuantities.NetFloorArea` | Programa edificable |
| `Qto_SpaceBaseQuantities.GrossFloorArea` | Mediciones |
| `Qto_SpaceBaseQuantities.NetVolume` | Climatización |
| `Qto_SpaceBaseQuantities.NetCeilingArea` | Acabados |

#### `IfcBuildingStorey`

| Pset / Property | Por qué |
|---|---|
| `Pset_BuildingStoreyCommon.EntranceLevel` | Planta de acceso |
| `Pset_BuildingStoreyCommon.AboveGround` | Sótano vs sobre rasante |
| `Pset_BuildingStoreyCommon.GrossPlanArea` | Programa |
| `Pset_BuildingStoreyCommon.NetPlanArea` | Programa |
| `Qto_BuildingStoreyBaseQuantities.GrossFloorArea` | Mediciones |

#### `IfcBuilding`

| Pset / Property | Por qué |
|---|---|
| `Pset_BuildingCommon.IsLandmarked` | Patrimonio |
| `Pset_BuildingCommon.NumberOfStoreys` | Tipología |
| `Pset_BuildingCommon.YearOfConstruction` | Antigüedad / valoración |
| `Pset_BuildingCommon.OccupancyType` | Tipología y normativa |
| `Qto_BuildingBaseQuantities.NetFloorArea` | Programa edificable total |
| `Qto_BuildingBaseQuantities.GrossFloorArea` | Mediciones brutas |

### Evidencia FZK-Haus — muro `#15042` "Wand-Int-ERDG-4"

Inspección directa con `ifcopenshell.util.element.get_psets()`:

```
[Pset_WallCommon]
  ThermalTransmittance: 1.5
  (...solo 1 propiedad — el resto faltan)

[BaseQuantities]
  Length: 4.17
  Height: 2.5
  Width: 0.24
  GrossFootprintArea: 1.0008
  (... + 5 cantidades más)

[AC_Pset_Name]          ← propietario ArchiCAD — IGNORAR
[ArchiCADProperties]    ← propietario ArchiCAD — IGNORAR (32 props)
[ArchiCADQuantities]    ← propietario ArchiCAD — IGNORAR (56 props)
```

Lectura crítica:
- FZK-Haus **no cumple los mínimos NEXUM** para muros: solo aporta `ThermalTransmittance` de los 11 que exigimos. Falta `Reference`, `LoadBearing`, `IsExternal`, `FireRating`, `AcousticRating`.
- Las 32 propiedades `ArchiCADProperties` y 56 `ArchiCADQuantities` son **ruido informacional**: específicas del fabricante, no transferibles.
- `BaseQuantities` (sin prefijo `Qto_Wall`) es una variante histórica de ArchiCAD que NEXUM debe **rechazar**: exigimos el nombre canónico `Qto_WallBaseQuantities`.

Esto justifica que NEXUM publique una IDS que rechace FZK-Haus tal cual. Es **bueno** para la formación: tenemos un modelo real con defectos típicos, no un sample perfecto.

### Consecuencias prácticas

| Ámbito | Decisión |
|---|---|
| **BEP** (sección 4.1.7) | Tabla de Psets mínimos por clase = la de arriba. Documentar como "anexo Psets v1.0". |
| **EIR** (LOIN E4–E6) | Para LOI ≥ 200: lista completa. Para LOI = 100: solo `Reference` + `IsExternal` + `Qto_*` dimensionales. |
| **Plantilla NEXUM** | Crear `Pset_NEXUM_AssetMeta` con campos: `AssetCode`, `OperatorRequirement`, `LeasingCategory` (claves de Sourcing Inverso). Lo definimos en S4·L. |
| **Validación IDS** (S7·L) | Una regla por tipo, traduciendo la tabla a XML IDS. Validador: `ifctester`. |
| **Script `s3l_ifc_inspect.py`** | Añadir en S4·L una función `check_minimum_psets(model, class_name)` que devuelva lista de elementos no conformes. |
| **E3** | Demostrar la auditoría de Psets del muro #15042. La salida es **deliberadamente** "no conforme NEXUM" — sirve como caso de no-cumplimiento para preparar S6·L y S7·L. |

### Deuda técnica abierta

- **D6-XX (S6·L)**: Definir umbral de "no conformidad" (¿cuántos elementos pueden saltarse la regla antes de rechazar el modelo entero?).
- **D7-XX (S7·L)**: Codificar todos los Psets en una IDS NEXUM v1.0.
- **D8-XX (S8·L)**: Crear `Pset_NEXUM_*` con CamelCase consistente.

---

## Síntesis · resoluciones cerradas en S3·X

| Duda | Estado | Decisión NEXUM |
|---|---|---|
| **D3-01** | Cerrada | Consultar siempre con subtipos. Exigir `IfcWallStandardCase` en exportación cuando aplique. |
| **D3-02** | Cerrada | **IFC4 (ADD2 TC1)** baseline. IFC4.3 solo para infraestructura. |
| **D3B-01** | Cerrada | Psets `Pset_*Common` + `Qto_*BaseQuantities` obligatorios. `Pset_NEXUM_*` proyecto. Vendor-specific = ruido. |
| **D3B-02** | Cerrada | 2nd level obligatorio en Living. Validación dual: subtipo + Name/Description (heurística por compatibilidad histórica). |

## Diferidas

| Duda | Aplazada a | Motivo |
|---|---|---|
| **D3-03** Export `IfcSpace` Revit | S4·L | Conceptual de lectura, encaja con lecciones IfcOpenShell |
| **D3-04** `IfcZone` Living/PBSA | S4·L | Idem |
| **D3-05** `IfcGrid` plantilla | S5·L | Tema de geometría, encaja con sesión específica |
| **D3B-03** `Qto_*BaseQuantities` mandatory | Absorbida en D3B-01 | Cubierta |
| **D3B-04** IDS bSDD URI classifications | S7·L | Tema específico IDS |
| **D3B-05** `IfcRelConnectsPathElements` Revit | S6·L | Tema de calidad de exportación |

---

## Referencias normativas usadas

1. [IfcWallStandardCase — buildingSMART IFC4 ADD2 TC1](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifcsharedbldgelements/lexical/ifcwallstandardcase.htm)
2. [IfcRelSpaceBoundary — buildingSMART IFC4 ADD2 TC1](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifcproductextension/lexical/ifcrelspaceboundary.htm)
3. [Property Sets — buildingSMART IFC4 ADD2 TC1 Annex B](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/annex/annex-b/alphabeticalorder_psets.htm)
4. ISO 16739-1:2018 — Industry Foundation Classes (IFC) for data sharing in the construction and facility management industries (IFC4 ADD2 TC1).
5. ISO 16739-1:2024 — Idem, edición revisada (IFC4.3).
6. ISO 19650-1:2018 — Information management using BIM, Part 1: Concepts and principles.

## Evidencia empírica (FZK-Haus)

Toda la evidencia citada se obtiene ejecutando:

```bash
python scripts/s3l_ifc_inspect.py
```

Y consultando el informe Markdown generado en `out/S3X_lab_run_<timestamp>.md`. Las inspecciones puntuales (Psets del muro #15042, semántica de boundaries) se realizan con scripts puntuales en `out/` que se documentarán en S4·L.
