"""
quality_engine.rules.d1_modelo · Reglas D1 Modelo (integridad estructural).

Checks cubiertos (E6 checklist §3.1):
    C-M-01 · FILE_SCHEMA == 'IFC4'              [yaml_python]
    C-M-02 · model.schema == 'IFC4' (coherencia) [yaml_python]
    C-M-03 · nº IfcProject == 1                  [ids_xml]
    C-M-04 · nº IfcSite ≥ 1                      [ids_xml]
    C-M-05 · nº IfcBuilding ≥ 1                  [ids_xml]
    C-M-06 · nº IfcBuildingStorey ≥ 1            [ids_xml]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: todas.

Estado S6·L: stubs. Implementación en S6·X.
"""

from typing import Any

from quality_engine.core.result import ResultadoCheck


def check_file_schema_ifc4(model: Any, params: dict) -> ResultadoCheck:
    """C-M-01 · STUB · S6·X."""
    raise NotImplementedError("S6·X · leer FILE_SCHEMA de cabecera STEP")


def check_model_schema_coherence(model: Any, params: dict) -> ResultadoCheck:
    """C-M-02 · STUB · S6·X."""
    raise NotImplementedError("S6·X · model.schema == FILE_SCHEMA declarado")
