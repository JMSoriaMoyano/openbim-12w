"""
quality_engine.rules.d8_coste · Reglas D8 Coste (5D).

Checks cubiertos (E6 checklist §3.8):
    C-Q-01 · 100% muros con Qto_WallBaseQuantities         [ids_xml]
    C-Q-02 · ≥ 80% productos con IfcCostItem asociado      [ids_xml]
    C-Q-03 · sniff QTO declarado vs calculado (tol 5%)     [yaml_python · sniff]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: diseño exclusivamente.

C-Q-01 y C-Q-02 se ejecutan vía backend IDS (rules nativas presencia/agregación).
C-Q-03 es sniff numérico: contrasta QTO declarado contra cálculo desde geometría.
"""

from pathlib import Path
from typing import Any

from quality_engine.core.result import ResultadoCheck


def _calc_volume_from_geometry(model: Any, product: Any) -> float | None:
    """
    Calcula el volumen del producto desde su representación geométrica usando
    el ShapeAnalyser de ifcopenshell. Devuelve m³ o None si no se puede.
    """
    try:
        import ifcopenshell.geom as geom
        import ifcopenshell.util.shape as shape_util

        settings = geom.settings()
        settings.set("use-world-coords", True)
        shape = geom.create_shape(settings, product)
        # ifcopenshell.util.shape.get_volume devuelve m³ si las unidades del modelo lo permiten
        vol = shape_util.get_volume(shape.geometry)
        if vol is None:
            return None
        return float(vol)
    except Exception:
        return None


def sniff_qto_coherence(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """
    C-Q-03 · Sniff QTO declarado vs calculado desde geometría.

    Para cada muro con Qto_WallBaseQuantities.NetVolume declarado, calcular
    el volumen desde la geometría real. Si |declarado - calculado| / declarado
    > tolerance_pct → discrepancia.

    FZK-Haus baseline: tiene Qto_WallBaseQuantities parciales en algunos muros.
    Si la geometría no es lo bastante limpia para calcular volumen, el muro se
    marca como 'inconclusivo' y se excluye del ratio.
    """
    import ifcopenshell.util.element as ie_util

    tol_pct = float(params.get("tolerance_pct") or 5.0)
    sample_size = int(params.get("sample_size") or 10)
    target_type = params.get("target_type") or "IfcWall"
    qto_pset = params.get("qto_pset") or "Qto_WallBaseQuantities"
    qto_prop = params.get("qto_prop") or "NetVolume"

    products = model.by_type(target_type)
    if not products:
        return ResultadoCheck(
            check_id="C-Q-03",
            dimension="D8",
            layer="no_grafica",
            status="not_applicable",
            backend="yaml_python",
            score=None,
            evidence={
                "target_type": target_type,
                "sample_size_requested": sample_size,
                "reason": f"No hay instancias de {target_type} en el modelo.",
            },
            message=f"No hay {target_type} para muestrear.",
            eir_source=eir_source,
        )

    declared_pairs: list[tuple[Any, float]] = []
    for p in products:
        psets = ie_util.get_psets(p) or {}
        qto = psets.get(qto_pset) or {}
        val = qto.get(qto_prop)
        if val is None:
            continue
        try:
            declared_pairs.append((p, float(val)))
        except (TypeError, ValueError):
            continue
        if len(declared_pairs) >= sample_size:
            break

    if not declared_pairs:
        return ResultadoCheck(
            check_id="C-Q-03",
            dimension="D8",
            layer="no_grafica",
            status="not_applicable",
            backend="yaml_python",
            score=None,
            evidence={
                "target_type": target_type,
                "qto_pset": qto_pset,
                "qto_prop": qto_prop,
                "total_products": len(products),
                "with_declared_qto": 0,
                "reason": f"Ningún {target_type} declara {qto_pset}.{qto_prop}.",
            },
            message=(
                f"Sin {qto_pset}.{qto_prop} declarado en ningún {target_type}. "
                "Sniff coste 5D no aplicable."
            ),
            eir_source=eir_source,
        )

    comparisons: list[dict[str, Any]] = []
    inconclusive: list[dict[str, Any]] = []
    in_tol = 0
    out_tol = 0
    for product, declared in declared_pairs:
        calculated = _calc_volume_from_geometry(model, product)
        if calculated is None or declared <= 0:
            inconclusive.append(
                {
                    "guid": getattr(product, "GlobalId", None),
                    "type": product.is_a(),
                    "declared": declared,
                    "reason": "geom_failed" if calculated is None else "declared_zero",
                }
            )
            continue
        diff_pct = abs(calculated - declared) / declared * 100.0
        comp = {
            "guid": getattr(product, "GlobalId", None),
            "type": product.is_a(),
            "declared_m3": round(declared, 6),
            "calculated_m3": round(calculated, 6),
            "diff_pct": round(diff_pct, 3),
            "within_tolerance": diff_pct <= tol_pct,
        }
        comparisons.append(comp)
        if diff_pct <= tol_pct:
            in_tol += 1
        else:
            out_tol += 1

    evaluated = in_tol + out_tol
    if evaluated == 0:
        return ResultadoCheck(
            check_id="C-Q-03",
            dimension="D8",
            layer="no_grafica",
            status="error",
            backend="yaml_python",
            score=None,
            evidence={
                "target_type": target_type,
                "declared_count": len(declared_pairs),
                "inconclusive_count": len(inconclusive),
                "inconclusive_sample": inconclusive[:5],
                "tolerance_pct": tol_pct,
            },
            message=(
                f"Todos los {len(declared_pairs)} {target_type} con QTO declarado "
                "fueron inconclusivos al calcular volumen desde geometría."
            ),
            eir_source=eir_source,
        )

    ratio = in_tol / evaluated
    # Para sniff usamos umbrales más laxos que las reglas duras:
    # pass ≥ 0.95, partial ≥ 0.7, fail < 0.7
    if ratio >= 0.95:
        status = "pass"
    elif ratio >= 0.70:
        status = "partial"
    else:
        status = "fail"

    return ResultadoCheck(
        check_id="C-Q-03",
        dimension="D8",
        layer="no_grafica",
        status=status,
        backend="yaml_python",
        score=round(ratio, 4),
        threshold_pass=0.95,
        threshold_partial=0.70,
        evidence={
            "target_type": target_type,
            "qto_pset": qto_pset,
            "qto_prop": qto_prop,
            "tolerance_pct": tol_pct,
            "sample_size_requested": sample_size,
            "with_declared_qto": len(declared_pairs),
            "evaluated": evaluated,
            "within_tolerance": in_tol,
            "out_of_tolerance": out_tol,
            "inconclusive_count": len(inconclusive),
            "comparisons_sample": comparisons[:10],
        },
        message=(
            f"{in_tol}/{evaluated} {target_type} dentro de tolerancia ±{tol_pct}% "
            f"(ratio {ratio:.1%}). Inconclusivos por geometría: {len(inconclusive)}."
        ),
        eir_source=eir_source,
    )
