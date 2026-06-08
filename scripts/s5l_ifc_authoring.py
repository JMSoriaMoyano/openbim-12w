"""
s5l_ifc_authoring.py · OpenBIM 12 semanas · S5·L Bloque D
==========================================================
Primer script de **autoría real** sobre modelos IFC.

Sustituye el ciclo de solo-lectura S3/S4 por mutaciones controladas según el
contrato vinculante definido en `docs/S5L_reglas_autoria.md` (v1.0).

Operaciones implementadas en este script
----------------------------------------

OP1 · set_pset_property
    Pobla `Pset_DoorCommon.FireRating = "EI 30"` en las IfcDoor del modelo
    fuente que carezcan de dicha propiedad (auto-detección).
    Justificación EIR: §4.2.ARQ · CTE DB-SI (puertas en sector residencial).
    Whitelist: §3.1 (IfcDoor · Pset_DoorCommon · FireRating).

OP2 · create_basic_wall
    Crea un IfcWall nuevo con representación geométrica básica
    (IfcExtrudedAreaSolid sobre IfcRectangleProfileDef), ubicado en la
    planta baja del proyecto.
    Whitelist: §3.2 (crear IfcWall con perfil rectangular extruido).

Principios rectores (recordatorio explícito · S5L_reglas_autoria.md §2)
-----------------------------------------------------------------------
- **P1** No mutar el modelo original. Toda escritura va a `out/<base>_authored.ifc`.
- **P2** Trazabilidad obligatoria vía `out/<base>_authored_diff.json` (§4.1).
- **P3** Una operación = una función con docstring que cite §EIR aplicable.
- **P4** Validación post-autoría (re-auditoría) se ejecuta en Bloque E, no aquí.
- **P5** Whitelist explícita (§3) · cualquier desviación rompe el contrato.

Decisiones de diseño (S5·L Bloque D · Q1=A, Q2=A)
-------------------------------------------------
- Q1 (FireRating): auto-detectar puertas sin `FireRating` y aplicar valor
  uniforme `"EI 30"` (estándar CTE DB-SI sector residencial). Si en el modelo
  fuente FZK-Haus se detectan 3 puertas sin valor, se procesarán las 3.
- Q2 (Geometría muro nuevo): IfcWall de 3.0m × 0.2m × 2.7m en coordenadas
  globales (10.0, 5.0, 0.0), eje X, contenedor planta baja (IfcBuildingStorey
  de menor elevación).

Autor: José M. Soria · NEXUM Developments
Versión: 0.1 · S5·L Bloque D · Lun 08/06/2026
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element

# Helper común del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ifc_helpers import load_ifc, resolve_model_path  # noqa: E402


# ---------------------------------------------------------------------------
# Constantes de autoría (whitelist v0.1)
# ---------------------------------------------------------------------------

SESSION_TAG = "S5·L"

# OP1 · FireRating en IfcDoor
DOOR_FIRE_RATING_VALUE = "EI 30"
DOOR_FIRE_RATING_PSET = "Pset_DoorCommon"
DOOR_FIRE_RATING_PROP = "FireRating"
DOOR_FIRE_RATING_EIR_REF = "§4.2.ARQ"
DOOR_FIRE_RATING_RATIONALE = (
    "Pobla FireRating ausente conforme a CTE DB-SI (sector residencial). "
    "Corrige hallazgo H3.DOOR.FireRating identificado en E4 "
    "(s4s_compliance_matrix_baseline.json)."
)

# OP2 · IfcWall nuevo (Q2 = Opción A)
NEW_WALL_NAME = "S5L-AUTH-WALL-001"
NEW_WALL_LENGTH_M = 3.0       # eje X
NEW_WALL_WIDTH_M = 0.2        # espesor (eje Y)
NEW_WALL_HEIGHT_M = 2.7       # altura (eje Z)
NEW_WALL_LOCATION_M = (10.0, 5.0, 0.0)  # global (x, y, z)
NEW_WALL_EIR_REF = "§3.2 whitelist geometría"
NEW_WALL_RATIONALE = (
    "Muro de prueba creado para validar pipeline de autoría geométrica. "
    "Cumple whitelist §3.2 (IfcWall con IfcExtrudedAreaSolid sobre "
    "IfcRectangleProfileDef)."
)


# ---------------------------------------------------------------------------
# Modelo de diff (estructura §4.1 de S5L_reglas_autoria.md)
# ---------------------------------------------------------------------------

@dataclass
class AuthorDiff:
    """Acumulador de operaciones de autoría · serializa a JSON §4.1."""

    source_ifc: str
    target_ifc: str
    session: str = SESSION_TAG
    authored_at: str = field(
        default_factory=lambda: dt.datetime.now().astimezone().isoformat(timespec="seconds")
    )
    operations: list[dict[str, Any]] = field(default_factory=list)

    def add_op(self, op: dict[str, Any]) -> None:
        op_id = f"OP-{len(self.operations) + 1:03d}"
        op_with_id = {"op_id": op_id, **op}
        self.operations.append(op_with_id)

    def to_dict(self) -> dict[str, Any]:
        ops_by_type: dict[str, int] = {}
        for op in self.operations:
            t = op.get("type", "unknown")
            ops_by_type[t] = ops_by_type.get(t, 0) + 1
        return {
            "source_ifc": self.source_ifc,
            "target_ifc": self.target_ifc,
            "session": self.session,
            "authored_at": self.authored_at,
            "operations": self.operations,
            "summary": {
                "ops_total": len(self.operations),
                "ops_by_type": ops_by_type,
            },
        }


# ---------------------------------------------------------------------------
# F1 · Cargar copia (P1 · no mutar original)
# ---------------------------------------------------------------------------

def _load_source_copy(path: str | Path) -> tuple[ifcopenshell.file, Path]:
    """Carga el IFC fuente en memoria sin mutar el fichero en disco (P1).

    ifcopenshell.open() devuelve un objeto en memoria; cualquier mutación
    posterior solo afecta a esa instancia. El fichero original solo se
    sobrescribiría si llamáramos `model.write(<misma_ruta>)`. Como nosotros
    escribiremos a `out/<base>_authored.ifc`, el original queda intacto.

    Returns
    -------
    (model, resolved_path)
        model : objeto ifcopenshell.file (mutable en memoria)
        resolved_path : Path absoluto del fichero fuente
    """
    src = resolve_model_path(path)
    model = load_ifc(src)
    return model, src


# ---------------------------------------------------------------------------
# F2 · set_pset_property (whitelist §3.1)
# ---------------------------------------------------------------------------

def set_pset_property(
    model: ifcopenshell.file,
    element: Any,
    pset_name: str,
    prop_name: str,
    value: Any,
    diff: AuthorDiff,
    eir_ref: str = "",
    rationale: str = "",
) -> bool:
    """Poblar/corregir una propiedad de Pset en un elemento IFC (P3).

    Justificación EIR: variable según invocación (§4.2.ARQ típico).
    Whitelist: §3.1 de S5L_reglas_autoria.md.

    Parameters
    ----------
    model : ifcopenshell.file (en memoria, mutable)
    element : entidad IFC concreta (ej. IfcDoor)
    pset_name : nombre del Pset (ej. "Pset_DoorCommon")
    prop_name : nombre de la propiedad (ej. "FireRating")
    value : valor a asignar
    diff : acumulador AuthorDiff (mutación in-place)
    eir_ref : cita §EIR que justifica la operación
    rationale : explicación breve para el diff JSON

    Returns
    -------
    bool : True si se aplicó la mutación, False si no era necesaria
           (valor previo idéntico al solicitado).
    """
    # 1. Snapshot valor antes
    psets_before = ifcopenshell.util.element.get_psets(element)
    value_before = psets_before.get(pset_name, {}).get(prop_name, None)

    # Regla §3.1: no sobrescribir valor válido sin justificación. Si ya existe
    # y coincide, no-op silencioso. Si existe y difiere, también respetamos
    # el valor existente (en este script solo poblamos ausentes).
    if value_before is not None:
        return False

    # 2. Mutar via ifcopenshell.api
    # En 0.8.x la API moderna usa "pset.add_pset" + "pset.edit_pset". Probamos
    # primero la API moderna; si falla por versión, caemos a la legacy.
    try:
        # ifcopenshell.api.run() es el dispatcher canónico
        pset = ifcopenshell.api.run(
            "pset.add_pset", model, product=element, name=pset_name
        )
        ifcopenshell.api.run(
            "pset.edit_pset", model, pset=pset, properties={prop_name: value}
        )
    except Exception as exc:
        raise RuntimeError(
            f"Fallo al poblar {pset_name}.{prop_name} en {element.is_a()} "
            f"#{element.id()}: {exc}"
        ) from exc

    # 3. Registrar en diff
    diff.add_op({
        "type": "set_pset_property",
        "element": {
            "id": element.id(),
            "global_id": getattr(element, "GlobalId", None),
            "type": element.is_a(),
            "name": getattr(element, "Name", None),
        },
        "pset": pset_name,
        "property": prop_name,
        "value_before": value_before,
        "value_after": value,
        "eir_ref": eir_ref,
        "rationale": rationale,
    })
    return True


# ---------------------------------------------------------------------------
# F3 · create_basic_wall (whitelist §3.2)
# ---------------------------------------------------------------------------

def create_basic_wall(
    model: ifcopenshell.file,
    name: str,
    length_m: float,
    width_m: float,
    height_m: float,
    location_m: tuple[float, float, float],
    container: Any,
    diff: AuthorDiff,
    eir_ref: str = "",
    rationale: str = "",
) -> Any:
    """Crear un IfcWall nuevo con geometría básica (P3).

    Whitelist §3.2: IfcWall con IfcExtrudedAreaSolid sobre IfcRectangleProfileDef,
    contenido en un IfcBuildingStorey existente.

    El muro se crea con eje longitudinal en X, espesor en Y, altura en Z.
    No se crea IfcOpeningElement asociado (no se requiere puerta/ventana).

    Parameters
    ----------
    model : ifcopenshell.file (mutable)
    name : nombre del muro (atributo Name)
    length_m, width_m, height_m : dimensiones en metros (sistema proyecto)
    location_m : coords globales (x, y, z) del origen local del muro
    container : IfcBuildingStorey donde se aloja (relación contención)
    diff : acumulador AuthorDiff
    eir_ref : cita §EIR/whitelist
    rationale : justificación breve

    Returns
    -------
    IfcWall recién creado.
    """
    # Antes de mutar, capturamos el conteo de muros para diff
    walls_before = len(model.by_type("IfcWall"))

    try:
        # 1. Crear la entidad IfcWall con relación de contención al storey
        wall = ifcopenshell.api.run(
            "root.create_entity",
            model,
            ifc_class="IfcWall",
            name=name,
        )

        # 2. Asignar contención espacial al IfcBuildingStorey
        ifcopenshell.api.run(
            "spatial.assign_container",
            model,
            products=[wall],
            relating_structure=container,
        )

        # 3. Construir geometría: IfcExtrudedAreaSolid sobre IfcRectangleProfileDef
        # Contexto de representación 3D del modelo
        contexts = [c for c in model.by_type("IfcGeometricRepresentationContext")
                    if c.ContextType == "Model" and not c.is_a("IfcGeometricRepresentationSubContext")]
        if not contexts:
            raise RuntimeError("No se encontró IfcGeometricRepresentationContext 'Model'.")
        body_context = None
        for sub in model.by_type("IfcGeometricRepresentationSubContext"):
            if sub.ContextIdentifier == "Body" and sub.ContextType == "Model":
                body_context = sub
                break
        if body_context is None:
            body_context = contexts[0]

        # Perfil rectangular (length × width) centrado en el origen del muro
        profile = model.create_entity(
            "IfcRectangleProfileDef",
            ProfileType="AREA",
            ProfileName=None,
            Position=model.create_entity(
                "IfcAxis2Placement2D",
                Location=model.create_entity("IfcCartesianPoint", Coordinates=(length_m / 2.0, width_m / 2.0)),
                RefDirection=model.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0)),
            ),
            XDim=length_m,
            YDim=width_m,
        )

        # Dirección de extrusión: vertical (eje Z)
        extrude_dir = model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))

        # Placement local de la extrusión (origen del perfil)
        extrude_placement = model.create_entity(
            "IfcAxis2Placement3D",
            Location=model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            Axis=model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            RefDirection=model.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0)),
        )

        # Sólido extruido
        solid = model.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=profile,
            Position=extrude_placement,
            ExtrudedDirection=extrude_dir,
            Depth=height_m,
        )

        # Representación del muro (cuerpo)
        body_rep = model.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body_context,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[solid],
        )

        product_rep = model.create_entity(
            "IfcProductDefinitionShape",
            Representations=[body_rep],
        )
        wall.Representation = product_rep

        # 4. ObjectPlacement global (10.0, 5.0, 0.0) relativo al storey
        # El storey ya tiene su propio placement; encadenamos relativo.
        storey_placement = container.ObjectPlacement
        wall_local_placement = model.create_entity(
            "IfcAxis2Placement3D",
            Location=model.create_entity("IfcCartesianPoint", Coordinates=location_m),
            Axis=model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            RefDirection=model.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0)),
        )
        wall.ObjectPlacement = model.create_entity(
            "IfcLocalPlacement",
            PlacementRelTo=storey_placement,
            RelativePlacement=wall_local_placement,
        )

    except Exception as exc:
        raise RuntimeError(f"Fallo al crear IfcWall '{name}': {exc}") from exc

    walls_after = len(model.by_type("IfcWall"))

    # Registrar en diff
    diff.add_op({
        "type": "create_element",
        "element": {
            "id": wall.id(),
            "global_id": getattr(wall, "GlobalId", None),
            "type": wall.is_a(),
            "name": name,
        },
        "geometry": {
            "primitive": "IfcExtrudedAreaSolid",
            "profile": "IfcRectangleProfileDef",
            "length_m": length_m,
            "width_m": width_m,
            "height_m": height_m,
            "location_m": list(location_m),
            "axis": "X",
        },
        "container": {
            "id": container.id(),
            "global_id": getattr(container, "GlobalId", None),
            "type": container.is_a(),
            "name": getattr(container, "Name", None),
        },
        "counts": {
            "walls_before": walls_before,
            "walls_after": walls_after,
        },
        "eir_ref": eir_ref,
        "rationale": rationale,
    })
    return wall


# ---------------------------------------------------------------------------
# F4 · write_authored_model
# ---------------------------------------------------------------------------

def write_authored_model(
    model: ifcopenshell.file,
    target_path: str | Path,
    diff: AuthorDiff,
    diff_path: str | Path,
) -> tuple[Path, Path]:
    """Escribe IFC autoriado y diff JSON al disco (P1, P2).

    No realiza re-auditoría (eso es Bloque E).
    Returns rutas absolutas finales.
    """
    target = Path(target_path).resolve()
    diff_target = Path(diff_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    diff_target.parent.mkdir(parents=True, exist_ok=True)

    # Escribir IFC mutado
    model.write(str(target))

    # Escribir diff JSON
    with diff_target.open("w", encoding="utf-8") as f:
        json.dump(diff.to_dict(), f, indent=2, ensure_ascii=False)

    return target, diff_target


# ---------------------------------------------------------------------------
# Helpers de selección
# ---------------------------------------------------------------------------

def _find_doors_without_fire_rating(model: ifcopenshell.file) -> list[Any]:
    """Devuelve IfcDoor sin Pset_DoorCommon.FireRating (auto-detección · Q1=A)."""
    result = []
    for door in model.by_type("IfcDoor"):
        psets = ifcopenshell.util.element.get_psets(door)
        fr = psets.get(DOOR_FIRE_RATING_PSET, {}).get(DOOR_FIRE_RATING_PROP, None)
        if fr is None:
            result.append(door)
    return result


def _find_ground_storey(model: ifcopenshell.file) -> Any:
    """Devuelve el IfcBuildingStorey de menor elevación (planta baja)."""
    storeys = list(model.by_type("IfcBuildingStorey"))
    if not storeys:
        raise RuntimeError("Modelo sin IfcBuildingStorey · no se puede anclar muro nuevo.")
    storeys.sort(key=lambda s: getattr(s, "Elevation", 0.0) or 0.0)
    return storeys[0]


# ---------------------------------------------------------------------------
# CLI orchestrator
# ---------------------------------------------------------------------------

def run_authoring(
    source: str,
    target_ifc: str | None = None,
    target_diff: str | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    """Orquestador completo · OP1 (FireRating × N puertas) + OP2 (muro nuevo).

    Parameters
    ----------
    source : nombre o ruta del IFC fuente (ej. 'AC20-FZK-Haus.ifc').
    target_ifc : ruta destino IFC (default: out/<base>_authored.ifc en repo).
    target_diff : ruta destino diff JSON (default: out/<base>_authored_diff.json).
    verbose : log a stdout.

    Returns
    -------
    Resumen dict (paths + operaciones aplicadas).
    """
    # 1. Cargar copia (P1)
    model, src_path = _load_source_copy(source)
    base = src_path.stem

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "out"
    if target_ifc is None:
        target_ifc = str(out_dir / f"{base}_authored.ifc")
    if target_diff is None:
        target_diff = str(out_dir / f"{base}_authored_diff.json")

    diff = AuthorDiff(
        source_ifc=str(src_path),
        target_ifc=str(Path(target_ifc).resolve()),
    )

    if verbose:
        print(f"[info] Fuente: {src_path}")
        print(f"[info] Schema: {model.schema}")
        print(f"[info] Destino IFC: {target_ifc}")
        print(f"[info] Destino diff: {target_diff}")

    # 2. OP1 · FireRating en puertas sin valor (Q1 = A)
    doors_pending = _find_doors_without_fire_rating(model)
    if verbose:
        print(f"[OP1] IfcDoor sin FireRating detectadas: {len(doors_pending)}")

    op1_applied = 0
    for door in doors_pending:
        ok = set_pset_property(
            model=model,
            element=door,
            pset_name=DOOR_FIRE_RATING_PSET,
            prop_name=DOOR_FIRE_RATING_PROP,
            value=DOOR_FIRE_RATING_VALUE,
            diff=diff,
            eir_ref=DOOR_FIRE_RATING_EIR_REF,
            rationale=DOOR_FIRE_RATING_RATIONALE,
        )
        if ok:
            op1_applied += 1
            if verbose:
                print(f"  [+] {door.is_a()} #{door.id()} · {DOOR_FIRE_RATING_PROP} = {DOOR_FIRE_RATING_VALUE!r}")

    # 3. OP2 · Crear IfcWall (Q2 = A)
    ground = _find_ground_storey(model)
    if verbose:
        print(f"[OP2] Storey contenedor: {ground.is_a()} #{ground.id()} · Name={getattr(ground, 'Name', None)!r}")

    new_wall = create_basic_wall(
        model=model,
        name=NEW_WALL_NAME,
        length_m=NEW_WALL_LENGTH_M,
        width_m=NEW_WALL_WIDTH_M,
        height_m=NEW_WALL_HEIGHT_M,
        location_m=NEW_WALL_LOCATION_M,
        container=ground,
        diff=diff,
        eir_ref=NEW_WALL_EIR_REF,
        rationale=NEW_WALL_RATIONALE,
    )
    if verbose:
        print(f"  [+] IfcWall '{NEW_WALL_NAME}' creado · #{new_wall.id()} · GlobalId={new_wall.GlobalId}")

    # 4. Escribir outputs (P1 garantizado: target ≠ source)
    if Path(target_ifc).resolve() == src_path.resolve():
        raise RuntimeError("Violación P1: target_ifc coincide con source. Abortado.")

    written_ifc, written_diff = write_authored_model(
        model=model,
        target_path=target_ifc,
        diff=diff,
        diff_path=target_diff,
    )

    summary = {
        "source": str(src_path),
        "schema": model.schema,
        "target_ifc": str(written_ifc),
        "target_diff": str(written_diff),
        "ops": {
            "op1_set_fire_rating": op1_applied,
            "op2_create_wall": 1,
        },
        "total_operations": len(diff.operations),
    }

    if verbose:
        print(f"[done] IFC escrito: {written_ifc} ({written_ifc.stat().st_size:,} bytes)")
        print(f"[done] Diff escrito: {written_diff} ({written_diff.stat().st_size:,} bytes)")
        print(f"[done] Operaciones registradas: {summary['total_operations']}")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="S5·L Bloque D · Autoría IFC controlada (whitelist v0.1)",
    )
    parser.add_argument(
        "--source",
        default="AC20-FZK-Haus.ifc",
        help="Nombre o ruta del IFC fuente (default: AC20-FZK-Haus.ifc)",
    )
    parser.add_argument(
        "--target-ifc",
        default=None,
        help="Ruta destino IFC (default: out/<base>_authored.ifc)",
    )
    parser.add_argument(
        "--target-diff",
        default=None,
        help="Ruta destino diff JSON (default: out/<base>_authored_diff.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Log detallado a stdout",
    )
    args = parser.parse_args()

    try:
        summary = run_authoring(
            source=args.source,
            target_ifc=args.target_ifc,
            target_diff=args.target_diff,
            verbose=args.verbose,
        )
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    if not args.verbose:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
