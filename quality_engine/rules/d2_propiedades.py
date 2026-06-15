"""
quality_engine.rules.d2_propiedades · Reglas D2 Propiedades (Psets).

Checks cubiertos (E6 checklist §3.2):
    C-P-01 · 100% muros con Pset_WallCommon      [ids_xml]
    C-P-02 · 100% puertas con Pset_DoorCommon    [ids_xml]
    C-P-03 · 100% puertas con FireRating         [ids_xml]
    C-P-04 · 100% muros con IsExternal           [ids_xml]
    C-P-05 · 100% muros con LoadBearing          [ids_xml]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: todas.

Nota: todos los checks D2 son migrables a IDS nativamente.
Este módulo queda como referencia funcional y fallback si IDS no está disponible.

Estado S6·L: stubs. Implementación en S6·X (fallback).
"""

from typing import Any

from quality_engine.core.result import ResultadoCheck


def check_pset_presence(
    model: Any, ifc_class: str, pset_name: str, threshold_partial: float = 0.8
) -> ResultadoCheck:
    """C-P-01/02 genérico · STUB · S6·X."""
    raise NotImplementedError("S6·X · ifcopenshell.util.element.get_psets")


def check_property_value_defined(
    model: Any, ifc_class: str, pset_name: str, property_name: str
) -> ResultadoCheck:
    """C-P-03/04/05 genérico · STUB · S6·X."""
    raise NotImplementedError("S6·X · check propiedad no None y no ''")
