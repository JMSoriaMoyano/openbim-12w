"""
s4x_ifc_lab.py · OpenBIM 12 semanas · S4·X (Mie 03/06/2026)
============================================================
Sesión 4 · Miércoles · Lab IfcOpenShell: consultas avanzadas reutilizables.

Objetivo: 3 consultas que combinan las primitivas de S4·L para responder
preguntas reales del workflow ISO 19650 (necesidad → regla → evidencia).

    Q1 · query_by_type_with_psets(model, ifc_type, pset_names=None)
         → instancias de un tipo IFC con sus Psets ya leídos
    Q2 · query_spatial_containment(model)
         → árbol Site→Building→Storey→Element con conteos
    Q3 · query_missing_property(model, ifc_type, pset_name, prop_name)
         → auditoría LOIN inversa: quién NO declara una propiedad

Diseño
------
- Reutiliza _ifc_helpers (load_ifc, report_header, resolve_model_path, get_type_object).
- Reutiliza read_psets de s4l_ifc_query (no duplicamos lógica de unwrap).
- Funciones puras: aceptan model, devuelven dicts JSON-serializables.
- CLI con --out opcional para escribir resultado a out/<fichero>.json.

Uso CLI
-------
    python scripts/s4x_ifc_lab.py --ifc <nombre.ifc> --query bytype \\
        --type IfcWallStandardCase [--psets Pset_WallCommon,Pset_WallCommonExt] \\
        [--out out/s4x_walls.json]

    python scripts/s4x_ifc_lab.py --ifc <nombre.ifc> --query spatial \\
        [--out out/s4x_spatial.json]

    python scripts/s4x_ifc_lab.py --ifc <nombre.ifc> --query missing \\
        --type IfcWallStandardCase --pset Pset_WallCommon --prop ThermalTransmittance \\
        [--out out/s4x_missing.json]

Autor: José M. Soria (NEXUM)
Versión: 0.1 (S4·X Bloque B · 3 consultas core)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import ifcopenshell

from _ifc_helpers import load_ifc, resolve_model_path
from s4l_ifc_query import read_psets


# ---------------------------------------------------------------------------
# Q1 · Instancias de un tipo IFC con sus Psets leídos
# ---------------------------------------------------------------------------

def query_by_type_with_psets(
    model: ifcopenshell.file,
    ifc_type: str,
    pset_names: list[str] | None = None,
) -> dict[str, Any]:
    """Devuelve todas las instancias de ifc_type con sus Psets ya extraídos.

    Parámetros
    ----------
    model : ifcopenshell.file
        Modelo IFC cargado.
    ifc_type : str
        Nombre de clase IFC exacto (ej. 'IfcWallStandardCase').
        Se usa model.by_type() que incluye subtipos por herencia STEP.
    pset_names : list[str] | None
        Si None → devuelve TODOS los psets/quantities/type_psets.
        Si lista → filtra solo los psets cuyo nombre esté en la lista.
        El filtro aplica a instance_psets, instance_quantities y type_psets.

    Devuelve
    --------
    dict con estructura:
        query        : metadatos de la consulta
        total_found  : nº instancias encontradas
        instances    : lista de dicts {id, guid, name, psets, quantities, type_psets}

    Notas
    -----
    - Reutiliza read_psets() de s4l_ifc_query.py para coherencia.
    - El filtrado por pset_names elimina psets enteros, no propiedades individuales.
    - Si pset_names contiene un nombre que no existe en ninguna instancia,
      el dict correspondiente quedará vacío (no es error).
    """
    try:
        instances = model.by_type(ifc_type)
    except RuntimeError as exc:
        # by_type lanza RuntimeError si el tipo no existe en el schema
        return {
            "query": {
                "type": "bytype",
                "ifc_type": ifc_type,
                "pset_filter": pset_names,
                "error": f"Tipo IFC inválido o no presente en schema: {exc}",
            },
            "total_found": 0,
            "instances": [],
        }

    pset_filter = set(pset_names) if pset_names else None
    result_instances: list[dict[str, Any]] = []

    for entity in instances:
        full = read_psets(entity)

        # Filtrado por nombre de pset si aplica
        if pset_filter is not None:
            full["instance_psets"] = {
                k: v for k, v in full["instance_psets"].items() if k in pset_filter
            }
            full["instance_quantities"] = {
                k: v for k, v in full["instance_quantities"].items() if k in pset_filter
            }
            full["type_psets"] = {
                k: v for k, v in full["type_psets"].items() if k in pset_filter
            }
            # Recalcular summary tras filtrado
            full["summary"] = {
                "instance_psets_count": len(full["instance_psets"]),
                "instance_quantities_count": len(full["instance_quantities"]),
                "type_psets_count": len(full["type_psets"]),
                "total_properties": (
                    sum(len(v) for v in full["instance_psets"].values())
                    + sum(len(v) for v in full["instance_quantities"].values())
                    + sum(len(v) for v in full["type_psets"].values())
                ),
            }

        result_instances.append(full)

    return {
        "query": {
            "type": "bytype",
            "ifc_type": ifc_type,
            "pset_filter": pset_names,
        },
        "total_found": len(result_instances),
        "instances": result_instances,
    }


# ---------------------------------------------------------------------------
# Q2 · Árbol de contenedores espaciales
# ---------------------------------------------------------------------------

def _ref_min(entity: Any) -> dict[str, Any]:
    """Referencia mínima de una entidad: id, is_a, name, guid."""
    return {
        "id": entity.id(),
        "is_a": entity.is_a(),
        "name": getattr(entity, "Name", None),
        "guid": getattr(entity, "GlobalId", None),
    }


def _aggregated_children(spatial: Any) -> list[Any]:
    """Hijos espaciales vía IfcRelAggregates (Site→Building→Storey→Space)."""
    children: list[Any] = []
    for rel in getattr(spatial, "IsDecomposedBy", None) or []:
        if rel.is_a("IfcRelAggregates"):
            children.extend(rel.RelatedObjects)
    return children


def _contained_elements(spatial: Any) -> list[Any]:
    """Elementos físicos contenidos vía IfcRelContainedInSpatialStructure."""
    elements: list[Any] = []
    for rel in getattr(spatial, "ContainsElements", None) or []:
        if rel.is_a("IfcRelContainedInSpatialStructure"):
            elements.extend(rel.RelatedElements)
    return elements


def _walk_spatial(spatial: Any) -> dict[str, Any]:
    """Recursión: descripción del nodo + hijos espaciales + elementos contenidos."""
    children_spatial = _aggregated_children(spatial)
    elements_here = _contained_elements(spatial)

    # Conteo de elementos por clase a este nivel
    elements_by_class: dict[str, int] = {}
    elements_list: list[dict[str, Any]] = []
    for el in elements_here:
        cls = el.is_a()
        elements_by_class[cls] = elements_by_class.get(cls, 0) + 1
        elements_list.append(_ref_min(el))

    return {
        **_ref_min(spatial),
        "children_spatial": [_walk_spatial(c) for c in children_spatial],
        "contained_elements_count": len(elements_here),
        "contained_elements_by_class": dict(
            sorted(elements_by_class.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "contained_elements": elements_list,
    }


def query_spatial_containment(model: ifcopenshell.file) -> dict[str, Any]:
    """Devuelve el árbol completo Site → Building → Storey → Element.

    Recorre desde IfcProject hacia abajo usando:
      - IfcRelAggregates : descomposición espacial (Project→Site→Building→Storey)
      - IfcRelContainedInSpatialStructure : elementos físicos contenidos

    Devuelve
    --------
    dict con estructura:
        query           : metadatos
        project         : dict del IfcProject raíz (recursivo)
        orphans         : elementos IfcElement NO contenidos en ninguna estructura
        summary         : conteos agregados (sites, buildings, storeys, spaces, orphans)

    Notas
    -----
    - 'orphans' detecta el hallazgo S4·L #1 ampliado: elementos sin contenedor
      espacial son red flag de import desde CAD sin estructura ISO 19650.
    - El árbol puede ser profundo (Storey→Space→SubSpace en algunos modelos).
    """
    projects = model.by_type("IfcProject")
    if not projects:
        return {
            "query": {"type": "spatial", "error": "No hay IfcProject en el modelo"},
            "project": None,
            "orphans": [],
            "summary": {},
        }

    project_tree = _walk_spatial(projects[0])

    # Detección de huérfanos: IfcElement sin ContainedInStructure
    orphans: list[dict[str, Any]] = []
    for el in model.by_type("IfcElement"):
        contained = getattr(el, "ContainedInStructure", None) or []
        if not contained:
            # Excepción: elementos rellenando aperturas (puertas/ventanas con FillsVoids)
            # están "contenidos" indirectamente vía el muro padre. Los marcamos aparte.
            fills = getattr(el, "FillsVoids", None) or []
            if fills:
                continue
            orphans.append(_ref_min(el))

    # Conteos agregados
    summary = {
        "sites": len(model.by_type("IfcSite")),
        "buildings": len(model.by_type("IfcBuilding")),
        "storeys": len(model.by_type("IfcBuildingStorey")),
        "spaces": len(model.by_type("IfcSpace")),
        "elements_total": len(model.by_type("IfcElement")),
        "orphans_count": len(orphans),
    }

    return {
        "query": {"type": "spatial"},
        "project": project_tree,
        "orphans": orphans,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Q3 · Auditoría LOIN inversa: quién NO declara una propiedad
# ---------------------------------------------------------------------------

def _find_property_value(
    entity: Any, pset_name: str, prop_name: str
) -> tuple[str, Any]:
    """Busca prop_name en pset_name de la entidad. Mira instance Y type psets.

    Devuelve tupla (estado, valor):
        ('absent_pset', None)       → el pset no existe en esta instancia
        ('absent_prop', None)       → el pset existe pero no contiene la propiedad
        ('present_none', None)      → la propiedad existe pero su valor es None
        ('present', valor)          → propiedad presente con valor no-None

    Orden de búsqueda: instance_psets primero, luego type_psets (override de instancia).
    """
    full = read_psets(entity)

    # Buscar en instance_psets
    if pset_name in full["instance_psets"]:
        pset = full["instance_psets"][pset_name]
        if prop_name not in pset:
            # Buscar fallback en type
            if pset_name in full["type_psets"] and prop_name in full["type_psets"][pset_name]:
                val = full["type_psets"][pset_name][prop_name]
                return ("present_none", None) if val is None else ("present", val)
            return ("absent_prop", None)
        val = pset[prop_name]
        return ("present_none", None) if val is None else ("present", val)

    # Buscar en type_psets si no hay en instance
    if pset_name in full["type_psets"]:
        pset = full["type_psets"][pset_name]
        if prop_name not in pset:
            return ("absent_prop", None)
        val = pset[prop_name]
        return ("present_none", None) if val is None else ("present", val)

    return ("absent_pset", None)


def query_missing_property(
    model: ifcopenshell.file,
    ifc_type: str,
    pset_name: str,
    prop_name: str,
) -> dict[str, Any]:
    """Auditoría LOIN inversa: quién NO declara una propiedad concreta.

    Recorre todas las instancias de ifc_type y clasifica según presencia
    de pset_name.prop_name:
      - absent_pset  : la instancia no tiene ese pset
      - absent_prop  : tiene el pset pero no la propiedad
      - present_none : tiene la propiedad pero su valor es None
      - present      : OK (propiedad presente con valor)

    Parámetros
    ----------
    model : ifcopenshell.file
    ifc_type : str
        Ej. 'IfcWallStandardCase'
    pset_name : str
        Ej. 'Pset_WallCommon'
    prop_name : str
        Ej. 'ThermalTransmittance'

    Devuelve
    --------
    dict con estructura:
        query          : metadatos
        total          : nº instancias del tipo
        compliance     : {present: N, absent_pset: N, absent_prop: N, present_none: N}
        compliance_pct : % de cumplimiento (present / total * 100)
        offenders      : lista de instancias incumplidoras con su estado
        sample_value   : un valor 'present' de ejemplo (para sanity check)

    Notas
    -----
    - Es la herramienta directa para construir la tabla de incumplimientos LOIN de E4.
    - 'present_none' es un caso especialmente importante: el modelador declaró
      la propiedad pero la dejó vacía. Es peor que 'absent' a efectos de auditoría
      porque enmascara el incumplimiento (parece que está, pero no tiene valor).
    """
    try:
        instances = model.by_type(ifc_type)
    except RuntimeError as exc:
        return {
            "query": {
                "type": "missing",
                "ifc_type": ifc_type,
                "pset_name": pset_name,
                "prop_name": prop_name,
                "error": f"Tipo IFC inválido: {exc}",
            },
            "total": 0,
            "compliance": {},
            "compliance_pct": 0.0,
            "offenders": [],
            "sample_value": None,
        }

    compliance = {"present": 0, "absent_pset": 0, "absent_prop": 0, "present_none": 0}
    offenders: list[dict[str, Any]] = []
    sample_value: Any = None

    for entity in instances:
        status, value = _find_property_value(entity, pset_name, prop_name)
        compliance[status] += 1

        if status == "present":
            if sample_value is None:
                sample_value = value
        else:
            offenders.append({
                **_ref_min(entity),
                "status": status,
            })

    total = len(instances)
    compliance_pct = (compliance["present"] / total * 100.0) if total else 0.0

    return {
        "query": {
            "type": "missing",
            "ifc_type": ifc_type,
            "pset_name": pset_name,
            "prop_name": prop_name,
        },
        "total": total,
        "compliance": compliance,
        "compliance_pct": round(compliance_pct, 2),
        "offenders": offenders,
        "sample_value": sample_value,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="S4·X · Consultas avanzadas IfcOpenShell (bytype, spatial, missing)"
    )
    parser.add_argument("--ifc", required=True, help="Ruta o nombre de fichero IFC")
    parser.add_argument(
        "--query",
        required=True,
        choices=["bytype", "spatial", "missing"],
        help="Consulta a ejecutar",
    )
    parser.add_argument("--type", help="Tipo IFC (requerido para bytype y missing)")
    parser.add_argument(
        "--psets",
        help="Lista de Psets a filtrar en bytype (separados por coma). Vacío = todos.",
    )
    parser.add_argument("--pset", help="Nombre del Pset (requerido para missing)")
    parser.add_argument("--prop", help="Nombre de la propiedad (requerido para missing)")
    parser.add_argument(
        "--out",
        help="Ruta de salida JSON. Si se omite, imprime a stdout.",
    )
    return parser.parse_args()


def _emit(result: dict[str, Any], out_path: str | None) -> None:
    """Escribe el resultado a fichero o a stdout según --out."""
    payload = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if out_path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload, encoding="utf-8")
        size_kb = p.stat().st_size / 1024
        print(f"[OK] Resultado escrito a {p} ({size_kb:.1f} KB)")
    else:
        print(payload)


def main() -> int:
    args = _parse_args()

    ifc_path = resolve_model_path(args.ifc)
    try:
        model = load_ifc(ifc_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.query == "bytype":
        if not args.type:
            print("[ERROR] --type es obligatorio para query=bytype", file=sys.stderr)
            return 2
        psets = [s.strip() for s in args.psets.split(",")] if args.psets else None
        result = query_by_type_with_psets(model, args.type, psets)
        _emit(result, args.out)
        return 0

    if args.query == "spatial":
        result = query_spatial_containment(model)
        _emit(result, args.out)
        return 0

    if args.query == "missing":
        missing_args = [a for a in (args.type, args.pset, args.prop) if not a]
        if missing_args:
            print(
                "[ERROR] --type, --pset y --prop son obligatorios para query=missing",
                file=sys.stderr,
            )
            return 2
        result = query_missing_property(model, args.type, args.pset, args.prop)
        _emit(result, args.out)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
