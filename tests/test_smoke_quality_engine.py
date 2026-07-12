"""
tests/test_smoke_quality_engine.py

Test smoke del motor quality_engine 0.2.x. Absorbe hito §3.4.3
de docs/DEUDAS_E7_E8.md.

Contrato blindado (blinda regresiones futuras):
    Dado FZK-Haus authored (SHA-256 fijo) + PBSA v0.2 diseño, la
    auditoría debe producir EXACTAMENTE:
        - 35 checks totales
        - 15 pass
        - 17 fail
        - 1 partial
        - 2 not_applicable
        - pct_pass == 45.45

Cualquier cambio en el motor, las reglas o el IDS que altere estos
números rompe el test. Es intencional: si cambia algo, hay que
justificarlo actualizando este contrato.

Uso local:
    pytest tests/ -v
Uso en CI:
    ver .github/workflows/ifc-ci.yml
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL = REPO_ROOT / "out" / "AC20-FZK-Haus_authored.ifc"
IDS = REPO_ROOT / "ids" / "PBSA_v0.2_prototype.ids"

# Contrato canónico establecido en S6·X, verificado en S9·L
EXPECTED_TOTAL = 35
EXPECTED_PASS = 15
EXPECTED_FAIL = 17
EXPECTED_PARTIAL = 1
EXPECTED_NA = 2
EXPECTED_PCT_PASS = 45.45

# NOTA S9·L: NO se compara SHA-256 de bytes del fichero.
# Los .ifc son texto STEP y sufren conversión CRLF/LF entre Linux y Windows.
# Se validan propiedades semánticas del modelo (schema, entidades, jerarquía).
EXPECTED_SCHEMA = "IFC4"
EXPECTED_MIN_ENTITIES = 500  # FZK-Haus authored tiene ~600-800 según autoría
EXPECTED_PROJECT_COUNT = 1
EXPECTED_BUILDING_COUNT = 1
EXPECTED_STOREY_MIN = 1


def test_model_exists():
    """FZK-Haus authored debe existir en out/."""
    assert MODEL.exists(), f"Modelo no encontrado: {MODEL}"


def test_ids_exists():
    """IDS v0.2 debe existir en ids/."""
    assert IDS.exists(), f"IDS no encontrado: {IDS}"


def test_ids_valid_against_schema():
    """El IDS v0.2 debe validar contra el schema oficial IDS 1.0."""
    from ifctester import ids as ifctester_ids

    spec = ifctester_ids.open(str(IDS), validate=True)
    assert spec is not None
    # 7 specifications esperadas en v0.2
    assert len(spec.specifications) == 7, (
        f"IDS v0.2 debe tener 7 specs, encontradas: "
        f"{len(spec.specifications)}"
    )


def test_engine_runs_diseno_variant():
    """El motor ejecuta la variante diseño end-to-end sin excepciones."""
    from quality_engine.core.runner import run_audit

    result = run_audit(
        model_path=MODEL,
        eir_variant="diseno",
        eir_version="0.2",
    )
    assert "audit_meta" in result
    assert "summary" in result
    assert "results" in result


def test_engine_produces_expected_summary():
    """Contrato canónico: los conteos deben ser exactos."""
    from quality_engine.core.runner import run_audit

    result = run_audit(
        model_path=MODEL,
        eir_variant="diseno",
        eir_version="0.2",
    )
    s = result["summary"]

    assert s["total"] == EXPECTED_TOTAL, (
        f"total: esperado {EXPECTED_TOTAL}, obtenido {s['total']}"
    )
    assert s["pass"] == EXPECTED_PASS, (
        f"pass: esperado {EXPECTED_PASS}, obtenido {s['pass']}"
    )
    assert s["fail"] == EXPECTED_FAIL, (
        f"fail: esperado {EXPECTED_FAIL}, obtenido {s['fail']}"
    )
    assert s.get("partial", 0) == EXPECTED_PARTIAL
    assert s.get("not_applicable", 0) == EXPECTED_NA
    assert s["pct_pass"] == EXPECTED_PCT_PASS, (
        f"pct_pass: esperado {EXPECTED_PCT_PASS}, obtenido {s['pct_pass']}"
    )


def test_model_semantic_stability():
    """Validar propiedades semánticas del modelo authored (schema + jerarquía).

    Reemplaza al antiguo test SHA-256 (eliminado en S9·L). El hash de bytes
    diverge entre Linux/Windows por conversión CRLF/LF y no es fiable como
    contrato. Aquí validamos lo que realmente importa: el modelo abre bien,
    tiene el schema esperado y la jerarquía IFC mínima está intacta.
    """
    import ifcopenshell

    model = ifcopenshell.open(str(MODEL))

    assert model.schema == EXPECTED_SCHEMA, (
        f"Schema: esperado {EXPECTED_SCHEMA}, obtenido {model.schema}"
    )

    total_entities = len(list(model))
    assert total_entities >= EXPECTED_MIN_ENTITIES, (
        f"Modelo demasiado pequeño: {total_entities} entidades "
        f"(mínimo esperado {EXPECTED_MIN_ENTITIES})"
    )

    projects = model.by_type("IfcProject")
    assert len(projects) == EXPECTED_PROJECT_COUNT, (
        f"IfcProject: esperado {EXPECTED_PROJECT_COUNT}, "
        f"encontrado {len(projects)}"
    )

    buildings = model.by_type("IfcBuilding")
    assert len(buildings) == EXPECTED_BUILDING_COUNT, (
        f"IfcBuilding: esperado {EXPECTED_BUILDING_COUNT}, "
        f"encontrado {len(buildings)}"
    )

    storeys = model.by_type("IfcBuildingStorey")
    assert len(storeys) >= EXPECTED_STOREY_MIN, (
        f"IfcBuildingStorey: mínimo {EXPECTED_STOREY_MIN}, "
        f"encontrado {len(storeys)}"
    )


def test_cli_help_ok():
    """El CLI responde a --help con código 0."""
    proc = subprocess.run(
        [sys.executable, "-m", "quality_engine.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "quality_engine" in proc.stdout


def test_cli_exit_code_2_on_missing_model(tmp_path):
    """Modelo inexistente → exit 2."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "quality_engine.cli",
            "--model",
            str(tmp_path / "no_existe.ifc"),
            "--variant",
            "diseno",
            "--out",
            str(tmp_path / "out.json"),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2


def test_cli_gate_fires_on_low_pct(tmp_path):
    """Con --fail-under=95 sobre variante diseño (pct=45.45), exit=4."""
    out_json = tmp_path / "out.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "quality_engine.cli",
            "--model",
            str(MODEL),
            "--variant",
            "diseno",
            "--fail-under",
            "95",
            "--out",
            str(out_json),
            "--quiet",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 4
    # El JSON se escribe aunque el gate falle (auditoría completó)
    assert out_json.exists()
