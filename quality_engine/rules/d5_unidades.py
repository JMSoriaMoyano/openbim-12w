"""
quality_engine.rules.d5_unidades · Reglas D5 Unidades.

Checks cubiertos (E6 checklist §3.5):
    C-U-01 · IfcUnitAssignment presente          [yaml_python]
    C-U-02 · sistema métrico SI                  [yaml_python]
    C-U-03 · sniff test longitudes coherente     [yaml_python · sniff]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: todas.

Estado S6·L: stubs. Implementación en S6·X.
"""

from typing import Any

from quality_engine.core.result import ResultadoCheck


def check_unit_assignment_present(model: Any, params: dict) -> ResultadoCheck:
    """C-U-01 · STUB · S6·X."""
    raise NotImplementedError("S6·X · model.by_type('IfcUnitAssignment')")


def check_si_metric_system(model: Any, params: dict) -> ResultadoCheck:
    """C-U-02 · STUB · S6·X."""
    raise NotImplementedError("S6·X · IfcSIUnit + Name=METRE/etc · Prefix válido")


def sniff_length_coherence(model: Any, params: dict) -> ResultadoCheck:
    """C-U-03 · STUB · S6·X · sniff test."""
    raise NotImplementedError(
        "S6·X · muestrear 10 longitudes muros · mediana vs umbral mm/m"
    )
