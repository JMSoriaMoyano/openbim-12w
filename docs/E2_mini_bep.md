# E2 · Mini-BEP — Proyecto Integrador Can Cabassa PBSA

> **Entregable E2 · Semana 2 · Cierre sábado 23/05/2026**
> BIM Execution Plan respondiendo al EIR del proyecto integrador.
> Versión: 0.4 · Estado: BORRADOR · Tipo: **pre-appointment** (oferta)
> Lead appointed party: _(equipo ficticio — completar)_ · Fecha: 18/05/2026

## Document Revision History

| Rev | Fecha | Sección | Descripción |
|---|---|---|---|
| 0.1 | 17/05/2026 | Todo el documento | Andamio inicial generado |
| 0.2 | 18/05/2026 | Todo el documento | Particularización a Can Cabassa PBSA tras S2·L (4 hitos, ARQ+EST+MEP+URB, GuBIMClass, Speckle como CDE) |
| 0.3 | 18/05/2026 | §4.1 (nueva) | Formalización de MVD aplicable y procedimientos de verificación |
| 0.4 | 18/05/2026 | §4.1.6 (nueva) | Configuración estandarizada de exportación IFC desde Revit + archivo `revit_ifc_export_config.json` |

---

## 0. Resumen ejecutivo

Breve párrafo (5–8 líneas) que explique cómo el equipo va a cubrir el EIR: enfoque BIM, herramientas, federación, calidad. No es un sumario, es una declaración de intenciones técnica.

---

## 1. Información del proyecto y del encargo

| Campo | Valor |
|---|---|
| Proyecto | Can Cabassa PBSA (versión didáctica plan formativo OpenBIM 12w) |
| Appointing party | NEXUM Developments |
| Lead appointed party | _(equipo — completar)_ |
| Appointed parties | ARQ, EST, MEP, URB (4 disciplinas) |
| Referencia del EIR | E2 · EIR Draft v0.2 |
| Estándares aplicables | ISO 19650-1/2, EN 17412-1, IFC4.3, IDS v1.0, BCF 3.0, GuBIMClass |
| Sistema de coordenadas | ETRS89 / UTM 31N |

---

## 2. Objetivos y usos BIM acordados

Trazabilidad uno-a-uno con la tabla §1 del EIR. Para cada uso, declarar la **estrategia técnica** que lo materializa.

| Uso EIR | Estrategia BIM propuesta | Herramienta principal | Responsable |
|---|---|---|---|
| U1 | Federación semanal en CDE + clash detection automatizado | _(p.ej. Solibri / BIMcollab Zoom)_ | Information manager |
| U2 | Modelos ejecutivos con clasificación y QTO scripted | _(p.ej. Revit + IfcOpenShell)_ | Disciplinas |
| U3 | Validación normativa con IDS específico CTE | _(ifctester)_ | QA/QC BIM |
| U4 | Plantilla IFC4.3 para FM | _(definir)_ | FM lead |

---

## 3. Equipo y matriz de responsabilidades

### 3.1 Organigrama del encargo (ISO 19650)

```
Appointing party (NEXUM Developments)
        │
Lead appointed party — Project Information Manager
        │
        ├── Appointed party · Arquitectura (ARQ)
        ├── Appointed party · Estructuras (EST)
        ├── Appointed party · Instalaciones (MEP)
        └── Appointed party · Urbanización (URB)
```

### 3.2 Matriz RACI (resumen)

R = Responsible · A = Accountable · C = Consulted · I = Informed

| Actividad | NEXUM | Lead AP | ARQ | EST | MEP | URB |
|---|---|---|---|---|---|---|
| Aprobación EIR | A | C | I | I | I | I |
| Redacción BEP | C | A/R | C | C | C | C |
| MIDP | A | R | C | C | C | C |
| TIDP por disciplina | I | A | R | R | R | R |
| Federación semanal | I | A/R | C | C | C | C |
| Validación IDS | A | R | C | C | C | C |
| Gestión BCF | I | A/R | R | R | R | R |
| Geo-referenciación | I | A | C | C | C | R |

### 3.3 Responsibility Matrix (por contenedor de información)

Véase MIDP en §5 — la columna `Autor (AP)` actúa como Responsibility Matrix simplificada.

---

## 4. Estrategia de federación

- **Modelo federado:** consolidación semanal de los modelos disciplinares en IFC4.3.
- **Sistema de coordenadas:** **ETRS89 / UTM 31N**, georreferenciación obligatoria desde H1 por inclusión de urbanización.
- **Origen del proyecto:** punto base definido por URB y compartido con resto de disciplinas vía `IfcMapConversion`.
- **Subdivisión:** por disciplina (ARQ, EST, MEP, URB) + por edificio/nivel cuando supere 200 MB.
- **Política de versiones:** semver simple `vX.Y` por publicación al CDE.
- **Naming de federado:** `CANCABASSA-NEXUM-FED-<Hito>-<YYYYMMDD>.ifc` siguiendo ISO 19650-2 §11.

### 4.1 MVD aplicable y procedimientos de verificación

Esta sección responde a la exigencia del EIR §3.1 y detalla cómo el Lead Appointed Party garantizará el cumplimiento de los MVD admitidos.

#### 4.1.1 MVD operativo por disciplina y hito

| Disciplina | H1 (Anteproyecto) | H2 (Básico) | H3 (Ejecutivo) | H4 (As-built) |
|---|---|---|---|---|
| ARQ | IFC4 Add2 RV | IFC4 Add2 RV | IFC4 Add2 RV | IFC4 Add2 RV |
| EST | — | IFC4 Add2 RV | IFC4 Add2 RV | IFC4 Add2 RV |
| MEP | — | — | IFC4 Add2 RV | IFC4 Add2 RV |
| URB | IFC4.3 RV | IFC4.3 RV | IFC4.3 RV | IFC4.3 RV |
| Federado | IFC4 Add2 RV (referenciando URB en IFC4.3 RV) | idem | idem | idem |

**Nota sobre federación cruzada IFC4 / IFC4.3:** dado que la urbanización se entrega en IFC4.3 y el resto de disciplinas en IFC4 Add2, el federado se construye mediante **referencia externa** (no fusión de esquemas). El visor/coordinador debe soportar ambos esquemas simultáneamente (Solibri 9.13+ y BIMcollab Zoom 9.0+ lo soportan).

#### 4.1.2 Intercambios bilaterales en DTV (excepciones autorizadas)

Se autorizan los siguientes intercambios DTV durante el desarrollo, registrados aquí como excepción al EIR §3.1.2:

| ID | Origen | Destino | Propósito | Smoke test |
|---|---|---|---|---|
| DTV-01 | AP-ARQ (Revit) | AP-EST (Tekla) | Transferencia de huecos estructurales en paredes y forjados con parámetros editables | Pendiente — ejecutar en semana de movilización |
| DTV-02 | AP-ARQ (Revit) | AP-MEP (Revit MEP) | Coordinación de patinillos y reservas paramétricas | Mismo entorno Revit; smoke test sumario |

Cualquier intercambio adicional en DTV requiere modificación formal de esta tabla y aprobación del Lead AP.

#### 4.1.3 Pipeline de verificación previo a publicación

Antes de pasar cualquier modelo del estado `Shared` a `Published`, el Lead Appointed Party ejecuta el siguiente pipeline automatizado:

```
1. Lectura cabecera STEP → extraer FILE_DESCRIPTION.ViewDefinition
   │
   ├─ ¿Cadena coincide con MVD esperado según §4.1.1?
   │    NO → RECHAZO (criterio EIR §3.1.5)
   │    SÍ ↓
   │
2. Validación schema IFC (sintaxis + cardinalidades) → buildingSMART IFC Validation Service
   │
   ├─ ¿Pasa validación schema?
   │    NO → RECHAZO
   │    SÍ ↓
   │
3. Validación MVD (subconjunto de entidades admitidas) → Solibri rule check / ifctester parcial
   │
   ├─ ¿Entidades dentro del MVD declarado?
   │    NO → RECHAZO
   │    SÍ ↓
   │
4. Validación IDS del hito → ifctester
   │
   ├─ ¿Pasa IDS?
   │    NO → RECHAZO
   │    SÍ ↓
   │
5. Aprobación manual del Information Manager → estado Published
```

Este pipeline se materializará progresivamente durante el plan formativo: pasos 1-2 desde S5, paso 3 desde S6, paso 4 desde S8, integración CI/CD completa en S9.

#### 4.1.4 Script de verificación del paso 1 (placeholder)

Verificación estructural mínima implementable hoy con IfcOpenShell:

```python
import ifcopenshell

def check_mvd_declaration(ifc_path: str, expected: str) -> tuple[bool, str]:
    """Lee FILE_DESCRIPTION.ViewDefinition y comprueba MVD declarado."""
    model = ifcopenshell.open(ifc_path)
    header = model.wrapped_data.header.file_description.description
    declared = next((d for d in header if d.startswith("ViewDefinition")), None)
    if declared is None:
        return False, "Sin MVD declarado en cabecera"
    if expected not in declared:
        return False, f"MVD declarado {declared!r} ≠ esperado {expected!r}"
    return True, declared
```

Este script se incorporará al repositorio `openbim-12w/scripts/` durante S5 como parte del toolkit de QA/QC.

#### 4.1.5 Registro de no conformidades

Las no conformidades de MVD se registran como issues BCF 3.0 categoría `Quality Control / MVD Compliance`, con prioridad `Critical` (bloquean la publicación). El Information Manager mantiene un log mensual de no conformidades como métrica de madurez del proceso.

#### 4.1.6 Configuración estandarizada de exportación IFC desde Revit

Dado que dos de las cuatro disciplinas autoras del proyecto (AP-ARQ y AP-MEP) trabajan en Revit, se exige **una única configuración de exportación compartida** distribuida como archivo `.json` importable. Esto garantiza que ambos exporters declaren el mismo MVD, exporten los mismos Psets y apliquen las mismas reglas de mapeo.

**Archivo oficial:** `configs/revit_ifc_export_config.json` (en el repositorio del proyecto).

##### Requisitos software previos

| Componente | Versión mínima | Notas |
|---|---|---|
| Revit | 2024.2 | Estable para Reference View |
| Open Source IFC Exporter for Revit | 24.1.0 | Se actualiza independientemente de Revit — instalar vía Autodesk App Store |
| Plataforma de despliegue del config | Carpeta corporativa accesible a todas las disciplinas Revit | |

##### Procedimiento de importación

```
1. Revit → File → Export → IFC…
2. En el diálogo Export IFC, click en "Modify setup…"
3. En la columna izquierda, click en el icono "Import setup…"
4. Seleccionar configs/revit_ifc_export_config.json
5. Verificar que aparece la configuración "NEXUM_CanCabassa_IFC4_RV" en la lista
6. Click OK → Save (no Export) para conservar la configuración en el .rvt
```

##### Ajustes que NO se guardan en el JSON (límite conocido del exporter)

Los siguientes ajustes deben configurarse manualmente en cada modelo Revit y **sincronizarse al fichero central** — quedan persistidos en el `.rvt`, no en el `.json`:

| Ajuste | Dónde se configura | Valor exigido |
|---|---|---|
| **File Header Information** | Modify Setup → General → File Header Information | Rellenar Author, Organization (NEXUM Developments), Authorization según disciplina |
| **Project Address** | Modify Setup → General → Project Address | Dirección real del activo Can Cabassa |
| **Classification Settings** | Modify Setup → Property Sets → Classification Settings… | **Name: `GuBIMClass`** · Source: `https://www.gubimclass.org` · Field name: `ClassificationCode` |

##### Parámetros críticos del JSON y su justificación

| Clave | Valor | Por qué |
|---|---|---|
| `IFCVersion` | `21` | Código numérico del exporter para **IFC 4 Reference View** (cumple EIR §3.1) |
| `FileVersionDescription` | `"IFC 4 Reference View [ReferenceView_V1.2]"` | Asegura la cadena correcta en cabecera STEP |
| `ExportBaseQuantities` | `true` | Obligatorio para U2 Mediciones (genera Qto_*) |
| `ExportIFCCommonPropertySets` | `true` | Psets nativos IFC (Pset_WallCommon, etc.) — exigidos por IDS hito |
| `ExportInternalRevitPropertySets` | `false` | Evita contaminar el IFC con propiedades propias de Revit |
| `SplitWallsAndColumns` | `false` | Reference View no admite splitting por nivel; lo gestiona el coordinador |
| `UseFamilyAndTypeNameForReference` | `true` | Trazabilidad ARQ ↔ EST ↔ MEP en federación |
| `IncludeSiteElevation` | `true` | Coherencia con georreferenciación ETRS89/UTM 31N |
| `StoreIFCGUID` | `true` | GUIDs estables entre exportaciones (crítico para BCF y trazabilidad) |
| `UseTypeNameOnlyForIfcType` | `true` | Buenas prácticas BIM Corner; evita nombres compuestos en IfcType |
| `IncludeSteelElements` | `true` | Compatibilidad con AP-EST (Tekla) vía intercambios DTV |
| `ExportRoomsInView` | `true` | Necesario para U4 FM operador PBSA |
| `ExportUserDefinedPsets` | `true` | Habilita Psets personalizados GuBIMClass + CTE |
| `ExportUserDefinedPsetsFileName` | `NEXUM_GuBIMClass_UserDefinedPsets.txt` | Plantilla Pset corporativa NEXUM (entregada con el config) |
| `ExportUserDefinedParameterMapping` | `true` | Mapeo de parámetros Revit → propiedades IFC según GuBIMClass |
| `TessellationLevelOfDetail` | `0.5` | Reference View exige geometría teselada con LOD medio (peso/calidad) |
| `VisibleElementsOfCurrentView` | `true` | Exporta solo elementos de la vista 3D dedicada `IFCExport_<Disciplina>` |

##### Vista dedicada de exportación (obligatoria)

Cada disciplina Revit debe crear una vista 3D específica para exportación IFC:

- **Nombre:** `IFCExport_ARQ_H<n>` / `IFCExport_MEP_H<n>` (donde `<n>` es el hito).
- **Filtros aplicados:** ocultar copy-monitor de otras disciplinas, links no relevantes, elementos de trabajo (workplanes, reference planes, drafting views).
- **Detail level:** Fine.
- **Visual style:** Shaded.
- **Phase:** la del hito.

La vista NO se modifica durante el día a día. Se versiona como cualquier otro contenedor de información.

##### Validación del IFC exportado

Una vez exportado el IFC, **antes de subirlo al CDE en estado Shared**, el autor ejecuta como mínimo:

1. **Local:** abrir el IFC en Bonsai (Blender) o BIMcollab Zoom y verificar visualmente.
2. **Schema + MVD:** cargarlo en [buildingSMART IFC Validation Service](https://validate.buildingsmart.org/) y guardar el reporte como `<nombre_ifc>_validation_report.pdf` adjunto en el CDE.
3. **IDS del hito:** ejecutar `ifctester` con el IDS correspondiente al hito.

Los tres reportes se adjuntan al contenedor de información en el CDE como evidencia de cumplimiento.

---

## 5. MIDP — Master Information Delivery Plan (simplificado)

| ID | Contenedor de información | Disciplina | Autor (AP) | Revisor | Hito | LOIN | Estado destino |
|---|---|---|---|---|---|---|---|
| C-01 | Modelo conceptual arquitectura | ARQ | AP-ARQ | Lead AP | H1 | LOIN-H1 | Published |
| C-02 | Modelo urbanización conceptual | URB | AP-URB | Lead AP | H1 | LOIN-H1 | Published |
| C-03 | Modelo arquitectura básico | ARQ | AP-ARQ | Lead AP | H2 | LOIN-H2 | Published |
| C-04 | Modelo estructura básico | EST | AP-EST | Lead AP | H2 | LOIN-H2 | Published |
| C-05 | Modelo urbanización básico | URB | AP-URB | Lead AP | H2 | LOIN-H2 | Published |
| C-06 | Informe cumplimiento CTE | ARQ | AP-ARQ | Lead AP | H2 | — | Published |
| C-07 | Modelo arquitectura ejecutivo | ARQ | AP-ARQ | Lead AP | H3 | LOIN-H3 | Published |
| C-08 | Modelo estructura ejecutivo | EST | AP-EST | Lead AP | H3 | LOIN-H3 | Published |
| C-09 | Modelo MEP ejecutivo | MEP | AP-MEP | Lead AP | H3 | LOIN-H3 | Published |
| C-10 | Modelo urbanización ejecutivo | URB | AP-URB | Lead AP | H3 | LOIN-H3 | Published |
| C-11 | Mediciones y presupuesto | QS | AP-QS | Lead AP | H3 | — | Published |
| C-12 | Modelo federado as-built | Lead AP | Lead AP | NEXUM | H4 | LOIN-H4 | Archived |
| C-13 | Dataset FM para operador PBSA | Lead AP | Lead AP | NEXUM + Operador | H4 | LOIN-H4 | Archived |

> Cada contenedor referencia un TIDP de la disciplina autora.

---

## 6. Procedimientos de calidad (puente a S6)

- **Validación previa a publicación:**
  1. Schema check (IFC válido contra IFC4/IFC4.3).
  2. IDS check del hito correspondiente con `ifctester`.
  3. Revisión visual en Bonsai / visor IFC.
  4. Aprobación documentada en CDE.
- **Frecuencia:** antes de cada `Shared → Published`.
- **Registro:** log de validación archivado junto al contenedor.

---

## 7. Entorno común de datos (CDE) propuesto

Responde al EIR §5, que deja la plataforma abierta. **Propuesta del lead appointed party: Speckle como CDE OpenBIM.**

| Aspecto | Propuesta |
|---|---|
| Plataforma | **Speckle** (open source, OpenBIM-nativo, federación IFC, API REST, integración Bonsai/Revit/Rhino) |
| Estados | WIP / Shared / Published / Archived (modelados como streams + branches en Speckle) |
| Convención de naming | ISO 19650-2 §11 — `CANCABASSA-<Originador>-<Volumen>-<Nivel>-<Tipo>-<Disciplina>-<Número>` |
| Backup y retención | Servidor Speckle propio NEXUM + snapshot diario S3 + retención 10 años post-entrega |
| Acceso | Roles `owner` / `contributor` / `reviewer` por stream |
| Integración CI/CD | Hooks Speckle → ifctester en pipeline GitHub Actions (preparación para S9 del plan formativo) |

**Justificación de la elección:** Speckle es coherente con el plan formativo OpenBIM 12w (sesión S11 dedicada al CDE OpenBIM), permite federación nativa IFC, API programática para automatizar validación IDS (S7-S8) y se integra con Bonsai (S5).

---

## 8. Tecnología y métodos

### 8.1 Software por función (con versiones exactas — patrón Smithsonian)

| Función | Herramienta primaria | Versión mínima | Alternativa OpenBIM |
|---|---|---|---|
| Autoría ARQ | Revit | 2024.2 | Bonsai (Blender 4.2 LTS) |
| Autoría EST | Tekla Structures | 2024 | — |
| Autoría MEP | Revit MEP | 2024.2 | — |
| Autoría URB | Civil 3D | 2024 | InfraWorks 2024 |
| Coordinación / Clash | Solibri Office | 9.13.10 | BIMcollab Zoom 9.0 |
| Validación IDS | ifctester | 0.8.5 | — |
| Issues / BCF | BIMcollab Zoom | 9.0 | BCF 3.0 nativo en Speckle |
| CDE | Speckle Server | 2.20 | — |
| Lenguaje scripting | Python | 3.12 | IfcOpenShell 0.8.5 |

### 8.2 Sistema de clasificación

**GuBIMClass** como sistema único de clasificación (Institut de Tecnologia de la Construcció de Catalunya). Aplicable transversalmente desde H1 (nivel 1) hasta H3 (clasificación completa).

### 8.3 Tolerancias geométricas

| Dimensión | Tolerancia admisible |
|---|---|
| Posición horizontal | ± 5 mm (edificación) / ± 20 mm (urbanización) |
| Cota | ± 5 mm |
| Verticalidad | ± 3 mm/m |
| Coordinación entre disciplinas | Sin solapes geométricos detectables en clash duro |

---

## 9. Plan de movilización

| Semana del encargo | Hito BEP | Acción |
|---|---|---|
| 0 | Firma | Activación CDE + plantillas |
| 1 | Kick-off | Distribución BEP definitivo + TIDPs |
| 2 | Primer ciclo | Primera federación de prueba |
| 4 | H1 | Anteproyecto publicado |

---

## 10. Riesgos BIM y mitigaciones (mini Risk Register)

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| R-01 | Interoperabilidad IFC entre autores (especialmente Tekla ↔ Revit) | Media | Alto | Pruebas tempranas en H1 + perfil IFC acordado + smoke tests semanales |
| R-02 | LOIN ambiguo en hitos intermedios | Media | Medio | IDS por hito desde el inicio + validación con ifctester antes de publicar |
| R-03 | Cambios de alcance no documentados | Alta | Alto | Control de versiones del BEP + log de cambios contra MIDP |
| R-04 | Discrepancia entre datos FM exigidos por operador PBSA y modelo as-built | Alta | Alto | Coordinar con operador antes de H1 + IDS-FM específico para H4 |
| R-05 | Georreferenciación urbanización ↔ edificación inconsistente | Media | Alto | Origen único definido por URB en H1 + `IfcMapConversion` obligatorio |
| R-06 | Madurez insuficiente del equipo en IFC4.3 (más reciente que IFC4) | Media | Medio | Sesión formativa interna pre-kick-off + uso de IFC4 Add2 TC1 si IFC4.3 falla |
| R-07 | Falta de integración Speckle ↔ Tekla maduro | Baja | Medio | Plan B: exportación IFC desde Tekla + ingesta manual a Speckle |

---

## Fuentes de referencia

- [Plantilla BEP Smithsonian (Nov 2024)](https://www.sifacilities.si.edu/sites/default/files/Files/BIM/OPDC_BIM_Project_Execution_Plan_Template_Nov2024.docx)
- [Plantillas ISO 19650 (Plannerly)](https://plannerly.com/category/iso-19650-templates/)
- ISO 19650-2:2018 — actividades 5.3 a 5.7
- EN 17412-1:2020 — LOIN

---

## Dudas pendientes

1.
2.
3.
