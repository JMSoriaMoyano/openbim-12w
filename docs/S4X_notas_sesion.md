# S4·X · Notas de sesión

**Sesión:** S4·X · Lab IfcOpenShell: lectura y consultas avanzadas
**Fecha:** Miércoles 03/06/2026
**Duración aprox:** 07:00 – 14:45 CEST (en bloques no continuos)
**Repo:** `openbim-12w` · commits del día: 5 (`b0dd6cb` → `837d808`)
**Próximo hito:** E4 · cierre sábado 06/06/2026

---

## 1. Bloques ejecutados

| Bloque | SHA | Contenido | Estado |
|---|---|---|---|
| A | `b0dd6cb` | Refactor: `scripts/_ifc_helpers.py` extraído + `MODELS_DIR` constante + `.gitignore` con excepción `*_baseline.json` + rename `S4L_psets_muro15042.json` → `_baseline.json` | Cerrado |
| A | `7f71c62` | Commit vacío de etiquetado del rename (deuda menor de proceso documentada) | Cerrado |
| B | `d4c1614` | `scripts/s4x_ifc_lab.py` v0.1 con 3 consultas core (`bytype`, `spatial`, `missing`) + flag `--out` opcional + baseline `out/s4x_missing_firerating_baseline.json` | Cerrado |
| C | `e8001e8` | `notebooks/S4X_lab_consultas.py` py-percent con 5 celdas de código + 6 markdown + resolución robusta de paths (vale en CLI, VS Code Interactive y Jupyter) | Cerrado |
| D | `837d808` | `docs/EIR_NEXUM_PBSA_v0.1.md` (draft interno) + `docs/S4X_consultas_requisitos.md` (mapeo consulta↔requisito ISO 19650) | Cerrado |
| E | — | Notas de sesión (este documento) + commit final | En curso |

## 2. Hallazgos técnicos confirmados

### Hallazgo A · ThermalTransmittance cumple en FZK-Haus
- Auditoría: `Pset_WallCommon.ThermalTransmittance` sobre los 13 `IfcWallStandardCase`
- Resultado: **100% compliance** (`sample_value = 1.5` W/m²K)
- Lectura: ArchiCAD popula este campo desde la plantilla por defecto. Buena base.

### Hallazgo B · FireRating incumple sistemáticamente
- Auditoría: `Pset_WallCommon.FireRating` sobre los 13 `IfcWallStandardCase`
- Resultado: **0% compliance** — 13/13 muros en `absent_prop`
- Distribución: 5 muros internos (Wand-Int-ERDG-*) + 5 externos planta baja + 3 externos planta alta = 13
- Lectura: confirma quirúrgicamente el hallazgo S4·L #2 (Pset_WallCommon prácticamente vacío)
- Evidencia versionada: `out/s4x_missing_firerating_baseline.json` (commit `d4c1614`)
- **Esta es la evidencia LOIN central para E4 sábado 06/06**

### Hallazgo C · Estructura espacial sin huérfanos reales
- Auditoría: `query_spatial_containment` sobre FZK-Haus
- Conteos: 1 site · 1 building · 2 storeys · 7 spaces · 102 IfcElement
- `orphans_count`: 20 (aparente)
- **Falso positivo:** los 20 son 17 `IfcOpeningElement` + 3 `IfcVirtualElement` — comportamiento IFC correcto, no son red flags
- Lectura: el modelo está bien estructurado espacialmente; la función necesita refinarse en v0.2 (ver deuda 5.1)

### Hallazgo D · ArchiCAD ignora Pset_DoorCommon también (inferido, sin auditar)
- Razonamiento: si `Pset_WallCommon` solo trae 1 propiedad de 11 posibles (S4·L hallazgo #2 + S4·X hallazgo B), por simetría con la lógica de plantillas ArchiCAD, `Pset_DoorCommon`, `Pset_WindowCommon` y `Pset_SlabCommon` probablemente sufren la misma carencia
- Auditoría pendiente: lanzar `query_missing_property` sobre las 11 propiedades obligatorias EIR de Door/Window/Slab antes de E4
- Impacto E4: este hallazgo escala la conclusión de "muros incumplen" a "el modelo en su conjunto requiere intervención de plantilla en autoría"

### Hallazgo E · El EIR como capa estratégica (no técnico)
- Redactar `EIR_NEXUM_PBSA_v0.1.md` reveló que el repo necesita un **doble eje narrativo**: técnico (scripts) y estratégico (contrato con proveedores)
- Sin el EIR, las consultas son herramientas sueltas; con EIR, son un sistema de validación auditable trazable a ISO 19650 y CTE
- Decisión: a partir de S5·L, cada nueva consulta debe citar explícitamente qué fila del EIR verifica

## 3. Decisiones técnicas y de proceso

### 3.1 · Política `out/*.json` resuelta (opción B)
- `.gitignore` ignora `out/*.json` por defecto
- Excepción: `out/*_baseline.json` SÍ se versiona (evidencia LOIN para entregables Ex)
- Convención de naming: cualquier evidencia que sea referencia estable se renombra a `<nombre>_baseline.json` antes de commit
- Aprendizaje operativo: `git mv` solo funciona en ficheros ya trackeados; para promocionar un fichero gitignored a baseline hay que usar `move` (filesystem) + `git add` directo

### 3.2 · Notebook formato py-percent (no .ipynb)
- Decidido por: diff-friendly en Git, sin metadata ruidosa, ejecutable como `.py` plano si Jupyter no está disponible
- Compatible: VS Code Interactive (celdas `# %%`), Jupyter (vía `jupytext --to ipynb`), Python normal (ejecución secuencial)
- Resolución de paths robusta: usa `Path(__file__).resolve().parent` con fallback a `Path.cwd()` — funciona desde cualquier CWD
- Pre-requisito documentado: extensión Microsoft Jupyter en VS Code (las de Python solas no bastan)

### 3.3 · Pset custom `Pset_NEXUM_PBSA`
- Convención de naming: `Pset_<ORG>_<TIPOLOGIA>` (ej. `Pset_NEXUM_PBSA`, futuro `Pset_NEXUM_SENIOR`, etc.)
- 8 propiedades en v0.1: `RoomType`, `BedCount`, `FurnitureLevel`, `NetUsableArea_PBSA`, `HasPrivateBathroom`, `ClusterId`, `OperatorReference`, `AccessibilityCompliant`
- Justificación: los Psets buildingSMART estándar no cubren atributos específicos PBSA (tipología habitación, cluster, área útil según estándar operador). Los Psets custom son **práctica estándar** en EIRs maduros y permiten auditoría con las mismas consultas
- A documentar en S7·L cuando llegue IDS: cómo declarar Pset custom en XML estándar buildingSMART

### 3.4 · EIR marcado como draft interno v0.1
- Estado: documento interno NEXUM, NO contractual
- Falta para v1.0 contractual: revisión BIM Manager NEXUM, alineación con operadores reales (Resa/Yugo/Greystar), ampliación a MEP y estructura (v0.2), validación con un proyecto piloto cerrado
- Roadmap explícito en el propio EIR (sección 10)

## 4. Hallazgos heredados validados / refinados

| Hallazgo S4·L | Estado S4·X |
|---|---|
| #1 · 6 clases invisibles para E3 | Confirmado parcialmente (3 `IfcVirtualElement` detectados como "huérfanos" en spatial) |
| #2 · `Pset_WallCommon` casi vacío | **Confirmado con métrica:** FireRating 0%, ThermalTransmittance 100%. Pset existe pero con solo 1 de 11 propiedades posibles |
| #3 · Vendor Psets con info canónica disfrazada | No tocado hoy (pendiente extracción canónica en S5·L) |
| #4 · BaseQuantities mal nombrado | No tocado (pendiente refactor de naming en S5·L) |
| #5 · ArchiCAD no usa Type PropertySets | Implícitamente confirmado (todas las auditorías hoy van por instance_psets sin fallback útil a type_psets) |
| #6 · Doble timestamp autoría | No relevante a S4·X (sin cambios) |
| #7 · `owning_user "Nicht definiert"` | Documentado en EIR sección 8 como incumplimiento de identidad y autoría a verificar manualmente |
| #8 · MVD declara 3 ViewDefinitions | No relevante a S4·X (sin cambios) |

## 5. Deudas técnicas documentadas

### 5.1 · `query_spatial_containment` v0.2 — excluir Opening y Virtual
- **Problema:** 20 falsos positivos sistemáticos en FZK-Haus (17 `IfcOpeningElement` + 3 `IfcVirtualElement`)
- **Solución v0.2:** excluir explícitamente esas dos clases antes de evaluar contención, y ampliar la excepción `FillsVoids` a `VoidsElements`
- **Cuándo:** S5·L o S6·L (no bloquea E4)

### 5.2 · Orquestador EIR completo
- **Problema:** auditar las 70+ propiedades del EIR exige orquestar 70+ llamadas a `query_missing_property` manualmente
- **Solución:** wrapper `audit_eir(model, eir_yaml_path)` que lea una representación YAML/JSON del EIR y ejecute la matriz completa, devolviendo un compliance report agregado
- **Cuándo:** S6·L (sesión dedicada a calidad)
- **Pre-requisito:** representar el EIR en formato máquina-legible (no markdown). Posible formato: YAML con esquema definido. Decisión pendiente de S6·L o S7·L (IDS resolvería esto de forma estándar)

### 5.3 · Commit vacío `7f71c62` (deuda menor de proceso)
- **Problema:** un commit etiqueta y nada más, ruido en history
- **Mitigación:** para próximas sesiones, agrupar rename + cambios en un único commit con mensaje compuesto
- **No se reescribe history:** ya está pusheado a `main`, no merece la pena

### 5.4 · Validación semántica de valores (no solo presencia)
- **Problema:** `query_missing_property` solo detecta ausencia. Un `FireRating = "blah"` cuenta como presente
- **Solución:** validación con IDS 1.0 (regex, enums, rangos)
- **Cuándo:** S7·L (sesión dedicada)

## 6. Aprendizajes del proceso

### 6.1 · Configuración VS Code para Python científico
- 4 extensiones Microsoft son suficientes: **Python**, **Pylance**, **Python Debugger**, **Python Environments**
- Para notebooks py-percent o `.ipynb`: añadir **Jupyter** (Microsoft) — sus dependencias (Cell Tags, Notebook Renderers, Keymap) se instalan automáticamente
- Crítico: abrir VS Code con `code .` desde la raíz del repo para que CWD y selector de intérprete funcionen bien
- Selección de intérprete: `Ctrl+Shift+P` → "Python: Select Interpreter" → elegir el del `.venv` (no el Python global)

### 6.2 · Pitfalls Windows CMD encontrados
- Continuación de línea: `^` (no `\` como en bash)
- `git mv` falla si el fichero está gitignored — usar `move` + `git add`
- LF vs CRLF: warnings normales al añadir ficheros creados con LF (no afectan al commit, Git los convierte transparentemente)

### 6.3 · Diseño de notebooks reproducibles
- `Path(__file__).resolve().parent` es más robusto que `Path.cwd()` porque sobrevive a CWD arbitrarios
- Imprimir `REPO_ROOT` y `SCRIPTS_DIR` en la celda Setup ahorra ~30 minutos de debugging cuando algo falla en una máquina nueva
- Las celdas markdown (`# %% [markdown]`) son rótulos sin output; las de código (`# %%`) son las únicas que ejecutan algo

### 6.4 · Estrategia documental
- Separar **doc operativo** (cómo usar las consultas) de **doc contractual** (qué exigimos al proveedor) facilita ambos lados
- El doc operativo puede cambiar cada sesión sin afectar al EIR
- El EIR cambia con versionado explícito y changelog

## 7. Preparación de E4 (sábado 06/06)

### Lo que ya tenemos para E4
- **3 consultas funcionales** validadas sobre FZK-Haus
- **1 evidencia versionada** (FireRating offenders baseline)
- **2 documentos estratégicos** (EIR draft + mapeo)
- **1 notebook reproducible** que demuestra el workflow end-to-end

### Lo que falta del lado consulta (1 hora estimada)
- Lanzar `query_missing_property` para 5-7 propiedades EIR más sobre `IfcWallStandardCase` (AcousticRating, LoadBearing, IsExternal, Compartmentation, Reference)
- Lanzar `query_missing_property` sobre `IfcDoor` (las 6 propiedades obligatorias del EIR)
- Lanzar `query_missing_property` sobre `IfcWindow` (las 4 propiedades obligatorias del EIR)
- Total estimado: ~15 auditorías → 15 JSON ad-hoc → promocionar 3-4 a baseline

### Lo que falta del lado evidencia (2 horas estimadas)
- Doc E4 final que sintetice: contexto, método, evidencias, conclusiones, recomendaciones al proveedor
- Tabla resumen compliance matrix (filas: propiedad EIR, columnas: tipo IFC, celdas: compliance_pct)
- Recomendación al proveedor: "actualice su plantilla ArchiCAD para poblar las N propiedades faltantes antes del siguiente entregable"

### Lo que NO toca E4
- IDS formal (S7·L)
- Orquestador automatizado (S6·L)
- Auditoría MEP y estructura (v0.2 EIR)

## 8. Hoja de ruta encadenada

| Hito | Fecha | Contenido principal |
|---|---|---|
| **S4·S** | Sáb 06/06 | Cierre E4 — auditoría LOIN completa sobre FZK-Haus, doc síntesis, etiqueta `e4-closed` |
| S5·L | Lun 08/06 | IfcOpenShell: geometría — bounding boxes, holguras, alturas libres |
| S5·X | Mié 10/06 | Lab geometría — intersecciones espaciales |
| S5·S | Sáb 13/06 | E5 |
| S6·L | Lun 15/06 | Calidad — orquestador EIR completo (deuda 5.2) |
| S7·L | Lun 22/06 | IDS 1.0 — traducir EIR a XML estándar (deuda 5.4) |
| S8·L | Lun 29/06 | `ifctester` Python — ejecución de IDS desde CLI |

## 9. Estado del repositorio al cierre

```
openbim-12w/
├── .gitignore                            (v2 · S4·X · con excepciones baseline)
├── docs/
│   ├── EIR_NEXUM_PBSA_v0.1.md            (NUEVO S4·X · 253 líneas)
│   ├── S4L_notas_sesion.md
│   ├── S4X_consultas_requisitos.md       (NUEVO S4·X · 201 líneas)
│   ├── S4X_notas_sesion.md               (ESTE FICHERO)
│   └── ... (notas previas E1-E3)
├── notebooks/                            (NUEVA CARPETA S4·X)
│   └── S4X_lab_consultas.py              (NUEVO · 5 celdas py-percent)
├── out/
│   ├── S4L_psets_muro15042_baseline.json (renombrado S4·X · Bloque A)
│   └── s4x_missing_firerating_baseline.json (NUEVO S4·X · Bloque B)
├── scripts/
│   ├── _ifc_helpers.py                   (NUEVO S4·X · 123 líneas)
│   ├── s3l_ifc_inspect.py
│   ├── s4l_ifc_query.py                  (refactor S4·X · v0.5)
│   └── s4x_ifc_lab.py                    (NUEVO S4·X · 486 líneas)
└── ... (resto sin cambios)
```

## 10. Métricas del día

- Commits en `main`: 5 (`b0dd6cb`, `7f71c62`, `d4c1614`, `e8001e8`, `837d808`)
- Líneas nuevas de Python: ~610 (`_ifc_helpers.py` + `s4x_ifc_lab.py` + `S4X_lab_consultas.py`)
- Líneas nuevas de documentación: ~660 (`EIR_NEXUM_PBSA_v0.1.md` + `S4X_consultas_requisitos.md` + este fichero estimado)
- Funciones públicas nuevas: 3 (`query_by_type_with_psets`, `query_spatial_containment`, `query_missing_property`)
- Helpers compartibles extraídos: 4 (`load_ifc`, `report_header`, `resolve_model_path`, `get_type_object`)
- Evidencias LOIN versionadas: 1 nueva (firerating baseline) + 1 renombrada (psets muro 15042)
- Documentos estratégicos creados: 1 EIR + 1 mapeo
- Hallazgos confirmados con métrica: 2 (Thermal 100%, Fire 0%)
- Hallazgos nuevos: 2 (E sobre estrategia, D inferido sobre Door/Window/Slab)
- Deudas técnicas documentadas: 4 (sección 5)

---

**Próximo punto de contacto:** Sábado 06/06 a las 05:00 UTC (07:00 CEST) — briefing automático antes de S4·S (cierre E4).
