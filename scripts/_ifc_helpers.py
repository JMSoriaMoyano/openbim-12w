"""
_ifc_helpers.py · OpenBIM 12 semanas · módulo común
====================================================
Helpers compartidos entre scripts de consulta IFC (s4l_*, s4x_*, s5l_*, ...).

Contenido
---------
    MODELS_DIR              · Path absoluto a models/samples/_local/
    resolve_model_path()    · Convierte nombre/ruta relativa → Path absoluto
    load_ifc()              · Carga IFC con validación mínima
    report_header()         · Cabecera estándar (schema, MVD, totales)
    get_type_object()       · Resolución IfcTypeObject (IFC2x3 + IFC4)

Diseño
------
- Sin estado global. Funciones puras o creadoras de objetos.
- Acepta str | Path indistintamente para rutas.
- get_type_object() es público (sin underscore) porque lo reusan varios scripts;
  en s4l_ifc_query.py se mantenía como _get_type_object por encapsulación local.

Autor: José M. Soria (NEXUM)
Versión: 0.1 (S4·X Bloque A · extracción inicial)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import ifcopenshell

# ---------------------------------------------------------------------------
# Rutas estándar del proyecto
# ---------------------------------------------------------------------------

# Resolución robusta: <repo_root>/models/samples/_local/
# __file__ está en scripts/, subimos un nivel hasta la raíz del repo.
MODELS_DIR: Path = (Path(__file__).resolve().parent.parent / "models" / "samples" / "_local")


def resolve_model_path(path_or_name: str | Path) -> Path:
    """Resuelve un nombre o ruta a un Path absoluto.

    Reglas
    ------
    - Si recibe un Path absoluto válido → lo devuelve tal cual.
    - Si recibe una ruta relativa que existe respecto al CWD → la resuelve.
    - Si recibe un nombre simple (ej. 'AC20-FZK-Haus.ifc') → MODELS_DIR / nombre.

    No valida existencia (eso lo hace load_ifc). Solo construye el Path correcto.

    Ejemplos
    --------
    >>> resolve_model_path('AC20-FZK-Haus.ifc')
    PosixPath('.../models/samples/_local/AC20-FZK-Haus.ifc')
    >>> resolve_model_path('models/samples/_local/AC20-FZK-Haus.ifc')
    PosixPath('.../models/samples/_local/AC20-FZK-Haus.ifc')
    """
    p = Path(path_or_name)
    if p.is_absolute():
        return p
    # Si la ruta relativa apunta a un fichero existente desde CWD, respetarla
    if p.exists():
        return p.resolve()
    # Si es solo un nombre o ruta corta, asumir MODELS_DIR
    if len(p.parts) == 1:
        return MODELS_DIR / p
    # Ruta relativa multi-parte que no existe: devolver tal cual resuelta
    return p.resolve()


# ---------------------------------------------------------------------------
# Carga y cabecera
# ---------------------------------------------------------------------------

def load_ifc(path: str | Path) -> ifcopenshell.file:
    """Carga un IFC desde disco con validación mínima.

    Acepta str o Path. No resuelve nombres (usar resolve_model_path antes si aplica).
    Lanza FileNotFoundError si no existe, ValueError si la extensión no es .ifc.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"IFC no encontrado: {p}")
    if not p.suffix.lower() == ".ifc":
        raise ValueError(f"Extensión inesperada (esperado .ifc): {p.suffix}")
    return ifcopenshell.open(str(p))


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
# Resolución de tipo (IFC2x3 + IFC4)
# ---------------------------------------------------------------------------

def get_type_object(entity: Any) -> Any:
    """Devuelve el IfcTypeObject asociado a una entidad, o None.

    IFC4 usa IsTypedBy (IfcRelDefinesByType, atributo inverso).
    IFC2x3 usaba IsDefinedBy con RelatingType (relación genérica).
    Probamos ambos para robustez cross-schema.
    """
    typed_by = getattr(entity, "IsTypedBy", None) or []
    if typed_by:
        return typed_by[0].RelatingType
    # Fallback IFC2x3
    for rel in getattr(entity, "IsDefinedBy", None) or []:
        if rel.is_a("IfcRelDefinesByType"):
            return rel.RelatingType
    return None
