"""
s3l_ifc_inspect.py — Inspector mínimo de IFC

Sesión:        S3·L (semana 3, lunes) · 25/05/2026
               S3·X (semana 3, miércoles) · 27/05/2026 [recuperación 28-29/05]
Nivel:         3 (6 funciones implementadas con IfcOpenShell; resto pseudocódigo)
Estado:        v0.3 — Bloques A+B+C operativos.
Schema base:   IFC4 (IFC4 ADD2 TC1)
Modelo:        models/samples/_local/AC20-FZK-Haus.ifc
SHA-256:       70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994

Funciones implementadas
-----------------------
  open_ifc                  (v0.2 · S3·X-A)
  report_header             (v0.2 · S3·X-A)
  walk_spatial_pyramid      (v0.2 · S3·X-A)
  count_physical_elements   (v0.2 · S3·X-A)
  check_minimum_psets       (v0.3 · S3·X-C · auditoría Psets NEXUM)
  explain_entity            (v0.3 · S3·X-C · anatomía completa por GUID)

Cambios v0.3 (S3·X Bloque C)
----------------------------
- Añadida tabla constante PSETS_NEXUM (Psets mínimos por clase, derivada
  del dictamen D3B-01 en docs/S3X_dudas_resueltas.md).
- Implementadas check_minimum_psets() y explain_entity().
- main() amplía el informe con dos bloques nuevos: "Auditoría Pset NEXUM" y
  "Anatomía del muro #15042".
- CLI extendido con segundo argumento opcional para inspeccionar otra entidad
  vía GUID en lugar del muro de referencia.

Pendientes para S4·L
--------------------
  list_elements_per_storey, count_relationships,
  validate_doors_have_openings, validate_unique_project

Ejecución
---------
  python scripts/s3l_ifc_inspect.py
  python scripts/s3l_ifc_inspect.py models/samples/_local/AC20-FZK-Haus.ifc
  python scripts/s3l_ifc_inspect.py models/samples/_local/AC20-FZK-Haus.ifc 2XPyKWY018sA1ygZKgQPtU

Salida
------
  - Consola: log completo de la inspección.
  - Fichero: out/S3X_lab_run_YYYYMMDD_HHMMSS.md.
"""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import ifcopenshell

if TYPE_CHECKING:
    from typing import Any
    IfcFile = Any  # ifcopenshell.file
    IfcEntity = Any  # ifcopenshell.entity_instance


# =============================================================================
# 0. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

EXPECTED_SHA256: str = (
    "70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994"
)
"""SHA-256 canónico de AC20-FZK-Haus.ifc declarado en models/samples/SOURCES.md §4.3."""

DEFAULT_IFC_PATH: Path = Path("models/samples/_local/AC20-FZK-Haus.ifc")
"""Ruta relativa al fichero de referencia (Opción B: no versionado en git)."""

OUT_DIR: Path = Path("out")
"""Directorio donde se escriben los informes de ejecución (git-ignored)."""

# Conteos esperados del FZK-Haus, usados como validación cruzada en S4·L
# y como casos de test en tests/test_s3l_ifc_inspect.py
EXPECTED_COUNTS_FZK: dict[str, int] = {
    # Entidades espaciales
    "IfcProject": 1,
    "IfcSite": 1,
    "IfcBuilding": 1,
    "IfcBuildingStorey": 2,
    # Elementos físicos
    "IfcWallStandardCase": 13,
    "IfcSlab": 4,
    "IfcWindow": 11,
    "IfcDoor": 5,
    "IfcStair": 1,
    "IfcRailing": 2,
    "IfcOpeningElement": 17,
    # Tipos
    "IfcWallType": 2,
    # Relaciones
    "IfcRelAggregates": 5,
    "IfcRelContainedInSpatialStructure": 2,
    "IfcRelDefinesByType": 18,
    "IfcRelDefinesByProperties": 482,
    "IfcRelAssociatesMaterial": 21,
    "IfcRelVoidsElement": 17,
    "IfcRelFillsElement": 16,
    "IfcRelConnectsPathElements": 16,
    "IfcRelSpaceBoundary": 81,
    "IfcRelAssociatesClassification": 1,
}


# =============================================================================
# Writer dual: imprime a consola Y acumula líneas para el informe Markdown
# =============================================================================

class DualWriter:
    """Acumula líneas de log y las vuelca tanto a stdout como a un fichero .md."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def line(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def heading(self, text: str, level: int = 2) -> None:
        prefix = "#" * level
        print(text)
        self.lines.append(f"{prefix} {text}")

    def code(self, text: str, lang: str = "") -> None:
        print(text)
        self.lines.append(f"```{lang}")
        self.lines.append(text)
        self.lines.append("```")

    def save(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


# =============================================================================
# 1. VERIFICACIÓN DE INTEGRIDAD
# =============================================================================

def verify_sha256(ifc_path: Path, expected: str = EXPECTED_SHA256) -> None:
    """
    Comprueba que el fichero IFC coincide bit a bit con el manifest oficial.

    Reglas:
    - Si el fichero no existe → FileNotFoundError con instrucciones de descarga.
    - Si el SHA-256 no coincide → ValueError con ambos hashes para diagnóstico.
    - Si coincide → retorno silencioso.
    """
    if not ifc_path.exists():
        raise FileNotFoundError(
            f"No se encuentra {ifc_path}.\n"
            f"Descarga el fichero siguiendo models/samples/SOURCES.md §3.\n"
            f"URL oficial: https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc"
        )

    sha256 = hashlib.sha256()
    with ifc_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    actual = sha256.hexdigest()
    if actual != expected:
        raise ValueError(
            f"SHA-256 no coincide para {ifc_path}.\n"
            f"  Esperado: {expected}\n"
            f"  Obtenido: {actual}\n"
            f"Borra el fichero y repite descarga desde models/samples/SOURCES.md §3."
        )


# =============================================================================
# 2. APERTURA DEL MODELO  [v0.2 — implementado]
# =============================================================================

def open_ifc(ifc_path: Path) -> "IfcFile":
    """
    Abre el fichero IFC con IfcOpenShell tras verificar el SHA-256.

    Returns:
        ifcopenshell.file: modelo cargado en memoria.

    Raises:
        FileNotFoundError / ValueError: ver verify_sha256().
        RuntimeError: si IfcOpenShell no consigue parsear el SPF.
    """
    verify_sha256(ifc_path)
    try:
        model = ifcopenshell.open(str(ifc_path))
    except Exception as e:
        raise RuntimeError(
            f"IfcOpenShell no pudo abrir {ifc_path}: {e}"
        ) from e
    return model


# =============================================================================
# 3. HEADER  [v0.2 — implementado]
# =============================================================================

def report_header(model: "IfcFile") -> dict:
    """
    Extrae metadatos del HEADER del SPF (sección STEP previa a DATA).

    En IfcOpenShell 0.8.x se accede vía model.wrapped_data.header() (función).
    Cada sub-bloque (file_description, file_name, file_schema) se expone como
    método *_py() que devuelve un entity_instance estilo IFC.

    Returns:
        dict con: schema, mvd, options_count, filename, timestamp, author,
        organization, preprocessor_version, originating_system, authorization.
    """
    h = model.wrapped_data.header()
    fd = h.file_description_py()
    fn = h.file_name_py()
    fs = h.file_schema_py()

    # file_description.description es una tupla de strings. El primer elemento
    # contiene la MVD; los siguientes son Options del exportador.
    desc_raw = fd.to_string()
    # Extracción pragmática: primer string entre comillas tras FILE_DESCRIPTION((
    # Para el FZK-Haus el MVD está en la primera entrada.
    mvd = ""
    if "ViewDefinition" in desc_raw:
        # Localizamos el primer 'ViewDefinition' y leemos hasta la siguiente coma cierre
        start = desc_raw.find("'ViewDefinition")
        if start != -1:
            end = desc_raw.find("'", start + 1)
            mvd = desc_raw[start + 1:end]

    options_count = desc_raw.count("Option [")

    # Helper para parsear FILE_NAME(...) string
    def _attr(entity_str: str, idx: int) -> str:
        """Extrae el atributo número idx (0-based) de una representación STEP."""
        try:
            # Parser muy simple: separa por comas top-level
            inside = entity_str[entity_str.index("(") + 1:entity_str.rindex(")")]
            depth = 0
            current = ""
            items = []
            for c in inside:
                if c == "(":
                    depth += 1
                    current += c
                elif c == ")":
                    depth -= 1
                    current += c
                elif c == "," and depth == 0:
                    items.append(current.strip())
                    current = ""
                else:
                    current += c
            items.append(current.strip())
            val = items[idx]
            return val.strip("'").strip("(").strip(")").strip("'")
        except Exception:
            return ""

    name_str = fn.to_string()
    schema_str = fs.to_string()

    return {
        "schema": model.schema,
        "schema_header": _attr(schema_str, 0),
        "mvd": mvd,
        "options_count": options_count,
        "filename": _attr(name_str, 0),
        "timestamp": _attr(name_str, 1),
        "author": _attr(name_str, 2),
        "organization": _attr(name_str, 3),
        "preprocessor_version": _attr(name_str, 4),
        "originating_system": _attr(name_str, 5),
        "authorization": _attr(name_str, 6),
    }


# =============================================================================
# 4. PIRÁMIDE ESPACIAL  [v0.2 — implementado]
# =============================================================================

def walk_spatial_pyramid(model: "IfcFile") -> dict:
    """
    Recorre la pirámide IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace
    siguiendo el inverse attribute `IsDecomposedBy` (que materializa IfcRelAggregates).

    Returns: árbol anidado con id, GlobalId, Name y atributos espaciales clave.
    """
    projects = model.by_type("IfcProject")
    if len(projects) != 1:
        raise ValueError(
            f"Esperado exactamente 1 IfcProject, encontrados {len(projects)}"
        )
    project = projects[0]

    def _site_to_dict(site) -> dict:
        return {
            "id": f"#{site.id()}",
            "guid": site.GlobalId,
            "name": site.Name,
            "ref_latitude": list(site.RefLatitude) if site.RefLatitude else None,
            "ref_longitude": list(site.RefLongitude) if site.RefLongitude else None,
            "ref_elevation": site.RefElevation,
            "buildings": [],
        }

    def _building_to_dict(b) -> dict:
        return {
            "id": f"#{b.id()}",
            "guid": b.GlobalId,
            "name": b.Name,
            "long_name": b.LongName,
            "storeys": [],
        }

    def _storey_to_dict(s) -> dict:
        return {
            "id": f"#{s.id()}",
            "guid": s.GlobalId,
            "name": s.Name,
            "elevation": s.Elevation,
            "spaces": [],
        }

    def _space_to_dict(sp) -> dict:
        return {
            "id": f"#{sp.id()}",
            "guid": sp.GlobalId,
            "name": sp.Name,
            "long_name": sp.LongName,
        }

    tree = {
        "project": {
            "id": f"#{project.id()}",
            "guid": project.GlobalId,
            "name": project.Name,
        },
        "sites": [],
    }

    for rel_agg in project.IsDecomposedBy:
        for site in rel_agg.RelatedObjects:
            if not site.is_a("IfcSite"):
                continue
            site_d = _site_to_dict(site)
            for rel_b in site.IsDecomposedBy:
                for building in rel_b.RelatedObjects:
                    if not building.is_a("IfcBuilding"):
                        continue
                    bld_d = _building_to_dict(building)
                    for rel_s in building.IsDecomposedBy:
                        for storey in rel_s.RelatedObjects:
                            if not storey.is_a("IfcBuildingStorey"):
                                continue
                            st_d = _storey_to_dict(storey)
                            for rel_sp in storey.IsDecomposedBy:
                                for sp in rel_sp.RelatedObjects:
                                    if sp.is_a("IfcSpace"):
                                        st_d["spaces"].append(_space_to_dict(sp))
                            bld_d["storeys"].append(st_d)
                    site_d["buildings"].append(bld_d)
            tree["sites"].append(site_d)

    return tree


# =============================================================================
# 5. CONTENCIÓN ESPACIAL [stub — S4·L]
# =============================================================================

def list_elements_per_storey(model: "IfcFile") -> dict[str, list[dict]]:
    """
    Lista los elementos físicos contenidos en cada planta usando
    `IfcRelContainedInSpatialStructure` (inverse attribute `ContainsElements`).

    [S4·L] Pendiente implementación.
    """
    raise NotImplementedError("S4·L: usar inverse attr ContainsElements")


# =============================================================================
# 6. CONTEO DE ELEMENTOS FÍSICOS  [v0.2 — implementado]
# =============================================================================

# Tipos que count_physical_elements interrogará por defecto. Mantener sincronizado
# con EXPECTED_COUNTS_FZK para que la validación cruzada funcione sin gaps.
PHYSICAL_TYPES: tuple[str, ...] = (
    "IfcWall",
    "IfcWallStandardCase",
    "IfcSlab",
    "IfcWindow",
    "IfcDoor",
    "IfcStair",
    "IfcRailing",
    "IfcOpeningElement",
    "IfcRoof",
    "IfcCovering",
    "IfcFurnishingElement",
)


# =============================================================================
# Psets mínimos NEXUM (dictamen D3B-01 · docs/S3X_dudas_resueltas.md)
# =============================================================================
# Mapa: nombre de clase IFC → { nombre del Pset/Qto → lista de propiedades obligatorias }
# Si una propiedad está presente pero su valor es None, también cuenta como ausente.
# Solo se evalúan instancias de la clase EXACTA (no subtipos) — la auditoría se
# diseña por clase efectiva, no por jerarquía.
PSETS_NEXUM: dict[str, dict[str, list[str]]] = {
    "IfcWallStandardCase": {
        "Pset_WallCommon": [
            "Reference", "LoadBearing", "IsExternal",
            "FireRating", "AcousticRating", "ThermalTransmittance",
        ],
        "Qto_WallBaseQuantities": [
            "Length", "Height", "Width", "GrossSideArea", "NetVolume",
        ],
    },
    "IfcSlab": {
        "Pset_SlabCommon": [
            "Reference", "LoadBearing", "IsExternal",
            "FireRating", "AcousticRating", "ThermalTransmittance",
        ],
        "Qto_SlabBaseQuantities": [
            "GrossArea", "Perimeter", "Width", "GrossVolume",
        ],
    },
    "IfcWindow": {
        "Pset_WindowCommon": [
            "Reference", "IsExternal", "FireRating",
            "ThermalTransmittance", "AcousticRating", "Infiltration",
        ],
        "Qto_WindowBaseQuantities": ["Width", "Height", "Area"],
    },
    "IfcDoor": {
        "Pset_DoorCommon": [
            "Reference", "IsExternal", "FireRating",
            "ThermalTransmittance", "AcousticRating", "Infiltration",
        ],
        "Qto_DoorBaseQuantities": ["Width", "Height", "Area"],
    },
    "IfcSpace": {
        "Pset_SpaceCommon": ["Reference", "Category", "PubliclyAccessible"],
        "Qto_SpaceBaseQuantities": [
            "NetFloorArea", "GrossFloorArea", "NetVolume", "NetCeilingArea",
        ],
    },
}


def count_physical_elements(model: "IfcFile") -> dict[str, int]:
    """
    Cuenta instancias de las clases físicas más relevantes.

    Nota técnica: model.by_type(t) por defecto incluye subtipos en
    IfcOpenShell. Por eso `IfcWall` y `IfcWallStandardCase` pueden devolver
    el mismo conteo si todas las paredes son del subtipo Standard (caso FZK).
    Para excluir subtipos: model.by_type(t, include_subtypes=False).
    """
    return {t: len(model.by_type(t)) for t in PHYSICAL_TYPES}


# =============================================================================
# 7. INVENTARIO DE RELACIONES  [stub — S4·L]
# =============================================================================

def count_relationships(model: "IfcFile") -> dict[str, int]:
    """
    Cuenta instancias de cada subtipo de IfcRelationship.

    [S4·L] Pendiente implementación.
    """
    raise NotImplementedError("S4·L: usar model.by_type() para cada relación")


# =============================================================================
# 7-bis. AUDITORÍA DE PSETS NEXUM  [v0.3 — implementado]
# =============================================================================

def check_minimum_psets(
    model: "IfcFile",
    rules: dict[str, dict[str, list[str]]] = PSETS_NEXUM,
) -> dict[str, dict]:
    """
    Audita el cumplimiento de los Psets mínimos NEXUM por clase IFC.

    Para cada clase listada en `rules`:
    1. Localiza todas las instancias de la clase EXACTA (sin subtipos).
    2. Por cada instancia, comprueba que cada Pset/Qto exigido está presente
       y que cada propiedad obligatoria tiene un valor no nulo.
    3. Acumula estadísticas: total, conformes, no conformes, Psets ausentes,
       propiedades ausentes (top contadores).

    Returns:
        dict[class_name] -> {
            "total": int,
            "compliant": int,
            "non_compliant": int,
            "missing_psets": dict[pset_name -> count],
            "missing_props": dict["pset.prop" -> count],
        }

    Notas técnicas
    --------------
    - Se usa `ifcopenshell.util.element.get_psets()` que normaliza el acceso
      a IfcPropertySet y IfcElementQuantity bajo un dict uniforme.
    - Una propiedad presente con valor `None` cuenta como AUSENTE (un IFC
      válido puede declarar la clave pero dejar el valor sin asignar).
    - El validador NO acepta variantes históricas como `BaseQuantities` (sin
      prefijo `Qto_Wall`). Esa decisión está alineada con el dictamen D3B-01:
      NEXUM exige nombres canónicos buildingSMART.
    """
    import ifcopenshell.util.element  # local import: solo necesario aquí

    results: dict[str, dict] = {}
    for class_name, expected in rules.items():
        elements = model.by_type(class_name, include_subtypes=False)
        summary = {
            "total": len(elements),
            "compliant": 0,
            "non_compliant": 0,
            "missing_psets": {},
            "missing_props": {},
        }
        for e in elements:
            psets = ifcopenshell.util.element.get_psets(e)
            ok = True
            for pset_name, props_needed in expected.items():
                if pset_name not in psets:
                    summary["missing_psets"][pset_name] = (
                        summary["missing_psets"].get(pset_name, 0) + 1
                    )
                    ok = False
                    continue
                pset_props = psets[pset_name]
                for prop in props_needed:
                    if prop not in pset_props or pset_props[prop] is None:
                        key = f"{pset_name}.{prop}"
                        summary["missing_props"][key] = (
                            summary["missing_props"].get(key, 0) + 1
                        )
                        ok = False
            if ok:
                summary["compliant"] += 1
            else:
                summary["non_compliant"] += 1
        results[class_name] = summary
    return results


# =============================================================================
# 8. ANATOMÍA DE UNA ENTIDAD  [v0.3 — implementado]
# =============================================================================

def explain_entity(model: "IfcFile", global_id: str) -> dict:
    """
    Devuelve TODAS las relaciones que tocan a una entidad concreta.

    Args:
        model: modelo IFC cargado.
        global_id: GlobalId (GUID base64 de 22 caracteres) de la entidad.

    Returns:
        dict con la anatomía completa: identidad, contención espacial, tipo,
        propiedades, materiales, huecos+fillers, conexiones path y boundaries.

    Estructura del retorno
    ----------------------
        {
          "identity": {"id", "guid", "class", "name", "object_type",
                       "predefined_type"},
          "contained_in": ["#479 IfcBuildingStorey 'Erdgeschoss'", ...],
          "types":        ["#15234 IfcWallType 'Leichtbeton 102890359 240'", ...],
          "properties":   ["IfcPropertySet 'Pset_WallCommon'", ...],
          "materials":    ["IfcMaterialLayerSetUsage", ...],
          "openings":     [{"opening": "#... 'Innentuer-1'", "filled_by":
                            "#... 'Tuer-EG-1' (IfcDoor)"}, ...],
          "connections":  ["#17040 IfcWallStandardCase 'Wand-Int-ERDG-2'", ...],
          "boundaries":   [{"space": "#20909 '4'", "name": "2ndLevel",
                            "description": "2a", "physical": "PHYSICAL",
                            "internal": "INTERNAL"}, ...],
        }

    Raises:
        ValueError: si no existe una entidad con ese GlobalId en el modelo.
    """
    target = model.by_guid(global_id) if hasattr(model, "by_guid") else None
    if target is None:
        # Fallback: búsqueda manual
        matches = [e for e in model if hasattr(e, "GlobalId") and e.GlobalId == global_id]
        if not matches:
            raise ValueError(f"No existe entidad con GlobalId='{global_id}' en el modelo")
        target = matches[0]

    def _ref(e) -> str:
        """Representación corta de una entidad IFC."""
        name = getattr(e, "Name", None) or ""
        return f"#{e.id()} {e.is_a()} '{name}'"

    out: dict = {
        "identity": {
            "id": f"#{target.id()}",
            "guid": target.GlobalId,
            "class": target.is_a(),
            "name": target.Name,
            "object_type": getattr(target, "ObjectType", None),
            "predefined_type": getattr(target, "PredefinedType", None),
        },
        "contained_in": [],
        "types": [],
        "properties": [],
        "materials": [],
        "openings": [],
        "connections": [],
        "boundaries": [],
    }

    # Contención espacial (ContainedInStructure → IfcRelContainedInSpatialStructure)
    for rel in getattr(target, "ContainedInStructure", []) or []:
        out["contained_in"].append(_ref(rel.RelatingStructure))

    # Tipo (IsTypedBy → IfcRelDefinesByType)
    for rel in getattr(target, "IsTypedBy", []) or []:
        out["types"].append(_ref(rel.RelatingType))

    # Propiedades y cantidades (IsDefinedBy → IfcRelDefinesByProperties)
    for rel in getattr(target, "IsDefinedBy", []) or []:
        if rel.is_a("IfcRelDefinesByProperties"):
            defs = rel.RelatingPropertyDefinition
            name = getattr(defs, "Name", "") or ""
            out["properties"].append(f"{defs.is_a()} '{name}'")

    # Asociaciones (HasAssociations → IfcRelAssociatesMaterial / Classification)
    for rel in getattr(target, "HasAssociations", []) or []:
        related = None
        if hasattr(rel, "RelatingMaterial"):
            related = rel.RelatingMaterial
        elif hasattr(rel, "RelatingClassification"):
            related = rel.RelatingClassification
        if related is not None:
            label = related.is_a() if hasattr(related, "is_a") else str(related)
            out["materials"].append(f"{rel.is_a()} → {label}")

    # Huecos (HasOpenings → IfcRelVoidsElement) y sus fillers (HasFillings)
    for rel in getattr(target, "HasOpenings", []) or []:
        opening = rel.RelatedOpeningElement
        entry = {"opening": _ref(opening), "filled_by": None}
        for fill_rel in getattr(opening, "HasFillings", []) or []:
            filler = fill_rel.RelatedBuildingElement
            entry["filled_by"] = _ref(filler)
        out["openings"].append(entry)

    # Conexiones (ConnectedTo + ConnectedFrom → IfcRelConnectsPathElements y similares)
    connected = []
    for rel in getattr(target, "ConnectedTo", []) or []:
        other = rel.RelatedElement
        if other.id() != target.id():
            connected.append(_ref(other))
    for rel in getattr(target, "ConnectedFrom", []) or []:
        other = rel.RelatingElement
        if other.id() != target.id():
            connected.append(_ref(other))
    out["connections"] = connected

    # Boundaries (inverso: barremos todas las IfcRelSpaceBoundary)
    for sb in model.by_type("IfcRelSpaceBoundary"):
        if sb.RelatedBuildingElement and sb.RelatedBuildingElement.id() == target.id():
            sp = sb.RelatingSpace
            sp_name = getattr(sp, "Name", None) or ""
            out["boundaries"].append({
                "space": f"#{sp.id()} '{sp_name}'",
                "name": sb.Name,
                "description": sb.Description,
                "physical": sb.PhysicalOrVirtualBoundary,
                "internal": sb.InternalOrExternalBoundary,
            })

    return out


# =============================================================================
# 9. VALIDACIONES DE COHERENCIA  [stub — S4·L / S6·L]
# =============================================================================

def validate_doors_have_openings(model: "IfcFile") -> list[dict]:
    """
    Reporta IfcDoor / IfcWindow que NO tienen IfcRelFillsElement asociada.

    [S4·L] Pendiente implementación.
    """
    raise NotImplementedError("S4·L: validar inverse FillsVoids")


def validate_unique_project(model: "IfcFile") -> None:
    """
    Comprueba la invariante 'un solo IfcProject por fichero'.

    [S4·L] Pendiente implementación.
    """
    raise NotImplementedError("S4·L: aserción de unicidad IfcProject")


# =============================================================================
# 10. RENDERIZADO DEL INFORME (consola + Markdown)
# =============================================================================

def _render_header(w: DualWriter, header: dict) -> None:
    w.heading("HEADER del SPF", level=2)
    w.line()
    w.line(f"- Schema (modelo)       : {header['schema']}")
    w.line(f"- Schema (HEADER raw)   : {header['schema_header']}")
    w.line(f"- MVD                   : {header['mvd']}")
    w.line(f"- Options del exportador: {header['options_count']}")
    w.line(f"- Filename              : {header['filename']}")
    w.line(f"- Timestamp             : {header['timestamp']}")
    w.line(f"- Author                : {header['author']}")
    w.line(f"- Organization          : {header['organization']}")
    w.line(f"- Preprocessor version  : {header['preprocessor_version']}")
    w.line(f"- Originating system    : {header['originating_system']}")
    w.line(f"- Authorization         : {header['authorization']}")
    w.line()


def _render_pyramid(w: DualWriter, tree: dict) -> None:
    w.heading("Pirámide espacial", level=2)
    w.line()
    p = tree["project"]
    w.line(f"IfcProject       {p['id']} '{p['name']}' (GUID: {p['guid']})")
    for site in tree["sites"]:
        lat = site["ref_latitude"]
        lon = site["ref_longitude"]
        lat_str = f"{lat[0]}°{lat[1]}'{lat[2]}\"N" if lat else "n/d"
        lon_str = f"{lon[0]}°{lon[1]}'{lon[2]}\"E" if lon else "n/d"
        w.line(
            f" └── IfcSite      {site['id']} '{site['name']}' "
            f"(lat {lat_str}, lon {lon_str}, elev {site['ref_elevation']}m)"
        )
        for b in site["buildings"]:
            w.line(
                f"      └── IfcBuilding {b['id']} '{b['name']}' "
                f"(long_name: {b['long_name']})"
            )
            for st in b["storeys"]:
                w.line(
                    f"           └── IfcBuildingStorey {st['id']} '{st['name']}' "
                    f"(Z={st['elevation']}m, {len(st['spaces'])} spaces)"
                )
                for sp in st["spaces"]:
                    w.line(
                        f"                   └── IfcSpace {sp['id']} "
                        f"'{sp['name']}' ({sp['long_name']})"
                    )
    w.line()


def _render_counts(w: DualWriter, counts: dict[str, int]) -> None:
    w.heading("Conteo de elementos físicos", level=2)
    w.line()
    w.line("| Tipo                          | Conteo |")
    w.line("|-------------------------------|-------:|")
    for t, n in counts.items():
        w.line(f"| {t:<29s} | {n:>6d} |")
    w.line()


def _render_invariants(w: DualWriter, model: "IfcFile") -> None:
    w.heading("Validación cruzada vs EXPECTED_COUNTS_FZK", level=2)
    w.line()
    w.line("| Tipo                              | Esperado | Obtenido | Estado |")
    w.line("|-----------------------------------|---------:|---------:|:------:|")
    n_ok = 0
    n_fail = 0
    for t, exp in EXPECTED_COUNTS_FZK.items():
        got = len(model.by_type(t))
        status = "OK" if got == exp else "FAIL"
        if got == exp:
            n_ok += 1
        else:
            n_fail += 1
        w.line(f"| {t:<33s} | {exp:>8d} | {got:>8d} |  {status:<4s}  |")
    w.line()
    w.line(f"**Resumen:** {n_ok} OK · {n_fail} FAIL · {len(EXPECTED_COUNTS_FZK)} total")
    w.line()


def _render_pset_audit(w: DualWriter, audit: dict[str, dict]) -> None:
    w.heading("Auditoría Pset NEXUM", level=2)
    w.line()
    w.line("Resumen por clase (Psets mínimos según dictamen D3B-01):")
    w.line()
    w.line("| Clase                | Total | OK | No conformes | % cumplim. |")
    w.line("|----------------------|------:|---:|-------------:|-----------:|")
    for cls, s in audit.items():
        pct = (s["compliant"] / s["total"] * 100) if s["total"] else 0
        w.line(
            f"| {cls:<20s} | {s['total']:>5d} | {s['compliant']:>2d} | "
            f"{s['non_compliant']:>12d} | {pct:>9.0f}% |"
        )
    w.line()
    # Detalle de propiedades ausentes (top 5 por clase)
    w.heading("Detalle de propiedades ausentes (top 5 por clase)", level=3)
    w.line()
    for cls, s in audit.items():
        if s["total"] == 0:
            continue
        w.line(f"**{cls}** ({s['total']} elementos):")
        w.line()
        if s["missing_psets"]:
            for pset_name, count in s["missing_psets"].items():
                w.line(f"- Pset entero ausente: `{pset_name}` en {count}/{s['total']} elementos")
        if s["missing_props"]:
            top = sorted(s["missing_props"].items(), key=lambda x: -x[1])[:5]
            for prop_key, count in top:
                w.line(f"- `{prop_key}` ausente en {count}/{s['total']} elementos")
        w.line()


def _render_entity_anatomy(w: DualWriter, anatomy: dict) -> None:
    id_ = anatomy["identity"]
    w.heading(f"Anatomía de {id_['id']} {id_['class']} '{id_['name']}'", level=2)
    w.line()
    w.line(f"- GlobalId        : `{id_['guid']}`")
    w.line(f"- ObjectType      : {id_['object_type']}")
    w.line(f"- PredefinedType  : {id_['predefined_type']}")
    w.line()

    sections = [
        ("Contención espacial (IfcRelContainedInSpatialStructure)", "contained_in"),
        ("Tipo (IfcRelDefinesByType)", "types"),
        ("Propiedades y cantidades (IfcRelDefinesByProperties)", "properties"),
        ("Materiales y clasificaciones (HasAssociations)", "materials"),
        ("Conexiones (IfcRelConnectsPathElements)", "connections"),
    ]
    for label, key in sections:
        w.line(f"### {label}")
        w.line()
        items = anatomy[key]
        if not items:
            w.line("_(ninguna)_")
        else:
            for it in items:
                w.line(f"- {it}")
        w.line()

    # Huecos (estructura especial: dict con opening + filled_by)
    w.line("### Huecos (IfcRelVoidsElement) y rellenos (IfcRelFillsElement)")
    w.line()
    if not anatomy["openings"]:
        w.line("_(ninguno — elemento sin aperturas)_")
    else:
        for op in anatomy["openings"]:
            filler = op["filled_by"] or "_(sin filler)_"
            w.line(f"- {op['opening']} → {filler}")
    w.line()

    # Boundaries (estructura especial)
    w.line("### Boundaries (IfcRelSpaceBoundary, inverso)")
    w.line()
    if not anatomy["boundaries"]:
        w.line("_(ninguno — elemento no toca a ningún IfcSpace)_")
    else:
        for b in anatomy["boundaries"]:
            w.line(
                f"- Hacia space {b['space']} · Name={b['name']} · "
                f"Description={b['description']} · {b['internal']} · {b['physical']}"
            )
    w.line()


# =============================================================================
# 11. ENTRY POINT
# =============================================================================

def main(argv: list[str]) -> int:
    """
    Entry point CLI.

    Uso:
        python scripts/s3l_ifc_inspect.py [ruta_al_ifc]
    """
    if len(argv) > 1:
        ifc_path = Path(argv[1])
    else:
        ifc_path = DEFAULT_IFC_PATH

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"S3X_lab_run_{timestamp}.md"

    w = DualWriter()
    w.heading(f"Lab S3·X — Inspección IFC", level=1)
    w.line()
    w.line(f"- Fecha de ejecución : {datetime.now().isoformat(timespec='seconds')}")
    w.line(f"- Fichero IFC        : `{ifc_path}`")
    w.line(f"- Script             : `scripts/s3l_ifc_inspect.py` v0.2")
    w.line(f"- IfcOpenShell       : {ifcopenshell.version}")
    w.line()

    try:
        model = open_ifc(ifc_path)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        w.heading("ERROR al abrir el modelo", level=2)
        w.code(str(e))
        w.save(out_path)
        print(f"\n[!] Informe parcial guardado en: {out_path}", file=sys.stderr)
        return 1

    w.line(f"- SHA-256 verificado : `{EXPECTED_SHA256}`")
    w.line(f"- Entidades totales  : {len(list(model))}")
    w.line()

    header = report_header(model)
    _render_header(w, header)

    tree = walk_spatial_pyramid(model)
    _render_pyramid(w, tree)

    counts = count_physical_elements(model)
    _render_counts(w, counts)

    _render_invariants(w, model)

    # Auditoría Pset NEXUM (v0.3)
    audit = check_minimum_psets(model)
    _render_pset_audit(w, audit)

    # Anatomía de la entidad de referencia (v0.3)
    # Por defecto: muro #15042 (GlobalId 2XPyKWY018sA1ygZKgQPtU)
    # Se puede sobrescribir con segundo argumento CLI.
    default_guid = "2XPyKWY018sA1ygZKgQPtU"
    guid = argv[2] if len(argv) > 2 else default_guid
    try:
        anatomy = explain_entity(model, guid)
        _render_entity_anatomy(w, anatomy)
    except ValueError as e:
        w.heading(f"Anatomía de entidad '{guid}'", level=2)
        w.code(f"ERROR: {e}")
        w.line()

    w.heading("Funciones pendientes para S4·L", level=2)
    w.line()
    pending = [
        "list_elements_per_storey",
        "count_relationships",
        "validate_doors_have_openings",
        "validate_unique_project",
    ]
    for p in pending:
        w.line(f"- `{p}`")
    w.line()

    w.save(out_path)
    print(f"\n[OK] Informe guardado en: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
