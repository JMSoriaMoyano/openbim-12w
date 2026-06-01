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
    python scripts/s4l_ifc_query.py --ifc <ruta.ifc> --query counts
    python scripts/s4l_ifc_query.py --ifc <ruta.ifc> --query guid --guid <GUID>
    python scripts/s4l_ifc_query.py --ifc <ruta.ifc> --query psets --guid <GUID>

Autor: José M. Soria (NEXUM)
Versión: 0.1 (esqueleto · Bloque A)
"""

from __future__ import annotations

import argparse
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

def count_by_type(model: ifcopenshell.file) -> dict[str, int]:
    """Devuelve un diccionario {clase_IFC: nº de instancias}, ordenado descendente.

    TODO Bloque B:
        - Iterar sobre model.by_type("IfcRoot") o equivalente.
        - Contar por entity.is_a().
        - Ordenar por valor descendente.
        - Considerar si filtrar tipos no físicos (IfcOwnerHistory, IfcCartesianPoint…).
    """
    raise NotImplementedError("Bloque B: pendiente de implementar")


# ---------------------------------------------------------------------------
# Q2 · Buscar por GUID  (a implementar en Bloque C)
# ---------------------------------------------------------------------------

def find_by_guid(model: ifcopenshell.file, guid: str) -> dict[str, Any] | None:
    """Localiza una entidad por su GlobalId y devuelve resumen identificativo.

    Devuelve None si no existe.

    TODO Bloque C:
        - Usar model.by_guid(guid) con manejo de RuntimeError si no existe.
        - Devolver: id, guid, is_a, name, description, predefined_type si aplica.
    """
    raise NotImplementedError("Bloque C: pendiente de implementar")


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
        out = count_by_type(model)
        # Limitar a top N
        top_n = dict(list(out.items())[: args.top])
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
