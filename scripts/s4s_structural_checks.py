"""
s4s_structural_checks.py · OpenBIM 12 semanas · S4·S (Sáb 06/06/2026, ejecutado 07/06)
=======================================================================================
Sesión 4 · Sábado · Cierre E4. Verificaciones estructurales del modelo IFC:
checks que operan sobre el modelo entero, NO sobre instancias o propiedades
LOIN concretas (eso es responsabilidad de s4x_ifc_lab.py).

Cobertura
---------
    C1 · check_mvd_compliance(model, expected_mvd_substr="ReferenceView")
         → audita cabecera STEP: ¿declara el MVD esperado por el EIR?
    C2 · check_bsdd_classification(model)
         → audita IfcClassificationReference: ¿Location apunta a URI bSDD válida?

Justificación EIR
-----------------
Ambas verificaciones son requisitos OBLIGATORIOS del EIR NEXUM PBSA v0.1:
  - §3.1   MVD obligatorio Reference View en cabecera STEP
  - §3.1.6 bSDD como diccionario obligatorio (URI HTTP en Location)

Hallazgo S4·L #8 reveló 3 ViewDefinitions en FZK-Haus → posible no conformidad
que esta sesión documenta de forma auditable y reproducible.

Diseño
------
- Funciones puras: aceptan model, devuelven dicts JSON-serializables.
- Sin red: la validación de URIs bSDD es solo formato (regex + dominio).
  La validación HTTP real (200 OK contra bsdd.buildingsmart.org) se hace en
  S7·L con IDS 1.0. Esto mantiene los checks reproducibles offline y en CI.
- Output homogéneo con s4x_ifc_lab.py: dict con 'query', 'compliance', 'offenders'
  cuando aplica, para que el orquestador YAML (Bloque B) los consuma uniformemente.

Uso CLI
-------
    python scripts/s4s_structural_checks.py --ifc <nombre.ifc> --check mvd \
        [--expected ReferenceView] [--out out/s4s_mvd.json]

    python scripts/s4s_structural_checks.py --ifc <nombre.ifc> --check bsdd \
        [--out out/s4s_bsdd.json]

Autor: José M. Soria (NEXUM)
Versión: 0.1 (S4·S Bloque A · verificaciones estructurales)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import ifcopenshell

from _ifc_helpers import load_ifc, resolve_model_path


# ---------------------------------------------------------------------------
# C1 · MVD compliance (header STEP)
# ---------------------------------------------------------------------------

def check_mvd_compliance(
    model: ifcopenshell.file,
    expected_mvd_substr: str = "ReferenceView",
) -> dict[str, Any]:
    """Audita el MVD declarado en la cabecera STEP del IFC.

    El EIR NEXUM PBSA v0.1 §3.1 exige que el modelo declare 'Reference View'
    (IFC4 Add2 RV o IFC4.3 RV) en FILE_DESCRIPTION.description.

    Parámetros
    ----------
    model : ifcopenshell.file
    expected_mvd_substr : str
        Substring que debe aparecer en al menos una de las ViewDefinitions
        declaradas. Por defecto 'ReferenceView'.
        Otros valores válidos según el EIR: 'CoordinationView', 'ReferenceView_V1.2'.

    Devuelve
    --------
    dict con estructura:
        query           : metadatos
        declared_views  : lista exacta de strings en FILE_DESCRIPTION.description
        expected        : substring esperado
        match_found     : bool · True si alguna entrada contiene el substring
        match_count     : nº de entradas que contienen el substring
        extra_views     : entradas que NO contienen el substring (potenciales no conformidades)
        compliance      : 'pass' | 'fail' | 'partial'
                          - pass    : match_count >= 1 y len(extra_views) == 0
                          - partial : match_count >= 1 y len(extra_views) > 0
                          - fail    : match_count == 0

    Notas
    -----
    - Sensible a mayúsculas/minúsculas en el substring por defecto.
      Se aplica comparación case-insensitive internamente para robustez.
    - 'partial' es informativo: FZK-Haus declara 3 ViewDefinitions y aunque
      una sea correcta, las otras 2 pueden generar ambigüedad para herramientas
      downstream. El EIR puede endurecerse en v0.2 a exigir 'pass' estricto.
    """
    header = model.header
    declared_raw = header.file_description.description or []
    declared = list(declared_raw)  # copia inmutable para serialización

    expected_lower = expected_mvd_substr.lower()
    matching = [v for v in declared if expected_lower in v.lower()]
    extras = [v for v in declared if expected_lower not in v.lower()]

    if len(matching) == 0:
        compliance = "fail"
    elif len(extras) == 0:
        compliance = "pass"
    else:
        compliance = "partial"

    return {
        "query": {
            "type": "mvd_compliance",
            "expected_substr": expected_mvd_substr,
        },
        "declared_views": declared,
        "expected": expected_mvd_substr,
        "match_found": len(matching) >= 1,
        "match_count": len(matching),
        "extra_views": extras,
        "compliance": compliance,
    }


# ---------------------------------------------------------------------------
# C2 · bSDD classification compliance
# ---------------------------------------------------------------------------

# Dominios aceptados como diccionarios bSDD válidos según EIR §3.1.6
# - bsdd.buildingsmart.org : registro oficial bSDD
# - identifier.buildingsmart.org : alias canónico documentado
# - gubimclass.itec.cat : URI GuBIMClass (sistema oficial catalán, pendiente
#   de migración a bSDD pero aceptado como diccionario reconocido)
_BSDD_DOMAINS_ACCEPTED: tuple[str, ...] = (
    "bsdd.buildingsmart.org",
    "identifier.buildingsmart.org",
    "gubimclass.itec.cat",
)

_URI_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


def _is_valid_bsdd_uri(location: str | None) -> tuple[bool, str]:
    """Valida formato y dominio de una URI de IfcClassificationReference.Location.

    Devuelve (es_valida, motivo).
        es_valida=True  → URI HTTP(S) con dominio en _BSDD_DOMAINS_ACCEPTED
        es_valida=False → motivo describe el incumplimiento
    """
    if location is None or str(location).strip() == "":
        return (False, "location_empty")
    loc = str(location).strip()
    if not _URI_PATTERN.match(loc):
        return (False, "not_http_uri")
    try:
        parsed = urlparse(loc)
    except ValueError:
        return (False, "uri_parse_error")
    netloc = (parsed.netloc or "").lower()
    if not netloc:
        return (False, "no_netloc")
    for accepted in _BSDD_DOMAINS_ACCEPTED:
        if netloc == accepted or netloc.endswith("." + accepted):
            return (True, "ok")
    return (False, f"domain_not_accepted:{netloc}")


def check_bsdd_classification(model: ifcopenshell.file) -> dict[str, Any]:
    """Audita IfcClassificationReference contra requisito bSDD del EIR §3.1.6.

    Recorre TODAS las instancias IfcClassificationReference del modelo y
    clasifica su atributo Location según validez como URI bSDD.

    Devuelve
    --------
    dict con estructura:
        query              : metadatos
        total_refs         : nº total de IfcClassificationReference
        bsdd_compliant     : nº con Location URI válida (dominio aceptado)
        non_compliant      : nº con Location inválida o no bSDD
        missing_location   : nº sin Location (atributo None o vacío)
        compliance_pct     : % bsdd_compliant / total_refs
        unique_locations   : dict {location_string: count} para inspección
        offenders          : lista de refs no conformes con su motivo
        accepted_domains   : lista de dominios considerados bSDD válidos

    Notas
    -----
    - No hace HTTP. Solo valida formato URI y dominio.
    - Validación HTTP real (200 OK) se hará en S7·L con IDS 1.0.
    - Si total_refs == 0, devuelve compliance_pct=0.0 (caso 'sin clasificación').
      El orquestador EIR debe interpretarlo como FAIL si la clasificación
      es obligatoria para ese hito (típicamente H2 en adelante).
    """
    refs = model.by_type("IfcClassificationReference")

    bsdd_compliant = 0
    non_compliant = 0
    missing_location = 0
    unique_locations: dict[str, int] = {}
    offenders: list[dict[str, Any]] = []

    for ref in refs:
        loc = getattr(ref, "Location", None)
        # Resolver clasificación padre para trazabilidad
        ref_source: Any = getattr(ref, "ReferencedSource", None)
        ref_source_name = getattr(ref_source, "Name", None) if ref_source else None

        # Registrar location en unique_locations (incluso si es None)
        key = loc if (loc is not None and str(loc).strip() != "") else "<missing>"
        unique_locations[key] = unique_locations.get(key, 0) + 1

        is_valid, reason = _is_valid_bsdd_uri(loc)

        if reason == "location_empty":
            missing_location += 1
            offenders.append({
                "id": ref.id(),
                "is_a": ref.is_a(),
                "identification": getattr(ref, "Identification", None),
                "name": getattr(ref, "Name", None),
                "location": loc,
                "referenced_source_name": ref_source_name,
                "reason": reason,
            })
        elif is_valid:
            bsdd_compliant += 1
        else:
            non_compliant += 1
            offenders.append({
                "id": ref.id(),
                "is_a": ref.is_a(),
                "identification": getattr(ref, "Identification", None),
                "name": getattr(ref, "Name", None),
                "location": loc,
                "referenced_source_name": ref_source_name,
                "reason": reason,
            })

    total = len(refs)
    compliance_pct = (bsdd_compliant / total * 100.0) if total else 0.0

    return {
        "query": {"type": "bsdd_classification"},
        "total_refs": total,
        "bsdd_compliant": bsdd_compliant,
        "non_compliant": non_compliant,
        "missing_location": missing_location,
        "compliance_pct": round(compliance_pct, 2),
        "unique_locations": dict(
            sorted(unique_locations.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "offenders": offenders,
        "accepted_domains": list(_BSDD_DOMAINS_ACCEPTED),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="S4·S · Verificaciones estructurales IFC (mvd, bsdd)"
    )
    parser.add_argument("--ifc", required=True, help="Ruta o nombre de fichero IFC")
    parser.add_argument(
        "--check",
        required=True,
        choices=["mvd", "bsdd"],
        help="Verificación a ejecutar",
    )
    parser.add_argument(
        "--expected",
        default="ReferenceView",
        help="Substring esperado en MVD (solo para --check mvd). Default: ReferenceView",
    )
    parser.add_argument(
        "--out",
        help="Ruta de salida JSON. Si se omite, imprime a stdout.",
    )
    return parser.parse_args()


def _emit(result: dict[str, Any], out_path: str | None) -> None:
    """Escribe el resultado a fichero o a stdout según --out."""
    payload = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if out_path:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload, encoding="utf-8")
        size_kb = p.stat().st_size / 1024
        print(f"[OK] Resultado escrito a {p} ({size_kb:.1f} KB)")
    else:
        print(payload)


def main() -> int:
    args = _parse_args()

    ifc_path = resolve_model_path(args.ifc)
    try:
        model = load_ifc(ifc_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.check == "mvd":
        result = check_mvd_compliance(model, expected_mvd_substr=args.expected)
        _emit(result, args.out)
        return 0

    if args.check == "bsdd":
        result = check_bsdd_classification(model)
        _emit(result, args.out)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
