"""
quality_engine.rules.d7_temporal · Reglas D7 Temporal (4D).

Checks cubiertos (E6 checklist §3.7):
    C-T-01 · ≥ 1 IfcTask declarada                          [ids_xml]
    C-T-02 · ≥ 80% productos con tarea asignada (contratista) [ids_xml]
    C-T-03 · ≥ 1 hito as-built declarado (asbuilt)          [ids_xml]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: contratista (C-T-01, C-T-02) · asbuilt (C-T-01, C-T-03).

Estado S6·L: stubs. Implementación en S6·X.
Estado previsto FZK-Haus: fail en las 3 (modelo sin 4D). Esperado.
"""

from typing import Any

from quality_engine.core.result import ResultadoCheck


def check_task_present(model: Any, params: dict) -> ResultadoCheck:
    """C-T-01 · STUB · S6·X."""
    raise NotImplementedError("S6·X · model.by_type('IfcTask')")


def check_product_task_assignment(model: Any, params: dict) -> ResultadoCheck:
    """C-T-02 · STUB · S6·X."""
    raise NotImplementedError(
        "S6·X · IfcRelAssignsToProcess · ratio productos asignados"
    )


def check_asbuilt_milestone(model: Any, params: dict) -> ResultadoCheck:
    """C-T-03 · STUB · S6·X."""
    raise NotImplementedError("S6·X · IfcTask con TaskType='COMPLETION'")
