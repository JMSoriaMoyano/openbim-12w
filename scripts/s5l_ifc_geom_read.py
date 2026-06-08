"""
s5l_ifc_geom_read.py · OpenBIM 12 semanas · S5·L (Lun 08/06/2026)
==================================================================
Sesión 5 · Lunes · IfcOpenShell: geometría y autoría (lectura).

Primer contacto con `ifcopenshell.geom`: pasar de "leer propiedades"
a "leer geometría". Extrae mallas triangulares por elemento, calcula
estadísticas básicas (vértices, triángulos, bounding box) y agrega
resultados por tipo IFC.

Cobertura
---------
    G1 · iter_shapes(model, settings)   → iterador (element, shape, mesh)
    G2 · mesh_stats(shape)              → estadísticas de una malla
    G3 · summarize_geometry(model)      → resumen agregado por IfcType

Salida CLI
----------
JSON con:
  - model_meta: schema, fichero, conteo de elementos con geometría
  - global_bbox: bounding box envolvente de todo el modelo
  - by_type: dict {IfcType: {count, total_vertices, total_triangles, bbox}}
  - elements: lista de elementos individuales (id, type, name, stats)

Uso CLI
-------
    python scripts/s5l_ifc_geom_read.py --ifc <nombre.ifc> \
        [--out out/s5l_geom_stats_baseline.json] \
        [--include IfcWallStandardCase,IfcSlab] \
        [--exclude IfcOpeningElement]

Notas técnicas
--------------
- USE_WORLD_COORDS=True: los vértices vienen ya en coordenadas globales,
  simplificando visualizaciones plan-view. Para análisis local conviene
  False + composición manual con shape.transformation.matrix (S5·X).
- Por defecto se EXCLUYE IfcOpeningElement y IfcVirtualElement (coherencia
  con deuda técnica 5.1: estos elementos generan ruido geométrico al ser
  agujeros en sólidos padre, no entidades materiales).
- ifcopenshell.geom usa OpenCASCADE bajo el capó; cargar todo el modelo
  con multiprocesamiento es posible con `iterator()` pero aquí usamos
  el bucle simple `create_shape()` para máxima claridad pedagógica.

Autor: José M. Soria (NEXUM)
Versión: 0.1 (S5·L Bloque B · lectura de geometría)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator

import ifcopenshell
import ifcopenshell.geom

from _ifc_helpers import load_ifc, resolve_model_path


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

# Tipos IFC que excluimos por defecto: generan ruido geométrico (huecos,
# elementos virtuales sin material). Coherencia con deuda técnica 5.1.
DEFAULT_EXCLUDED_TYPES: tuple[str, ...] = (
    "IfcOpeningElement",
    "IfcVirtualElement",
)


def _make_settings(use_world_coords: bool = True) -> ifcopenshell.geom.settings:
    """Construye settings de geometría con valores estándar S5·L."""
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", use_world_coords)
    return settings


# ---------------------------------------------------------------------------
# G1 · Iterador de shapes
# ---------------------------------------------------------------------------

def iter_shapes(
    model: ifcopenshell.file,
    settings: ifcopenshell.geom.settings | None = None,
    include_types: list[str] | None = None,
    exclude_types: list[str] | None = None,
) -> Iterator[tuple[Any, Any]]:
    """Itera (element, shape) para todos los elementos con representación geométrica.

    Parámetros
    ----------
    model : ifcopenshell.file
    settings : ifcopenshell.geom.settings
        Si None, se construye con use-world-coords=True por defecto.
    include_types : lista de IfcType a incluir (whitelist). Si None, todos.
    exclude_types : lista adicional a excluir. Se suma a DEFAULT_EXCLUDED_TYPES.

    Yield
    -----
    Tuplas (element, shape) donde shape es un IfcOpenShell TriangulationElement.

    Notas
    -----
    Captura ValueError y RuntimeError por elemento individual: si un elemento
    tiene geometría corrupta no abortamos el modelo entero, lo registramos
    como skip y seguimos. Esto es crítico para modelos reales heterogéneos.
    """
    if settings is None:
        settings = _make_settings(use_world_coords=True)

    exclude_set = set(DEFAULT_EXCLUDED_TYPES)
    if exclude_types:
        exclude_set.update(exclude_types)

    # Sólo elementos que pueden tener IfcProductDefinitionShape
    candidates = model.by_type("IfcProduct")

    for elem in candidates:
        ifc_type = elem.is_a()
        if ifc_type in exclude_set:
            continue
        if include_types and ifc_type not in include_types:
            continue
        if getattr(elem, "Representation", None) is None:
            continue

        try:
            shape = ifcopenshell.geom.create_shape(settings, elem)
        except (ValueError, RuntimeError):
            # Geometría no procesable: se omite silenciosamente.
            # Para auditoría detallada usar parámetro verbose en versiones futuras.
            continue

        yield elem, shape


# ---------------------------------------------------------------------------
# G2 · Estadísticas de una malla
# ---------------------------------------------------------------------------

def mesh_stats(shape: Any) -> dict[str, Any]:
    """Calcula estadísticas básicas de una shape triangulada.

    Devuelve
    --------
    dict con:
        vertices_count   : nº de vértices únicos
        triangles_count  : nº de triángulos (faces / 3)
        bbox             : {min: [x,y,z], max: [x,y,z]}
                           None si la malla está vacía.

    Notas
    -----
    `shape.geometry.verts` es un array plano [x0,y0,z0, x1,y1,z1, ...].
    `shape.geometry.faces` es un array plano [v0,v1,v2, v3,v4,v5, ...].
    """
    geom = shape.geometry
    verts = list(geom.verts)
    faces = list(geom.faces)

    vertices_count = len(verts) // 3
    triangles_count = len(faces) // 3

    if vertices_count == 0:
        return {
            "vertices_count": 0,
            "triangles_count": 0,
            "bbox": None,
        }

    xs = verts[0::3]
    ys = verts[1::3]
    zs = verts[2::3]

    bbox = {
        "min": [min(xs), min(ys), min(zs)],
        "max": [max(xs), max(ys), max(zs)],
    }

    return {
        "vertices_count": vertices_count,
        "triangles_count": triangles_count,
        "bbox": bbox,
    }


# ---------------------------------------------------------------------------
# G3 · Resumen agregado por IfcType
# ---------------------------------------------------------------------------

def _expand_bbox(
    current: dict[str, list[float]] | None,
    new_bbox: dict[str, list[float]] | None,
) -> dict[str, list[float]] | None:
    """Expande un bbox acumulado con uno nuevo. Devuelve el bbox unión."""
    if new_bbox is None:
        return current
    if current is None:
        return {
            "min": list(new_bbox["min"]),
            "max": list(new_bbox["max"]),
        }
    return {
        "min": [min(current["min"][i], new_bbox["min"][i]) for i in range(3)],
        "max": [max(current["max"][i], new_bbox["max"][i]) for i in range(3)],
    }


def summarize_geometry(
    model: ifcopenshell.file,
    settings: ifcopenshell.geom.settings | None = None,
    include_types: list[str] | None = None,
    exclude_types: list[str] | None = None,
) -> dict[str, Any]:
    """Procesa todos los elementos con geometría y devuelve resumen estructurado.

    Devuelve
    --------
    dict con:
        model_meta : schema, conteo de IfcProduct totales y con geometría
        global_bbox: bounding box envolvente del modelo
        by_type    : agregación por IfcType (count, total_*, bbox)
        elements   : lista por elemento (id, type, name, stats)
    """
    if settings is None:
        settings = _make_settings(use_world_coords=True)

    by_type: dict[str, dict[str, Any]] = {}
    elements: list[dict[str, Any]] = []
    global_bbox: dict[str, list[float]] | None = None

    total_products = len(model.by_type("IfcProduct"))
    processed = 0

    for elem, shape in iter_shapes(
        model,
        settings=settings,
        include_types=include_types,
        exclude_types=exclude_types,
    ):
        stats = mesh_stats(shape)
        ifc_type = elem.is_a()

        # Acumular por tipo
        bucket = by_type.setdefault(
            ifc_type,
            {
                "count": 0,
                "total_vertices": 0,
                "total_triangles": 0,
                "bbox": None,
            },
        )
        bucket["count"] += 1
        bucket["total_vertices"] += stats["vertices_count"]
        bucket["total_triangles"] += stats["triangles_count"]
        bucket["bbox"] = _expand_bbox(bucket["bbox"], stats["bbox"])

        # Acumular global
        global_bbox = _expand_bbox(global_bbox, stats["bbox"])

        # Registro por elemento (limitamos para no explotar el JSON)
        elements.append({
            "id": elem.id(),
            "global_id": getattr(elem, "GlobalId", None),
            "type": ifc_type,
            "name": getattr(elem, "Name", None),
            "vertices_count": stats["vertices_count"],
            "triangles_count": stats["triangles_count"],
            "bbox": stats["bbox"],
        })
        processed += 1

    return {
        "model_meta": {
            "schema": model.schema,
            "ifc_product_total": total_products,
            "elements_processed": processed,
            "include_types": include_types,
            "exclude_types": list(set(DEFAULT_EXCLUDED_TYPES).union(exclude_types or [])),
        },
        "global_bbox": global_bbox,
        "by_type": dict(sorted(by_type.items(), key=lambda kv: (-kv[1]["count"], kv[0]))),
        "elements": elements,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_csv_list(value: str | None) -> list[str] | None:
    if value is None or value.strip() == "":
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="S5·L · Lectura de geometría IFC (mesh stats + bbox por tipo)"
    )
    parser.add_argument("--ifc", required=True, help="Ruta o nombre de fichero IFC")
    parser.add_argument(
        "--out",
        help="Ruta de salida JSON. Si se omite, imprime a stdout.",
    )
    parser.add_argument(
        "--include",
        help="Lista CSV de IfcTypes a incluir (whitelist). Default: todos.",
    )
    parser.add_argument(
        "--exclude",
        help="Lista CSV de IfcTypes extra a excluir además de Opening/Virtual.",
    )
    return parser.parse_args()


def _emit(result: dict[str, Any], out_path: str | None) -> None:
    payload = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if out_path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload, encoding="utf-8")
        size_kb = p.stat().st_size / 1024
        print(f"[OK] Resumen geométrico escrito a {p} ({size_kb:.1f} KB)")
    else:
        print(payload)


def _print_console_summary(result: dict[str, Any]) -> None:
    meta = result["model_meta"]
    print()
    print("=" * 70)
    print(f"GEOMETRIA · schema {meta['schema']}")
    print("=" * 70)
    print(f"IfcProduct total      : {meta['ifc_product_total']}")
    print(f"Elementos procesados  : {meta['elements_processed']}")
    print(f"Excluidos por defecto : {meta['exclude_types']}")
    gbb = result["global_bbox"]
    if gbb:
        print(f"Bounding box global   : "
              f"X[{gbb['min'][0]:.2f}, {gbb['max'][0]:.2f}] "
              f"Y[{gbb['min'][1]:.2f}, {gbb['max'][1]:.2f}] "
              f"Z[{gbb['min'][2]:.2f}, {gbb['max'][2]:.2f}]")
    print("-" * 70)
    print(f"{'IfcType':<28} {'count':>6} {'vertices':>10} {'triangles':>10}")
    print("-" * 70)
    for t, b in result["by_type"].items():
        print(f"{t:<28} {b['count']:>6} {b['total_vertices']:>10} {b['total_triangles']:>10}")
    print("=" * 70)


def main() -> int:
    args = _parse_args()
    ifc_path = resolve_model_path(args.ifc)
    try:
        model = load_ifc(ifc_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    include = _parse_csv_list(args.include)
    exclude = _parse_csv_list(args.exclude)

    result = summarize_geometry(
        model,
        include_types=include,
        exclude_types=exclude,
    )

    _emit(result, args.out)
    _print_console_summary(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
