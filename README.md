# openbim-12w

Repositorio de trabajo del plan formativo **OpenBIM 12 semanas** (11/05/2026 – 01/08/2026).

> Syllabus completo: ver [`openbim_syllabus_12_semanas.md`](../openbim_syllabus_12_semanas.md) en el workspace.

## Estructura

```
openbim-12w/
├── models/      # IFC propios (E5, FINAL) y de muestra
├── ids/         # Especificaciones IDS por entregable
├── scripts/     # Python: queries, builder, validator, BCF
├── bcf/         # .bcfzip generados
├── reports/     # Validaciones (HTML, PDF, JSON)
├── docs/        # Glosario, BEP, mapas IFC, CDE workflow
├── final/       # Proyecto integrador E12
└── .github/
    └── workflows/
        └── ifc-ci.yml   # CI: ifctester en push a models/
```

## Setup local (hacer 1 vez antes de la S1)

```bash
# 1. Crear entorno
conda create -n openbim python=3.12 -y
conda activate openbim

# 2. Instalar IfcOpenShell (incluye ifctester y bcf)
conda install -c ifcopenshell -c conda-forge ifcopenshell -y

# 3. Dependencias adicionales
pip install -r requirements.txt

# 4. Smoke test
python scripts/00_smoke_test.py
```

Adicionalmente, instalar [Bonsai](https://bonsaibim.org) sobre Blender 4.x (visualización de IFC y panel BCF).

## Recursos clave

- [IFC 4.3.2 docs](https://ifc43-docs.standards.buildingsmart.org)
- [IfcOpenShell docs](https://docs.ifcopenshell.org)
- [IDS v1.0 spec](https://github.com/buildingSMART/IDS/releases/tag/v1.0.0)
- [IFC Validation Service](https://www.buildingsmart.org/users/services/validation-service/)
- [Sample IFC files](https://github.com/buildingSMART/Sample-Test-Files)

## Hoja de ruta de entregables

| ID  | Semana | Entregable                          | Carpeta              |
| --- | ------ | ----------------------------------- | -------------------- |
| E1  | 1      | Glosario ISO 19650                  | `docs/`              |
| E2  | 2      | BEP simplificado                    | `docs/`              |
| E3  | 3      | Mapa de entidades IFC               | `docs/`              |
| E4  | 4      | Notebook de auditoría               | `scripts/`           |
| E5  | 5      | Mini-house IFC por código           | `models/`,`scripts/` |
| E6  | 6      | Validador IFC propio (CLI)          | `scripts/validator/` |
| E7  | 7      | Primer IDS                          | `ids/`               |
| E8  | 8      | IDS de proyecto + reporte           | `ids/`,`reports/`    |
| E9  | 9      | Pipeline CI verde                   | `.github/`           |
| E10 | 10     | BCF programático                    | `bcf/`               |
| E11 | 11     | Workflow CDE documentado            | `docs/`              |
| E12 | 12     | **Proyecto integrador final**       | `final/`             |

## Convenciones

- Commits en inglés, prefijos: `feat:`, `fix:`, `docs:`, `test:`, `ci:`.
- Branches: `wXX/<entregable>` (ej. `w06/validator`).
- Naming IFC siguiendo ISO 19650: `<Proyecto>-<Disciplina>-<Zona>-<Nivel>-<Tipo>-<Estado>.ifc`.
