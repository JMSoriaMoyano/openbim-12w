# ---
# title: "S4·X · Lab IfcOpenShell: consultas avanzadas"
# session: "S4·X (Mie 03/06/2026)"
# author: "José M. Soria (NEXUM)"
# format: "py:percent (compatible VS Code Interactive y Jupyter via jupytext)"
# ---

# %% [markdown]
# # S4·X · Lab IfcOpenShell: consultas avanzadas
#
# Objetivo: ejecutar de forma interactiva las 3 consultas de `s4x_ifc_lab.py`
# sobre FZK-Haus y construir evidencia de incumplimientos LOIN para E4.
#
# Este notebook NO escribe a `out/` — solo ejecuta y muestra resultados.
# Para persistir evidencias usa la CLI con `--out`.
#
# **Pre-requisitos:**
# - Repo `openbim-12w` clonado, venv activo, `pip install -r requirements.txt`
# - Fichero `models/samples/_local/AC20-FZK-Haus.ifc` presente
# - Scripts `_ifc_helpers.py`, `s4l_ifc_query.py`, `s4x_ifc_lab.py` en `scripts/`
#
# **Cómo ejecutar:**
# - VS Code: abrir este `.py`, clic en "Run Cell" sobre cualquier `# %%`
# - Jupyter: `jupytext --to ipynb notebooks/S4X_lab_consultas.py` y abrir el `.ipynb`

# %% Setup
"""Imports y carga del modelo. Ejecuta esta celda primero."""
import json
import sys
from collections import Counter
from pathlib import Path

# Añadimos scripts/ al sys.path para poder importar como módulos.
# Resolución robusta: partimos de la ubicación física del fichero, no del CWD.
# Esto garantiza que el notebook funciona desde VS Code, Jupyter o CLI,
# independientemente desde dónde se invoque Python.
try:
    # Caso normal: ejecutado como .py desde VS Code Interactive o CLI
    NOTEBOOK_DIR = Path(__file__).resolve().parent
except NameError:
    # Caso fallback: ejecutado en Jupyter clásico (no hay __file__)
    NOTEBOOK_DIR = Path.cwd()
    if NOTEBOOK_DIR.name != "notebooks":
        NOTEBOOK_DIR = NOTEBOOK_DIR / "notebooks"

REPO_ROOT = NOTEBOOK_DIR.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

print(f"[setup] REPO_ROOT = {REPO_ROOT}")
print(f"[setup] SCRIPTS_DIR = {SCRIPTS_DIR}")

from _ifc_helpers import load_ifc, resolve_model_path, report_header  # noqa: E402
from s4x_ifc_lab import (  # noqa: E402
    query_by_type_with_psets,
    query_spatial_containment,
    query_missing_property,
)

IFC_NAME = "AC20-FZK-Haus.ifc"
ifc_path = resolve_model_path(IFC_NAME)
model = load_ifc(ifc_path)

# Cabecera de sanity check
header = report_header(model, ifc_path)
print(json.dumps(header, indent=2, ensure_ascii=False, default=str))


# %% [markdown]
# ## Celda 1 · `query_by_type_with_psets`
#
# Devuelve todas las instancias de un tipo IFC con sus Psets ya leídos.
# Caso de uso: "dame los IfcWallStandardCase con solo Pset_WallCommon".
#
# Validación cruzada con S4·L: deben ser **13 muros** (5 internos + 8 externos).

# %% Q1 · Muros con Pset_WallCommon
result_q1 = query_by_type_with_psets(
    model,
    ifc_type="IfcWallStandardCase",
    pset_names=["Pset_WallCommon"],
)

print(f"Total IfcWallStandardCase: {result_q1['total_found']}")
print(f"Pset filter: {result_q1['query']['pset_filter']}")
print()

# Muro #15042 (referencia E3 baseline) — primer elemento de la lista
muro_15042 = next(
    (i for i in result_q1["instances"] if i["entity"]["id"] == 15042),
    None,
)
if muro_15042:
    print("Muro #15042 (referencia E3):")
    print(f"  GUID: {muro_15042['entity']['guid']}")
    print(f"  Name: {muro_15042['entity']['name']}")
    print(f"  Pset_WallCommon: {muro_15042['instance_psets'].get('Pset_WallCommon', {})}")
    print(f"  Summary: {muro_15042['summary']}")


# %% [markdown]
# ## Celda 2 · `query_spatial_containment`
#
# Recorre el árbol Site→Building→Storey→Element.
# Hallazgo S4·X documentado: 20 "huérfanos" son falso positivo
# (17 IfcOpeningElement + 3 IfcVirtualElement, comportamiento IFC correcto).
#
# Mejora pendiente v0.2: excluir IfcOpeningElement e IfcVirtualElement antes
# de evaluar `ContainedInStructure`.

# %% Q2 · Árbol espacial
result_q2 = query_spatial_containment(model)

print("Summary espacial:")
print(json.dumps(result_q2["summary"], indent=2, ensure_ascii=False))
print()

# Desglose de huérfanos por clase
huerfanos_por_clase = Counter(o["is_a"] for o in result_q2["orphans"])
print("Huérfanos por clase (esperado: IfcOpeningElement + IfcVirtualElement):")
for cls, n in huerfanos_por_clase.most_common():
    print(f"  {cls}: {n}")

# Estructura espacial: Site → Building → Storeys
project = result_q2["project"]
print(f"\nProyecto: {project['name']} ({project['guid']})")
for site in project["children_spatial"]:
    print(f"  Site: {site['name']}")
    for building in site["children_spatial"]:
        print(f"    Building: {building['name']}")
        for storey in building["children_spatial"]:
            n_el = storey["contained_elements_count"]
            classes = ", ".join(
                f"{k}:{v}" for k, v in list(storey["contained_elements_by_class"].items())[:5]
            )
            print(f"      Storey: {storey['name']} — {n_el} elementos ({classes}...)")


# %% [markdown]
# ## Celda 3 · `query_missing_property` (auditoría LOIN inversa)
#
# Detecta instancias que NO declaran una propiedad concreta.
# Comparamos 2 propiedades canónicas de Pset_WallCommon:
# - `ThermalTransmittance` → S4·L muestra que muro #15042 SÍ la declara
# - `FireRating` → S4·L hallazgo #2 sugiere que está ausente sistemáticamente

# %% Q3.a · ThermalTransmittance
result_thermal = query_missing_property(
    model,
    ifc_type="IfcWallStandardCase",
    pset_name="Pset_WallCommon",
    prop_name="ThermalTransmittance",
)
print("ThermalTransmittance · Pset_WallCommon")
print(f"  Total muros: {result_thermal['total']}")
print(f"  Compliance: {result_thermal['compliance']}")
print(f"  Compliance %: {result_thermal['compliance_pct']}")
print(f"  Sample value: {result_thermal['sample_value']}")

# %% Q3.b · FireRating (incumplimiento esperado)
result_fire = query_missing_property(
    model,
    ifc_type="IfcWallStandardCase",
    pset_name="Pset_WallCommon",
    prop_name="FireRating",
)
print("\nFireRating · Pset_WallCommon")
print(f"  Total muros: {result_fire['total']}")
print(f"  Compliance: {result_fire['compliance']}")
print(f"  Compliance %: {result_fire['compliance_pct']}")
print(f"  Offenders: {len(result_fire['offenders'])}")


# %% [markdown]
# ## Celda 4 · Síntesis E4 — Tabla de incumplimientos
#
# Output formateado de los 13 offenders de FireRating, listos para incluir
# como evidencia en el entregable E4 (sábado 06/06).

# %% Q4 · Tabla offenders FireRating
print(f"{'ID':>6}  {'NAME':<22}  {'GUID':<24}  {'STATUS':<14}")
print("-" * 72)
for off in result_fire["offenders"]:
    print(
        f"{off['id']:>6}  "
        f"{(off['name'] or '<sin nombre>'):<22}  "
        f"{off['guid']:<24}  "
        f"{off['status']:<14}"
    )

# Distribución int/ext según convención naming ArchiCAD ("Wand-Int-*" vs "Wand-Ext-*")
internos = [o for o in result_fire["offenders"] if "-Int-" in (o["name"] or "")]
externos = [o for o in result_fire["offenders"] if "-Ext-" in (o["name"] or "")]
print(f"\nDesglose por tipología (heurística por nombre):")
print(f"  Internos (Wand-Int-*): {len(internos)}")
print(f"  Externos (Wand-Ext-*): {len(externos)}")


# %% [markdown]
# ## Notas finales y next steps
#
# **Hallazgos S4·X (resumen ejecutivo):**
# 1. ThermalTransmittance · Pset_WallCommon: **100% compliance** (sample=1.5)
# 2. FireRating · Pset_WallCommon: **0% compliance** (13/13 absent_prop)
# 3. Estructura espacial sin huérfanos reales (20 "huérfanos" = aperturas y virtuales, ok IFC)
#
# **Para E4 sábado 06/06:**
# - Evidencia central: `out/s4x_missing_firerating_baseline.json` (versionado)
# - Auditoría ampliable a otras propiedades NEXUM (AcousticRating, LoadBearing, IsExternal)
#   simplemente cambiando `--prop` en la CLI
# - Considerar añadir auditoría sobre otros tipos: IfcSlab, IfcRoof, IfcDoor, IfcWindow
#
# **Deuda técnica documentada (v0.2 de s4x_ifc_lab.py):**
# - `query_spatial_containment` debe excluir IfcOpeningElement e IfcVirtualElement
#   antes de evaluar contención espacial (huérfanos = falsos positivos sistemáticos)
# - Posible añadir 4ª consulta `query_by_pset_name` para listar qué Psets aparecen
#   en el modelo (descubrimiento, no auditoría)
