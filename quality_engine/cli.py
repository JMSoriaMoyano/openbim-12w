"""
quality_engine.cli · Entrypoint productivo del motor.

Sesión origen: stub creado en S6·L, productivizado en S9·L
(absorbe hito §3.4.1 de docs/DEUDAS_E7_E8.md).

Uso básico:
    python -m quality_engine.cli \\
        --model out/AC20-FZK-Haus_authored.ifc \\
        --variant diseno \\
        --eir-version 0.2 \\
        --out out/audit_result.json

Con filtro de backends:
    python -m quality_engine.cli \\
        --model out/AC20-FZK-Haus_authored.ifc \\
        --variant comun \\
        --backends yaml_python \\
        --out out/audit_result.json

Códigos de salida:
    0  · auditoría ejecutada, resultado escrito a --out (independiente del pct_pass)
    2  · argumentos inválidos / rutas inexistentes
    3  · error interno del motor (excepción no controlada)
    4  · gate de CI activo (--fail-under N) y pct_pass < N

El código 0 no significa "modelo válido"; significa "auditoría completada".
El gate de CI se activa explícitamente con --fail-under.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser CLI productivo."""
    parser = argparse.ArgumentParser(
        prog="quality_engine",
        description="Motor de calidad BIM · quality_engine 0.2.x · S9·L productivo",
    )
    parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Ruta al modelo IFC (obligatorio)",
    )
    parser.add_argument(
        "--variant",
        choices=["comun", "diseno", "contratista", "asbuilt"],
        required=True,
        help="Variante EIR a auditar (obligatorio)",
    )
    parser.add_argument(
        "--eir-version",
        default="0.2",
        help="Versión EIR (default: 0.2)",
    )
    parser.add_argument(
        "--eir-dir",
        type=Path,
        default=None,
        help="Directorio de EIR YAMLs (default: <repo>/eir)",
    )
    parser.add_argument(
        "--backends",
        default=None,
        help=(
            "Backends a ejecutar, separados por coma. "
            "Opciones: yaml_python, ids_xml. Default: ambos."
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Ruta de salida del JSON resultado (obligatorio)",
    )
    parser.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help=(
            "Gate de CI: si pct_pass < N, salir con código 4. "
            "Omitir para desactivar el gate."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Silenciar el resumen por stdout",
    )
    return parser


def _validate_paths(args: argparse.Namespace) -> None:
    """Valida rutas críticas antes de invocar el motor."""
    if not args.model.exists():
        raise FileNotFoundError(f"Modelo IFC no existe: {args.model}")
    if not args.model.is_file():
        raise ValueError(f"--model debe ser un fichero: {args.model}")
    if args.eir_dir is not None and not args.eir_dir.is_dir():
        raise NotADirectoryError(f"--eir-dir no es un directorio: {args.eir_dir}")
    args.out.parent.mkdir(parents=True, exist_ok=True)


def _parse_backends(raw: str | None) -> list[str] | None:
    """Convierte 'yaml_python,ids_xml' → ['yaml_python', 'ids_xml']. None → None."""
    if raw is None:
        return None
    items = [b.strip() for b in raw.split(",") if b.strip()]
    valid = {"yaml_python", "ids_xml"}
    for b in items:
        if b not in valid:
            raise ValueError(
                f"Backend desconocido: {b!r}. Válidos: {sorted(valid)}"
            )
    return items


def _write_result(result: dict[str, Any], out_path: Path) -> None:
    """Serializa el resultado a JSON UTF-8."""
    payload = {
        "audit_meta": result["audit_meta"],
        "summary": result["summary"],
        "results": result["results"],
    }
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


def _print_summary(result: dict[str, Any]) -> None:
    """Imprime resumen legible por stdout."""
    meta = result["audit_meta"]
    s = result["summary"]
    print("=" * 60)
    print(f"quality_engine · auditoría completada")
    print("=" * 60)
    print(f"  motor      : {meta['engine_version']}")
    print(f"  variante   : {meta['eir_variant']} v{meta['eir_version']}")
    print(f"  modelo     : {Path(meta['model_path']).name}")
    print(f"  backends   : {', '.join(meta['backends_used'])}")
    print(f"  timestamp  : {meta['timestamp_utc']}")
    print("-" * 60)
    print(f"  total      : {s['total']}")
    print(f"  applicable : {s['applicable']}")
    print(f"  pass       : {s['pass']}")
    print(f"  fail       : {s['fail']}")
    print(f"  partial    : {s.get('partial', 0)}")
    print(f"  n/a        : {s.get('not_applicable', 0)}")
    print(f"  error      : {s.get('error', 0)}")
    print(f"  pct_pass   : {s['pct_pass']}%")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    """Entrypoint productivo del motor."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Validación de argumentos ANTES de importar el motor (arranque rápido)
    try:
        _validate_paths(args)
        backends = _parse_backends(args.backends)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"[error argumentos] {exc}", file=sys.stderr)
        return 2

    # Import diferido: sólo cargamos el motor si los argumentos son válidos.
    try:
        from quality_engine.core.runner import run_audit
    except Exception as exc:
        print(f"[error import motor] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    # Ejecución
    try:
        result = run_audit(
            model_path=args.model,
            eir_variant=args.variant,
            eir_version=args.eir_version,
            eir_dir=args.eir_dir,
            backends=backends,
        )
    except Exception as exc:
        print(f"[error motor] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    # Persistencia
    try:
        _write_result(result, args.out)
    except Exception as exc:
        print(f"[error escritura] {exc}", file=sys.stderr)
        return 3

    if not args.quiet:
        _print_summary(result)

    # Gate de CI
    if args.fail_under is not None:
        pct = result["summary"]["pct_pass"]
        if pct < args.fail_under:
            print(
                f"[gate CI] pct_pass={pct}% < fail-under={args.fail_under}%",
                file=sys.stderr,
            )
            return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
