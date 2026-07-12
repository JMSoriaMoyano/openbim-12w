"""
scripts/s6x_generate_e6_outputs.py · Bloque E del S6·X.

Ejecuta el motor `quality_engine` contra AC20-FZK-Haus_authored.ifc para las
4 variantes EIR (comun/diseno/contratista/asbuilt) y genera:

    1. out/AC20-FZK-Haus_compliance_post_<variant>_v2.json     (matriz)
    2. docs/audit_report_<variant>.md                          (reporte)

Uso:
    python scripts/s6x_generate_e6_outputs.py

Convenciones S6·X:
    - El sufijo _v2 distingue las matrices del motor nuevo de las del
      auditor legacy s4s_audit_eir.py (que viven sin sufijo).
    - Los reports MD son exhaustivos: evidence completa, offenders sample,
      recomendaciones, hallazgos clave. Base para E6_auditoria_calidad_fzk_haus.md.
    - Se incluye solo backend yaml_python para variantes que no son `diseno`
      y ambos backends para `diseno`. (Decisión: IDS aplica a todas porque
      las 7 specs son universales; lo dejamos siempre activo.)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Asegurar que el paquete quality_engine es importable desde scripts/
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from quality_engine.core.runner import run_audit


MODEL_PATH = REPO_ROOT / "out" / "AC20-FZK-Haus_authored.ifc"
OUT_DIR = REPO_ROOT / "out"
DOCS_DIR = REPO_ROOT / "docs"

VARIANTS = ("comun", "diseno", "contratista", "asbuilt")
EIR_VERSION = "0.2"


# ---------------------------------------------------------------------------
# Helpers de formato Markdown
# ---------------------------------------------------------------------------

STATUS_BADGE = {
    "pass": "✓ PASS",
    "fail": "✗ FAIL",
    "partial": "◐ PARTIAL",
    "not_applicable": "— N/A",
    "error": "! ERROR",
}


def _fmt_score(s: float | None) -> str:
    if s is None:
        return "—"
    return f"{s:.2%}"


def _fmt_threshold(t: float | None) -> str:
    if t is None:
        return "—"
    return f"{t:.0%}"


def _sanitize_evidence(ev: dict[str, Any], max_items: int = 5) -> dict[str, Any]:
    """Trunca evidence largo para JSON legible."""
    if not isinstance(ev, dict):
        return ev
    out: dict[str, Any] = {}
    for k, v in ev.items():
        if isinstance(v, list) and len(v) > max_items:
            out[k] = v[:max_items]
            out[f"{k}_truncated_from"] = len(v)
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Generación de matriz JSON
# ---------------------------------------------------------------------------

def emit_matrix(result: dict[str, Any], variant: str) -> Path:
    """Guarda matriz JSON con sufijo _v2."""
    out_path = OUT_DIR / f"AC20-FZK-Haus_compliance_post_{variant}_v2.json"
    serialized = {
        "audit_meta": result["audit_meta"],
        "summary": result["summary"],
        "results": result["results"],
    }
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(serialized, fh, indent=2, ensure_ascii=False)
    return out_path


# ---------------------------------------------------------------------------
# Generación de reporte MD exhaustivo
# ---------------------------------------------------------------------------

def emit_report(result: dict[str, Any], variant: str) -> Path:
    """Genera docs/audit_report_<variant>.md exhaustivo."""
    meta = result["audit_meta"]
    summary = result["summary"]
    results = result["results"]

    # Agrupaciones útiles
    by_backend: dict[str, list[dict[str, Any]]] = {}
    by_dim: dict[str, list[dict[str, Any]]] = {}
    fails: list[dict[str, Any]] = []
    partials: list[dict[str, Any]] = []
    na: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for r in results:
        by_backend.setdefault(r["backend"], []).append(r)
        by_dim.setdefault(r["dimension"], []).append(r)
        if r["status"] == "fail":
            fails.append(r)
        elif r["status"] == "partial":
            partials.append(r)
        elif r["status"] == "not_applicable":
            na.append(r)
        elif r["status"] == "error":
            errors.append(r)

    lines: list[str] = []
    add = lines.append

    # ---------------- Encabezado ----------------
    add(f"# Audit Report · variante {variant}")
    add("")
    add(f"> Generado el {meta['timestamp_utc']} por el motor "
        f"`{meta['engine_version']}`.")
    add("")
    add("## 1. Metadatos de auditoría")
    add("")
    add("| Campo | Valor |")
    add("|---|---|")
    add(f"| Variante EIR | `{meta['eir_variant']}` |")
    add(f"| Versión EIR | `{meta['eir_version']}` |")
    add(f"| Fuente EIR | `{meta['eir_source']}` |")
    add(f"| YAMLs usados | `{', '.join(Path(p).name for p in meta['eir_paths'])}` |")
    add(f"| Modelo IFC | `{Path(meta['model_path']).name}` |")
    add(f"| SHA-256 modelo | `{meta['model_sha256']}` |")
    add(f"| Schema modelo | `{meta['model_schema']}` |")
    add(f"| Backends | `{', '.join(meta['backends_used'])}` |")
    add(f"| Threshold pass | {meta['thresholds']['pass_min_pct']}% |")
    add(f"| Threshold partial | {meta['thresholds']['partial_min_pct']}% |")
    add(f"| Motor | `{meta['engine_version']}` |")
    add("")

    # ---------------- Summary ----------------
    add("## 2. Resumen global")
    add("")
    add("| Métrica | Valor |")
    add("|---|---|")
    for k in ("total", "applicable", "pass", "fail", "partial",
              "not_applicable", "error", "pct_pass"):
        v = summary.get(k)
        if k == "pct_pass":
            add(f"| `{k}` | **{v}%** |")
        else:
            add(f"| `{k}` | {v} |")
    add("")

    # ---------------- Distribución por backend ----------------
    add("## 3. Distribución por backend")
    add("")
    add("| Backend | Total | Pass | Fail | Partial | N/A | Error |")
    add("|---|---|---|---|---|---|---|")
    for backend in sorted(by_backend.keys()):
        rs = by_backend[backend]
        counts = {"pass": 0, "fail": 0, "partial": 0, "not_applicable": 0, "error": 0}
        for r in rs:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        add(f"| `{backend}` | {len(rs)} | {counts['pass']} | {counts['fail']} | "
            f"{counts['partial']} | {counts['not_applicable']} | {counts['error']} |")
    add("")

    # ---------------- Distribución por dimensión ISO 19650-2 ----------------
    add("## 4. Distribución por dimensión (ISO 19650-2)")
    add("")
    add("| Dim | Nombre | Total | Pass | Fail | Partial | N/A | Pct |")
    add("|---|---|---|---|---|---|---|---|")
    DIM_NAMES = {
        "D1": "Modelo", "D2": "Propiedades", "D3": "Relaciones",
        "D4": "Geometría", "D5": "Unidades", "D6": "Clasificación",
        "D7": "Temporal 4D", "D8": "Coste 5D",
    }
    for dim in sorted(by_dim.keys()):
        rs = by_dim[dim]
        counts = {"pass": 0, "fail": 0, "partial": 0, "not_applicable": 0, "error": 0}
        for r in rs:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        applicable = len(rs) - counts["not_applicable"]
        pct = (counts["pass"] / applicable * 100.0) if applicable else 0.0
        add(f"| {dim} | {DIM_NAMES.get(dim, '?')} | {len(rs)} | {counts['pass']} | "
            f"{counts['fail']} | {counts['partial']} | {counts['not_applicable']} | "
            f"{pct:.1f}% |")
    add("")

    # ---------------- Detalle por check ----------------
    add("## 5. Detalle por check")
    add("")
    add("Tabla de resumen rápido (ordenada por dimensión, luego check_id):")
    add("")
    add("| check_id | Dim | Backend | Status | Score | Pass≥ | Partial≥ | Mensaje |")
    add("|---|---|---|---|---|---|---|---|")
    sorted_results = sorted(results, key=lambda r: (r["dimension"], r["check_id"]))
    for r in sorted_results:
        msg = (r.get("message") or "").replace("|", "\\|").replace("\n", " ")
        if len(msg) > 90:
            msg = msg[:87] + "..."
        add(f"| `{r['check_id']}` | {r['dimension']} | `{r['backend']}` | "
            f"{STATUS_BADGE.get(r['status'], r['status'])} | "
            f"{_fmt_score(r['score'])} | {_fmt_threshold(r['threshold_pass'])} | "
            f"{_fmt_threshold(r['threshold_partial'])} | {msg} |")
    add("")

    # ---------------- Hallazgos clave ----------------
    add("## 6. Hallazgos clave")
    add("")

    if fails:
        add(f"### 6.1 Fallos críticos ({len(fails)})")
        add("")
        for r in fails:
            add(f"#### `{r['check_id']}` · {r['dimension']} · backend `{r['backend']}`")
            add("")
            add(f"- **Estado:** {STATUS_BADGE['fail']}")
            add(f"- **Score:** {_fmt_score(r['score'])}")
            add(f"- **Mensaje:** {r.get('message', '')}")
            ev = _sanitize_evidence(r.get("evidence") or {})
            if ev:
                add("- **Evidencia:**")
                add("```json")
                add(json.dumps(ev, indent=2, ensure_ascii=False))
                add("```")
            # Recomendación si hay instructions IDS
            if isinstance(r.get("evidence"), dict):
                instr = r["evidence"].get("instructions")
                if instr:
                    add(f"- **Recomendación (IDS):** {instr}")
            add("")
    else:
        add("### 6.1 Fallos críticos")
        add("")
        add("Sin fallos críticos.")
        add("")

    if partials:
        add(f"### 6.2 Cumplimiento parcial ({len(partials)})")
        add("")
        for r in partials:
            add(f"- `{r['check_id']}` ({r['dimension']}) · score "
                f"{_fmt_score(r['score'])} · {r.get('message', '')}")
        add("")

    if na:
        add(f"### 6.3 No aplicables ({len(na)})")
        add("")
        add("Estos checks no se pudieron evaluar contra el modelo (ausencia de "
            "datos necesarios). No restan del pct_pass pero indican lagunas en "
            "el modelo a cubrir en próximas iteraciones.")
        add("")
        for r in na:
            add(f"- `{r['check_id']}` ({r['dimension']}) · {r.get('message', '')}")
        add("")

    if errors:
        add(f"### 6.4 Errores de ejecución ({len(errors)})")
        add("")
        for r in errors:
            add(f"- `{r['check_id']}` ({r['dimension']}) · {r.get('message', '')}")
        add("")

    # ---------------- Recomendaciones consolidadas ----------------
    add("## 7. Recomendaciones consolidadas")
    add("")
    if fails or partials:
        add("Acciones sugeridas, ordenadas por impacto (de mayor a menor):")
        add("")
        # Prioridad: fallos en D1 > D3 > D2 > resto
        priority_order = ["D1", "D3", "D2", "D5", "D6", "D7", "D8", "D4"]
        action_items: list[tuple[str, dict[str, Any]]] = []
        for r in fails + partials:
            action_items.append((r["dimension"], r))
        action_items.sort(
            key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else 99
        )
        for i, (_, r) in enumerate(action_items, 1):
            rec_text = r.get("message", "").split(".")[0]
            add(f"{i}. **`{r['check_id']}` ({r['dimension']}):** {rec_text}.")
        add("")
    else:
        add("Sin fallos ni cumplimientos parciales: el modelo supera la auditoría "
            "para esta variante.")
        add("")

    # ---------------- Footer ----------------
    add("---")
    add("")
    add("**Trazabilidad:** este reporte fue generado por "
        f"`scripts/s6x_generate_e6_outputs.py` a partir de "
        f"`out/AC20-FZK-Haus_compliance_post_{variant}_v2.json`. La matriz JSON "
        "es la fuente canónica; este Markdown es derivado.")
    add("")
    add("Motor: `quality_engine 0.2.0-s6x` · Sesión S6·X · "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    add("")

    out_path = DOCS_DIR / f"audit_report_{variant}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if not MODEL_PATH.exists():
        print(f"ERROR: modelo no encontrado en {MODEL_PATH}")
        return 1

    OUT_DIR.mkdir(exist_ok=True, parents=True)
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    print(f"Modelo: {MODEL_PATH.name}")
    print(f"Variantes: {', '.join(VARIANTS)}")
    print()

    global_summary: list[dict[str, Any]] = []

    for variant in VARIANTS:
        print(f"[{variant}] ejecutando audit...")
        result = run_audit(
            model_path=MODEL_PATH,
            eir_variant=variant,
            eir_version=EIR_VERSION,
            backends=["yaml_python", "ids_xml"],
        )
        matrix_path = emit_matrix(result, variant)
        report_path = emit_report(result, variant)
        s = result["summary"]
        print(
            f"  → matrix:  {matrix_path.relative_to(REPO_ROOT)}  "
            f"({s['total']} checks, {s['pct_pass']}% pass)"
        )
        print(f"  → report:  {report_path.relative_to(REPO_ROOT)}")
        global_summary.append(
            {
                "variant": variant,
                "total": s["total"],
                "pass": s["pass"],
                "fail": s["fail"],
                "partial": s["partial"],
                "not_applicable": s["not_applicable"],
                "error": s["error"],
                "pct_pass": s["pct_pass"],
            }
        )

    print()
    print("=== Resumen comparativo ===")
    print(
        f"{'Variante':<14} {'Total':>6} {'Pass':>5} {'Fail':>5} "
        f"{'Part':>5} {'N/A':>5} {'Err':>4} {'Pct%':>7}"
    )
    for g in global_summary:
        print(
            f"{g['variant']:<14} {g['total']:>6} {g['pass']:>5} {g['fail']:>5} "
            f"{g['partial']:>5} {g['not_applicable']:>5} {g['error']:>4} "
            f"{g['pct_pass']:>7}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
