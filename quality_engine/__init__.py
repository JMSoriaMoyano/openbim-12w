"""
quality_engine · Motor de calidad BIM modular (refactor S6·L).

Estructura:
    core/       orquestación, modelo de resultado, merge común+variante
    backends/   ejecutores: yaml_python (legacy) + ids_xml (estándar IDS v1.0)
    rules/      reglas organizadas por dimensión D1-D8 del marco S6·L
    cli.py      entrypoint nuevo (paralelo a scripts/s4s_audit_eir.py)

Marco de referencia: docs/S6L_marco_calidad.md v1.0
Checklist objetivo:  docs/E6_checklist_calidad.md v1.0

Estado S6·L: estructura + stubs. Implementación viene en S6·X (Mié 17/06).
"""

__version__ = "0.1.0-stub"
__status__ = "skeleton"
