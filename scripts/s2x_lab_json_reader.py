"""S2·X · Mini-lab · Lectura comentada del revit_ifc_export_config.json

Comprueba 12 invariantes críticas del setup IFC NEXUM antes de cualquier
exportación desde Revit. Se ejecuta en seco (sin Revit, sin IfcOpenShell).

Uso:
    python scripts/s2x_lab_json_reader.py
    python scripts/s2x_lab_json_reader.py --config configs/otro.json

Salida:
    Stdout legible + exit code 0 (OK) o 1 (algún FAIL).

Origen pedagógico: Sesión S2·X (20/05/2026).
Evolución prevista: S4·L lo formaliza como 02_validate_revit_config.py con
argparse rico, logging estructurado y salida JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_CONFIG = Path("configs/revit_ifc_export_config.json")


def load_config(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"FATAL · No existe el fichero: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"FATAL · JSON inválido en {path}: {exc}")


def run_checks(cfg: dict) -> dict[str, bool]:
    """12 invariantes críticas del setup NEXUM IFC4 Reference View."""
    return {
        "Schema IFC4 Reference View (IFCVersion=21)": cfg.get("IFCVersion") == 21,
        "Fichero .ifc plano (IFCFileType=0)": cfg.get("IFCFileType") == 0,
        "FileVersionDescription coherente con Reference View":
            "Reference View" in cfg.get("FileVersionDescription", ""),
        "GUIDs estables (StoreIFCGUID=true)": cfg.get("StoreIFCGUID") is True,
        "Common Psets activos": cfg.get("ExportIFCCommonPropertySets") is True,
        "Internal Revit Psets desactivados": cfg.get("ExportInternalRevitPropertySets") is False,
        "UserDefined Psets activos": cfg.get("ExportUserDefinedPsets") is True,
        "Base Quantities activos (Qto_*)": cfg.get("ExportBaseQuantities") is True,
        "Solo elementos visibles de la vista": cfg.get("VisibleElementsOfCurrentView") is True,
        "Sin Linked Files embebidos": cfg.get("ExportLinkedFiles") is False,
        "Shared Coordinates (SitePlacement=0)": cfg.get("SitePlacement") == 0,
        "Site elevation incluido": cfg.get("IncludeSiteElevation") is True,
    }


def print_report(cfg: dict, checks: dict[str, bool]) -> int:
    name = cfg.get("Name", "(sin nombre)")
    meta = cfg.get("_NEXUM_metadata", {}) or {}
    print("=" * 70)
    print(f"Setup    : {name}")
    print(f"Versión  : {meta.get('version', '?')} · Fecha: {meta.get('date', '?')}")
    print(f"Autor    : {meta.get('author', '?')}")
    print(f"BEP ref  : {meta.get('BEP_reference', '?')}")
    print(f"EIR ref  : {meta.get('EIR_reference', '?')}")
    print(f"bSDD ref : {meta.get('bsdd_reference', '?')}")
    print("=" * 70)
    width = max(len(d) for d in checks)
    for desc, ok in checks.items():
        mark = " OK " if ok else "FAIL"
        print(f"  [{mark}] {desc.ljust(width)}")
    print("=" * 70)
    failed = [d for d, ok in checks.items() if not ok]
    if failed:
        print(f"RESULTADO: {len(failed)} FAIL · {len(checks) - len(failed)} OK")
        print("\nFallos:")
        for d in failed:
            print(f"  - {d}")
        return 1
    print(f"RESULTADO: TODAS OK ({len(checks)}/{len(checks)})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG,
        help=f"Ruta al JSON (por defecto: {DEFAULT_CONFIG})",
    )
    args = parser.parse_args()
    cfg = load_config(args.config)
    checks = run_checks(cfg)
    return print_report(cfg, checks)


if __name__ == "__main__":
    sys.exit(main())
