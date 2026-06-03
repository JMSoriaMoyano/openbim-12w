# EIR NEXUM PBSA · v0.1

**Documento:** Exchange Information Requirements (plantilla genérica)
**Tipología:** Purpose-Built Student Accommodation (PBSA)
**Fases cubiertas:** Proyecto Ejecutivo + As-built
**Autor:** NEXUM Developments
**Versión:** 0.1 (S4·X · 03/06/2026 · primera línea base, sujeta a revisión por proyecto)
**Marco normativo:**

- ISO 19650-1:2018 / ISO 19650-2:2018 (gestión de la información)
- BS EN 17412-1:2020 — Level of Information Need ([BSI Knowledge](https://knowledge.bsigroup.com/products/building-information-modelling-level-of-information-need-concepts-and-principles))
- IFC 4.3.2 (schema base) ([buildingSMART IFC 4.3.2](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/))
- CTE (Código Técnico de la Edificación · España): DB-SI, DB-HR, DB-HE, DB-SUA

---

## 0. Propósito y alcance

Este EIR define los **requisitos de información alfanumérica** que NEXUM exige a los proveedores BIM (arquitectura, ingeniería) en proyectos de Purpose-Built Student Accommodation. Cubre **dos fases de entrega**:

- **Fase E · Proyecto Ejecutivo** (modelo para construcción)
- **Fase H · As-built / Handover** (modelo para operación, entregado al operador PBSA)

No cubre fases tempranas (Anteproyecto, Básico) — se asume que esas fases producen modelos de menor LOD/LOIN y no son contractuales con NEXUM.

**Exclusiones de v0.1:** MEP avanzado (climatización, electricidad detallada), estructura (refuerzos, conexiones), urbanización exterior. Se ampliarán en v0.2.

## 1. Tipos IFC objeto del EIR

Esta versión cubre **8 tipos IFC** que conforman el grueso del modelo arquitectónico PBSA:

| Tipo IFC | Aplicación PBSA | Volumen típico por edificio (200 camas) |
|---|---|---|
| `IfcWall` / `IfcWallStandardCase` | Muros perimetrales y particiones interiores | 800-1500 instancias |
| `IfcSlab` | Forjados, soleras, cubiertas planas | 4-8 instancias por planta |
| `IfcRoof` | Cubiertas inclinadas (poco común en PBSA urbano) | 0-2 |
| `IfcStair` | Núcleos de comunicación vertical | 2-4 instancias |
| `IfcRailing` | Barandillas, pasamanos | 20-40 |
| `IfcDoor` | Puertas (habitaciones, cortafuegos, sectorización) | 200-400 |
| `IfcWindow` | Ventanas y huecos vidriados | 200-400 |
| `IfcSpace` | Habitaciones, baños, cocinas comunes, salas, circulaciones | 250-500 |

## 2. Marco LOIN aplicado

Cada propiedad del EIR se clasifica según:

| Código | Significado |
|---|---|
| **O** | Obligatoria — incumplimiento = no aceptación del entregable |
| **R** | Recomendada — su ausencia genera observación en revisión, no rechazo |
| **F** | Facultativa — solicitada solo si aplica al caso concreto (ej. CombustibleRating en muro no estructural) |

Y por fase de exigibilidad:

| Código | Fase |
|---|---|
| **E** | Exigible en Proyecto Ejecutivo |
| **H** | Exigible en As-built / Handover |
| **E+H** | Exigible en ambas fases (típico de propiedades estáticas de diseño) |

## 3. Ejes de información

Las propiedades se agrupan en **4 ejes**:

1. **Identificación y trazabilidad** — qué es y de dónde viene
2. **Cumplimiento normativo (CTE)** — DB-SI, DB-HR, DB-HE, DB-SUA
3. **Operación y mantenimiento (FM)** — handover al operador
4. **Costes, cantidades y clasificación** — 5D y QTO

---

## 4. Matriz de propiedades por tipo IFC

### 4.1 · IfcWall / IfcWallStandardCase

Pset estándar: [`Pset_WallCommon`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_WallCommon.htm)

| Propiedad | Pset | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| Reference | Pset_WallCommon | 1 | O | E+H | Código tipológico interno del proyecto (ej. "MUR-INT-EI60-001") |
| Status | Pset_WallCommon | 1 | R | E+H | New / Existing / Demolish / Temporary |
| FireRating | Pset_WallCommon | 2 (DB-SI) | O | E+H | Valor según UNE-EN 13501-2 (ej. "EI 60", "EI 90") |
| AcousticRating | Pset_WallCommon | 2 (DB-HR) | O | E+H | Valor R'w en dB (ej. "R'w ≥ 50 dB") |
| ThermalTransmittance | Pset_WallCommon | 2 (DB-HE) | O envolvente, F particiones | E+H | U-value en W/m²K. Solo obligatorio en envolvente. |
| IsExternal | Pset_WallCommon | 1 | O | E+H | TRUE=envolvente, FALSE=partición |
| LoadBearing | Pset_WallCommon | 1 | O | E+H | TRUE=estructural, FALSE=no estructural |
| Compartmentation | Pset_WallCommon | 2 (DB-SI) | O en sectorización | E+H | TRUE si forma sector de incendio |
| ExtendToStructure | Pset_WallCommon | 1 | R | E+H | TRUE=muro de losa a losa (estanqueidad acústica/incendio) |
| Combustible | Pset_WallCommon | 2 (DB-SI) | R | E+H | FALSE esperado en evacuación |
| SurfaceSpreadOfFlame | Pset_WallCommon | 2 (DB-SI) | F | E+H | Clase de reacción al fuego del acabado superficial |

### 4.2 · IfcSlab

Pset estándar: `Pset_SlabCommon`

| Propiedad | Pset | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| Reference | Pset_SlabCommon | 1 | O | E+H | Código tipológico (ej. "FOR-EI120-001") |
| Status | Pset_SlabCommon | 1 | R | E+H | |
| FireRating | Pset_SlabCommon | 2 (DB-SI) | O | E+H | Sectorización vertical |
| AcousticRating | Pset_SlabCommon | 2 (DB-HR) | O | E+H | Ruido entre plantas — crítico en PBSA |
| ThermalTransmittance | Pset_SlabCommon | 2 (DB-HE) | O en cubierta y solera | E+H | |
| LoadBearing | Pset_SlabCommon | 1 | O | E+H | |
| Combustible | Pset_SlabCommon | 2 (DB-SI) | R | E+H | |
| PitchAngle | Pset_SlabCommon | 1 | F | E+H | Solo si solera/cubierta inclinada |

### 4.3 · IfcRoof

Pset estándar: `Pset_RoofCommon`

| Propiedad | Pset | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| Reference | Pset_RoofCommon | 1 | O | E+H | |
| FireRating | Pset_RoofCommon | 2 (DB-SI) | O | E+H | |
| ThermalTransmittance | Pset_RoofCommon | 2 (DB-HE) | O | E+H | |
| ProjectedArea | Pset_RoofCommon | 4 | R | E+H | Para QTO |
| TotalArea | Pset_RoofCommon | 4 | R | E+H | Para QTO |

### 4.4 · IfcStair

Pset estándar: `Pset_StairCommon`

| Propiedad | Pset | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| Reference | Pset_StairCommon | 1 | O | E+H | |
| FireRating | Pset_StairCommon | 2 (DB-SI) | O en evacuación | E+H | Escaleras protegidas / especialmente protegidas |
| NumberOfRiser | Pset_StairCommon | 2 (DB-SUA) | O | E+H | DB-SUA limita número máximo entre rellanos |
| NumberOfTreads | Pset_StairCommon | 2 (DB-SUA) | O | E+H | |
| RiserHeight | Pset_StairCommon | 2 (DB-SUA) | O | E+H | DB-SUA 16-17.5cm uso público |
| TreadLength | Pset_StairCommon | 2 (DB-SUA) | O | E+H | DB-SUA mín 28cm |
| RequiredHeadroom | Pset_StairCommon | 2 (DB-SUA) | O | E+H | Mín 220cm |
| HandicapAccessible | Pset_StairCommon | 2 (DB-SUA) | R | E+H | Indica si cumple accesibilidad |

### 4.5 · IfcRailing

Pset estándar: `Pset_RailingCommon`

| Propiedad | Pset | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| Reference | Pset_RailingCommon | 1 | O | E+H | |
| Height | Pset_RailingCommon | 2 (DB-SUA) | O | E+H | Mín 90cm interiores, 110cm exteriores |
| HandicapAccessible | Pset_RailingCommon | 2 (DB-SUA) | R | E+H | |

### 4.6 · IfcDoor

Pset estándar: [`Pset_DoorCommon`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_DoorCommon.htm)

| Propiedad | Pset | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| Reference | Pset_DoorCommon | 1 | O | E+H | Código (ej. "PUE-EI60-001") |
| Status | Pset_DoorCommon | 1 | R | E+H | |
| FireRating | Pset_DoorCommon | 2 (DB-SI) | O en sectorización | E+H | EI 30/60/90 según uso |
| AcousticRating | Pset_DoorCommon | 2 (DB-HR) | O habitaciones | E+H | Crítico en puertas a circulación |
| ThermalTransmittance | Pset_DoorCommon | 2 (DB-HE) | O envolvente | E+H | Solo puertas exteriores |
| IsExternal | Pset_DoorCommon | 1 | O | E+H | |
| FireExit | Pset_DoorCommon | 2 (DB-SI) | O evacuación | E+H | Identifica puerta de evacuación |
| HandicapAccessible | Pset_DoorCommon | 2 (DB-SUA) | O en rutas accesibles | E+H | Anchura libre, mecanismos, esfuerzo |
| SelfClosing | Pset_DoorCommon | 2 (DB-SI) | O cortafuegos | E+H | TRUE en puertas EI |
| SmokeStop | Pset_DoorCommon | 2 (DB-SI) | R | E+H | |
| SecurityRating | Pset_DoorCommon | 3 (FM) | R | E+H | Tipo de cerradura, acceso por tarjeta |

### 4.7 · IfcWindow

Pset estándar: `Pset_WindowCommon`

| Propiedad | Pset | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| Reference | Pset_WindowCommon | 1 | O | E+H | |
| FireRating | Pset_WindowCommon | 2 (DB-SI) | F | E+H | Solo si requiere protección |
| AcousticRating | Pset_WindowCommon | 2 (DB-HR) | O fachada urbana | E+H | Crítico en PBSA urbano |
| ThermalTransmittance | Pset_WindowCommon | 2 (DB-HE) | O | E+H | U-value del conjunto marco+vidrio |
| GlazingAreaFraction | Pset_WindowCommon | 4 | R | E+H | Para cálculos solares |
| Infiltration | Pset_WindowCommon | 2 (DB-HE) | R | E+H | Permeabilidad al aire (clase) |
| IsExternal | Pset_WindowCommon | 1 | O | E+H | |

### 4.8 · IfcSpace

Pset estándar: [`Pset_SpaceCommon`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_SpaceCommon.htm)

| Propiedad | Pset | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| Reference | Pset_SpaceCommon | 1 | O | E+H | Código habitación (ej. "HAB-P02-015") |
| IsExternal | Pset_SpaceCommon | 1 | O | E+H | TRUE en terrazas, FALSE interior |
| GrossPlannedArea | Pset_SpaceCommon | 4 | O | E+H | Área programa, para QTO |
| NetPlannedArea | Pset_SpaceCommon | 4 | O | E+H | Área útil, base SBA/NRA del operador |
| PubliclyAccessible | Pset_SpaceCommon | 1 | R | E+H | Aseos comunes, salas de estudio |
| HandicapAccessible | Pset_SpaceCommon | 2 (DB-SUA) | O en habitaciones accesibles | E+H | Mín 5% camas accesibles (estándar PBSA) |

## 5. Pset custom NEXUM PBSA

Pset propietario: `Pset_NEXUM_PBSA` (a aplicar sobre `IfcSpace` que represente habitación o tipología PBSA).

| Propiedad | Tipo | Eje | LOIN | Fase | Notas |
|---|---|---|---|---|---|
| RoomType | IfcLabel (enum) | 1 | O | E+H | Studio / Twin / Ensuite / Cluster / Accessible / Common / Service |
| BedCount | IfcInteger | 1 | O en habitación | E+H | 1 (studio, ensuite) o 2 (twin, cluster) |
| FurnitureLevel | IfcLabel (enum) | 3 (FM) | R | H | Bare / Furnished / FullyFurnished |
| NetUsableArea_PBSA | IfcAreaMeasure | 4 | O | E+H | Área útil PBSA según estándar del operador (excluye pasillo interior de cluster) |
| HasPrivateBathroom | IfcBoolean | 1 | O en habitación | E+H | FALSE en cluster con baño compartido |
| ClusterId | IfcIdentifier | 1 | O en cluster | E+H | ID del cluster al que pertenece (ej. "CLU-P03-A") |
| OperatorReference | IfcIdentifier | 1 | R | H | Código que el operador usará para gestión (ej. "RESA-HAB-2034") |
| AccessibilityCompliant | IfcBoolean | 2 (DB-SUA) | O en habitación | E+H | TRUE si la habitación cumple DB-SUA para PMR |

## 6. Quantities exigidas (BaseQuantities)

Adicionales a Psets, se exige `Qto_*BaseQuantities` poblado para QTO automatizado:

| Tipo IFC | Quantity Set | Quantities mínimas |
|---|---|---|
| IfcWall | Qto_WallBaseQuantities | Length, Height, Width, NetSideArea, NetVolume |
| IfcSlab | Qto_SlabBaseQuantities | GrossArea, NetArea, GrossVolume, NetVolume |
| IfcDoor | Qto_DoorBaseQuantities | Width, Height, Area |
| IfcWindow | Qto_WindowBaseQuantities | Width, Height, Area |
| IfcSpace | Qto_SpaceBaseQuantities | NetFloorArea, GrossFloorArea, NetVolume, GrossVolume, FinishCeilingHeight |

## 7. Clasificación

Se exige `IfcClassificationReference` sobre cada elemento con sistema **GuBIMClass** (clasificación BIM española) o **Uniclass 2015** (alternativo aceptado). Mínimo: nivel de elemento.

## 8. Identidad y autoría

Atributos IFC raíz exigidos en cada entidad:

| Atributo | Aplicación | LOIN | Notas |
|---|---|---|---|
| GlobalId | Todos | O | UUID IFC válido, estable entre revisiones |
| Name | Todos | O | Nombre legible (puede repetirse entre instancias del mismo tipo) |
| Description | Tipos custom o singulares | R | |
| OwnerHistory.OwningUser | Todos | O | Person + Organization correctamente definidos (NO "Nicht definiert", `S4·L hallazgo #7`) |
| Tag | Todos | R | ID nativo de la herramienta de autoría (ArchiCAD GUID, Revit ElementId) |

## 9. Validación

Esta plantilla es **auditable automáticamente** mediante los scripts del repositorio `openbim-12w`:

- `scripts/s4x_ifc_lab.py --query missing --type <tipo> --pset <pset> --prop <prop>` para cada fila marcada **O**
- Cobertura completa del EIR generable con un script wrapper (TODO S6·L)
- A partir de S7·L este EIR se traducirá a IDS 1.0 (XML) para validación con `ifctester`

## 10. Versionado y mantenimiento

- **v0.1** (S4·X · 03/06/2026) — primera línea base, 8 tipos IFC, ~70 propiedades, fases Ejecutivo + As-built
- **v0.2** (planificada S6/S7) — ampliar a MEP básico (IfcFlowTerminal, IfcLightFixture), estructura básica (IfcBeam, IfcColumn), añadir auditoría IDS formal
- **v1.0** (objetivo Q4 2026) — versión contractual para Can Cabassa PBSA, revisada con BIM Manager NEXUM y validada con operador

Toda revisión queda registrada en `git log` y en el changelog de este documento.

---

## Changelog

- **v0.1 · 03/06/2026** — Creación inicial. Cubre 8 tipos IFC arquitectónicos, 4 ejes de información, Pset custom `Pset_NEXUM_PBSA`. Fases Ejecutivo + As-built. Marco CTE (DB-SI, DB-HR, DB-HE, DB-SUA).
