# S5·L · Reglas de autoría IFC

**Documento:** S5·L · Reglas de autoría sobre modelos IFC
**Sesión:** S5·L (Lun 08/06/2026)
**Aplicable a:** todo bloque de autoría (S5·L Bloque D, S5·X y posteriores)
**Estado:** v1.0 · vinculante para el resto del programa
**Autor:** José M. Soria · NEXUM Developments

---

## 1. Propósito

Antes de **modificar geometría o atributos** de un modelo IFC con `ifcopenshell.api` es imprescindible fijar un contrato sobre **qué se permite tocar, qué no, y cómo se deja constancia auditable del cambio**.

Las consultas de lectura (S3, S4) no requerían este contrato porque no mutaban el modelo. La autoría sí. Este documento es la base de todas las sesiones de autoría posteriores.

---

## 2. Principios rectores

| # | Principio | Aplicación práctica |
|:---:|---|---|
| **P1** | **No mutar el modelo original** | Todo cambio se aplica sobre una copia escrita a `out/<nombre>_authored.ifc`. El IFC fuente permanece intacto. |
| **P2** | **Autoría reversible y trazable** | Cada operación deja un registro JSON en `out/<nombre>_authored_diff.json` con antes/después y timestamp. |
| **P3** | **Una operación, una función** | Cada operación de autoría se implementa en una función Python con docstring que cita el §EIR que la justifica. |
| **P4** | **Validación post-autoría obligatoria** | Tras escribir, re-cargar el IFC y re-ejecutar el orquestador EIR. La mejora debe ser cuantificable. |
| **P5** | **Whitelist explícita** | Solo se pueden modificar las clases IFC, Psets y propiedades declaradas en §3. Cualquier otra modificación requiere ampliar primero esta whitelist. |

---

## 3. Whitelist de autoría · v0.1

### 3.1 Operaciones de propiedad (Pset)

Permitidas:

| Acción | Clase IFC | Pset | Propiedad | Justificación EIR |
|---|---|---|---|---|
| Poblar | `IfcDoor` | `Pset_DoorCommon` | `FireRating` | §4.2.ARQ (CTE DB-SI) |
| Poblar | `IfcWindow` | `Pset_WindowCommon` | `FireRating`, `IsExternal` | §4.2.ARQ |
| Poblar | `IfcWallStandardCase` | `Pset_WallCommon` | `FireRating`, `LoadBearing`, `IsExternal` | §4.2.ARQ, §4.2.EST |
| Poblar | `IfcSlab` | `Pset_SlabCommon` | `FireRating`, `LoadBearing` | §4.2.ARQ, §4.2.EST |
| Poblar | `IfcSpace` | `Pset_SpaceCommon` | `GrossPlannedArea`, `IsExternal` | §4.4.FM |
| Poblar | `IfcBuildingStorey` | `Pset_BuildingStoreyCommon` | `EntranceLevel` | §4.4.FM |

**Regla:** solo se **POBLAN** propiedades inexistentes o se **CORRIGEN** valores claramente erróneos (ej. tipo de dato). **Nunca se sobrescribe un valor válido sin justificación documentada.**

### 3.2 Operaciones de geometría

Permitidas:

| Acción | Clase IFC | Restricción |
|---|---|---|
| **Crear** | `IfcWall` o `IfcWallStandardCase` | Con representación geométrica básica (`IfcExtrudedAreaSolid` sobre `IfcRectangleProfileDef`) y ubicación en sistema de coordenadas del proyecto |
| **Crear** | `IfcOpeningElement` (asociado a muro nuevo) | Solo si se crea un muro nuevo que requiera abertura para puerta/ventana |

Prohibidas en v0.1:

- ❌ Borrar elementos existentes (geometría o instancias)
- ❌ Modificar geometría de elementos existentes (vértices, perfiles, extrusiones)
- ❌ Modificar relaciones de agregación (`IfcRelAggregates`) o contención espacial (`IfcRelContainedInSpatialStructure`) ya existentes — solo se permite **crear** nuevas relaciones para elementos nuevos
- ❌ Modificar la cabecera STEP (`FILE_DESCRIPTION`, `FILE_NAME`) o el `IfcProject` raíz
- ❌ Reasignar `GlobalId` de elementos existentes

### 3.3 Ampliaciones futuras

| Whitelist | Sesión prevista |
|---|---|
| Edición de geometría existente (mover, escalar) | S5·X o S6·L |
| Borrado controlado de elementos | S6·L (con reglas estrictas de huérfanos) |
| Edición de relaciones espaciales | S6·L |
| Creación de Psets personalizados (no comunes) | S7·L (junto con IDS) |

---

## 4. Trazabilidad obligatoria

### 4.1 Estructura del fichero diff

Toda función de autoría debe escribir/actualizar `out/<base>_authored_diff.json` con la estructura:

```json
{
  "source_ifc": "<ruta_o_nombre>.ifc",
  "target_ifc": "out/<base>_authored.ifc",
  "session": "S5·L",
  "authored_at": "2026-06-08T08:00:00+02:00",
  "operations": [
    {
      "op_id": "OP-001",
      "type": "set_pset_property",
      "element": {"id": 1234, "global_id": "...", "type": "IfcDoor", "name": "Door-1"},
      "pset": "Pset_DoorCommon",
      "property": "FireRating",
      "value_before": null,
      "value_after": "EI 30",
      "eir_ref": "§4.2.ARQ",
      "rationale": "Corrige hallazgo H3.DOOR.FireRating de E4"
    }
  ],
  "summary": {
    "ops_total": 4,
    "ops_by_type": {"set_pset_property": 3, "create_element": 1}
  }
}
```

### 4.2 Nomenclatura de ficheros

| Tipo | Patrón | Ejemplo |
|---|---|---|
| IFC editado | `out/<base>_authored.ifc` | `out/AC20-FZK-Haus_authored.ifc` |
| Diff de autoría | `out/<base>_authored_diff.json` | `out/AC20-FZK-Haus_authored_diff.json` |
| Matriz EIR post-autoría | `out/<base>_compliance_matrix_post.json` | `out/AC20-FZK-Haus_compliance_matrix_post.json` |

El `.gitignore` ya soporta `*_authored.ifc` como evidencia versionada (S5·L Bloque B). El diff JSON entra por el patrón `_baseline` si se renombra con sufijo `_baseline`, o se añade explícitamente al `git add`.

### 4.3 Reproducibilidad

Toda función de autoría debe ser **determinista**: ejecutarla N veces sobre el mismo modelo fuente debe producir el mismo `_authored.ifc` byte-a-byte (módulo timestamps autorizados en cabecera STEP). Si la API de ifcopenshell genera GlobalIds aleatorios para elementos nuevos, se deben fijar mediante semilla declarada en el diff JSON.

---

## 5. Flujo canónico

```
                          ┌────────────────┐
                          │ IFC fuente     │
                          │ (no mutable)   │
                          └────────┬───────┘
                                   │ copy
                                   ▼
                          ┌────────────────┐
                          │ IFC trabajo    │
                          │ (en memoria)   │
                          └────────┬───────┘
                                   │ apply_operations()
                                   ▼
                ┌──────────────────────────────────┐
                │ Para cada op autorizada (§3):    │
                │   1. snapshot valor before       │
                │   2. mutar via ifcopenshell.api  │
                │   3. registrar en diff JSON      │
                └──────────────────┬───────────────┘
                                   │ write
                                   ▼
                  ┌────────────────────────────┐
                  │ out/<base>_authored.ifc    │
                  │ out/<base>_authored_diff.json │
                  └────────────┬───────────────┘
                               │ re-load + audit
                               ▼
                  ┌────────────────────────────┐
                  │ s4s_audit_eir.py           │
                  │ → matrix_post              │
                  └────────────┬───────────────┘
                               │ compare
                               ▼
                  ┌────────────────────────────┐
                  │ Δ compliance               │
                  │ (debe ser ≥ 0 en todos)    │
                  └────────────────────────────┘
```

**Regla crítica P4:** si la matriz post-autoría empeora algún chequeo (Δ negativo), la operación queda **inválida** y debe ser revertida antes de commit.

---

## 6. Criterios de aceptación E5 (sábado 13/06)

Con estas reglas en vigor, el entregable E5 se considera aceptado cuando:

- ✅ Existe `scripts/s5l_ifc_authoring.py` con al menos 2 funciones autorizadas (1 propiedad + 1 geometría)
- ✅ Existe `out/AC20-FZK-Haus_authored.ifc` válido (re-cargable con `ifcopenshell.open()` sin errores)
- ✅ Existe `out/AC20-FZK-Haus_authored_diff.json` con todas las operaciones trazadas
- ✅ Existe `out/AC20-FZK-Haus_compliance_matrix_post.json` con **al menos 1 chequeo mejorado** (típicamente `H3.DOOR.FireRating` de 40% a 100%)
- ✅ Existe `docs/E5_autoria_fzk_haus.md` describiendo las operaciones realizadas y su impacto en compliance
- ✅ Cero retrocesos: ningún chequeo empeora respecto a `out/s4s_compliance_matrix_baseline.json`

---

## 7. Excepciones y enmiendas

Cualquier desviación de estas reglas requiere:

1. Anotación explícita en el commit (mensaje empezando por `[exception-S5L]`)
2. Actualización de este documento en mismo commit
3. Justificación EIR (cita §)

---

**Fin de S5L_reglas_autoria.md v1.0. Vinculante a partir de S5·L Bloque D.**
