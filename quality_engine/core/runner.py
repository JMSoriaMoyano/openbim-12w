"""
quality_engine.core.runner · Orquestador de auditoría.

Pipeline:
    1. Cargar EIR común + variante (vía core.merger)
    2. Cargar modelo IFC (vía ifcopenshell)
    3. Distribuir checks a backends (yaml_python · ids_xml)
    4. Consolidar matriz de resultados
    5. Inyectar audit_meta (eir_source, model_sha, timestamp, schema)

Marco de referencia: docs/S6L_marco_calidad.md §4.3.
"""

from pathlib import Path
from typing import Any

from quality_engine.core.result import ResultadoCheck


def run_audit(
    model_path: Path,
    eir_variant: str,
    eir_version: str = "0.2",
    backends: list[str] | None = None,
) -> dict[str, Any]:
    """
    Ejecuta auditoría completa contra un modelo IFC.

    Args:
        model_path    ruta al .ifc (ej. out/AC20-FZK-Haus_authored.ifc)
        eir_variant   variante EIR: comun / diseno / contratista / asbuilt
        eir_version   versión EIR (default '0.2')
        backends      lista de backends a usar (default ambos)

    Returns:
        Matriz de compliance lista para serializar a JSON:
            {
                "audit_meta": {...},
                "summary": {"total": N, "pass": X, "fail": Y, "partial": Z},
                "results": [ResultadoCheck.to_dict(), ...]
            }

    STUB · implementar en S6·X.
    """
    raise NotImplementedError("S6·X · implementar pipeline completo")


def consolidate_results(
    results: list[ResultadoCheck],
) -> dict[str, int]:
    """
    Calcula summary {total, pass, fail, partial, not_applicable, error}.

    STUB · implementar en S6·X.
    """
    raise NotImplementedError("S6·X · contar estados y devolver dict")
