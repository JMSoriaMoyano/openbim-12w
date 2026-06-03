# S4·X · Mapeo consulta ↔ requisito ISO 19650

**Sesión:** S4·X (Mié 03/06/2026) · Lab IfcOpenShell
**Objetivo:** atar cada consulta técnica del repo a un requisito de información ISO 19650 y a una propiedad del EIR NEXUM PBSA v0.1.
**Doc relacionado:** [`EIR_NEXUM_PBSA_v0.1.md`](EIR_NEXUM_PBSA_v0.1.md)

---

## 1. Marco conceptual

ISO 19650 establece el flujo de requisitos de información:

```
OIR → AIR → EIR → BEP → Modelos del proveedor → Validación → Aceptación
```

- **OIR** (Organizational Information Requirements) — qué información necesita NEXUM como organización
- **AIR** (Asset Information Requirements) — qué necesita el activo (PBSA) durante operación
- **EIR** (Exchange Information Requirements) — qué debe entregar el proveedor en cada hito
- **BEP** (BIM Execution Plan) — cómo el proveedor responde al EIR
- **Validación** — verificación automática del cumplimiento

Las **3 consultas** de `s4x_ifc_lab.py` operan en el último eslabón: **validación**. Convierten requisitos en evidencia binaria (cumple / no cumple) sobre IFC reales.

## 2. Tabla principal · 3 consultas × 5 dimensiones

| Consulta | Pregunta de negocio | Requisito ISO 19650 | Regla aplicada | Evidencia generada |
|---|---|---|---|---|
| `query_by_type_with_psets` | ¿Qué declara cada elemento de tipo X? | LOIN — Alphanumerical Information ([BS EN 17412-1:2020](https://knowledge.bsigroup.com/products/building-information-modelling-level-of-information-need-concepts-and-principles)) | Para cada `IfcWall` (u otro tipo) debe constar `Pset_*Common` con las N propiedades obligatorias del EIR | JSON con instancias + psets reales — input para revisión humana o cruce con EIR |
| `query_spatial_containment` | ¿Dónde está cada elemento? ¿Hay huérfanos? | EIR — Structuring/Filing requirements (ISO 19650-2 §5.1.7) | Todo `IfcElement` físico debe estar contenido en una estructura espacial (`IfcRelContainedInSpatialStructure`) o relacionado por aperturas / virtualidad | Árbol Site/Building/Storey/Element + lista de huérfanos clasificada |
| `query_missing_property` | ¿Qué elementos NO declaran una propiedad concreta? | LOIN — verificación negativa | El 100% de instancias de tipo X debe declarar `Pset.prop` con valor no-`null` (según matriz EIR sección 4) | Tabla offenders + `compliance_pct` — directamente publicable como evidencia E4 |

## 3. Detalle por consulta

### 3.1 · `query_by_type_with_psets`

**Caso de uso NEXUM:** "Dame todos los IfcDoor con sus Pset_DoorCommon — quiero auditar manualmente FireRating, AcousticRating y SelfClosing en una pasada".

**CLI:**

```cmd
python scripts\s4x_ifc_lab.py --ifc <modelo.ifc> --query bytype ^
  --type IfcDoor --psets Pset_DoorCommon ^
  --out out\auditoria_puertas.json
```

**Notebook (equivalente):**

```python
result = query_by_type_with_psets(model, "IfcDoor", pset_names=["Pset_DoorCommon"])
```

**Output esperado:** dict con `total_found`, `query` (metadatos), `instances` (lista de dicts `{entity, instance_psets, instance_quantities, type_psets, summary}`).

**Interpretación:**

- `total_found = 0` con `query.error` poblado → tipo IFC mal escrito o no presente en schema
- `total_found > 0` y `instances[*].summary.total_properties = 0` → el tipo existe pero ningún elemento declara los Psets filtrados (red flag fuerte)
- Casos OK → cruzar manualmente cada `instance_psets` con la matriz EIR sección 4 correspondiente

**Limitaciones conocidas v0.1:**

- El filtrado por `pset_names` aplica también a `instance_quantities` y `type_psets`. Si pasas el nombre de un Pset, no recibirás quantities aunque existan (a no ser que el `Qto_*` esté en la lista también).
- No hay validación de schema IFC2x3 vs IFC4 sobre el nombre del Pset (algunos Psets cambian de nombre entre versiones).

### 3.2 · `query_spatial_containment`

**Caso de uso NEXUM:** "Antes de aceptar el modelo del arquitecto, verifico que toda la geometría está bien colocada en la estructura espacial. Si hay huérfanos físicos, es síntoma de import desde CAD sin reorganización ISO 19650".

**CLI:**

```cmd
python scripts\s4x_ifc_lab.py --ifc <modelo.ifc> --query spatial ^
  --out out\arbol_espacial.json
```

**Notebook (equivalente):**

```python
result = query_spatial_containment(model)
print(result["summary"])
print(result["orphans"])
```

**Output esperado:** dict con `project` (árbol recursivo Site→Building→Storey→Element), `orphans` (lista de huérfanos con `is_a`), `summary` (conteos agregados).

**Interpretación:**

- `summary.orphans_count = 0` → modelo bien estructurado
- `summary.orphans_count > 0` con clases `IfcOpeningElement` o `IfcVirtualElement` → falso positivo (comportamiento IFC correcto, ver limitaciones)
- `summary.orphans_count > 0` con clases físicas (`IfcWall`, `IfcDoor`, etc.) → red flag REAL — elementos sin contenedor espacial
- `summary.storeys = 0` → modelo sin plantas (probablemente un site/building sin descomposición — error grave)

**Limitaciones conocidas v0.1 (a corregir en v0.2):**

- La función reporta como huérfanos a los `IfcOpeningElement` (aperturas en muros) y `IfcVirtualElement` (líneas separación espacios). **Son falsos positivos por diseño IFC**: estas clases NO se contienen en estructura espacial, se relacionan vía `IfcRelVoidsElement` o son simbólicas.
- En FZK-Haus genera 20 falsos positivos (17 + 3). Filtrar manualmente o esperar a v0.2.

### 3.3 · `query_missing_property`

**Caso de uso NEXUM:** "El BEP del proveedor se compromete a entregar todos los muros con `Pset_WallCommon.FireRating`. Necesito una métrica numérica de cumplimiento y la lista de incumplidores para devolver el modelo al proveedor".

**CLI:**

```cmd
python scripts\s4x_ifc_lab.py --ifc <modelo.ifc> --query missing ^
  --type IfcWallStandardCase --pset Pset_WallCommon --prop FireRating ^
  --out out\incumplimientos_firerating.json
```

**Notebook (equivalente):**

```python
result = query_missing_property(model, "IfcWallStandardCase", "Pset_WallCommon", "FireRating")
print(f"Compliance: {result['compliance_pct']}%")
print(f"Offenders: {len(result['offenders'])}")
```

**Output esperado:**

```json
{
  "total": 13,
  "compliance": {"present": 0, "absent_pset": 0, "absent_prop": 13, "present_none": 0},
  "compliance_pct": 0.0,
  "offenders": [...],
  "sample_value": null
}
```

**Interpretación:**

- `compliance.present = total` (compliance_pct = 100%) → cumplimiento perfecto
- `compliance.absent_pset` > 0 → el Pset entero no existe en esas instancias (peor caso, indica que el proveedor no aplicó el Pset)
- `compliance.absent_prop` > 0 → el Pset existe pero falta esa propiedad concreta (más común, falta de rigor en la plantilla del proveedor)
- `compliance.present_none` > 0 → **caso MÁS GRAVE**: el modelador declaró la propiedad pero la dejó vacía. Enmascara el incumplimiento (parece que está pero no aporta valor).

**Caso validado S4·X sobre FZK-Haus:**

| Propiedad | Resultado | Lectura |
|---|---|---|
| `Pset_WallCommon.ThermalTransmittance` | 100% compliance (13/13) | ArchiCAD popula bien este campo desde la plantilla |
| `Pset_WallCommon.FireRating` | 0% compliance (0/13, todos `absent_prop`) | Incumplimiento sistemático — evidencia central E4 |

Evidencia versionada: [`out/s4x_missing_firerating_baseline.json`](../out/s4x_missing_firerating_baseline.json)

**Limitaciones conocidas v0.1:**

- No distingue entre "valor presente pero inválido" (ej. `FireRating = "blablabla"`) y "valor presente válido". Eso requiere validación semántica (IDS, S7·L).
- Solo audita una propiedad por ejecución — para auditar la matriz EIR completa hay que orquestar múltiples llamadas (TODO S6·L).

## 4. Mapeo consultas ↔ propiedades EIR NEXUM PBSA v0.1

Esta tabla cruza la matriz del EIR ([`EIR_NEXUM_PBSA_v0.1.md` §4](EIR_NEXUM_PBSA_v0.1.md)) con la consulta que la verifica y el estado de validación en FZK-Haus (modelo de pruebas):

| Tipo IFC | Pset | Propiedad | LOIN EIR | Consulta | Estado FZK-Haus |
|---|---|---|---|---|---|
| IfcWall | Pset_WallCommon | Reference | O | `missing` | pendiente auditar |
| IfcWall | Pset_WallCommon | FireRating | O | `missing` | **0% — confirmado S4·X** |
| IfcWall | Pset_WallCommon | AcousticRating | O | `missing` | pendiente auditar |
| IfcWall | Pset_WallCommon | ThermalTransmittance | O envolvente | `missing` | **100% — confirmado S4·X** |
| IfcWall | Pset_WallCommon | IsExternal | O | `missing` | pendiente auditar |
| IfcWall | Pset_WallCommon | LoadBearing | O | `missing` | pendiente auditar |
| IfcWall | Pset_WallCommon | Compartmentation | O sectorización | `missing` | pendiente auditar |
| IfcDoor | Pset_DoorCommon | FireRating | O sectorización | `missing` | pendiente auditar |
| IfcDoor | Pset_DoorCommon | AcousticRating | O habitaciones | `missing` | pendiente auditar |
| IfcDoor | Pset_DoorCommon | FireExit | O evacuación | `missing` | pendiente auditar |
| IfcDoor | Pset_DoorCommon | SelfClosing | O cortafuegos | `missing` | pendiente auditar |
| IfcWindow | Pset_WindowCommon | ThermalTransmittance | O | `missing` | pendiente auditar |
| IfcWindow | Pset_WindowCommon | AcousticRating | O fachada urbana | `missing` | pendiente auditar |
| IfcSpace | Pset_SpaceCommon | NetPlannedArea | O | `missing` | pendiente auditar |
| IfcSpace | Pset_SpaceCommon | HandicapAccessible | O accesibles | `missing` | pendiente auditar |
| IfcSpace | Pset_NEXUM_PBSA | RoomType | O | `missing` | **no aplica** (FZK-Haus no es PBSA, no tiene Pset custom NEXUM) |
| TODOS | — | GlobalId, Name | O | manual / `bytype` | OK por defecto en ArchiCAD |
| TODOS | (OwnerHistory) | OwningUser | O | manual | **incumplimiento documentado S4·L hallazgo #7** (Person no definida) |

**Cobertura E4:** 2 de 17 propiedades obligatorias auditadas el sábado 06/06. Suficiente para demostrar el método. La auditoría completa del EIR (las 17 + propiedades de Slab/Roof/Stair/Railing) se planifica para S6·L cuando integremos un wrapper de orquestación.

## 5. Limitaciones del enfoque actual y evolución

### Lo que NO hace este enfoque (v0.1)
- **No es IDS formal.** Las reglas están en código Python, no en XML estándar buildingSMART. Eso llega en **S7·L**.
- **No valida semántica.** Solo presencia/ausencia, no si el valor es correcto (ej. "FireRating = blah" cuenta como presente).
- **No es ejecutable por terceros sin el repo.** Un proveedor no puede correr estas consultas si no le entregamos el código. Con IDS sí podrá.

### Evolución planificada
| Sesión | Aporte |
|---|---|
| S5·L | Geometría con IfcOpenShell — añadir consultas geométricas (intersecciones, holguras, alturas libres) |
| S6·L | Calidad: orquestador de la matriz EIR completa — un solo comando audita las 17+ propiedades |
| S7·L | IDS 1.0 — traducir este EIR a XML estándar |
| S8·L | `ifctester` (Python) — ejecutar la validación IDS desde CLI |
| S9·L | CI/CD — automatización de validación en cada commit del proveedor |

---

## Notas

- Este documento es **vivo**: cada sesión añade consultas y refina interpretaciones. La versión congelada al cierre de E4 (sáb 06/06) se etiquetará como `s4x-closed` en el repo.
- Cualquier proveedor BIM que reciba el EIR puede solicitar acceso al repo para entender exactamente cómo se validará su modelo. Trazabilidad total.
