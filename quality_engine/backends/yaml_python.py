"""
quality_engine.backends.yaml_python · Backend legacy (motor propio Python).

Ejecuta los checks que NO son migrables a IDS (marco §4.2):
    - Lógica condicional cruzada entre Psets
    - Sniff tests numéricos (unidades, QTO)
    - Validaciones de cabecera STEP
    - Validaciones 4D temporales (secuencia)

Composición: invoca funciones de quality_engine.rules.d*_*.

Estado S6·L: stub. Implementación en S6·X migrará reglas desde
scripts/s4s_audit_eir.py manteniendo equivalencia funcional.
"""

from pathlib import Path
from typing import Any

from quality_engine.core.result import ResultadoCheck


def run_yaml_python_backend(
    model: Any,  # ifcopenshell.file
    eir_consolidado: dict[str, Any],
    eir_source: str,
) -> list[ResultadoCheck]:
    """
    Ejecuta todos los checks del EIR que aplican backend yaml_python.

    Filtra `checks[]` por `backend == 'yaml_python'` y los ejecuta vía
    las funciones de quality_engine.rules.

    STUB · implementar en S6·X.
    """
    raise NotImplementedError("S6·X · dispatcher por check_id → rules.d*_*")
