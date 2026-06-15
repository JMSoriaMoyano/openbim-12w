"""
quality_engine.rules.d4_geometria · Reglas D4 Geometría.

Checks cubiertos (E6 checklist §3.4):
    C-G-01 · 100% productos con IfcProductDefinitionShape [ids_xml]
    C-G-02 · bounding box no nulo                         [yaml_python]
    C-G-03 · muros con representación Body+Axis coherente [yaml_python]

Capa ISO 19650-2: gráfica (única dimensión gráfica del marco).
Variantes aplicables: todas.

Estado S6·L: stubs. Implementación en S6·X.
"""

from typing import Any

from quality_engine.core.result import ResultadoCheck


def check_bounding_box_non_null(model: Any, params: dict) -> ResultadoCheck:
    """C-G-02 · STUB · S6·X."""
    raise NotImplementedError(
        "S6·X · ifcopenshell.geom.create_shape + bbox no nulo"
    )


def check_wall_body_axis_coherence(model: Any, params: dict) -> ResultadoCheck:
    """C-G-03 · STUB · S6·X."""
    raise NotImplementedError(
        "S6·X · IfcShapeRepresentation Body vs Axis · distancia eje-centroide"
    )
