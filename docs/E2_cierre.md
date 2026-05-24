# E2 · Documento de cierre del Entregable Semana 2

> **Documento de control** del cierre del Entregable E2 dentro del plan formativo OpenBIM 12 semanas. Producido en la sesión retrospectiva **S2·S del 24/05/2026** (slot original 23/05). Función: dejar trazabilidad ISO 19650-2 §5.7 (Information Container Approval) del paquete E2 antes del arranque de **S3·L** el lunes 25/05/2026 a las 07:00.

---

## 1. Identificación

| Campo | Valor |
|---|---|
| **Proyecto integrador** | Can Cabassa PBSA (Purpose Built Student Accommodation) |
| **Appointing party** | NEXUM Developments |
| **Entregable** | E2 · Semana 2 del plan formativo OpenBIM 12w |
| **Periodo cubierto** | 11/05/2026 → 24/05/2026 (sesiones S2·L, S2·X y S2·S) |
| **Fecha de cierre** | 24/05/2026 (cierre retrospectivo del slot 23/05) |
| **Autor del cierre** | Jose M. Soria (jmsoria@ciccp.es) |
| **Versión del cierre** | 1.0 |
| **Repositorio** | [JMSoriaMoyano/openbim-12w](https://github.com/JMSoriaMoyano/openbim-12w) |
| **Próximo hito** | S3·L · lunes 25/05/2026 · 07:00 CEST · IFC schema: jerarquía y relaciones |

---

## 2. Inventario de E2

Los siguientes artefactos componen el entregable E2 en su estado al cierre. Los hashes SHA-256 se calculan sobre la versión del workspace local pendiente de commit final S2·S (LF Unix). El SHA-256 sobre la versión Windows local del usuario diferirá por la conversión automática LF→CRLF; esto es esperado y no constituye corrupción.

| Ruta | Tipo | Líneas | SHA-256 (workspace LF) | Rol en E2 |
|---|---|---|---|---|
| `docs/E2_eir_draft.md` | DOC | 292 | `ae0eaa2910088abff07e9480141d8ebd87061974be05880ba1262fb192388d3d` | Exchange Information Requirements (cliente↔NEXUM). Versión v0.5. |
| `docs/E2_mini_bep.md` | DOC | 629 | `9f1db5ff014cf2a92a8d82d6277bd15ca9830a55385a36f4661b9d54842a90bf` | BIM Execution Plan (NEXUM↔equipo proyectista). Versión v0.7. |
| `docs/S2L_bsdd_implementacion.md` | DOC | 282 | `845f99455a4e87a90f75033a016c16702a1f1075150e06df2b19f8996192c60d` | Nota técnica bSDD reusable cross-proyecto. Versión v0.1. |
| `configs/revit_ifc_export_config.json` | CFG | 66 | `f64bb2768a5767d7fd683875c50fcd19cf2dde01f851cc71424f85bb41a4184f` | **Anexo A** operativo del BEP. Setup Revit IFC Exporter. Versión v0.4. |
| `scripts/s2x_lab_json_reader.py` | CODE | 95 | `212d1e24fd20ca0932d27156fb4f21cd68b6a13dc4951f1060c2e8166b41932b` | Validador del Anexo A. 12 invariantes técnicas. |

**Artefactos complementarios producidos durante E2 pero no normativos** (documentación de proceso, no contractuales):

| Ruta | Tipo | Rol |
|---|---|---|
| `docs/S2L_loin_en_ids.md` | DOC | Lectura comentada de S2·L sobre LOIN ↔ IDS |
| `docs/S2L_lecturas_bep_templates.md` | DOC | Análisis de plantillas BEP de referencia (Smithsonian, Plannerly) |
| `docs/S2X_lectura_comentada_revit_config.md` | DOC | Guía didáctica de la sesión S2·X |
| `docs/S2X_notas_sesion.md` | DOC | Notas en vivo de S2·X (v0.3) |

---

## 3. Resultado del checklist ISO 19650 (8 criterios)

Verificación realizada el 24/05/2026 durante la sesión S2·S. Resultado: **8/8 cubiertos**.

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| B1 | Roles ISO 19650 nombrados | 🟡 Aceptable | EIR §6 + BEP §3.1 declaran los 4 roles (Appointing, Lead AP, AP, IM). Nombres nominales `_(a designar)_` por estar en fase pre-appointment, lo cual es coherente con ISO 19650-2 §5.3. Registrado en Dudas pendientes. |
| B2 | Contenedores de información identificados | ✅ Cumple | BEP §5 MIDP lista 13 contenedores (C-01...C-13) con autor, revisor, hito, LOIN y estado destino. |
| B3 | Estados de revisión declarados | ✅ Cumple | EIR §5 exige los 4 estados ISO 19650-1 §12 (WIP/Shared/Published/Archived). BEP §7 los materializa como streams+branches en Speckle. |
| B4 | Transmittals formalizados | ✅ Cumple | BEP §11 (nueva en v0.7) define convención de IDs, campos obligatorios, verificación por receptor, almacenamiento y plan operativo para S11·L. |
| B5 | Coherencia BEP↔EIR↔JSON | ✅ Cumple | Referencias cruzadas EIR §3.1 → BEP §4.1.6 → JSON `_NEXUM_metadata`. Trinidad de trazabilidad cerrada. |
| B6 | Referencia cruzada a nota técnica bSDD | ✅ Cumple | BEP §4.1.6.bis incluye nota técnica de apoyo apuntando a `docs/S2L_bsdd_implementacion.md`. |
| B7 | LOIN/MVD sin contradicciones | ✅ Cumple | EIR §3.1.1 (IFC4 Add2 RV + IFC4.3 RV URB) ↔ BEP §4.1.1 idéntico. DTV solo en excepciones autorizadas (DTV-01 Revit↔Tekla, DTV-02 Revit↔Revit MEP). |
| B8 | Anexo A (JSON) declarado formalmente | ✅ Cumple | BEP §4.1.6 cierra con declaración explícita de `configs/revit_ifc_export_config.json` v0.4 como **Anexo A operativo** del BEP. |

---

## 4. Decisiones formalizadas en E2

Las siguientes decisiones técnicas se elevan a **convención permanente NEXUM** a través de E2 y serán heredadas por todos los proyectos sucesores:

### 4.1 JSON `revit_ifc_export_config.json` v0.4 como Anexo A operativo

El JSON queda formalmente declarado como anexo contractual del BEP. Su modificación requiere actualización del BEP y nuevo commit firmado. Validación obligatoria con `s2x_lab_json_reader.py` antes de cualquier merge a `main`.

### 4.2 `_NEXUM_metadata` como convención permanente

Cualquier configuración de herramienta de terceros (JSON/XML/YAML) gestionada por NEXUM llevará un bloque `_NEXUM_metadata` con un mínimo de 8 claves: `purpose`, `version`, `date`, `author`, `BEP_reference`, `EIR_reference`, `related_files`, `notes_no_guardados_en_archivo`. Aplicable a futuras configuraciones BCF, IDS, Solibri rulesets y Speckle stream configs.

### 4.3 GUID stability como regla de gobernanza (Decisión 21/05)

Todo proyecto NEXUM activa `StoreIFCGUID=true` desde la primera exportación. Proyectos heredados sin esta garantía pasan auditoría previa de paridad de GUIDs antes de ser aceptados en el CDE. BCFs huérfanos por inestabilidad de GUIDs se cierran como `Closed-Obsolete` salvo issues abiertos, que se re-emiten manualmente. La ruta de forzar GUIDs antiguos vía Dynamo/pyRevit queda prohibida.

### 4.4 Plantilla Revit unificada `NEXUM_CanCabassa.rte`

Formalizada en BEP §4.1.7 (v0.6) como prerrequisito de coherencia bSDD↔Pset↔Mapping. Contiene parámetros compartidos críticos (incluido `IfcGUID` en todas las categorías), clasificaciones GuBIMClass cargadas, dirección del proyecto y file header NEXUM. A crear materialmente en S3·L (lunes 25/05).

### 4.5 Transmittals (BEP §11) — stub mínimo viable

E2 fija convención de IDs (`TRA-CANCABASSA-<NN>-<YYYYMMDD>`), 10 campos obligatorios por transmittal (incluido `attachments_hash_sha256`), procedimiento de verificación por receptor y almacenamiento write-once. Implementación operativa en S11·L cuando se aborde el CDE OpenBIM Speckle.

---

## 5. Deuda técnica heredada a E3 y posteriores

### 5.1 Bloqueos pendientes (priorizados)

| ID | Item | Severidad | Hito de resolución |
|---|---|---|---|
| D-01 | URI definitiva GuBIMClass en bSDD (`[BSDD-URI-PENDING-S3L]` en BEP §4.1.6.bis.1) | Alta | **S3·L · lun 25/05/2026** |
| D-02 | Decisión NEXUM sobre publicación de dominio propio en bSDD | Media | **S3·L · lun 25/05/2026** |
| D-03 | Crear materialmente `templates/NEXUM_CanCabassa.rte` v1 + `NEXUM_SharedParameters.txt` | Alta | **S3·L · lun 25/05/2026** |
| D-04 | Crear `configs/_template_revit_ifc_export_config.json` con placeholders `[OBLIGATORIO: ...]` | Media | **S3·L · lun 25/05/2026** |
| D-05 | Crear `configs/NEXUM_GuBIMClass_UserDefinedPsets.txt` y `configs/NEXUM_ParameterMapping.txt` | Media | **S3·L · lun 25/05/2026** |
| D-06 | Iniciar tabla maestra Revit↔bSDD por disciplina (mínimo 10 propiedades ARQ y MEP) | Media | **S3·L · lun 25/05/2026** |

### 5.2 Scripts pendientes (con sesión de creación)

| Script | Propósito | Sesión |
|---|---|---|
| `check_guid_stability.py` | Paso 1 del pipeline CDE · verificación de paridad GUIDs entre exportaciones consecutivas | S6·L |
| `bsdd_resolve.py` | Resolver URIs bSDD sobre IFC entregado | S6·L |
| `bsdd_client.py` | Cliente HTTP a bSDD API REST/GraphQL | S4·L |
| `check_template_consistency.py` | Paso 5 del pipeline CDE · detecta TEMPLATE_MISMATCH | S6·L |
| `validate_ifc_against_ids.py` | Paso 2 del pipeline CDE · validación contra IDS v1.0 | S8·L |
| `bcf_guid_remap.py` | Mapping `old_guid → new_guid` para BCFs huérfanos (Ruta 2 de la decisión GUID stability) | S10·L |
| `generate_transmittal.py` | Emisión automática de transmittals BEP §11 desde Speckle | S11·L |

### 5.3 Mejoras candidatas a v0.5 del JSON y v0.5 del script

**JSON `revit_ifc_export_config.json` v0.5:**
- `_NEXUM_metadata.min_ifc_exporter_version_tested` (registro de la versión efectivamente probada)
- `_NEXUM_metadata.discipline` como campo explícito (no solo en `applies_to`)
- `_NEXUM_metadata.milestone_scope` con array de hitos cubiertos

**Script `s2x_lab_json_reader.py` v0.5:**
- Invariantes de gobernanza M01–M08 (formalizadas en S2·X) además de las 12 técnicas actuales
- Flag `--strict` que falla si la metadata está incompleta aun cuando las 12 técnicas pasen
- Output opcional `--json` para parseo en GitHub Actions (preparación S9·L)

### 5.4 Items de gobernanza pendientes (no técnicos)

- Designación nominal de Lead Appointed Party, Appointed Parties por disciplina e Information Manager.
- Cláusulas comerciales del EIR §7: penalizaciones por incumplimiento del MIDP y propiedad intelectual de los modelos.
- Coordinación con operador PBSA antes de H1 (R-04 del Risk Register).
- Confirmación de compatibilidad con Revit IFC Exporter 25.x cuando Autodesk lo publique.

---

## 6. Trazabilidad de cierre

### 6.1 Cronología de E2

| Fecha | Sesión | Hito |
|---|---|---|
| 11/05/2026 | S1·L | OpenBIM, buildingSMART, ISO 19650 (incluida por contexto del entregable E1, no parte de E2) |
| 16/05/2026 | S1·S | Cierre E1 (no parte de E2) |
| 18/05/2026 | S2·L | EIR v0.4 + BEP v0.5 + JSON v0.3 + nota técnica bSDD v0.1 |
| 20/05/2026 | (planificada S2·X miércoles) | Diferida a 21/05 por indisponibilidad |
| 21/05/2026 | S2·X | JSON v0.4 + `s2x_lab_json_reader.py` + BEP v0.6 (§4.1.7 plantilla unificada) + notas sesión v0.2 |
| 23/05/2026 | (slot original S2·S sábado) | Diferida a 24/05 |
| 24/05/2026 | S2·S (este documento) | EIR v0.5 + BEP v0.7 + S2L_bsdd_implementacion.md publicado en `main` + `E2_cierre.md` |
| 25/05/2026 | **S3·L (próximo)** | Arranque con las 6 acciones derivadas de §5.1 |

### 6.2 Historial de commits relevantes

| SHA corto | Fecha | Resumen |
|---|---|---|
| `e2818ea` | 21/05/2026 06:35 UTC | S2X: notas sesion + lab JSON reader 12 invariantes + BEP 0.6 con 4.1.7 plantilla unificada |
| `f14dd52` | 24/05/2026 ~12:30 UTC | S2S: add S2L_bsdd_implementacion.md (recuperado · deuda técnica para cierre E2) |
| _(pendiente)_ | 24/05/2026 | S2S: cierre E2 (BEP v0.7, EIR v0.5, E2_cierre.md, Dudas pobladas) |

### 6.3 Decisión de versión final por archivo

Las siguientes versiones son las **canónicas** del cierre E2:

| Archivo | Versión canónica E2 |
|---|---|
| `E2_eir_draft.md` | **v0.5** |
| `E2_mini_bep.md` | **v0.7** |
| `S2L_bsdd_implementacion.md` | **v0.1** |
| `revit_ifc_export_config.json` | **v0.4** |
| `s2x_lab_json_reader.py` | (sin SemVer interno; 12 invariantes técnicas) |

Cualquier versión superior generada en E3 (S3·L onwards) ya no pertenece a E2 — pertenece a su entregable de origen y referenciará E2 como antecesor.

---

## 7. Aprobación

En esta fase del plan formativo se sustituye la firma formal por la **firma git** del autor (`git log` muestra el commit y el autor de cada cambio). Tras el commit S2·S final, el cierre E2 quedará trazado como:

- **Autor:** Jose M. Soria
- **Email:** jmsoria@ciccp.es
- **Mecanismo de firma:** `user.email` + `user.name` del repo + `gh push` autorizado al remoto
- **Verificación:** `git log --format='%h %an <%ae> %s' --since='2026-05-11' --until='2026-05-25' -- docs/E2_*.md configs/revit_ifc_export_config.json scripts/s2x_lab_json_reader.py docs/S2L_bsdd_implementacion.md docs/E2_cierre.md`

Este `git log` filtrado constituye el equivalente operativo a un Information Container Approval Log de ISO 19650-2 §5.7.4.

---

## 8. Notas operativas

### 8.1 Discrepancia LF ↔ CRLF entre repo y local Windows

Los hashes SHA-256 del §2 están calculados sobre la versión **LF Unix** del workspace que produce los archivos. Al hacer `git pull` desde Windows, git aplica conversión automática **LF → CRLF** (configuración por defecto `core.autocrlf=true`) por lo que el SHA-256 de los archivos en `C:\Users\jmsor\OpenBIM\openbim-12w\` será diferente. Esto **no constituye corrupción ni divergencia**: es comportamiento esperado del cliente git en Windows. La fuente de verdad es el SHA blob del propio repo GitHub, no el SHA del archivo en disco.

Ejemplo verificable: `S2L_bsdd_implementacion.md` mide 17.289 bytes en GitHub (LF) y 17.571 bytes en disco Windows (CRLF). Los 282 bytes adicionales son los `\r` añadidos por la conversión, uno por cada salto de línea del documento.

### 8.2 S1X_lab_ifc_primer_contacto.md

Documento detectado en `main` (commits anteriores a E2) pero ausente del workspace remoto del autor. Decisión adoptada en S2·S Bloque A: **ignorar durante E2** por no pertenecer al entregable. A revisar en sesión libre cuando sea oportuno; no bloquea E2 ni E3.

### 8.3 Sesión S2·X movida desde miércoles 20/05 a jueves 21/05

Registrada documentalmente en `S2X_notas_sesion.md` y en el commit `e2818ea`. No tiene implicación contractual pero queda anotada en §6.1 por completitud.

### 8.4 Próxima ejecución automática del briefing OpenBIM

El cron `6ffa9c6f` disparará el lunes 25/05/2026 a las 05:00 UTC (07:00 CEST), antes de la sesión S3·L. Leerá `main` con el commit S2·S incluido y publicará el briefing matinal con estado actualizado del repo y prioridades de la sesión.

---

## Document Revision History

| Rev | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 2026-05-24 | Jose M. Soria | Cierre formal del entregable E2. Producido durante sesión retrospectiva S2·S (slot original 23/05). Incluye inventario, checklist ISO 19650, decisiones, deuda heredada, trazabilidad y notas operativas. |
