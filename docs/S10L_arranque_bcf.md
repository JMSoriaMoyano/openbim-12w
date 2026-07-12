# S10·L · Arranque BCF 3.0 y BCF-XML

**Semana:** S10 · lunes 13/07 – sábado 18/07
**Tema oficial:** BCF 3.0 y BCF-XML
**Modo:** trimodal L (conceptos) · X (lab) · S (entregable E10 + push)
**Entregable:** E10 · cierre sábado 18/07
**Redactado:** 12/07/2026 (domingo, tras catch-up de S6-S9)

---

## 1. Objetivo de la semana

Introducir BCF (BIM Collaboration Format) 3.0 como estándar buildingSMART para el intercambio de issues/tópicos entre herramientas de modelado y revisión. Al final de S10 debe existir en el repo:

1. Comprensión clara de la estructura BCF-XML (topics, viewpoints, comments, snapshots).
2. Un flujo Python funcional para leer y escribir ficheros `.bcfzip` con `bcf-client`.
3. Un ciclo de retorno demostrable: **auditoría** (S6·X/S9·L) → **issue BCF** referenciando un `IfcGuid` que ha fallado → **archivado como evidencia**.
4. Resolución en paralelo de **DT-S6X-IDS** (deuda E7 §2.4.1): `IFCWALL` strict no captura `IfcWallStandardCase`.

---

## 2. Marco conceptual (S10·L)

### 2.1 Qué es BCF

BCF (BIM Collaboration Format) es un formato abierto de buildingSMART para intercambio de comunicación estructurada sobre un modelo IFC. No es un formato de modelo — es un formato de **tópicos** ligados al modelo por `IfcGuid`.

**Documentación oficial:** https://github.com/buildingSMART/BCF-XML

### 2.2 Anatomía de un `.bcfzip`

Un fichero BCF-XML es un ZIP con estructura:

```
project.bcfzip/
├── bcf.version                  · versión del schema (3.0)
├── project.bcfp                 · metadatos del proyecto
├── documents.xml                · adjuntos referenciados
├── extensions.xml               · valores custom de campos (labels, priorities)
└── <topic-uuid>/
    ├── markup.bcf               · el topic (autor, fecha, estado, comments)
    ├── viewpoint.bcfv           · viewpoint (cámara, componentes visibles)
    └── snapshot.png             · captura del viewpoint
```

Cada carpeta `<topic-uuid>/` es **un issue** independiente. Un `.bcfzip` puede contener N topics.

### 2.3 Estructura del `markup.bcf` (XML)

Simplificado:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Markup>
  <Topic Guid="a1b2c3..." TopicType="Issue" TopicStatus="Open">
    <Title>Muro sin FireRating</Title>
    <CreationDate>2026-07-13T10:00:00Z</CreationDate>
    <CreationAuthor>jmsoria@ciccp.es</CreationAuthor>
    <Priority>High</Priority>
    <ReferenceLink>ifc://Pset_WallCommon/FireRating</ReferenceLink>
  </Topic>
  <Comment Guid="...">
    <Date>2026-07-13T10:00:00Z</Date>
    <Author>jmsoria@ciccp.es</Author>
    <Comment>Check C-P-01 FAIL en variante diseño.</Comment>
  </Comment>
</Markup>
```

### 2.4 Cambios clave BCF 3.0 vs BCF 2.1

- `TopicStatus` como cadena libre (antes enum cerrado).
- Soporte formal de **DocumentReferences** en el topic.
- Extensions.xml estandarizado (antes tácito).
- Snapshots opcionales (viewpoint puede referenciar solo componentes).

---

## 3. Lab técnico (S10·X)

### 3.1 Setup

**Sin nueva dependencia.** `bcf-client 0.8.5` ya viene instalado como transitiva de `ifctester>=0.8.5` (fijado en `requirements.txt` en S9·L). Verificar con:

```bash
python -c "import bcf; print(bcf.__version__)"
```

Debe imprimir `0.8.5`.

### 3.2 Script objetivo · `scripts/s10x_bcf_from_audit.py`

Convierte un resultado de auditoría `quality_engine` en un `.bcfzip`:

**Contrato:**

```
python scripts/s10x_bcf_from_audit.py \
  --audit reports/ci/audit_diseno.json \
  --model out/AC20-FZK-Haus_authored.ifc \
  --out out/audit_diseno_issues.bcfzip \
  --min-severity fail
```

**Comportamiento:**

- Lee el JSON de auditoría (formato `quality_engine 0.2.0-s6x`).
- Filtra checks con `status in {fail, partial}` (según `--min-severity`).
- Para cada check fallido, si el `evidence` incluye `offenders` (lista de IfcGuids), genera **un topic BCF por offender** con:
  - `Title` = `[{check_id}] {message}`
  - `TopicStatus` = "Open"
  - `Priority` = "High" si `fail`, "Normal" si `partial`
  - `ReferenceLink` apuntando al Pset/atributo del check
  - `Comment` con el evidence completo (excerpt de la regla)
  - Sin snapshot (S10 no genera imágenes — se añadirá en S11 con Bonsai)
- Empaqueta todo en `.bcfzip` con `bcf.v3.bcfxml.BcfXml`.

### 3.3 Test smoke (extensión de `tests/test_smoke_quality_engine.py`)

Añadir tests:

- `test_bcf_generation_smoke`: dado el audit JSON de S9·L (variante `diseno`), el script produce un `.bcfzip` no vacío.
- `test_bcf_reopen_roundtrip`: reabrir el `.bcfzip` generado y comprobar que contiene ≥ 1 topic con `TopicStatus == "Open"`.
- `test_bcf_references_ifc_guids`: los `ReferenceLink` (o los campos custom) referencian IfcGuids que existen realmente en el modelo IFC de origen.

---

## 4. Entregable E10 (S10·S · sábado 18/07)

### 4.1 Alcance mínimo

1. `scripts/s10x_bcf_from_audit.py` funcional.
2. `out/audit_diseno_issues.bcfzip` versionado en el repo (excepción explícita en `.gitignore` si aplica).
3. `docs/S10L_marco_bcf.md` con la teoría §2 de este documento ampliada (~200 líneas).
4. `docs/S10X_lab_bcf.md` con guía de reproducción del script.
5. `docs/E10_cierre_bcf.md` con:
   - Resumen: qué es BCF, qué hemos hecho.
   - Evidencia: pantallazos del `.bcfzip` abierto en un viewer (BIMcollab Zoom / Solibri / desktop).
   - Cierre de DT-S6X-IDS: cómo se resuelve.
6. 3 tests adicionales en `tests/test_smoke_quality_engine.py`.
7. Tag `e10-closed` tras CI verde.

### 4.2 Criterios de aceptación E10

| # | Criterio | Verificación |
|---|---|---|
| 1 | `bcf-client` importable | `import bcf` sin error |
| 2 | Script `s10x_bcf_from_audit.py` funcional | CLI --help ok |
| 3 | Genera `.bcfzip` a partir de audit JSON | Fichero existe post-run |
| 4 | Genera 1 topic por offender IFC | Test smoke lo verifica |
| 5 | Topics referencian IfcGuids reales | Test roundtrip |
| 6 | Docs marco + lab + cierre redactados | 3 md files |
| 7 | Fix DT-S6X-IDS aplicado | IDS captura subtipos wall |
| 8 | Tests pasan en CI (12/12 = 9 previos + 3 nuevos) | Workflow verde |
| 9 | `.bcfzip` de ejemplo versionado | En repo bajo `out/` o `examples/` |
| 10 | Notas de sesión S10·L/X/S publicadas | 3 md files |

### 4.3 Sacrificios asumidos por comprensión de deuda previa

- **Sin integración con BIMcollab / Solibri.** Se limita a lectura/escritura de `.bcfzip` local.
- **Sin snapshots reales.** Los viewpoints se registran sin PNG (se añadirá en S11 con Bonsai integrado).
- **Sin flujo bidireccional BCF → IFC.** Solo generación desde auditoría; el retorno (aplicar solución al modelo) queda para S11.

---

## 5. Fix paralelo · DT-S6X-IDS

### 5.1 El problema

En `ids/PBSA_v0.2_prototype.ids`, la especificación C-P-01 usa:

```xml
<ids:applicability>
  <ids:entity>
    <ids:name><ids:simpleValue>IFCWALL</ids:simpleValue></ids:name>
  </ids:entity>
</ids:applicability>
```

Esto aplica **strict** al tipo `IfcWall` puro. FZK-Haus contiene 1 IfcWall + 13 IfcWallStandardCase → el check se ejecuta sobre 1 elemento, no 14.

### 5.2 La solución

Duplicar la spec con `<ids:predefinedType>` explícito o crear una segunda spec para `IFCWALLSTANDARDCASE`:

**Opción A · dos specs separadas (recomendada, más legible):**

```xml
<ids:specification name="C-P-01a · Wall Reference" ...>
  <ids:applicability minOccurs="0">
    <ids:entity><ids:name><ids:simpleValue>IFCWALL</ids:simpleValue></ids:name></ids:entity>
  </ids:applicability>
  <ids:requirements>...</ids:requirements>
</ids:specification>

<ids:specification name="C-P-01b · WallStandardCase Reference" ...>
  <ids:applicability minOccurs="0">
    <ids:entity><ids:name><ids:simpleValue>IFCWALLSTANDARDCASE</ids:simpleValue></ids:name></ids:entity>
  </ids:applicability>
  <ids:requirements>...</ids:requirements>
</ids:specification>
```

**Opción B · una spec con OR (no soportado en IDS 1.0 estable):** descartada, sintaxis no estándar.

Aplicar Opción A a C-P-01 (Wall), C-P-02 (Slab → SlabStandardCase) y C-P-03 (Door — normalmente Door no tiene StandardCase pero sí IfcDoorStyle: verificar).

### 5.3 Impacto sobre contrato canónico

Al ampliar de 3 specs a 6 specs (3 wall + 3 slab + 3 door), el `total` del contrato canónico pasará de 35 → 38 o más. **El test `test_engine_produces_expected_summary` fallará** — se debe actualizar simultáneamente:

```python
# En tests/test_smoke_quality_engine.py, S10·L
EXPECTED_TOTAL = 38  # o el nuevo valor exacto
EXPECTED_PASS = ...  # recalcular
EXPECTED_FAIL = ...
```

Este cambio se documenta explícitamente en el commit de S10·L como *bump de contrato canónico*.

---

## 6. Plan de sesión (L / X / S)

### Lunes 13/07 (S10·L) · 07:30-09:00 (90 min)

1. Leer §2 de este documento + docs oficiales buildingSMART BCF-XML (30 min).
2. Redactar `docs/S10L_marco_bcf.md` con notas propias del marco (30 min).
3. Aplicar fix DT-S6X-IDS al `.ids` (opción A) + actualizar contrato canónico en tests (20 min).
4. Verificar `pytest tests/` verde antes de commit (10 min).

**Commit L:** `S10L marco BCF + fix DT-S6X-IDS + bump contrato canonico`

### Miércoles 15/07 (S10·X) · 07:30-09:00 (90 min)

1. Escribir `scripts/s10x_bcf_from_audit.py` (45 min).
2. Escribir 3 tests smoke BCF (20 min).
3. Ejecutar el script sobre `reports/ci/audit_diseno.json` y verificar `.bcfzip` generado (15 min).
4. Redactar `docs/S10X_lab_bcf.md` con guía (10 min).

**Commit X:** `S10X lab BCF from audit + 3 tests + ejemplo bcfzip`

### Sábado 18/07 (S10·S) · 09:00-11:00 (120 min)

1. Verificar CI verde sobre commit X.
2. Abrir el `.bcfzip` generado en BIMcollab Zoom (o alternativa) y capturar 2-3 pantallazos (30 min).
3. Redactar `docs/E10_cierre_bcf.md` v1.0 (~180 líneas condensado) (60 min).
4. Aplicar tag `e10-closed` (5 min).
5. Actualizar `docs/DEUDAS_E7_E8.md` marcando §2.4.1 como cerrado (5 min).
6. Recuperación de contexto para S11·L (20 min).

**Commit S:** `E10 cierre BCF + tag + cierre parcial deuda E7 §2.4.1`

---

## 7. Riesgos identificados

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| `bcf-client` API cambia entre v0.8.5 y siguientes | baja | media | Versión fijada `~=` en requirements |
| Fix DT-S6X-IDS rompe más checks de lo esperado | media | alta | Ejecutar `pytest` tras cada edit del .ids, no acumular |
| No hay viewer BCF disponible en tu Windows | media | media | BIMcollab Zoom es freeware; alternativa: xeokit-bcf-viewer web |
| S10·L se solapa con trabajo profesional real | media | media | Comprometer solo 90 min lunes, no arrastrar |

---

## 8. Referencias

- **BCF-XML repo oficial:** https://github.com/buildingSMART/BCF-XML
- **BCF 3.0 spec:** https://github.com/buildingSMART/BCF-XML/tree/master/Documentation
- **bcf-client (Python):** https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/bcf
- **DEUDAS_E7_E8.md** (repo): hito §2.4.1 se cierra en esta semana.
- **E6_auditoria_calidad_fzk_haus.md** (repo): §9 lista DT-S6X-IDS.
- **S9L_notas_sesion.md** (repo): plataforma sobre la que S10 construye.

---

**Autor:** José M. Soria (jmsoria@ciccp.es) · 12/07/2026
