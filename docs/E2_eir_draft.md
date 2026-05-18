# E2 · EIR Draft — Proyecto Integrador Can Cabassa PBSA

> **Entregable E2 · Semana 2 · Cierre sábado 23/05/2026**
> Documento emitido por el *appointing party* (NEXUM como promotor) en el marco de ISO 19650-2, actividad 5.2 (Invitation to tender).
> Versión: 0.3 · Estado: BORRADOR
> Autor: José M. Soria · Fecha: 18/05/2026

## Document Revision History

| Rev | Fecha | Sección | Descripción |
|---|---|---|---|
| 0.1 | 17/05/2026 | Todo el documento | Andamio inicial generado |
| 0.2 | 18/05/2026 | Todo el documento | Particularización a Can Cabassa PBSA tras S2·L (5 decisiones de diseño) |
| 0.3 | 18/05/2026 | §3.1 (nueva) | Formalización de MVD aplicable (Reference View por defecto, DTV bilateral acordado) |

## Preámbulo — Cascada de requisitos asumida

Este EIR se inscribe en el marco de información de NEXUM Developments como appointing party. A efectos del proyecto integrador se **asumen como dados** los niveles superiores de la cascada ISO 19650:

- **OIR (Organizational Information Requirements):** requisitos corporativos de NEXUM para todos sus encargos (estandarización IFC4.3, OpenBIM, retención mínima 10 años, soberanía del dato).
- **PIR (Project Information Requirements):** necesidades específicas del proyecto Can Cabassa PBSA derivadas de su business case (forward funding, BREEAM, certificación PBSA operadora).
- **AIR (Asset Information Requirements):** requisitos para la fase de operación del activo como residencia de estudiantes (FM, mantenimiento, energía).

El presente EIR **destila** estas necesidades superiores en requisitos exigibles a la cadena de suministro para la fase de entrega del activo.

---

## 0. Identificación del activo

| Campo | Valor |
|---|---|
| Proyecto | Can Cabassa PBSA (versión didáctica plan formativo OpenBIM 12w) |
| Promotor (appointing party) | NEXUM Developments |
| Tipología | Residencia de estudiantes (PBSA) + urbanización asociada |
| Localización | _(municipio, comarca — completar)_ |
| Superficie construida estimada | _(m² — completar)_ |
| Fase del encargo | Diseño básico → Proyecto ejecutivo → Construcción → Entrega |
| Inversión estimada | 20 M€+ |
| Modelo financiero | Forward funding |

---

## 1. Propósito de la información (BIM uses)

### 1.1 Lista de usos BIM exigidos

| # | Uso BIM | Propósito | Hito en que se evalúa |
|---|---|---|---|
| U1 | Coordinación 3D multidisciplinar | Detección de interferencias ARQ-EST-MEP-URB | H2 + H3 |
| U2 | Mediciones y presupuesto | Extracción cuantitativa fiable para forward funding | H3 |
| U3 | Verificación normativa CTE | Cumplimiento DB-SI, DB-HE, DB-HR | H2 |
| U4 | Gestión de activos (FM) | Información estructurada para operador PBSA | H4 |
| U5 | Análisis BREEAM / ESG | Soporte de certificación de sostenibilidad | H2 + H3 |

### 1.2 Justificación detallada de cada uso BIM (patrón Smithsonian)

| Uso | Valor para el proyecto | Responsable principal | Recursos/competencias requeridas | Notas | Proceder |
|---|---|---|---|---|---|
| U1 Coordinación 3D | Alto — evita sobrecostes de obra | Lead appointed party | Federación IFC + clash detection automatizado | Federación semanal en CDE | Sí |
| U2 Mediciones | Alto — soporta business case | Appointed party (QS) | Extracción QTO desde IFC + QC manual | Vinculado a hito ejecutivo | Sí |
| U3 Verificación CTE | Medio-Alto — reduce riesgo regulatorio | Appointed party (ARQ) | IDS específico CTE + ifctester | Puente a S7 del plan formativo | Sí |
| U4 Gestión de activos | Alto — exigencia operador PBSA | Lead appointed party | Plantilla IFC4.3 con Psets FM | Coordinar con operador antes de H1 | Sí |
| U5 BREEAM/ESG | Medio — diferenciador comercial | Appointed party (sostenibilidad) | Datos energéticos + materiales | Alcance a confirmar tras kick-off | Sí |

---

## 2. Hitos de entrega de información

Se definen **4 hitos** alineados con las fases típicas de un encargo PBSA español:

| Hito | Fecha objetivo | Disciplinas exigidas | Entregables principales |
|---|---|---|---|
| H1 · Anteproyecto | _(completar)_ | ARQ, URB | Modelo conceptual + memoria + ubicación urbanística |
| H2 · Proyecto Básico | _(completar)_ | ARQ, EST, URB | Modelos federados + informes CTE + estudios BREEAM |
| H3 · Proyecto Ejecutivo | _(completar)_ | ARQ, EST, MEP, URB | Modelos detallados + mediciones + IDS validado |
| H4 · As-built / Entrega | _(completar)_ | Todas | Modelo as-built + manual O&M + datos FM para operador |

---

## 3. Estándares y formatos exigidos

- **Esquema IFC:** IFC4 Add2 TC1 (mínimo) / **IFC4.3** (preferente; obligatorio para urbanización).
- **MVD:** véase §3.1 (formalización específica).
- **Validación de calidad:** IDS v1.0 (buildingSMART) emitidos por el appointing party — uno por hito.
- **Issues y coordinación:** BCF 3.0.
- **Nomenclatura de archivos:** ISO 19650-2 §11 (`<Proyecto>-<Originador>-<Volumen>-<Nivel>-<Tipo>-<Disciplina>-<Número>`).
- **Clasificación:** **GuBIMClass** (sistema oficial del Institut de Tecnologia de la Construcció de Catalunya — coherencia con marco regulatorio catalán).
- **Sistema de coordenadas:** ETRS89 / UTM zona 31N (obligatorio para urbanización).

### 3.1 MVD aplicable

La entrega de modelos IFC al CDE se rige por **Model View Definition (MVD)** explícito y verificable. NEXUM exige:

#### 3.1.1 MVD por defecto — Reference View

Toda entrega oficial al CDE (estado `Published`) debe declararse y validarse contra **Reference View**, en la variante correspondiente al esquema:

| Ámbito del modelo | Esquema IFC | MVD obligatorio |
|---|---|---|
| Edificación (ARQ, EST, MEP) | IFC4 Add2 TC1 | **IFC4 Add2 Reference View** |
| Urbanización (URB) | IFC4.3 | **IFC4.3 Reference View** |
| Modelo federado (Lead AP) | Coincide con el esquema dominante del hito | Reference View del esquema correspondiente |

**Propósitos cubiertos por Reference View:**

- Coordinación multidisciplinar y clash detection (U1)
- Validación IDS por hito (U3)
- Mediciones y QTO (U2, vía `Qto_*` y geometría teselada)
- Archivo y trazabilidad as-built (U4)

#### 3.1.2 MVD bilateral excepcional — Design Transfer View

Se admite **Design Transfer View (DTV)** únicamente en intercambios bilaterales entre dos appointed parties, cuando:

1. Ambas partes hayan validado previamente la compatibilidad de su software con DTV mediante un *smoke test* documentado.
2. El uso de DTV esté justificado por necesidad de **round-trip editable** (p.ej. transferencia de elementos paramétricos entre autores).
3. El intercambio se registre en el BEP como excepción autorizada por el Lead AP.
4. **El entregable final al CDE en estado `Published` se realice siempre en Reference View**, independientemente de los intercambios DTV intermedios.

DTV **no es admisible** como formato de entrega oficial al CDE.

#### 3.1.3 Declaración obligatoria en cabecera IFC

Todo archivo IFC entregado debe declarar su MVD en la cabecera STEP:

```
FILE_DESCRIPTION (
  ('ViewDefinition [ReferenceView_V1.2]'),
  '2;1'
);
```

La cadena exacta admitida según esquema y MVD:

| Combinación | Cadena `ViewDefinition` |
|---|---|
| IFC4 Add2 + Reference View | `ReferenceView_V1.2` |
| IFC4.3 + Reference View | `ReferenceView` (IFC4.3 oficial) |
| IFC4 Add2 + Design Transfer View | `DesignTransferView_V1.0` (solo intercambios bilaterales) |

#### 3.1.4 Verificación automatizada

El Lead Appointed Party debe verificar el MVD declarado antes de cada publicación al CDE mediante:

- **Validación estructural:** lectura de la cabecera STEP (`FILE_DESCRIPTION.ViewDefinition`) — script Python con IfcOpenShell.
- **Validación de conformidad:** comprobación de que las entidades presentes en el modelo pertenecen al subconjunto declarado por el MVD. Herramientas admisibles: **buildingSMART IFC Validation Service**, **ifctester** (parcial), **Solibri**.

#### 3.1.5 Criterio de no conformidad

Un modelo IFC se rechaza en la admisión al CDE si:

- No declara MVD en cabecera.
- Declara un MVD no admitido por este EIR.
- Declara Reference View pero contiene entidades incompatibles con dicho MVD (p.ej. geometría paramétrica donde se exige teselada).
- Declara DTV sin la excepción registrada en el BEP.

---

## 4. LOIN — Level of Information Need (resumen por hito)

Referencia normativa: **EN 17412-1:2020**. Tabla resumen; el detalle por disciplina y elemento se desarrollará en el BEP y se materializará como IDS en cada hito.

| Hito | Geometría (LOD) | Información alfanumérica (LOI) | Documentación |
|---|---|---|---|
| H1 | Volumetría + ubicación urbanística | Identificador + función + clasificación GuBIMClass nivel 1 | Memoria conceptual + estudio urbanístico |
| H2 | Elementos con dimensiones reales | Tipo, material genérico, GuBIMClass completo, propiedades CTE | Fichas de elementos tipo + cumplimiento CTE |
| H3 | Detalle constructivo | Propiedades técnicas completas, fabricante (si aplica), QTO | Fichas técnicas, certificados, mediciones |
| H4 | Geometría as-built | Datos de O&M, garantías, lote, datos FM para operador PBSA | Manuales, certificados finales, plan O&M |

> Nota: el LOIN se especifica **por propósito y por hito**, no de forma global. La versión máquina-legible se entregará como IDS (uno por hito) en S7 del plan formativo.

---

## 5. Entorno común de datos (CDE)

NEXUM no prescribe plataforma concreta — **la elección queda abierta al lead appointed party** en su propuesta (Pre-BEP). Los requisitos funcionales son obligatorios:

| Aspecto | Requisito |
|---|---|
| Plataforma | A definir por el lead appointed party en el Pre-BEP. Debe ser compatible OpenBIM y soportar IFC + BCF nativos. |
| Estados de información | ISO 19650-1 §12: WIP / Shared / Published / Archived |
| Auditoría | Trazabilidad completa de cambios, aprobaciones y descargas |
| Acceso | Roles diferenciados por organización y disciplina |
| Retención | Durante encargo + 10 años mínimo tras entrega final |
| Interoperabilidad | Acceso programático vía API para integraciones de QA/QC |

---

## 6. Roles y responsabilidades exigidas

| Rol ISO 19650 | Responsable | Obligaciones mínimas |
|---|---|---|
| Appointing party | NEXUM | Emisión EIR, aprobaciones, gestión CDE corporativo |
| Lead appointed party | _(a designar)_ | BEP, MIDP, coordinación cadena de suministro |
| Appointed parties | _(por disciplina)_ | TIDP, modelos disciplinares, calidad |
| Information manager | _(rol contratable)_ | Gestión del CDE y procedimientos de información |

---

## 7. Requisitos comerciales y contractuales

- El BEP post-appointment forma parte del contrato.
- Penalizaciones por incumplimiento de hitos del MIDP: _(a definir)_.
- Propiedad intelectual de los modelos: _(cláusula a redactar)_.

---

## 8. Criterios de aceptación

Un entregable se considera aceptado cuando:

1. Pasa la validación IDS asociada al hito.
2. Cumple la nomenclatura ISO 19650-2 §11.
3. Está publicado en el estado correcto del CDE.
4. Tiene aprobación documentada del information manager.

---

## Fuentes de referencia

- ISO 19650-1:2018 — Organization and digitization of information
- ISO 19650-2:2018 — Delivery phase of assets
- EN 17412-1:2020 — Level of Information Need
- [buildingSMART · IDS](https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/)
- [Plantillas ISO 19650 (Plannerly)](https://plannerly.com/category/iso-19650-templates/)

---

## Dudas pendientes

1.
2.
3.
