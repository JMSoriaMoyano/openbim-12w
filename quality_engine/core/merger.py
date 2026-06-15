"""
quality_engine.core.merger · Merge común + variante EIR.

Hereda contrato de scripts/s4s_audit_eir.py (S5·X · refactor multi-variante):
    - structural[] y loin[] se concatenan (común primero, variante después)
    - meta de la variante prevalece sobre meta común
    - fail-fast si hay colisión de check_id entre común y variante

Marco de referencia: docs/S6L_marco_calidad.md §4.3.
"""

from typing import Any


class CheckIdCollisionError(ValueError):
    """Excepción lanzada cuando un check_id existe en común Y en variante."""

    pass


def merge_eir(common: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    """
    Fusiona EIR común + variante respetando el contrato S5·X.

    Args:
        common  EIR común (PBSA_v0.2_comun.yaml ya parseado)
        variant EIR variante (diseno / contratista / asbuilt ya parseado)

    Returns:
        EIR consolidado listo para ejecutar contra el modelo.

    Raises:
        CheckIdCollisionError si dos checks comparten check_id.

    STUB · implementar en S6·X. La lógica ya existe en scripts/s4s_audit_eir.py
    y se migrará verbatim aquí.
    """
    raise NotImplementedError(
        "S6·X · portar lógica de merge desde scripts/s4s_audit_eir.py"
    )
