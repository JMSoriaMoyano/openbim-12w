# E1 · Glosario ISO 19650

**Entregable:** S1·S — sábado 16/05/2026
**Mínimo:** ≥ 12 términos con definición ES/EN, contexto de uso y fuente verificable.

---

## 1. EIR — Exchange Information Requirements

**EN:** *Specification for what information is to be produced, when it is to be produced, by what methods and procedures, and to what standard.*
**ES:** Requisitos de Intercambio de Información — documento contractual que define qué información debe entregarse, cuándo, cómo y bajo qué estándares.

**Contexto de uso:** lo redacta el *Appointing Party* y se entrega al *Lead Appointed Party* como parte de los documentos de licitación. Es la base sobre la que se construye el BEP.

**No confundir con:** OIR (a nivel organización) ni PIR (a nivel proyecto).

**Fuente:**

---

## 2. BEP — BIM Execution Plan

**EN:** *Plan prepared by the suppliers to explain how the information management aspects of the appointment will be carried out.*
**ES:** Plan de Ejecución BIM — documento donde el *Lead Appointed Party* describe cómo va a cumplir el EIR: roles, software, procesos, hitos, federación de modelos.

**Contexto de uso:** dos versiones — *pre-appointment BEP* (en respuesta a la licitación) y *delivery BEP* (tras adjudicación, refinado y firmado).

**Fuente:**

---

## 3. CDE — Common Data Environment

**EN:** *Agreed source of information for any given project or asset, for collecting, managing and disseminating each information container through a managed process.*
**ES:** Entorno Común de Datos — repositorio único acordado donde se gestionan todos los contenedores de información del proyecto a lo largo de 4 estados: WIP, Shared, Published, Archive.

**Ejemplos de implementación:** Autodesk Construction Cloud, Speckle, Trimble Connect, Bentley ProjectWise, BIMcollab Nexus.

**Fuente:**

---

## 4. LOIN — Level of Information Need

**EN:** *Framework which defines the extent and granularity of information needed to fulfil each information requirement.*
**ES:** Nivel de Necesidad de Información — marco que sustituye y supera al antiguo LOD (Level of Development) anglosajón. Define la información geométrica, alfanumérica y documental necesaria por elemento, propósito y fase.

**Tres dimensiones:** geometrical information, alphanumerical information, documentation.

**Norma específica:** EN 17412-1:2020.

**Fuente:**

---

## 5. AIM — Asset Information Model

**EN:** *Information model relating to the operational phase of an asset.*
**ES:** Modelo de Información del Activo — modelo que da soporte a la fase de operación y mantenimiento, una vez entregado el activo al *Appointing Party*.

**Contexto de uso:** se nutre del PIM en la entrega final del proyecto y se mantiene vivo durante toda la vida útil del activo.

**Fuente:**

---

## 6. PIM — Project Information Model

**EN:** *Information model relating to the delivery phase of a project.*
**ES:** Modelo de Información del Proyecto — modelo que se construye y gestiona durante la fase de diseño y construcción, hasta el handover.

**Transición:** al cierre del proyecto, el subconjunto relevante del PIM se transfiere al AIM.

**Fuente:**

---

## 7. Appointing Party

**EN:** *Receiver of information concerning works, goods or services from a lead appointed party.*
**ES:** Parte Designante — quien encarga el proyecto, redacta el EIR y recibe los entregables. Equivale al antiguo *Employer* o *Client*.

**Responsabilidades:** definir OIR/PIR/EIR, establecer el CDE inicial, aprobar el BEP.

**Fuente:**

---

## 8. Lead Appointed Party

**EN:** *Provider of information for works, goods or services to an appointing party, who appoints further parties for delivery.*
**ES:** Parte Designada Principal — contratista principal o coordinador BIM contratado que responde al *Appointing Party* y subcontrata a los *Appointed Parties*.

**Responsabilidades:** preparar el BEP, montar el MIDP a partir de los TIDPs, garantizar la federación y entrega.

**Fuente:**

---

## 9. Task Team / Appointed Party

**EN:** *Group assembled to perform a specific task; appointed party provides information for works, goods or services to a lead appointed party.*
**ES:** Equipo de Tarea / Parte Designada — cada disciplina o subcontratista que produce información para una entrega específica (estructura, MEP, arquitectura, etc.).

**Relación:** cada *Task Team* prepara su propio TIDP, que el *Lead Appointed Party* agrega en el MIDP.

**Fuente:**

---

## 10. MIDP — Master Information Delivery Plan

**EN:** *Plan that incorporates all relevant task information delivery plans.*
**ES:** Plan Maestro de Entrega de Información — agregación de todos los TIDPs en un único plan que muestra qué información se entrega, por quién, cuándo y en qué formato a lo largo del proyecto.

**Lo mantiene:** *Lead Appointed Party*.

**Fuente:**

---

## 11. TIDP — Task Information Delivery Plan

**EN:** *Plan of information deliverables prepared by a task team for its scope of work.*
**ES:** Plan de Entrega de Información por Equipo de Tarea — plan individual de cada *Task Team* que detalla qué entregables produce, en qué hito y bajo qué LOIN.

**Lo mantiene:** cada *Task Team* responsable.

**Fuente:**

---

## 12. OIR — Organizational Information Requirements

**EN:** *Information requirements in relation to organizational objectives.*
**ES:** Requisitos de Información Organizacional — información que necesita la organización en su conjunto, independientemente de un proyecto concreto. Alimenta a los AIR (Asset Information Requirements) y a los EIR.

**Cadena de requisitos:** OIR → AIR → PIR → EIR.

**Fuente:**

---

## Términos extra (opcional, suman puntos)

### 13. PIR — Project Information Requirements

**EN:** *Information required to answer or inform high-level strategic objectives in relation to a particular built asset project.*
**ES:** Requisitos de Información del Proyecto — información estratégica que el *Appointing Party* necesita en cada hito clave del proyecto.

**Fuente:**

---

### 14. AIR — Asset Information Requirements

**EN:** *Information requirements in relation to the operation of an asset.*
**ES:** Requisitos de Información del Activo — qué información se necesita para operar y mantener el activo una vez construido.

**Fuente:**

---

### 15. Information Container

**EN:** *Named persistent set of information retrievable from a file, system or application storage hierarchy.*
**ES:** Contenedor de Información — unidad mínima de información gestionada en el CDE: puede ser un IFC, un PDF, una hoja de cálculo, etc. Tiene un código único y estados (WIP/Shared/Published/Archive).

**Fuente:**

---

### 16. Information Standard

**EN:** *Standard agreed for a particular project or asset, against which information is produced.*
**ES:** Estándar de Información — documento que define **las reglas técnicas y formales** que toda la información del proyecto debe cumplir: nomenclatura de ficheros, clasificación, formatos de intercambio (IFC, BCF, COBie), metadatos obligatorios, sistema de coordenadas y unidades, códigos de estado y suitability, estructura del CDE.

**Contexto de uso:** lo define el *Appointing Party* en la actividad 5.1 y se emite junto al EIR en 5.2. Es **obligatorio y prescriptivo**, aplica a todos los appointments del proyecto. Es el "manual de estilo" de los datos.

**Responde a la pregunta:** *qué reglas debe cumplir la información.*

**Ejemplos de contenido:**

- Patrón de nombrado: `PRJ-ORG-VOL-LEV-TYP-ROL-NNNN.ifc`
- Clasificación: Uniclass 2015 (tablas Pr/Ss/EF) o GuBIMClass para España
- Status codes: S0 (WIP) → S1 (coordination) → S2 (information) → S4 (approval) → S6/S7 (PIM/AIM)
- Formatos: IFC 4.x, BCF 3.0, COBie, PDF/A

**No confundir con:** *production methods and procedures* (ver entrada 17), que definen el **cómo** se produce, no el **qué** se exige.

**Fuente:**

---

### 17. Production Methods and Procedures

**EN:** *Methods and procedures used by appointed parties to produce information in accordance with the project's information standard.*
**ES:** Métodos y Procedimientos de Producción — conjunto de procesos operativos detallados que cada equipo sigue para **generar entregables que cumplan el information standard**. Es la capa de proceso entre el estándar (reglas) y la herramienta (Revit, ArchiCAD, Tekla, IfcOpenShell).

**Contexto de uso:** los **propone el Lead Appointed Party** dentro del BEP (pre y post-appointment), se **testean obligatoriamente en la actividad 5.5 (Mobilization)** antes de empezar producción real, y se ejecutan durante 5.6–5.7.

**Responde a la pregunta:** *cómo se produce la información para cumplir el estándar.*

**Cubre típicamente:**

- Plantillas de modelado (`.rte`, `.pln`), librerías de familias, parámetros compartidos
- Reglas de federación de modelos de disciplinas (origen compartido, IFC reference)
- Flujo de coordinación y clash detection (Navisworks, Solibri, BIMcollab)
- Reglas IDS aplicables y uso del IFC Validation Service
- Flujo de issues BCF (creación, asignación, SLA, cierre)
- Procedimiento de publicación al CDE con metadatos correctos
- Matriz de aprobaciones para cambios de estado S0→S1→S2→...
- Reglas de versionado (P01.01, C01.01) y disparadores de revisión

**Diferencia con information standard:**

| Information Standard          | Production Methods and Procedures        |
| ----------------------------- | ---------------------------------------- |
| Define **el qué**             | Define **el cómo**                       |
| Lo emite el Appointing Party  | Los propone el Lead Appointed Party      |
| Obligatorio y prescriptivo    | Propuesto y negociable                   |
| Aplica a **todo** el proyecto | Aplica al **appointment** específico     |
| Cambia poco                   | Se refina tras testeo en 5.5             |

**Analogía mental:** el information standard es la receta y el plato final esperado; los production methods and procedures son la técnica del cocinero, sus utensilios y su mise en place. Dos cocineros pueden cocinar distinto, pero el plato final debe ser idéntico.

**Fuente:**

---

### 18. Information Protocol

**EN:** *Legal agreement or contractual addendum identifying the information management requirements and obligations of the parties.*
**ES:** Protocolo de Información — anexo o cláusula contractual que **da fuerza legal** a los requisitos de gestión de información del proyecto. Convierte el EIR, el information standard, los production methods and procedures y el BEP en obligaciones contractuales exigibles.

**Contexto de uso:** lo establece el *Appointing Party* en la actividad 5.1 como **marco contractual** y se incorpora a cada appointment firmado en 5.4. Sin él, los documentos BIM son orientativos y no exigibles legalmente.

**Responde a la pregunta:** *qué obligaciones contractuales sostienen el proceso BIM.*

**Contenido típico:**

- Definiciones de roles (Appointing Party, Lead Appointed Party, Task Team)
- Obligaciones de cumplir el EIR, BEP, information standard y production methods
- Derechos de propiedad intelectual sobre la información producida
- Licencias de uso de los modelos
- Régimen de responsabilidad y limitaciones (qué pasa si un modelo tiene errores)
- Procedimiento de gestión de cambios contractuales
- Cláusulas de precedencia entre documentos (qué prevalece si hay conflicto)

**Ejemplos de referencia:**

- [CIC BIM Protocol Second Edition (2018)](https://www.cic.org.uk/services/publications) (Reino Unido)
- En España suele incorporarse como anexo al contrato basado en plantillas del Ministerio o de itdUPM/es.BIM.

**Tríada documental de 5.1 (recuérdala bien):**

```
Information Standard         → reglas técnicas (qué cumplir)
Production Methods & Procs.  → procesos operativos (cómo cumplirlo)
Information Protocol         → marco contractual (qué obliga)
```

Los tres forman el **marco de gestión de información del proyecto**. Sin los tres, no puedes pasar a 5.2 (licitar).

**Fuente:**

---

## Diagrama del ciclo ISO 19650-2 (entregable adicional)

> Insertar aquí imagen del ciclo (`E1_ciclo_iso19650.jpg` o diagrama Mermaid).

```mermaid
flowchart LR
    A[1. Assessment & Need] --> B[2. Invitation to Tender]
    B --> C[3. Tender Response]
    C --> D[4. Appointment]
    D --> E[5. Mobilization]
    E --> F[6. Collaborative Production]
    F --> G[7. Information Model Delivery]
    G --> H[8. Project Close-out / AIM Handover]
```

**Roles por fase:**

| Fase | Appointing Party | Lead Appointed Party | Task Team |
| ---- | ---------------- | -------------------- | --------- |
| 1    | …                | —                    | —         |
| 2    | …                | —                    | —         |
| 3    | (revisa)         | …                    | …         |
| 4    | …                | …                    | —         |
| 5    | (recibe)         | …                    | …         |
| 6    | (revisa CDE)     | …                    | …         |
| 7    | (acepta)         | …                    | …         |
| 8    | (custodia AIM)   | (cierra PIM)         | —         |

---

## Dudas para profundizar (rellenar durante S1·L y S1·X)

1.
2.
3.

---

## Fuentes consultadas

- [buildingSMART · OpenBIM](https://www.buildingsmart.org/about/openbim/)
- [UK BIM Framework — Guidance documents](https://ukbimframework.org/resources/)
- [IFC overview · buildingSMART](https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/)
- *(añadir aquí cualquier otra que uses)*

---

## Criterios de aceptación (autocomprobación sábado)

- [ ] ≥ 12 términos definidos con ES + EN (objetivo ampliado: 18)
- [ ] Cada término tiene **Fuente** rellenada con URL o documento concreto
- [ ] Tríada de 5.1 cubierta: information standard + production methods + information protocol
- [ ] Diagrama del ciclo ISO 19650-2 incluido (imagen o Mermaid)
- [ ] Tabla de roles por fase completada
- [ ] 3 dudas anotadas para resolver
- [ ] Commit + push al repo `openbim-12w`
