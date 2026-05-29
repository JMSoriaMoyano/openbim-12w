# E3 — Auditoría informacional del modelo IFC AC20-FZK-Haus

> **Estado:** plantilla v0.1 generada por agente en S3·X Bloque C.
> **Tu tarea (sábado 30/05):** rellenar los bloques `<!-- TODO -->` con tu análisis personal.
> **No borres** los bloques `<!-- AUTO -->`: son evidencia automática del script.
> Puedes regenerar la evidencia ejecutando: `python scripts/s3l_ifc_inspect.py`.

**Sesión cubierta:** S3·L (25/05/2026) + S3·X (recuperación 28-29/05/2026)
**Entregable:** E3 · ciclo semana 3
**Cierre objetivo:** sábado 30/05/2026

---

## 1. Datos del modelo

<!-- AUTO: copiar de out/S3X_lab_run_<latest>.md sección HEADER -->

| Campo | Valor |
|---|---|
| Fichero | `models/samples/_local/AC20-FZK-Haus.ifc` |
| SHA-256 | `70cc8ff245fc0894201d96496c031005a5cbd7a96b22d8a1b87c5a883fb77994` |
| Schema declarado | IFC4 |
| MVD | `ViewDefinition [CoordinationView_V2.0]` |
| Author | (rellenar con valor del informe) |
| Organization | (rellenar) |
| Originating system | (rellenar) |
| Timestamp | (rellenar) |
| Entidades totales | 44,249 |

<!-- TODO: añade aquí tu lectura crítica de los metadatos.

  Pistas:
  - ¿Qué te dice el MVD CoordinationView_V2.0 sobre el alcance del modelo? Es un
    MVD de coordinación, no de transferencia para análisis (¿qué falta?).
  - ¿Qué versión de ArchiCAD lo originó? ¿Cómo afecta esto a la fidelidad IFC4
    a la luz del dictamen D3B-02 (boundaries declaradas como clase base)?
  - ¿Cuántos años tiene el modelo? ¿Sigue siendo representativo de una entrega
    NEXUM en 2026?
-->

---

## 2. Estructura espacial

<!-- AUTO: copiar de out/S3X_lab_run_<latest>.md sección Pirámide -->

```
IfcProject       #66 'Projekt-FZK-Haus'
 └── IfcSite      #389 'Gelaende' (lat 49°6'0"N, lon 8°26'0"E, elev 110.0m)
      └── IfcBuilding #434 'FZK-Haus' (long_name: Wohnhaus)
           └── IfcBuildingStorey #479 'Erdgeschoss' (Z=0.0m, 4 spaces)
                   └── IfcSpace ...
                   └── IfcSpace ...
                   └── IfcSpace ...
                   └── IfcSpace ...
           └── IfcBuildingStorey #35065 'Dachgeschoss' (Z=2.7m, 3 spaces)
                   └── IfcSpace ...
                   └── IfcSpace ...
                   └── IfcSpace ...
```

| Nivel | Cantidad | Notas |
|---|---|---|
| `IfcProject` | 1 | Cumple invariante D6-XX (unicidad de proyecto) |
| `IfcSite` | 1 | Georreferenciado, 110m sobre nivel del mar |
| `IfcBuilding` | 1 | Tipología: Wohnhaus (vivienda unifamiliar) |
| `IfcBuildingStorey` | 2 | Erdgeschoss (PB) + Dachgeschoss (PA) |
| `IfcSpace` | 7 | 4 en PB + 3 en PA |

<!-- TODO: lectura crítica de la estructura espacial.

  Pistas:
  - ¿Hay tantos IfcSpace como estancias reales esperarías en una vivienda de
    7 estancias? ¿Coincide con el plano arquitectónico clásico de FZK-Haus?
  - El sótano: ¿está modelado o no? ¿Por qué importa para Can Cabassa
    (PBSA tiene siempre sótano técnico)?
  - ¿El nombre 'Dachgeschoss' (=ático) es interpretable por una herramienta
    de análisis energético? ¿Qué exigiría NEXUM al respecto?
-->

---

## 3. Inventario físico

<!-- AUTO: copiar tabla de out/S3X_lab_run_<latest>.md -->

| Clase | Cantidad |
|---|---:|
| IfcWall (incluye subtipos) | 13 |
| IfcWallStandardCase (estricto) | 13 |
| IfcSlab | 4 |
| IfcWindow | 11 |
| IfcDoor | 5 |
| IfcStair | 1 |
| IfcRailing | 2 |
| IfcOpeningElement | 17 |
| IfcRoof | 0 |
| IfcCovering | 0 |
| IfcFurnishingElement | 0 |

**Validación cruzada vs `EXPECTED_COUNTS_FZK`:** 22 OK · 0 FAIL · 22 total.

<!-- TODO: comentario sobre los conteos.

  Pistas (apoyate en D3-01):
  - El conteo IfcWall(13) - IfcWallStandardCase(13) = 0 significa que TODAS
    las paredes cumplen las 3 restricciones del subtipo Standard. ¿Por qué es
    una BUENA señal sobre la calidad del export de ArchiCAD 20?
  - ¿Por qué hay 17 IfcOpeningElement vs 11 IfcWindow + 5 IfcDoor = 16? ¿Qué
    representa el hueco "extra"? (Pista: revisa los IfcRelFillsElement = 16
    en el informe; coincide con 11+5).
  - Ningún IfcRoof, IfcCovering ni IfcFurnishingElement. ¿Es un problema para
    NEXUM? ¿En qué LOI/LOD habría que exigirlos?
-->

---

## 4. Inventario relacional

<!-- AUTO: copiar de la sección validación cruzada del informe -->

| Relación | Cantidad | Concepto |
|---|---:|---|
| IfcRelAggregates | 5 | Pirámide: 1 Project→Site + 1 Site→Building + 1 Building→Storey + 2 Storey→Spaces |
| IfcRelContainedInSpatialStructure | 2 | Elementos físicos contenidos en cada Storey |
| IfcRelDefinesByType | 18 | Asociación a IfcWallType (2 tipos diferentes) |
| IfcRelDefinesByProperties | 482 | Cada elemento tiene ~5 Psets/Qtos |
| IfcRelAssociatesMaterial | 21 | Cada elemento físico tiene material asignado |
| IfcRelVoidsElement | 17 | Cada hueco corta un muro |
| IfcRelFillsElement | 16 | 16 huecos están rellenados por carpinterías |
| IfcRelConnectsPathElements | 16 | Muros conectados entre sí en su trazado |
| IfcRelSpaceBoundary | 81 | Boundaries 2nd level (Name='2ndLevel', Description='2a') |
| IfcRelAssociatesClassification | 1 | Una clasificación global del proyecto |

<!-- TODO: lectura crítica de las relaciones.

  Pistas (apoyate en D3B-02):
  - 81 boundaries son MUCHAS para un chalet de 7 estancias. ¿Tiene sentido?
    (Pista: cada cara con espacio adyacente cuenta; los 4 lados del salón
    cuentan como 4 boundaries 2a). Calcula el ratio boundaries / IfcSpace.
  - 16 IfcRelVoidsElement + 16 IfcRelFillsElement = 16 ventanas/puertas
    correctamente integradas en muros. Hay 1 IfcOpeningElement HUÉRFANO (17-16).
    ¿Es un fallo del modelo o tiene sentido? Identifícalo con explain_entity.
  - 482 IfcRelDefinesByProperties / ~60 elementos físicos = ~8 Psets por
    elemento de media. La mayoría son del fabricante (vendor-specific). ¿Es
    ruido o información útil? Cita el dictamen D3B-01.
-->

---

## 5. Caso de estudio: muro `#15042` (Wand-Int-ERDG-4)

<!-- AUTO: copiar de la sección Anatomía del informe -->

**Identidad:**
- ID: `#15042`
- GUID: `2XPyKWY018sA1ygZKgQPtU`
- Clase: `IfcWallStandardCase`
- Nombre: `Wand-Int-ERDG-4` (muro interior, planta baja, número 4)

**7 tipos de relaciones tocan al muro:**

| Relación | Hacia | Lectura |
|---|---|---|
| `IfcRelContainedInSpatialStructure` | `#479 IfcBuildingStorey 'Erdgeschoss'` | Pertenece a planta baja |
| `IfcRelDefinesByType` | `#15234 IfcWallType 'Leichtbeton 102890359 240'` | Tipo: hormigón ligero, 240mm |
| `IfcRelDefinesByProperties` (×5) | 1 Pset_WallCommon + 2 vendor-specific + 1 BaseQuantities + 1 vendor quantities | Solo 1 Pset NEXUM-conforme, el resto ruido |
| `IfcRelAssociatesMaterial` | `IfcMaterialLayerSetUsage` | Multimaterial estratificado |
| `IfcRelConnectsPathElements` (×2) | `#17040 Wand-Int-ERDG-2`, `#31470 Wand-Ext-ERDG-3` | Forma esquina con otros 2 muros |
| `IfcRelVoidsElement` | _(ninguno)_ | Muro ciego, sin huecos |
| `IfcRelSpaceBoundary` (×2) | Space `#20909` ('4') + Space `#33774` ('5') | Separa 2 estancias |

### 5.1 Diagrama de relaciones del muro

```
                            #66 IfcProject
                                 │
                              IfcRelAggregates
                                 │
                            #389 IfcSite
                                 │
                              IfcRelAggregates
                                 │
                          #434 IfcBuilding
                                 │
                              IfcRelAggregates
                                 │
                  ┌──── #479 IfcBuildingStorey 'Erdgeschoss'
                  │           │
                  │      IfcRelContainedInSpatialStructure
                  │           │
                  │           ▼
                  │     #15042 IfcWallStandardCase 'Wand-Int-ERDG-4'
                  │           │  │  │  │  │  │
                  │           │  │  │  │  │  └─ IfcRelSpaceBoundary ─→ #20909 IfcSpace '4'
                  │           │  │  │  │  └──── IfcRelSpaceBoundary ─→ #33774 IfcSpace '5'
                  │           │  │  │  └─ IfcRelConnectsPathElements ─→ #17040 muro vecino
                  │           │  │  └──── IfcRelConnectsPathElements ─→ #31470 muro vecino
                  │           │  └─ IfcRelAssociatesMaterial ─→ IfcMaterialLayerSetUsage
                  │           │
                  │           ├─ IfcRelDefinesByType ─→ #15234 IfcWallType 'Leichtbeton…'
                  │           │
                  │           └─ IfcRelDefinesByProperties (×5)
                  │                 ├─ Pset_WallCommon (1 prop válida de 6 NEXUM)
                  │                 ├─ AC_Pset_Name (vendor)
                  │                 ├─ ArchiCADProperties (vendor, 32 props)
                  │                 ├─ BaseQuantities (NO Qto_WallBaseQuantities)
                  │                 └─ ArchiCADQuantities (vendor, 56 props)
                  │
                  └──── #35065 IfcBuildingStorey 'Dachgeschoss' (no contiene #15042)
```

<!-- TODO: análisis razonado del muro.

  Pistas:
  - ¿Cumple el muro las 3 restricciones de IfcWallStandardCase (eje recto +
    extrusión + LayerSetUsage)? Confirma observando las relaciones.
  - El Pset 'BaseQuantities' (sin prefijo Qto_Wall) ¿es válido para NEXUM?
    (Pista: revisa D3B-01, exigimos nombres canónicos).
  - El muro NO tiene huecos. ¿Es coherente con que sea Interior y separe 2
    estancias contiguas? ¿Qué tipo de muro NEXUM esperaría sin huecos?
  - Si NEXUM recibiera este muro tal cual: ¿lo aceptaría en el CDE? ¿Qué
    correcciones pediría al equipo de diseño?
-->

---

## 6. Auditoría Pset NEXUM

<!-- AUTO: copiar de la sección Auditoría Pset NEXUM del informe -->

| Clase | Total | OK | No conformes | % cumplim. |
|---|---:|---:|---:|---:|
| IfcWallStandardCase | 13 | 0 | 13 | 0% |
| IfcSlab | 4 | 0 | 4 | 0% |
| IfcWindow | 11 | 0 | 11 | 0% |
| IfcDoor | 5 | 0 | 5 | 0% |
| IfcSpace | 7 | 0 | 7 | 0% |
| **Total** | **40** | **0** | **40** | **0%** |

**Hallazgos principales:**

1. **Qto_*BaseQuantities ausente al 100%** en las 5 clases auditadas. ArchiCAD
   20 las llama `BaseQuantities` sin prefijo, lo que NEXUM rechaza por dictamen D3B-01.
2. **Pset_WallCommon.Reference ausente al 100%.** Sin trazabilidad básica.
3. **Pset_*Common.IsExternal ausente al 100%.** Bloqueante para análisis térmico.
4. **FireRating y AcousticRating ausentes** en >70% de elementos. Bloqueante para
   cumplimiento CTE-SI y CTE-DB-HR.
5. **Pset_SpaceCommon.PubliclyAccessible ausente al 100%.** Bloqueante para
   evaluación de accesibilidad.

<!-- TODO: tu interpretación.

  Pistas:
  - Si recibieses este modelo para Can Cabassa, ¿qué le dirías al equipo de
    diseño? Redacta un párrafo "lessons learned" para la próxima entrega.
  - El modelo cumple invariantes geométricos (22 OK conteos) pero falla
    invariantes informacionales (0% Pset NEXUM). ¿Qué nos enseña esto sobre
    la distinción entre LOG (geometría) y LOI (información) de ISO 19650?
  - ¿Cómo plasmarías estos hallazgos en una IDS NEXUM v1.0 (S7·L)?
-->

---

## 7. Conformidad final · veredicto

<!-- TODO: escribe tu veredicto razonado en 4-6 frases.

  Plantilla orientativa:
  > "Tras la auditoría informacional del modelo AC20-FZK-Haus.ifc, este
  > modelo [SÍ / NO] se acepta en el CDE NEXUM en su estado actual porque:
  >
  > 1. Estructura espacial: …
  > 2. Inventario físico: …
  > 3. Calidad informacional (Psets): …
  > 4. Calidad relacional: …
  >
  > Acción propuesta: [aceptar / aceptar con condiciones / rechazar y devolver
  > al equipo de diseño con la lista de correcciones …]"

  No hay respuesta correcta única; lo que importa es que justifiques el
  veredicto con evidencia de las secciones 1-6.
-->

---

## 8. Lecciones para Can Cabassa

<!-- TODO: 3-5 puntos extrapolables a nuestro PBSA.

  Pistas — temas que probablemente debas tocar:
  - El export desde Revit (no ArchiCAD) genera Psets diferentes pero igual de
    incompletos. ¿Qué exigir en el BEP de Can Cabassa para evitar este 0%?
  - Necesitamos que cada IfcSpace tenga su programa funcional (dormitorio,
    baño, sala común, etc.) codificado en Pset_SpaceCommon.Category. El
    FZK-Haus no lo tiene — ¿cómo lo aseguramos en Can Cabassa?
  - El modelo es de 2016. Los modelos actuales (2026) suelen incluir clasificación
    Uniclass/OmniClass vía IfcRelAssociatesClassification. FZK-Haus solo tiene 1
    instancia — clasificación global, no por elemento. ¿Cómo lo escalamos para
    Can Cabassa?
  - PBSA tiene zonificación funcional (zona alquiler, zona común, zona
    técnica). ¿Cómo usar IfcZone (D3-04 aplazada a S4·L) para representarlo?
-->

---

## Referencias

- `docs/S3L_ifc_jerarquia.md` — fundamentos jerárquicos IFC4
- `docs/S3L_ifc_relaciones.md` — anatomía de las 5+3 relaciones clave
- `docs/S3L_ifc_glosario.md` — 40 términos definidos
- `docs/S3X_dudas_resueltas.md` — dictámenes D3-01, D3-02, D3B-01, D3B-02
- `scripts/s3l_ifc_inspect.py` v0.3 — script que generó la evidencia
- `out/S3X_lab_run_<timestamp>.md` — informe auto-generado
- `models/samples/SOURCES.md` — manifest del IFC con SHA-256

## Notas de cierre

- **Tiempo estimado de redacción:** 2.5–3.5 h en sábado.
- **No olvides:** ejecutar `python scripts/s3l_ifc_inspect.py` al inicio del sábado
  para regenerar `out/S3X_lab_run_*.md` con datos frescos.
- **Renombrar el informe** a `out/E3_lab_run.md` para que quede como evidencia
  versionada del entregable (este último .md SÍ se commitea, a diferencia de los
  runs efímeros).
- **Cuando termines**, marca todos los checks de `docs/E3_checklist.md` y
  rellena `docs/E3_cierre.md`.
