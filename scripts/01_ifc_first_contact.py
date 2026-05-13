"""
01_ifc_first_contact.py
=======================
S1·X · Lab: primer contacto con IFC + IfcOpenShell

Procesa N ficheros IFC y para cada uno reporta:
  1. Esquema IFC (IFC2X3, IFC4, IFC4X3, ...)
  2. Cardinalidad de la jerarquia espacial (Project/Site/Building/Storey/Space)
  3. Conteos de las 10 clases mas representativas
  4. Resumen de tipos (capa de catalogo)
  5. Top 5 clases por numero de instancias (descubrimiento)

Uso:
    conda activate openbim
    cd C:\\Users\\jmsor\\OpenBIM\\openbim-12w
    python scripts/01_ifc_first_contact.py <ifc1> [ifc2] [ifc3] ...

Salida:
  - Por consola: tablas legibles por fichero
  - En reports/S1X_first_contact.json: datos crudos para el commit
  - En reports/S1X_first_contact.md: tabla comparativa lista para el docs/

Autor: Jose M. Soria - Plan OpenBIM 12 semanas, S1
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from datetime import datetime

try:
    import ifcopenshell
except ImportError:
    sys.exit(
        "ERROR: ifcopenshell no esta instalado. Activa el entorno con:\n"
        "  conda activate openbim\n"
        "y reintenta."
    )


# Las 10 clases que mas informacion dan en un primer contacto.
# Cubren jerarquia espacial, elementos fisicos comunes y patron de tipos.
CLASES_OBJETIVO = [
    "IfcProject",
    "IfcSite",
    "IfcBuilding",
    "IfcBuildingStorey",
    "IfcSpace",
    "IfcWall",
    "IfcSlab",
    "IfcWindow",
    "IfcDoor",
    "IfcBuildingElementProxy",
]


def analizar_ifc(ruta: Path) -> dict:
    """Abre un IFC y extrae el resumen estructural."""
    print(f"\n{'=' * 70}\nAnalizando: {ruta.name}\n{'=' * 70}")

    model = ifcopenshell.open(str(ruta))

    # 1. Esquema
    esquema = model.schema  # ej. 'IFC4', 'IFC4X3_ADD2'
    print(f"  Esquema IFC: {esquema}")

    # 2. Jerarquia espacial (cardinalidad)
    jerarquia = {
        "IfcProject": len(model.by_type("IfcProject")),
        "IfcSite": len(model.by_type("IfcSite")),
        "IfcBuilding": len(model.by_type("IfcBuilding")),
        "IfcBuildingStorey": len(model.by_type("IfcBuildingStorey")),
        "IfcSpace": len(model.by_type("IfcSpace")),
    }

    print(f"\n  Jerarquia espacial:")
    for clase, n in jerarquia.items():
        marca = "  OK" if (clase != "IfcProject" or n == 1) else "  ALERTA"
        print(f"    {clase:25s} : {n:4d} {marca if n else ''}")

    # 3. Conteos de las 10 clases objetivo
    conteos_objetivo = {clase: len(model.by_type(clase)) for clase in CLASES_OBJETIVO}

    print(f"\n  Conteos de las 10 clases objetivo:")
    for clase, n in conteos_objetivo.items():
        print(f"    {clase:30s} : {n:5d}")

    # 4. Tipos (capa de catalogo)
    tipos = {
        "IfcWallType": len(model.by_type("IfcWallType")),
        "IfcSlabType": len(model.by_type("IfcSlabType")),
        "IfcWindowType": len(model.by_type("IfcWindowType")),
        "IfcDoorType": len(model.by_type("IfcDoorType")),
        "IfcSpaceType": len(model.by_type("IfcSpaceType")),
    }
    n_tipos_total = len(model.by_type("IfcTypeProduct"))

    print(f"\n  Capa de tipos (IfcTypeProduct total: {n_tipos_total}):")
    for tipo, n in tipos.items():
        print(f"    {tipo:25s} : {n:4d}")

    # 5. Top 5 clases por instancias (descubrimiento)
    # Recorremos todas las instancias y agrupamos por su clase IFC
    contador = Counter()
    for inst in model:
        contador[inst.is_a()] += 1
    top5 = contador.most_common(5)

    print(f"\n  Top 5 clases mas frecuentes en el fichero:")
    for clase, n in top5:
        print(f"    {clase:35s} : {n:6d}")

    # 6. Nombre del proyecto (atributo Name del IfcProject)
    proyectos = model.by_type("IfcProject")
    nombre_proyecto = proyectos[0].Name if proyectos else "(sin nombre)"

    # 7. Total de entidades (compatibilidad IfcOpenShell 0.7 y 0.8)
    # En 0.8 el objeto file no soporta len(); se usa el contador acumulado
    total_entidades = sum(contador.values())

    print(f"\n  Nombre del proyecto: {nombre_proyecto!r}")
    print(f"  Total de entidades IFC: {total_entidades}")

    return {
        "fichero": ruta.name,
        "ruta": str(ruta),
        "esquema": esquema,
        "nombre_proyecto": nombre_proyecto,
        "total_entidades": total_entidades,
        "jerarquia_espacial": jerarquia,
        "conteos_objetivo": conteos_objetivo,
        "tipos": tipos,
        "ifctypeproduct_total": n_tipos_total,
        "top5_clases": top5,
    }


def generar_markdown(resultados: list[dict], destino: Path) -> None:
    """Genera tabla comparativa Markdown para el docs/."""
    lineas = [
        "# S1·X · Lab: primer contacto IFC + IfcOpenShell",
        "",
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Ficheros analizados: {len(resultados)}",
        "",
        "## Resumen estructural",
        "",
        "| Fichero | Esquema | Entidades | Project | Site | Building | Storey | Space |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in resultados:
        j = r["jerarquia_espacial"]
        lineas.append(
            f"| `{r['fichero']}` | {r['esquema']} | {r['total_entidades']} | "
            f"{j['IfcProject']} | {j['IfcSite']} | {j['IfcBuilding']} | "
            f"{j['IfcBuildingStorey']} | {j['IfcSpace']} |"
        )

    lineas += [
        "",
        "## Conteos de las 10 clases objetivo",
        "",
        "| Clase IFC | " + " | ".join(r["fichero"] for r in resultados) + " |",
        "|---" * (len(resultados) + 1) + "|",
    ]
    for clase in CLASES_OBJETIVO:
        fila = f"| `{clase}` |"
        for r in resultados:
            fila += f" {r['conteos_objetivo'][clase]} |"
        lineas.append(fila)

    lineas += [
        "",
        "## Top 5 clases mas frecuentes por fichero",
        "",
    ]
    for r in resultados:
        lineas.append(f"### `{r['fichero']}`")
        lineas.append("")
        lineas.append("| Clase | Instancias |")
        lineas.append("|---|---:|")
        for clase, n in r["top5_clases"]:
            lineas.append(f"| `{clase}` | {n} |")
        lineas.append("")

    lineas += [
        "## Observaciones",
        "",
        "_Anadir aqui 3 observaciones manuales tras revisar los resultados:_",
        "",
        "1. ",
        "2. ",
        "3. ",
        "",
        "## Dudas para resolver",
        "",
        "1. ",
        "2. ",
        "3. ",
        "",
    ]

    destino.write_text("\n".join(lineas), encoding="utf-8")
    print(f"\nMarkdown generado: {destino}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(
            "\nERROR: indica al menos un fichero IFC.\n"
            "Ejemplo:\n"
            "  python scripts/01_ifc_first_contact.py "
            "C:\\Users\\jmsor\\OpenBIM\\Sample-Test-Files\\IFC4.0\\xxx.ifc"
        )

    rutas = [Path(p) for p in sys.argv[1:]]
    for ruta in rutas:
        if not ruta.is_file():
            sys.exit(f"ERROR: no existe el fichero: {ruta}")

    resultados = [analizar_ifc(r) for r in rutas]

    # Persistencia
    raiz_repo = Path(__file__).resolve().parent.parent
    carpeta_reports = raiz_repo / "reports"
    carpeta_reports.mkdir(exist_ok=True)
    carpeta_docs = raiz_repo / "docs"
    carpeta_docs.mkdir(exist_ok=True)

    json_destino = carpeta_reports / "S1X_first_contact.json"
    json_destino.write_text(
        json.dumps(resultados, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nJSON guardado: {json_destino}")

    md_destino = carpeta_docs / "S1X_lab_ifc_primer_contacto.md"
    generar_markdown(resultados, md_destino)

    print("\nLab completado. Siguiente paso: revisar reports + docs y commitear.")


if __name__ == "__main__":
    main()
