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
    python scripts/s4s_audit_eir.py \
        --ifc AC20-FZK-Haus.ifc \
        --eir eir/PBSA_v0.1_obligatorias.yaml \
        --out out/s4s_compliance_matrix_baseline.json

Diseño
------
- Despachador (dispatch) explícito por nombre de función: ningún eval/import dinámico
  sin whitelist. Solo las 3 funciones declaradas en CHECK_REGISTRY son invocables.
- Funciones puras: no muta el YAML, no escribe ficheros aparte del --out.
- Output JSON-serializable end-to-end, listo para consumir desde docs (Bloque C).

Autor: José M. Soria (NEXUM)
Versión: 0.1 (S4·S Bloque B · orquestador inicial Obligatorias)
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
# Registro de funciones invocables desde YAML (whitelist explícita)
# ---------------------------------------------------------------------------

CHECK_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "query_missing_property": query_missing_property,
    "check_mvd_compliance": check_mvd_compliance,
    "check_bsdd_classification": check_bsdd_classification,
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

    return {
        "eir_meta": meta,
        "audit_meta": {
            "ifc_audited": ifc_path_str,
            "structural_checks_count": len(structural),
            "loin_checks_count": len(loin),
            "total_checks": len(results),
            "thresholds_applied": {
                "pass_min_pct": pass_min,
                "partial_min_pct": partial_min,
            },
        },
        "summary": _build_summary(results),
        "results": results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="S4·S · Orquestador de auditoría EIR (YAML → matriz JSON)"
    )
    parser.add_argument("--ifc", required=True, help="Ruta o nombre de fichero IFC")
    parser.add_argument(
        "--eir",
        required=True,
        help="Ruta al YAML de chequeos EIR (ej. eir/PBSA_v0.1_obligatorias.yaml)",
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

    # Cargar EIR YAML
    eir_path = Path(args.eir)
    if not eir_path.exists():
        print(f"[ERROR] EIR YAML no encontrado: {eir_path}", file=sys.stderr)
        return 1
    with eir_path.open("r", encoding="utf-8") as fh:
        eir_spec = yaml.safe_load(fh)
    if not isinstance(eir_spec, dict):
        print(f"[ERROR] EIR YAML no es un mapping en la raíz: {eir_path}", file=sys.stderr)
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

    _emit(audit, args.out)
    _print_console_summary(audit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
