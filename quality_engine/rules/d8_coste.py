"""
quality_engine.rules.d8_coste · Reglas D8 Coste (5D).

Checks cubiertos (E6 checklist §3.8):
    C-Q-01 · 100% muros con Qto_WallBaseQuantities         [ids_xml]
    C-Q-02 · ≥ 80% productos con IfcCostItem asociado      [ids_xml]
    C-Q-03 · sniff QTO declarado vs calculado (tol 5%)     [yaml_python · sniff]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: diseño exclusivamente.

Estado S6·L: stubs. Implementación en S6·X.
Estado previsto FZK-Haus: fail/partial (FZK-Haus tiene Qto_* parciales).
"""

from typing import Any

from quality_engine.core.result import ResultadoCheck


def check_wall_quantities_present(model: Any, params: dict) -> ResultadoCheck:
    """C-Q-01 · STUB · S6·X."""
    raise NotImplementedError(
        "S6·X · Qto_WallBaseQuantities en cada IfcWall · ratio = 1.0"
    )


def check_cost_item_association(model: Any, params: dict) -> ResultadoCheck:
    """C-Q-02 · STUB · S6·X."""
    raise NotImplementedError(
        "S6·X · IfcRelAssignsToControl con IfcCostItem · ratio ≥ 0.8"
    )


def sniff_qto_coherence(model: Any, params: dict) -> ResultadoCheck:
    """C-Q-03 · STUB · S6·X · sniff test."""
    raise NotImplementedError(
        "S6·X · NetVolume declarado vs calculado desde geometría · tol 5%"
    )
