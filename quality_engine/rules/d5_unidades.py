"""
quality_engine.rules.d5_unidades · Reglas D5 Unidades.

Checks cubiertos (E6 checklist §3.5):
    C-U-01 · IfcUnitAssignment presente          [yaml_python]
    C-U-02 · sistema métrico SI                  [yaml_python]
    C-U-03 · sniff test longitudes coherente     [yaml_python · sniff]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: todas.
"""

from pathlib import Path
from statistics import median
from typing import Any

from quality_engine.core.result import ResultadoCheck


# Factor de conversión a metros para los IfcSIUnit prefix más comunes
SI_PREFIX_TO_METER = {
    None: 1.0,
    "MILLI": 1e-3,
    "CENTI": 1e-2,
    "DECI": 1e-1,
    "KILO": 1e3,
}


def _get_si_units(model: Any) -> dict[str, dict[str, Any]]:
    """
    Devuelve {UnitType: {Name, Prefix, factor_m}} para los IfcSIUnit del modelo.

    Solo considera el primer IfcUnitAssignment (debería haber exactamente uno).
    """
    out: dict[str, dict[str, Any]] = {}
    ua_list = model.by_type("IfcUnitAssignment")
    if not ua_list:
        return out
    ua = ua_list[0]
    for u in ua.Units or []:
        if u.is_a("IfcSIUnit"):
            unit_type = getattr(u, "UnitType", None)
            name = getattr(u, "Name", None)
            prefix = getattr(u, "Prefix", None)
            factor = SI_PREFIX_TO_METER.get(prefix, 1.0)
            out[unit_type] = {
                "name": name,
                "prefix": prefix,
                "ifc_class": "IfcSIUnit",
                "factor_to_base_m": factor if name == "METRE" else None,
            }
        elif u.is_a("IfcConversionBasedUnit") or u.is_a("IfcDerivedUnit"):
            unit_type = getattr(u, "UnitType", None)
            out[unit_type] = {
                "name": getattr(u, "Name", None),
                "ifc_class": u.is_a(),
                "non_si": True,
            }
    return out


def check_unit_assignment_present(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """C-U-01 · Existe al menos un IfcUnitAssignment con ≥ 1 unidad."""
    ua_list = model.by_type("IfcUnitAssignment")
    n_ua = len(ua_list)
    units_count = 0
    if n_ua >= 1:
        units_count = len(ua_list[0].Units or [])

    ok = n_ua >= 1 and units_count > 0
    return ResultadoCheck(
        check_id="C-U-01",
        dimension="D5",
        layer="no_grafica",
        status="pass" if ok else "fail",
        backend="yaml_python",
        score=1.0 if ok else 0.0,
        evidence={
            "ifc_unit_assignment_count": n_ua,
            "units_in_first_assignment": units_count,
        },
        message=(
            f"IfcUnitAssignment presente con {units_count} unidades."
            if ok
            else "Modelo sin IfcUnitAssignment o sin unidades declaradas."
        ),
        eir_source=eir_source,
    )


def check_si_metric_system(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """C-U-02 · Las unidades requeridas son IfcSIUnit con nombre esperado."""
    required = params.get("required_units") or {
        "LENGTHUNIT": "METRE",
        "AREAUNIT": "SQUARE_METRE",
        "VOLUMEUNIT": "CUBIC_METRE",
    }
    units = _get_si_units(model)

    issues: list[str] = []
    found: dict[str, dict[str, Any]] = {}
    for unit_type, expected_name in required.items():
        u = units.get(unit_type)
        if u is None:
            issues.append(f"{unit_type}: no declarada")
            found[unit_type] = None
            continue
        found[unit_type] = u
        if u.get("non_si"):
            issues.append(
                f"{unit_type}: usa {u.get('ifc_class')} (no IfcSIUnit) name={u.get('name')}"
            )
            continue
        if u.get("name") != expected_name:
            issues.append(
                f"{unit_type}: name={u.get('name')} (esperado {expected_name})"
            )

    ok = len(issues) == 0
    return ResultadoCheck(
        check_id="C-U-02",
        dimension="D5",
        layer="no_grafica",
        status="pass" if ok else "fail",
        backend="yaml_python",
        score=1.0 if ok else max(0.0, 1.0 - len(issues) / max(1, len(required))),
        evidence={
            "required_units": required,
            "found_units": found,
            "issues": issues,
        },
        message=(
            "Sistema SI métrico correcto: " + ", ".join(
                f"{k}={v.get('name')}" for k, v in found.items() if v
            )
            if ok
            else "Problemas en unidades SI: " + "; ".join(issues)
        ),
        eir_source=eir_source,
    )


def _length_samples_from_walls(model: Any, sample_size: int) -> list[float]:
    """
    Muestrea hasta `sample_size` longitudes de muros usando Qto_WallBaseQuantities.Length
    si está disponible; si no, usa la altura del bbox como fallback de magnitud.
    """
    import ifcopenshell.util.element as ie_util

    samples: list[float] = []
    walls = model.by_type("IfcWall")
    for w in walls:
        if len(samples) >= sample_size:
            break
        psets = ie_util.get_psets(w) or {}
        qto = psets.get("Qto_WallBaseQuantities") or {}
        length = qto.get("Length") or qto.get("Width") or qto.get("Height")
        if length is not None:
            try:
                samples.append(float(length))
            except (TypeError, ValueError):
                continue
    return samples


def _slab_area_samples(model: Any, sample_size: int) -> list[float]:
    """Muestrea áreas netas de losas (raíz² sirve como longitud-equivalente)."""
    import ifcopenshell.util.element as ie_util
    import math

    samples: list[float] = []
    for s in model.by_type("IfcSlab"):
        if len(samples) >= sample_size:
            break
        psets = ie_util.get_psets(s) or {}
        qto = psets.get("Qto_SlabBaseQuantities") or {}
        area = qto.get("NetArea") or qto.get("GrossArea")
        if area is not None:
            try:
                samples.append(math.sqrt(float(area)))
            except (TypeError, ValueError):
                continue
    return samples


def sniff_length_coherence(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """
    C-U-03 · Sniff numérico de longitudes.

    Muestrea hasta `sample_size` longitudes de muros (Qto_WallBaseQuantities.Length)
    y opcionalmente losas (sqrt(NetArea)) y verifica que la mediana cae dentro del
    rango plausible (expected_range_m). Detecta unidades mal interpretadas
    (típicamente factor 1000: mm declarado como m, o viceversa).
    """
    expected = params.get("expected_range_m") or {"min": 0.05, "max": 100.0}
    sample_size = int(params.get("sample_size") or 20)
    min_m = float(expected.get("min", 0.05))
    max_m = float(expected.get("max", 100.0))

    wall_samples = _length_samples_from_walls(model, sample_size)
    slab_samples = _slab_area_samples(
        model, max(0, sample_size - len(wall_samples))
    )
    all_samples = wall_samples + slab_samples

    if not all_samples:
        return ResultadoCheck(
            check_id="C-U-03",
            dimension="D5",
            layer="no_grafica",
            status="not_applicable",
            backend="yaml_python",
            score=None,
            evidence={
                "expected_range_m": expected,
                "wall_samples": [],
                "slab_samples": [],
                "reason": "Sin Qto_WallBaseQuantities ni Qto_SlabBaseQuantities en el modelo.",
            },
            message="No hay QTO de muros/losas para muestrear longitudes.",
            eir_source=eir_source,
        )

    med = float(median(all_samples))
    in_range = min_m <= med <= max_m

    # Detección de factor 1000 (sospecha de unidades mm/m mal etiquetadas)
    suspect_factor: float | None = None
    if not in_range:
        if med > max_m and (med / 1000.0) >= min_m and (med / 1000.0) <= max_m:
            suspect_factor = 1000.0
        elif med < min_m and (med * 1000.0) >= min_m and (med * 1000.0) <= max_m:
            suspect_factor = 0.001

    status = "pass" if in_range else "fail"
    return ResultadoCheck(
        check_id="C-U-03",
        dimension="D5",
        layer="no_grafica",
        status=status,
        backend="yaml_python",
        score=1.0 if in_range else 0.0,
        evidence={
            "expected_range_m": expected,
            "wall_samples_count": len(wall_samples),
            "slab_samples_count": len(slab_samples),
            "median_m": round(med, 6),
            "min_m": round(min(all_samples), 6),
            "max_m": round(max(all_samples), 6),
            "in_range": in_range,
            "suspect_unit_factor": suspect_factor,
        },
        message=(
            f"Mediana de longitudes = {med:.3f} m dentro del rango "
            f"[{min_m}, {max_m}]."
            if in_range
            else (
                f"Mediana fuera de rango: {med:.3f} m (esperado [{min_m}, {max_m}]). "
                + (
                    f"Sospecha de factor de unidades x{suspect_factor}."
                    if suspect_factor
                    else "Sin patrón claro de factor."
                )
            )
        ),
        eir_source=eir_source,
    )
