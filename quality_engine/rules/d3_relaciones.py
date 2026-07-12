"""
quality_engine.rules.d3_relaciones · Reglas D3 Relaciones.

Checks cubiertos (E6 checklist §3.3):
    C-R-01 · containment a IfcBuildingStorey       [yaml_python]
    C-R-02 · jerarquía Project→Site→Building→Storey [yaml_python]
    C-R-03 · nº elementos huérfanos == 0           [yaml_python]

Capa ISO 19650-2: no gráfica.
Variantes aplicables: todas.
"""

from pathlib import Path
from typing import Any

from quality_engine.core.result import ResultadoCheck


DEFAULT_TARGET_TYPES = (
    "IfcWall",
    "IfcSlab",
    "IfcDoor",
    "IfcWindow",
    "IfcColumn",
    "IfcBeam",
)


def _collect_targets(model: Any, target_types: tuple[str, ...]) -> list[Any]:
    """Devuelve la unión de instancias de los tipos pedidos."""
    out: list[Any] = []
    for t in target_types:
        try:
            out.extend(model.by_type(t))
        except Exception:
            # Tipo no existe en el esquema (raro pero defensivo)
            continue
    return out


def check_containment_to_storey(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """
    C-R-01 · Todo IfcProduct físico debe estar contenido en un IfcBuildingStorey
    vía IfcRelContainedInSpatialStructure.
    """
    target_types = tuple(params.get("target_types") or DEFAULT_TARGET_TYPES)
    products = _collect_targets(model, target_types)

    total = len(products)
    if total == 0:
        return ResultadoCheck(
            check_id="C-R-01",
            dimension="D3",
            layer="no_grafica",
            status="not_applicable",
            backend="yaml_python",
            score=None,
            evidence={"target_types": list(target_types), "total": 0},
            message="No hay productos de los tipos diana en el modelo.",
            eir_source=eir_source,
        )

    contained = 0
    offenders: list[dict[str, Any]] = []
    for p in products:
        rels = getattr(p, "ContainedInStructure", None) or []
        is_in_storey = False
        for rel in rels:
            struct = getattr(rel, "RelatingStructure", None)
            if struct is not None and struct.is_a("IfcBuildingStorey"):
                is_in_storey = True
                break
        if is_in_storey:
            contained += 1
        else:
            if len(offenders) < 20:  # cap para no inflar JSON
                offenders.append(
                    {
                        "guid": getattr(p, "GlobalId", None),
                        "type": p.is_a(),
                        "name": getattr(p, "Name", None),
                    }
                )

    score = contained / total
    status = "pass" if score == 1.0 else ("partial" if score >= 0.6 else "fail")
    return ResultadoCheck(
        check_id="C-R-01",
        dimension="D3",
        layer="no_grafica",
        status=status,
        backend="yaml_python",
        score=round(score, 4),
        threshold_pass=1.0,
        threshold_partial=0.6,
        evidence={
            "target_types": list(target_types),
            "total": total,
            "contained_in_storey": contained,
            "offenders_count": total - contained,
            "offenders_sample": offenders,
        },
        message=(
            f"{contained}/{total} productos contenidos en IfcBuildingStorey "
            f"({score:.1%})."
        ),
        eir_source=eir_source,
    )


def check_spatial_hierarchy(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """
    C-R-02 · Jerarquía completa IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey
    vía IfcRelAggregates.
    """
    projects = model.by_type("IfcProject")
    sites = model.by_type("IfcSite")
    buildings = model.by_type("IfcBuilding")
    storeys = model.by_type("IfcBuildingStorey")

    counts = {
        "IfcProject": len(projects),
        "IfcSite": len(sites),
        "IfcBuilding": len(buildings),
        "IfcBuildingStorey": len(storeys),
    }

    def _children(entity: Any) -> list[Any]:
        out: list[Any] = []
        for rel in getattr(entity, "IsDecomposedBy", None) or []:
            if rel.is_a("IfcRelAggregates"):
                out.extend(rel.RelatedObjects or [])
        return out

    # Verificamos rutas Project → Site → Building → Storey
    ok_proj_site = any(
        any(child.is_a("IfcSite") for child in _children(p)) for p in projects
    )
    ok_site_bldg = any(
        any(child.is_a("IfcBuilding") for child in _children(s)) for s in sites
    )
    ok_bldg_storey = any(
        any(child.is_a("IfcBuildingStorey") for child in _children(b))
        for b in buildings
    )

    chain_ok = all([
        counts["IfcProject"] == 1,
        counts["IfcSite"] >= 1,
        counts["IfcBuilding"] >= 1,
        counts["IfcBuildingStorey"] >= 1,
        ok_proj_site,
        ok_site_bldg,
        ok_bldg_storey,
    ])

    issues: list[str] = []
    if counts["IfcProject"] != 1:
        issues.append(f"IfcProject count={counts['IfcProject']} (debe ser 1)")
    if counts["IfcSite"] < 1:
        issues.append("IfcSite ausente")
    if counts["IfcBuilding"] < 1:
        issues.append("IfcBuilding ausente")
    if counts["IfcBuildingStorey"] < 1:
        issues.append("IfcBuildingStorey ausente")
    if not ok_proj_site:
        issues.append("Project no agrega Site vía IfcRelAggregates")
    if not ok_site_bldg:
        issues.append("Site no agrega Building vía IfcRelAggregates")
    if not ok_bldg_storey:
        issues.append("Building no agrega Storey vía IfcRelAggregates")

    return ResultadoCheck(
        check_id="C-R-02",
        dimension="D3",
        layer="no_grafica",
        status="pass" if chain_ok else "fail",
        backend="yaml_python",
        score=1.0 if chain_ok else 0.0,
        evidence={
            "counts": counts,
            "edge_project_site": ok_proj_site,
            "edge_site_building": ok_site_bldg,
            "edge_building_storey": ok_bldg_storey,
            "issues": issues,
        },
        message=(
            "Jerarquía Project→Site→Building→Storey completa."
            if chain_ok
            else "Jerarquía espacial rota: " + "; ".join(issues)
        ),
        eir_source=eir_source,
    )


def check_no_orphans(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """
    C-R-03 · Productos físicos sin containment ni agregación = huérfanos.
    Un producto puede no estar contenido directamente en un storey si está
    agregado a otro elemento (p.ej. abertura agregada a muro). Aceptamos como
    no-huérfano si tiene `ContainedInStructure` no vacío O `Decomposes` no vacío.
    """
    target_types = tuple(params.get("target_types") or DEFAULT_TARGET_TYPES)
    products = _collect_targets(model, target_types)
    total = len(products)
    if total == 0:
        return ResultadoCheck(
            check_id="C-R-03",
            dimension="D3",
            layer="no_grafica",
            status="not_applicable",
            backend="yaml_python",
            score=None,
            evidence={"target_types": list(target_types), "total": 0},
            message="No hay productos de los tipos diana en el modelo.",
            eir_source=eir_source,
        )

    orphans: list[dict[str, Any]] = []
    for p in products:
        has_containment = bool(getattr(p, "ContainedInStructure", None))
        has_decomposes = bool(getattr(p, "Decomposes", None))
        if not (has_containment or has_decomposes):
            if len(orphans) < 20:
                orphans.append(
                    {
                        "guid": getattr(p, "GlobalId", None),
                        "type": p.is_a(),
                        "name": getattr(p, "Name", None),
                    }
                )

    orphan_count = sum(
        1
        for p in products
        if not (
            bool(getattr(p, "ContainedInStructure", None))
            or bool(getattr(p, "Decomposes", None))
        )
    )
    ok = orphan_count == 0
    return ResultadoCheck(
        check_id="C-R-03",
        dimension="D3",
        layer="no_grafica",
        status="pass" if ok else "fail",
        backend="yaml_python",
        score=1.0 - (orphan_count / total),
        evidence={
            "target_types": list(target_types),
            "total": total,
            "orphans_count": orphan_count,
            "orphans_sample": orphans,
        },
        message=(
            "Sin productos huérfanos."
            if ok
            else f"{orphan_count}/{total} productos huérfanos (sin containment ni agregación)."
        ),
        eir_source=eir_source,
    )
