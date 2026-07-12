"""
quality_engine.core.runner · Orquestador de auditoría.

Pipeline:
    1. Cargar EIR común + variante (vía core.merger)
    2. Cargar modelo IFC (vía ifcopenshell)
    3. Distribuir checks:
         - quality_engine_checks → backend yaml_python (rules.d*_*) o ids_xml
         - structural_checks/loin_checks legacy → adaptador a ResultadoCheck
    4. Consolidar matriz de resultados
    5. Inyectar audit_meta (eir_source, model_sha, timestamp, schema)

Marco de referencia: docs/S6L_marco_calidad.md §4.3.
"""

from __future__ import annotations

import hashlib
import importlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import ifcopenshell

from quality_engine.core.merger import load_eir_spec
from quality_engine.core.result import ResultadoCheck


# ---------------------------------------------------------------------------
# Whitelist de funciones del nuevo motor (Sección 'quality_engine_checks')
# ---------------------------------------------------------------------------

ALLOWED_QE_MODULES = {
    "quality_engine.rules.d1_modelo",
    "quality_engine.rules.d2_propiedades",
    "quality_engine.rules.d3_relaciones",
    "quality_engine.rules.d4_geometria",
    "quality_engine.rules.d5_unidades",
    "quality_engine.rules.d6_clasificacion",
    "quality_engine.rules.d7_temporal",
    "quality_engine.rules.d8_coste",
}


def _resolve_qe_fn(dotted: str) -> Callable[..., ResultadoCheck]:
    """
    Resuelve 'module.path:function' con whitelist de módulos.
    Falla si el módulo no está en ALLOWED_QE_MODULES.
    """
    if ":" not in dotted:
        raise ValueError(
            f"check_fn debe tener formato 'module.path:function', recibido: {dotted!r}"
        )
    mod_name, fn_name = dotted.split(":", 1)
    if mod_name not in ALLOWED_QE_MODULES:
        raise ValueError(
            f"Módulo no autorizado en whitelist: {mod_name!r}. "
            f"Permitidos: {sorted(ALLOWED_QE_MODULES)}"
        )
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, fn_name, None)
    if fn is None or not callable(fn):
        raise ValueError(f"Función no encontrada en {mod_name}: {fn_name}")
    return fn


# ---------------------------------------------------------------------------
# Adaptador legacy → ResultadoCheck
# ---------------------------------------------------------------------------

def _ensure_scripts_on_path() -> None:
    """Añade openbim-12w/scripts al sys.path para importar módulos legacy."""
    repo_root = Path(__file__).resolve().parents[2]
    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))


def _classify_pct(pct: float, pass_min: float, partial_min: float) -> str:
    if pct >= pass_min:
        return "pass"
    if pct >= partial_min:
        return "partial"
    return "fail"


def _adapt_legacy_structural(
    check: dict[str, Any],
    model: Any,
    eir_source: str,
) -> ResultadoCheck:
    """Adaptador para structural_checks legacy (check_mvd_compliance, check_bsdd_classification)."""
    _ensure_scripts_on_path()
    fn_name = check["check_fn"]
    params = check.get("params", {}) or {}

    if fn_name == "check_mvd_compliance":
        from s4s_structural_checks import check_mvd_compliance

        raw = check_mvd_compliance(model, **params)
    elif fn_name == "check_bsdd_classification":
        from s4s_structural_checks import check_bsdd_classification

        raw = check_bsdd_classification(model, **params)
    else:
        return ResultadoCheck(
            check_id=check["check_id"],
            dimension="D1",
            layer="no_grafica",
            status="error",
            backend="yaml_python",
            evidence={"reason": f"check_fn legacy desconocido: {fn_name}"},
            message=f"check_fn legacy no soportado por adaptador: {fn_name}",
            eir_source=eir_source,
        )

    raw_status = raw.get("compliance", "unknown")
    status_map = {
        "pass": "pass",
        "fail": "fail",
        "partial": "partial",
        "n/a": "not_applicable",
        "unknown": "error",
    }
    status = status_map.get(raw_status, "error")

    # Heurística de dimensión por nombre de check_id legacy
    cid = check["check_id"]
    if "MVD" in cid:
        dimension = "D1"
    elif "BSDD" in cid or "Classification" in cid:
        dimension = "D6"
    else:
        dimension = "D1"

    return ResultadoCheck(
        check_id=cid,
        dimension=dimension,
        layer="no_grafica",
        status=status,
        backend="yaml_python",
        score=None,
        evidence={"legacy_raw": raw, "params": params},
        message=raw.get("message", f"Legacy structural {fn_name} → {raw_status}"),
        eir_source=eir_source,
    )


def _adapt_legacy_loin(
    check: dict[str, Any],
    model: Any,
    pass_min: float,
    partial_min: float,
    eir_source: str,
) -> ResultadoCheck:
    """Adaptador para loin_checks legacy (query_missing_property)."""
    _ensure_scripts_on_path()
    from s4x_ifc_lab import query_missing_property

    raw = query_missing_property(
        model=model,
        ifc_type=check["ifc_type"],
        pset_name=check["pset"],
        prop_name=check["prop"],
    )
    pct = float(raw.get("compliance_pct", 0.0))
    total = int(raw.get("total", 0))
    present = int((raw.get("compliance", {}) or {}).get("present", 0))

    if total == 0:
        status = "not_applicable"
    else:
        status = _classify_pct(pct, pass_min, partial_min)

    # Mapear hito legacy + prop al dimension más cercano
    prop = check.get("prop", "")
    if prop in {"FireRating", "LoadBearing", "IsExternal", "ThermalTransmittance"}:
        dimension = "D2"
    elif prop in {"GrossPlannedArea", "NumberOfStoreys", "YearOfConstruction"}:
        dimension = "D2"
    else:
        dimension = "D2"

    return ResultadoCheck(
        check_id=check["check_id"],
        dimension=dimension,
        layer="no_grafica",
        status=status,
        backend="yaml_python",
        score=round(pct / 100.0, 4) if total else None,
        threshold_pass=pass_min / 100.0,
        threshold_partial=partial_min / 100.0,
        evidence={
            "ifc_type": check["ifc_type"],
            "pset": check["pset"],
            "prop": check["prop"],
            "total": total,
            "present": present,
            "compliance_pct": round(pct, 2),
            "offenders_count": len(raw.get("offenders", []) or []),
        },
        message=(
            f"{present}/{total} instancias de {check['ifc_type']} declaran "
            f"{check['pset']}.{check['prop']} ({pct:.1f}%)."
        ),
        eir_source=eir_source,
    )


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def consolidate_results(results: list[ResultadoCheck]) -> dict[str, int]:
    """Cuenta resultados por status."""
    summary = {
        "total": len(results),
        "pass": 0,
        "fail": 0,
        "partial": 0,
        "not_applicable": 0,
        "error": 0,
    }
    for r in results:
        summary[r.status] = summary.get(r.status, 0) + 1
    applicable = summary["total"] - summary["not_applicable"]
    summary["applicable"] = applicable
    summary["pct_pass"] = round(
        (summary["pass"] / applicable * 100.0) if applicable else 0.0, 2
    )
    return summary


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_audit(
    model_path: Path,
    eir_variant: str,
    eir_version: str = "0.2",
    eir_dir: Path | None = None,
    backends: list[str] | None = None,
) -> dict[str, Any]:
    """
    Ejecuta auditoría completa contra un modelo IFC.

    Args:
        model_path    ruta al .ifc (ej. out/AC20-FZK-Haus_authored.ifc)
        eir_variant   variante EIR: comun / diseno / contratista / asbuilt
        eir_version   versión EIR (default '0.2')
        eir_dir       directorio de YAMLs (default <repo>/eir)
        backends      lista filtro: ['yaml_python'], ['ids_xml'] o None (ambos)

    Returns:
        Matriz de compliance lista para serializar a JSON.
    """
    model_path = Path(model_path)
    if eir_dir is None:
        eir_dir = Path(__file__).resolve().parents[2] / "eir"
    backends_filter = set(backends) if backends else {"yaml_python", "ids_xml"}

    spec, source_info = load_eir_spec(eir_variant, eir_version, Path(eir_dir))
    eir_source = f"{eir_variant}@{eir_version}"

    model = ifcopenshell.open(str(model_path))

    thresholds = (spec.get("meta", {}) or {}).get("thresholds", {}) or {}
    pass_min = float(thresholds.get("pass_min_pct", 95.0))
    partial_min = float(thresholds.get("partial_min_pct", 60.0))

    results: list[ResultadoCheck] = []

    # 1. Quality engine checks (motor nuevo)
    if "yaml_python" in backends_filter:
        for check in spec.get("quality_engine_checks", []) or []:
            backend = check.get("backend", "yaml_python")
            if backend != "yaml_python":
                # ids_xml se ejecuta en bloque por backends/ids_xml.py (Bloque D)
                continue
            try:
                fn = _resolve_qe_fn(check["check_fn"])
                res = fn(
                    model=model,
                    ifc_path=model_path,
                    params=check.get("params", {}) or {},
                    eir_source=eir_source,
                )
                results.append(res)
            except Exception as exc:
                results.append(
                    ResultadoCheck(
                        check_id=check["check_id"],
                        dimension=check.get("dimension", "D1"),
                        layer=check.get("layer", "no_grafica"),
                        status="error",
                        backend="yaml_python",
                        evidence={"exception": str(exc), "type": type(exc).__name__},
                        message=f"Excepción ejecutando {check['check_fn']}: {exc}",
                        eir_source=eir_source,
                    )
                )

    # 2. Legacy structural_checks (vía adaptador)
    if "yaml_python" in backends_filter:
        for check in spec.get("structural_checks", []) or []:
            try:
                res = _adapt_legacy_structural(check, model, eir_source)
                results.append(res)
            except Exception as exc:
                results.append(
                    ResultadoCheck(
                        check_id=check["check_id"],
                        dimension="D1",
                        layer="no_grafica",
                        status="error",
                        backend="yaml_python",
                        evidence={"exception": str(exc), "type": type(exc).__name__},
                        message=f"Excepción en adaptador legacy: {exc}",
                        eir_source=eir_source,
                    )
                )

    # 3. Legacy loin_checks (vía adaptador)
    if "yaml_python" in backends_filter:
        for check in spec.get("loin_checks", []) or []:
            try:
                res = _adapt_legacy_loin(
                    check, model, pass_min, partial_min, eir_source
                )
                results.append(res)
            except Exception as exc:
                results.append(
                    ResultadoCheck(
                        check_id=check["check_id"],
                        dimension="D2",
                        layer="no_grafica",
                        status="error",
                        backend="yaml_python",
                        evidence={"exception": str(exc), "type": type(exc).__name__},
                        message=f"Excepción en adaptador LOIN: {exc}",
                        eir_source=eir_source,
                    )
                )

    # 4. IDS XML backend (Bloque D · se invoca desde aquí cuando esté listo)
    ids_results: list[ResultadoCheck] = []
    if "ids_xml" in backends_filter:
        try:
            from quality_engine.backends.ids_xml import run_ids_backend

            ids_results = run_ids_backend(
                model=model,
                ifc_path=model_path,
                spec=spec,
                eir_source=eir_source,
            )
            results.extend(ids_results)
        except NotImplementedError:
            # Bloque D aún no implementado: continúa sin IDS
            pass
        except Exception as exc:
            results.append(
                ResultadoCheck(
                    check_id="IDS-BACKEND-ERROR",
                    dimension="D2",
                    layer="no_grafica",
                    status="error",
                    backend="ids_xml",
                    evidence={"exception": str(exc), "type": type(exc).__name__},
                    message=f"Backend ids_xml falló: {exc}",
                    eir_source=eir_source,
                )
            )

    # 5. Audit meta + serialización
    summary = consolidate_results(results)
    audit_meta = {
        "eir_source": eir_source,
        "eir_variant": eir_variant,
        "eir_version": eir_version,
        "eir_paths": source_info.get("paths_used", []),
        "model_path": str(model_path),
        "model_sha256": _sha256_of_file(model_path),
        "model_schema": getattr(model, "schema", None),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "thresholds": {"pass_min_pct": pass_min, "partial_min_pct": partial_min},
        "backends_used": sorted(backends_filter),
        "engine_version": "quality_engine 0.2.0-s6x",
    }

    return {
        "audit_meta": audit_meta,
        "summary": summary,
        "results": [r.to_dict() for r in results],
    }
