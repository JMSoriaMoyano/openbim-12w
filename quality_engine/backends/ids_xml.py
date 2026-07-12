"""
quality_engine.backends.ids_xml · Backend IDS v1.0 (buildingSMART).

Invoca `ifctester` (Python · parte de IfcOpenShell) contra un fichero .ids XML
estándar y normaliza los resultados a ResultadoCheck.

Migra ~64% de los checks E6 según marco §4.2 + checklist §2.

Dependencias:
    - ifctester (parte de IfcOpenShell, instalado vía pip)
    - prototipo IDS: ids/PBSA_v0.2_prototype.ids (v2 reescrito en S6·X)

Convención S6·X:
    - El backend localiza automáticamente ids/PBSA_v<eir_version>_prototype.ids
      bajo el repo, salvo que se pase `ids_path` explícito.
    - El identifier de cada <ids:specification> mapea 1:1 al check_id E6
      (ej. identifier="C-P-03" → check_id "C-P-03").
    - Si una spec no tiene identifier, se usa el name como check_id (fallback).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from quality_engine.core.result import ResultadoCheck


# Mapeo identifier → dimension (D1-D8) según el checklist E6.
# Si una spec del IDS no está aquí, se asigna D2 por defecto.
IDENTIFIER_TO_DIMENSION: dict[str, str] = {
    "C-M-01": "D1", "C-M-02": "D1", "C-M-03": "D1", "C-M-04": "D1",
    "C-M-05": "D1", "C-M-06": "D1",
    "C-P-01": "D2", "C-P-02": "D2", "C-P-03": "D2",
    "C-P-04": "D2", "C-P-05": "D2",
    "C-R-01": "D3", "C-R-02": "D3", "C-R-03": "D3",
    "C-G-01": "D4", "C-G-02": "D4", "C-G-03": "D4",
    "C-U-01": "D5", "C-U-02": "D5", "C-U-03": "D5",
    "C-C-01": "D6", "C-C-02": "D6",
    "C-T-01": "D7", "C-T-02": "D7", "C-T-03": "D7",
    "C-Q-01": "D8", "C-Q-02": "D8", "C-Q-03": "D8",
}


def _default_ids_path(eir_version: str) -> Path:
    """Localiza ids/PBSA_v<ver>_prototype.ids relativo a la raíz del repo."""
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "ids" / f"PBSA_v{eir_version}_prototype.ids"


def _classify_ids_spec(
    pct_pass: int | float | None,
    status: bool,
    total_applicable: int,
) -> str:
    """Mapea (status, pct) → estado canónico ResultadoCheck."""
    if total_applicable == 0:
        return "not_applicable"
    if status:
        return "pass"
    # status=False → mirar pct para distinguir partial de fail
    if pct_pass is None:
        return "fail"
    try:
        pct = float(pct_pass)
    except (TypeError, ValueError):
        return "fail"
    if pct >= 95.0:
        return "pass"
    if pct >= 60.0:
        return "partial"
    return "fail"


def run_ids_backend(
    model: Any,
    ifc_path: Path,
    spec: dict[str, Any],
    eir_source: str,
    ids_path: Path | None = None,
) -> list[ResultadoCheck]:
    """
    Ejecuta validación IDS contra el modelo.

    Args:
        model        modelo IFC cargado con ifcopenshell.open()
        ifc_path     ruta al .ifc (para trazabilidad en evidence)
        spec         EIR spec mergeado (no usado por ahora, reservado para
                     filtrado futuro por variante)
        eir_source   trazabilidad '{variant}@{version}'
        ids_path     ruta al .ids XML (default: ids/PBSA_v<ver>_prototype.ids)

    Returns:
        Lista de ResultadoCheck con backend='ids_xml'.
    """
    from ifctester import ids as ifctester_ids
    from ifctester import reporter as ifctester_reporter

    eir_version = (spec.get("meta") or {}).get("eir_version", "0.2")
    if ids_path is None:
        ids_path = _default_ids_path(str(eir_version))

    if not ids_path.exists():
        return [
            ResultadoCheck(
                check_id="IDS-BACKEND-NOT-FOUND",
                dimension="D2",
                layer="no_grafica",
                status="error",
                backend="ids_xml",
                evidence={"ids_path_attempted": str(ids_path)},
                message=f"Fichero IDS no encontrado en {ids_path}.",
                eir_source=eir_source,
            )
        ]

    # 1. Cargar y validar el IDS contra schema oficial 1.0
    try:
        ids_obj = ifctester_ids.open(str(ids_path), validate=True)
    except Exception as exc:
        return [
            ResultadoCheck(
                check_id="IDS-SCHEMA-INVALID",
                dimension="D2",
                layer="no_grafica",
                status="error",
                backend="ids_xml",
                evidence={
                    "ids_path": str(ids_path),
                    "exception": str(exc),
                    "type": type(exc).__name__,
                },
                message=f"IDS no cumple schema buildingSMART 1.0: {exc}",
                eir_source=eir_source,
            )
        ]

    # 2. Validar IFC contra IDS
    ids_obj.validate(model)

    # 3. Reporter JSON
    rep = ifctester_reporter.Json(ids_obj)
    rep.report()
    report_data = json.loads(rep.to_string())

    # 4. Normalizar cada spec → ResultadoCheck
    results: list[ResultadoCheck] = []
    for s in report_data.get("specifications", []) or []:
        name = s.get("name", "")
        # identifier es la clave canónica que mapea al check_id E6
        identifier = s.get("identifier")
        if not identifier:
            # Fallback: extraer prefijo "C-X-NN" del name si existe
            head = name.split(" ", 1)[0] if name else "IDS-SPEC"
            identifier = head if head.startswith("C-") else f"IDS:{head}"

        ids_status = bool(s.get("status", False))
        pct = s.get("percent_checks_pass")
        total_applicable = int(s.get("total_applicable") or 0)
        total_pass = int(s.get("total_checks_pass") or 0)
        total_fail = int(s.get("total_checks_fail") or 0)

        canonical_status = _classify_ids_spec(pct, ids_status, total_applicable)

        # Capturar muestra de fallos para evidence
        fail_samples: list[dict[str, Any]] = []
        for req in s.get("requirements", []) or []:
            for failure in (req.get("failed_entities") or [])[:5]:
                fail_samples.append(
                    {
                        "guid": failure.get("GlobalId") or failure.get("global_id"),
                        "class": failure.get("class") or failure.get("Class"),
                        "name": failure.get("Name") or failure.get("name"),
                        "reason": failure.get("reason"),
                    }
                )
                if len(fail_samples) >= 10:
                    break
            if len(fail_samples) >= 10:
                break

        dimension = IDENTIFIER_TO_DIMENSION.get(identifier, "D2")

        score: float | None
        if total_applicable == 0:
            score = None
        elif pct is not None:
            try:
                score = round(float(pct) / 100.0, 4)
            except (TypeError, ValueError):
                score = total_pass / total_applicable if total_applicable else None
        else:
            score = total_pass / total_applicable if total_applicable else None

        results.append(
            ResultadoCheck(
                check_id=identifier,
                dimension=dimension,
                layer="no_grafica",
                status=canonical_status,
                backend="ids_xml",
                score=score,
                threshold_pass=0.95,
                threshold_partial=0.60,
                evidence={
                    "ids_spec_name": name,
                    "ids_path": str(ids_path),
                    "total_applicable": total_applicable,
                    "total_checks_pass": total_pass,
                    "total_checks_fail": total_fail,
                    "percent_checks_pass": pct,
                    "ids_status_raw": ids_status,
                    "failed_entities_sample": fail_samples,
                    "description": s.get("description"),
                    "instructions": s.get("instructions"),
                },
                message=(
                    f"IDS spec '{identifier}' {canonical_status.upper()} · "
                    f"{total_pass}/{total_applicable} entidades cumplen "
                    f"({pct if pct is not None else '?'}%)."
                ),
                eir_source=eir_source,
            )
        )

    return results
