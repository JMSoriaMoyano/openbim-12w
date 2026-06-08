# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3 (.venv)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # S5·L · Explorador geométrico de AC20-FZK-Haus
#
# **Sesión 5 · Lunes** · IfcOpenShell: geometría y autoría (lectura).
#
# Notebook didáctico que muestra cómo pasar de "leer propiedades" a
# "leer geometría" usando `ifcopenshell.geom` y visualiza el modelo
# en planta (proyección XY) coloreado por tipo IFC.
#
# **Output esperado:**
# - Tabla de stats por tipo IFC (count, vertices, triangles, bbox)
# - Figura plan view (`out/s5l_geom_planview_baseline.png`)
#
# **Política de coordenadas:** `use-world-coords=True` para visualización
# directa sin componer transformaciones manualmente.

# %% [markdown]
# ## Celda 1 · Imports y configuración

# %%
import sys
from pathlib import Path

# Ajuste de path para que el notebook encuentre los módulos de scripts/
NOTEBOOK_DIR = Path.cwd()
REPO_ROOT = NOTEBOOK_DIR if (NOTEBOOK_DIR / "scripts").exists() else NOTEBOOK_DIR.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import ifcopenshell
import ifcopenshell.geom
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import numpy as np

from _ifc_helpers import load_ifc, resolve_model_path
from s5l_ifc_geom_read import iter_shapes, summarize_geometry, _make_settings

print("Repo root detectado:", REPO_ROOT)
print("ifcopenshell:", ifcopenshell.version)
print("matplotlib:", plt.matplotlib.__version__)

# %% [markdown]
# ## Celda 2 · Cargar modelo y resumen agregado

# %%
IFC_NAME = "AC20-FZK-Haus.ifc"
ifc_path = resolve_model_path(IFC_NAME)
print(f"Cargando: {ifc_path}")

model = load_ifc(ifc_path)
print(f"Schema: {model.schema}")

# Llamada al resumen estructurado (misma función que el CLI)
summary = summarize_geometry(model)

print(f"\nElementos procesados: {summary['model_meta']['elements_processed']}")
print(f"Bounding box global: {summary['global_bbox']}")

# %% [markdown]
# ## Celda 3 · Tabla de stats por tipo IFC

# %%
print(f"{'IfcType':<28} {'count':>6} {'vertices':>10} {'triangles':>10}")
print("-" * 60)
for t, b in summary["by_type"].items():
    print(f"{t:<28} {b['count']:>6} {b['total_vertices']:>10} {b['total_triangles']:>10}")

# %% [markdown]
# ## Celda 4 · Recolectar vértices XY por tipo
#
# Para la plan view proyectamos cada triángulo al plano XY ignorando Z.
# Coloreamos por tipo IFC con una paleta consistente.

# %%
# Paleta por tipo (consistente con convenciones BIM habituales)
TYPE_COLORS: dict[str, str] = {
    "IfcWallStandardCase": "#1f77b4",  # azul
    "IfcWall":             "#1f77b4",
    "IfcSlab":             "#2ca02c",  # verde
    "IfcDoor":             "#d62728",  # rojo
    "IfcWindow":           "#9467bd",  # morado
    "IfcStair":            "#ff7f0e",  # naranja
    "IfcRailing":          "#8c564b",  # marrón
    "IfcMember":           "#7f7f7f",  # gris
    "IfcBeam":             "#bcbd22",  # oliva
    "IfcSpace":            "#e377c2",  # rosa
    "IfcSite":             "#17becf",  # cian
}
DEFAULT_COLOR = "#cccccc"

# Recorremos shapes de nuevo (más rápido que recalcular triángulos desde summary)
settings = _make_settings(use_world_coords=True)

triangles_by_type: dict[str, list[np.ndarray]] = {}

for elem, shape in iter_shapes(model, settings=settings):
    ifc_type = elem.is_a()
    verts = np.array(shape.geometry.verts).reshape(-1, 3)
    faces = np.array(shape.geometry.faces).reshape(-1, 3)
    if len(faces) == 0:
        continue
    # Proyección XY: tomamos sólo columnas 0 y 1
    tri_xy = verts[faces][:, :, :2]  # shape: (n_tri, 3, 2)
    triangles_by_type.setdefault(ifc_type, []).append(tri_xy)

print(f"Tipos con geometría XY: {sorted(triangles_by_type.keys())}")

# %% [markdown]
# ## Celda 5 · Render plan view + guardar PNG
#
# Generamos una figura matplotlib con todos los triángulos proyectados
# en XY, agrupados por tipo y coloreados según paleta. Se guarda en
# `out/s5l_geom_planview_baseline.png` para entrar como evidencia en repo.

# %%
fig, ax = plt.subplots(figsize=(12, 10))

# Ordenamos tipos para que los grandes vayan al fondo y los pequeños arriba
TYPE_DRAW_ORDER = [
    "IfcSite", "IfcSlab", "IfcSpace", "IfcStair", "IfcRailing",
    "IfcMember", "IfcBeam",
    "IfcWallStandardCase", "IfcWall",
    "IfcWindow", "IfcDoor",
]
remaining = [t for t in triangles_by_type if t not in TYPE_DRAW_ORDER]
draw_order = [t for t in TYPE_DRAW_ORDER if t in triangles_by_type] + remaining

for ifc_type in draw_order:
    color = TYPE_COLORS.get(ifc_type, DEFAULT_COLOR)
    patches = []
    for tri_array in triangles_by_type[ifc_type]:
        for tri in tri_array:
            patches.append(MplPolygon(tri, closed=True))
    pc = PatchCollection(
        patches,
        facecolor=color,
        edgecolor="black",
        linewidths=0.15,
        alpha=0.55,
        label=ifc_type,
    )
    ax.add_collection(pc)

# Configuración de ejes
gbb = summary["global_bbox"]
margin = 1.0
ax.set_xlim(gbb["min"][0] - margin, gbb["max"][0] + margin)
ax.set_ylim(gbb["min"][1] - margin, gbb["max"][1] + margin)
ax.set_aspect("equal")
ax.set_xlabel("X [m]")
ax.set_ylabel("Y [m]")
ax.set_title(f"S5·L · Plan view AC20-FZK-Haus.ifc · schema {model.schema}\n"
             f"{summary['model_meta']['elements_processed']} elementos · "
             f"proyección XY · use-world-coords")
ax.grid(True, linestyle=":", alpha=0.4)

# Leyenda manual (PatchCollection no genera handles automáticamente)
from matplotlib.patches import Patch
legend_handles = [
    Patch(facecolor=TYPE_COLORS.get(t, DEFAULT_COLOR), edgecolor="black",
          alpha=0.55, label=f"{t} ({summary['by_type'][t]['count']})")
    for t in draw_order
]
ax.legend(handles=legend_handles, loc="upper right", fontsize=8, framealpha=0.9)

plt.tight_layout()

# Guardar como PNG en out/ (entrará como evidencia baseline en commit)
out_dir = REPO_ROOT / "out"
out_dir.mkdir(exist_ok=True)
png_path = out_dir / "s5l_geom_planview_baseline.png"
fig.savefig(png_path, dpi=120, bbox_inches="tight")
print(f"[OK] Plan view guardada en {png_path} ({png_path.stat().st_size / 1024:.1f} KB)")

plt.show()

# %% [markdown]
# ## Celda 6 · Observaciones técnicas
#
# **Hallazgos sobre FZK-Haus:**
#
# 1. **127 IfcProduct → 90 elementos con geometría.** La diferencia (37)
#    son entidades sin representación geométrica (Project, Site, Building,
#    Storey) o excluidas por defecto (IfcOpeningElement, IfcVirtualElement).
#
# 2. **Bounding box ~18×16×7 m** coherente con casa unifamiliar de 2
#    plantas. El offset negativo en X e Y (-3 m) indica que el origen IFC
#    no coincide con la esquina del edificio.
#
# 3. **IfcRailing y IfcStair** acumulan más triángulos por unidad que muros
#    o forjados: geometrías curvas/complejas requieren más teselado.
#
# 4. **IfcWindow** son 11 elementos con 6644 triángulos: aprox. 600 tri/ventana,
#    sugiere modelado detallado de marcos.
#
# 5. **IfcMember** (42 elementos, 504 tri) son probablemente miembros de
#    estructura/barandilla muy simples (~12 tri cada uno).
#
# **Próximos pasos S5·L:**
# - Bloque C · Reglas de autoría (qué se toca y qué no).
# - Bloque D · Autoría real: poblar FireRating en 3 puertas + crear IfcWall.
# - Bloque E · Re-auditoría EIR post-autoría (cierre del bucle).

# %%
print("Notebook S5L_geom_explorer ejecutado correctamente.")
