"""
quality_engine.cli · Entrypoint del motor refactorizado.

Uso futuro (S6·X · post-implementación):
    python -m quality_engine.cli \
        --model out/AC20-FZK-Haus_authored.ifc \
        --variant diseno \
        --eir-version 0.2 \
        --ids ids/PBSA_v0.2_prototype.ids \
        --out out/

Convivencia con auditor legacy:
    scripts/s4s_audit_eir.py sigue operativo intacto (Q-D2=a).
    Este CLI crece en paralelo. La paridad funcional + sustitución
    se evaluará al cierre S7·L (cuando IDS esté estable).

Estado S6·L: stub. Implementación en S6·X.
"""

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser CLI · STUB · S6·X."""
    parser = argparse.ArgumentParser(
        prog="quality_engine",
        description="Motor de calidad BIM modular · marco S6·L v1.0",
    )
    parser.add_argument(
        "--model", type=Path, required=True, help="Ruta al modelo IFC"
    )
    parser.add_argument(
        "--variant",
        choices=["comun", "diseno", "contratista", "asbuilt"],
        required=True,
        help="Variante EIR",
    )
    parser.add_argument(
        "--eir-version", default="0.2", help="Versión EIR (default 0.2)"
    )
    parser.add_argument(
        "--ids",
        type=Path,
        default=None,
        help="Ruta al .ids XML (opcional, activa backend ids_xml)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("out/"),
        help="Directorio de salida para matrices JSON",
    )
    return parser


def main() -> int:
    """Entrypoint · STUB · S6·X.

    Nota S6·L: argparse parsea primero para que `--help` funcione (sale
    con SystemExit 0 antes de llegar a NotImplementedError). Solo lanzamos
    el NotImplementedError tras parsear, cuando hay un comando real.
    """
    parser = build_parser()
    args = parser.parse_args()
    raise NotImplementedError(
        "S6·X · cargar EIR · cargar modelo · run_audit · escribir matrices "
        f"(args parseados: variant={args.variant}, model={args.model})"
    )


if __name__ == "__main__":
    raise SystemExit(main())
