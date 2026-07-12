# Audit Report · variante asbuilt

> Generado el 2026-06-17T17:25:16.624929+00:00 por el motor `quality_engine 0.2.0-s6x`.

## 1. Metadatos de auditoría

| Campo | Valor |
|---|---|
| Variante EIR | `asbuilt` |
| Versión EIR | `0.2` |
| Fuente EIR | `asbuilt@0.2` |
| YAMLs usados | `PBSA_v0.2_comun.yaml, PBSA_v0.2_asbuilt.yaml` |
| Modelo IFC | `AC20-FZK-Haus_authored.ifc` |
| SHA-256 modelo | `c8a16f3f63b0e47160b4cec38b7ab85813d9d1dd9fb14a2538806960ca4ad175` |
| Schema modelo | `IFC4` |
| Backends | `ids_xml, yaml_python` |
| Threshold pass | 95.0% |
| Threshold partial | 60.0% |
| Motor | `quality_engine 0.2.0-s6x` |

## 2. Resumen global

| Métrica | Valor |
|---|---|
| `total` | 33 |
| `applicable` | 32 |
| `pass` | 15 |
| `fail` | 16 |
| `partial` | 1 |
| `not_applicable` | 1 |
| `error` | 0 |
| `pct_pass` | **46.88%** |

## 3. Distribución por backend

| Backend | Total | Pass | Fail | Partial | N/A | Error |
|---|---|---|---|---|---|---|
| `ids_xml` | 7 | 4 | 2 | 1 | 0 | 0 |
| `yaml_python` | 26 | 11 | 14 | 0 | 1 | 0 |

## 4. Distribución por dimensión (ISO 19650-2)

| Dim | Nombre | Total | Pass | Fail | Partial | N/A | Pct |
|---|---|---|---|---|---|---|---|
| D1 | Modelo | 7 | 6 | 1 | 0 | 0 | 85.7% |
| D2 | Propiedades | 19 | 4 | 14 | 1 | 0 | 21.1% |
| D3 | Relaciones | 3 | 3 | 0 | 0 | 0 | 100.0% |
| D5 | Unidades | 3 | 2 | 0 | 0 | 1 | 100.0% |
| D6 | Clasificación | 1 | 0 | 1 | 0 | 0 | 0.0% |

## 5. Detalle por check

Tabla de resumen rápido (ordenada por dimensión, luego check_id):

| check_id | Dim | Backend | Status | Score | Pass≥ | Partial≥ | Mensaje |
|---|---|---|---|---|---|---|---|
| `C-M-01` | D1 | `yaml_python` | ✓ PASS | 100.00% | 100% | — | FILE_SCHEMA=IFC4 coincide con esperado IFC4. |
| `C-M-02` | D1 | `yaml_python` | ✓ PASS | 100.00% | 100% | — | Coherente: header=IFC4, runtime=IFC4, esperado=IFC4. |
| `C-M-03` | D1 | `ids_xml` | ✓ PASS | 100.00% | 95% | 60% | IDS spec 'C-M-03' PASS · 1/1 entidades cumplen (100%). |
| `C-M-04` | D1 | `ids_xml` | ✓ PASS | 100.00% | 95% | 60% | IDS spec 'C-M-04' PASS · 1/1 entidades cumplen (100%). |
| `C-M-05` | D1 | `ids_xml` | ✓ PASS | 100.00% | 95% | 60% | IDS spec 'C-M-05' PASS · 1/1 entidades cumplen (100%). |
| `C-M-06` | D1 | `ids_xml` | ✓ PASS | 100.00% | 95% | 60% | IDS spec 'C-M-06' PASS · 2/2 entidades cumplen (100%). |
| `STR.MVD.ReferenceView` | D1 | `yaml_python` | ✗ FAIL | — | 100% | — | Legacy structural check_mvd_compliance → fail |
| `C-P-01` | D2 | `ids_xml` | ✗ FAIL | 0.00% | 95% | 60% | IDS spec 'C-P-01' FAIL · 0/1 entidades cumplen (0%). |
| `C-P-02` | D2 | `ids_xml` | ✗ FAIL | 0.00% | 95% | 60% | IDS spec 'C-P-02' FAIL · 0/4 entidades cumplen (0%). |
| `C-P-03` | D2 | `ids_xml` | ◐ PARTIAL | 60.00% | 95% | 60% | IDS spec 'C-P-03' PARTIAL · 3/5 entidades cumplen (60%). |
| `H3.DOOR.FireRating` | D2 | `yaml_python` | ✓ PASS | 100.00% | 95% | 60% | 5/5 instancias de IfcDoor declaran Pset_DoorCommon.FireRating (100.0%). |
| `H3.SLAB.FireRating` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/4 instancias de IfcSlab declaran Pset_SlabCommon.FireRating (0.0%). |
| `H3.SLAB.LoadBearing` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/4 instancias de IfcSlab declaran Pset_SlabCommon.LoadBearing (0.0%). |
| `H3.WALL.FireRating` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.FireRating (0.0%). |
| `H3.WALL.IsExternal` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.IsExternal (0.0%). |
| `H3.WALL.LoadBearing` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.LoadBearing (0.0%). |
| `H3.WALL.ThermalTransmittance` | D2 | `yaml_python` | ✓ PASS | 100.00% | 95% | 60% | 13/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.ThermalTransmittance (... |
| `H3.WINDOW.IsExternal` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/11 instancias de IfcWindow declaran Pset_WindowCommon.IsExternal (0.0%). |
| `H4.BUILDING.IsLandmarked` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/1 instancias de IfcBuilding declaran Pset_BuildingCommon.IsLandmarked (0.0%). |
| `H4.BUILDING.NumberOfStoreys` | D2 | `yaml_python` | ✓ PASS | 100.00% | 95% | 60% | 1/1 instancias de IfcBuilding declaran Pset_BuildingCommon.NumberOfStoreys (100.0%). |
| `H4.BUILDING.YearOfConstruction` | D2 | `yaml_python` | ✓ PASS | 100.00% | 95% | 60% | 1/1 instancias de IfcBuilding declaran Pset_BuildingCommon.YearOfConstruction (100.0%). |
| `H4.SPACE.GrossPlannedArea` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/7 instancias de IfcSpace declaran Pset_SpaceCommon.GrossPlannedArea (0.0%). |
| `H4.SPACE.IsExternal` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/7 instancias de IfcSpace declaran Pset_SpaceCommon.IsExternal (0.0%). |
| `H4.SPACE.OccupancyNumber` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/7 instancias de IfcSpace declaran Pset_SpaceOccupancyRequirements.OccupancyNumber (0.... |
| `H4.SPACE.OccupancyType` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/7 instancias de IfcSpace declaran Pset_SpaceOccupancyRequirements.OccupancyType (0.0%). |
| `H4.STOREY.EntranceLevel` | D2 | `yaml_python` | ✗ FAIL | 0.00% | 95% | 60% | 0/2 instancias de IfcBuildingStorey declaran Pset_BuildingStoreyCommon.EntranceLevel (0... |
| `C-R-01` | D3 | `yaml_python` | ✓ PASS | 100.00% | 100% | 60% | 38/38 productos contenidos en IfcBuildingStorey (100.0%). |
| `C-R-02` | D3 | `yaml_python` | ✓ PASS | 100.00% | 100% | — | Jerarquía Project→Site→Building→Storey completa. |
| `C-R-03` | D3 | `yaml_python` | ✓ PASS | 100.00% | 100% | — | Sin productos huérfanos. |
| `C-U-01` | D5 | `yaml_python` | ✓ PASS | 100.00% | 100% | — | IfcUnitAssignment presente con 13 unidades. |
| `C-U-02` | D5 | `yaml_python` | ✓ PASS | 100.00% | 100% | — | Sistema SI métrico correcto: LENGTHUNIT=METRE, AREAUNIT=SQUARE_METRE, VOLUMEUNIT=CUBIC_... |
| `C-U-03` | D5 | `yaml_python` | — N/A | — | 100% | — | No hay QTO de muros/losas para muestrear longitudes. |
| `STR.BSDD.Classification` | D6 | `yaml_python` | ✗ FAIL | — | 100% | — | Legacy structural check_bsdd_classification → fail |

## 6. Hallazgos clave

### 6.1 Fallos críticos (16)

#### `STR.MVD.ReferenceView` · D1 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** —
- **Mensaje:** Legacy structural check_mvd_compliance → fail
- **Evidencia:**
```json
{
  "legacy_raw": {
    "query": {
      "type": "mvd_compliance",
      "expected_substr": "ReferenceView"
    },
    "declared_views": [
      "ViewDefinition [, QuantityTakeOffAddOnView, SpaceBoundary2ndLevelAddOnView]",
      "Option [Drawing Scale: 100.000000]",
      "Option [Global Unique Identifiers (GUID): Keep existing]",
      "Option [Elements to export: Entire project]",
      "Option [Partial Structure Display: Entire Model]",
      "Option [IFC Domain: All]",
      "Option [Structural Function: All Elements]",
      "Option [Convert Grid elements: On]",
      "Option [Convert IFC Annotations and ARCHICAD 2D elements: On]",
      "Option [Convert 2D symbols of Doors and Windows: Off]",
      "Option [Explode Composite and Complex Profile elements into parts: Off]",
      "Option [Export geometries that Participates in Collision Detection only: On]",
      "Option [Multi-skin complex geometries: Building element parts]",
      "Option [Elements in Solid Element Operations: Extruded/revolved]",
      "Option [Elements with junctions: Extruded/revolved without junctions]",
      "Option [Slabs with slanted edge(s): Extruded]",
      "Option [Use legacy geometric methods as in Coordination View 1.0: Off]",
      "Option [IFC Site Geometry: As boundary representation (BRep)]",
      "Option [IFC Site Location: At Project Origin]",
      "Option [Properties To Export: All properties]",
      "Option [Space containment: Off]",
      "Option [Bounding Box: On]",
      "Option [Geometry to type objects: On]",
      "Option [Element Properties: On]",
      "Option [Properties To Export: All]",
      "Option [IFC Base Quantities: On]",
      "Option [Window Door Lining and Panel Parameters: On]",
      "Option [IFC Space boundaries: On]",
      "Option [ARCHICAD Zone Categories as IFC Space classification data: On]"
    ],
    "expected": "ReferenceView",
    "match_found": false,
    "match_count": 0,
    "extra_views": [
      "ViewDefinition [, QuantityTakeOffAddOnView, SpaceBoundary2ndLevelAddOnView]",
      "Option [Drawing Scale: 100.000000]",
      "Option [Global Unique Identifiers (GUID): Keep existing]",
      "Option [Elements to export: Entire project]",
      "Option [Partial Structure Display: Entire Model]",
      "Option [IFC Domain: All]",
      "Option [Structural Function: All Elements]",
      "Option [Convert Grid elements: On]",
      "Option [Convert IFC Annotations and ARCHICAD 2D elements: On]",
      "Option [Convert 2D symbols of Doors and Windows: Off]",
      "Option [Explode Composite and Complex Profile elements into parts: Off]",
      "Option [Export geometries that Participates in Collision Detection only: On]",
      "Option [Multi-skin complex geometries: Building element parts]",
      "Option [Elements in Solid Element Operations: Extruded/revolved]",
      "Option [Elements with junctions: Extruded/revolved without junctions]",
      "Option [Slabs with slanted edge(s): Extruded]",
      "Option [Use legacy geometric methods as in Coordination View 1.0: Off]",
      "Option [IFC Site Geometry: As boundary representation (BRep)]",
      "Option [IFC Site Location: At Project Origin]",
      "Option [Properties To Export: All properties]",
      "Option [Space containment: Off]",
      "Option [Bounding Box: On]",
      "Option [Geometry to type objects: On]",
      "Option [Element Properties: On]",
      "Option [Properties To Export: All]",
      "Option [IFC Base Quantities: On]",
      "Option [Window Door Lining and Panel Parameters: On]",
      "Option [IFC Space boundaries: On]",
      "Option [ARCHICAD Zone Categories as IFC Space classification data: On]"
    ],
    "compliance": "fail"
  },
  "params": {
    "expected_mvd_substr": "ReferenceView"
  }
}
```

#### `STR.BSDD.Classification` · D6 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** —
- **Mensaje:** Legacy structural check_bsdd_classification → fail
- **Evidencia:**
```json
{
  "legacy_raw": {
    "query": {
      "type": "bsdd_classification"
    },
    "total_refs": 1,
    "bsdd_compliant": 0,
    "non_compliant": 0,
    "missing_location": 1,
    "compliance_pct": 0.0,
    "compliance": "fail",
    "unique_locations": {
      "<missing>": 1
    },
    "offenders": [
      {
        "id": 21169,
        "is_a": "IfcClassificationReference",
        "identification": "000",
        "name": "Allgemeines",
        "location": null,
        "referenced_source_name": null,
        "reason": "location_empty"
      }
    ],
    "accepted_domains": [
      "bsdd.buildingsmart.org",
      "identifier.buildingsmart.org",
      "gubimclass.itec.cat"
    ]
  },
  "params": {}
}
```

#### `H3.WALL.FireRating` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.FireRating (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcWallStandardCase",
  "pset": "Pset_WallCommon",
  "prop": "FireRating",
  "total": 13,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 13
}
```

#### `H3.WALL.LoadBearing` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.LoadBearing (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcWallStandardCase",
  "pset": "Pset_WallCommon",
  "prop": "LoadBearing",
  "total": 13,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 13
}
```

#### `H3.WALL.IsExternal` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.IsExternal (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcWallStandardCase",
  "pset": "Pset_WallCommon",
  "prop": "IsExternal",
  "total": 13,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 13
}
```

#### `H3.SLAB.FireRating` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/4 instancias de IfcSlab declaran Pset_SlabCommon.FireRating (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcSlab",
  "pset": "Pset_SlabCommon",
  "prop": "FireRating",
  "total": 4,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 4
}
```

#### `H3.SLAB.LoadBearing` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/4 instancias de IfcSlab declaran Pset_SlabCommon.LoadBearing (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcSlab",
  "pset": "Pset_SlabCommon",
  "prop": "LoadBearing",
  "total": 4,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 4
}
```

#### `H3.WINDOW.IsExternal` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/11 instancias de IfcWindow declaran Pset_WindowCommon.IsExternal (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcWindow",
  "pset": "Pset_WindowCommon",
  "prop": "IsExternal",
  "total": 11,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 11
}
```

#### `H4.SPACE.GrossPlannedArea` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/7 instancias de IfcSpace declaran Pset_SpaceCommon.GrossPlannedArea (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcSpace",
  "pset": "Pset_SpaceCommon",
  "prop": "GrossPlannedArea",
  "total": 7,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 7
}
```

#### `H4.SPACE.IsExternal` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/7 instancias de IfcSpace declaran Pset_SpaceCommon.IsExternal (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcSpace",
  "pset": "Pset_SpaceCommon",
  "prop": "IsExternal",
  "total": 7,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 7
}
```

#### `H4.STOREY.EntranceLevel` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/2 instancias de IfcBuildingStorey declaran Pset_BuildingStoreyCommon.EntranceLevel (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcBuildingStorey",
  "pset": "Pset_BuildingStoreyCommon",
  "prop": "EntranceLevel",
  "total": 2,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 2
}
```

#### `H4.SPACE.OccupancyType` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/7 instancias de IfcSpace declaran Pset_SpaceOccupancyRequirements.OccupancyType (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcSpace",
  "pset": "Pset_SpaceOccupancyRequirements",
  "prop": "OccupancyType",
  "total": 7,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 7
}
```

#### `H4.SPACE.OccupancyNumber` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/7 instancias de IfcSpace declaran Pset_SpaceOccupancyRequirements.OccupancyNumber (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcSpace",
  "pset": "Pset_SpaceOccupancyRequirements",
  "prop": "OccupancyNumber",
  "total": 7,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 7
}
```

#### `H4.BUILDING.IsLandmarked` · D2 · backend `yaml_python`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** 0/1 instancias de IfcBuilding declaran Pset_BuildingCommon.IsLandmarked (0.0%).
- **Evidencia:**
```json
{
  "ifc_type": "IfcBuilding",
  "pset": "Pset_BuildingCommon",
  "prop": "IsLandmarked",
  "total": 1,
  "present": 0,
  "compliance_pct": 0.0,
  "offenders_count": 1
}
```

#### `C-P-01` · D2 · backend `ids_xml`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** IDS spec 'C-P-01' FAIL · 0/1 entidades cumplen (0%).
- **Evidencia:**
```json
{
  "ids_spec_name": "C-P-01 · IfcWall con Pset_WallCommon.Reference",
  "ids_path": "/home/user/workspace/openbim-12w/ids/PBSA_v0.2_prototype.ids",
  "total_applicable": 1,
  "total_checks_pass": 0,
  "total_checks_fail": 1,
  "percent_checks_pass": 0,
  "ids_status_raw": false,
  "failed_entities_sample": [
    {
      "guid": "3sSuArjhP1VAHDFwRlK_Hf",
      "class": "IfcWall",
      "name": "S5L-AUTH-WALL-001",
      "reason": "The required property set does not exist"
    }
  ],
  "description": "Todo IfcWall debe declarar Pset_WallCommon.Reference como IfcIdentifier con valor no vacío.",
  "instructions": "Si falla: añadir Pset_WallCommon.Reference al muro en la herramienta de autoría antes de re-exportar."
}
```
- **Recomendación (IDS):** Si falla: añadir Pset_WallCommon.Reference al muro en la herramienta de autoría antes de re-exportar.

#### `C-P-02` · D2 · backend `ids_xml`

- **Estado:** ✗ FAIL
- **Score:** 0.00%
- **Mensaje:** IDS spec 'C-P-02' FAIL · 0/4 entidades cumplen (0%).
- **Evidencia:**
```json
{
  "ids_spec_name": "C-P-02 · IfcSlab con Pset_SlabCommon.LoadBearing",
  "ids_path": "/home/user/workspace/openbim-12w/ids/PBSA_v0.2_prototype.ids",
  "total_applicable": 4,
  "total_checks_pass": 0,
  "total_checks_fail": 4,
  "percent_checks_pass": 0,
  "ids_status_raw": false,
  "failed_entities_sample": [
    {
      "guid": "1pPHnf7cXCpPsNEnQf8_6B",
      "class": "IfcSlab",
      "name": "Bodenplatte",
      "reason": "The property set does not contain the required property"
    },
    {
      "guid": "2RGlQk4xH47RHK93zcTzUL",
      "class": "IfcSlab",
      "name": "Slab-033",
      "reason": "The property set does not contain the required property"
    },
    {
      "guid": "07Enbsqm9C7AQC9iyBwfSD",
      "class": "IfcSlab",
      "name": "Dach-1",
      "reason": "The property set does not contain the required property"
    },
    {
      "guid": "2IxUUNUVPB6Ob$eicCfP2N",
      "class": "IfcSlab",
      "name": "Dach-2",
      "reason": "The property set does not contain the required property"
    }
  ],
  "description": "Toda IfcSlab debe declarar Pset_SlabCommon.LoadBearing (IfcBoolean) para análisis estructural y QTO.",
  "instructions": "Si falla: añadir Pset_SlabCommon.LoadBearing a la losa en la herramienta de autoría."
}
```
- **Recomendación (IDS):** Si falla: añadir Pset_SlabCommon.LoadBearing a la losa en la herramienta de autoría.

### 6.2 Cumplimiento parcial (1)

- `C-P-03` (D2) · score 60.00% · IDS spec 'C-P-03' PARTIAL · 3/5 entidades cumplen (60%).

### 6.3 No aplicables (1)

Estos checks no se pudieron evaluar contra el modelo (ausencia de datos necesarios). No restan del pct_pass pero indican lagunas en el modelo a cubrir en próximas iteraciones.

- `C-U-03` (D5) · No hay QTO de muros/losas para muestrear longitudes.

## 7. Recomendaciones consolidadas

Acciones sugeridas, ordenadas por impacto (de mayor a menor):

1. **`STR.MVD.ReferenceView` (D1):** Legacy structural check_mvd_compliance → fail.
2. **`H3.WALL.FireRating` (D2):** 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.
3. **`H3.WALL.LoadBearing` (D2):** 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.
4. **`H3.WALL.IsExternal` (D2):** 0/13 instancias de IfcWallStandardCase declaran Pset_WallCommon.
5. **`H3.SLAB.FireRating` (D2):** 0/4 instancias de IfcSlab declaran Pset_SlabCommon.
6. **`H3.SLAB.LoadBearing` (D2):** 0/4 instancias de IfcSlab declaran Pset_SlabCommon.
7. **`H3.WINDOW.IsExternal` (D2):** 0/11 instancias de IfcWindow declaran Pset_WindowCommon.
8. **`H4.SPACE.GrossPlannedArea` (D2):** 0/7 instancias de IfcSpace declaran Pset_SpaceCommon.
9. **`H4.SPACE.IsExternal` (D2):** 0/7 instancias de IfcSpace declaran Pset_SpaceCommon.
10. **`H4.STOREY.EntranceLevel` (D2):** 0/2 instancias de IfcBuildingStorey declaran Pset_BuildingStoreyCommon.
11. **`H4.SPACE.OccupancyType` (D2):** 0/7 instancias de IfcSpace declaran Pset_SpaceOccupancyRequirements.
12. **`H4.SPACE.OccupancyNumber` (D2):** 0/7 instancias de IfcSpace declaran Pset_SpaceOccupancyRequirements.
13. **`H4.BUILDING.IsLandmarked` (D2):** 0/1 instancias de IfcBuilding declaran Pset_BuildingCommon.
14. **`C-P-01` (D2):** IDS spec 'C-P-01' FAIL · 0/1 entidades cumplen (0%).
15. **`C-P-02` (D2):** IDS spec 'C-P-02' FAIL · 0/4 entidades cumplen (0%).
16. **`C-P-03` (D2):** IDS spec 'C-P-03' PARTIAL · 3/5 entidades cumplen (60%).
17. **`STR.BSDD.Classification` (D6):** Legacy structural check_bsdd_classification → fail.

---

**Trazabilidad:** este reporte fue generado por `scripts/s6x_generate_e6_outputs.py` a partir de `out/AC20-FZK-Haus_compliance_post_asbuilt_v2.json`. La matriz JSON es la fuente canónica; este Markdown es derivado.

Motor: `quality_engine 0.2.0-s6x` · Sesión S6·X · 2026-06-17
