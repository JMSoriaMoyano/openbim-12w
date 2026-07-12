"""
quality_engine.rules.d1_modelo · Reglas D1 Modelo (integridad estructural).

Checks cubiertos (E6 checklist §3.1):
    C-M-01 · FILE_SCHEMA == 'IFC4'                [yaml_python]
    C-M-02 · model.schema == FILE_SCHEMA declarado [yaml_python]

(C-M-03/04/05/06 sobre IfcProject/Site/Building/Storey se delegan a IDS.)

Capa ISO 19650-2: no gráfica.
Variantes aplicables: todas.
"""

from pathlib import Path
from typing import Any

from quality_engine.core.result import ResultadoCheck


def _read_file_schema_from_header(ifc_path: Path) -> str | None:
    """
    Lee el primer FILE_SCHEMA(('XXX')) del header STEP sin parsear todo el IFC.

    Es más fiable que confiar en model.schema porque detecta casos donde el
    fichero declara un esquema en cabecera pero ifcopenshell lo interpreta
    como otro (corrupción / reescritura inconsistente).
    """
    if not ifc_path.exists():
        return None
    # Lectura tolerante: header STEP siempre en ASCII en las primeras líneas
    with ifc_path.open("r", encoding="utf-8", errors="ignore") as fh:
        for _ in range(50):
            line = fh.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith("FILE_SCHEMA"):
                # Forma típica: FILE_SCHEMA(('IFC4'));
                start = line.find("(('")
                end = line.find("'", start + 3) if start != -1 else -1
                if start != -1 and end != -1:
                    return line[start + 3 : end]
            if line.startswith("DATA;"):
                break
    return None


def check_file_schema_ifc4(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """C-M-01 · FILE_SCHEMA del header STEP coincide con expected_schema."""
    expected = params.get("expected_schema", "IFC4")
    declared = _read_file_schema_from_header(Path(ifc_path))

    if declared is None:
        return ResultadoCheck(
            check_id="C-M-01",
            dimension="D1",
            layer="no_grafica",
            status="error",
            backend="yaml_python",
            score=None,
            evidence={"expected": expected, "declared": None, "ifc_path": str(ifc_path)},
            message="No se pudo leer FILE_SCHEMA del header STEP.",
            eir_source=eir_source,
        )

    ok = declared == expected
    return ResultadoCheck(
        check_id="C-M-01",
        dimension="D1",
        layer="no_grafica",
        status="pass" if ok else "fail",
        backend="yaml_python",
        score=1.0 if ok else 0.0,
        evidence={"expected": expected, "declared": declared, "ifc_path": str(ifc_path)},
        message=(
            f"FILE_SCHEMA={declared} coincide con esperado {expected}."
            if ok
            else f"FILE_SCHEMA declarado '{declared}' no coincide con esperado '{expected}'."
        ),
        eir_source=eir_source,
    )


def check_model_schema_coherence(
    model: Any,
    ifc_path: Path,
    params: dict[str, Any],
    eir_source: str = "",
) -> ResultadoCheck:
    """C-M-02 · model.schema (ifcopenshell) coincide con FILE_SCHEMA declarado."""
    expected = params.get("expected_schema", "IFC4")
    declared = _read_file_schema_from_header(Path(ifc_path))
    runtime = getattr(model, "schema", None)

    if declared is None or runtime is None:
        return ResultadoCheck(
            check_id="C-M-02",
            dimension="D1",
            layer="no_grafica",
            status="error",
            backend="yaml_python",
            score=None,
            evidence={
                "expected": expected,
                "declared_header": declared,
                "runtime_schema": runtime,
                "ifc_path": str(ifc_path),
            },
            message="No se pudo leer FILE_SCHEMA del header o model.schema.",
            eir_source=eir_source,
        )

    coherent = declared == runtime
    expected_ok = runtime == expected
    ok = coherent and expected_ok

    if ok:
        msg = f"Coherente: header={declared}, runtime={runtime}, esperado={expected}."
    elif not coherent:
        msg = (
            f"Incoherencia header/runtime: header={declared} vs runtime={runtime}. "
            "Posible fichero corrupto o reescrito sin actualizar cabecera."
        )
    else:
        msg = (
            f"Coherente entre header y runtime ({runtime}) pero no coincide "
            f"con esperado {expected}."
        )

    return ResultadoCheck(
        check_id="C-M-02",
        dimension="D1",
        layer="no_grafica",
        status="pass" if ok else "fail",
        backend="yaml_python",
        score=1.0 if ok else 0.0,
        evidence={
            "expected": expected,
            "declared_header": declared,
            "runtime_schema": runtime,
            "coherent_header_runtime": coherent,
            "ifc_path": str(ifc_path),
        },
        message=msg,
        eir_source=eir_source,
    )
