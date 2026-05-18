# S2·X — Lectura comentada del `revit_ifc_export_config.json`

**Sesión:** S2·X · Miércoles 20/05/2026 · 07:30–09:00
**Tema marco:** BEP, EIR y plan de información (profundización/lab)
**Material asociado:** `configs/revit_ifc_export_config.json` v0.3
**Referencias cruzadas:** BEP §4.1.6 · EIR §3.1
**Objetivo de la sesión:** entender, parámetro a parámetro, por qué cada clave del JSON tiene el valor que tiene; conectar cada decisión con la formalización del MVD y con los facets IDS que la verificarán aguas abajo.

---

## 0. Cómo trabajar la sesión (07:30–09:00)

| Tramo | Minutos | Actividad |
|---|---|---|
| 07:30–07:40 | 10' | Abrir VS Code en `C:\Users\jmsor\OpenBIM\openbim-12w\` y cargar simultáneamente: `configs/revit_ifc_export_config.json`, `docs/E2_mini_bep.md` §4.1.6 y `docs/E2_eir_draft.md` §3.1. Pantalla dividida. |
| 07:40–08:30 | 50' | Recorrido por los 6 bloques temáticos (§1–§6 de este documento). Por cada parámetro: leer el valor → leer el comentario → marcar en rojo en VS Code (vía comentario fuera del JSON, en un `.md` paralelo de notas) cualquier duda. |
| 08:30–08:50 | 20' | Mini-laboratorio: ejecutar el snippet Python de §7 para cargar y validar el JSON. Anotar fallos. |
| 08:50–09:00 | 10' | Cerrar con la sección §8 (preguntas frecuentes y antipatrones) y registrar conclusiones en `S2X_notas_sesion.md`. |

> **Regla:** no se modifica el JSON durante la sesión. Si surgen cambios, se anotan y se aplican como v0.4 en sesión posterior con commit dedicado.

---

## 1. Bloque A — Identidad y versión del setup

Estos parámetros identifican el preset y fijan el MVD/Schema. Son los más críticos: si están mal, el resto da igual.

| Línea | Clave | Valor | Lectura |
|---|---|---|---|
| 2 | `Name` | `"NEXUM_CanCabassa_IFC4_RV"` | Nombre del setup tal como aparecerá en el desplegable de Revit (`File → Export → IFC → <Modify setup>`). Convención NEXUM: `<empresa>_<proyecto>_<schema>_<MVD>`. Permite que cualquier técnico del equipo identifique de un vistazo qué exporta. **No es un identificador técnico** (Revit no lo usa internamente), pero sí es contractual: aparece literalmente en el BEP §4.1.6. |
| 3 | `IFCVersion` | `21` | Código numérico interno del exportador. `21` = **IFC 4 Reference View**. Otros valores típicos: `9` = IFC 2x3 CV 2.0, `10` = IFC 4 DTV, `11` = IFC 4 Reference View (alias antiguo), `24` = IFC 4x3. **Es la única clave que determina el MVD efectivo**: el resto de propiedades pueden estar bien y, si esta está mal, la exportación no cumple el MVD prometido. Verificable cruzando con `FileVersionDescription`. |
| 4 | `IFCFileType` | `0` | Formato físico del fichero. `0` = `.ifc` (STEP, texto plano). Alternativas: `1` = `.ifcXML`, `2` = `.ifcZIP`. NEXUM exige `0` para máxima interoperabilidad: ifctester, Solibri, IFC Validation Service y la mayoría de viewers leen `.ifc` nativo sin sorpresas. |
| 43 | `FileVersionDescription` | `"IFC 4 Reference View [ReferenceView_V1.2]"` | Cadena humana que se serializa en la cabecera STEP (`FILE_DESCRIPTION`). Debe ser **coherente con `IFCVersion=21`**. Si alguien cambia `IFCVersion` a `10` (DTV) y olvida actualizar esta cadena, el header del IFC mentirá y el script `03_check_ifc_header.py` (que crearemos en S4·L) marcará incidencia. |
| 41 | `IsBuiltIn` | `false` | Falso indica que es un setup personalizado, no uno de los 6 que Revit trae de fábrica. NEXUM **siempre** trabaja con custom setups versionados, nunca con los built-in (Autodesk los puede modificar entre versiones sin previo aviso). |
| 42 | `IsInSession` | `false` | Falso indica que el setup está guardado en disco (importable/exportable), no es un setup volátil en memoria. Es el modo correcto para configuraciones que se versionan en Git. |

> **Pregunta tipo de la sesión:** *"¿Qué pasa si quiero exportar IFC 2x3 para un colaborador heredado?"* Respuesta esperada: se crea un setup paralelo `NEXUM_CanCabassa_IFC2x3_CV20` con `IFCVersion=9` y MVD CoordinationView 2.0, **nunca** se modifica este JSON. El BEP §4.1 lo recoge como DTV-* (transferencia bilateral controlada).

---

## 2. Bloque B — Geometría y representación

Estos parámetros controlan qué se exporta como geometría y con qué fidelidad. Cualquier cambio aquí altera el peso del IFC y los resultados de clash/QTO.

| Línea | Clave | Valor | Lectura |
|---|---|---|---|
| 8 | `SpaceBoundaries` | `1` | Nivel de límites de espacio. `0` = ninguno, `1` = 1st-level (cada Space limita con elementos), `2` = 2nd-level (subdivide superficies por colindancia entre Spaces). NEXUM elige `1` porque el MVD Reference View **no admite** `2` (es exclusivo de DTV/CV2.0). Necesario para QTO de superficies útiles y para Energy Analysis básico. |
| 9 | `SitePlacement` | `0` | Cómo se ancla el modelo en coordenadas. `0` = Shared Coordinates (Survey Point), `1` = Project Base Point, `2` = Internal origin, `3` = IFC Site location (declarado). NEXUM exige `0` para que Can Cabassa esté georreferenciado en ETRS89/UTM 31N (coherente con EIR §3.1 «coordenadas reales»). Si se usa `2`, el modelo nace en `(0,0,0)` y federar con URB (que sí usa UTM) es imposible. |
| 11 | `SplitWallsAndColumns` | `false` | Si es `true`, Revit parte muros y pilares multi-nivel en piezas por planta antes de exportar. Reference View **rechaza** esto: cada IfcWall debe ser una pieza continua. Si se pone `true`, el validador MVD da error «InvalidRepresentation». |
| 15 | `Export2DElements` | `false` | Si exporta líneas de detalle 2D (anotaciones, símbolos planos). En Reference View **debe ser `false`** (es un MVD para coordinación 3D, no para entrega gráfica). Las anotaciones se entregan en PDF/DWG aparte. |
| 17 | `Use2DRoomBoundaryForVolume` | `false` | Si `true`, calcula volúmenes de Space usando solo el perímetro 2D del Room. NEXUM lo deja `false` porque queremos volúmenes 3D reales (tienen en cuenta techos inclinados y losas variables). Importante para QTO de climatización. |
| 20 | `ExportSolidModelRep` | `false` | Si `true`, fuerza B-Rep sólido para todo. En Reference View se exige **representación facetada (triangulada)**, no B-Rep. Dejar en `false` permite que el exportador use Tessellation, que es lo que el MVD requiere. |
| 27 | `ExportBoundingBox` | `false` | Si exporta cajas envolventes adicionales para cada elemento. NEXUM no lo necesita: añade peso al IFC y los viewers modernos calculan el bounding box on-the-fly. |
| 29 | `UseActiveViewGeometry` | `false` | Si `true`, exporta exactamente la geometría tal y como se ve en la vista activa (con cortes, secciones, etc.). NEXUM lo deja en `false`: queremos la geometría **completa de cada elemento**, no recortada por planos de la vista. |
| 30 | `TessellationLevelOfDetail` | `0.5` | Densidad de la malla triangular (0.0 = mínima, 1.0 = máxima). `0.5` es el equilibrio recomendado por Autodesk: malla fina para curvas (ARQ con muros curvos del proyecto), peso aceptable. Valores superiores a `0.7` disparan el tamaño del IFC sin mejora visible. |
| 31 | `UseOnlyTriangulation` | `false` | Si `true`, fuerza triangulación pura (sin polígonos n-laterales). NEXUM lo deja `false` para permitir que el exportador use facetas optimizadas. Reference View admite ambos. |

> **Decisión documentada:** la combinación `SpaceBoundaries=1 + SplitWallsAndColumns=false + ExportSolidModelRep=false + Tessellation=0.5` **es la firma MVD Reference View**. Cambiar cualquiera de ellos invalida la promesa del setup. Esto se reflejará en S6·L (calidad) como una check obligatoria.

---

## 3. Bloque C — Property Sets y Quantities

Aquí se decide qué información alfanumérica viaja con la geometría. Es el corazón del LOIN dimensión alfanumérica (recordar `S2L_loin_en_ids.md` §3).

| Línea | Clave | Valor | Lectura |
|---|---|---|---|
| 10 | `ExportBaseQuantities` | `true` | Exporta los Qto_* estándar de buildingSMART (Qto_WallBaseQuantities, Qto_SlabBaseQuantities, etc.). **Imprescindible para QTO automatizado**. Si está en `false`, ifctester no puede validar cantidades y los mediciones hay que recalcularlas en otra herramienta. |
| 13 | `ExportInternalRevitPropertySets` | `false` | **Bloque crítico**. Si `true`, Revit exporta TODOS sus parámetros internos como Psets (cientos por elemento, en inglés, con nombres `Pset_Revit_*`). NEXUM lo deja en `false` porque:<br>1. Reference View **no los necesita** (los Pset_ son OOTB buildingSMART, no Revit internos).<br>2. Multiplican el peso del IFC por 3-5×.<br>3. Crean ruido en validación IDS (facets matcheando properties que no aportan valor contractual). |
| 14 | `ExportIFCCommonPropertySets` | `true` | Exporta los `Pset_*` estándar de buildingSMART (Pset_WallCommon, Pset_DoorCommon, etc.). **Imprescindible**: estos son los Psets que el IDS NEXUM va a verificar (S7·L). Sin ellos, las facets `Property` del IDS fallan en cascada. |
| 18 | `UseFamilyAndTypeNameForReference` | `true` | Construye el campo `Reference` (IfcRoot.Name del Type) concatenando `Family : Type`. Útil para que el nombre del IfcWallType sea legible y trazable al objeto Revit original. Si está en `false`, solo aparece el nombre del Type, con riesgo de colisiones (varios Families pueden tener Types con el mismo nombre). |
| 19 | `ExportPartsAsBuildingElements` | `false` | Si `true`, las Parts de Revit (subdivisiones internas de muros multicapa, p.ej.) se exportan como IfcBuildingElement independientes. NEXUM lo deja `false`: queremos un muro = un IfcWall, no una colección de capas como elementos. Las capas se preservan en el MaterialLayerSet del WallType. |
| 21 | `ExportSchedulesAsPsets` | `false` | Si `true`, cada tabla de cantidades de Revit se convierte en un Pset_ aplicado al elemento. NEXUM lo deja `false`: las schedules son artefactos de presentación, no información contractual. Si se necesita una tabla específica como Pset, se modela explícitamente vía `ExportUserDefinedPsets`. |
| 22 | `ExportSpecificSchedules` | `false` | Variante restringida del anterior. `false` por la misma razón. |
| 23 | `ExportUserDefinedPsets` | `true` | **Bloque crítico activo**. Permite cargar Psets personalizados desde el `.txt` referenciado en línea 24. Aquí es donde NEXUM inyecta los Psets `Pset_NEXUM_*` que el EIR §3 declara obligatorios (p.ej. `Pset_NEXUM_Sostenibilidad`, `Pset_NEXUM_GuBIMClass`). |
| 24 | `ExportUserDefinedPsetsFileName` | `"NEXUM_GuBIMClass_UserDefinedPsets.txt"` | Ruta al fichero `.txt` con la definición de los Psets propios. El formato es el documentado por Autodesk (líneas `PropertySet:` + `Element:` + lista de propiedades). Este `.txt` se versionará en `configs/` al final de S2·X como tarea pendiente. |
| 25 | `ExportUserDefinedParameterMapping` | `true` | Activa el mapeo manual de parámetros Revit ↔ properties IFC. Necesario para que parámetros Revit con nombre en castellano (p.ej. «Resistencia al fuego») se exporten con el nombre IFC canónico (`FireRating`). Sin esto, las facets IDS no matchearán. |
| 26 | `ExportUserDefinedParameterMappingFileName` | `"NEXUM_ParameterMapping.txt"` | Fichero `.txt` del mapeo. Mismo formato Autodesk. Se versionará junto con el anterior. |
| 39 | `UseTypeNameOnlyForIfcType` | `true` | Cuando exporta un IfcXxxType (p.ej. IfcWallType), usa solo el `Type Name` de Revit, no el `Family : Type`. Es coherente con la convención de NEXUM para nombrado de Types (códigos cortos tipo `MUR-EX-300`). |
| 40 | `UseVisibleRevitNameAsEntityName` | `false` | Si `true`, sobreescribe el nombre del Entity con el nombre visible en Revit. NEXUM lo deja `false` para preservar la lógica de naming nativa del exportador, que respeta convenciones IFC. |

> **Regla mnemotécnica:** «Internal=NO, Common=SÍ, UserDefined=SÍ». Si recordamos esto, el 80% del LOIN alfanumérico ya está bien configurado.

---

## 4. Bloque D — Filtros de contenido y vistas

Estos parámetros determinan **qué elementos del modelo** entran en el IFC. Conectan directamente con la práctica BIM de tener una vista de trabajo y una vista de exportación.

| Línea | Clave | Valor | Lectura |
|---|---|---|---|
| 12 | `IncludeSteelElements` | `true` | Si `true`, exporta elementos modelados con la API de Steel (perfiles laminados, conexiones, etc.). Aunque la disciplina EST de Can Cabassa es hormigón principalmente, dejamos `true` para no perder posibles elementos metálicos puntuales (barandillas estructurales, perfiles aux.). |
| 16 | `VisibleElementsOfCurrentView` | `true` | **Clave maestra del workflow NEXUM**. Si `true`, exporta solo los elementos visibles en la vista activa al pulsar Export. Esto obliga a tener una **«Vista IFC»** dedicada en Revit con los filtros adecuados (sin grids, sin levels duplicados, con disciplinas correctas). Es la mejor garantía para no exportar basura. Si está `false`, exporta TODO el modelo, incluido lo oculto y lo desfasado. |
| 33 | `ExportRoomsInView` | `true` | Asegura que los Rooms visibles en la vista activa se exporten como IfcSpace. Necesario para QTO de superficies y para que las facets IDS de Spaces tengan elementos donde aterrizar. |
| 34 | `ExportLinkedFiles` | `false` | **Crítico**. Si `true`, exporta también los modelos vinculados (linked .rvt) en el mismo IFC. NEXUM lo deja `false`: cada disciplina exporta su propio IFC y la federación ocurre **fuera de Revit** (Solibri, BIMcollab Zoom, Speckle). Si se pusiera `true`, perderíamos trazabilidad por disciplina. |
| 35 | `ActiveViewId` | `-1` | `-1` = usa la vista activa en el momento del Export. Si fuera un Id concreto, fijaría la vista al guardar el setup (peligroso: si esa vista se borra/renombra, falla). |
| 36 | `ExcludeFilter` | `""` | Filtro adicional de exclusión por categoría/parámetro. Vacío porque ya filtramos vía «Vista IFC». Si en futuras versiones queremos excluir explícitamente, p.ej. todos los `DetailItems`, se rellena aquí con la sintaxis Autodesk. |
| 5–7 | `ActivePhaseId` | `{"IntegerValue": -1}` | `-1` = todas las fases. Si se pusiera el Id de la Phase «New Construction», excluiríamos elementos «Existing» (estado actual del solar). En H1 (Anteproyecto) y H2 (Básico) queremos todas las fases visibles. |

> **Práctica recomendada:** crear en Revit una vista 3D llamada `IFC_Export_ARQ` con un View Template `IFC_Export` que aplique todos los filtros NEXUM. El Export se hace siempre desde esta vista. Se documentará como anexo del BEP §4.1.6 en próxima revisión.

---

## 5. Bloque E — Metadatos COBie y administrativos

Estos parámetros van directamente al header del IFC (`FILE_DESCRIPTION`, `IfcOrganization`, `IfcProject.Name`). Son legibles por humanos en cualquier viewer.

| Línea | Clave | Valor | Lectura |
|---|---|---|---|
| 37 | `COBieCompanyInfo` | `"NEXUM Developments"` | Aparece como `IfcOrganization.Name` del autor del fichero. Coherente con el BEP §1 «Organización Lead». |
| 38 | `COBieProjectInfo` | `"Can Cabassa PBSA"` | Aparece como `IfcProject.Name`. Debe coincidir literalmente con el nombre del proyecto declarado en EIR §1. |
| 32 | `StoreIFCGUID` | `true` | **Imprescindible para BCF**. Si `true`, Revit guarda el GUID asignado al exportar como parámetro persistente del elemento. La siguiente exportación reusa el mismo GUID, garantizando **estabilidad GUID entre revisiones**. Sin esto, cada exportación genera GUIDs nuevos y los BCF de S10·L pierden referencias. |

> **Nota S2·X:** las 3 cajas de información que el JSON **no guarda** (File Header Information, Project Address, Classification Settings) deben revisarse en Revit directamente. Lo veremos brevemente en pantalla compartida: `File → Export → IFC → Modify setup → pestaña Property Sets / Address / etc.`

---

## 6. Bloque F — Metadatos NEXUM (no estándar Autodesk)

Este bloque es **una extensión propia**. Autodesk ignora cualquier clave que empiece por `_`. La usamos como capa de gobernanza y trazabilidad.

| Línea | Clave | Lectura |
|---|---|---|
| 44–59 | `_NEXUM_metadata` | Objeto JSON anidado con metadatos del setup. Autodesk lo descarta silenciosamente al cargar, pero nuestros scripts Python (S4·L) lo leerán para auditoría. |
| 45 | `purpose` | Frase libre que documenta la intención del setup. |
| 46 | `applies_to` | Lista de productos/versiones donde este setup es aplicable. Si el equipo MEP usa Revit MEP 2024.2, esto se valida en S6·L. |
| 47 | `min_revit_version` | Versión mínima de Revit. El IFC exporter cambió API en 2024.2; versiones anteriores no soportan algunas claves. |
| 48 | `min_ifc_exporter_version` | Versión mínima del add-in `IFC for Revit` (que se actualiza independientemente del Revit core). Se descarga de [Autodesk App Store](https://apps.autodesk.com/RVT/en/Detail/Index?id=8617146236117233562). |
| 49 | `version` | Versión semántica del propio JSON (no del software). Sube cuando se cambia cualquier valor del JSON. Hoy v0.3. |
| 50 | `date` | Fecha de última edición. |
| 51 | `author` | Responsable de la edición. |
| 52–53 | `BEP_reference` / `EIR_reference` | Trazabilidad cruzada con los documentos contractuales. Permite que en cualquier momento alguien pueda partir del JSON y encontrar la justificación documental. |
| 54–58 | `notes_no_guardados_en_json` | Lista de aspectos que **no son configurables por JSON** y deben gestionarse en el `.rvt`. Es un recordatorio para no caer en falsa sensación de control total. |

> **Convención NEXUM:** todo metadato propio va dentro de un único objeto `_NEXUM_metadata` con prefijo `_` para señalar que no es estándar Autodesk. Otros proyectos pueden tener `_ACME_metadata`, `_CLIENT_metadata`, etc.

---

## 7. Mini-laboratorio (20')

Ejecutar este snippet desde el entorno `openbim` (Python 3.12.13). No requiere Revit ni IfcOpenShell, solo `json` estándar.

```python
# scripts/s2x_lab_json_reader.py
import json
from pathlib import Path

CONFIG_PATH = Path(r"C:\Users\jmsor\OpenBIM\openbim-12w\configs\revit_ifc_export_config.json")

with CONFIG_PATH.open("r", encoding="utf-8") as f:
    cfg = json.load(f)

# 1) Comprobaciones críticas (las que validaremos automáticamente en S4·L)
checks = {
    "Schema IFC4 Reference View": cfg.get("IFCVersion") == 21,
    "Fichero .ifc plano": cfg.get("IFCFileType") == 0,
    "FileVersionDescription coherente": "Reference View" in cfg.get("FileVersionDescription", ""),
    "GUIDs estables": cfg.get("StoreIFCGUID") is True,
    "Common Psets activos": cfg.get("ExportIFCCommonPropertySets") is True,
    "Internal Psets desactivados": cfg.get("ExportInternalRevitPropertySets") is False,
    "User Psets activos": cfg.get("ExportUserDefinedPsets") is True,
    "Base Quantities activos": cfg.get("ExportBaseQuantities") is True,
    "Visible View only": cfg.get("VisibleElementsOfCurrentView") is True,
    "Sin Linked Files": cfg.get("ExportLinkedFiles") is False,
    "Shared Coordinates": cfg.get("SitePlacement") == 0,
    "Site elevation included": cfg.get("IncludeSiteElevation") is True,
}

print(f"Setup: {cfg.get('Name')}")
print(f"Versión metadata: {cfg.get('_NEXUM_metadata', {}).get('version')}")
print("-" * 60)
for desc, ok in checks.items():
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark}] {desc}")
print("-" * 60)

failed = [d for d, ok in checks.items() if not ok]
if failed:
    print(f"FALLAN {len(failed)} comprobaciones. Revisar antes de exportar.")
else:
    print("Todas las comprobaciones críticas OK.")
```

**Qué hacer en la sesión:**
1. Crear el fichero `scripts/s2x_lab_json_reader.py` con el contenido anterior.
2. Ejecutar: `python scripts/s2x_lab_json_reader.py`.
3. Esperar `Todas las comprobaciones críticas OK.` Si algo falla, anotar en `S2X_notas_sesion.md`.
4. **Variación didáctica:** cambiar manualmente `IFCVersion` a `10` en el JSON, re-ejecutar, observar el FAIL, **revertir el cambio**.

> Este snippet es la semilla de `02_validate_revit_config.py` que formalizaremos en S4·L con argparse, logging y salida JSON estructurada.

---

## 8. Preguntas frecuentes y antipatrones

**P1 — ¿Por qué `IFCVersion=21` y no `10`?**
`10` = IFC 4 Design Transfer View. DTV admite primitivas constructivas (Sweeps, B-Reps, CSG) y es bidireccional editable. Reference View (`21`) es **unidireccional** y solo permite geometría facetada. NEXUM exige Reference View para entregas estandarizadas, porque garantiza interoperabilidad sin renegociaciones. DTV solo se usa en transferencias bilaterales DTV-01/DTV-02 documentadas en BEP §4.1.

**P2 — ¿Por qué `ExportLinkedFiles=false`?**
Porque la federación es responsabilidad del CDE (Speckle/Solibri), no del modelado. Si exportáramos linked, perderíamos: (a) trazabilidad por disciplina, (b) capacidad de actualizar una sola disciplina sin re-exportar todo, (c) control de quién es autor de qué. La regla NEXUM: **un IFC por disciplina, federación a posteriori**.

**P3 — ¿Por qué `TessellationLevelOfDetail=0.5` y no `1.0`?**
`1.0` produce mallas excesivamente finas. En Can Cabassa, un muro curvo del lobby pasa de 1.200 triángulos (LoD 0.5) a 8.500 (LoD 1.0) sin mejora visible. El IFC ARQ pasa de ~80 MB a ~340 MB. Solibri y Speckle se ralentizan. `0.5` es el sweet spot documentado por Autodesk.

**P4 — ¿Y si Autodesk añade claves nuevas en Revit 2025?**
Nuestro JSON tiene un conjunto cerrado. Si Autodesk añade `ExportXYZ` en Revit 2025, al cargar nuestro JSON tomará el valor por defecto de esa clave (lo que Autodesk decida). Para evitar sorpresas, NEXUM revisa el JSON al actualizar Revit major (release notes del add-in IFC for Revit) y añade explícitamente las claves nuevas con valor consciente. Tarea documentada en BEP §4.1.6.

**P5 — ¿Puedo editar el `.txt` de UserDefinedPsets directamente?**
Sí, pero con disciplina: el `.txt` se versiona en `configs/`, todo cambio entra por PR y se valida en CI (S9·L). Editar el `.txt` sin pasar por Git rompe la trazabilidad.

**Antipatrón A1:** activar `ExportInternalRevitPropertySets=true` «por si acaso». Resultado: IFC inflado, IDS contaminado.
**Antipatrón A2:** poner `VisibleElementsOfCurrentView=false` para no tener que mantener la vista IFC. Resultado: exporta basura (vistas borrador, elementos ocultos, fases erróneas).
**Antipatrón A3:** cambiar `Name` del setup entre exportaciones (porque «suena más bonito»). Resultado: el BEP §4.1.6 deja de coincidir con el setup real → no conformidad contractual.
**Antipatrón A4:** desactivar `StoreIFCGUID` para «que pesen menos los .rvt». Resultado: BCF rotos en cuanto se exporta dos veces.

---

## 9. Salida esperada al cerrar S2·X

Al final de la sesión debemos tener:

- [ ] `docs/S2X_notas_sesion.md` con dudas/conclusiones (lo crearemos en vivo).
- [ ] `scripts/s2x_lab_json_reader.py` ejecutándose en verde.
- [ ] Comprensión clara de los **6 bloques** (Identidad, Geometría, Psets, Filtros, COBie, Metadatos NEXUM).
- [ ] Lista priorizada de mejoras candidatas para v0.4 del JSON (si las hay).
- [ ] Commit en `openbim-12w`:
  ```bash
  git add docs/S2X_lectura_comentada_revit_config.md \
          docs/S2X_notas_sesion.md \
          scripts/s2x_lab_json_reader.py
  git commit -m "S2X: lectura comentada Revit IFC config + lab JSON reader"
  git push
  ```

## 10. Conexiones con sesiones posteriores

| Sesión | Reutilización del JSON |
|---|---|
| **S3·L (25/05)** | El JSON queda «contexto»; el foco vuelve a IFC schema. Se referencia para mostrar cómo cada clave del JSON se materializa en entidades IFC reales. |
| **S4·L (01/06)** | Formalización del snippet de §7 como `02_validate_revit_config.py` profesional. |
| **S6·L (15/06)** | El JSON es input del pipeline de calidad: paso 0 = validar config, paso 1 = exportar, paso 2 = validar IFC resultante. |
| **S7·L–S8·L (22–29/06)** | Las claves `ExportIFCCommonPropertySets`/`ExportUserDefinedPsets` se cruzan con las facets `Property` del IDS NEXUM. |
| **S9·L (06/07)** | El JSON entra en CI: GitHub Action que ejecuta `s2x_lab_json_reader.py` en cada PR que toque `configs/`. |

---

## Document Revision History

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 0.1 | 2026-05-18 | Jose M. Soria | Versión inicial · lectura comentada parámetro a parámetro de `revit_ifc_export_config.json` v0.3 · 6 bloques temáticos + mini-lab + FAQ + antipatrones + conexiones con sesiones futuras |

---

**Referencias externas oficiales:**
- [Autodesk · Modifying or Creating an IFC Setup](https://help.autodesk.com/view/RVT/2024/ENU/?guid=GUID-E029E3AD-1639-4446-A935-C9796BC34C95)
- [Open Source IFC for Revit (GitHub)](https://github.com/Autodesk/revit-ifc)
- [buildingSMART · IFC 4 Reference View MVD](https://technical.buildingsmart.org/standards/ifc/mvd/)
- [ITeC · GuBIMClass](https://www.gubimclass.org/)
