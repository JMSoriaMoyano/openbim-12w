"""
s3l_ifc_inspect.py — Inspector mínimo de IFC

Sesión:        S3·L (semana 3, lunes) · 25/05/2026
Nivel:         2 (pseudocódigo + walkthrough conceptual)
Estado:        v0.1 — ESQUELETO. La implementación real con IfcOpenShell se hace en S4·L.
Schema base:   IFC4 (IFC4 ADD2 TC1)
Modelo:        models/samples/_local/AC20-FZK-Haus.ifc
SHA-256:       70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994

Propósito de este fichero
-------------------------
Este script NO ejecuta nada todavía. Es el contrato funcional + esqueleto:

  1. Define la API pública (funciones, contratos, tipos de retorno).
  2. Documenta el algoritmo de cada bloque en lenguaje natural y
     mediante stubs con `raise NotImplementedError("...")`.
  3. Incluye el bloque de verificación SHA-256 + carga (paso 0)
     que en S4·L será lo único que cambie: añadir `ifcopenshell.open()`
     y rellenar las funciones.

Cómo evolucionará en S4·L (semana 4, lunes — "IfcOpenShell: lectura y consultas")
--------------------------------------------------------------------------------
- Se añadirá `import ifcopenshell`.
- Cada `raise NotImplementedError(...)` se reemplazará por consultas
  reales (`model.by_type("IfcProject")`, `ifcopenshell.util.element.get_psets()`).
- Se añadirá un `pytest` mínimo en `tests/test_s3l_ifc_inspect.py`
  con asserts contra el FZK-Haus (1 IfcProject, 13 IfcWallStandardCase, 482
  IfcRelDefinesByProperties, etc. — conteos extraídos en S3·L).

Ejecución prevista (S4·L)
-------------------------
  python scripts/s3l_ifc_inspect.py models/samples/_local/AC20-FZK-Haus.ifc

Salida prevista (S4·L)
----------------------
  === HEADER ===
  Schema declarado: IFC4
  MVD: ViewDefinition [, QuantityTakeOffAddOnView, SpaceBoundary2ndLevelAddOnView]
  Originating: GRAPHISOFT ARCHICAD-64 20.0.0 GER FULL
  Fecha: 2016-12-21T17:54:06

  === Pirámide espacial ===
  IfcProject       'Projekt-FZK-Haus' (0lY6P5Ur90TAQnnnI6wtnb)
   └── IfcSite      'Gelaende' (lat 49°6'N, lon 8°26'E, elev 110m)
        └── IfcBuilding 'FZK-Haus / Wohnhaus'
             ├── IfcBuildingStorey 'Erdgeschoss'  (Z=0.0m, 6 spaces, 38 elementos)
             └── IfcBuildingStorey 'Dachgeschoss' (Z=2.7m, 1 space, ~58 elementos)

  === Conteo de elementos físicos ===
  IfcWallStandardCase ........... 13
  IfcSlab .......................  4
  IfcWindow ..................... 11
  IfcDoor .......................  5
  IfcStair ......................  1
  IfcRailing ....................  2
  IfcOpeningElement ............. 17

  === Inventario de relaciones ===
  IfcRelDefinesByProperties ...... 482
  IfcRelSpaceBoundary ............  81
  IfcRelAssociatesMaterial .......  21
  IfcRelDefinesByType ............  18
  IfcRelVoidsElement .............  17
  IfcRelFillsElement .............  16
  IfcRelConnectsPathElements .....  16
  IfcRelAggregates ...............   5
  IfcRelContainedInSpatialStructure  2
  IfcRelAssociatesClassification .   1
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

# En S4·L se descomentará:
# import ifcopenshell
# import ifcopenshell.util.element

if TYPE_CHECKING:
    # Para type hints sin import real todavía
    from typing import Any
    IfcFile = Any  # ifcopenshell.file
    IfcEntity = Any  # ifcopenshell.entity_instance


# =============================================================================
# 0. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

EXPECTED_SHA256: str = (
    "70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994"
)
"""SHA-256 canónico de AC20-FZK-Haus.ifc declarado en models/samples/SOURCES.md §4.3."""

DEFAULT_IFC_PATH: Path = Path("models/samples/_local/AC20-FZK-Haus.ifc")
"""Ruta relativa al fichero de referencia (Opción B: no versionado en git)."""

# Conteos esperados del FZK-Haus, usados como validación cruzada en S4·L
# y como casos de test en tests/test_s3l_ifc_inspect.py
EXPECTED_COUNTS_FZK: dict[str, int] = {
    # Entidades espaciales
    "IfcProject": 1,
    "IfcSite": 1,
    "IfcBuilding": 1,
    "IfcBuildingStorey": 2,
    # Elementos físicos
    "IfcWallStandardCase": 13,
    "IfcSlab": 4,
    "IfcWindow": 11,
    "IfcDoor": 5,
    "IfcStair": 1,
    "IfcRailing": 2,
    "IfcOpeningElement": 17,
    # Tipos
    "IfcWallType": 2,
    # Relaciones
    "IfcRelAggregates": 5,
    "IfcRelContainedInSpatialStructure": 2,
    "IfcRelDefinesByType": 18,
    "IfcRelDefinesByProperties": 482,
    "IfcRelAssociatesMaterial": 21,
    "IfcRelVoidsElement": 17,
    "IfcRelFillsElement": 16,
    "IfcRelConnectsPathElements": 16,
    "IfcRelSpaceBoundary": 81,
    "IfcRelAssociatesClassification": 1,
}


# =============================================================================
# 1. VERIFICACIÓN DE INTEGRIDAD (HOY YA SE PUEDE EJECUTAR)
# =============================================================================

def verify_sha256(ifc_path: Path, expected: str = EXPECTED_SHA256) -> None:
    """
    Comprueba que el fichero IFC coincide bit a bit con el manifest oficial.

    Reglas:
    - Si el fichero no existe → FileNotFoundError con instrucciones de descarga.
    - Si el SHA-256 no coincide → ValueError con ambos hashes para diagnóstico.
    - Si coincide → retorno silencioso.

    Esta función es la ÚNICA que ya funciona en S3·L. Las siguientes son
    pseudocódigo hasta S4·L.
    """
    if not ifc_path.exists():
        raise FileNotFoundError(
            f"No se encuentra {ifc_path}.\n"
            f"Descarga el fichero siguiendo models/samples/SOURCES.md §3.\n"
            f"URL oficial: https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc"
        )

    sha256 = hashlib.sha256()
    with ifc_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    actual = sha256.hexdigest()
    if actual != expected:
        raise ValueError(
            f"SHA-256 no coincide para {ifc_path}.\n"
            f"  Esperado: {expected}\n"
            f"  Obtenido: {actual}\n"
            f"Borra el fichero y repite descarga desde models/samples/SOURCES.md §3."
        )


# =============================================================================
# 2. APERTURA DEL MODELO  (NIVEL 2 — pseudocódigo)
# =============================================================================

def open_ifc(ifc_path: Path) -> "IfcFile":
    """
    Abre el fichero IFC con IfcOpenShell.

    [S4·L] Implementación:
        return ifcopenshell.open(str(ifc_path))

    [S4·L] Validación adicional recomendada:
        - Comprobar que model.schema == "IFC4" (o lo declarado en SOURCES.md).
        - Comprobar que model.by_type("IfcProject") tiene exactamente 1 entidad.
        - Log: número total de entidades (model.by_type("IfcRoot")).
    """
    raise NotImplementedError("S4·L: implementar con ifcopenshell.open()")


# =============================================================================
# 3. HEADER (Bloque A §6.1)
# =============================================================================

def report_header(model: "IfcFile") -> dict:
    """
    Extrae metadatos del HEADER del SPF.

    [S4·L] Implementación esperada (devuelve dict):
        {
            "schema":      model.schema,                 # 'IFC4'
            "mvd":         model.wrapped_data.header.file_description.description,
            "filename":    model.wrapped_data.header.file_name.name,
            "timestamp":   model.wrapped_data.header.file_name.time_stamp,
            "author":      model.wrapped_data.header.file_name.author,
            "organization": model.wrapped_data.header.file_name.organization,
            "originating_system": model.wrapped_data.header.file_name.originating_system,
        }

    En el FZK-Haus debe devolver:
        schema = 'IFC4'
        mvd contiene 'ViewDefinition' + 'QuantityTakeOffAddOnView' + 'SpaceBoundary2ndLevelAddOnView'
        originating_system contiene 'GRAPHISOFT ARCHICAD-64 20.0.0'
    """
    raise NotImplementedError("S4·L: parsear HEADER del SPF")


# =============================================================================
# 4. PIRÁMIDE ESPACIAL (Bloque A §4, Bloque B §1.1)
# =============================================================================

def walk_spatial_pyramid(model: "IfcFile") -> dict:
    """
    Recorre la pirámide IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace
    siguiendo `IfcRelAggregates`.

    Algoritmo:
        1. Localizar el único IfcProject (assert: len == 1).
        2. Para cada IfcProject, seguir IfcRelAggregates.IsDecomposedBy → IfcSite(s).
        3. Para cada IfcSite, seguir IsDecomposedBy → IfcBuilding(s).
        4. Para cada IfcBuilding, seguir IsDecomposedBy → IfcBuildingStorey(s).
        5. Para cada Storey, seguir IsDecomposedBy → IfcSpace(s).

    [S4·L] La navegación inversa usa el inverse attribute `IsDecomposedBy`:
        for rel_agg in project.IsDecomposedBy:
            for site in rel_agg.RelatedObjects:
                ...

    Estructura de retorno (dict-tree):
        {
            "project": {"id": "#66", "guid": "0lY6P5Ur90TAQnnnI6wtnb", "name": "Projekt-FZK-Haus"},
            "sites": [
                {
                    "id": "#389", "name": "Gelaende",
                    "lat_long_elev": [(49,6,1,566000), (8,26,11,540400), 110.0],
                    "buildings": [
                        {
                            "id": "#434", "name": "FZK-Haus",
                            "storeys": [
                                {"id": "#479", "name": "Erdgeschoss", "elevation": 0.0,
                                 "spaces": [{"id": "#20909", "name": "Schlafzimmer"}, ...]},
                                {"id": "#35065", "name": "Dachgeschoss", "elevation": 2.7,
                                 "spaces": [...]}
                            ]
                        }
                    ]
                }
            ]
        }
    """
    raise NotImplementedError("S4·L: recorrer pirámide con IfcRelAggregates")


# =============================================================================
# 5. CONTENCIÓN ESPACIAL (Bloque B §1.2)
# =============================================================================

def list_elements_per_storey(model: "IfcFile") -> dict[str, list[dict]]:
    """
    Lista los elementos físicos contenidos en cada planta usando
    `IfcRelContainedInSpatialStructure`.

    Algoritmo:
        Para cada IfcBuildingStorey:
            rel = storey.ContainsElements  # inverse attr (LISTA de IfcRelContained...)
            for r in rel:
                for elem in r.RelatedElements:
                    registrar (elem.GlobalId, elem.is_a(), elem.Name)

    [S4·L] En FZK-Haus debe devolver:
        {
            "Erdgeschoss": [<38 elementos>],
            "Dachgeschoss": [<~58 elementos>]
        }

    Donde cada elemento es:
        {"id": "#14502", "guid": "...", "type": "IfcSlab", "name": "..."}
    """
    raise NotImplementedError("S4·L: usar inverse attr ContainsElements")


# =============================================================================
# 6. CONTEO DE ELEMENTOS FÍSICOS (Bloque B §0)
# =============================================================================

def count_physical_elements(model: "IfcFile") -> dict[str, int]:
    """
    Cuenta instancias de las clases físicas más relevantes.

    [S4·L] Implementación:
        types = ["IfcWall", "IfcWallStandardCase", "IfcSlab", "IfcWindow",
                 "IfcDoor", "IfcStair", "IfcRailing", "IfcOpeningElement",
                 "IfcRoof", "IfcCovering", "IfcFurnishingElement"]
        return {t: len(model.by_type(t)) for t in types}

    Validación cruzada contra EXPECTED_COUNTS_FZK (subset).
    """
    raise NotImplementedError("S4·L: usar model.by_type() para cada tipo")


# =============================================================================
# 7. INVENTARIO DE RELACIONES (Bloque B §0)
# =============================================================================

def count_relationships(model: "IfcFile") -> dict[str, int]:
    """
    Cuenta instancias de cada subtipo de IfcRelationship.

    [S4·L] Implementación:
        rel_types = ["IfcRelAggregates", "IfcRelContainedInSpatialStructure",
                     "IfcRelDefinesByType", "IfcRelDefinesByProperties",
                     "IfcRelAssociatesMaterial", "IfcRelVoidsElement",
                     "IfcRelFillsElement", "IfcRelConnectsPathElements",
                     "IfcRelSpaceBoundary", "IfcRelAssociatesClassification",
                     "IfcRelNests", "IfcRelAssignsToGroup"]
        return {t: len(model.by_type(t)) for t in rel_types}

    Validación cruzada contra EXPECTED_COUNTS_FZK (subset).
    """
    raise NotImplementedError("S4·L: usar model.by_type() para cada relación")


# =============================================================================
# 8. ANATOMÍA DE UNA ENTIDAD (Bloque B §4 — caso de estudio del muro #15042)
# =============================================================================

def explain_entity(model: "IfcFile", global_id: str) -> dict:
    """
    Devuelve TODAS las relaciones que tocan a una entidad concreta.
    Es la materialización en código del 'caso de estudio del muro #15042'
    de Bloque B §4.

    Algoritmo:
        elem = model.by_guid(global_id)
        result = {
            "type": elem.is_a(),
            "name": elem.Name,
            "contained_in": [...],          # IfcRelContainedInSpatialStructure (inv: ContainedInStructure)
            "is_typed_by": [...],           # IfcRelDefinesByType            (inv: IsTypedBy)
            "psets": [...],                 # IfcRelDefinesByProperties      (inv: IsDefinedBy)
            "materials": [...],             # IfcRelAssociatesMaterial       (inv: HasAssociations filtrado)
            "voids": [...],                 # IfcRelVoidsElement             (inv: HasOpenings)
            "fills": [...],                 # IfcRelFillsElement             (inv: FillsVoids)
            "connections": [...],           # IfcRelConnectsPathElements     (inv: ConnectedTo / ConnectedFrom)
            "space_boundaries": [...],      # IfcRelSpaceBoundary            (inv: ProvidesBoundaries / BoundedBy)
            "classifications": [...],       # IfcRelAssociatesClassification (inv: HasAssociations filtrado)
        }

    [S4·L] El acceso a estos inverse attributes es el "Santo Grial" de
    IfcOpenShell — todo el modelo navega a través de ellos. Idem para
    los descendientes (descomposición): inv `IsDecomposedBy` y `Decomposes`.
    """
    raise NotImplementedError("S4·L: usar inverse attributes para navegar")


# =============================================================================
# 9. VALIDACIONES DE COHERENCIA (Bloque B §1.6, §6)
# =============================================================================

def validate_doors_have_openings(model: "IfcFile") -> list[dict]:
    """
    Reporta IfcDoor / IfcWindow que NO tienen IfcRelFillsElement asociada
    (anomalía: puerta o ventana "flotante").

    Algoritmo:
        anomalies = []
        for door in model.by_type("IfcDoor") + model.by_type("IfcWindow"):
            if not door.FillsVoids:   # inverse attr
                anomalies.append({"id": door.id(), "guid": door.GlobalId, ...})
        return anomalies

    [S4·L] En FZK-Haus: hay 5 doors + 11 windows = 16 carpinterías
    y exactamente 16 IfcRelFillsElement → debe devolver lista vacía.
    """
    raise NotImplementedError("S4·L: validar inverse FillsVoids")


def validate_unique_project(model: "IfcFile") -> None:
    """
    Comprueba la invariante 'un solo IfcProject por fichero'.

    [S4·L]:
        projects = model.by_type("IfcProject")
        assert len(projects) == 1, f"Esperado 1 IfcProject, encontrados {len(projects)}"
    """
    raise NotImplementedError("S4·L: aserción de unicidad IfcProject")


# =============================================================================
# 10. ENTRY POINT
# =============================================================================

def main(argv: list[str]) -> int:
    """
    Entry point CLI.

    Uso:
        python scripts/s3l_ifc_inspect.py [ruta_al_ifc]

    En S3·L (hoy) ejecuta solo verify_sha256() + imprime "OK, listo para S4·L".
    En S4·L se rellena con las 9 funciones de arriba.
    """
    if len(argv) > 1:
        ifc_path = Path(argv[1])
    else:
        ifc_path = DEFAULT_IFC_PATH

    print(f"[S3·L] Inspector IFC v0.1 (Nivel 2 - pseudocódigo)")
    print(f"[S3·L] Fichero objetivo: {ifc_path}")

    try:
        verify_sha256(ifc_path)
        print(f"[S3·L] ✓ SHA-256 verificado: {EXPECTED_SHA256}")
    except (FileNotFoundError, ValueError) as e:
        print(f"[S3·L] ✗ Error: {e}", file=sys.stderr)
        return 1

    print(f"[S3·L] ✓ Listo para implementación real en S4·L")
    print(f"[S3·L]   Funciones pendientes:")
    pending = [
        "open_ifc()",
        "report_header()",
        "walk_spatial_pyramid()",
        "list_elements_per_storey()",
        "count_physical_elements()",
        "count_relationships()",
        "explain_entity()",
        "validate_doors_have_openings()",
        "validate_unique_project()",
    ]
    for p in pending:
        print(f"[S3·L]    - {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
