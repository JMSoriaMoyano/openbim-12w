# S2·X — Notas de sesión

**Fecha real de ejecución:** 20/05/2026 (sesión movida del slot estándar 07:30 al 07:09 por arranque temprano)
**Bloque:** 07:09–08:39 (90 min)
**Material guía:** `docs/S2X_lectura_comentada_revit_config.md`
**Setup analizado:** `configs/revit_ifc_export_config.json` v0.4
**Asistente:** Jose M. Soria

---

## 0. Setup de pantalla

| Panel | Fichero | Para qué |
|---|---|---|
| Izquierda | `configs/revit_ifc_export_config.json` | El JSON bajo lectura |
| Centro | `docs/S2X_lectura_comentada_revit_config.md` | Guía de lectura |
| Derecha (este fichero) | `docs/S2X_notas_sesion.md` | Anotaciones en vivo |

---

## 1. Recorrido por bloques (45')

### Bloque A — Identidad y versión (07:15–07:21)
- Decisiones confirmadas:
  - [x] `IFCVersion=21` ↔ `FileVersionDescription` coherente
  - [x] `Name` coincide con convención NEXUM (`NEXUM_CanCabassa_IFC4_RV`)
- Dudas o ajustes propuestos:
  - Considerar incluir cota de versión mínima del IFC Exporter (24.1.0) como invariante adicional en v0.5 del script

### Bloque B — Geometría y representación (07:21–07:30)
- Decisiones confirmadas:
  - [x] `SpaceBoundaries=1` apto para Reference View
  - [x] `SplitWallsAndColumns=false` (RV no admite split)
  - [x] `TessellationLevelOfDetail=0.5` (sweet spot calidad/peso)
  - [x] `SitePlacement=0` (Shared Coordinates) ratificado tras pregunta MEP
- Pregunta resuelta: ¿qué pasa con MEP si `SitePlacement=2`? → geometrías alejadas del origen, ruido geométrico, viewer crash potencial. NEXUM mantiene **siempre** Shared Coordinates.

### Bloque C — Property Sets y Quantities (07:30–07:38)
- Regla mnemotécnica «Internal=NO, Common=SÍ, UserDefined=SÍ»: clara y consolidada
- Decisiones confirmadas:
  - [x] `ExportInternalRevitPropertySets=false`
  - [x] `ExportIFCCommonPropertySets=true`
  - [x] `ExportUserDefinedPsets=true` + ruta a `NEXUM_GuBIMClass_UserDefinedPsets.txt`
  - [x] `ExportBaseQuantities=true` (Qto_*)
- Pregunta resuelta: nombres inconsistentes Revit MEP (`Coeficiente_U` vs `ThermalTransmittance` IFC) → obligación de mapping vía `NEXUM_ParameterMapping.txt` + tabla maestra BEP §4.1.6.bis.4
- **Acción derivada (hoy 07:24):** se creó **BEP §4.1.7 · Plantilla Revit unificada** como prerrequisito de coherencia bSDD↔Pset↔Mapping (v0.6 del BEP)

### Bloque D — Filtros y vistas (07:38–07:45)
- Decisiones confirmadas:
  - [x] `VisibleElementsOfCurrentView=true` → obliga vista `IFC_Export_ARQ` en `.rvt` (a configurar en plantilla S3·L)
  - [x] `Export2DElements=false` (RV es 3D puro)
  - [x] `ExportLinkedFiles=false` (federación se hace en Speckle / Solibri, no embebida)
- Pregunta resuelta: ¿fachadas como modelo enlazado de subcontrata? → tres rutas:
  - **Ruta A (preferida):** federación en Speckle, cada modelo IFC independiente con su MVD
  - **Ruta B:** federación en Solibri para checking
  - **Ruta C:** unificar vía IfcOpenShell solo si ruta A/B no son viables (S4·L–S5·L lo cubrirán)

### Bloque E — COBie y administrativos (07:45–07:52)
- `StoreIFCGUID=true` ratificado (crítico para BCF de S10·L)
- `COBieCompanyInfo` y `COBieProjectInfo` rellenos con datos NEXUM Developments + Can Cabassa
- **Decisión 21/05 · GUID stability (a raíz de la pregunta de control del Bloque E):**
  Todo proyecto NEXUM debe activar `StoreIFCGUID=true` desde la PRIMERA exportación IFC.
  - Cualquier proyecto heredado sin esa garantía entra en NEXUM con auditoría previa de paridad de GUIDs (`check_guid_stability.py`, BEP §4.1.6.5 paso 1, pendiente S6·L).
  - Si la auditoría falla: BCFs heredados se cierran como `Closed-Obsolete` en BIMcollab salvo los issues con `Status ∈ {Open, In Progress}`, que se re-emiten manualmente sobre los GUIDs nuevos.
  - Ruta alternativa si modelo Revit no se ha tocado entre exportaciones: script `bcf_guid_remap.py` (candidato a S10·L · BCF 3.0) que genera mapping `old_guid → new_guid` por match `(IfcClass, Name, ObjectPlacement, GeometryHash)` y reescribe `markup.bcf` + `viewpoint.bcfv`.
  - Ruta de forzar GUIDs antiguos vía Dynamo/pyRevit queda **PROHIBIDA** en proyectos NEXUM (riesgo de colisión silenciosa, viola IFC4 §5.1.3.2).
- Dudas o ajustes propuestos:
  -

### Bloque F — `_NEXUM_metadata` v0.4 (07:55–08:06)
- Decisiones confirmadas:
  - [x] Convención prefijo `_` para extensiones externas (Revit lo ignora silenciosamente al re-guardar)
  - [x] 12 claves de v0.4 recorridas y justificadas individualmente
  - [x] Trinidad de trazabilidad **EIR §3.1 → BEP §4.1.6 → JSON → .rte/.txt** validada como modelo ISO 19650-2 §5.3.4 compliant
  - [x] 3 elementos que viven en `.rvt` (File Header, Project Address, Classification Settings) identificados y trasladados a acción S3·L (plantilla `.rte`)
  - [x] `bsdd_reference` + `related_files` cierran trazabilidad con el trabajo bSDD de ayer
- **Decisión F.5 · Convención permanente NEXUM:** toda configuración de herramienta de terceros (JSON/XML/YAML) gestionada por NEXUM llevará bloque `_NEXUM_metadata` con mínimo 8 claves obligatorias. Aplicable futuro: BCF settings, IDS, Solibri rulesets, Speckle stream configs.
- Pregunta resuelta (JSON MEP copia-pega del ARQ): identificadas **3 capas defensivas** → plantilla con placeholders `[OBLIGATORIO: ...]` + invariantes M01–M08 en script + gate CDE `check_template_consistency.py`. Las tres se acumulan, no son alternativas.
- Dudas o ajustes propuestos:
  - Estudiar si Revit IFC Exporter 25.x sigue ignorando claves desconocidas (re-test al cambiar de versión)

---

## 2. Mini-lab Python (08:06–08:17)

Duración real: 11 min (8 min ejecución + 3 min debug del argparse inicial).

### Paso 1 · Baseline
```cmd
python scripts\s2x_lab_json_reader.py
```

**Salida observada:** cabecera con `NEXUM_CanCabassa_IFC4_RV` · v0.4 · 2026-05-18 · Jose M. Soria · refs BEP/EIR/bSDD correctas.

```
[ OK ] Schema IFC4 Reference View (IFCVersion=21)
[ OK ] Fichero .ifc plano (IFCFileType=0)
[ OK ] FileVersionDescription coherente con Reference View
[ OK ] GUIDs estables (StoreIFCGUID=true)
[ OK ] Common Psets activos
[ OK ] Internal Revit Psets desactivados
[ OK ] UserDefined Psets activos
[ OK ] Base Quantities activos (Qto_*)
[ OK ] Solo elementos visibles de la vista
[ OK ] Sin Linked Files embebidos
[ OK ] Shared Coordinates (SitePlacement=0)
[ OK ] Site elevation incluido
RESULTADO: TODAS OK (12/12)
%ERRORLEVEL% = 0
```

### Paso 2 · Variación didáctica (rotura controlada)
Cambio en `configs/revit_ifc_export_config.json`: `IFCVersion: 21` → `IFCVersion: 10` (downgrade IFC4 RV → IFC2x3).

```
[FAIL] Schema IFC4 Reference View (IFCVersion=21)
[ OK ] (las otras 11 invariantes)
RESULTADO: 1 FAIL · 11 OK
Fallos:
  - Schema IFC4 Reference View (IFCVersion=21)
%ERRORLEVEL% = 1
```

**Hallazgo crítico:** la cabecera de `_NEXUM_metadata` siguió mostrando v0.4 · fecha 2026-05-18 inalteradas → confirma que romper el JSON sin tocar la metadata es el **caso más peligroso** (versión falsa). Justifica las invariantes M01–M08 propuestas en Bloque F.

### Paso 3 · Reversión y verificación
Reversión `IFCVersion: 10` → `21`, guardar, re-ejecutar.

- `RESULTADO: TODAS OK (12/12)` → vuelta a baseline
- `%ERRORLEVEL% = 0`
- `git diff configs/revit_ifc_export_config.json` → salida vacía → reversión byte-a-byte confirmada
- `git status` → `configs/*.json` NO aparece modificado

### Conclusión del lab
El script demuestra ser **gatekeeper técnico válido** para CI/CD (S9·L). Exit code determinista (0/1), detección quirúrgica de invariantes rotas, sin falsos positivos. Pendiente extender con invariantes de gobernanza M01–M08 (Bloque F).

---

## 3. FAQ y antipatrones (08:17–08:23)

### Antipatrones identificados en el flujo NEXUM real

#### A1 · Resetazo silencioso de GUIDs (gravedad ALTA)
- **Síntoma:** BCFs huérfanos masivos tras re-exportar IFC (`Element not found in current model`)
- **Causa raíz:** `StoreIFCGUID=false` o nunca configurado → Revit regenera GUIDs en cada export → viola IFC4 §5.1.3.2
- **Detección NEXUM:** `check_guid_stability.py` paso 1 del pipeline (pendiente S6·L)
- **Prevención NEXUM:** `StoreIFCGUID=true` desde primera exportación + parámetro compartido `IfcGUID` en plantilla §4.1.7.3
- **Coste si se ignora:** 2–4 h × disciplina × hito de re-emisión manual de BCFs + non-conformance ISO 19650

#### A2 · JSON copia-pega entre disciplinas (gravedad MEDIA-ALTA)
- **Síntoma:** Setup MEP hereda metadata literal del ARQ (mismo autor, fecha, purpose genérico, sin `applies_to`)
- **Causa raíz:** Falta plantilla obligatoria con placeholders `[OBLIGATORIO: ...]` + ausencia de gate automático
- **Detección NEXUM:** Invariantes M01–M08 (Bloque F) + `check_template_consistency.py` paso 5 (BEP §4.1.6.5)
- **Prevención NEXUM:** `_template_revit_ifc_export_config.json` con placeholders que fallan invariantes si no se sustituyen
- **Coste si se ignora:** Trazabilidad EIR↔BEP↔herramienta rota → evidencia auditable perdida en hito

#### A3 · Downgrade silencioso de MVD (gravedad ALTA)
- **Síntoma:** Setup migrado de proyecto antiguo arrastra `IFCVersion=10` (IFC2x3) cuando BEP exige IFC4 RV
- **Causa raíz:** Reciclaje de configs sin re-validar MVD del BEP actual. Revit no avisa.
- **Detección NEXUM:** Invariante 1 de `s2x_lab_json_reader.py` → **demostrada funcional hoy en Paso 2 del lab**
- **Prevención NEXUM:** Pre-commit hook local + CI/CD obligatorio en `main` (S9·L)
- **Coste si se ignora:** Hito rechazado por cliente, re-trabajo completo de export, posible penalización contractual

#### A4 · Configuración invisible en el `.rvt` (gravedad MEDIA)
- **Síntoma:** Export técnicamente correcto pero sin clasificación GuBIMClass / sin Project Address / con File Header "Autodesk"
- **Causa raíz:** Estos 3 elementos NO se serializan en el JSON, viven en el `.rvt` (ver `_NEXUM_metadata.notes_no_guardados_en_json`)
- **Detección NEXUM:** `validate_ifc_against_ids.py` paso 2 del pipeline (pendiente S8·L con IDS v1.0)
- **Prevención NEXUM:** `NEXUM_CanCabassa.rte` v1 con los 3 elementos pre-configurados (a crear S3·L)
- **Coste si se ignora:** Fallo IDS automático → entrega rechazada en validación openBIM

### FAQ rápida (3 preguntas surgidas en sesión)

1. **¿Por qué el script no detectó el downgrade de `_NEXUM_metadata.version` cuando rompí `IFCVersion`?**
   Las 12 invariantes actuales son técnicas puras. Las invariantes de gobernanza (M01–M08) son propuesta del Bloque F → candidatas v0.5 del script.

2. **¿Es seguro que el script tenga exit code 1 en CI/CD? ¿Y si falla por mal motivo?**
   Sí, si las invariantes son deterministas y vinculadas al BEP. Si una invariante deja de aplicar, se modifica el BEP primero y el script después, nunca al revés. El script es **ejecución del BEP**, no fuente de verdad.

3. **¿Por qué `argparse` en S2 si solo procesa 1 archivo?**
   Embrión correcto para S4·L (`02_validate_revit_config.py` con logging estructurado, output JSON parseable, multi-archivo `*.json`). No es decoración.

---

## 4. Cierre (08:23–08:30)

### Acuerdos de sesión

1. **JSON v0.4 ratificado** como setup oficial NEXUM para Can Cabassa PBSA, disciplinas ARQ + MEP, hitos H1–H4.
2. **`_NEXUM_metadata` se eleva a convención permanente NEXUM** (decisión F.5): toda configuración de herramienta de terceros (JSON/XML/YAML) gestionada por NEXUM llevará bloque `_NEXUM_metadata` con mínimo: `purpose`, `version`, `date`, `author`, `BEP_reference`, `EIR_reference`, `related_files`, `notes_no_guardados_en_archivo`.
3. **GUID stability como regla de gobernanza** (decisión 21/05 Bloque E): `StoreIFCGUID=true` desde primera exportación en todo proyecto NEXUM. Proyectos heredados requieren auditoría previa de paridad de GUIDs.
4. **Plantilla Revit unificada `NEXUM_CanCabassa.rte`** queda formalizada como prerrequisito de coherencia bSDD↔Pset↔Mapping (BEP §4.1.7, v0.6 del BEP).
5. **`s2x_lab_json_reader.py` validado como gatekeeper** de CI/CD. Listo para integrarse en GitHub Actions en S9·L con extensión M01–M08.

### Acciones para S3·L (lun 25/05)

- [ ] Confirmar URI exacto de GuBIMClass en [bSDD Search](https://search.bsdd.buildingsmart.org/) y fijar `[BSDD-URI-PENDING-S3L]` en EIR §3.1.6.1 + BEP §4.1.6.bis.1
- [ ] Decidir publicación de dominio `nexum.developments` en bSDD (sí/no, con justificación escrita)
- [ ] Iniciar tabla maestra Revit↔bSDD por disciplina (BEP §4.1.6.bis.4) — mínimo 10 propiedades por disciplina ARQ/MEP
- [ ] Crear `templates/NEXUM_CanCabassa.rte` v1 + `NEXUM_SharedParameters.txt` con parámetro `IfcGUID` en todas las categorías (BEP §4.1.7.3)
- [ ] Crear `configs/_template_revit_ifc_export_config.json` con placeholders `[OBLIGATORIO: ...]` (acción derivada Bloque F)
- [ ] Crear `NEXUM_GuBIMClass_UserDefinedPsets.txt` y `NEXUM_ParameterMapping.txt` (referenciados por JSON v0.4)

### Mejoras candidatas para próximas versiones

**v0.5 del JSON `revit_ifc_export_config.json`:**
- Añadir `_NEXUM_metadata.min_ifc_exporter_version_tested` (registro de versión efectivamente probada)
- Añadir `_NEXUM_metadata.discipline` como campo explícito (no solo en `applies_to`)
- Añadir `_NEXUM_metadata.milestone_scope` con array de hitos cubiertos

**v0.5 del script `s2x_lab_json_reader.py`:**
- Incorporar invariantes M01–M08 de gobernanza (Bloque F)
- Añadir flag `--strict` que falla si la metadata está incompleta aun cuando las 12 técnicas pasen
- Output opcional `--json` para parseo en GitHub Actions (preparación S9·L)

**Scripts pendientes derivados:**
- `check_guid_stability.py` → S6·L
- `bsdd_resolve.py` y `bsdd_client.py` → S4·L / S6·L
- `check_template_consistency.py` (paso 5 pipeline) → S6·L
- `bcf_guid_remap.py` (mapping old→new GUIDs en BCF huérfanos) → candidato S10·L
- `validate_ifc_against_ids.py` (paso 2 pipeline) → S8·L

### Commit propuesto al cerrar la sesión

```cmd
cd C:\Users\jmsor\OpenBIM\openbim-12w
git add docs/S2X_notas_sesion.md scripts/s2x_lab_json_reader.py docs/E2_mini_bep.md
git commit -m "S2X: notas sesion + lab JSON reader 12 invariantes + BEP 0.6 con 4.1.7 plantilla unificada"
git push
```

Tras el push, `git status` debe quedar `nothing to commit, working tree clean`.

---

## Document Revision History

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 0.1 | 2026-05-20 | Jose M. Soria | Plantilla de notas para S2·X · pendiente rellenar en vivo durante la sesión |
| 0.2 | 2026-05-21 | Jose M. Soria | Registro de Decisión 21/05 · GUID stability en Bloque E (a raíz de pregunta de control sobre 1.847 BCFs huérfanos) |
| 0.3 | 2026-05-21 | Jose M. Soria | Cierre formal de S2·X: bloques A–F completados, mini-lab Python 3 pasos documentado, 4 antipatrones formalizados, 5 acuerdos de sesión, 6 acciones S3·L, mejoras candidatas v0.5 JSON y script |
