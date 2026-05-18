# S2·L · Resumen conceptual — Smithsonian BEP Template + Plannerly ISO 19650 Templates

> **Sesión:** S2·L · 18/05/2026 · BEP, EIR y plan de información
> **Tema específico:** Análisis comparado de dos referencias operativas para la redacción del E2
> **Versión:** 1.0 · **Autor:** José M. Soria · **Estado:** Material de estudio

---

## 1. Por qué leer estas dos referencias

El objetivo de S2 es traducir el marco ISO 19650 a documentos operativos. Las dos lecturas elegidas representan **dos aproximaciones complementarias** al mismo problema:

| Referencia | Origen | Aproximación | Valor para el E2 |
|---|---|---|---|
| **Smithsonian OPDC BEP Template** | Cliente institucional público (EE.UU.) | Plantilla **operativa monolítica**: un único documento BEP exhaustivo | Mostrar **qué bloques** debe contener un BEP completo |
| **Plannerly ISO 19650 Templates** | Plataforma SaaS comercial alineada con ISO 19650 (UK/Internacional) | **Catálogo modular**: un documento por cada artefacto del ciclo | Mostrar **cómo se descompone** el plan de información en piezas separadas |

La síntesis útil para NEXUM: del Smithsonian heredamos **profundidad técnica por sección**; de Plannerly heredamos **arquitectura documental** alineada ISO 19650.

---

## 2. Smithsonian OPDC BIM Project Execution Plan Template (Nov 2024)

### 2.1 Contexto y autoría

- Editor: **Office of Planning, Design and Construction (OPDC)** del Smithsonian Institution.
- Última versión: **Noviembre 2024**.
- Ámbito: obligatorio para todos los proyectos de capital del Smithsonian (museos, almacenamiento, infraestructura federal).
- Filosofía: anglosajona, alineada con la tradición **Penn State BIM Project Execution Planning Guide**, no con ISO 19650 directamente — pero estructuralmente equivalente.
- Distribución: documento Word `.docx` con tablas rellenables (26 tablas, ~40 páginas).

### 2.2 Estructura completa (6 bloques principales)

#### Bloque 1 · BIM Project Execution Plan Overview

- Document Revision History — control de versiones del propio BEP (tabla con `Rev`, `Date`, `Section`, `Description of Updates`).

> **Lectura ISO 19650:** equivale al **control de versiones** que un BEP post-appointment debe mantener obligatoriamente.

#### Bloque 2 · Project Information

- Basic Project Information — identificación del proyecto.
- Project Schedule — fases con fechas estimadas.
- BIM Execution Plan Timeline — cuándo se revisa el BEP por fase (Schematic Design, Design Development, Construction Documents, Construction, Facility Turnover).
- Key Project Contacts — directorio con `Role`, `Organization`, `Contact Name`, `Location`, `E-Mail`, `Phone`.
- **BIM Roles and Responsibilities** — núcleo del bloque: roles BIM por organización.
- **BIM Use Staffing** — tabla con `BIM Use`, `Organization`, `Number of Total Staff for BIM Use`, `Estimated Worker Hours`, `Location(s)`, `Lead Contact`.

> **Lectura ISO 19650:** combina lo que la norma exige separar — directorio de roles (BEP §5.1.5) + matriz de responsabilidades (Responsibility Matrix). En tu E2 conviene mantenerlos separados.

#### Bloque 3 · Project Specific Deliverables

- **BIM Goals** — tabla con `Project Phase`, `Priority (High/Med/Low/Not Pursued)`, `Goal Description`, `Potential BIM Uses`. **Esto es el equivalente práctico al "propósito BIM" del EIR.**
- **BIM Uses** — checklist de 16 columnas y 4 fases (Plan / Design / Construct / Operate) cubriendo los **25 BIM Uses estándar Penn State**: Programming, Site Analysis, Design Authoring, Design Reviews, Site Utilization Planning, Construction System Design, Building Maintenance Scheduling, Building System Analysis, etc.
- **Detailed BIM Use Requirements** — para cada BIM Use marcado: `Value to Project`, `Responsible Party`, `Value to Resp. Party`, `Additional Resources/Skills Req'd`, `Notes`, `Proceed with Use (Yes/No/Maybe)`.
- Project Deliverables, desglosados en:
  - **Design Deliverables** — entregables por fase de diseño.
  - **Construction Deliverables** — entregables de construcción con `Submission Requirements` y `Format` (`.rvt`, `.ifc`, `.nwc`, `.nwd`, `.dwg`, `.xlsx`).
  - **SI Deliverables for Design and Construction** — entregables específicos del cliente Smithsonian.

> **Lectura ISO 19650:** este bloque equivale a **EIR + MIDP**. La tabla "Detailed BIM Use Requirements" es muy potente porque obliga al equipo a **justificar cada BIM Use**, no solo enumerarlo. Recomiendo replicar esta lógica en el E2.

#### Bloque 4 · Electronic Communications

Esta es la sección más operativa del documento Smithsonian:

- **Software Requirements** — versión exacta de cada herramienta.
- **Electronic File Storage** — plataforma del CDE.
- **Project Folder Structure** — taxonomía de carpetas.
- **Information Exchange Schedule** — calendario de intercambios.
- SI Asset Management — sistema de gestión de activos del cliente.
- **Space Naming** — nomenclatura de espacios IFC.
- **Model File Naming** — convención de archivos de modelo.
- **Sheet View Naming** — nomenclatura de vistas/planos.
- **Trade Contractor Coordination File Naming** — nomenclatura para subcontratistas.
- **Reference Points** — punto base, punto de proyecto, georreferenciación.

> **Lectura ISO 19650:** este bloque cubre lo que la norma denomina **"methods and procedures"** (ISO 19650-2 §5.4.6) y **"common naming convention"** (§11). Es la sección más densa técnicamente y la que más fricción genera entre disciplinas si no se cierra a tiempo.

#### Bloque 5 · Collaboration Procedures

- **Meetings**: tipo `Project Meetings` y `BIM Coordination Meetings` — frecuencia, agenda tipo, asistentes obligatorios.
- **Coordination Schedules**: separado en `Design` y `Construction`.
- **BIM Coordination**:
  - *Model Element Color Coding* — paleta RGB exacta por sistema (tabla con 19 sistemas: Outside Air = `128,255,255`, Supply Air = `0,128,192`, etc.). Ejemplo de **estandarización visual ultra-granular**.
  - *Hierarchy of Systems Coordination* — orden de prioridad para resolución de clashes.
- **Quality Control** — procedimientos de QC.
- **Model Accuracy and Tolerances** — tolerancias geométricas admisibles.

> **Lectura ISO 19650:** equivale a los procedimientos de calidad del BEP. La paleta de colores por sistema es un buen ejemplo de "estandarización defensiva" típica de cliente institucional con muchos proyectos paralelos.

#### Bloque 6 · Model Content Requirements

- **Model Content LOD** — matriz de elementos × LOD esperado por fase (heredera de AIA E202).
- **Revit Worksets** — particionamiento del modelo para trabajo colaborativo.

> **Lectura ISO 19650:** esta es la sección donde Smithsonian se aleja más del enfoque europeo. Usa LOD (geometría) sin distinguir LOI (información alfanumérica), porque la plantilla es anterior a la consolidación de EN 17412-1 LOIN. **En tu E2, sustituye esto por una tabla LOIN por hito según EN 17412-1.**

#### Apéndices

- Appendix A — Definitions (glosario).
- Appendix B — References (normativa y guías).

---

### 2.3 Las 5 lecciones de diseño del Smithsonian BEP

1. **Las tablas son el corazón del BEP.** 26 tablas estructuradas obligan a contestar; el texto libre es secundario. Replícalo en el E2.
2. **Cada BIM Use debe justificarse, no solo enumerarse.** La tabla "Detailed BIM Use Requirements" es el patrón más útil — obliga a `Value to Project` + `Responsible Party` + `Proceed with Use`.
3. **La nomenclatura no es accesoria.** Smithsonian dedica 5 subsecciones a naming. En ISO 19650 corresponde al §11 — no lo dejes ambiguo.
4. **El BEP se versiona como cualquier entregable.** El revision history en la primera página es buena práctica.
5. **El cliente puede ser muy prescriptivo.** Smithsonian fija formato, paleta de colores y plataforma. Esto es legítimo en un EIR institucional.

---

## 3. Plannerly ISO 19650 Templates

### 3.1 Contexto y autoría

- Editor: **Plannerly** — plataforma SaaS especializada en gestión de información ISO 19650.
- Filosofía: descomposición modular del paquete documental ISO 19650-2.
- Distribución: cada plantilla es un documento independiente (Word/PDF) + flujo digital en la plataforma.
- Punto fuerte: alineación 1:1 con la nomenclatura ISO 19650.

### 3.2 Catálogo completo de plantillas ISO 19650 ([Plannerly](https://plannerly.com/what-is-iso-19650/))

| Sigla | Nombre completo | Fase ISO 19650-2 | Producido por |
|---|---|---|---|
| **OIR** | Organizational Information Requirements | Pre-proyecto (nivel corporativo) | Appointing party |
| **PIR** | Project Information Requirements | Assessment (5.1) | Appointing party |
| **EIR** | Exchange Information Requirements | Invitation to tender (5.2) | Appointing party |
| **AIR** | Asset Information Requirements | Pre-proyecto (continuo) | Appointing party |
| **Pre-BEP** | Pre-appointment BIM Execution Plan | Tender response (5.3) | Prospective lead appointed party |
| **BEP** | (Post-appointment) BIM Execution Plan | Appointment + Mobilization (5.4-5.5) | Lead appointed party |
| **RM** | Responsibility Matrix | Mobilization (5.5) | Lead appointed party |
| **TIDP** | Task Information Delivery Plan | Mobilization (5.5) | Each appointed party |
| **MIDP** | Master Information Delivery Plan | Mobilization (5.5) | Lead appointed party |
| **RACI** | RACI Charts (Responsible, Accountable, Consulted, Informed) | Mobilization (5.5) | Lead appointed party |
| **RISK** | Risk Register | Transversal | Lead appointed party |
| **Mobilization Plan** | Plan de movilización del encargo | Mobilization (5.5) | Lead appointed party |
| **Information Protocol** | Anexo contractual legal sobre gestión de información | Appointment (5.4) | Appointing party + abogados |

### 3.3 La pirámide de requisitos OIR → PIR → AIR → EIR

Este es el aporte conceptual más valioso de Plannerly: la **cascada de requisitos** que precede al EIR.

```
Nivel corporativo                  ┌─────────────────┐
                                   │   OIR           │  Organizational
(estrategia de la organización)    │                 │  Information
                                   └────────┬────────┘  Requirements
                                            │
                          ┌─────────────────┴─────────────────┐
                          ▼                                   ▼
Nivel proyecto/activo  ┌──────────┐                      ┌──────────┐
                       │   PIR    │                      │   AIR    │
(qué información       │          │                      │          │
necesita un proyecto   │          │                      │          │  (qué información
o un activo en         │          │                      │          │   necesita el
operación)             └────┬─────┘                      └────┬─────┘   activo en uso)
                            │                                 │
                            └──────────────┬──────────────────┘
                                           ▼
Nivel intercambio              ┌─────────────────────┐
                               │        EIR          │
(qué se pide a la              │ Exchange Information│
cadena de suministro           │     Requirements    │
en un encargo concreto)        └─────────────────────┘
```

**Mensaje clave:** el EIR no nace de la nada. Es el **destilado contractual** de necesidades superiores (OIR, PIR, AIR) traducidas a requisitos exigibles a la cadena de suministro para un encargo concreto.

> **Aplicación al E2 de NEXUM:** aunque nuestro proyecto integrador no formalizará OIR/PIR/AIR (alcance demasiado amplio para el ejercicio), conviene **mencionar en el EIR draft que estos requisitos se asumen como dados** por NEXUM como organización. Mantiene la cadena lógica visible.

### 3.4 El triángulo Pre-BEP → BEP → MIDP/TIDP

Plannerly visualiza la transición licitación → ejecución con esta secuencia:

```
TENDER (5.2)               TENDER RESPONSE (5.3)        APPOINTMENT (5.4) + MOBILIZATION (5.5)
┌──────────┐               ┌───────────┐                ┌───────────┐
│   EIR    │  ───────────▶ │  Pre-BEP  │  ───────────▶ │    BEP    │
└──────────┘               └───────────┘                │ (post-app)│
                                                        └─────┬─────┘
                                                              │
                                              ┌───────────────┴───────────────┐
                                              ▼                               ▼
                                       ┌──────────┐                   ┌──────────┐
                                       │   MIDP   │ ◀──── consolida── │   TIDP   │
                                       │ (master) │                   │ (×n)     │
                                       └──────────┘                   └──────────┘
                                                                    Responsibility Matrix
                                                                    Risk Register
                                                                    Mobilization Plan
```

**Las tres lecturas obligatorias de este flujo:**

1. **EIR → Pre-BEP**: el cliente pregunta, el equipo licitador responde con su propuesta.
2. **Pre-BEP → BEP (post-appointment)**: la propuesta gana, se convierte en plan vinculante.
3. **BEP → MIDP**: el plan se descompone en un calendario maestro de contenedores de información, alimentado por los TIDP de cada disciplina.

### 3.5 Plantillas anexas que cierran el sistema

Tres plantillas que Plannerly trata como obligatorias y que el Smithsonian fusiona en bloques:

| Plantilla | Función |
|---|---|
| **Responsibility Matrix (RM)** | Reparto de responsabilidades por entregable de información. No es lo mismo que RACI: la RM es por contenedor de información; el RACI es por actividad/proceso. |
| **Information Protocol** | Anexo contractual que da fuerza legal a las exigencias BIM. Sin él, EIR/BEP son técnicamente vinculantes pero legalmente débiles. |
| **Risk Register** | Registro vivo de riesgos BIM (interoperabilidad, capacidad, capacitación, calidad). Transversal a todas las fases. |

---

## 4. Comparativa lado-a-lado — Smithsonian vs Plannerly

| Aspecto | Smithsonian BEP Template | Plannerly ISO 19650 Templates |
|---|---|---|
| Alineación normativa | Penn State / AIA E202 (tradición US) | ISO 19650-1/2:2018 (norma internacional) |
| Arquitectura documental | **Monolítica** (un BEP cubre todo) | **Modular** (13+ documentos separados) |
| Tratamiento del LOIN | LOD geométrico solo (pre-EN 17412) | LOIN integrado en EIR/BEP (EN 17412-1) |
| Granularidad de roles | Roles BIM agregados | Roles ISO 19650 (appointing/lead AP/AP) |
| Énfasis | Detalle técnico operativo (naming, colores, tolerancias) | Trazabilidad documental y contractual |
| Mejor para... | **Cliente institucional con flota de proyectos similares** | **Encargo único con cadena de suministro compleja** |
| Riesgo si se usa puro | Rigidez excesiva, no escala fuera del Smithsonian | Sobre-documentación si el proyecto es pequeño |

---

## 5. Síntesis aplicable al E2 — qué tomar de cada lectura

### Del Smithsonian (profundidad técnica)

1. **Replicar la tabla "Detailed BIM Use Requirements"** en el EIR — obliga a justificar cada uso BIM.
2. **Incluir tabla explícita de naming conventions** en el BEP (model files, sheets, spaces). Decisión a tomar en NEXUM: ¿GuBIMClass o Uniclass como base?
3. **Tabla de software con versión exacta** — no basta "Revit", indicar "Revit 2024.2".
4. **Tabla de tolerancias** — incluir aunque sea valores genéricos (geométricas y de coordinación).
5. **Revision history del propio BEP** — primera tabla del documento.

### De Plannerly (arquitectura documental)

1. **Mantener separados EIR (E2 documento 1) y BEP (E2 documento 2)** — ya lo hicimos en los andamios.
2. **Mencionar la cascada OIR → PIR → AIR → EIR** en el preámbulo del EIR draft — aunque no se desarrollen.
3. **Añadir referencia explícita a la Responsibility Matrix** dentro del BEP — sea como sección o como anexo.
4. **Considerar añadir un mini Risk Register** al cierre del E2 (5-7 riesgos BIM identificados).
5. **Alinear nomenclatura de roles** estrictamente con ISO 19650-1:2018 §3 (appointing party, lead appointed party, appointed party).

### Lo que **no** tomar

- **No** copiar la tabla de colores RGB del Smithsonian — es excesivo para el alcance del E2.
- **No** intentar generar OIR/PIR/AIR — fuera de alcance.
- **No** desarrollar el Information Protocol — requiere asesoría legal real.
- **No** usar terminología LOD/LOI pura — usar LOIN según EN 17412-1.

---

## 6. Estructura recomendada de los entregables E2 tras estas lecturas

Cruzando lo aprendido con los andamios ya creados:

### E2_eir_draft.md (NEXUM como appointing party)

```
0. Identificación del activo
1. Propósito BIM (BIM uses justificados)              ← inspiración Smithsonian
2. Hitos de entrega
3. Estándares y formatos exigidos                      ← Smithsonian §Software
4. LOIN por hito (EN 17412-1)                          ← NO Plannerly NO Smithsonian: propio
5. CDE
6. Roles ISO 19650                                     ← Plannerly
7. Requisitos contractuales (referencia a Information Protocol futuro) ← Plannerly
8. Criterios de aceptación
+ preámbulo: cascada OIR/PIR/AIR asumida               ← Plannerly
```

### E2_mini_bep.md (lead appointed party respondiendo)

```
0. Resumen ejecutivo
1. Información del proyecto y del encargo              ← Smithsonian
2. Objetivos y usos BIM acordados (trazabilidad EIR)   ← Smithsonian + Plannerly
3. Equipo y matriz de responsabilidades (RM + RACI)    ← Plannerly
4. Estrategia de federación                            ← Smithsonian
5. MIDP simplificado                                   ← Plannerly
6. Procedimientos de calidad
7. CDE propuesto
8. Tecnología y métodos (software con versión)         ← Smithsonian
9. Plan de movilización                                ← Plannerly
10. Riesgos BIM (mini Risk Register)                   ← Plannerly
+ Document Revision History en cabecera                ← Smithsonian
```

Los andamios `E2_eir_draft.md` y `E2_mini_bep.md` ya creados cubren esta estructura. Tras estas lecturas solo restará añadir:

- En el EIR: preámbulo OIR/PIR/AIR + tabla "Detailed BIM Use Requirements".
- En el mini-BEP: Document Revision History + tabla software con versiones exactas + mini Risk Register.

---

## 7. Fuentes

1. [BIM Project Execution Plan Template · Smithsonian OPDC · Nov 2024](https://www.sifacilities.si.edu/sites/default/files/Files/BIM/OPDC_BIM_Project_Execution_Plan_Template_Nov2024.docx) — plantilla operativa completa con 26 tablas.
2. [Smithsonian Architect-Engineer Information Center · Codes & Standards](https://www.sifacilities.si.edu/codes-standards) — repositorio oficial de estándares Smithsonian.
3. [ISO 19650 templates (OIR, PIR, EIR, AIR, BEP, TIDP, MIDP, Responsibility Matrix...) · Plannerly](https://plannerly.com/what-is-iso-19650/) — catálogo completo de plantillas con flujo ISO 19650-2.
4. [ISO 19650 Workflow with free templates (PDF) · Plannerly](https://plannerly.com/wp-content/uploads/2024/02/ISO-19650-Workflow-with-free-ISO-19650-templates.pdf) — diagrama oficial del flujo Assessment → Tender → Tender Response → Appointment → Mobilization → Production → Delivery → Close-out.
5. [ISO 19650-1:2018](https://www.iso.org/standard/68078.html) — conceptos y principios.
6. [ISO 19650-2:2018](https://www.iso.org/standard/68080.html) — fase de entrega de activos.
7. [BIM Project Execution Planning Guide v2.2 · Penn State / BIMForum](https://bimforum.org/wp-content/uploads/2022/06/BIMForum_BXP_2020-11.pdf) — base metodológica de la plantilla Smithsonian (25 BIM Uses, Project Execution Planning Procedure).
