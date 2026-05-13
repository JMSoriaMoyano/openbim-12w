# S1·X · Lab: primer contacto IFC + IfcOpenShell

Generado: 2026-05-13 08:15
Ficheros analizados: 3

## Resumen estructural

| Fichero | Esquema | Entidades | Project | Site | Building | Storey | Space |
|---|---|---|---|---|---|---|---|
| `Building-Architecture.ifc` | IFC4 | 444 | 1 | 2 | 1 | 1 | 2 |
| `Building-Architecture.ifc` | IFC4X3 | 383 | 1 | 2 | 1 | 1 | 2 |
| `Infra-Road.ifc` | IFC4X3 | 887 | 1 | 6 | 0 | 0 | 0 |

## Conteos de las 10 clases objetivo

| Clase IFC | Building-Architecture.ifc | Building-Architecture.ifc | Infra-Road.ifc |
|---|---|---|---|
| `IfcProject` | 1 | 1 | 1 |
| `IfcSite` | 2 | 2 | 6 |
| `IfcBuilding` | 1 | 1 | 0 |
| `IfcBuildingStorey` | 1 | 1 | 0 |
| `IfcSpace` | 2 | 2 | 0 |
| `IfcWall` | 4 | 4 | 0 |
| `IfcSlab` | 3 | 3 | 0 |
| `IfcWindow` | 0 | 0 | 0 |
| `IfcDoor` | 0 | 0 | 0 |
| `IfcBuildingElementProxy` | 5 | 4 | 1 |

## Top 5 clases mas frecuentes por fichero

### `Building-Architecture.ifc`

| Clase | Instancias |
|---|---:|
| `IfcDirection` | 50 |
| `IfcCartesianPoint` | 36 |
| `IfcPropertySingleValue` | 34 |
| `IfcAxis2Placement3D` | 24 |
| `IfcLocalPlacement` | 22 |

### `Building-Architecture.ifc`

| Clase | Instancias |
|---|---:|
| `IfcDirection` | 50 |
| `IfcCartesianPoint` | 36 |
| `IfcAxis2Placement3D` | 24 |
| `IfcLocalPlacement` | 22 |
| `IfcRelDefinesByType` | 15 |

### `Infra-Road.ifc`

| Clase | Instancias |
|---|---:|
| `IfcDirection` | 182 |
| `IfcLocalPlacement` | 92 |
| `IfcAxis2Placement3D` | 91 |
| `IfcCartesianPoint` | 91 |
| `IfcShapeRepresentation` | 65 |

## Observaciones

_Anadir aqui 3 observaciones manuales tras revisar los resultados:_

1. IfcProject es único y obligatorio.
2. IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace es la cadena espacial canónica.
3. Los espacios se contienen en un IfcBuildingStorey, y agrupan elementos físicos por criterios funcionales.
4. Los elementos físicos se contienen en un IfcBuildingStorey (no en el Building directamente).
5. Cada producto físico suele referenciar a un tipo (IfcWallType, etc.) que define sus propiedades comunes.

## Dudas para resolver

1. 
2. 
3. 
