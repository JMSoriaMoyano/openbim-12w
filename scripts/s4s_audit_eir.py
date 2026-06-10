"""
s4s_audit_eir.py · OpenBIM 12 semanas · S4·S Bloque B (Sáb 06/06/2026, ejec. 07/06)
=====================================================================================
Orquestador de auditoría EIR contra un modelo IFC.

Lee un fichero YAML que declara los chequeos OBLIGATORIOS del EIR
(estructurales + LOIN) e invoca dinámicamente las funciones de verificación
implementadas en:
  - scripts/s4x_ifc_lab.py        · query_missing_property (LOIN)
  - scripts/s4s_structural_checks.py · check_mvd_compliance, check_bsdd_classification

Genera una matriz de cumplimiento consolidada en out/<prefix>_baseline.json
con:
  - resumen ejecutivo (pass/partial/fail por categoría e hito)
  - detalle por check con estado, % cumplimiento y conteo de offenders
  - trazabilidad completa al EIR (eir_ref, rationale, severity)

Política de umbrales (loin_checks)
----------------------------------
    pass     : compliance_pct >= 95
    partial  : 60 <= compliance_pct < 95
    fail     : compliance_pct < 60

Política para structural_checks: usa el campo 'compliance' devuelto por
la función (pass | partial | fail) directamente, sin aplicar umbrales.

Uso CLI
-------
Modo legacy (single-file, compatibilidad v0.1):
    python scripts/s4s_audit_eir.py \\
        --ifc AC20-FZK-Haus.ifc \\
        --eir eir/PBSA_v0.1_obligatorias.yaml \\
        --out out/s4s_compliance_matrix_baseline.json

Modo multi-variant (v0.2+, S5·X · DF-01 cerrada):
    python scripts/s4s_audit_eir.py \\
        --ifc out/AC20-FZK-Haus_authored.ifc \\
        --variant diseno \\
        --out out/AC20-FZK-Haus_compliance_post_diseno.json

El flag --variant compone automáticamente las rutas:
    eir/PBSA_v<eir-version>_comun.yaml      (base obligatoria)
  + eir/PBSA_v<eir-version>_<variant>.yaml  (extensión específica)
La versión por defecto es 0.2 (configurable con --eir-version).

Diseño
------
- Despachador (dispatch) explícito por nombre de función: ningún eval/import dinámico
  sin whitelist. Solo las 3 funciones declaradas en CHECK_REGISTRY son invocables.
- Funciones puras: no muta el YAML, no escribe ficheros aparte del --out.
- Output JSON-serializable end-to-end, listo para consumir desde docs (Bloque C).
- Merge contract (--variant): structural_checks y loin_checks se concatenan
  (común + variante). meta = {**comun.meta, **variant.meta} (variante prevalece).
  Colisiones de check_id entre común y variante → ValueError (fail-fast).

Autor: José M. Soria (NEXUM)
Versión: 0.2 (S5·X · DF-01 cerrada · multi-variant support)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

import yaml  # PyYAML

from _ifc_helpers import load_ifc, resolve_model_path
from s4x_ifc_lab import query_missing_property
from s4s_structural_checks import (
    check_bsdd_classification,
    check_mvd_compliance,
)

# ---------------------------------------------------------------------------
# Variantes soportadas v0.2 (DF-01 cerrada en S5·X)
# ---------------------------------------------------------------------------

SUPPORTED_VARIANTS = ("comun", "diseno", "contratista", "asbuilt")
DEFAULT_EIR_VERSION = "0.2"
EIR_DIR = Path("eir")


# ---------------------------------------------------------------------------
# Registro de funciones invocables desde YAML (whitelist explícita)
# ---------------------------------------------------------------------------

CHECK_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "query_missing_property": query_missing_property,
    "check_mvd_compliance": check_mvd_compliance,
    "check_bsdd_classification": check_bsdd_classification,
}


# ---------------------------------------------------------------------------
# Carga + merge multi-variant (DF-01 cerrada en S5·X)
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict[str, Any]:
    """Carga un YAML como dict. Falla rápido si la raíz no es mapping."""
    if not path.exists():
        raise FileNotFoundError(f"YAML no encontrado: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"YAML no es un mapping en la raíz: {path}")
    return data


def _merge_eir_specs(
    comun: dict[str, Any],
    variant_spec: dict[str, Any],
    variant_name: str,
) -> dict[str, Any]:
    """Funde el EIR común con una variante específica.

    Contrato de merge (definido en eir/PBSA_v0.2_comun.yaml):
      - structural_checks = comun.structural_checks + variant.structural_checks
      - loin_checks       = comun.loin_checks       + variant.loin_checks
      - meta              = {**comun.meta, **variant.meta}  (variante prevalece)
      - check_id duplicado entre comun y variant → ValueError (fail-fast)
    """
    merged_meta = {**(comun.get("meta", {}) or {}), **(variant_spec.get("meta", {}) or {})}

    comun_structural = list(comun.get("structural_checks", []) or [])
    var_structural = list(variant_spec.get("structural_checks", []) or [])
    comun_loin = list(comun.get("loin_checks", []) or [])
    var_loin = list(variant_spec.get("loin_checks", []) or [])

    # Fail-fast en colisiones de check_id
    all_comun_ids = {c["check_id"] for c in comun_structural + comun_loin}
    all_var_ids = {c["check_id"] for c in var_structural + var_loin}
    collisions = all_comun_ids & all_var_ids
    if collisions:
        raise ValueError(
            f"Colisión de check_id entre común y variante '{variant_name}': "
            f"{sorted(collisions)}. El refactor DF-01 prohíbe esta sobreescritura."
        )

    return {
        "meta": merged_meta,
        "structural_checks": comun_structural + var_structural,
        "loin_checks": comun_loin + var_loin,
        "_merge_origin": {
            "comun_structural_count": len(comun_structural),
            "variant_structural_count": len(var_structural),
            "comun_loin_count": len(comun_loin),
            "variant_loin_count": len(var_loin),
            "variant_name": variant_name,
        },
    }


def load_eir_spec(
    eir_path_str: str | None,
    variant: str | None,
    eir_version: str,
    eir_dir: Path = EIR_DIR,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Carga el EIR spec según el modo (legacy single-file o multi-variant).

    Returns
    -------
    (eir_spec, source_info)
        eir_spec : dict mergeado listo para audit_eir()
        source_info : metadatos de origen (paths usados, modo) para trazabilidad
    """
    if variant is not None:
        if variant not in SUPPORTED_VARIANTS:
            raise ValueError(
                f"Variante no soportada: {variant!r}. "
                f"Permitidas: {SUPPORTED_VARIANTS}"
            )
        comun_path = eir_dir / f"PBSA_v{eir_version}_comun.yaml"
        comun = _load_yaml(comun_path)

        if variant == "comun":
            # Auditar solo común (útil para verificar P4 vs baseline v0.1)
            return comun, {
                "mode": "multi_variant",
                "variant": "comun",
                "eir_version": eir_version,
                "paths_used": [str(comun_path)],
            }

        variant_path = eir_dir / f"PBSA_v{eir_version}_{variant}.yaml"
        variant_spec = _load_yaml(variant_path)
        merged = _merge_eir_specs(comun, variant_spec, variant)
        return merged, {
            "mode": "multi_variant",
            "variant": variant,
            "eir_version": eir_version,
            "paths_used": [str(comun_path), str(variant_path)],
        }

    # Modo legacy: --eir <path>
    if eir_path_str is None:
        raise ValueError("Debe pasarse --eir <path> o --variant <name>.")
    path = Path(eir_path_str)
    spec = _load_yaml(path)
    return spec, {
        "mode": "legacy_single_file",
        "variant": None,
        "eir_version": (spec.get("meta", {}) or {}).get("eir_version"),
        "paths_used": [str(path)],
    }


# ---------------------------------------------------------------------------
# Aplicación de umbrales (solo LOIN)
# ---------------------------------------------------------------------------

def _classify_loin(compliance_pct: float, pass_min: float, partial_min: float) -> str:
    """Aplica umbrales pass/partial/fail a un % de cumplimiento LOIN."""
    if compliance_pct >= pass_min:
        return "pass"
    if compliance_pct >= partial_min:
        return "partial"
    return "fail"


# ---------------------------------------------------------------------------
# Ejecución de un chequeo individual
# ---------------------------------------------------------------------------

def _run_structural(
    check: dict[str, Any],
    model: Any,
) -> dict[str, Any]:
    """Ejecuta un structural_check y normaliza la salida."""
    fn = CHECK_REGISTRY[check["check_fn"]]
    params = check.get("params", {}) or {}
    raw = fn(model, **params)

    # Normalizar campos comunes para la matriz
    return {
        "check_id": check["check_id"],
        "hito": check["hito"],
        "category": "structural",
        "eir_ref": check["eir_ref"],
        "severity": check["severity"],
        "rationale": check["rationale"],
        "check_fn": check["check_fn"],
        "params": params,
        "status": raw.get("compliance", "unknown"),
        "raw_result": raw,
    }


def _run_loin(
    check: dict[str, Any],
    model: Any,
    pass_min: float,
    partial_min: float,
) -> dict[str, Any]:
    """Ejecuta un loin_check y normaliza la salida."""
    raw = query_missing_property(
        model=model,
        ifc_type=check["ifc_type"],
        pset_name=check["pset"],
        prop_name=check["prop"],
    )

    pct = float(raw.get("compliance_pct", 0.0))
    total = int(raw.get("total", 0))
    compliance = raw.get("compliance", {}) or {}
    present = int(compliance.get("present", 0))
    offenders_count = len(raw.get("offenders", []) or [])

    # Si total==0 (no hay instancias del tipo), marcamos N/A
    # para diferenciar de un fail real con instancias incumplidoras.
    if total == 0:
        status = "n/a"
    else:
        status = _classify_loin(pct, pass_min, partial_min)

    return {
        "check_id": check["check_id"],
        "hito": check["hito"],
        "category": "loin",
        "eir_ref": check["eir_ref"],
        "severity": check["severity"],
        "rationale": check["rationale"],
        "ifc_type": check["ifc_type"],
        "pset": check["pset"],
        "prop": check["prop"],
        "check_fn": "query_missing_property",
        "total": total,
        "present": present,
        "compliance_pct": round(pct, 2),
        "offenders_count": offenders_count,
        "status": status,
        "compliance_breakdown": compliance,
    }


# ---------------------------------------------------------------------------
# Construcción del resumen ejecutivo
# ---------------------------------------------------------------------------

def _build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Construye el resumen ejecutivo agregando por status, categoría e hito."""
    counts_by_status = {"pass": 0, "partial": 0, "fail": 0, "n/a": 0, "unknown": 0}
    by_category: dict[str, dict[str, int]] = {}
    by_hito: dict[str, dict[str, int]] = {}

    for r in results:
        st = r.get("status", "unknown")
        counts_by_status[st] = counts_by_status.get(st, 0) + 1

        cat = r.get("category", "unknown")
        by_category.setdefault(cat, {"pass": 0, "partial": 0, "fail": 0, "n/a": 0, "unknown": 0})
        by_category[cat][st] = by_category[cat].get(st, 0) + 1

        hito = r.get("hito", "unknown")
        by_hito.setdefault(hito, {"pass": 0, "partial": 0, "fail": 0, "n/a": 0, "unknown": 0})
        by_hito[hito][st] = by_hito[hito].get(st, 0) + 1

    total = len(results)
    pass_n = counts_by_status["pass"]
    # pct_global excluye N/A del denominador (solo cuenta chequeos aplicables)
    applicable = total - counts_by_status["n/a"]
    pct_global = (pass_n / applicable * 100.0) if applicable else 0.0

    return {
        "total_checks": total,
        "applicable_checks": applicable,
        "counts_by_status": counts_by_status,
        "pct_global_pass": round(pct_global, 2),
        "by_category": by_category,
        "by_hito": by_hito,
    }


# ---------------------------------------------------------------------------
# Orquestación principal
# ---------------------------------------------------------------------------

def audit_eir(
    model: Any,
    eir_spec: dict[str, Any],
    ifc_path_str: str,
) -> dict[str, Any]:
    """Ejecuta todos los chequeos del EIR y devuelve matriz consolidada.

    Parámetros
    ----------
    model : ifcopenshell.file
    eir_spec : dict
        Contenido cargado del YAML (meta + structural_checks + loin_checks).
    ifc_path_str : str
        Ruta al IFC auditado (para trazabilidad en el output).

    Devuelve
    --------
    dict con estructura:
        eir_meta   : copia del bloque 'meta' del YAML
        audit_meta : ifc auditado + nº de chequeos cargados
        summary    : resumen ejecutivo (counts por status/categoría/hito)
        results    : lista de chequeos normalizados
    """
    meta = eir_spec.get("meta", {}) or {}
    thresholds = meta.get("thresholds", {}) or {}
    pass_min = float(thresholds.get("pass_min_pct", 95.0))
    partial_min = float(thresholds.get("partial_min_pct", 60.0))

    structural = eir_spec.get("structural_checks", []) or []
    loin = eir_spec.get("loin_checks", []) or []

    # Validar que todos los check_fn están en el registro (fail-fast)
    declared_fns = {c["check_fn"] for c in structural + loin}
    unknown = declared_fns - set(CHECK_REGISTRY.keys())
    if unknown:
        raise ValueError(
            f"check_fn no registrados (whitelist): {sorted(unknown)}. "
            f"Permitidos: {sorted(CHECK_REGISTRY.keys())}"
        )

    results: list[dict[str, Any]] = []

    for check in structural:
        results.append(_run_structural(check, model))

    for check in loin:
        results.append(_run_loin(check, model, pass_min, partial_min))

    audit_meta_block = {
        "ifc_audited": ifc_path_str,
        "structural_checks_count": len(structural),
        "loin_checks_count": len(loin),
        "total_checks": len(results),
        "thresholds_applied": {
            "pass_min_pct": pass_min,
            "partial_min_pct": partial_min,
        },
    }
    # Si el spec viene de merge multi-variant, propagar metadatos de origen
    if "_merge_origin" in eir_spec:
        audit_meta_block["merge_origin"] = eir_spec["_merge_origin"]

    return {
        "eir_meta": meta,
        "audit_meta": audit_meta_block,
        "summary": _build_summary(results),
        "results": results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "S4·S · Orquestador de auditoría EIR (YAML → matriz JSON). "
            "v0.2 soporta multi-variant (--variant) tras refactor DF-01 (S5·X)."
        )
    )
    parser.add_argument("--ifc", required=True, help="Ruta o nombre de fichero IFC")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--eir",
        help="[Legacy] Ruta a un YAML EIR single-file (compat v0.1).",
    )
    src.add_argument(
        "--variant",
        choices=SUPPORTED_VARIANTS,
        help=(
            "[v0.2+] Variante a auditar: comun (solo base), diseno (5D/QTO), "
            "contratista (4D/WBS) o asbuilt (LOIN-FM). Compone rutas "
            "eir/PBSA_v<X.Y>_comun.yaml + eir/PBSA_v<X.Y>_<variant>.yaml."
        ),
    )
    parser.add_argument(
        "--eir-version",
        default=DEFAULT_EIR_VERSION,
        help=f"Versión EIR a usar con --variant (default: {DEFAULT_EIR_VERSION}).",
    )
    parser.add_argument(
        "--out",
        help="Ruta de salida JSON. Si se omite, imprime a stdout.",
    )
    return parser.parse_args()


def _emit(result: dict[str, Any], out_path: str | None) -> None:
    payload = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if out_path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload, encoding="utf-8")
        size_kb = p.stat().st_size / 1024
        print(f"[OK] Matriz de cumplimiento escrita a {p} ({size_kb:.1f} KB)")
    else:
        print(payload)


def _print_console_summary(audit: dict[str, Any]) -> None:
    """Imprime resumen compacto a stdout (siempre, incluso con --out)."""
    s = audit["summary"]
    print()
    print("=" * 70)
    print(f"AUDITORIA EIR · {audit['audit_meta']['ifc_audited']}")
    print("=" * 70)
    print(f"Total chequeos     : {s['total_checks']} (aplicables: {s['applicable_checks']})")
    print(f"% Pass global      : {s['pct_global_pass']}%")
    print(f"Counts por status  : {s['counts_by_status']}")
    print(f"Por categoria      : {s['by_category']}")
    print(f"Por hito           : {s['by_hito']}")
    print("-" * 70)
    print("Detalle por chequeo:")
    for r in audit["results"]:
        status = r["status"]
        extra = ""
        if r["category"] == "loin":
            extra = f" ({r['compliance_pct']}% · {r['present']}/{r['total']})"
        print(f"  [{status:>7}] {r['check_id']:<40} {r['eir_ref']}{extra}")
    print("=" * 70)


def main() -> int:
    args = _parse_args()

    # Cargar EIR spec (legacy single-file o multi-variant según flags)
    try:
        eir_spec, source_info = load_eir_spec(
            eir_path_str=args.eir,
            variant=args.variant,
            eir_version=args.eir_version,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    # Cargar IFC
    ifc_path = resolve_model_path(args.ifc)
    try:
        model = load_ifc(ifc_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    # Ejecutar auditoría
    try:
        audit = audit_eir(model, eir_spec, str(ifc_path))
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    # Inyectar source_info en audit_meta para trazabilidad
    audit["audit_meta"]["eir_source"] = source_info

    _emit(audit, args.out)
    _print_console_summary(audit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
