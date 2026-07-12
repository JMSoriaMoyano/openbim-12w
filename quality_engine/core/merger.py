"""
quality_engine.core.merger · Merge común + variante EIR.

Hereda contrato de scripts/s4s_audit_eir.py (S5·X · refactor multi-variante):
    - structural[] y loin[] se concatenan (común primero, variante después)
    - meta de la variante prevalece sobre meta común
    - fail-fast si hay colisión de check_id entre común y variante

Marco de referencia: docs/S6L_marco_calidad.md §4.3.
"""

from pathlib import Path
from typing import Any

import yaml


SUPPORTED_VARIANTS = ("comun", "diseno", "contratista", "asbuilt")


class CheckIdCollisionError(ValueError):
    """Excepción lanzada cuando un check_id existe en común Y en variante."""

    pass


def load_yaml(path: Path) -> dict[str, Any]:
    """Carga un YAML como dict. Falla rápido si la raíz no es mapping."""
    if not path.exists():
        raise FileNotFoundError(f"YAML no encontrado: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"YAML no es un mapping en la raíz: {path}")
    return data


def merge_eir(
    common: dict[str, Any],
    variant: dict[str, Any],
    variant_name: str = "variant",
) -> dict[str, Any]:
    """
    Fusiona EIR común + variante respetando el contrato S5·X.

    Args:
        common         EIR común (PBSA_v0.2_comun.yaml ya parseado).
        variant        EIR variante (diseno / contratista / asbuilt ya parseado).
        variant_name   Nombre de la variante (para mensajes de error y trazabilidad).

    Returns:
        EIR consolidado listo para ejecutar contra el modelo.

    Raises:
        CheckIdCollisionError si dos checks comparten check_id entre común y variante.
    """
    merged_meta = {
        **(common.get("meta", {}) or {}),
        **(variant.get("meta", {}) or {}),
    }

    common_structural = list(common.get("structural_checks", []) or [])
    var_structural = list(variant.get("structural_checks", []) or [])
    common_loin = list(common.get("loin_checks", []) or [])
    var_loin = list(variant.get("loin_checks", []) or [])
    common_qe = list(common.get("quality_engine_checks", []) or [])
    var_qe = list(variant.get("quality_engine_checks", []) or [])

    # Fail-fast en colisiones de check_id (contrato S5·X · DF-01 ampliado S6·X)
    all_common_ids = {
        c["check_id"] for c in common_structural + common_loin + common_qe
    }
    all_var_ids = {c["check_id"] for c in var_structural + var_loin + var_qe}
    collisions = all_common_ids & all_var_ids
    if collisions:
        raise CheckIdCollisionError(
            f"Colisión de check_id entre común y variante '{variant_name}': "
            f"{sorted(collisions)}. El refactor DF-01 prohíbe esta sobreescritura."
        )

    return {
        "meta": merged_meta,
        "structural_checks": common_structural + var_structural,
        "loin_checks": common_loin + var_loin,
        "quality_engine_checks": common_qe + var_qe,
        "_merge_origin": {
            "common_structural_count": len(common_structural),
            "variant_structural_count": len(var_structural),
            "common_loin_count": len(common_loin),
            "variant_loin_count": len(var_loin),
            "common_qe_count": len(common_qe),
            "variant_qe_count": len(var_qe),
            "variant_name": variant_name,
        },
    }


def load_eir_spec(
    variant: str,
    eir_version: str,
    eir_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Carga el EIR spec para una variante (modo multi-variante S5·X).

    Args:
        variant       'comun' | 'diseno' | 'contratista' | 'asbuilt'.
        eir_version   p. ej. '0.2'.
        eir_dir       Directorio donde residen PBSA_v<ver>_<variant>.yaml.

    Returns:
        (eir_spec, source_info)
            eir_spec    : dict mergeado listo para el runner.
            source_info : metadatos de origen para trazabilidad.
    """
    if variant not in SUPPORTED_VARIANTS:
        raise ValueError(
            f"Variante no soportada: {variant!r}. Permitidas: {SUPPORTED_VARIANTS}"
        )

    common_path = eir_dir / f"PBSA_v{eir_version}_comun.yaml"
    common = load_yaml(common_path)

    if variant == "comun":
        return common, {
            "mode": "multi_variant",
            "variant": "comun",
            "eir_version": eir_version,
            "paths_used": [str(common_path)],
        }

    variant_path = eir_dir / f"PBSA_v{eir_version}_{variant}.yaml"
    variant_spec = load_yaml(variant_path)
    merged = merge_eir(common, variant_spec, variant)
    return merged, {
        "mode": "multi_variant",
        "variant": variant,
        "eir_version": eir_version,
        "paths_used": [str(common_path), str(variant_path)],
    }
