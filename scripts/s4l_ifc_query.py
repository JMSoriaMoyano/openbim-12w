"""
s4l_ifc_query.py · OpenBIM 12 semanas · S4·L (Lun 01/06/2026)
==============================================================
Sesión 4 · Lunes · IfcOpenShell: lectura y consultas.

Objetivo: ofrecer 3 consultas reproducibles sobre cualquier IFC.
    Q1 · count_by_type(model)           → conteo de entidades por tipo
    Q2 · find_by_guid(model, guid)      → localizar entidad por GUID
    Q3 · read_psets(entity)             → leer Psets/BaseQuantities de una entidad

Diseño:
    - Sin dependencias más allá de ifcopenshell (stable, ya pineado en requirements.txt).
    - Funciones puras: aceptan modelo/entidad, devuelven dicts JSON-serializables.
    - CLI mínima para correr cada consulta independientemente desde terminal.
    - Reutiliza el patrón de s3l_ifc_inspect.py (open_ifc + report_header).

Uso CLI:
    python scripts/s4l_ifc_query.py --ifc <ruta.ifc> --query header
    python scripts/s4l_ifc_query.py --ifc <ruta.ifc> --query counts [--level bruto|root|product] [--top N]
    python scripts/s4l_ifc_query.py --ifc <ruta.ifc> --query guid   --guid <GUID>
    python scripts/s4l_ifc_query.py --ifc <ruta.ifc> --query psets  --guid <GUID>

Autor: José M. Soria (NEXUM)
Versión: 0.5 (S4·X Bloque A · refactor: helpers comunes + MODELS_DIR)

Changelog
---------
0.5 (S4·X · 03/06): Extracción de load_ifc, report_header y _get_type_object
     a scripts/_ifc_helpers.py. Sin cambios funcionales. MODELS_DIR resuelve
     rutas relativas automáticamente desde CLI.
0.4 (S4·L Bloque D · 01/06): read_psets con valores reales + type psets.
0.3 (S4·L Bloque C · 01/06): find_by_guid L3 estructurado en 6 secciones.
0.2 (S4·L Bloque B · 01/06): count_by_type con 3 niveles bruto/root/product.
0.1 (S4·L Bloque A · 01/06): Esqueleto + report_header.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from typing import Any

import ifcopenshell

from _ifc_helpers import (
    load_ifc,
    report_header,
    resolve_model_path,
    get_type_object as _get_type_object,
)


# ---------------------------------------------------------------------------
# Q1 · Conteo por tipo  (a implementar en Bloque B)
# ---------------------------------------------------------------------------

# Niveles válidos para count_by_type. Cada uno responde una pregunta distinta:
#   - bruto   : todas las entidades STEP del fichero (incluye geometría primitiva).
#   - root    : solo entidades con GlobalId (heredan de IfcRoot). Inventario semántico.
#   - product : solo elementos físicos colocables en el espacio (heredan de IfcProduct).
COUNT_LEVELS = ("bruto", "root", "product")


def count_by_type(
    model: ifcopenshell.file,
    level: str = "root",
) -> dict[str, int]:
    """Devuelve {clase_IFC: nº instancias}, ordenado descendente por valor.

    Parámetros
    ----------
    model : ifcopenshell.file
        Modelo IFC ya cargado con load_ifc().
    level : {'bruto', 'root', 'product'}, default 'root'
        Nivel de filtrado:
          - 'bruto'   : iter(model) — TODAS las entidades STEP (geometría incluida).
          - 'root'    : model.by_type('IfcRoot') — solo entidades con GlobalId.
          - 'product' : model.by_type('IfcProduct') — solo elementos físicos.

    Devuelve
    --------
    dict[str, int]
        Diccionario ordenado descendente por valor. Las claves son los nombres
        de clase exactos (resultado de entity.is_a()), sin agregar subtipos.

    Notas
    -----
    - 'root' incluye también tipos abstractos (IfcRelAggregates, IfcOwnerHistory…)
      porque heredan de IfcRoot. Es el inventario "semántico" completo, no solo físico.
    - 'product' es el equivalente más cercano al "inventario de obra":
      muros, forjados, ventanas, espacios, sitios… excluyendo relaciones y propiedades.
    """
    if level not in COUNT_LEVELS:
        raise ValueError(
            f"level inválido: {level!r}. Debe ser uno de {COUNT_LEVELS}"
        )

    if level == "bruto":
        iterable = iter(model)
    elif level == "root":
        iterable = model.by_type("IfcRoot")
    else:  # product
        iterable = model.by_type("IfcProduct")

    counts: dict[str, int] = {}
    for entity in iterable:
        cls = entity.is_a()
        counts[cls] = counts.get(cls, 0) + 1

    # Ordenar descendente por valor, alfabético como desempate estable.
    sorted_items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return dict(sorted_items)


# ---------------------------------------------------------------------------
# Q2 · Buscar por GUID (L3 · estructurado completo)
# ---------------------------------------------------------------------------

def _format_creation_date(value: Any) -> str | None:
    """Convierte timestamp IFC (int Unix o str ISO) a ISO 8601 legible.

    IFC2x3 usa int (segundos desde epoch). IFC4 puede usar IfcDateTime (str ISO).
    Devuelve None si el valor es None o no parseable.
    """
    if value is None:
        return None
    if isinstance(value, int):
        try:
            return _dt.datetime.fromtimestamp(value).isoformat(timespec="seconds")
        except (OSError, OverflowError, ValueError):
            return None
    if isinstance(value, str):
        return value  # asumimos que ya viene formateado
    return str(value)


def _entity_ref(entity: Any) -> dict[str, Any] | None:
    """Devuelve {id, is_a, name, guid} de una entidad, o None si entity es None."""
    if entity is None:
        return None
    return {
        "id": entity.id(),
        "is_a": entity.is_a(),
        "name": getattr(entity, "Name", None),
        "guid": getattr(entity, "GlobalId", None),
    }


def _get_spatial_container(entity: Any) -> Any:
    """Devuelve el contenedor espacial directo (BuildingStorey, Space…) o None.

    Usa IfcRelContainedInSpatialStructure inverso. Solo aplica a IfcElement.
    """
    rels = getattr(entity, "ContainedInStructure", None) or []
    if not rels:
        return None
    return rels[0].RelatingStructure


def _count_relationships(entity: Any) -> dict[str, int | bool]:
    """Cuenta relaciones inversas relevantes. No las lista, solo las cuenta."""
    def _len(attr: str) -> int:
        return len(getattr(entity, attr, None) or [])

    return {
        "is_decomposed_by_count": _len("IsDecomposedBy"),
        "decomposes_count": _len("Decomposes"),
        "is_defined_by_count": _len("IsDefinedBy"),
        "is_typed_by": bool(getattr(entity, "IsTypedBy", None)),
        "has_openings_count": _len("HasOpenings"),
        "fills_voids_count": _len("FillsVoids"),
        "connected_to_count": _len("ConnectedTo"),
        "connected_from_count": _len("ConnectedFrom"),
        "boundary_count": _len("ProvidesBoundaries"),
        "referenced_by_count": _len("ReferencedBy"),
    }


def _summarize_psets(entity: Any) -> dict[str, Any]:
    """Devuelve resumen agregado de Psets/Qto/Vendor (nombres y counts, no valores).

    Los valores serán cubiertos por Q3 (read_psets) en Bloque D.
    """
    pset_count = 0
    qto_count = 0
    vendor_count = 0
    names: list[str] = []

    for rel in getattr(entity, "IsDefinedBy", None) or []:
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        pdef = rel.RelatingPropertyDefinition
        name = getattr(pdef, "Name", None) or "<sin nombre>"
        names.append(name)
        if pdef.is_a("IfcElementQuantity"):
            qto_count += 1
        elif pdef.is_a("IfcPropertySet"):
            if name.startswith("Pset_"):
                pset_count += 1
            else:
                vendor_count += 1

    return {
        "pset_count": pset_count,
        "qto_count": qto_count,
        "vendor_pset_count": vendor_count,
        "pset_names": names,
    }


def find_by_guid(model: ifcopenshell.file, guid: str) -> dict[str, Any] | None:
    """Localiza una entidad por GlobalId y devuelve resumen estructurado L3.

    Devuelve None si el GUID no existe en el modelo.

    Estructura de salida (6 secciones):
        identity         : id, guid, is_a, name, description, object_type, predefined_type
        authoring        : owning_user, owning_application, creation_date, last_modified_date
        spatial_container: ref al contenedor espacial directo (BuildingStorey/Space…)
        type_object      : ref al IfcTypeObject asociado
        relationships    : counts de relaciones inversas relevantes
        psets_summary    : counts y nombres de Psets/Qto/Vendor (valores en Q3)

    Notas
    -----
    - L3 es complementario a explain_entity() de S3·L: aquel es narrativo,
      este es estructurado JSON-serializable para consumo programático.
    - Los valores reales de los Psets se obtienen con Q3 (read_psets).
    """
    try:
        entity = model.by_guid(guid)
    except RuntimeError:
        return None

    # Identidad
    identity = {
        "id": entity.id(),
        "guid": guid,
        "is_a": entity.is_a(),
        "name": getattr(entity, "Name", None),
        "description": getattr(entity, "Description", None),
        "object_type": getattr(entity, "ObjectType", None),
        "predefined_type": getattr(entity, "PredefinedType", None),
    }

    # Autoría (OwnerHistory)
    oh = getattr(entity, "OwnerHistory", None)
    if oh is None:
        authoring = None
    else:
        owning_user = getattr(oh, "OwningUser", None)
        owning_app = getattr(oh, "OwningApplication", None)
        user_name = None
        app_name = None
        if owning_user is not None:
            person = getattr(owning_user, "ThePerson", None)
            user_name = getattr(person, "FamilyName", None) or getattr(person, "Identification", None)
        if owning_app is not None:
            app_name = getattr(owning_app, "ApplicationFullName", None) or getattr(owning_app, "ApplicationIdentifier", None)
        authoring = {
            "owning_user": user_name,
            "owning_application": app_name,
            "creation_date": _format_creation_date(getattr(oh, "CreationDate", None)),
            "last_modified_date": _format_creation_date(getattr(oh, "LastModifiedDate", None)),
        }

    return {
        "identity": identity,
        "authoring": authoring,
        "spatial_container": _entity_ref(_get_spatial_container(entity)),
        "type_object": _entity_ref(_get_type_object(entity)),
        "relationships": _count_relationships(entity),
        "psets_summary": _summarize_psets(entity),
    }


# ---------------------------------------------------------------------------
# Q3 · Leer Psets con valores reales (instancia + tipo)
# ---------------------------------------------------------------------------

def _unwrap_value(prop: Any) -> Any:
    """Extrae el valor escalar/lista de cualquier IfcProperty o IfcPhysicalQuantity.

    Maneja los tipos más comunes:
      - IfcPropertySingleValue       → .NominalValue.wrappedValue (o None)
      - IfcPropertyEnumeratedValue   → lista de wrappedValue
      - IfcPropertyListValue         → lista de wrappedValue
      - IfcPropertyBoundedValue      → dict {lower, upper, set_point}
      - IfcPhysicalSimpleQuantity    → .LengthValue / .AreaValue / .VolumeValue / etc.
      - IfcPropertyReferenceValue    → resumen del objeto referenciado
      - Cualquier otro               → str(prop) como fallback seguro
    """
    # --- IfcPropertySingleValue ---
    if prop.is_a("IfcPropertySingleValue"):
        nv = getattr(prop, "NominalValue", None)
        return getattr(nv, "wrappedValue", None) if nv is not None else None

    # --- IfcPropertyEnumeratedValue ---
    if prop.is_a("IfcPropertyEnumeratedValue"):
        values = getattr(prop, "EnumerationValues", None) or []
        return [getattr(v, "wrappedValue", None) for v in values]

    # --- IfcPropertyListValue ---
    if prop.is_a("IfcPropertyListValue"):
        values = getattr(prop, "ListValues", None) or []
        return [getattr(v, "wrappedValue", None) for v in values]

    # --- IfcPropertyBoundedValue ---
    if prop.is_a("IfcPropertyBoundedValue"):
        return {
            "lower": getattr(getattr(prop, "LowerBoundValue", None), "wrappedValue", None),
            "upper": getattr(getattr(prop, "UpperBoundValue", None), "wrappedValue", None),
            "set_point": getattr(getattr(prop, "SetPointValue", None), "wrappedValue", None),
        }

    # --- IfcPropertyReferenceValue ---
    if prop.is_a("IfcPropertyReferenceValue"):
        ref = getattr(prop, "PropertyReference", None)
        if ref is None:
            return None
        return {
            "is_a": ref.is_a(),
            "name": getattr(ref, "Name", None),
        }

    # --- IfcPhysicalSimpleQuantity (Length/Area/Volume/Count/Weight/Time) ---
    if prop.is_a("IfcPhysicalSimpleQuantity"):
        for attr in ("LengthValue", "AreaValue", "VolumeValue",
                     "CountValue", "WeightValue", "TimeValue"):
            val = getattr(prop, attr, None)
            if val is not None:
                return val
        return None

    # --- Fallback ---
    return str(prop)


def _read_property_set(pset: Any) -> dict[str, Any]:
    """Devuelve {nombre_propiedad: valor} para un IfcPropertySet o IfcElementQuantity.

    - IfcPropertySet usa atributo .HasProperties
    - IfcElementQuantity usa atributo .Quantities
    """
    result: dict[str, Any] = {}

    if pset.is_a("IfcPropertySet"):
        items = getattr(pset, "HasProperties", None) or []
    elif pset.is_a("IfcElementQuantity"):
        items = getattr(pset, "Quantities", None) or []
    else:
        return result

    for item in items:
        name = getattr(item, "Name", None) or "<sin nombre>"
        result[name] = _unwrap_value(item)

    return result


def _split_instance_psets(entity: Any) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Separa los PropertyDefinitions de la INSTANCIA en (psets, quantities).

    Devuelve (instance_psets, instance_quantities), cada uno {nombre: {prop: valor}}.
    """
    psets: dict[str, dict[str, Any]] = {}
    quantities: dict[str, dict[str, Any]] = {}

    for rel in getattr(entity, "IsDefinedBy", None) or []:
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        pdef = rel.RelatingPropertyDefinition
        name = getattr(pdef, "Name", None) or "<sin nombre>"
        if pdef.is_a("IfcElementQuantity"):
            quantities[name] = _read_property_set(pdef)
        elif pdef.is_a("IfcPropertySet"):
            psets[name] = _read_property_set(pdef)
        # otras IfcPropertyDefinition (rarezas) se ignoran

    return psets, quantities


def _get_type_psets(entity: Any) -> dict[str, dict[str, Any]]:
    """Devuelve {nombre_pset: {prop: valor}} de los PropertySets HEREDADOS del IfcTypeObject.

    Si la entidad no tiene tipo asociado, devuelve dict vacío.
    Solo recoge IfcPropertySet (los IfcElementQuantity raramente cuelgan del type).
    """
    type_obj = _get_type_object(entity)
    if type_obj is None:
        return {}

    result: dict[str, dict[str, Any]] = {}
    for pset in getattr(type_obj, "HasPropertySets", None) or []:
        if not pset.is_a("IfcPropertySet"):
            continue
        name = getattr(pset, "Name", None) or "<sin nombre>"
        result[name] = _read_property_set(pset)

    return result


def read_psets(entity: ifcopenshell.entity_instance) -> dict[str, Any]:
    """Devuelve la radiografía completa de propiedades de una entidad.

    Estructura de salida (5 secciones):
        entity              : id, guid, is_a, name (identificación mínima)
        instance_psets      : {nombre_pset: {propiedad: valor}} — IfcPropertySet directos
        instance_quantities : {nombre_qto: {propiedad: valor}} — IfcElementQuantity directos
        type_psets          : {nombre_pset: {propiedad: valor}} — heredados del IfcTypeObject
        summary             : counts agregados

    Diseño
    ------
    - Incluye valores None explícitamente (auditoría LOIN: declarada pero vacía ≠ ausente).
    - No deduplica entre instance y type (puede haber overrides; el auditor decide).
    - Maneja los 5 tipos de IfcProperty + IfcPhysicalSimpleQuantity vía _unwrap_value().
    - Valores en unidades declaradas en IfcUnitAssignment del proyecto (no normaliza).
    """
    instance_psets, instance_quantities = _split_instance_psets(entity)
    type_psets = _get_type_psets(entity)

    # Conteo total de propiedades individuales (suma de claves de cada subdict)
    total_props = (
        sum(len(v) for v in instance_psets.values())
        + sum(len(v) for v in instance_quantities.values())
        + sum(len(v) for v in type_psets.values())
    )

    return {
        "entity": {
            "id": entity.id(),
            "guid": getattr(entity, "GlobalId", None),
            "is_a": entity.is_a(),
            "name": getattr(entity, "Name", None),
        },
        "instance_psets": instance_psets,
        "instance_quantities": instance_quantities,
        "type_psets": type_psets,
        "summary": {
            "instance_psets_count": len(instance_psets),
            "instance_quantities_count": len(instance_quantities),
            "type_psets_count": len(type_psets),
            "total_properties": total_props,
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="S4·L · Consultas básicas sobre IFC (counts, guid, psets)"
    )
    parser.add_argument("--ifc", required=True, help="Ruta al fichero IFC")
    parser.add_argument(
        "--query",
        required=True,
        choices=["header", "counts", "guid", "psets"],
        help="Consulta a ejecutar",
    )
    parser.add_argument("--guid", help="GUID requerido para query=guid y query=psets")
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Limitar salida de 'counts' a los N tipos más frecuentes (default 20)",
    )
    parser.add_argument(
        "--level",
        choices=list(COUNT_LEVELS),
        default="root",
        help="Nivel de filtrado para 'counts' (default 'root')",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    # Resolución de ruta: si el usuario pasa solo el nombre del fichero,
    # se busca automáticamente en models/samples/_local/.
    ifc_path = resolve_model_path(args.ifc)

    try:
        model = load_ifc(ifc_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.query == "header":
        out = report_header(model, ifc_path)
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return 0

    if args.query == "counts":
        out = count_by_type(model, level=args.level)
        # Limitar a top N
        top_n = dict(list(out.items())[: args.top])
        # Cabecera resumen previa al JSON para contexto
        total_classes = len(out)
        total_instances = sum(out.values())
        print(
            f"# level={args.level} · clases={total_classes} · "
            f"instancias={total_instances} · top={min(args.top, total_classes)}"
        )
        print(json.dumps(top_n, indent=2, ensure_ascii=False))
        return 0

    if args.query in {"guid", "psets"}:
        if not args.guid:
            print(f"[ERROR] --guid es obligatorio para query={args.query}", file=sys.stderr)
            return 2

        if args.query == "guid":
            out = find_by_guid(model, args.guid)
            if out is None:
                print(f"[INFO] GUID no encontrado: {args.guid}")
                return 0
            print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
            return 0

        # query == "psets"
        try:
            entity = model.by_guid(args.guid)
        except RuntimeError:
            print(f"[INFO] GUID no encontrado: {args.guid}")
            return 0
        out = read_psets(entity)
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
