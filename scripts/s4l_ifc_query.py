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
Versión: 0.3 (Bloque C · find_by_guid L3 estructurado)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path
from typing import Any

import ifcopenshell

# ---------------------------------------------------------------------------
# Utilidades comunes (reutilizadas de s3l_ifc_inspect.py)
# ---------------------------------------------------------------------------

def load_ifc(path: str | Path) -> ifcopenshell.file:
    """Carga un IFC desde disco con validación mínima."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"IFC no encontrado: {p}")
    if not p.suffix.lower() == ".ifc":
        raise ValueError(f"Extensión inesperada (esperado .ifc): {p.suffix}")
    model = ifcopenshell.open(str(p))
    return model


def report_header(model: ifcopenshell.file, path: str | Path) -> dict[str, Any]:
    """Cabecera mínima: schema, MVD, archivo, totales."""
    schema = model.schema
    header = model.header
    return {
        "file": str(path),
        "schema": schema,
        "mvd": header.file_description.description[0] if header.file_description.description else None,
        "originating_system": header.file_name.originating_system,
        "timestamp": header.file_name.time_stamp,
        "total_entities": len(list(model)),
    }


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


def _get_type_object(entity: Any) -> Any:
    """Devuelve el IfcTypeObject asociado (vía IsTypedBy / IsDefinedBy) o None.

    IFC4 usa IsTypedBy (IfcRelDefinesByType); IFC2x3 usaba IsDefinedBy con
    RelatingType. Probamos ambos para robustez.
    """
    typed_by = getattr(entity, "IsTypedBy", None) or []
    if typed_by:
        return typed_by[0].RelatingType
    # Fallback IFC2x3
    for rel in getattr(entity, "IsDefinedBy", None) or []:
        if rel.is_a("IfcRelDefinesByType"):
            return rel.RelatingType
    return None


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
# Q3 · Leer Psets  (a implementar en Bloque D)
# ---------------------------------------------------------------------------

def read_psets(entity: ifcopenshell.entity_instance) -> dict[str, dict[str, Any]]:
    """Devuelve {nombre_pset: {propiedad: valor, ...}} para una entidad.

    Incluye Psets, Qto y propiedades vendor-specific.

    TODO Bloque D:
        - Iterar IsDefinedBy → RelDefinesByProperties → RelatingPropertyDefinition.
        - Aceptar IfcPropertySet, IfcElementQuantity.
        - Extraer valores con .wrappedValue cuando aplique.
        - Manejar propiedades nulas y tipos enumerados.
    """
    raise NotImplementedError("Bloque D: pendiente de implementar")


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

    try:
        model = load_ifc(args.ifc)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.query == "header":
        out = report_header(model, args.ifc)
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
