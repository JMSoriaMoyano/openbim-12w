"""
quality_engine.core.result · Modelo de resultado de un check de calidad.

Dataclass canónica devuelta por todo backend tras ejecutar un check.
Marco de referencia: docs/S6L_marco_calidad.md §5 (pass/fail/partial).
"""

from dataclasses import dataclass, field
from typing import Literal, Any

# Estados canónicos del marco §5.
CheckStatus = Literal["pass", "fail", "partial", "not_applicable", "error"]

# Capas ISO 19650-2 del marco §2.
LayerISO = Literal["grafica", "no_grafica", "documentacion"]

# Dimensiones D1-D8 del marco §2.
Dimension = Literal["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]

# Backends soportados (marco §4.2).
Backend = Literal["yaml_python", "ids_xml"]


@dataclass
class ResultadoCheck:
    """
    Resultado canónico de un check de calidad.

    Toda regla en quality_engine.rules.d*_* y todo backend en
    quality_engine.backends.* DEBE devolver instancias de esta clase.

    Atributos:
        check_id        identificador único (ej. 'C-M-01', 'C-P-03')
        dimension       dimensión D1-D8 a la que pertenece
        layer           capa ISO 19650-2
        status          estado: pass / fail / partial / not_applicable / error
        backend         qué backend ejecutó el check
        score           ratio 0.0-1.0 cuando aplica (% cumplimiento)
        threshold_pass  umbral para 'pass' (default 1.0 = 100%)
        threshold_partial  umbral para 'partial'
        evidence        dict con datos de evidencia (conteos, samples, etc.)
        message         texto humano corto explicando el resultado
        eir_source      trazabilidad: '{variant}@{version}' (ej. 'diseno@0.2')
    """

    check_id: str
    dimension: Dimension
    layer: LayerISO
    status: CheckStatus
    backend: Backend
    score: float | None = None
    threshold_pass: float = 1.0
    threshold_partial: float | None = None
    evidence: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    eir_source: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serializa a dict para matriz JSON.

        El orden de claves está fijado para que la matriz sea diff-friendly
        entre ejecuciones (estable bajo git).
        """
        return {
            "check_id": self.check_id,
            "dimension": self.dimension,
            "layer": self.layer,
            "status": self.status,
            "backend": self.backend,
            "score": self.score,
            "threshold_pass": self.threshold_pass,
            "threshold_partial": self.threshold_partial,
            "message": self.message,
            "eir_source": self.eir_source,
            "evidence": self.evidence,
        }
