"""
quality_engine.rules.d6_clasificacion · Reglas D6 Clasificación.

Checks cubiertos (E6 checklist §3.6):
    C-C-01 · ≥ 1 sistema de clasificación declarado  [ids_xml]
    C-C-02 · ≥ 70% muros con clasificación           [ids_xml]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: todas.

Nota: ambos checks D6 son migrables a IDS (`classification` facet nativo).
Este módulo queda como fallback.

Estado S6·L: stubs. Implementación en S6·X.
"""

from typing import Any

from quality_engine.core.result import ResultadoCheck


def check_classification_system_declared(model: Any, params: dict) -> ResultadoCheck:
    """C-C-01 · STUB · S6·X."""
    raise NotImplementedError("S6·X · model.by_type('IfcClassification')")


def check_wall_classification_coverage(
    model: Any, params: dict
) -> ResultadoCheck:
    """C-C-02 · STUB · S6·X."""
    raise NotImplementedError(
        "S6·X · IfcRelAssociatesClassification sobre IfcWall · ratio ≥ 0.7"
    )
